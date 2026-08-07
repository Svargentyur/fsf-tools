<div align="center">

# 🛡️ FSF Tools

**File Sanitization Framework** — the Swiss Army knife for file metadata

[![PyPI](https://img.shields.io/pypi/v/fsf-tools.svg)](https://pypi.org/project/fsf-tools/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)

*View, clean, spoof, strip, forge, hash, and audit metadata across images, audio, PDF, and Office files*

**[Русское руководство / Russian Guide](README_RU.md)**

<br />

![FSF Tools Preview](docs/screenshot.png)

</div>

---

## ✨ What Makes FSF Tools Different?

| Feature | FSF Tools 🛡️ | ExifTool 📸 | MAT2 🧹 |
|---------|-------------|------------|---------|
| **Core Philosophy** | **Generate plausible metadata** | Read/write tags | Strip everything |
| **User Knowledge** | **Automated (presets, profiles)** | Requires expert knowledge | None (just cleans) |
| **Physical Correlation** | **Yes (Exposure Triangle sync)** | No | N/A |
| **Identity Forging** | **Yes (Consistent personas)** | No | No |
| **Forensic Audit** | **Built-in inconsistency checks** | No | No |
| **Surgical Strip** | **Yes (GPS-only, dates-only, etc.)** | Manual per-tag | All or nothing |
| **Trip Timeline** | **Yes (multi-day GPS drift)** | No | No |
| **Hash Mutation** | **Yes (change hash without corruption)** | No | No |
| **Metadata Templates** | **Yes (save/load YAML profiles)** | Partial (argfiles) | No |

## 🚀 Quick Start

### Install
```bash
pip install fsf-tools
# or clone for development
git clone https://github.com/Svargentyur/fsf-tools.git
cd fsf-tools
pip install -e .
```

## 📋 Commands (16 total)

### 🔍 View metadata
```bash
fsf view photo.jpg
fsf view --json photo.jpg
```

### 🧹 Clean (strip all metadata)
```bash
fsf clean photo.jpg
fsf clean photo.jpg -o clean.jpg
```

### ✂️ Strip (surgical removal) `NEW`
Remove only specific metadata categories — keep everything else intact.
```bash
fsf strip photo.jpg --gps              # GPS/location only
fsf strip photo.jpg --dates            # Date/time only
fsf strip photo.jpg --device           # Camera make/model/serial
fsf strip photo.jpg --thumbnail        # Embedded thumbnail
fsf strip photo.jpg --all              # All of the above
```

### 🎭 Spoof (set specific values)
```bash
fsf spoof photo.jpg --preset iphone_15_pro --city tokyo --sync-time
fsf spoof document.pdf --author "Jane Doe" --title "Quarterly Report"
```

### 🎲 Randomize (generate plausible fakes)
```bash
fsf randomize photo.jpg
fsf randomize photo.jpg --scene night_street --preset sony_a7iv --sync-time
```

### 🧬 Forge (consistent identity across files)
```bash
fsf forge *.jpg --locale jp --camera fuji_xt5 --city kyoto
```

### 📅 Timeline (trip simulation) `NEW`
Apply a realistic multi-day trip timeline with GPS drift between hotspots, time-of-day correlated exposure, and natural shooting patterns.
```bash
fsf timeline *.jpg --city tokyo --preset sony_a7iv --days 3 --sync-time
fsf timeline *.jpg --city paris --style enthusiast --days 5
```

### 🔑 Hash (compute, verify, mutate) `NEW`
```bash
fsf hash photo.jpg                         # Show MD5/SHA1/SHA256
fsf hash photo.jpg -a sha512               # Specific algorithm
fsf hash photo.jpg --mutate                # Change hash without corrupting file
fsf hash photo.jpg --verify <expected>     # Verify against known hash
```

### 📋 Template (save/load metadata profiles) `NEW`
```bash
fsf template save photo.jpg my_preset -d "Tokyo night preset"
fsf template list
fsf template apply my_preset target.jpg
fsf template delete my_preset
```

### 🕵️ Audit (forensic consistency check)
```bash
fsf audit photo.jpg
```

### 🛠️ Other Commands
- `fsf clone` — Clone metadata from one file to another
- `fsf compare` — Compare metadata of two files side by side
- `fsf batch` — Batch process all supported files in a directory
- `fsf report` — Analyze a file for privacy risks (risk score 0–100)
- `fsf export` — Export file metadata to a JSON file
- `fsf presets` — List available camera presets and cities

## 🎯 Realism Features

- 📸 **Exposure Triangle**: ISO, shutter speed, and aperture are physically correlated
- 🌇 **Scene Profiles**: 6 profiles (daylight, golden hour, indoor, night, portrait, landscape)
- 📷 **18 Camera Presets**: With real firmware strings, lens models, and resolutions
- 🌍 **20 Cities**: With 80+ tourist hotspot GPS coordinates
- 👤 **Identity Forge**: Generate consistent personas with names in 6 locales
- 🔍 **Forensic Audit**: 10 checks for EXIF inconsistencies
- ⏱️ **Timestamp Sync**: Match file system mtime/atime to EXIF dates
- 📅 **Trip Timeline**: Multi-day GPS drift with time-of-day scene correlation
- ✂️ **Surgical Strip**: Remove GPS/dates/device/thumbnail independently
- 🔑 **Hash Mutation**: Change file hash without affecting visual content
- 📋 **YAML Templates**: Save and reuse metadata profiles

## 📁 Supported Formats

| Format | View | Clean | Spoof | Strip | Clone |
|--------|:---:|:---:|:---:|:---:|:---:|
| **JPEG / PNG / TIFF / WebP** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **MP3 / FLAC / OGG / M4A** | ✅ | ✅ | ✅ | — | ✅ |
| **PDF** | ✅ | ✅ | ✅ | — | ✅ |
| **DOCX / XLSX / PPTX** | ✅ | ✅ | ✅ | — | ✅ |

## 🔧 Development

```bash
git clone https://github.com/Svargentyur/fsf-tools.git
cd fsf-tools
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest  # 27 tests
```

## 📝 License

Released under the [GNU General Public License v3.0 (GPL-3.0)](LICENSE).
