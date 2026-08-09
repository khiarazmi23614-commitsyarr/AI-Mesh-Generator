@echo off
setlocal
python -m pip install --upgrade pyinstaller
pyinstaller --noconfirm --onefile --windowed --name AI-Mesh-Generator app\main.py
if errorlevel 1 exit /b 1
echo Build complete: dist\AI-Mesh-Generator.exe
