import pytest
from fsf_core.randomizer import MetadataRandomizer

@pytest.fixture
def randomizer():
    return MetadataRandomizer()

def test_random_image_exif_returns_all_keys(randomizer):
    meta = randomizer.random_image_exif()
    assert 'make' in meta
    assert 'model' in meta
    assert 'iso' in meta
    assert 'exposure_time' in meta

def test_random_image_exif_iso_is_valid_stop(randomizer):
    meta = randomizer.random_image_exif()
    assert meta['iso'] > 0

def test_random_image_exif_exposure_is_reasonable(randomizer):
    meta = randomizer.random_image_exif()
    assert 0 < meta['exposure_time'] < 30

def test_random_image_exif_with_preset(randomizer):
    meta = randomizer.random_image_exif(preset_name='iphone_15_pro')
    assert meta['make'].lower() == 'apple'
    assert 'iphone 15 pro' in meta['model'].lower()

def test_random_image_exif_with_city(randomizer):
    meta = randomizer.random_image_exif(city='tokyo')
    assert 'gps_lat' in meta

def test_random_image_exif_actual_size(randomizer):
    meta = randomizer.random_image_exif(actual_size=(640, 480))
    assert meta.get('image_width') == 640
    assert meta.get('image_height') == 480

def test_random_audio_tags_returns_keys(randomizer):
    meta = randomizer.random_audio_tags()
    assert 'title' in meta
    assert 'artist' in meta

def test_random_pdf_meta_returns_keys(randomizer):
    meta = randomizer.random_pdf_meta()
    assert 'title' in meta
    assert 'author' in meta

def test_forge_identity(randomizer):
    identity = randomizer.forge_identity()
    assert 'name' in identity
    assert 'camera' in identity
    assert 'home_city' in identity
