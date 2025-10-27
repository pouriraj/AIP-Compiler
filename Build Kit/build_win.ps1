Param([string]$Python="py",[switch]$Clean)

Write-Host "== Iran AIP Compiler - Windows build (Version 1.4.3) ==" -ForegroundColor Cyan

if ($Clean) { Remove-Item ".venv-build","build","dist" -Recurse -Force -ErrorAction SilentlyContinue }

& $Python -m venv .venv-build
$PIP = ".\.venv-build\Scripts\pip.exe"
$PY  = ".\.venv-build\Scripts\python.exe"

& $PY -m pip install --upgrade pip
& $PIP install pyinstaller pypdf pillow

pip install -U "pypdf[crypto]" cryptography
pyinstaller --onefile --noconsole aip_compiler.py ^
  --collect-submodules cryptography ^
  --hidden-import pypdf._crypt_providers

# Optional icons (put icons/iac.png then run make_icons.py)
if (Test-Path ".\make_icons.py") { & $PY .\make_icons.py }

$iconArg = @()
if (Test-Path ".\icons\iac.ico") { $iconArg = @("--icon","icons\iac.ico") }

# Bundle maps directory into the EXE
$datas = @("--add-data","maps;maps")

& $PY -m PyInstaller --noconfirm --windowed --onefile --name "IranAIPCompiler" --collect-all tkinter --hidden-import tkinter --hidden-import _tkinter @iconArg @datas "src\aip_compiler.py"

if ($LASTEXITCODE -ne 0) { Write-Error "PyInstaller failed ($LASTEXITCODE)"; exit $LASTEXITCODE }
Write-Host "Build complete. See dist\IranAIPCompiler.exe" -ForegroundColor Green
