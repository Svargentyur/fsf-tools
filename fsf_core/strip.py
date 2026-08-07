"""Surgical metadata stripping — remove specific metadata categories."""
import logging
from pathlib import Path
from PIL import Image
from PIL.ExifTags import Base as ExifTags
import piexif

log = logging.getLogger('fsf')

class SurgicalStripper:
    """Remove specific categories of metadata without touching everything else."""
    
    # GPS-related EXIF IFD tags
    GPS_TAGS = {'GPSInfo'}
    
    # DateTime-related tags
    DATE_TAGS = {
        'DateTime', 'DateTimeOriginal', 'DateTimeDigitized',
        'SubSecTime', 'SubSecTimeOriginal', 'SubSecTimeDigitized',
        'GPSDateStamp', 'GPSTimeStamp'
    }
    
    # Camera identification tags
    DEVICE_TAGS = {
        'Make', 'Model', 'Software', 'BodySerialNumber',
        'LensMake', 'LensModel', 'LensSerialNumber',
        'CameraSerialNumber', 'InternalSerialNumber'
    }
    
    # Thumbnail data
    THUMBNAIL_TAGS = {'JPEGThumbnail', 'TIFFThumbnail', 'Thumbnail'}
    
    @staticmethod
    def strip_gps(filepath: Path, output: Path = None) -> bool:
        """Remove only GPS/location data from an image."""
        out_path = output or filepath
        try:
            exif_dict = piexif.load(str(filepath))
            exif_dict.pop('GPS', None)
            exif_dict['GPS'] = {}
            exif_bytes = piexif.dump(exif_dict)
            
            with Image.open(filepath) as img:
                img.save(str(out_path), exif=exif_bytes)
            
            log.info(f'Stripped GPS from {filepath.name}')
            return True
        except Exception as e:
            log.error(f'Failed to strip GPS: {e}')
            return False
    
    @staticmethod
    def strip_dates(filepath: Path, output: Path = None) -> bool:
        """Remove only date/time information from an image."""
        out_path = output or filepath
        try:
            exif_dict = piexif.load(str(filepath))
            
            # Remove date tags from 0th IFD
            date_tag_ids_0th = [piexif.ImageIFD.DateTime]
            for tag_id in date_tag_ids_0th:
                exif_dict['0th'].pop(tag_id, None)
            
            # Remove date tags from Exif IFD
            date_tag_ids_exif = [
                piexif.ExifIFD.DateTimeOriginal,
                piexif.ExifIFD.DateTimeDigitized,
                piexif.ExifIFD.SubSecTime,
                piexif.ExifIFD.SubSecTimeOriginal,
                piexif.ExifIFD.SubSecTimeDigitized,
            ]
            for tag_id in date_tag_ids_exif:
                exif_dict['Exif'].pop(tag_id, None)
            
            # Remove GPS date
            if 'GPS' in exif_dict:
                exif_dict['GPS'].pop(piexif.GPSIFD.GPSDateStamp, None)
                exif_dict['GPS'].pop(piexif.GPSIFD.GPSTimeStamp, None)
            
            exif_bytes = piexif.dump(exif_dict)
            with Image.open(filepath) as img:
                img.save(str(out_path), exif=exif_bytes)
            
            log.info(f'Stripped dates from {filepath.name}')
            return True
        except Exception as e:
            log.error(f'Failed to strip dates: {e}')
            return False
    
    @staticmethod
    def strip_device(filepath: Path, output: Path = None) -> bool:
        """Remove only camera/device identification data."""
        out_path = output or filepath
        try:
            exif_dict = piexif.load(str(filepath))
            
            device_tags_0th = [
                piexif.ImageIFD.Make,
                piexif.ImageIFD.Model,
                piexif.ImageIFD.Software,
            ]
            for tag_id in device_tags_0th:
                exif_dict['0th'].pop(tag_id, None)
            
            device_tags_exif = [
                piexif.ExifIFD.LensMake,
                piexif.ExifIFD.LensModel,
                piexif.ExifIFD.BodySerialNumber,
            ]
            for tag_id in device_tags_exif:
                exif_dict['Exif'].pop(tag_id, None)
            
            exif_bytes = piexif.dump(exif_dict)
            with Image.open(filepath) as img:
                img.save(str(out_path), exif=exif_bytes)
            
            log.info(f'Stripped device info from {filepath.name}')
            return True
        except Exception as e:
            log.error(f'Failed to strip device info: {e}')
            return False
    
    @staticmethod 
    def strip_thumbnail(filepath: Path, output: Path = None) -> bool:
        """Remove embedded thumbnail (privacy risk — may contain original crop)."""
        out_path = output or filepath
        try:
            exif_dict = piexif.load(str(filepath))
            exif_dict.pop('thumbnail', None)
            exif_dict['1st'] = {}
            exif_bytes = piexif.dump(exif_dict)
            
            with Image.open(filepath) as img:
                img.save(str(out_path), exif=exif_bytes)
            
            log.info(f'Stripped thumbnail from {filepath.name}')
            return True
        except Exception as e:
            log.error(f'Failed to strip thumbnail: {e}')
            return False
