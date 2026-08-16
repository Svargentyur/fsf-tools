"""Pipeline system — chain multiple FSF operations."""

import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from .exceptions import FSFError

log = logging.getLogger('fsf')

DEFAULT_PIPELINE_DIR = Path.home() / '.config' / 'fsf-tools' / 'pipelines'


class PipelineStep:
    """A single step in a pipeline."""
    
    VALID_ACTIONS = [
        'clean', 'spoof', 'randomize', 'strip', 'hash', 'audit', 'template'
    ]
    
    def __init__(self, action: str, **kwargs):
        if action not in self.VALID_ACTIONS:
            raise FSFError(f"Unknown pipeline action: {action}. Valid: {', '.join(self.VALID_ACTIONS)}")
        self.action = action
        self.params = kwargs
    
    def __repr__(self):
        params_str = ', '.join(f'{k}={v}' for k, v in self.params.items())
        return f"PipelineStep({self.action}, {params_str})" if params_str else f"PipelineStep({self.action})"


class Pipeline:
    """Execute a sequence of metadata operations on a file."""
    
    def __init__(self, name: str = 'inline', steps: List[PipelineStep] = None):
        self.name = name
        self.steps = steps or []
        self.results: List[Dict[str, Any]] = []
    
    def add_step(self, action: str, **kwargs):
        self.steps.append(PipelineStep(action, **kwargs))
        return self
    
    def execute(self, filepath: Path, output: Path = None) -> List[Dict[str, Any]]:
        """Execute all steps on the given file.
        
        Returns list of result dicts: [{'step': 'clean', 'status': 'ok', 'detail': '...'}, ...]
        """
        from .handlers.image import ImageHandler
        from .handlers.audio import AudioHandler
        from .handlers.pdf import PdfHandler
        
        self.results = []
        work_path = filepath
        
        # Determine handler
        handler, ftype = None, None
        if ImageHandler.can_handle(filepath):
            handler, ftype = ImageHandler(), 'image'
        elif AudioHandler.can_handle(filepath):
            handler, ftype = AudioHandler(), 'audio'
        elif PdfHandler.can_handle(filepath):
            handler, ftype = PdfHandler(), 'pdf'
        else:
            try:
                from .handlers.office import OfficeHandler
                if OfficeHandler.can_handle(filepath):
                    handler, ftype = OfficeHandler(), 'office'
            except ImportError:
                pass
            if handler is None:
                try:
                    from .handlers.video import VideoHandler
                    if VideoHandler.can_handle(filepath):
                        handler, ftype = VideoHandler(), 'video'
                except ImportError:
                    pass
        
        if handler is None:
            raise FSFError(f"No handler found for {filepath.suffix}")
        
        # If output specified, copy file first
        if output and output != filepath:
            import shutil
            shutil.copy2(filepath, output)
            work_path = output
        
        for i, step in enumerate(self.steps):
            step_num = i + 1
            try:
                result = self._execute_step(step, work_path, handler, ftype)
                result['step_num'] = step_num
                self.results.append(result)
                log.info(f"Pipeline step {step_num}/{len(self.steps)}: {step.action} — {result['status']}")
            except Exception as e:
                self.results.append({
                    'step_num': step_num,
                    'step': step.action,
                    'status': 'error',
                    'detail': str(e),
                })
                log.error(f"Pipeline step {step_num} failed: {e}")
                # Continue to next step (don't break pipeline)
        
        return self.results
    
    def _execute_step(self, step: PipelineStep, filepath: Path,
                      handler, ftype: str) -> Dict[str, Any]:
        """Execute a single pipeline step."""
        action = step.action
        params = step.params
        
        if action == 'clean':
            handler.clean_metadata(filepath)
            return {'step': 'clean', 'status': 'ok', 'detail': 'All metadata removed'}
        
        elif action == 'spoof':
            if ftype == 'image':
                from .randomizer import MetadataRandomizer
                rng = MetadataRandomizer()
                preset = params.get('preset')
                city = params.get('city')
                scene = params.get('scene')
                exif = rng.random_image_exif(preset_name=preset, city=city, scene=scene)
                handler.spoof_metadata(filepath, exif)
                detail = f"preset={preset or 'random'}, city={city or 'random'}"
            elif ftype == 'audio':
                from .randomizer import MetadataRandomizer
                rng = MetadataRandomizer()
                tags = rng.random_audio_tags()
                handler.spoof_metadata(filepath, tags)
                detail = 'Random audio tags applied'
            else:
                from .randomizer import MetadataRandomizer
                rng = MetadataRandomizer()
                meta = rng.random_pdf_meta() if ftype == 'pdf' else {}
                handler.spoof_metadata(filepath, meta)
                detail = f'Spoofed {ftype} metadata'
            return {'step': 'spoof', 'status': 'ok', 'detail': detail}
        
        elif action == 'randomize':
            # Same as spoof but with no preset params
            if ftype == 'image':
                from .randomizer import MetadataRandomizer
                rng = MetadataRandomizer()
                exif = rng.random_image_exif()
                handler.spoof_metadata(filepath, exif)
            return {'step': 'randomize', 'status': 'ok', 'detail': 'Random metadata applied'}
        
        elif action == 'strip':
            from .strip import SurgicalStripper
            categories = params.get('categories', ['gps'])
            stripped = []
            for cat in categories:
                if cat == 'gps' and SurgicalStripper.strip_gps(filepath):
                    stripped.append('GPS')
                elif cat == 'dates' and SurgicalStripper.strip_dates(filepath):
                    stripped.append('dates')
                elif cat == 'device' and SurgicalStripper.strip_device(filepath):
                    stripped.append('device')
                elif cat == 'thumbnail' and SurgicalStripper.strip_thumbnail(filepath):
                    stripped.append('thumbnail')
            return {'step': 'strip', 'status': 'ok', 'detail': f"Stripped: {', '.join(stripped)}"}
        
        elif action == 'hash':
            from .hasher import FileHasher
            if params.get('mutate', False):
                result = FileHasher.mutate_hash(filepath)
                return {'step': 'hash', 'status': 'ok', 'detail': f"Hash mutated", 'data': result}
            else:
                hashes = FileHasher.compute(filepath)
                return {'step': 'hash', 'status': 'ok', 'detail': f"Computed hashes", 'data': hashes}
        
        elif action == 'audit':
            from .audit import ForensicAuditor
            auditor = ForensicAuditor()
            audit_result = auditor.audit(filepath)
            # v3.0: audit returns (findings, score) tuple
            if isinstance(audit_result, tuple):
                findings, score = audit_result
            else:
                findings, score = audit_result, None
            fails = sum(1 for f in findings if f['level'] == 'FAIL')
            warns = sum(1 for f in findings if f['level'] == 'WARN')
            passes = sum(1 for f in findings if f['level'] == 'PASS')
            status = 'ok' if fails == 0 else 'warning'
            score_info = f", score={score}" if score is not None else ""
            return {
                'step': 'audit', 'status': status,
                'detail': f"{passes} pass, {warns} warn, {fails} fail{score_info}",
                'data': findings
            }
        
        elif action == 'template':
            from .templates import TemplateManager
            tm = TemplateManager()
            template_name = params.get('name')
            if template_name:
                metadata = tm.load(template_name)
                handler.spoof_metadata(filepath, metadata)
                return {'step': 'template', 'status': 'ok', 'detail': f"Applied template '{template_name}'"}
            else:
                return {'step': 'template', 'status': 'error', 'detail': 'No template name specified'}
        
        return {'step': action, 'status': 'error', 'detail': 'Unknown action'}


