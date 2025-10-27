#!/bin/bash
set -euo pipefail
# Always work from this script's directory
cd "$(dirname "$0")"

echo "== Iran AIP Compiler — macOS build (Version 1.4.4) =="
if [[ "${1:-}" == "--clean" ]]; then rm -rf .venv-build build dist; fi

python3 -m venv .venv-build
./.venv-build/bin/python -m pip install --upgrade pip
./.venv-build/bin/pip install pyinstaller pypdf pillow
./.venv-build/bin/pip install -U "pypdf[crypto]" cryptography
./.venv-build/bin/pyinstaller --onefile --noconsole aip_compiler.py ^
  --collect-submodules cryptography ^
  --hidden-import pypdf._crypt_providers


# Only try to build icons if the PNG is present
if [[ -f "icons/iac.png" ]]; then
  ./.venv-build/bin/python make_icons.py || true
fi

ICON_ARG=()
if [[ -f "icons/iac.icns" ]]; then ICON_ARG=(--icon "icons/iac.icns"); fi
DATAS=(--add-data "maps:maps")

./.venv-build/bin/pyinstaller --noconfirm --windowed --onedir --name "Iran AIP Compiler" "${ICON_ARG[@]}" "${DATAS[@]}" "src/aip_compiler.py"
echo "Build complete. App bundle in dist/"
