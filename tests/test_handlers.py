import pytest
from pathlib import Path
from fsf_core.handlers.image import ImageHandler
from fsf_core.handlers.audio import AudioHandler
from fsf_core.handlers.pdf import PdfHandler

def test_image_can_handle(tmp_jpg, tmp_png):
    assert ImageHandler.can_handle(tmp_jpg)
    assert ImageHandler.can_handle(tmp_png)
    assert not ImageHandler.can_handle(Path("test.txt"))

def test_image_view_metadata(tmp_jpg):
    meta = ImageHandler.view_metadata(tmp_jpg)
    assert 'basic' in meta
    assert 'exif' in meta
    assert meta['basic']['Format'] == 'JPEG'

def test_image_clean_metadata(tmp_jpg, tmp_path):
    out = tmp_path / "clean.jpg"
    res = ImageHandler.clean_metadata(tmp_jpg, out)
    assert res.exists()
    meta = ImageHandler.view_metadata(res)
    assert not meta['exif']

def test_image_spoof_metadata(tmp_jpg, tmp_path):
    out = tmp_path / "spoof.jpg"
    data = {'make': 'TestMake'}
    res = ImageHandler.spoof_metadata(tmp_jpg, data, out)
    assert res.exists()
    meta = ImageHandler.view_metadata(res)
    assert any(k == 'Make' and 'TestMake' in v for k, v in meta['exif'].items())

def test_image_clean_output(tmp_jpg, tmp_path):
    out = tmp_path / "clean2.jpg"
    res = ImageHandler.clean_metadata(tmp_jpg, out)
    assert res == out

def test_audio_can_handle(tmp_mp3):
    assert AudioHandler.can_handle(tmp_mp3)
    assert not AudioHandler.can_handle(Path("test.txt"))

def test_audio_view_metadata(tmp_mp3):
    meta = AudioHandler.view_metadata(tmp_mp3)
    assert 'basic' in meta
    assert 'tags' in meta
    assert any('Test Song' in v for v in meta['tags'].values())

def test_audio_clean_metadata(tmp_mp3, tmp_path):
    out = tmp_path / "clean.mp3"
    res = AudioHandler.clean_metadata(tmp_mp3, out)
    meta = AudioHandler.view_metadata(res)
    assert not meta['tags']

def test_audio_spoof_metadata(tmp_mp3, tmp_path):
    out = tmp_path / "spoof.mp3"
    data = {'title': 'Spoofed Song'}
    res = AudioHandler.spoof_metadata(tmp_mp3, data, out)
    meta = AudioHandler.view_metadata(res)
    assert any('Spoofed Song' in v for v in meta['tags'].values())

def test_pdf_can_handle(tmp_pdf):
    assert PdfHandler.can_handle(tmp_pdf)
    assert not PdfHandler.can_handle(Path("test.txt"))

def test_pdf_view_metadata(tmp_pdf):
    meta = PdfHandler.view_metadata(tmp_pdf)
    assert 'basic' in meta
    assert 'info' in meta
    assert meta['info'].get('Title') == 'Test Doc'

def test_pdf_clean_metadata(tmp_pdf, tmp_path):
    out = tmp_path / "clean.pdf"
    res = PdfHandler.clean_metadata(tmp_pdf, out)
    meta = PdfHandler.view_metadata(res)
    assert not meta['info']

def test_pdf_spoof_metadata(tmp_pdf, tmp_path):
    out = tmp_path / "spoof.pdf"
    data = {'title': 'Spoofed Doc'}
    res = PdfHandler.spoof_metadata(tmp_pdf, data, out)
    meta = PdfHandler.view_metadata(res)
    assert meta['info'].get('Title') == 'Spoofed Doc'
