Param([string]$Python="py",[switch]$Clean)
Write-Host "== Iran AIP Compiler - Windows build (Version 1) ==" -ForegroundColor Cyan
if ($Clean) { if (Test-Path ".venv-build"){Remove-Item ".venv-build" -Recurse -Force}; if (Test-Path "build"){Remove-Item "build" -Recurse -Force}; if (Test-Path "dist"){Remove-Item "dist" -Recurse -Force} }
& $Python -m venv .venv-build
$PIP = ".\.venv-build\Scripts\pip.exe"; $PY = ".\.venv-build\Scripts\python.exe"
& $PY -m pip install --upgrade pip
& $PIP install pyinstaller pypdf pillow
if (Test-Path ".\make_icons.py") { & $PY .\make_icons.py }
$iconArg = @(); if (Test-Path ".\icons\iac.ico") { $iconArg = @("--icon","icons\iac.ico") }
$datas = @("--add-data","maps;maps")
& $PY -m PyInstaller --noconfirm --windowed --onefile --name "IranAIPCompiler" $iconArg $datas "src\aip_compiler.py"
Write-Host "Build complete. See dist\IranAIPCompiler.exe" -ForegroundColor Green
