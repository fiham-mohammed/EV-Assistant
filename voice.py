import os
import tempfile
from pathlib import Path

import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
CHANNELS = 1
DEFAULT_RECORD_SECONDS = 5

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "base.en"
)

_whisper_model = None


def get_whisper_model():
    global _whisper_model

    if _whisper_model is None:
        print(
            f"[Voice] Loading Whisper model: "
            f"{WHISPER_MODEL}"
        )

        _whisper_model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8",
        )

    return _whisper_model


def get_microphone_name():
    device = sd.query_devices(
        kind="input"
    )

    return device["name"]


def record_audio(
    duration=DEFAULT_RECORD_SECONDS
):
    print(
        f"\n[Voice] Microphone: "
        f"{get_microphone_name()}"
    )

    print(
        f"[Voice] Listening for "
        f"{duration} seconds..."
    )

    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
    )

    sd.wait()

    print("[Voice] Recording complete.")

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False,
    )

    temp_file.close()

    audio_path = Path(temp_file.name)

    write(
        audio_path,
        SAMPLE_RATE,
        recording,
    )

    return audio_path


def transcribe_audio(audio_path):
    model = get_whisper_model()

    print("[Voice] Transcribing...")

    segments, _ = model.transcribe(
        str(audio_path),
        language="en",
        vad_filter=True,
    )

    text_parts = []

    for segment in segments:
        text = segment.text.strip()

        if text:
            text_parts.append(text)

    return " ".join(text_parts).strip()


def listen(duration=DEFAULT_RECORD_SECONDS):
    audio_path = record_audio(duration)

    try:
        return transcribe_audio(
            audio_path
        )

    finally:
        audio_path.unlink(
            missing_ok=True
        )


if __name__ == "__main__":
    print("=" * 50)
    print("EV Voice Test")
    print("=" * 50)

    text = listen()

    if text:
        print(
            f"\nEV heard: {text}"
        )
    else:
        print(
            "\nEV couldn't detect speech."
        )