"""Interactive TUI for FSF Tools using Textual."""

import os
import sys
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Static, Button, Label,
    Tree, DataTable, Input, RichLog,
)
from textual.binding import Binding
from textual.screen import ModalScreen
from textual import on
from rich.text import Text
from rich.table import Table

from .handlers.image import ImageHandler
from .handlers.audio import AudioHandler
from .handlers.pdf import PdfHandler
from . import ui as fsf_ui


def _get_handler(filepath: Path):
    """Return appropriate handler for file."""
    if ImageHandler.can_handle(filepath):
        return ImageHandler(), 'image'
    if AudioHandler.can_handle(filepath):
        return AudioHandler(), 'audio'
    if PdfHandler.can_handle(filepath):
        return PdfHandler(), 'pdf'
    try:
        from .handlers.office import OfficeHandler
        if OfficeHandler.can_handle(filepath):
            return OfficeHandler(), 'office'
    except ImportError:
        pass
    try:
        from .handlers.video import VideoHandler
        if VideoHandler.can_handle(filepath):
            return VideoHandler(), 'video'
    except ImportError:
        pass
    return None, None


SUPPORTED_EXTS = {
    '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp',
    '.mp3', '.flac', '.ogg', '.m4a', '.aac',
    '.pdf', '.docx', '.xlsx', '.pptx',
    '.mp4', '.mov', '.m4v', '.mkv', '.avi', '.webm',
}


class ActionConfirmScreen(ModalScreen):
    """Modal confirmation for destructive actions."""
    
    def __init__(self, action: str, filepath: str):
        super().__init__()
        self.action_name = action
        self.filepath_str = filepath
    
    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"Confirm: {self.action_name} on {self.filepath_str}?", id="confirm-label"),
            Horizontal(
                Button("Yes", variant="success", id="btn-yes"),
                Button("Cancel", variant="error", id="btn-cancel"),
                id="confirm-buttons",
            ),
            id="confirm-dialog",
        )
    
    @on(Button.Pressed, "#btn-yes")
    def on_yes(self) -> None:
        self.dismiss(True)
    
    @on(Button.Pressed, "#btn-cancel")
    def on_cancel(self) -> None:
        self.dismiss(False)


