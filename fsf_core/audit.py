import logging
import os
import math
from pathlib import Path
from PIL import Image
from datetime import datetime

log = logging.getLogger('fsf')

class ForensicAuditor:
    def __init__(self):
        self.make_software_map = {
            'Apple': lambda s: s.startswith('1') and '.' in s,
            'samsung': lambda s: s.startswith('S') and 'XX' in s,
            'Google': lambda s: s.startswith('HDR+'),
            'Canon': lambda s: s.startswith('Firmware Version'),
            'SONY': lambda s: 'ILCE' in s or ' v' in s,
            'NIKON CORPORATION': lambda s: s.startswith('Ver.'),
            'FUJIFILM': lambda s: 'Digital Camera X-' in s or 'Ver' in s,
            'GoPro': lambda s: s.startswith('H'),
            'DJI': lambda s: s.startswith('v'),
        }

    def audit(self, filepath: Path) -> list[dict]:
        findings = []
        try:
            from fsf_core.handlers.image import ImageHandler
            if not ImageHandler.can_handle(filepath):
                return findings
            
            meta = ImageHandler.view_metadata(filepath)
            
            if not meta.get('exif') and not meta.get('gps'):
                findings.append({
                    'level': 'WARN',
                    'check': 'Empty metadata',
                    'detail': 'File has NO metadata at all (suspiciously clean)'
                })
                return findings

            exif = meta.get('exif', {})
            gps = meta.get('gps', {})
            basic = meta.get('basic', {})
            
            # 1. EXIF consistency: Camera make vs model
            make = exif.get('Make', '')
            model = exif.get('Model', '')
            if make and model:
                if 'Apple' in make and 'iPhone' not in model:
                    findings.append({'level': 'FAIL', 'check': 'Make/Model mismatch', 'detail': f'Apple make with non-iPhone model: {model}'})
                elif 'Canon' in make and 'EOS' not in model and 'Canon' not in model:
                    findings.append({'level': 'WARN', 'check': 'Make/Model mismatch', 'detail': f'Canon make with unusual model: {model}'})

            # 2. Timestamp consistency
            dt_orig = exif.get('DateTimeOriginal') or exif.get('DateTime')
            if dt_orig:
                try:
                    exif_dt = datetime.strptime(dt_orig, '%Y:%m:%d %H:%M:%S')
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    diff = abs((exif_dt - file_mtime).total_seconds())
                    if diff > 86400: # 24h
                        findings.append({'level': 'WARN', 'check': 'Timestamp consistency', 'detail': f'EXIF DateTime differs from file mtime by more than 24h ({diff/3600:.1f}h)'})
                    
                    # 9. Date sanity
                    if exif_dt.year > datetime.now().year + 1:
                        findings.append({'level': 'WARN', 'check': 'Date sanity', 'detail': 'Date is in the future'})
                    if exif_dt.year < 2000:
                        findings.append({'level': 'WARN', 'check': 'Date sanity', 'detail': 'Date is before 2000'})
                except ValueError:
                    pass

            # 3. GPS plausibility
            lat = gps.get('GPSLatitude')
            lon = gps.get('GPSLongitude')
            if lat and lon:
                try:
                    def parse_coord(coord_str):
                        # parse string like "(35.0, 40.0, 34.2)"
                        cleaned = str(coord_str).replace('(', '').replace(')', '').replace(' ', '')
                        parts = cleaned.split(',')
                        if len(parts) >= 3:
                            d = float(parts[0])
                            m = float(parts[1])
                            s = float(parts[2])
                            return d + m/60.0 + s/3600.0
                        return float(coord_str)
                    
                    lat_val = parse_coord(lat)
                    lon_val = parse_coord(lon)
                    if not (-90 <= lat_val <= 90 and -180 <= lon_val <= 180):
                        findings.append({'level': 'FAIL', 'check': 'GPS plausibility', 'detail': 'Coordinates out of bounds (-90/90, -180/180)'})
                except Exception:
                    pass

            # 4. Exposure triangle
            iso = exif.get('ISOSpeedRatings')
            exp_time = exif.get('ExposureTime')
            f_num = exif.get('FNumber')
            if iso and exp_time and f_num:
                try:
                    iso_val = float(iso)
                    if '/' in str(exp_time):
                        num, den = str(exp_time).split('/')
                        exp_val = float(num) / float(den)
                    else:
                        exp_val = float(exp_time)
                    
                    if '/' in str(f_num):
                        num, den = str(f_num).split('/')
                        f_val = float(num) / float(den)
                    else:
                        f_val = float(f_num)
                        
                    if f_val > 0 and exp_val > 0 and iso_val > 0:
                        ev100 = math.log2((f_val**2) / exp_val)
                        ev = ev100 + math.log2(iso_val / 100)
                        if not (0 <= ev <= 20):
                            findings.append({'level': 'WARN', 'check': 'Exposure triangle', 'detail': f'EV value out of normal bounds (0-20): {ev:.1f}'})
                except Exception:
                    pass

            # 5. Resolution match
            exif_w = exif.get('PixelXDimension') or exif.get('ExifImageWidth')
            exif_h = exif.get('PixelYDimension') or exif.get('ExifImageHeight')
            size_str = basic.get('Size')
            if exif_w and exif_h and size_str:
                try:
                    actual_w, actual_h = map(int, size_str.split('x'))
                    exif_w_val = int(exif_w)
                    exif_h_val = int(exif_h)
                    if not ((exif_w_val == actual_w and exif_h_val == actual_h) or (exif_w_val == actual_h and exif_h_val == actual_w)):
                        findings.append({'level': 'WARN', 'check': 'Resolution match', 'detail': f'EXIF resolution ({exif_w_val}x{exif_h_val}) does not match actual image size ({actual_w}x{actual_h})'})
                except Exception:
                    pass

            # 6. Software consistency
            software = exif.get('Software')
            if make and software:
                for k, v_func in self.make_software_map.items():
                    if k.lower() in make.lower():
                        if not v_func(str(software)):
                            findings.append({'level': 'WARN', 'check': 'Software consistency', 'detail': f'Software string "{software}" does not match typical pattern for make "{make}"'})
                        break

            # 7. Thumbnail check
            if 'Thumbnail' in exif or 'Compression' in exif or 'JPEGInterchangeFormat' in exif:
                findings.append({'level': 'WARN', 'check': 'Thumbnail check', 'detail': 'EXIF contains embedded thumbnail (privacy risk)'})

            # 10. Lens vs camera
            lens_model = exif.get('LensModel')
            if lens_model and make:
                make_u = make.upper()
                if 'RF' in lens_model and 'CANON' not in make_u:
                    findings.append({'level': 'WARN', 'check': 'Lens vs camera', 'detail': f'RF mount lens with non-Canon make: {make}'})
                if 'FE' in lens_model and 'SONY' not in make_u:
                    findings.append({'level': 'WARN', 'check': 'Lens vs camera', 'detail': f'FE mount lens with non-SONY make: {make}'})
                if 'NIKKOR Z' in lens_model and 'NIKON' not in make_u:
                    findings.append({'level': 'WARN', 'check': 'Lens vs camera', 'detail': f'Z mount lens with non-Nikon make: {make}'})
                if 'XF' in lens_model and 'FUJIFILM' not in make_u:
                    findings.append({'level': 'WARN', 'check': 'Lens vs camera', 'detail': f'XF mount lens with non-Fujifilm make: {make}'})

        except Exception as e:
            log.error(f'Error auditing {filepath}: {e}')
            
        return findings
