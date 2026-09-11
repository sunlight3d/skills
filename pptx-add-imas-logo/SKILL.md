---
name: pptx-add-imas-logo
description: >-
  Adds the IMAS logo to the bottom right corner of presentations (Google Slides and local PowerPoint .pptx files), covering previous watermark logos. Supports individual presentations, Google Drive folders, and local .pptx files.
---

# PPTX Add IMAS Logo

## Overview
This skill automatically covers any previous logos (such as NotebookLM watermarks or draft logos) at the bottom right corner of a presentation by first inserting a white rectangle with no border, and then overlaying the IMAS logo.

It supports:
- **Google Slides online** via Google Slides API (single presentation ID or entire Google Drive folder).
- **Local PowerPoint (`.pptx`) files** via `python-pptx`.

## Configuration
- **Logo image:** `logo_imas.png` (dimensions: 1527x688, aspect ratio ~2.22:1).
- **Scale:** Default width `2,000,000 EMU` (~157 pt) and proportional height `901,113 EMU` (~70.9 pt).
- **Margin:** `100,000 EMU` (~7.9 pt) margin from the bottom-right edges to cleanly cover corner watermarks.
- **Default Image URL (Online):** `https://raw.githubusercontent.com/sunlight3d/skills/master/pptx-add-imas-logo/logo_imas.png`

## Dependencies
- `uv` Python package manager (recommended) or `pip`
- `python-pptx` (for local `.pptx` manipulation)
- `google-auth` (for Google Slides API authentication)
- `google-api-python-client` (for Google Slides/Drive API interaction)

## Quick Start

### 1. Local PowerPoint Presentation (.pptx)
```bash
# Process a local .pptx file in-place
uv run pptx_add_imas_logo.py /path/to/presentation.pptx

# Process a local .pptx file and save to a new output file
uv run pptx_add_imas_logo.py /path/to/presentation.pptx --output /path/to/output.pptx
```

### 2. Google Slides Presentation (Online)
```bash
# Process a single Google Slides presentation
uv run pptx_add_imas_logo.py <PRESENTATION_ID> --credentials /path/to/credentials.json

# Process all presentations inside a Google Drive folder
uv run pptx_add_imas_logo.py <FOLDER_ID> --folder --credentials /path/to/credentials.json
```

## Features
- **Dual Support:** Process both remote Google Slides and local `.pptx` presentation files.
- **Corner Watermark Masking:** Overlays a solid white background shape before placing the IMAS logo, completely hiding underlying NotebookLM or other watermark marks.
- **Smart Cleanup / Skipping:** Deletes previous cover shapes or skips duplicate shapes to prevent multiple logo overlays on repeated runs.
- **Folder Batching:** Easily process multiple Google Slides decks in a single command using the `--folder` flag.

## Common Mistakes
- **Google Slides API Permission Error**: Ensure the service account email has **Editor** permissions on the presentation (or folder) itself, and that the "Google Slides API" is enabled in the Google Cloud Console.
- **Network Timeouts on macOS**: If running on macOS, the script forces IPv4 resolution internally to avoid IPv6 connection timeouts.
- **Local File in Use**: Make sure the local `.pptx` file is closed in PowerPoint before running to avoid permission lock errors.
