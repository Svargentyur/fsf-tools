<div align="center">

# 🛡️ FSF Tools

**File Sanitization Framework** — the Swiss Army knife for file metadata

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-2.0.0-success.svg)](https://github.com/fsf-tools/fsf-tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*View, clean, spoof, forge, and audit metadata across images, audio, PDF, and Office files*

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

## 🚀 Quick Start

### Install
```bash
pip install fsf-tools
# or clone for development
git clone https://github.com/fsf-tools/fsf-tools.git
cd fsf-tools
pip install -e .
```

## 📋 Commands

### 🔍 View metadata
Extract and view metadata in human-readable or JSON format.
```bash
fsf view photo.jpg
fsf view --json photo.jpg
```

### 🧹 Clean (strip all metadata)
Remove all identifying metadata from a file to protect your privacy.
```bash
fsf clean photo.jpg
fsf clean photo.jpg -o clean.jpg
```

### 🎭 Spoof (set specific values)
Inject realistic metadata based on presets and specific inputs.
```bash
fsf spoof photo.jpg --preset iphone_15_pro --city tokyo
fsf spoof document.pdf --author "Jane Doe" --title "Quarterly Report"
```

### 🎲 Randomize (generate plausible fakes)
Automatically generate highly realistic, statistically plausible metadata.
```bash
fsf randomize photo.jpg
fsf randomize photo.jpg --scene night_street --preset sony_a7iv --sync-time
```

### 🧬 Forge (consistent identity across files)
Apply a unified, generated persona (camera, location, author) across multiple files.
```bash
fsf forge *.jpg --locale jp --camera fuji_xt5 --city kyoto
```

### 🕵️ Audit (check for forensic inconsistencies)
Verify that your spoofed files don't contain tell-tale signs of tampering.
```bash
fsf audit photo.jpg
```

### 🛠️ Other Commands
- `fsf clone` — Clone metadata from one file to another.
- `fsf compare` — Compare metadata of two files side by side.
- `fsf batch` — Batch process all supported files in a directory.
- `fsf report` — Analyze a file for privacy risks in metadata.
- `fsf export` — Export file metadata to a JSON file.
- `fsf presets` — List available presets for spoofing.

## 🎯 Realism Features

- 📸 **Exposure Triangle**: ISO, shutter speed, and aperture are physically correlated
- 🌇 **Scene Profiles**: 6 profiles (daylight, golden hour, indoor, night, portrait, landscape)
- 📷 **18 Camera Presets**: With real firmware strings, lens models, and resolutions
- 🌍 **20 Cities**: With 80+ tourist hotspot GPS coordinates
- 👤 **Identity Forge**: Generate consistent personas with names in 6 locales
- 🔍 **Forensic Audit**: Check your fakes for consistency before deployment
- ⏱️ **Timestamp Sync**: Match file system timestamps to EXIF dates

## 📁 Supported Formats

| Format | View | Clean | Spoof | Clone |
|--------|:---:|:---:|:---:|:---:|
| **JPEG / PNG / TIFF / WebP** | ✅ | ✅ | ✅ | ✅ |
| **MP3 / FLAC / OGG / M4A** | ✅ | ✅ | ✅ | ✅ |
| **PDF** | ✅ | ✅ | ✅ | ✅ |
| **DOCX / XLSX / PPTX** | ✅ | ✅ | ✅ | ✅ |

## 🔧 Development

```bash
git clone https://github.com/fsf-tools/fsf-tools.git
cd fsf-tools
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## 📝 License

Released under the [MIT License](LICENSE).
