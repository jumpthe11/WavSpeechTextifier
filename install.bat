@echo off
set /p use_venv="Do you want to create and use a Virtual Environment (venv) to keep dependencies isolated? (Y/N): "

if /i "%use_venv%"=="Y" (
    echo.
    echo Creating virtual environment (venv)...
    python -m venv venv
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo.
    echo Proceeding without Virtual Environment...
)

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ==============================================================
echo Installation Complete!
if /i "%use_venv%"=="Y" (
    echo All dependencies are installed inside the "venv" folder.
    echo If you want to delete them later, simply delete the "venv" folder.
) else (
    echo Dependencies were installed in your global Python environment.
)
echo ==============================================================
pause
