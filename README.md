# WavSpeechTextifier

WavSpeechTextifier is a Python utility that scans a directory for `.wav` audio files, transcribes them using local AI speech-to-text models (specifically `faster-whisper`), and renames the files based on their transcribed content. This is particularly useful for organizing datasets of unlabelled voice lines or audio clips.

## Features

- **Local Inference:** Transcribe audio files entirely locally using `faster-whisper` (CTranslate2 backend). It is extremely lightweight, uses very little memory, and runs incredibly fast on CPU.
- **VAD Filtering for Short Audio:** Voice Activity Detection (VAD) is enabled to aggressively filter out silence, preventing Whisper from "hallucinating" words on short audio clips (1-5 seconds).
- **Auto-Renaming:** Automatically generates safe, OS-friendly filenames from the spoken text and prevents overwriting by appending counters.
- **Configurable:** Fully configurable via command-line arguments (set default model, device, max filename length, etc.).
- **Easy Cleanup:** Models and dependencies are fully isolated. Dependencies go into the `venv` folder and models go into the `models` folder. Delete these folders when you are done to completely clean up the tool.
- **Progress Tracking:** Shows progress during the transcription and renaming process using `tqdm`.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/WavSpeechTextifier.git
   cd WavSpeechTextifier
   ```

2. **Install dependencies:**
   We provide an `install.bat` script for Windows users that automatically creates a virtual environment (`venv` folder) and installs all dependencies inside it. This keeps your system clean.
   - Simply double-click **`install.bat`**
   
   *(Manual installation)*:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

### 🎨 Web Interface (Recommended)
We have added a beautiful, modern web interface using Streamlit!
1. Double-click **`run_ui.bat`**
2. A browser window will open automatically.
3. Select your folder, choose your model, and click start!

### 💻 Command Line Interface
If your virtual environment is activated, you can run the python script directly from the terminal.

```bash
# Activate environment (Windows)
venv\Scripts\activate

# Run manually:
python voiceline_renamer.py /path/to/wav/files
```

### Command-line Arguments

You can provide settings directly from the command line:

```bash
python voiceline_renamer.py /path/to/wav/files --model small.en --device cpu
```

- `--provider`: Speech-to-text provider (default: `faster-whisper`).
- `--model`: Whisper model size (default: `small.en`).
- `--device`: Compute device to run inference on, e.g., `cpu` or `cuda` (default: `cpu`).
- `--max-length`: Maximum length of the generated filename (default: `80`).
- `--models-dir`: The directory where the models are cached locally.

## Requirements
- Python 3.8+
- `faster-whisper`
