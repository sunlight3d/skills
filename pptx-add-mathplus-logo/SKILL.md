---
name: pptx-add-mathplus-logo
description: >-
  Adds the MathPlus Academy logo inside an opaque white rectangle to the bottom-right corner of Google Slides and PowerPoint (.pptx) presentations, covering NotebookLM watermark logos completely. Supports individual presentations, Google Drive folders, and local .pptx files.
---

# PPTX Add MathPlus Logo

## Overview
This skill automatically covers any previous logos or watermarks (such as the NotebookLM watermark) at the bottom-right corner of a Google Slides or PowerPoint (.pptx) presentation by overlaying an opaque white rectangle featuring the official **MathPlus Academy** logo.

It can process:
1. **Google Slides presentations** (by presentation ID or full URL).
2. **Google Drive folders** (automatically discovering and processing all slide decks within the folder).
3. **Local PowerPoint files** (`.pptx`) and local directories of `.pptx` files.

## Configuration & Sizing
- **Logo Asset**: `logo_mathplus.png` (2400 x 900 px, aspect ratio 2.667:1).
  - Features the crisp green 4-leaf clover emblem on the left.
  - "MathPlus+" in brand green (`#008134`) and warm orange (`#F79A00`).
  - "— ACADEMY —" subtitle in dark charcoal and orange accents.
  - Solid opaque white background (`#FFFFFF`) to ensure 100% masking of the watermark beneath.
- **Dimensions on Slide**:
  - Width: `2,300,000 EMU` (~181 pt / 2.52 in / 6.4 cm)
  - Height: `862,500 EMU` (~67.9 pt / 0.94 in / 2.4 cm)
  - Margins: `pos_x = slide_width - width - margin_x` (`margin_x = 0`), `pos_y = slide_height - height - margin_y` (`margin_y = 38,100 EMU`).
  - This completely eclipses the standard NotebookLM watermark (`width ~173 pt`, `height ~25.6 pt`) with generous safety margins.

## Dependencies
- `uv` Python package manager (required to run the utility script)
- `google-auth` & `google-api-python-client` (for Google Slides API interaction)
- `python-pptx` (for local `.pptx` manipulation)
- `Pillow` (image processing)

## Quick Start

### 1. Process Google Slides Online
```bash
# Process a single presentation by URL or ID
uv run /Volumes/data/code/skills/pptx-add-mathplus-logo/pptx_add_mathplus_logo.py "https://docs.google.com/presentation/d/PRESENTATION_ID/edit"

# Process all presentations in a Google Drive folder
uv run /Volumes/data/code/skills/pptx-add-mathplus-logo/pptx_add_mathplus_logo.py "https://drive.google.com/drive/folders/FOLDER_ID" --folder
```

### 2. Process Local PowerPoint Presentations (.pptx)
```bash
# Process a single local .pptx file
uv run /Volumes/data/code/skills/pptx-add-mathplus-logo/pptx_add_mathplus_logo.py "/path/to/presentation.pptx"

# Process with a custom output path
uv run /Volumes/data/code/skills/pptx-add-mathplus-logo/pptx_add_mathplus_logo.py "/path/to/presentation.pptx" --output "/path/to/presentation_branded.pptx"

# Process all .pptx files in a directory
uv run /Volumes/data/code/skills/pptx-add-mathplus-logo/pptx_add_mathplus_logo.py "/path/to/folder_with_pptx"
```

### 3. Remove Existing Logos
```bash
# Remove MathPlus/NotebookLM cover elements
uv run /Volumes/data/code/skills/pptx-add-mathplus-logo/pptx_add_mathplus_logo.py <ID_OR_PATH> --remove-only
```

## Features
- **Smart Replacement / Cleanup**: Automatically identifies and deletes existing logo covers (`mathplus_logo_`, `cover_img_`, `cover_rect_`) before adding the new one, preventing duplicate stacked layers.
- **Auto-Detection**: Intelligently identifies whether the target is a local `.pptx` file, a local directory, a Google Slides presentation URL, or a Google Drive folder URL.
- **Universal Credentials Detection**: Automatically searches for service account `credentials.json` in standard locations across the workspace and user environment.
- **macOS IPv6 Bypass**: Automatically forces IPv4 DNS resolution to prevent socket timeouts when calling Google APIs on macOS.

## Common Pitfalls & Tips
- **Google Slides Permission Error**: Ensure the service account email is added with **Editor** permissions to the presentation or Google Drive folder.
- **Watermark Visibility**: The solid white background rectangle guarantees the NotebookLM watermark underneath is 100% obscured.