class FSFApp(App):
    """FSF Tools — Interactive Terminal UI."""
    
    TITLE = "FSF Tools v3.0"
    SUB_TITLE = "File Sanitization Framework"
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main-container {
        layout: horizontal;
        height: 1fr;
    }
    
    #file-panel {
        width: 35;
        min-width: 25;
        border: solid $primary;
        background: $surface;
    }
    
    #file-panel-title {
        text-style: bold;
        color: $text;
        text-align: center;
        padding: 1 0;
        background: $primary-background;
    }
    
    #detail-panel {
        width: 1fr;
        border: solid $secondary;
        background: $surface;
    }
    
    #detail-title {
        text-style: bold;
        color: $text;
        text-align: center;
        padding: 1 0;
        background: $secondary-background;
    }
    
    #metadata-table {
        height: 1fr;
    }
    
    #action-bar {
        dock: bottom;
        height: 3;
        background: $panel;
        layout: horizontal;
        padding: 0 1;
    }
    
    #action-bar Button {
        margin: 0 1;
    }
    
    #log-panel {
        dock: bottom;
        height: 8;
        border-top: solid $accent;
        background: $surface;
    }
    
    #confirm-dialog {
        align: center middle;
        width: 50;
        height: 10;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }
    
    #confirm-label {
        text-align: center;
        padding: 1;
        text-style: bold;
    }
    
    #confirm-buttons {
        align: center middle;
        height: 3;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "clean_file", "Clean"),
        Binding("r", "randomize_file", "Randomize"),
        Binding("a", "audit_file", "Audit"),
        Binding("h", "hash_file", "Hash"),
        Binding("d", "refresh_view", "Refresh"),
    ]
    
    def __init__(self, directory: str = "."):
        super().__init__()
        self.work_dir = Path(directory).resolve()
        self.current_file: Optional[Path] = None
        self.current_handler = None
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            with Vertical(id="file-panel"):
                yield Label("📁 Files", id="file-panel-title")
                yield Tree(str(self.work_dir), id="file-tree")
            
            with Vertical(id="detail-panel"):
                yield Label("📋 Metadata", id="detail-title")
                yield DataTable(id="metadata-table")
        
        with Horizontal(id="action-bar"):
            yield Button("🧹 Clean [C]", variant="error", id="btn-clean")
            yield Button("🎲 Random [R]", variant="warning", id="btn-random")
            yield Button("🕵️ Audit [A]", variant="primary", id="btn-audit")
            yield Button("🔑 Hash [H]", variant="default", id="btn-hash")
        
        yield RichLog(id="log-panel", highlight=True, markup=True)
        yield Footer()
    
    def on_mount(self) -> None:
        """Populate file tree on startup."""
        tree = self.query_one("#file-tree", Tree)
        tree.root.expand()
        self._populate_tree(tree.root, self.work_dir)
        
        table = self.query_one("#metadata-table", DataTable)
        table.add_columns("Field", "Value")
        
        log = self.query_one("#log-panel", RichLog)
        log.write("[bold cyan]FSF Tools TUI[/bold cyan] — Select a file to view metadata")
        log.write("[dim]Hotkeys: C=Clean, R=Randomize, A=Audit, H=Hash, Q=Quit[/dim]")
    
    def _populate_tree(self, node, path: Path, depth: int = 0):
        """Recursively populate file tree with supported files."""
        if depth > 3:  # Limit depth
            return
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return
        
        for entry in entries:
            if entry.name.startswith('.'):
                continue
            if entry.is_dir():
                branch = node.add(f"📂 {entry.name}", data=str(entry))
                self._populate_tree(branch, entry, depth + 1)
            elif entry.suffix.lower() in SUPPORTED_EXTS:
                icon = self._get_file_icon(entry.suffix.lower())
                node.add_leaf(f"{icon} {entry.name}", data=str(entry))
    
    def _get_file_icon(self, ext: str) -> str:
        if ext in {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp'}:
            return '🖼️'
        if ext in {'.mp3', '.flac', '.ogg', '.m4a', '.aac'}:
            return '🎵'
        if ext == '.pdf':
            return '📄'
        if ext in {'.docx', '.xlsx', '.pptx'}:
            return '📊'
        if ext in {'.mp4', '.mov', '.m4v', '.mkv', '.avi', '.webm'}:
            return '🎬'
        return '📎'
    
    @on(Tree.NodeSelected)
    def on_tree_select(self, event: Tree.NodeSelected) -> None:
        """When a file is selected in the tree."""
        if event.node.data is None:
            return
        filepath = Path(event.node.data)
        if filepath.is_file():
            self.current_file = filepath
            self._load_metadata(filepath)
    
    def _load_metadata(self, filepath: Path) -> None:
        """Load and display metadata for selected file."""
        handler, ftype = _get_handler(filepath)
        self.current_handler = handler
        
        title = self.query_one("#detail-title", Label)
        table = self.query_one("#metadata-table", DataTable)
        log_widget = self.query_one("#log-panel", RichLog)
        
        table.clear()
        
        if not handler:
            title.update(f"❌ Unsupported: {filepath.name}")
            log_widget.write(f"[red]Unsupported format: {filepath.suffix}[/red]")
            return
        
        title.update(f"📋 {filepath.name} [{ftype}]")
        
        try:
            metadata = handler.view_metadata(filepath)
            for category, data in metadata.items():
                if not data:
                    continue
                # Category header
                table.add_row(
                    Text(f"━━ {category.upper()} ━━", style="bold magenta"),
                    Text("", style="dim"),
                )
                for key, value in data.items():
                    val_str = str(value)
                    # Color code by type
                    if any(g in key.lower() for g in ['gps', 'lat', 'lon', 'altitude']):
                        style = "yellow"
                    elif any(d in key.lower() for d in ['date', 'time', 'created', 'modified']):
                        style = "green"
                    elif any(c in key.lower() for c in ['make', 'model', 'camera', 'software', 'lens']):
                        style = "cyan"
                    else:
                        style = "white"
                    
                    table.add_row(
                        Text(str(key), style="bold cyan"),
                        Text(val_str[:80], style=style),
                    )
            
            field_count = sum(len(d) for d in metadata.values())
            log_widget.write(f"[green]✓ Loaded {field_count} fields from {filepath.name}[/green]")
        except Exception as e:
            log_widget.write(f"[red]Error reading {filepath.name}: {e}[/red]")
    
    # ─── Actions ───
    
    def _require_file(self) -> bool:
        if not self.current_file:
            log_widget = self.query_one("#log-panel", RichLog)
            log_widget.write("[yellow]⚠ No file selected[/yellow]")
            return False
        return True
    
    def action_clean_file(self) -> None:
        if not self._require_file():
            return
        self.push_screen(
            ActionConfirmScreen("Clean ALL metadata", self.current_file.name),
            callback=self._do_clean
        )
    
    def _do_clean(self, confirmed: bool) -> None:
        if not confirmed or not self.current_file:
            return
        log_widget = self.query_one("#log-panel", RichLog)
        try:
            handler, _ = _get_handler(self.current_file)
            if handler:
                handler.clean_metadata(self.current_file)
                log_widget.write(f"[green]✓ Cleaned all metadata from {self.current_file.name}[/green]")
                self._load_metadata(self.current_file)
        except Exception as e:
            log_widget.write(f"[red]✗ Clean failed: {e}[/red]")
    
    def action_randomize_file(self) -> None:
        if not self._require_file():
            return
        log_widget = self.query_one("#log-panel", RichLog)
        try:
            handler, ftype = _get_handler(self.current_file)
            if handler and ftype == 'image':
                from .randomizer import MetadataRandomizer
                rng = MetadataRandomizer()
                exif = rng.random_image_exif()
                handler.spoof_metadata(self.current_file, exif)
                log_widget.write(f"[green]✓ Randomized metadata for {self.current_file.name}[/green]")
                self._load_metadata(self.current_file)
            else:
                log_widget.write(f"[yellow]⚠ Randomize only supports images currently[/yellow]")
        except Exception as e:
            log_widget.write(f"[red]✗ Randomize failed: {e}[/red]")
    
    def action_audit_file(self) -> None:
        if not self._require_file():
            return
        log_widget = self.query_one("#log-panel", RichLog)
        try:
            from .audit import ForensicAuditor
            auditor = ForensicAuditor()
            audit_result = auditor.audit(self.current_file)
            if isinstance(audit_result, tuple):
                findings, score = audit_result
            else:
                findings, score = audit_result, None
            if not findings:
                score_msg = f" (Score: {score}/100)" if score is not None else ""
                log_widget.write(f"[green]✓ Audit PASSED — no issues found in {self.current_file.name}{score_msg}[/green]")
            else:
                score_msg = f" Score: {score}/100" if score is not None else ""
                log_widget.write(f"[bold cyan]Audit Results{score_msg}:[/bold cyan]")
                for f in findings:
                    icon = {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌'}.get(f['level'], '•')
                    color = {'PASS': 'green', 'WARN': 'yellow', 'FAIL': 'red'}.get(f['level'], 'white')
                    log_widget.write(f"[{color}]{icon} {f['check']}: {f['detail']}[/{color}]")
        except Exception as e:
            log_widget.write(f"[red]✗ Audit failed: {e}[/red]")
    
    def action_hash_file(self) -> None:
        if not self._require_file():
            return
        log_widget = self.query_one("#log-panel", RichLog)
        try:
            from .hasher import FileHasher
            hashes = FileHasher.compute(self.current_file)
            log_widget.write(f"[bold cyan]Hashes for {self.current_file.name}:[/bold cyan]")
            for alg, val in hashes.items():
                log_widget.write(f"  [cyan]{alg.upper()}[/cyan]: {val}")
        except Exception as e:
            log_widget.write(f"[red]✗ Hash failed: {e}[/red]")
    
    def action_refresh_view(self) -> None:
        if self.current_file:
            self._load_metadata(self.current_file)
    
    @on(Button.Pressed, "#btn-clean")
    def on_btn_clean(self) -> None:
        self.action_clean_file()
    
    @on(Button.Pressed, "#btn-random")
    def on_btn_random(self) -> None:
        self.action_randomize_file()
    
    @on(Button.Pressed, "#btn-audit")
    def on_btn_audit(self) -> None:
        self.action_audit_file()
    
    @on(Button.Pressed, "#btn-hash")
    def on_btn_hash(self) -> None:
        self.action_hash_file()


def run_tui(directory: str = "."):
    """Launch the FSF Tools TUI."""
    app = FSFApp(directory=directory)
    app.run()
