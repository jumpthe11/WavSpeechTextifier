@echo off
setlocal

:: Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found. Make sure you ran install.bat!
    echo Attempting to run anyway using system python...
)

echo Starting WavSpeechTextifier Streamlit UI...
streamlit run app.py

pause
