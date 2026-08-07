import yaml
import logging
from pathlib import Path
from datetime import datetime
from .exceptions import FSFError

log = logging.getLogger('fsf')

DEFAULT_TEMPLATE_DIR = Path.home() / '.config' / 'fsf-tools' / 'templates'

class TemplateManager:
    def __init__(self, template_dir=None):
        self.template_dir = Path(template_dir) if template_dir else DEFAULT_TEMPLATE_DIR
        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, name: str, metadata: dict, description: str = '') -> Path:
        """Save metadata dict as a named YAML template."""
        template = {
            'name': name,
            'description': description,
            'created': datetime.now().isoformat(),
            'version': '2.1.0',
            'metadata': metadata
        }
        path = self.template_dir / f'{name}.yaml'
        with open(path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, allow_unicode=True)
        log.info(f'Saved template: {path}')
        return path
    
    def load(self, name: str) -> dict:
        """Load a template by name and return the metadata dict."""
        path = self.template_dir / f'{name}.yaml'
        if not path.exists():
            raise FSFError(f'Template not found: {name}')
        with open(path) as f:
            template = yaml.safe_load(f)
        return template.get('metadata', {})
    
    def list_templates(self) -> list:
        """List all saved templates."""
        templates = []
        for path in sorted(self.template_dir.glob('*.yaml')):
            try:
                with open(path) as f:
                    t = yaml.safe_load(f)
                templates.append({
                    'name': t.get('name', path.stem),
                    'description': t.get('description', ''),
                    'created': t.get('created', 'unknown'),
                    'file': str(path)
                })
            except Exception:
                continue
        return templates
    
    def delete(self, name: str) -> bool:
        path = self.template_dir / f'{name}.yaml'
        if path.exists():
            path.unlink()
            return True
        return False
    
    def extract_and_save(self, filepath: Path, name: str, handler, description: str = '') -> Path:
        """Extract metadata from a file and save it as a template."""
        metadata = handler.view_metadata(filepath)
        return self.save(name, metadata, description)
