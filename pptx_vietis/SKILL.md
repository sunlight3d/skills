---
name: pptx_vietis
description: Creates beautiful, branded PowerPoint presentations (.pptx) matching the VietIS corporate identity. Trigger this skill whenever the user asks to generate a slide deck, presentation, or ppt/pptx file and mentions VietIS, "chuẩn màu VietIS", or "VietIS templates". This skill provides a specialized Node.js template using pptxgenjs to build slides programmatically.
---

# VietIS PowerPoint Generator Skill

This skill enables you to generate `.pptx` presentations that adhere strictly to the VietIS brand guidelines (colors, fonts, margins, shapes, and backgrounds). 

When generating a VietIS PowerPoint presentation, **ALWAYS** follow these steps:

## Prerequisites
You must install `pptxgenjs` in the scratch directory or wherever you will execute the script:
```bash
npm install pptxgenjs
```

## Creating the Script
Instead of writing a script from scratch, **ALWAYS** copy the template script provided at `scripts/create_ppt_template.js` inside this skill's folder to the current working directory or a scratchpad (e.g., `create_ppt.js`). 

The template contains all the correct VietIS brand colors:
- `TEAL`: `"00A89D"`
- `ORANGE`: `"F05A28"`
- `LIGHT_TEAL`: `"E6F6F5"`
- `LIGHT_ORANGE`: `"FDEEE9"`
- `DARK_GRAY`: `"333333"`

It also securely points to the essential assets required for the master slide:
- `assets/bg.png` (The abstract wavy teal background)
- `assets/logo.png` (The official VietIS logo)

## Adapting the Content
1. Copy the `create_ppt_template.js` file into your workspace (or rewrite it inline).
2. Look at the helper functions provided: `addTitle()`, `addSubtext()`, `addBox()`, `addArrow()`.
3. Use `addBox()` to create beautiful rounded rectangles. Ensure you pass the correct arguments:
   `addBox(slide, x, y, width, height, symbol_emoji, title, body, bgColor, borderColor, titleColor)`
   - The symbol emoji should be a single character if provided.
   - You MUST ensure x, y, width, and height are well-measured so the boxes don't overlap. (Grid usually is 10 inches wide by 5.625 inches tall).
4. Do NOT mess with the internal logic of `addBox()` (e.g. `margin: 10`, `paraSpaceAfter: 4`). These specific values were painstakingly calibrated to prevent text from overflowing and to ensure perfect vertical alignment between icons and text.

## Execution
Run the resulting Node.js script:
```bash
node create_ppt.js
```
Provide the generated `.pptx` file directly to the user. Do not give them the `.js` code unless they explicitly ask for it; they only care about the final PowerPoint file!
