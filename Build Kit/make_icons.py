from pathlib import Path
try:
    from PIL import Image
except Exception:
    print("Pillow not installed; skipping icon conversion."); raise SystemExit(0)

root = Path(__file__).resolve().parent
png = root/"icons/iac.png"
if not png.exists():
    print("icons/iac.png missing"); raise SystemExit(0)

ico = root/"icons/iac.ico"
icns = root/"icons/iac.icns"
img = Image.open(png).convert("RGBA")
img.save(ico, sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
img.save(icns, sizes=[(16,16),(32,32),(64,64),(128,128),(256,256),(512,512)])
print("Wrote:", ico, icns)
