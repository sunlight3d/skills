---
name: pptx_remove_notebookLM_logo
description: >-
  Removes the NotebookLM logo watermark from Google Slides online and local PowerPoint (.pptx) files
  by adding a white cover rectangle in the bottom-right corner of each slide.
---

# PPTX/Google Slides Remove NotebookLM Logo

## Overview
This skill automatically covers the NotebookLM logo watermark (typically located at the bottom-right corner of full-slide images) by inserting a white rectangle with no border at the bottom-right of each slide. It supports both remote Google Slides presentations via the Google Slides API and local PowerPoint (`.pptx`) files.

## Dependencies
- `uv` Python package manager (required to run the utility script)
- `python-pptx` (auto-installed by `uv run` for local PowerPoint manipulation)
- `google-auth` (auto-installed by `uv run` for Google API authentication)
- `requests` (auto-installed by `uv run` for REST communication with Google API)

## Quick Start
You can trigger this skill using the command-line utility:

```bash
# Process a Google Slides presentation online using a Service Account
uv run pptx_remove_notebookLM_logo.py google-slides <PRESENTATION_ID> --credentials /path/to/credentials.json

# Process a local .pptx file (this will overwrite the file in-place)
uv run pptx_remove_notebookLM_logo.py local-pptx /path/to/presentation.pptx

# Process a local .pptx file and save it as a new file
uv run pptx_remove_notebookLM_logo.py local-pptx /path/to/presentation.pptx --output /path/to/output.pptx
```

## Utility Scripts
The utility script `pptx_remove_notebookLM_logo.py` exposes two main commands:

### `google-slides`
- **Description**: Connects to the Google Slides API, resets any previous image crops/transforms on the slides to original properties, and overlays a white cover shape on each slide at the bottom-right.
- **Arguments**:
  - `presentation_id` (positional, required): The ID of the presentation to modify.
  - `--credentials` (optional): Path to Google Service Account credentials JSON file. Defaults to `/Users/hoangnd/Documents/funix-auto-sheet-f464a0b5957e.json`.

### `local-pptx`
- **Description**: Uses `python-pptx` to open a local presentation file, scan all slides, overlay a white cover shape at the bottom-right of each slide, and save the presentation.
- **Arguments**:
  - `file_path` (positional, required): Path to the `.pptx` file.
  - `--output` (optional): Path to write the output. If not specified, overwrites the input file.

## Common Mistakes
- **Google Slides API Permission Error**: Ensure the service account email has **Editor** permissions on the presentation itself, and that the "Google Slides API" is enabled in the Google Cloud Console for the corresponding GCP project.
- **Incorrect Credentials Path**: If running the online mode, make sure the `--credentials` points to the correct JSON key file.
- **Network Timeouts on macOS**: If running on macOS, the script forces IPv4 resolution internally to avoid common connection timeouts with IPv6.
