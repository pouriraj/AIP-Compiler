#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

echo "== Iran AIP Compiler — macOS build (Version 1) =="
if [[ "${1:-}" == "--clean" ]]; then rm -rf .venv-build build dist; fi

python3 -m venv .venv-build
./.venv-build/bin/python -m pip install --upgrade pip
./.venv-build/bin/pip install pyinstaller pypdf pillow

if [[ -f "icons/iac.png" ]]; then
  ./.venv-build/bin/python make_icons.py || true
fi

ICON_ARG=()
[[ -f "icons/iac.icns" ]] && ICON_ARG=(--icon "icons/iac.icns")
DATAS=(--add-data "maps:maps")

./.venv-build/bin/pyinstaller --noconfirm --windowed --onedir --name "Iran AIP Compiler" "${ICON_ARG[@]}" "${DATAS[@]}" "src/aip_compiler.py"
echo "Build complete. App bundle in dist/"
