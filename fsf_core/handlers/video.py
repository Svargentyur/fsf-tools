"""Video file metadata handler."""
import shutil
import mutagen
from mutagen.mp4 import MP4
from pathlib import Path
import logging
import subprocess
import json as json_mod
from fsf_core.exceptions import MetadataError, HandlerError

log = logging.getLogger('fsf')

# Video extensions — .mp4/.m4v/.mov use mutagen, others use ffprobe
MUTAGEN_EXTENSIONS = {".mp4", ".m4v", ".mov"}
FFPROBE_EXTENSIONS = {".mkv", ".avi", ".webm", ".flv", ".wmv"}
SUPPORTED_EXTENSIONS = MUTAGEN_EXTENSIONS | FFPROBE_EXTENSIONS


def _has_ffprobe() -> bool:
    """Check if ffprobe is available on PATH."""
    try:
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


class VideoHandler:
    """Handle video file metadata (MP4/MOV via mutagen, others via ffprobe)."""
    
    @staticmethod
    def can_handle(filepath: Path) -> bool:
        ext = filepath.suffix.lower()
        if ext in MUTAGEN_EXTENSIONS:
            return True
        if ext in FFPROBE_EXTENSIONS:
            return _has_ffprobe()
        return False
    
    @staticmethod
    def view_metadata(filepath: Path) -> dict:
        """Extract metadata from video file.
        Returns dict: {'basic': {...}, 'tags': {...}}
        """
        result = {'basic': {}, 'tags': {}}
        ext = filepath.suffix.lower()
        
        if ext in MUTAGEN_EXTENSIONS:
            try:
                f = mutagen.File(filepath)
                if f is None:
                    return result
                if f.info:
                    result['basic']['Duration'] = f"{int(f.info.length // 60)}:{int(f.info.length % 60):02d}"
                    if hasattr(f.info, 'bitrate') and f.info.bitrate:
                        result['basic']['Bitrate'] = f"{f.info.bitrate // 1000}kbps"
                    if hasattr(f.info, 'codec'):
                        result['basic']['Codec'] = f.info.codec or 'unknown'
                    result['basic']['Format'] = 'MP4/MOV'
                
                # MP4 tags use a specific atom-based system
                if isinstance(f, MP4) and f.tags:
                    tag_map = {
                        '\xa9nam': 'Title',
                        '\xa9ART': 'Artist',
                        '\xa9alb': 'Album',
                        '\xa9day': 'Date',
                        '\xa9cmt': 'Comment',
                        '\xa9gen': 'Genre',
                        '\xa9too': 'Encoder',
                        '\xa9wrt': 'Writer',
                        'desc': 'Description',
                        '\xa9grp': 'Group',
                        'cprt': 'Copyright',
                        'aART': 'Album Artist',
                        'purd': 'Purchase Date',
                    }
                    for atom, label in tag_map.items():
                        if atom in f.tags:
                            val = f.tags[atom]
                            result['tags'][label] = str(val[0]) if isinstance(val, list) else str(val)
                    
                    # GPS data (if present, e.g. from iPhone videos)
                    if '\xa9xyz' in f.tags:
                        result['tags']['GPS'] = str(f.tags['\xa9xyz'][0])
                
            except Exception as e:
                log.warning(f"Failed to read MP4 metadata: {e}")
        
        elif ext in FFPROBE_EXTENSIONS and _has_ffprobe():
            try:
                cmd = [
                    'ffprobe', '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_format', '-show_streams',
                    str(filepath)
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if proc.returncode == 0:
                    data = json_mod.loads(proc.stdout)
                    fmt = data.get('format', {})
                    result['basic']['Format'] = fmt.get('format_long_name', 'unknown')
                    duration = float(fmt.get('duration', 0))
                    result['basic']['Duration'] = f"{int(duration // 60)}:{int(duration % 60):02d}"
                    bitrate = int(fmt.get('bit_rate', 0))
                    if bitrate:
                        result['basic']['Bitrate'] = f"{bitrate // 1000}kbps"
                    result['basic']['Size'] = fmt.get('size', 'unknown')
                    
                    # Stream info
                    for stream in data.get('streams', []):
                        if stream.get('codec_type') == 'video':
                            result['basic']['Video Codec'] = stream.get('codec_name', '')
                            result['basic']['Resolution'] = f"{stream.get('width', '?')}x{stream.get('height', '?')}"
                            result['basic']['FPS'] = stream.get('r_frame_rate', '')
                        elif stream.get('codec_type') == 'audio':
                            result['basic']['Audio Codec'] = stream.get('codec_name', '')
                            result['basic']['Sample Rate'] = stream.get('sample_rate', '')
                    
                    # Tags from format
                    tags = fmt.get('tags', {})
                    for k, v in tags.items():
                        result['tags'][k] = str(v)
            except Exception as e:
                log.warning(f"ffprobe failed: {e}")
        
        return result
    
    @staticmethod
    def clean_metadata(filepath: Path, output: Path = None) -> Path:
        """Remove all metadata from video file."""
        out_path = output or filepath
        ext = filepath.suffix.lower()
        
        if ext in MUTAGEN_EXTENSIONS:
            if output and filepath != out_path:
                shutil.copy2(filepath, out_path)
            try:
                f = mutagen.File(out_path)
                if f and f.tags:
                    f.tags.clear()
                    f.save()
                log.info(f"Cleaned metadata from {out_path.name}")
            except Exception as e:
                raise HandlerError(f"Failed to clean video metadata: {e}")
        
        elif ext in FFPROBE_EXTENSIONS and _has_ffprobe():
            # Use ffmpeg to strip metadata
            try:
                tmp = out_path.with_suffix('.tmp' + ext)
                cmd = [
                    'ffmpeg', '-y', '-i', str(filepath),
                    '-map_metadata', '-1', '-c', 'copy',
                    str(tmp)
                ]
                subprocess.run(cmd, capture_output=True, check=True, timeout=60)
                shutil.move(str(tmp), str(out_path))
                log.info(f"Cleaned metadata from {out_path.name} (ffmpeg)")
            except Exception as e:
                if tmp.exists():
                    tmp.unlink()
                raise HandlerError(f"Failed to clean video metadata via ffmpeg: {e}")
        
        return out_path
    
    @staticmethod
    def spoof_metadata(filepath: Path, data: dict, output: Path = None) -> Path:
        """Spoof metadata on video file.
        
        data keys: title, artist, album, date, comment, encoder,
                   description, genre, copyright, writer
        """
        out_path = output or filepath
        ext = filepath.suffix.lower()
        
        if ext in MUTAGEN_EXTENSIONS:
            if output and filepath != out_path:
                shutil.copy2(filepath, out_path)
            try:
                f = MP4(out_path)
                if f.tags is None:
                    f.add_tags()
                
                tag_map = {
                    'title': '\xa9nam',
                    'artist': '\xa9ART',
                    'album': '\xa9alb',
                    'date': '\xa9day',
                    'comment': '\xa9cmt',
                    'genre': '\xa9gen',
                    'encoder': '\xa9too',
                    'writer': '\xa9wrt',
                    'description': 'desc',
                    'copyright': 'cprt',
                    'album_artist': 'aART',
                }
                
                for key, atom in tag_map.items():
                    if key in data:
                        f.tags[atom] = [str(data[key])]
                
                f.save()
                log.info(f"Spoofed metadata on {out_path.name}")
            except Exception as e:
                raise HandlerError(f"Failed to spoof video metadata: {e}")
        else:
            raise HandlerError(f"Spoofing not supported for {ext} (only MP4/MOV/M4V)")
        
        return out_path
