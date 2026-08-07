class FSFError(Exception):
    """Base exception for FSF Tools"""

class UnsupportedFormatError(FSFError):
    """File format not supported"""

class MetadataError(FSFError):
    """Error reading/writing metadata"""

class PresetNotFoundError(FSFError):
    """Preset not found"""

class HandlerError(FSFError):
    """Handler operation failed"""
