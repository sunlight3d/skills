---
name: pptx-add-vietis-logo
description: >-
  Adds the VietIS logo to the bottom right corner of Google Slides presentations, covering previous watermark logos. Supports both individual presentations and Google Drive folders.
---

# PPTX Add VietIS Logo

## Overview
This skill automatically covers any previous logos (like NotebookLM watermarks) at the bottom right corner of a Google Slides presentation by first inserting a white rectangle with no border, and then overlaying the VietIS logo. It uses the Google Slides API to batch update all slides in a presentation, and intelligently skips slides that already contain the logo.

It can process a single Google Slides presentation or automatically discover and process all presentations inside a specified Google Drive folder.

## Configuration
The script calculates the size of the logo maintaining aspect ratio (3246x1280) with a fixed width of `2,000,000 EMU` (~157 pt). It leaves a small margin of `100,000 EMU` from the bottom-right edges to perfectly cover most typical corner watermarks.

## Dependencies
- `uv` Python package manager (required to run the utility script)
- `google-auth` (auto-installed by `uv run` for Google API authentication)
- `google-api-python-client` (auto-installed by `uv run` for Google API interaction)

## Quick Start
You can trigger this skill using the command-line utility:

```bash
# Process a single Google Slides presentation
uv run pptx_add_vietis_logo.py <PRESENTATION_ID> --credentials /path/to/credentials.json

# Process all presentations inside a Google Drive folder
uv run pptx_add_vietis_logo.py <FOLDER_ID> --folder --credentials /path/to/credentials.json
```

## Features
- **Smart Skipping**: The script automatically checks each slide for existing logo covers in the bottom-right corner and skips them, allowing you to run it multiple times safely.
- **Folder Batching**: Easily process multiple slide decks in a single command using the `--folder` flag.

## Common Mistakes
- **Google Slides API Permission Error**: Ensure the service account email has **Editor** permissions on the presentation (or folder) itself, and that the "Google Slides API" is enabled in the Google Cloud Console for the corresponding GCP project.
- **Network Timeouts on macOS**: If running on macOS, the script forces IPv4 resolution internally to avoid common connection timeouts with IPv6.
- **Image URL expiry**: The script defaults to an image URL. If that URL becomes unavailable, a new public URL for the logo must be provided via the `--image-url` argument or updated in the script.