class PipelineManager:
    """Manage saved pipeline configs."""
    
    def __init__(self, pipeline_dir: Path = None):
        self.pipeline_dir = pipeline_dir or DEFAULT_PIPELINE_DIR
        self.pipeline_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, pipeline: Pipeline, description: str = '') -> Path:
        """Save a pipeline as YAML."""
        config = {
            'name': pipeline.name,
            'description': description,
            'steps': [
                {'action': s.action, **s.params}
                for s in pipeline.steps
            ]
        }
        path = self.pipeline_dir / f"{pipeline.name}.yaml"
        with open(path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return path
    
    def load(self, name: str) -> Pipeline:
        """Load a pipeline from YAML config."""
        path = self.pipeline_dir / f"{name}.yaml"
        if not path.exists():
            raise FSFError(f"Pipeline config not found: {name}")
        
        with open(path) as f:
            config = yaml.safe_load(f)
        
        pipeline = Pipeline(name=config.get('name', name))
        for step_cfg in config.get('steps', []):
            action = step_cfg.pop('action')
            pipeline.add_step(action, **step_cfg)
        
        return pipeline
    
    def list_pipelines(self) -> list:
        """List all saved pipeline configs."""
        pipelines = []
        for path in sorted(self.pipeline_dir.glob('*.yaml')):
            try:
                with open(path) as f:
                    cfg = yaml.safe_load(f)
                pipelines.append({
                    'name': cfg.get('name', path.stem),
                    'description': cfg.get('description', ''),
                    'steps': len(cfg.get('steps', [])),
                    'file': str(path),
                })
            except Exception:
                continue
        return pipelines
    
    def delete(self, name: str) -> bool:
        path = self.pipeline_dir / f"{name}.yaml"
        if path.exists():
            path.unlink()
            return True
        return False
    
    @staticmethod
    def parse_inline(spec: str) -> Pipeline:
        """Parse an inline pipeline specification.
        
        Format: 'action1+action2:param1:param2+action3'
        Examples:
            'clean+spoof:iphone_15_pro:tokyo+audit'
            'strip:gps+hash:mutate+audit'
            'clean+randomize+audit'
        """
        pipeline = Pipeline(name='inline')
        parts = spec.split('+')
        
        for part in parts:
            tokens = part.split(':')
            action = tokens[0].strip()
            
            # Parse action-specific params
            if action == 'spoof' and len(tokens) >= 2:
                params = {}
                if len(tokens) >= 2:
                    params['preset'] = tokens[1]
                if len(tokens) >= 3:
                    params['city'] = tokens[2]
                if len(tokens) >= 4:
                    params['scene'] = tokens[3]
                pipeline.add_step(action, **params)
            elif action == 'strip' and len(tokens) >= 2:
                categories = tokens[1:]
                pipeline.add_step(action, categories=categories)
            elif action == 'hash' and len(tokens) >= 2 and tokens[1] == 'mutate':
                pipeline.add_step(action, mutate=True)
            elif action == 'template' and len(tokens) >= 2:
                pipeline.add_step(action, name=tokens[1])
            else:
                pipeline.add_step(action)
        
        return pipeline


# Built-in pipeline presets
BUILTIN_PIPELINES = {
    'paranoid': Pipeline(name='paranoid').add_step('clean').add_step(
        'spoof', preset='iphone_15_pro', city='tokyo', scene='daylight_outdoor'
    ).add_step('strip', categories=['thumbnail']).add_step(
        'hash', mutate=True
    ).add_step('audit'),
    
    'privacy': Pipeline(name='privacy').add_step(
        'strip', categories=['gps', 'device', 'thumbnail']
    ).add_step('hash', mutate=True),
    
    'quick-clean': Pipeline(name='quick-clean').add_step('clean').add_step('audit'),
}
