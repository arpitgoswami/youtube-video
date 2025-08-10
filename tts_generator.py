"""
Text-to-speech generation module for the story video maker
"""

from pathlib import Path
from gtts import gTTS
from config import config, TMPDIR

def tts_gtts(text: str, filename: Path, lang: str = "en") -> Path:
    """Generate TTS using gTTS."""
    tts = gTTS(text=text, lang=lang)
    tts.save(str(filename))
    return filename

def generate_speech(text: str, output_path: str) -> Path:
    """Generate TTS narration."""
    out_path = Path(output_path)
    if config["tts_backend"] == "gtts":
        try:
            return tts_gtts(text, out_path)
        except Exception as e:
            print(f"[warn] gTTS failed: {e}. No narration generated.")
            raise RuntimeError(f"TTS generation failed: {str(e)}")
    else:
        raise ValueError(f"Unsupported TTS backend: {config['tts_backend']}")