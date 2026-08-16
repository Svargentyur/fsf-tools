"""FSF Tools CLI — File Sanitization Framework."""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .handlers.image import ImageHandler
from .handlers.audio import AudioHandler
from .handlers.pdf import PdfHandler
from .randomizer import MetadataRandomizer
from .reporter import PrivacyReporter
from .presets import CAMERA_PRESETS, CITY_PRESETS
from .logger import setup_logging
from .exceptions import FSFError, HandlerError, UnsupportedFormatError
from .timestamp import sync_timestamps
from . import ui

log = logging.getLogger('fsf')

# Lazy import for optional handlers
_office_handler = None
def _get_office_handler():
    global _office_handler
    if _office_handler is None:
        try:
            from .handlers.office import OfficeHandler
            _office_handler = OfficeHandler
        except ImportError:
            _office_handler = False
    return _office_handler if _office_handler else None


# Lazy import for video handler
_video_handler = None
def _get_video_handler():
    global _video_handler
    if _video_handler is None:
        try:
            from .handlers.video import VideoHandler
            _video_handler = VideoHandler
        except ImportError:
            _video_handler = False
    return _video_handler if _video_handler else None


def _get_handler(filepath: Path):
    """Return the appropriate handler for a file, or (None, None)."""
    if ImageHandler.can_handle(filepath):
        return ImageHandler(), 'image'
    if AudioHandler.can_handle(filepath):
        return AudioHandler(), 'audio'
    if PdfHandler.can_handle(filepath):
        return PdfHandler(), 'pdf'
    OfficeHandler = _get_office_handler()
    if OfficeHandler and OfficeHandler.can_handle(filepath):
        return OfficeHandler(), 'office'
    VideoHandler = _get_video_handler()
    if VideoHandler and VideoHandler.can_handle(filepath):
        return VideoHandler(), 'video'
    return None, None


