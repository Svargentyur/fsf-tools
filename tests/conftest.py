import pytest
from pathlib import Path
from PIL import Image
import struct

@pytest.fixture
def tmp_jpg(tmp_path):
    """Create minimal JPEG test file."""
    img = Image.new('RGB', (100, 100), color='red')
    path = tmp_path / 'test.jpg'
    img.save(path, 'JPEG')
    return path

@pytest.fixture
def tmp_png(tmp_path):
    img = Image.new('RGB', (100, 100), color='blue')
    path = tmp_path / 'test.png'
    img.save(path, 'PNG')
    return path

@pytest.fixture
def tmp_mp3(tmp_path):
    """Create minimal MP3 with ID3 tags."""
    from mutagen.mp3 import MP3
    from mutagen.id3 import TIT2, TPE1
    # MPEG1 Layer3 128kbps frame
    header = b'\xff\xfb\x90\x00'
    path = tmp_path / 'test.mp3'
    path.write_bytes((header + b'\x00' * 413) * 10)
    audio = MP3(path)
    audio.add_tags()
    audio.tags.add(TIT2(encoding=3, text='Test Song'))
    audio.tags.add(TPE1(encoding=3, text='Test Artist'))
    audio.save()
    return path

@pytest.fixture
def tmp_pdf(tmp_path):
    import pikepdf
    path = tmp_path / 'test.pdf'
    pdf = pikepdf.new()
    pdf.add_blank_page(page_size=(612, 792))
    pdf.docinfo['/Author'] = 'Test Author'
    pdf.docinfo['/Title'] = 'Test Doc'
    pdf.save(path)
    return path
