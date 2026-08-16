import math
from fsf_core.handlers.image import ImageHandler
from pathlib import Path
from PIL import Image

def test():
    imgs = list(Path('/home/winston/Pictures').rglob('*.jpg'))
    if imgs:
        meta = ImageHandler.view_metadata(imgs[0])
        print("Meta:", meta.get('gps', {}).get('GPSAltitude'))
        with Image.open(imgs[0]) as img:
            print("JFIF:", img.info.get('jfif_version'))
            exif = img.getexif()
            if exif:
                ifd1 = exif.get_ifd(1)
                print("IFD1:", ifd1)
test()
