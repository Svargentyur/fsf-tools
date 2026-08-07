"""File hash computation and manipulation."""
import hashlib
import logging
import os
from pathlib import Path

log = logging.getLogger('fsf')

class FileHasher:
    ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha512']
    
    @staticmethod
    def compute(filepath: Path, algorithms: list = None) -> dict:
        """Compute file hashes using specified algorithms."""
        if algorithms is None:
            algorithms = ['md5', 'sha1', 'sha256']
        
        hashers = {alg: hashlib.new(alg) for alg in algorithms}
        
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                for h in hashers.values():
                    h.update(chunk)
        
        return {alg: h.hexdigest() for alg, h in hashers.items()}
    
    @staticmethod
    def mutate_hash(filepath: Path, output: Path = None) -> dict:
        """Append random null bytes to change the file hash without affecting content.
        
        This works because most file formats ignore trailing bytes.
        Returns old and new hashes.
        """
        out_path = output or filepath
        old_hashes = FileHasher.compute(filepath)
        
        data = filepath.read_bytes()
        # Append 1-16 random bytes that won't affect file rendering
        junk = os.urandom(16)
        
        with open(out_path, 'wb') as f:
            f.write(data)
            f.write(junk)
        
        new_hashes = FileHasher.compute(out_path)
        log.info(f'Hash mutated for {filepath.name}')
        
        return {'old': old_hashes, 'new': new_hashes}
    
    @staticmethod
    def verify(filepath: Path, expected: str, algorithm: str = 'sha256') -> bool:
        """Verify file hash against expected value."""
        actual = FileHasher.compute(filepath, [algorithm])[algorithm]
        return actual == expected.lower()
