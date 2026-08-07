import shutil
from pathlib import Path
from PIL import Image, ExifTags, UnidentifiedImageError
import logging
from fsf_core.exceptions import MetadataError, HandlerError

log = logging.getLogger('fsf')

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"}

class ImageHandler:
    """Handle image metadata (EXIF, GPS, etc.)"""
    
    @staticmethod
    def can_handle(filepath: Path) -> bool:
        return filepath.suffix.lower() in SUPPORTED_EXTENSIONS
    
    @staticmethod
    def view_metadata(filepath: Path) -> dict:
        """Extract all metadata from image file.
        Returns dict with categories:
        {
            'basic': {'Format': 'JPEG', 'Size': '4032x3024', ...},
            'exif': {'Make': 'Apple', 'Model': 'iPhone 15 Pro', ...},
            'gps': {'Latitude': 35.6762, 'Longitude': 139.6503, ...},
        }
        """
        result = {'basic': {}, 'exif': {}, 'gps': {}}
        try:
            with Image.open(filepath) as img:
                result['basic'] = {
                    'Format': img.format,
                    'Mode': img.mode,
                    'Size': f"{img.width}x{img.height}"
                }
                exif_data = img.getexif()
                if exif_data:
                    for k, v in exif_data.items():
                        tag = ExifTags.TAGS.get(k, k)
                        result['exif'][str(tag)] = str(v)
                        
                    ifd = exif_data.get_ifd(ExifTags.IFD.Exif)
                    for k, v in ifd.items():
                        tag = ExifTags.TAGS.get(k, k)
                        result['exif'][str(tag)] = str(v)

                    gps_ifd = exif_data.get_ifd(ExifTags.IFD.GPSInfo)
                    for k, v in gps_ifd.items():
                        tag = ExifTags.GPSTAGS.get(k, k)
                        result['gps'][str(tag)] = str(v)
        except (UnidentifiedImageError, OSError) as e:
            log.debug(f"Could not read metadata from {filepath.name}: {e}")
            result['basic']['Error'] = str(e)
        return result
    
    @staticmethod
    def clean_metadata(filepath: Path, output: Path | None = None) -> Path:
        """Remove ALL metadata from image. Save to output or overwrite.
        For JPEG: re-save without EXIF.
        For PNG: remove text chunks.
        Returns path to cleaned file.
        """
        out_path = output or filepath
        try:
            with Image.open(filepath) as img:
                data = list(img.getdata()) if not hasattr(img, 'get_flattened_data') else list(img.get_flattened_data())
                img_without_exif = Image.new(img.mode, img.size)
                img_without_exif.putdata(data)
                
                if out_path != filepath:
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                
                if filepath.suffix.lower() == '.png':
                    img.save(out_path, format=img.format, pnginfo=None)
                else:
                    img_without_exif.save(out_path, format=img.format)
                log.info(f"Cleaned metadata from {filepath.name}")
        except (UnidentifiedImageError, OSError) as e:
            raise HandlerError(f"Failed to clean {filepath.name}: {e}") from e
        return out_path
    
    @staticmethod
    def spoof_metadata(filepath: Path, data: dict, output: Path | None = None) -> Path:
        """Write spoofed EXIF data to image.
        data dict should contain EXIF-compatible fields:
        - make, model, software, datetime, gps_lat, gps_lon, gps_lat_ref, gps_lon_ref,
          focal_length, f_number, iso, exposure_time, orientation
        """
        out_path = output or filepath
        try:
            exif_bytes = ImageHandler._build_exif(data)
            with Image.open(filepath) as img:
                # Strip old EXIF by creating clean image from pixel data
                pixel_data = list(img.getdata()) if not hasattr(img, 'get_flattened_data') else list(img.get_flattened_data())
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(pixel_data)

                if out_path != filepath:
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                clean_img.save(out_path, format=img.format or 'JPEG', exif=exif_bytes)
                log.info(f"Spoofed metadata for {filepath.name}")
        except (UnidentifiedImageError, OSError) as e:
            raise HandlerError(f"Failed to spoof metadata for {filepath.name}: {e}") from e
        return out_path
    
    @staticmethod
    def clone_metadata(source: Path, target: Path, output: Path | None = None) -> Path:
        """Copy EXIF data from source image to target image."""
        out_path = output or target
        try:
            with Image.open(source) as src_img:
                exif = src_img.info.get('exif')
            if exif:
                with Image.open(target) as tgt_img:
                    if out_path != target:
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                    tgt_img.save(out_path, format=tgt_img.format, exif=exif)
                    log.info(f"Cloned metadata from {source.name} to {target.name}")
            else:
                if out_path != target:
                    shutil.copy2(target, out_path)
                log.info(f"No metadata to clone from {source.name}")
        except (UnidentifiedImageError, OSError) as e:
            raise HandlerError(f"Failed to clone metadata from {source.name} to {target.name}: {e}") from e
        return out_path

    @staticmethod
    def _build_exif(data: dict) -> bytes:
        from PIL.TiffImagePlugin import IFDRational

        exif = Image.Exif()

        # ── IFD0 (main image) tags ──
        TAG_MAP = {
            'make': 0x010F,
            'model': 0x0110,
            'orientation': 0x0112,
            'software': 0x0131,
            'datetime': 0x0132,
        }

        for key, tag_id in TAG_MAP.items():
            if key in data:
                exif[tag_id] = data[key]

        # Set image dimensions in IFD0 if available
        if 'image_width' in data:
            exif[0x0100] = data['image_width']   # ImageWidth
        if 'image_height' in data:
            exif[0x0101] = data['image_height']   # ImageLength

        # ── ExifIFD tags ──
        IFD_EXIF = 0x8769
        exif_ifd = {}

        # Rational values (need IFDRational)
        RATIONAL_TAGS = {
            'exposure_time': 0x829A,
            'f_number': 0x829D,
            'focal_length': 0x920A,
        }
        for key, tag_id in RATIONAL_TAGS.items():
            if key in data:
                exif_ifd[tag_id] = IFDRational(data[key])

        # Integer values
        INT_TAGS = {
            'iso': 0x8827,                  # ISOSpeedRatings
            'exposure_program': 0x8822,     # ExposureProgram
            'metering_mode': 0x9207,        # MeteringMode
            'flash': 0x9209,                # Flash
            'color_space': 0xA001,          # ColorSpace
            'white_balance': 0xA403,        # WhiteBalance
            'scene_capture_type': 0xA406,   # SceneCaptureType
            'focal_length_35mm': 0xA405,    # FocalLengthIn35mmFilm
        }
        for key, tag_id in INT_TAGS.items():
            if key in data:
                exif_ifd[tag_id] = data[key]

        # String values
        STR_TAGS = {
            'datetime_original': 0x9003,    # DateTimeOriginal
            'datetime_digitized': 0x9004,   # DateTimeDigitized
            'subsec_time_original': 0x9291,  # SubSecTimeOriginal
            'lens_model': 0xA434,           # LensModel
        }
        for key, tag_id in STR_TAGS.items():
            if key in data:
                exif_ifd[tag_id] = str(data[key])

        # Image dimensions in ExifIFD too
        if 'image_width' in data:
            exif_ifd[0xA002] = data['image_width']   # PixelXDimension
        if 'image_height' in data:
            exif_ifd[0xA003] = data['image_height']   # PixelYDimension

        # ExifVersion (always 0232 for modern cameras)
        exif_ifd[0x9000] = b"0232"

        if exif_ifd:
            exif.get_ifd(IFD_EXIF).update(exif_ifd)

        # ── GPS IFD ──
        IFD_GPS = 0x8825
        if any(k.startswith('gps_') for k in data if k != 'gps_version'):
            gps_ifd = {}
            gps_ifd[0x0000] = b'\x02\x03\x00\x00'  # GPSVersionID

            if 'gps_lat' in data and 'gps_lat_ref' in data:
                lat = abs(data['gps_lat'])
                gps_ifd[0x0001] = data['gps_lat_ref']
                deg = int(lat)
                min_val = int((lat - deg) * 60)
                sec = ((lat - deg) * 60 - min_val) * 60
                gps_ifd[0x0002] = (
                    IFDRational(deg, 1),
                    IFDRational(min_val, 1),
                    IFDRational(int(sec * 10000), 10000),
                )

            if 'gps_lon' in data and 'gps_lon_ref' in data:
                lon = abs(data['gps_lon'])
                gps_ifd[0x0003] = data['gps_lon_ref']
                deg = int(lon)
                min_val = int((lon - deg) * 60)
                sec = ((lon - deg) * 60 - min_val) * 60
                gps_ifd[0x0004] = (
                    IFDRational(deg, 1),
                    IFDRational(min_val, 1),
                    IFDRational(int(sec * 10000), 10000),
                )

            # GPS Altitude
            if 'gps_altitude' in data:
                gps_ifd[0x0005] = 0  # AltitudeRef: above sea level
                gps_ifd[0x0006] = IFDRational(int(data['gps_altitude'] * 100), 100)

            # GPS DateStamp + TimeStamp from gps_timestamp
            if 'gps_timestamp' in data:
                ts = data['gps_timestamp']
                if hasattr(ts, 'strftime'):
                    gps_ifd[0x001D] = ts.strftime("%Y:%m:%d")  # GPSDateStamp
                    gps_ifd[0x0007] = (  # GPSTimeStamp
                        IFDRational(ts.hour, 1),
                        IFDRational(ts.minute, 1),
                        IFDRational(ts.second, 1),
                    )

            exif.get_ifd(IFD_GPS).update(gps_ifd)

        return exif.tobytes()
