---
name: pptx-add-netpro-logo
description: >-
  Adds the Netpro logo to the bottom right corner of Google Slides presentations, covering previous watermark logos.
---

# PPTX Add Netpro Logo

## Overview
This skill automatically covers any previous logos (like NotebookLM watermarks) at the bottom right corner of a Google Slides presentation by first inserting a white rectangle with no border, and then overlaying the Netpro logo. It uses the Google Slides API to batch update all slides in a presentation.

## Configuration
The script calculates the size of the logo maintaining aspect ratio (2592x1660) with a fixed width of `2,000,000 EMU` (~157 pt). It leaves a small margin of `100,000 EMU` from the bottom-right edges to perfectly cover most typical corner watermarks.

## Dependencies
- `uv` Python package manager (required to run the utility script)
- `google-auth` (auto-installed by `uv run` for Google API authentication)
- `google-api-python-client` (auto-installed by `uv run` for Google API interaction)

## Quick Start
You can trigger this skill using the command-line utility:

```bash
# Process a Google Slides presentation online using a Service Account
uv run pptx_add_netpro_logo.py <PRESENTATION_ID> --credentials /path/to/credentials.json
```

## Common Mistakes
- **Google Slides API Permission Error**: Ensure the service account email has **Editor** permissions on the presentation itself, and that the "Google Slides API" is enabled in the Google Cloud Console for the corresponding GCP project.
- **Network Timeouts on macOS**: If running on macOS, the script forces IPv4 resolution internally to avoid common connection timeouts with IPv6.
- **Image URL expiry**: The script defaults to an image URL. If that URL becomes unavailable, a new public URL for the logo must be provided via the `--image-url` argument or updated in the script. (A local copy of `logo_netpro.png` is provided in this skill's folder).
