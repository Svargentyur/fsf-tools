import shutil
import pikepdf
from pathlib import Path
from datetime import datetime
import logging
from fsf_core.exceptions import MetadataError, HandlerError

log = logging.getLogger('fsf')
SUPPORTED_EXTENSIONS = {".pdf"}

class PdfHandler:
    """Handle PDF metadata."""
    
    @staticmethod
    def can_handle(filepath: Path) -> bool:
        return filepath.suffix.lower() in SUPPORTED_EXTENSIONS
    
    @staticmethod
    def view_metadata(filepath: Path) -> dict:
        """Extract PDF metadata. Return dict with:
        {
            'basic': {'Pages': 42, 'PDF Version': '1.7', ...},
            'info': {'Author': '...', 'Creator': '...', 'Producer': '...', ...},
        }
        """
        result = {'basic': {}, 'info': {}}
        try:
            with pikepdf.open(filepath) as pdf:
                result['basic']['Pages'] = len(pdf.pages)
                result['basic']['PDF Version'] = pdf.pdf_version
                
                docinfo = pdf.docinfo
                for k, v in docinfo.items():
                    result['info'][str(k).replace('/', '')] = str(v)
        except (pikepdf.PdfError, OSError) as e:
            log.debug(f"Could not read metadata from {filepath.name}: {e}")
        return result
    
    @staticmethod
    def clean_metadata(filepath: Path, output: Path | None = None) -> Path:
        """Remove all metadata from PDF."""
        out_path = output or filepath
        if out_path != filepath:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            
        try:
            with pikepdf.open(filepath) as pdf:
                del pdf.docinfo
                pdf.save(out_path)
                log.info(f"Cleaned metadata from {filepath.name}")
        except (pikepdf.PdfError, OSError) as e:
            raise HandlerError(f"Failed to clean {filepath.name}: {e}") from e
        return out_path
    
    @staticmethod
    def spoof_metadata(filepath: Path, data: dict, output: Path | None = None) -> Path:
        """Write spoofed metadata. data can include:
        author, title, subject, creator, producer, creation_date, mod_date
        """
        out_path = output or filepath
        if out_path != filepath:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filepath, out_path)
            
        try:
            with pikepdf.open(out_path, allow_overwriting_input=True) as pdf:
                # Clear existing XMP metadata to avoid conflicts
                if '/Metadata' in pdf.Root:
                    del pdf.Root['/Metadata']

                # Write only to docinfo (simple and reliable)
                mapping_docinfo = {
                    'author': '/Author',
                    'title': '/Title',
                    'subject': '/Subject',
                    'creator': '/Creator',
                    'producer': '/Producer',
                    'creation_date': '/CreationDate',
                    'mod_date': '/ModDate',
                }
                for k, v in data.items():
                    if k in mapping_docinfo:
                        pdf.docinfo[mapping_docinfo[k]] = str(v)

                pdf.save(out_path)
                log.info(f"Spoofed metadata for {filepath.name}")
        except (pikepdf.PdfError, OSError) as e:
            raise HandlerError(f"Failed to spoof metadata for {filepath.name}: {e}") from e
        return out_path
    
    @staticmethod
    def clone_metadata(source: Path, target: Path, output: Path | None = None) -> Path:
        """Copy metadata from source PDF to target PDF."""
        out_path = output or target
        if out_path != target:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, out_path)
            
        try:
            with pikepdf.open(source) as src_pdf, pikepdf.open(out_path, allow_overwriting_input=True) as tgt_pdf:
                for k, v in src_pdf.docinfo.items():
                    tgt_pdf.docinfo[k] = v
                tgt_pdf.save(out_path)
                log.info(f"Cloned metadata from {source.name} to {target.name}")
        except (pikepdf.PdfError, OSError) as e:
            raise HandlerError(f"Failed to clone metadata from {source.name} to {target.name}: {e}") from e
        return out_path
