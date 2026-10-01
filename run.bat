@echo off
:: Activate the virtual environment only if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Run the script with any arguments passed to this batch file
python voiceline_renamer.py %*

:: If there was an error (e.g. user didn't provide a directory path), pause so they can read the error message
if %ERRORLEVEL% neq 0 (
    echo.
    echo Script exited with an error. Did you forget to provide the folder path?
    echo Example usage from command line: run.bat /path/to/wav/files
    pause
)
