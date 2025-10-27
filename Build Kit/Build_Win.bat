@echo off
setlocal
cd /d %~dp0

where python >nul 2>nul || (
  echo Python not found. Install Python 3 from https://www.python.org/downloads/ and check "Add python.exe to PATH".
  pause
  exit /b 1
)

python -m venv .venv-build
call .venv-build\Scripts\activate

python -m pip install --upgrade pip
pip install pyinstaller pypdf pillow

pip install -U "pypdf[crypto]" cryptography
pyinstaller --onefile --noconsole aip_compiler.py ^
  --collect-submodules cryptography ^
  --hidden-import pypdf._crypt_providers

if exist make_icons.py python make_icons.py

set ICON_ARG=
if exist icons\iac.ico set ICON_ARG=--icon icons\iac.ico

pyinstaller --noconfirm --windowed --onefile --name IranAIPCompiler %ICON_ARG% src\aip_compiler.py

echo.
echo Done. EXE: dist\IranAIPCompiler.exe
pause
