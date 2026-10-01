import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseTranscriber(ABC):
    """
    Abstract Base Class for speech-to-text transcribers.
    """

    def __init__(
        self,
        model_name: str,
        language: Optional[str] = "en",
        device: Optional[str] = "cpu",
        models_dir: Optional[str] = None
    ):
        self.model_name = model_name
        self.language = language
        self.device = device
        self.models_dir = models_dir

    @abstractmethod
    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribes the audio file at audio_path and returns the text string.
        """
        pass





class FasterWhisperTranscriber(BaseTranscriber):
    """
    Local Whisper transcriber using faster-whisper (CTranslate2 backend).
    Extremely lightweight and fast. Uses VAD to prevent hallucinations on short audio.
    """

    def __init__(
        self,
        model_name: str = "base.en",
        language: Optional[str] = "en",
        device: Optional[str] = "cpu",
        models_dir: Optional[str] = None
    ):
        super().__init__(model_name, language, device, models_dir)
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise ImportError(
                "faster-whisper package is not installed. Install it via 'pip install faster-whisper'."
            )

        compute_type = "float16" if device and "cuda" in device.lower() else "int8"
        kwargs = {}
        if self.models_dir:
            os.makedirs(self.models_dir, exist_ok=True)
            kwargs["download_root"] = self.models_dir

        print(f"Loading Faster-Whisper model '{self.model_name}' on device '{self.device}' (compute_type={compute_type})"
              f"{f' (models_dir: {self.models_dir})' if self.models_dir else ''}...")
        self.model = WhisperModel(self.model_name, device=self.device or "cpu", compute_type=compute_type, **kwargs)

    def transcribe(self, audio_path: Path) -> str:
        # vad_filter=True is the magic setting that prevents Whisper from hallucinating on short audio!
        segments, _ = self.model.transcribe(
            str(audio_path),
            language=self.language,
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False
        )
        return " ".join([segment.text for segment in segments]).strip()



PROVIDERS = {
    "faster-whisper": FasterWhisperTranscriber,
}


def get_transcriber(
    provider: str = "faster-whisper",
    model_name: str = "base.en",
    language: Optional[str] = "en",
    device: Optional[str] = "cpu",
    models_dir: Optional[str] = None
) -> BaseTranscriber:
    """
    Factory function to get a transcriber instance based on the provider name.
    """
    provider_key = provider.lower().strip()
    if provider_key not in PROVIDERS:
        supported = ", ".join(PROVIDERS.keys())
        raise ValueError(
            f"Unsupported provider '{provider}'. Supported providers are: {supported}"
        )

    transcriber_cls = PROVIDERS[provider_key]
    return transcriber_cls(
        model_name=model_name,
        language=language,
        device=device,
        models_dir=models_dir
    )

