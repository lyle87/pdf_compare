@echo off
setlocal

REM Build a single-file Windows executable (includes Python + dependencies)
REM Requirements: Python 3.8+ with pip installed

pushd %~dp0

python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller

pyinstaller ^
  --noconfirm ^
  --onefile ^
  --name "PDFCompare" ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import "fitz" ^
  app.py

if exist dist\PDFCompare.exe (
  echo.
  echo [OK] Built dist\PDFCompare.exe
  echo Double-click PDFCompare.exe to launch the app without installing Python.
) else (
  echo.
  echo [ERROR] Build failed. Check the PyInstaller output above.
)

popd
endlocal
