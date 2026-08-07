import os
from pathlib import Path
from datetime import datetime
from fsf_core.timestamp import sync_timestamps, get_file_timestamps

def test_sync_timestamps(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello")
    
    dt_str = "2020:01:01 12:00:00"
    sync_timestamps(file_path, dt_str)
    
    stat = file_path.stat()
    dt = datetime.fromtimestamp(stat.st_mtime)
    assert dt.strftime("%Y:%m:%d %H:%M:%S") == dt_str

def test_get_file_timestamps(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello")
    
    ts = get_file_timestamps(file_path)
    assert 'mtime' in ts
    assert 'atime' in ts
    assert 'ctime' in ts
