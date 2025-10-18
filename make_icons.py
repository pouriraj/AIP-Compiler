#!/usr/bin/env python3
from PIL import Image
from pathlib import Path

icons = Path("icons")
png = icons/"iac.png"
icons.mkdir(exist_ok=True, parents=True)
if not png.exists():
    print("icons/iac.png not found, skipping.")
    raise SystemExit(0)

# ICO (Windows)
Image.open(png).save(icons/"iac.ico", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])

# ICNS (macOS) via Pillow's icns save (Pillow >=9.2)
Image.open(png).save(icons/"iac.icns")
print("Wrote:", icons/"iac.ico", icons/"iac.icns")
