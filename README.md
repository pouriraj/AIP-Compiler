# Iran AIP Compiler (Version 1)

> **Turn messy eAIP folders into one, tablet‑friendly PDF with rich bookmarks.**

## Features
- Combine **AIP (GEN/ENR/AD 0–3)**, **AIC**, **SUP**, and **AMDT** into a single PDF.
- Clean bookmark tree with **PART 1–3** and family groups; **AD2/AD3 by ICAO** with `CODE — Name` and base `CODE.pdf` forced to the top.
- **AIC/SUP year grouping** (handles forms like `AIC 1-14` → 2014, `AIC4-08` → 2008, `AIC 2024.1` → 2024).
- **AMDT** placed **first** inside **AIP**.
- Dynamic PDF metadata (Title, Author, Subject, Creator/Producer, Language, Page Count).
- **GUI** with live logs + **TSV template export** for customization.
- **CLI** for batch/automation.

## Where to get the AIP
- **Primary:** https://ais.airport.ir/aip-cd
- **Portal:** https://ais.airport.ir/

Download the official eAIP package and **extract it**. The root should contain subfolders: **AIP**, **AIC**, **SUP**, **AMDT** (and often `AUTORUN.INF`).

## Quick Start (GUI)
1. Download/clone this repo. On Windows, run `dist/IranAIPCompiler.exe` if you have a release; otherwise build first (below).
2. Launch the app.
3. **AIP Root Folder** → select the extracted **eAIP** root.
4. **Output PDF** → leave blank to auto-title from AIRAC/WEF (you can change it).
5. **TSV Maps Dir (optional)** → leave empty to use embedded maps, or click **Export TSV templates**, edit, and point to your folder.
6. Click **Compile** and watch the **log**.

## Building the app
### Windows
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.uild_win.ps1 -Clean
.\dist\IranAIPCompiler.exe
```
### macOS
```bash
chmod +x build_mac.command
./build_mac.command --clean
open dist/
```

## CLI usage
```bash
# GUI
IranAIPCompiler.exe --gui

# Full compile (quote paths with spaces)
IranAIPCompiler.exe --root "D:\AIP\CD eAIP AIRAC 2-25 WEF 02 OCT 2025(RAR)" -o "D:\AIP\Iran AIP AIRAC 2-25 (WEF 02 OCT 2025).pdf"
```

Args:
- `--root` or positional `root`: eAIP root path
- `-o, --output`: output path (defaults to computed title)
- `--maps-dir`: folder with TSV overrides (defaults to embedded)
- `--gui`: open GUI

## Customizing the bookmark maps (TSV)
Use the **maps/*.tsv** files (tab‑separated). Columns for `GEN.tsv`, `ENR.tsv`, `AD.tsv`:

- **Order**: sort key, numeric
- **Level**: bookmark level relative to the family parent
- **Code**: e.g., `GEN 0.6`
- **Title**: e.g., `Table of Contents to Part 1` (renders as `GEN 0.6 — Table of Contents to Part 1`)
- **Pattern**: `fnmatch` glob(s); you can OR with `|`
- **Family**: group title, e.g., `GEN 1 — National regulations & requirements`
- **Enabled**: `TRUE` or `FALSE`
- **Notes**: free text

`AD_ICAO.tsv` gives `CODE — Name` for AD2/AD3 grouping.

## Troubleshooting
- **Only a few pages compiled** → ensure the correct **root** folder; check log for `[HARDSET] Missing ...`; adjust **Pattern** in TSVs or add alternates with `|`.
- **“unrecognized arguments: -- C:/path”** → don’t put `--` before the positional root path; or use `--root "C:/path"`.
- **“No such file ... GEN.tsv”** → if you set **TSV Maps Dir**, it must include **GEN.tsv, ENR.tsv, AD.tsv, AD_ICAO.tsv**. Leave it empty to use embedded maps.
- **AIC/SUP year wrong** → rename files to include a year (e.g., `AIC 2024.1`), or edit the year bucketing rules in code.
- **macOS icon step fails** → ensure `icons/iac.png`; else the build script skips icons.

## License
MIT. Source PDFs belong to their owners (IAC). This tool is for operational convenience.

— Built with ❤️ by Ali Pouriraj
