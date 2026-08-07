from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import box

from fsf_core import __version__

console = Console()

VERSION = __version__

BANNER = r"""
 ███████╗███████╗███████╗  ████████╗ ██████╗  ██████╗ ██╗     ███████╗
 ██╔════╝██╔════╝██╔════╝  ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
 █████╗  ███████╗█████╗       ██║   ██║   ██║██║   ██║██║     ███████╗
 ██╔══╝  ╚════██║██╔══╝       ██║   ██║   ██║██║   ██║██║     ╚════██║
 ██║     ███████║██║          ██║   ╚██████╔╝╚██████╔╝███████╗███████║
 ╚═╝     ╚══════╝╚═╝          ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
"""

def print_banner():
    """Print the FSF Tools banner with gradient colors."""
    # Use Rich Text with styles to create gradient effect
    # Magenta -> Cyan gradient on the ASCII art
    lines = BANNER.strip().split('\n')
    colors = ['bright_magenta', 'magenta', 'purple4', 'blue', 'cyan', 'bright_cyan']
    text = Text()
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        text.append(line + '\n', style=color)
    console.print(text)
    console.print(f"  [dim]File Sanitization Framework v{VERSION}[/dim]")
    console.print(f"  [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]\n")

def print_metadata_table(metadata: dict, filepath: str):
    """Display metadata in a beautiful rich table.
    metadata is a dict of categories -> {key: value} pairs.
    Example: {'basic': {'Format': 'JPEG', ...}, 'exif': {'Make': 'Apple', ...}}
    """
    # Create a panel for each category
    for category, data in metadata.items():
        if not data:
            continue
        table = Table(
            show_header=True,
            header_style="bold bright_cyan",
            border_style="dim",
            box=box.ROUNDED,
            title=f"[bold]{category.upper()}[/bold]",
            title_style="bold magenta",
            expand=True,
        )
        table.add_column("Field", style="cyan", min_width=20)
        table.add_column("Value", style="white")
        for key, value in data.items():
            table.add_row(str(key), str(value))
        console.print(table)
        console.print()

def print_success(message: str):
    console.print(f"  [bold green]✓[/bold green] {message}")

def print_error(message: str):
    console.print(f"  [bold red]✗[/bold red] {message}")

def print_warning(message: str):
    console.print(f"  [bold yellow]⚠[/bold yellow] {message}")

def print_info(message: str):
    console.print(f"  [bold blue]ℹ[/bold blue] {message}")

def print_file_header(filepath: str):
    """Print a styled header showing the file being processed."""
    console.print(Panel(
        f"[bold white]{filepath}[/bold white]",
        title="[bold cyan]📄 Target File[/bold cyan]",
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print()

def create_progress():
    """Create a Rich progress bar for batch operations."""
    return Progress(
        SpinnerColumn("dots", style="cyan"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40, style="cyan", complete_style="bright_cyan"),
        TaskProgressColumn(),
        TextColumn("[dim]{task.fields[status]}", justify="right"),
        console=console,
    )

def print_risk_report(risks: list, overall_score: int, filepath: str):
    """Display privacy risk report.
    risks: list of dicts with keys: field, value, risk_level ('high'/'medium'/'low'), description
    overall_score: 0-100 risk score
    """
    # Color based on score
    if overall_score >= 70:
        score_color = "red"
        score_label = "HIGH RISK"
        score_emoji = "🔴"
    elif overall_score >= 40:
        score_color = "yellow"
        score_label = "MEDIUM RISK"
        score_emoji = "🟡"
    else:
        score_color = "green"
        score_label = "LOW RISK"
        score_emoji = "🟢"
    
    # Overall score panel
    score_text = Text()
    score_text.append(f"\n  {score_emoji} Privacy Risk Score: ", style="bold")
    score_text.append(f"{overall_score}/100", style=f"bold {score_color}")
    score_text.append(f"  [{score_label}]\n", style=f"bold {score_color}")
    console.print(Panel(score_text, border_style=score_color, title="[bold]Privacy Analysis[/bold]"))
    
    # Risk items table
    if risks:
        table = Table(
            show_header=True,
            header_style="bold bright_cyan",
            border_style="dim",
            box=box.ROUNDED,
            expand=True,
        )
        table.add_column("Risk", style="bold", min_width=6)
        table.add_column("Field", style="cyan", min_width=15)
        table.add_column("Value", style="white", min_width=20)
        table.add_column("Description", style="dim")
        
        risk_icons = {'high': '[bold red]HIGH[/bold red]', 'medium': '[bold yellow]MED[/bold yellow]', 'low': '[green]LOW[/green]'}
        for risk in risks:
            table.add_row(
                risk_icons.get(risk['risk_level'], risk['risk_level']),
                risk['field'],
                str(risk['value']),
                risk['description'],
            )
        console.print(table)

def print_diff(before: dict, after: dict):
    """Show diff between before and after metadata in dry-run mode."""
    table = Table(
        title="[bold]Metadata Changes Preview[/bold]",
        title_style="bold magenta",
        show_header=True,
        header_style="bold bright_cyan",
        border_style="dim",
        box=box.ROUNDED,
        expand=True,
    )
    table.add_column("Field", style="cyan")
    table.add_column("Before", style="red")
    table.add_column("After", style="green")
    
    all_keys = set()
    for cat_data in before.values():
        all_keys.update(cat_data.keys())
    for cat_data in after.values():
        all_keys.update(cat_data.keys())
    
    for key in sorted(all_keys):
        old_val = None
        new_val = None
        for cat_data in before.values():
            if key in cat_data:
                old_val = cat_data[key]
        for cat_data in after.values():
            if key in cat_data:
                new_val = cat_data[key]
        if str(old_val) != str(new_val):
            table.add_row(key, str(old_val or '—'), str(new_val or '—'))
    
    console.print(table)
