import os
from datetime import datetime
from pathlib import Path

def sync_timestamps(filepath: Path, datetime_str: str) -> None:
    dt = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
    timestamp = dt.timestamp()
    os.utime(filepath, (timestamp, timestamp))

def get_file_timestamps(filepath: Path) -> dict:
    stat = filepath.stat()
    return {
        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y:%m:%d %H:%M:%S"),
        "atime": datetime.fromtimestamp(stat.st_atime).strftime("%Y:%m:%d %H:%M:%S"),
        "ctime": datetime.fromtimestamp(stat.st_ctime).strftime("%Y:%m:%d %H:%M:%S"),
    }