def _validate_file(filepath: str) -> Path:
    """Validate that file exists and return Path."""
    p = Path(filepath).resolve()
    if not p.is_file():
        ui.print_error(f"File not found: {filepath}")
        sys.exit(1)
    return p


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(ui.VERSION, prog_name="FSF Tools")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose/debug output")
@click.option("-q", "--quiet", is_flag=True, help="Suppress all output except errors")
def cli(ctx, verbose, quiet):
    """FSF Tools — File Sanitization Framework.

    A powerful CLI utility for viewing, cleaning, spoofing, and cloning
    file metadata across images, audio, PDF, and Office formats.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    setup_logging(verbose=verbose, quiet=quiet)
    if quiet:
        ui.console.quiet = True
    if ctx.invoked_subcommand is None:
        ui.print_banner()
        click.echo(ctx.get_help())



# ─────────────────────────────────────────────────────
#  VIEW command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output metadata as JSON")
def view(file: str, as_json: bool):
    """View all metadata of a file."""
    filepath = _validate_file(file)
    handler, ftype = _get_handler(filepath)

    if not handler:
        ui.print_error(f"Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    ui.print_banner()
    ui.print_file_header(str(filepath))

    metadata = handler.view_metadata(filepath)

    if as_json:
        ui.console.print_json(json.dumps(metadata, indent=2, ensure_ascii=False, default=str))
    else:
        ui.print_metadata_table(metadata, str(filepath))

    # Quick privacy note
    reporter = PrivacyReporter()
    risks, score = reporter.analyze(metadata, ftype)
    if score > 0:
        if score >= 70:
            ui.print_warning(f"Privacy Risk: [bold red]{score}/100[/bold red] — run [cyan]fsf report {file}[/cyan] for details")
        elif score >= 40:
            ui.print_warning(f"Privacy Risk: [bold yellow]{score}/100[/bold yellow] — run [cyan]fsf report {file}[/cyan] for details")
        else:
            ui.print_info(f"Privacy Risk: [green]{score}/100[/green]")


# ─────────────────────────────────────────────────────
#  CLEAN command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file (default: overwrite)")
@click.option("--dry-run", is_flag=True, help="Show what would be removed without modifying")
def clean(file: str, output: Optional[str], dry_run: bool):
    """Strip ALL metadata from a file."""
    filepath = _validate_file(file)
    handler, ftype = _get_handler(filepath)

    if not handler:
        ui.print_error(f"Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    ui.print_banner()
    ui.print_file_header(str(filepath))

    # Show current metadata
    before = handler.view_metadata(filepath)
    has_metadata = any(bool(v) for k, v in before.items() if k != 'basic')

    if not has_metadata:
        ui.print_success("File is already clean — no metadata found!")
        return

    if dry_run:
        ui.print_info("[bold]Dry-run mode[/bold] — showing metadata that would be removed:\n")
        ui.print_metadata_table(before, str(filepath))
        ui.print_warning("No changes made (dry-run)")
        return

    out_path = Path(output).resolve() if output else None
    result = handler.clean_metadata(filepath, out_path)

    # Verify
    after = handler.view_metadata(result)
    after_meta = any(bool(v) for k, v in after.items() if k != 'basic')

    if not after_meta:
        ui.print_success(f"Metadata cleaned successfully → [cyan]{result}[/cyan]")
    else:
        ui.print_warning(f"Some metadata may remain in [cyan]{result}[/cyan]")


# ─────────────────────────────────────────────────────
#  SPOOF command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file (default: overwrite)")
@click.option("--preset", type=str, default=None, help="Camera preset name (e.g. iphone_15_pro, canon_eos_r5)")
@click.option("--city", type=str, default=None, help="City for GPS coordinates (e.g. tokyo, paris)")
@click.option("--make", type=str, default=None, help="Camera make")
@click.option("--model", type=str, default=None, help="Camera model")
@click.option("--software", type=str, default=None, help="Software")
@click.option("--date", "datetime_str", type=str, default=None, help="Date/time (YYYY:MM:DD HH:MM:SS)")
@click.option("--author", type=str, default=None, help="Author (for PDF)")
@click.option("--title", type=str, default=None, help="Title (for audio/PDF)")
@click.option("--artist", type=str, default=None, help="Artist (for audio)")
@click.option("--album", type=str, default=None, help="Album (for audio)")
@click.option("--genre", type=str, default=None, help="Genre (for audio)")
@click.option("--year", type=str, default=None, help="Year (for audio/PDF)")
@click.option("--sync-time", is_flag=True, help="Sync file timestamps (mtime/atime) to match metadata")
@click.option("--dry-run", is_flag=True, help="Show what would change without modifying")
def spoof(file: str, output: Optional[str], preset: Optional[str], city: Optional[str],
          make: Optional[str], model: Optional[str], software: Optional[str],
          datetime_str: Optional[str], author: Optional[str], title: Optional[str],
          artist: Optional[str], album: Optional[str], genre: Optional[str],
          year: Optional[str], sync_time: bool, dry_run: bool):
    """Spoof metadata of a file with custom values."""
    filepath = _validate_file(file)
    handler, ftype = _get_handler(filepath)

    if not handler:
        ui.print_error(f"Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    ui.print_banner()
    ui.print_file_header(str(filepath))

    # Build spoof data
    data = {}

    if ftype == 'image':
        # Apply camera preset if specified
        if preset:
            if preset not in CAMERA_PRESETS:
                ui.print_error(f"Unknown preset: {preset}")
                ui.print_info(f"Available: {', '.join(CAMERA_PRESETS.keys())}")
                sys.exit(1)
            cam = CAMERA_PRESETS[preset]
            data['make'] = cam['make']
            data['model'] = cam['model']
            data['software'] = cam.get('software', '')

        # Apply GPS city
        if city:
            if city not in CITY_PRESETS:
                ui.print_error(f"Unknown city: {city}")
                ui.print_info(f"Available: {', '.join(CITY_PRESETS.keys())}")
                sys.exit(1)
            city_data = CITY_PRESETS[city]
            data['gps_lat'] = abs(city_data['lat'])
            data['gps_lon'] = abs(city_data['lon'])
            data['gps_lat_ref'] = city_data['lat_ref']
            data['gps_lon_ref'] = city_data['lon_ref']

        # Manual overrides
        if make: data['make'] = make
        if model: data['model'] = model
        if software: data['software'] = software
        if datetime_str:
            data['datetime'] = datetime_str
            data['datetime_original'] = datetime_str
            data['datetime_digitized'] = datetime_str

    elif ftype == 'audio':
        if title: data['title'] = title
        if artist: data['artist'] = artist
        if album: data['album'] = album
        if genre: data['genre'] = genre
        if year: data['year'] = year

    elif ftype == 'pdf':
        if author: data['author'] = author
        if title: data['title'] = title
        if software: data['creator'] = software
        if year: data['creation_date'] = f"D:{year}0101000000"

    elif ftype == 'office':
        if author: data['author'] = author
        if title: data['title'] = title
        if software: data['company'] = software

    if not data:
        ui.print_error("No spoof data specified. Use --preset, --make, --model, etc.")
        ui.print_info("Run [cyan]fsf spoof --help[/cyan] to see all options")
        sys.exit(1)

    if dry_run:
        ui.print_info("[bold]Dry-run mode[/bold] — preview of changes:\n")
        before = handler.view_metadata(filepath)
        # Build a fake "after" to show diff
        after = {'spoofed': data}
        ui.print_diff(before, after)
        ui.print_warning("No changes made (dry-run)")
        return

    out_path = Path(output).resolve() if output else None
    result = handler.spoof_metadata(filepath, data, out_path)

    # Sync file timestamps to match metadata
    if sync_time:
        dt_str = data.get('datetime') or data.get('datetime_original')
        if dt_str:
            sync_timestamps(result, dt_str)
            log.info(f"File timestamps synced to {dt_str}")

    ui.print_success(f"Metadata spoofed successfully → [cyan]{result}[/cyan]")

    # Show the new metadata
    ui.console.print()
    new_meta = handler.view_metadata(result)
    ui.print_metadata_table(new_meta, str(result))


# ─────────────────────────────────────────────────────
#  RANDOMIZE command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file (default: overwrite)")
@click.option("--preset", type=str, default=None, help="Camera preset for randomization")
@click.option("--city", type=str, default=None, help="City for GPS randomization")
@click.option("--scene", type=click.Choice(["daylight_outdoor", "golden_hour", "indoor", "night_street", "portrait", "landscape"]),
              default=None, help="Scene profile for correlated exposure params")
@click.option("--sync-time", is_flag=True, help="Sync file timestamps to match generated metadata")
@click.option("--dry-run", is_flag=True, help="Show what would change without modifying")
def randomize(file: str, output: Optional[str], preset: Optional[str],
              city: Optional[str], scene: Optional[str], sync_time: bool, dry_run: bool):
    """Generate random plausible metadata for a file."""
    filepath = _validate_file(file)
    handler, ftype = _get_handler(filepath)

    if not handler:
        ui.print_error(f"Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    ui.print_banner()
    ui.print_file_header(str(filepath))

    randomizer = MetadataRandomizer()

    if ftype == 'image':
        # Get actual image dimensions for EXIF consistency
        try:
            from PIL import Image
            with Image.open(filepath) as img:
                actual_size = img.size
        except Exception:
            actual_size = None
        data = randomizer.random_image_exif(preset_name=preset, city=city, scene=scene,
                                            actual_size=actual_size)
    elif ftype == 'audio':
        data = randomizer.random_audio_tags()
    elif ftype == 'pdf':
        data = randomizer.random_pdf_meta()
    else:
        data = {}

    if dry_run:
        ui.print_info("[bold]Dry-run mode[/bold] — preview of random metadata:\n")
        before = handler.view_metadata(filepath)
        after = {'randomized': data}
        ui.print_diff(before, after)
        ui.print_warning("No changes made (dry-run)")
        return

    out_path = Path(output).resolve() if output else None
    result = handler.spoof_metadata(filepath, data, out_path)
    # Sync file timestamps
    if sync_time:
        dt_str = data.get('datetime') or data.get('datetime_original')
        if dt_str:
            sync_timestamps(result, dt_str)
            log.info(f"File timestamps synced to {dt_str}")

    ui.print_success(f"Random metadata applied → [cyan]{result}[/cyan]")

    ui.console.print()
    new_meta = handler.view_metadata(result)
    ui.print_metadata_table(new_meta, str(result))


# ─────────────────────────────────────────────────────
#  CLONE command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file (default: overwrite target)")
def clone(source: str, target: str, output: Optional[str]):
    """Clone metadata from SOURCE file to TARGET file."""
    src_path = _validate_file(source)
    tgt_path = _validate_file(target)

    handler_src, ftype_src = _get_handler(src_path)
    handler_tgt, ftype_tgt = _get_handler(tgt_path)

    if not handler_src:
        ui.print_error(f"Unsupported source format: {src_path.suffix}")
        sys.exit(1)
    if not handler_tgt:
        ui.print_error(f"Unsupported target format: {tgt_path.suffix}")
        sys.exit(1)
    if ftype_src != ftype_tgt:
        ui.print_error(f"Format mismatch: {src_path.suffix} → {tgt_path.suffix}")
        ui.print_info("Both files must be of the same type (image↔image, audio↔audio, pdf↔pdf)")
        sys.exit(1)

    ui.print_banner()
    ui.print_info(f"Cloning metadata: [cyan]{src_path.name}[/cyan] → [cyan]{tgt_path.name}[/cyan]\n")

    out_path = Path(output).resolve() if output else None
    result = handler_src.clone_metadata(src_path, tgt_path, out_path)
    ui.print_success(f"Metadata cloned successfully → [cyan]{result}[/cyan]")


# ─────────────────────────────────────────────────────
#  BATCH command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--action", type=click.Choice(["clean", "randomize"]), required=True, help="Action to perform")
@click.option("--preset", type=str, default=None, help="Camera preset (for randomize)")
@click.option("-o", "--output-dir", type=click.Path(), default=None, help="Output directory (default: overwrite)")
@click.option("--recursive", "-r", is_flag=True, help="Process subdirectories recursively")
def batch(directory: str, action: str, preset: Optional[str],
          output_dir: Optional[str], recursive: bool):
    """Batch process all supported files in a directory."""
    dir_path = Path(directory).resolve()
    out_dir = Path(output_dir).resolve() if output_dir else None

    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    ui.print_banner()
    ui.print_info(f"Batch [bold]{action}[/bold] on [cyan]{dir_path}[/cyan]\n")

    # Collect files
    if recursive:
        files = [f for f in dir_path.rglob("*") if f.is_file()]
    else:
        files = [f for f in dir_path.iterdir() if f.is_file()]

    # Filter supported
    supported = []
    for f in files:
        handler, ftype = _get_handler(f)
        if handler:
            supported.append((f, handler, ftype))

    if not supported:
        ui.print_warning("No supported files found in directory")
        return

    ui.print_info(f"Found [bold]{len(supported)}[/bold] supported files\n")

    randomizer = MetadataRandomizer()
    success = 0
    failed = 0

    with ui.create_progress() as progress:
        task = progress.add_task("Processing...", total=len(supported), status="")

        for filepath, handler, ftype in supported:
            progress.update(task, status=filepath.name)
            try:
                if out_dir:
                    rel = filepath.relative_to(dir_path)
                    out_path = out_dir / rel
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    out_path = None

                if action == "clean":
                    handler.clean_metadata(filepath, out_path)
                elif action == "randomize":
                    if ftype == 'image':
                        data = randomizer.random_image_exif(preset_name=preset)
                    elif ftype == 'audio':
                        data = randomizer.random_audio_tags()
                    elif ftype == 'pdf':
                        data = randomizer.random_pdf_meta()
                    else:
                        data = {}
                    handler.spoof_metadata(filepath, data, out_path)

                success += 1
            except Exception:
                failed += 1

            progress.advance(task)

    ui.console.print()
    ui.print_success(f"Processed: [bold green]{success}[/bold green] files")
    if failed:
        ui.print_error(f"Failed: [bold red]{failed}[/bold red] files")


# ─────────────────────────────────────────────────────
#  REPORT command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output report as JSON")
def report(file: str, as_json: bool):
    """Analyze file for privacy risks in metadata."""
    filepath = _validate_file(file)
    handler, ftype = _get_handler(filepath)

    if not handler:
        ui.print_error(f"Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    ui.print_banner()
    ui.print_file_header(str(filepath))

    metadata = handler.view_metadata(filepath)
    reporter = PrivacyReporter()
    risks, score = reporter.analyze(metadata, ftype)

    if as_json:
        report_data = {
            'file': str(filepath),
            'type': ftype,
            'score': score,
            'risks': risks,
            'metadata': metadata,
        }
        ui.console.print_json(json.dumps(report_data, indent=2, ensure_ascii=False, default=str))
    else:
        ui.print_risk_report(risks, score, str(filepath))

        if score == 0:
            ui.console.print()
            ui.print_success("No privacy risks detected — file is clean! 🛡️")
        elif score < 40:
            ui.console.print()
            ui.print_info("Low risk. Consider running [cyan]fsf clean[/cyan] for full protection.")
        else:
            ui.console.print()
            ui.print_warning("Run [cyan]fsf clean <file>[/cyan] to strip all metadata")
            ui.print_info("Or [cyan]fsf randomize <file>[/cyan] to replace with fake data")


# ─────────────────────────────────────────────────────
#  PRESETS command
# ─────────────────────────────────────────────────────
@cli.command()
@click.option("--cameras", is_flag=True, help="List camera presets")
@click.option("--cities", is_flag=True, help="List city GPS presets")
@click.option("--all", "show_all", is_flag=True, help="List all presets")
def presets(cameras: bool, cities: bool, show_all: bool):
    """List available presets for spoofing."""
    ui.print_banner()

    if cameras or show_all or (not cameras and not cities):
        from rich.table import Table
        from rich import box

        table = Table(
            title="[bold]Camera Presets[/bold]",
            title_style="bold magenta",
            show_header=True,
            header_style="bold bright_cyan",
            border_style="dim",
            box=box.ROUNDED,
            expand=True,
        )
        table.add_column("Preset Name", style="bold cyan")
        table.add_column("Make", style="white")
        table.add_column("Model", style="white")
        table.add_column("Focal Length", style="yellow")
        table.add_column("Aperture", style="yellow")
        table.add_column("ISO Range", style="dim")

        for name, cam in CAMERA_PRESETS.items():
            table.add_row(
                name,
                cam['make'],
                cam['model'],
                f"{cam['focal_length']}mm",
                f"f/{cam['f_number']}",
                f"{cam['iso'][0]}-{cam['iso'][1]}",
            )
        ui.console.print(table)
        ui.console.print()

    if cities or show_all:
        from rich.table import Table
        from rich import box

        table = Table(
            title="[bold]City GPS Presets[/bold]",
            title_style="bold magenta",
            show_header=True,
            header_style="bold bright_cyan",
            border_style="dim",
            box=box.ROUNDED,
            expand=True,
        )
        table.add_column("City", style="bold cyan")
        table.add_column("Latitude", style="white")
        table.add_column("Longitude", style="white")
        table.add_column("Hotspots", style="dim")

        for name, city_data in CITY_PRESETS.items():
            hotspot_count = len(city_data.get('hotspots', []))
            table.add_row(
                name.replace("_", " ").title(),
                f"{abs(city_data['lat']):.4f}° {city_data['lat_ref']}",
                f"{abs(city_data['lon']):.4f}° {city_data['lon_ref']}",
                f"{hotspot_count} locations",
            )
        ui.console.print(table)


# ─────────────────────────────────────────────────────
#  EXPORT command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), required=True, help="Output JSON file")
def export(file: str, output: str):
    """Export file metadata to a JSON file."""
    filepath = _validate_file(file)
    handler, ftype = _get_handler(filepath)

    if not handler:
        ui.print_error(f"Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    metadata = handler.view_metadata(filepath)
    out_path = Path(output).resolve()

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'file': str(filepath),
            'type': ftype,
            'metadata': metadata,
        }, f, indent=2, ensure_ascii=False, default=str)

    ui.print_success(f"Metadata exported → [cyan]{out_path}[/cyan]")


# ─────────────────────────────────────────────────────
#  FORGE command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--locale", type=click.Choice(["en", "de", "jp", "es", "ru", "kr"]),
              default=None, help="Name locale for the forged identity")
@click.option("--camera", type=str, default=None, help="Camera preset for the identity")
@click.option("--city", type=str, default=None, help="Home city for GPS")
@click.option("-o", "--output-dir", type=click.Path(), default=None, help="Output directory")
def forge(files: tuple, locale: Optional[str], camera: Optional[str],
          city: Optional[str], output_dir: Optional[str]):
    """Forge a consistent fake identity across multiple files.

    Creates a persona (name, camera, location, style) and applies
    it consistently across all specified files, as if they were all
    taken by the same person over time.
    """
    ui.print_banner()

    randomizer = MetadataRandomizer()
    identity = randomizer.forge_identity(locale)

    # Apply overrides
    if camera:
        if camera not in CAMERA_PRESETS:
            ui.print_error(f"Unknown camera preset: {camera}")
            sys.exit(1)
        identity["camera_preset"] = camera
        identity["camera"] = CAMERA_PRESETS[camera]
    if city:
        if city not in CITY_PRESETS:
            ui.print_error(f"Unknown city: {city}")
            sys.exit(1)
        identity["home_city"] = city

    # Show the forged identity
    from rich.table import Table
    from rich import box

    table = Table(
        title="[bold]Forged Identity[/bold]",
        title_style="bold magenta",
        show_header=False,
        border_style="cyan",
        box=box.ROUNDED,
        expand=True,
    )
    table.add_column("Field", style="bold cyan", min_width=15)
    table.add_column("Value", style="white")
    table.add_row("👤 Name", identity["name"])
    table.add_row("📷 Camera", f"{identity['camera']['make']} {identity['camera']['model']}")
    table.add_row("📍 City", identity["home_city"].replace("_", " ").title())
    table.add_row("🖥️  Software", identity["software"])
    table.add_row("🎨 Style", identity["style"].replace("_", " ").title())
    table.add_row("📅 Period", identity["base_date"].strftime("%B %Y"))
    ui.console.print(table)
    ui.console.print()

    out_dir = Path(output_dir).resolve() if output_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    for i, file in enumerate(files):
        filepath = _validate_file(file)
        handler, ftype = _get_handler(filepath)

        if not handler:
            ui.print_warning(f"Skipping unsupported: {filepath.name}")
            continue

        if ftype == 'image':
            data = randomizer.random_image_from_identity(identity, day_offset=i)
        elif ftype == 'audio':
            data = randomizer.random_audio_tags()
            data['artist'] = identity['name']
        elif ftype == 'pdf':
            data = randomizer.random_pdf_meta()
            data['author'] = identity['name']
        else:
            continue

        if out_dir:
            out_path = out_dir / filepath.name
        else:
            out_path = None

        result = handler.spoof_metadata(filepath, data, out_path)
        ui.print_success(f"{filepath.name} → forged as [cyan]{identity['name']}[/cyan]")
        success += 1

    ui.console.print()
    ui.print_success(f"Forged identity applied to [bold]{success}[/bold] files")


# ─────────────────────────────────────────────────────
#  COMPARE command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
def compare(file1: str, file2: str):
    """Compare metadata of two files side by side."""
    from rich.table import Table
    from rich import box

    path1 = _validate_file(file1)
    path2 = _validate_file(file2)

    handler1, ftype1 = _get_handler(path1)
    handler2, ftype2 = _get_handler(path2)

    if not handler1:
        ui.print_error(f"Unsupported: {path1.suffix}")
        sys.exit(1)
    if not handler2:
        ui.print_error(f"Unsupported: {path2.suffix}")
        sys.exit(1)

    ui.print_banner()
    ui.print_info(f"Comparing: [cyan]{path1.name}[/cyan] vs [cyan]{path2.name}[/cyan]\n")

    meta1 = handler1.view_metadata(path1)
    meta2 = handler2.view_metadata(path2)

    # Flatten metadata dicts
    flat1 = {}
    flat2 = {}
    for cat_data in meta1.values():
        flat1.update(cat_data)
    for cat_data in meta2.values():
        flat2.update(cat_data)

    all_keys = sorted(set(flat1.keys()) | set(flat2.keys()))

    table = Table(
        title="[bold]Metadata Comparison[/bold]",
        title_style="bold magenta",
        show_header=True,
        header_style="bold bright_cyan",
        border_style="dim",
        box=box.ROUNDED,
        expand=True,
    )
    table.add_column("Field", style="cyan", min_width=18)
    table.add_column(path1.name, style="white", min_width=20, max_width=40)
    table.add_column(path2.name, style="white", min_width=20, max_width=40)
    table.add_column("Match", style="bold", min_width=3, justify="center")

    matches = 0
    diffs = 0
    for key in all_keys:
        v1 = str(flat1.get(key, '—'))
        v2 = str(flat2.get(key, '—'))
        if v1 == v2:
            match_icon = "[green]=[/green]"
            matches += 1
        else:
            match_icon = "[red]≠[/red]"
            diffs += 1
        table.add_row(key, v1, v2, match_icon)

    ui.console.print(table)
    ui.console.print()
    ui.print_info(f"[green]{matches}[/green] matching · [red]{diffs}[/red] different")


# ─────────────────────────────────────────────────────
#  AUDIT command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output audit results as JSON")
def audit(file: str, as_json: bool):
    """Check spoofed metadata for forensic consistency.

    Analyzes the file for metadata inconsistencies that forensic tools
    would flag — mismatched camera/software, impossible exposure values,
    timestamp conflicts, and more.
    """
    from rich.table import Table
    from rich.panel import Panel
    from rich import box

    filepath = _validate_file(file)
    handler, ftype = _get_handler(filepath)

    if not handler:
        ui.print_error(f"Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    ui.print_banner()
    ui.print_file_header(str(filepath))

    try:
        from .audit import ForensicAuditor
        auditor = ForensicAuditor()
        audit_result = auditor.audit(filepath)
        # v3.0: audit returns (findings, score) tuple
        if isinstance(audit_result, tuple):
            findings, score = audit_result
        else:
            findings, score = audit_result, None
    except ImportError:
        ui.print_error("Audit module not available")
        sys.exit(1)

    if as_json:
        data = {'findings': findings, 'score': score}
        if score is not None:
            data['label'] = ForensicAuditor.score_label(score)
        ui.console.print_json(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        return

    if not findings:
        ui.print_success("No inconsistencies found — metadata looks clean! ✓")
        if score is not None:
            ui.print_info(f"Forensic Score: [bold green]{score}/100[/bold green] ({ForensicAuditor.score_label(score)})")
        return

    # Count by level
    fails = sum(1 for f in findings if f['level'] == 'FAIL')
    warns = sum(1 for f in findings if f['level'] == 'WARN')
    oks = sum(1 for f in findings if f['level'] == 'OK' or f['level'] == 'PASS')

    # Score-based grade (v3.0)
    if score is not None:
        label = ForensicAuditor.score_label(score)
        if score >= 90:
            score_color = 'green'
        elif score >= 70:
            score_color = 'cyan'
        elif score >= 50:
            score_color = 'yellow'
        else:
            score_color = 'red'
        grade_text = f"[bold {score_color}]{score}/100 — {label}[/bold {score_color}]"
    elif fails > 0:
        grade_text = f"[bold red]SUSPICIOUS[/bold red] — {fails} critical issues"
    elif warns > 2:
        grade_text = f"[bold yellow]QUESTIONABLE[/bold yellow] — {warns} warnings"
    elif warns > 0:
        grade_text = f"[bold yellow]MINOR ISSUES[/bold yellow] — {warns} warnings"
    else:
        grade_text = "[bold green]CLEAN[/bold green] — no issues detected"

    ui.console.print(Panel(
        f"  Forensic Score: {grade_text}",
        title="[bold]🔍 Audit Result[/bold]",
        border_style="cyan",
        expand=True,
    ))
    ui.console.print()

    table = Table(
        title="[bold]Forensic Findings[/bold]",
        title_style="bold magenta",
        show_header=True,
        header_style="bold bright_cyan",
        border_style="dim",
        box=box.ROUNDED,
        expand=True,
    )
    table.add_column("Level", style="bold", min_width=4, justify="center")
    table.add_column("Check", style="cyan", min_width=20)
    table.add_column("Detail", style="white")

    level_icons = {
        'FAIL': '[bold red]FAIL[/bold red]',
        'WARN': '[bold yellow]WARN[/bold yellow]',
        'PASS': '[bold green]PASS[/bold green]',
        'OK': '[bold green]OK[/bold green]',
    }

    for finding in findings:
        level = level_icons.get(finding['level'], finding['level'])
        table.add_row(level, finding['check'], finding['detail'])

    ui.console.print(table)
    ui.console.print()

    if fails > 0:
        ui.print_warning("Forensic tools would likely flag this file")
        ui.print_info("Use [cyan]fsf randomize[/cyan] for more realistic metadata")
    elif warns > 0:
        ui.print_info("Minor inconsistencies — probably fine for casual inspection")


# ─────────────────────────────────────────────────────
#  HASH command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--mutate", is_flag=True, help="Mutate file hash by appending junk bytes")
@click.option("--verify", "expected_hash", type=str, default=None, help="Verify file against expected SHA256 hash")
@click.option("--algorithm", "-a", type=click.Choice(["md5", "sha1", "sha256", "sha512"]), default=None, help="Hash algorithm")
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file for mutated hash")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def hash(file: str, mutate: bool, expected_hash: str, algorithm: str, output: str, as_json: bool):
    """Compute, verify, or mutate file hashes."""
    from .hasher import FileHasher

    filepath = _validate_file(file)
    ui.print_banner()
    ui.print_file_header(str(filepath))

    if expected_hash:
        alg = algorithm or "sha256"
        match = FileHasher.verify(filepath, expected_hash, alg)
        if match:
            ui.print_success(f"Hash MATCHES ({alg})")
        else:
            actual = FileHasher.compute(filepath, [alg])[alg]
            ui.print_error(f"Hash MISMATCH ({alg})")
            ui.print_info(f"Expected: {expected_hash}")
            ui.print_info(f"Actual:   {actual}")
        return

    if mutate:
        out_path = Path(output) if output else filepath
        result = FileHasher.mutate_hash(filepath, out_path)
        if as_json:
            click.echo(json.dumps(result, indent=2))
        else:
            from rich.table import Table
            table = Table(title="Hash Mutation", show_header=True)
            table.add_column("Algorithm", style="cyan")
            table.add_column("Before", style="red")
            table.add_column("After", style="green")
            for alg in result['old']:
                table.add_row(alg.upper(), result['old'][alg], result['new'][alg])
            ui.console.print(table)
            ui.print_success(f"Hash mutated → {out_path.name}")
        return

    # Default: compute hashes
    algos = [algorithm] if algorithm else ["md5", "sha1", "sha256"]
    hashes = FileHasher.compute(filepath, algos)
    if as_json:
        click.echo(json.dumps(hashes, indent=2))
    else:
        from rich.table import Table
        table = Table(title="File Hashes", show_header=True)
        table.add_column("Algorithm", style="cyan")
        table.add_column("Hash", style="green")
        for alg, val in hashes.items():
            table.add_row(alg.upper(), val)
        ui.console.print(table)


# ─────────────────────────────────────────────────────
#  STRIP command (surgical removal)
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--gps", is_flag=True, help="Strip only GPS/location data")
@click.option("--dates", is_flag=True, help="Strip only date/time info")
@click.option("--device", is_flag=True, help="Strip only camera/device identification")
@click.option("--thumbnail", is_flag=True, help="Strip embedded thumbnail")
@click.option("--all", "strip_all", is_flag=True, help="Strip GPS + dates + device + thumbnail")
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file")
def strip(file: str, gps: bool, dates: bool, device: bool, thumbnail: bool, strip_all: bool, output: str):
    """Surgically remove specific metadata categories (GPS, dates, device, thumbnail)."""
    from .strip import SurgicalStripper

    filepath = _validate_file(file)
    out_path = Path(output) if output else filepath

    if not any([gps, dates, device, thumbnail, strip_all]):
        ui.print_error("Specify what to strip: --gps, --dates, --device, --thumbnail, or --all")
        ui.print_info("Run [cyan]fsf strip --help[/cyan] for options")
        sys.exit(1)

    ui.print_banner()
    ui.print_file_header(str(filepath))

    # Work on a copy if output specified
    if output and filepath != out_path:
        import shutil
        shutil.copy2(filepath, out_path)
        work_path = out_path
    else:
        work_path = filepath

    stripped = []
    if gps or strip_all:
        if SurgicalStripper.strip_gps(work_path):
            stripped.append("GPS/location")
    if dates or strip_all:
        if SurgicalStripper.strip_dates(work_path):
            stripped.append("date/time")
    if device or strip_all:
        if SurgicalStripper.strip_device(work_path):
            stripped.append("camera/device ID")
    if thumbnail or strip_all:
        if SurgicalStripper.strip_thumbnail(work_path):
            stripped.append("thumbnail")

    if stripped:
        ui.print_success(f"Stripped: {', '.join(stripped)}")
    else:
        ui.print_warning("No metadata categories were stripped (file may not be a JPEG)")


# ─────────────────────────────────────────────────────
#  TEMPLATE command group
# ─────────────────────────────────────────────────────
@cli.group()
def template():
    """Save, load, and manage metadata templates."""
    pass


@template.command("save")
@click.argument("file", type=click.Path(exists=True))
@click.argument("name")
@click.option("--description", "-d", default="", help="Template description")
def template_save(file: str, name: str, description: str):
    """Extract metadata from FILE and save as a named template."""
    from .templates import TemplateManager

    filepath = _validate_file(file)
    handler, ftype = _get_handler(filepath)

    if not handler:
        ui.print_error(f"Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    ui.print_banner()
    tm = TemplateManager()
    path = tm.extract_and_save(filepath, name, handler, description)
    ui.print_success(f"Template '{name}' saved → {path}")


@template.command("load")
@click.argument("name")
def template_load(name: str):
    """Show the contents of a saved template."""
    from .templates import TemplateManager

    ui.print_banner()
    tm = TemplateManager()
    try:
        metadata = tm.load(name)
        click.echo(json.dumps(metadata, indent=2, default=str))
    except FSFError as e:
        ui.print_error(str(e))
        sys.exit(1)


@template.command("apply")
@click.argument("name")
@click.argument("file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file")
def template_apply(name: str, file: str, output: str):
    """Apply a saved template to a file."""
    from .templates import TemplateManager

    filepath = _validate_file(file)
    handler, ftype = _get_handler(filepath)
    if not handler:
        ui.print_error(f"Unsupported file format: {filepath.suffix}")
        sys.exit(1)

    ui.print_banner()
    tm = TemplateManager()
    try:
        metadata = tm.load(name)
    except FSFError as e:
        ui.print_error(str(e))
        sys.exit(1)

    out_path = Path(output) if output else None
    handler.spoof_metadata(filepath, metadata, output=out_path)
    ui.print_success(f"Template '{name}' applied to {filepath.name}")


@template.command("list")
def template_list():
    """List all saved templates."""
    from .templates import TemplateManager
    from rich.table import Table

    ui.print_banner()
    tm = TemplateManager()
    templates = tm.list_templates()

    if not templates:
        ui.print_info("No templates saved yet. Use [cyan]fsf template save <file> <name>[/cyan]")
        return

    table = Table(title="Saved Templates", show_header=True)
    table.add_column("Name", style="cyan bold")
    table.add_column("Description", style="white")
    table.add_column("Created", style="dim")
    for t in templates:
        table.add_row(t['name'], t['description'] or "—", t['created'][:19])
    ui.console.print(table)


@template.command("delete")
@click.argument("name")
def template_delete(name: str):
    """Delete a saved template."""
    from .templates import TemplateManager

    tm = TemplateManager()
    if tm.delete(name):
        ui.print_success(f"Template '{name}' deleted")
    else:
        ui.print_error(f"Template '{name}' not found")


# ─────────────────────────────────────────────────────
#  TIMELINE command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--city", type=str, default=None, help="City for GPS hotspots")
@click.option("--preset", type=str, default=None, help="Camera preset name")
@click.option("--days", type=int, default=None, help="Trip duration in days")
@click.option("--style", type=click.Choice(["casual", "enthusiast", "professional"]), default="casual",
              help="Shooting style")
@click.option("--sync-time", is_flag=True, help="Sync filesystem timestamps to EXIF")
@click.option("-o", "--output-dir", type=click.Path(), default=None, help="Output directory")
def timeline(files, city, preset, days, style, sync_time, output_dir):
    """Apply a realistic trip timeline across multiple photos.

    Generates chronologically ordered metadata with GPS drift between
    hotspots, time-of-day correlated exposure settings, and natural
    shooting patterns.
    """
    from .timeline import TripTimeline

    file_list = [_validate_file(f) for f in files]

    if not file_list:
        ui.print_error("No files specified")
        sys.exit(1)

    ui.print_banner()
    ui.console.print(f"  [bold cyan]Timeline Generator[/bold cyan] — {len(file_list)} photos\n")

    tl = TripTimeline(city=city, preset=preset, days=days, style=style)
    timeline_data = tl.generate(num_photos=len(file_list))

    if output_dir:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

    from rich.table import Table
    table = Table(title=f"Trip: {tl.city} • {tl.days} days • {style}", show_header=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("File", style="cyan")
    table.add_column("DateTime", style="green")
    table.add_column("GPS", style="yellow")
    table.add_column("Scene", style="magenta")

    handler = ImageHandler()

    for i, (filepath, exif_data) in enumerate(zip(file_list, timeline_data)):
        out_path = Path(output_dir) / filepath.name if output_dir else None

        try:
            handler.spoof_metadata(filepath, exif_data, output=out_path)
            target = out_path or filepath

            if sync_time and 'datetime_original' in exif_data:
                sync_timestamps(target, exif_data['datetime_original'])

            dt = exif_data.get('datetime_original', '?')
            lat = exif_data.get('gps_lat', 0)
            lat_ref = exif_data.get('gps_lat_ref', 'N')
            lon = exif_data.get('gps_lon', 0)
            lon_ref = exif_data.get('gps_lon_ref', 'E')
            gps_str = f"{lat:.4f}°{lat_ref} {lon:.4f}°{lon_ref}"

            # Determine scene from time
            hour = int(dt.split(' ')[1].split(':')[0]) if ' ' in dt else 0
            scene = tl._get_scene_for_hour(hour)

            table.add_row(str(i+1), filepath.name, dt, gps_str, scene)
        except Exception as e:
            table.add_row(str(i+1), filepath.name, "[red]ERROR[/red]", str(e), "")

    ui.console.print(table)
    ui.console.print()
    ui.print_success(f"Timeline applied: {len(file_list)} photos over {tl.days} days in {tl.city}")


# ─────────────────────────────────────────────────────
#  TUI command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("directory", type=click.Path(exists=True), default=".")
def tui(directory: str):
    """Launch interactive Terminal UI for browsing and editing metadata.

    Navigate files with arrow keys, view metadata, and perform actions
    (Clean, Randomize, Audit, Hash) with hotkeys.
    """
    from .tui import run_tui
    run_tui(directory=directory)


# ─────────────────────────────────────────────────────
#  PIPELINE command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--steps", "-s", type=str, default=None,
              help="Inline pipeline spec: 'clean+spoof:iphone_15_pro:tokyo+audit'")
@click.option("--config", "-c", type=str, default=None,
              help="Load pipeline from saved YAML config name")
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file")
def pipeline(file: str, steps: str, config: str, output: str):
    """Run a chain of operations on a file.

    \b
    Inline examples:
      fsf pipeline photo.jpg -s 'clean+spoof:iphone_15_pro:tokyo+audit'
      fsf pipeline photo.jpg -s 'strip:gps+hash:mutate+audit'
      fsf pipeline photo.jpg -s 'clean+randomize+audit'

    \b
    From saved config:
      fsf pipeline photo.jpg --config paranoid
    """
    from .pipeline import Pipeline, PipelineManager
    from rich.table import Table

    filepath = _validate_file(file)
    out_path = Path(output) if output else None

    if not steps and not config:
        ui.print_error("Specify --steps or --config")
        ui.print_info("Example: [cyan]fsf pipeline photo.jpg -s 'clean+spoof:iphone_15_pro:tokyo+audit'[/cyan]")
        sys.exit(1)

    ui.print_banner()
    ui.print_file_header(str(filepath))

    if config:
        pm = PipelineManager()
        try:
            pipe = pm.load(config)
        except FSFError as e:
            ui.print_error(str(e))
            sys.exit(1)
        ui.print_info(f"Loaded pipeline: [bold]{config}[/bold] ({len(pipe.steps)} steps)")
    else:
        pipe = PipelineManager.parse_inline(steps)
        ui.print_info(f"Inline pipeline: {len(pipe.steps)} steps")

    ui.console.print()
    results = pipe.execute(filepath, output=out_path)

    # Show results table
    table = Table(title="Pipeline Results", show_header=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Step", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Detail", style="white")

    for r in results:
        status_style = {'ok': '[green]OK[/green]', 'warning': '[yellow]WARN[/yellow]',
                        'error': '[red]ERROR[/red]'}.get(r['status'], r['status'])
        table.add_row(str(r.get('step_num', '?')), r['step'], status_style, r.get('detail', ''))

    ui.console.print(table)
    errors = sum(1 for r in results if r['status'] == 'error')
    if errors:
        ui.print_warning(f"{errors} step(s) failed")
    else:
        ui.print_success(f"Pipeline complete: {len(results)} steps executed")


# ─────────────────────────────────────────────────────
#  DIFF command
# ─────────────────────────────────────────────────────
@cli.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def diff(file1: str, file2: str, as_json: bool):
    """Show only changed metadata fields between two files.

    Unlike 'compare' which shows all fields side by side,
    'diff' highlights only the differences.
    """
    from rich.table import Table
    from rich import box

    fp1 = _validate_file(file1)
    fp2 = _validate_file(file2)

    h1, t1 = _get_handler(fp1)
    h2, t2 = _get_handler(fp2)

    if not h1 or not h2:
        ui.print_error("Both files must be supported formats")
        sys.exit(1)

    meta1 = h1.view_metadata(fp1)
    meta2 = h2.view_metadata(fp2)

    # Flatten metadata dicts
    flat1, flat2 = {}, {}
    for cat, data in meta1.items():
        for k, v in data.items():
            flat1[f"{cat}.{k}"] = str(v)
    for cat, data in meta2.items():
        for k, v in data.items():
            flat2[f"{cat}.{k}"] = str(v)

    all_keys = sorted(set(flat1.keys()) | set(flat2.keys()))
    diffs = []
    for key in all_keys:
        v1 = flat1.get(key, '—')
        v2 = flat2.get(key, '—')
        if v1 != v2:
            diffs.append((key, v1, v2))

    if as_json:
        diff_data = [{'field': k, 'file1': v1, 'file2': v2} for k, v1, v2 in diffs]
        click.echo(json.dumps(diff_data, indent=2, default=str))
        return

    ui.print_banner()

    if not diffs:
        ui.print_success("Files have identical metadata")
        return

    table = Table(
        title=f"Metadata Diff ({len(diffs)} changes)",
        show_header=True,
        header_style="bold bright_cyan",
        border_style="dim",
        box=box.ROUNDED,
        expand=True,
    )
    table.add_column("Field", style="cyan", min_width=20)
    table.add_column(fp1.name, style="red", min_width=25)
    table.add_column(fp2.name, style="green", min_width=25)

    for key, v1, v2 in diffs:
        table.add_row(key, str(v1)[:60], str(v2)[:60])

    ui.console.print(table)
    ui.console.print()
    ui.print_info(f"{len(diffs)} field(s) differ between the two files")


def main():
    """Entry point."""
    try:
        cli(standalone_mode=False)
    except HandlerError as e:
        ui.print_error(str(e))
        sys.exit(1)
    except FSFError as e:
        ui.print_error(str(e))
        sys.exit(1)
    except click.exceptions.Abort:
        ui.console.print("\n[dim]Aborted.[/dim]")
        sys.exit(130)
