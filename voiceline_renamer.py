import argparse
import os
import re
from pathlib import Path
from tqdm import tqdm

from transcribers import get_transcriber, PROVIDERS

# Windows CUDA 12 DLL workaround for CTranslate2 (faster-whisper)
if os.name == "nt":
    import site
    for sp in site.getsitepackages():
        cublas_path = os.path.join(sp, "nvidia", "cublas", "bin")
        cudnn_path = os.path.join(sp, "nvidia", "cudnn", "bin")
        if os.path.exists(cublas_path) and cublas_path not in os.environ["PATH"]:
            os.environ["PATH"] = cublas_path + os.pathsep + os.environ["PATH"]
        if os.path.exists(cudnn_path) and cudnn_path not in os.environ["PATH"]:
            os.environ["PATH"] = cudnn_path + os.pathsep + os.environ["PATH"]


def clean_filename(text: str, max_length: int = 80) -> str:
    """
    Cleans the transcribed text to make it a valid, OS-friendly filename.
    """
    # Remove invalid characters for Windows/macOS/Linux
    clean_text = re.sub(r'[\\/*?:"<>|]', "", text)
    # Remove excessive spaces and trim
    clean_text = " ".join(clean_text.split()).strip()

    # Truncate to avoid OS path length limits
    if len(clean_text) > max_length:
        clean_text = clean_text[:max_length].rsplit(' ', 1)[0] + "..."

    return clean_text


def get_unique_path(directory: Path, base_name: str, extension: str) -> Path:
    """
    Ensures no files are overwritten by appending a counter to the filename.
    """
    target_path = directory / f"{base_name}{extension}"
    counter = 1

    while target_path.exists():
        target_path = directory / f"{base_name}_{counter}{extension}"
        counter += 1

    return target_path


def process_audio_files(
    directory_path: str,
    provider: str = "faster-whisper",
    model_name: str = "small.en",
    language: str = "en",
    device: str = "cpu",
    max_length: int = 80,
    models_dir: str = None
) -> None:
    """
    Scans the directory for .wav files and renames them based on their content using the chosen model/provider.
    """
    directory = Path(directory_path)

    if not directory.exists() or not directory.is_dir():
        print(f"Error: The directory '{directory_path}' does not exist.")
        return

    wav_files = list(directory.glob("*.wav"))

    if not wav_files:
        print(f"No .wav files found in '{directory_path}'.")
        return

    if models_dir:
        os.makedirs(models_dir, exist_ok=True)
        abs_models_dir = os.path.abspath(models_dir)
        # Set cache directories to keep downloads local
        os.environ["HF_HOME"] = abs_models_dir

    print(f"Initializing transcriber (Provider: '{provider}', Model: '{model_name}', Device: '{device}')...")
    try:
        transcriber = get_transcriber(
            provider=provider,
            model_name=model_name,
            language=language,
            device=device,
            models_dir=models_dir
        )
    except Exception as e:
        print(f"Failed to initialize transcriber: {e}")
        return

    print(f"Found {len(wav_files)} .wav files. Starting transcription...\n")

    success_count = 0

    for file_path in tqdm(wav_files, desc="Renaming Files", unit="file"):
        try:
            transcription = transcriber.transcribe(file_path)

            if not transcription or not transcription.strip():
                continue  # Skip empty audio or silent transcriptions

            new_base_name = clean_filename(transcription, max_length=max_length)
            if not new_base_name:
                continue

            target_path = get_unique_path(directory, new_base_name, file_path.suffix)

            file_path.rename(target_path)
            success_count += 1

        except Exception as e:
            tqdm.write(f"Error processing {file_path.name}: {e}")

    print(f"\nTask Completed! Successfully renamed {success_count}/{len(wav_files)} files.")


if __name__ == "__main__":
    # Get defaults from environment variables or fallback to defaults
    env_provider = os.getenv("MODEL_PROVIDER", "faster-whisper")
    env_model = os.getenv("MODEL_NAME", os.getenv("MODEL_SIZE", "small.en"))
    env_language = os.getenv("LANGUAGE", "en")
    env_device = os.getenv("DEVICE", "cpu")
    env_max_length = int(os.getenv("MAX_FILENAME_LENGTH", "80"))
    env_models_dir = os.getenv("MODELS_DIR", os.getenv("DOWNLOAD_ROOT", "./models"))

    parser = argparse.ArgumentParser(
        description="Rename random .wav voicelines using local AI speech-to-text models."
    )
    parser.add_argument(
        "directory",
        type=str,
        nargs="?",
        default=None,
        help="Path to the folder containing .wav files (if omitted, a folder selection dialog will open)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=env_provider,
        choices=list(PROVIDERS.keys()),
        help=f"Speech-to-text provider (default: {env_provider})"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=env_model,
        help=f"Model name/size or model path to use (default: {env_model})"
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default=env_models_dir,
        help=f"Directory path where models are saved/downloaded (default: {env_models_dir})"
    )
    parser.add_argument(
        "--language",
        type=str,
        default=env_language,
        help=f"Language code for transcription (default: {env_language})"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=env_device,
        help=f"Device for inference e.g. cpu, cuda (default: {env_device})"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=env_max_length,
        help=f"Maximum filename length (default: {env_max_length})"
    )

    args = parser.parse_args()
    
    directory_path = args.directory
    
    # If no directory is provided via command line, open a GUI folder picker
    if not directory_path:
        print("No folder path provided via command line. Opening folder selector...")
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Hide the root tkinter window
            root = tk.Tk()
            root.withdraw()
            # Make sure it appears on top
            root.attributes('-topmost', True)
            
            directory_path = filedialog.askdirectory(title="Select folder with .wav files")
            
            if not directory_path:
                print("No folder selected. Exiting.")
                exit(0)
        except ImportError:
            print("Error: Could not open folder dialog (tkinter not found). Please provide the directory via command line.")
            exit(1)

    process_audio_files(
        directory_path=directory_path,
        provider=args.provider,
        model_name=args.model,
        language=args.language,
        device=args.device,
        max_length=args.max_length,
        models_dir=args.models_dir
    )