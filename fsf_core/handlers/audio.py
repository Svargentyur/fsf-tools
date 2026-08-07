import shutil
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TRCK, COMM, TENC, TPE2
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
from pathlib import Path
import logging
from fsf_core.exceptions import MetadataError, HandlerError

log = logging.getLogger('fsf')
SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".ogg", ".m4a", ".mp4", ".aac"}

class AudioHandler:
    """Handle audio file metadata."""
    
    @staticmethod
    def can_handle(filepath: Path) -> bool:
        return filepath.suffix.lower() in SUPPORTED_EXTENSIONS
    
    @staticmethod
    def view_metadata(filepath: Path) -> dict:
        """Extract metadata. Return dict with:
        {
            'basic': {'Format': 'MP3', 'Duration': '3:42', 'Bitrate': '320kbps', ...},
            'tags': {'Title': '...', 'Artist': '...', 'Album': '...', ...},
        }
        """
        result = {'basic': {}, 'tags': {}}
        try:
            f = mutagen.File(filepath)
            if f is None:
                return result
            if f.info:
                result['basic']['Duration'] = f"{int(f.info.length // 60)}:{int(f.info.length % 60):02d}"
                if hasattr(f.info, 'bitrate'):
                    result['basic']['Bitrate'] = f"{f.info.bitrate // 1000}kbps"
                result['basic']['Format'] = type(f).__name__
                
            if f.tags:
                for k, v in f.tags.items():
                    result['tags'][str(k)] = str(v)
        except (mutagen.MutagenError, OSError) as e:
            log.debug(f"Could not read metadata from {filepath.name}: {e}")
        return result
    
    @staticmethod
    def clean_metadata(filepath: Path, output: Path | None = None) -> Path:
        """Remove all tags from audio file."""
        out_path = output or filepath
        if out_path != filepath:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filepath, out_path)
            
        try:
            f = mutagen.File(out_path)
            if f and f.tags:
                f.delete()
                f.save()
                log.info(f"Cleaned metadata from {filepath.name}")
        except (mutagen.MutagenError, OSError) as e:
            raise HandlerError(f"Failed to clean {filepath.name}: {e}") from e
        return out_path
    
    @staticmethod
    def spoof_metadata(filepath: Path, data: dict, output: Path | None = None) -> Path:
        """Write spoofed tags. data can include:
        title, artist, album, year, genre, track, comment, encoder, album_artist
        """
        out_path = output or filepath
        if out_path != filepath:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filepath, out_path)
            
        try:
            f = mutagen.File(out_path)
            if f is None:
                return out_path
                
            ext = out_path.suffix.lower()
            if ext == '.mp3':
                # Clear old tags and add fresh ones
                f.delete()
                f = mutagen.File(out_path)
                f.add_tags()
                if 'title' in data: f.tags.add(TIT2(encoding=3, text=data['title']))
                if 'artist' in data: f.tags.add(TPE1(encoding=3, text=data['artist']))
                if 'album' in data: f.tags.add(TALB(encoding=3, text=data['album']))
                if 'year' in data: f.tags.add(TDRC(encoding=3, text=str(data['year'])))
                if 'genre' in data: f.tags.add(TCON(encoding=3, text=data['genre']))
                if 'track' in data: f.tags.add(TRCK(encoding=3, text=str(data['track'])))
                if 'comment' in data: f.tags.add(COMM(encoding=3, lang='eng', desc='', text=data['comment']))
                if 'encoder' in data: f.tags.add(TENC(encoding=3, text=data['encoder']))
                if 'album_artist' in data: f.tags.add(TPE2(encoding=3, text=data['album_artist']))
            elif ext in ('.flac', '.ogg'):
                if not f.tags:
                    f.add_tags()
                for k, v in data.items():
                    key = 'albumartist' if k == 'album_artist' else k
                    f.tags[key] = str(v)
            elif ext in ('.m4a', '.mp4'):
                if not f.tags:
                    f.add_tags()
                mapping = {
                    'title': '\xa9nam', 'artist': '\xa9ART', 'album': '\xa9alb',
                    'year': '\xa9day', 'genre': '\xa9gen', 'comment': '\xa9cmt',
                    'encoder': '\xa9too', 'album_artist': 'aART'
                }
                for k, v in data.items():
                    if k in mapping:
                        f.tags[mapping[k]] = str(v)
                    elif k == 'track':
                        try:
                            f.tags['trkn'] = [(int(v), 0)]
                        except ValueError:
                            pass
            f.save()
            log.info(f"Spoofed metadata for {filepath.name}")
        except (mutagen.MutagenError, OSError) as e:
            raise HandlerError(f"Failed to spoof metadata for {filepath.name}: {e}") from e
        return out_path
    
    @staticmethod
    def clone_metadata(source: Path, target: Path, output: Path | None = None) -> Path:
        """Copy tags from source to target."""
        out_path = output or target
        if out_path != target:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, out_path)
            
        try:
            src = mutagen.File(source)
            tgt = mutagen.File(out_path)
            if src and src.tags and tgt:
                if type(src) == type(tgt):
                    tgt.tags = src.tags
                    tgt.save()
                    log.info(f"Cloned metadata from {source.name} to {target.name}")
        except (mutagen.MutagenError, OSError) as e:
            raise HandlerError(f"Failed to clone metadata from {source.name} to {target.name}: {e}") from e
        return out_path
