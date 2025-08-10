"""
Configuration settings for the story video maker
"""

import uuid
import tempfile
from pathlib import Path

# Core configuration
config = {
    "output_file": "story_video.mp4",
    "resolution": (720, 720),     # match A4F output size
    "fps": 24,
    "image_backend": "a4f",       # we use A4F for images
    "tts_backend": "gtts",
    "crossfade_duration": 1.0,    # 1 second crossfade between scenes
    "a4f_api_key": "ddc-a4f-b51043b4eb3b4486a26eef5790319455",  # replace in production
    "scene_padding_seconds": 0.3
}

# Story scenes
story_scenes = [
    {
        "prompt": "A beautiful storybook opening with golden letters on a magical background, sparkles and warm colors",
        "narration": "Amir's Dream - A Story of Courage and Wonder"
    },
    {
        "prompt": "A sleepy village at dawn, soft mist, warm golden light, hyperrealistic, cinematographic",
        "narration": "In a small, sleepy village, the sun rose over fields of gold."
    },
    {
        "prompt": "A little boy running through tall grass with a handmade kite, joyful expression",
        "narration": "There lived a boy named Amir who carried dreams in his pockets and a kite in his hands."
    },
    {
        "prompt": "A wise old woman weaving a tapestry outside a clay house, intricate patterns, warm colors",
        "narration": "Every evening he would visit the old weaver who told stories stitched into cloth."
    },
    {
        "prompt": "A dramatic storm approaching the village with lightning, but a small house with a warm light inside",
        "narration": "One stormy night, the sky roared and a lesson about courage was about to begin."
    },
    {
        "prompt": "A beautiful sunset over the village with a boy flying a kite high in the golden sky, storybook ending style",
        "narration": "Thanks for watching Amir's Dream. May your dreams take flight too."
    }
]

# Temporary directory setup
TMPDIR = Path(tempfile.gettempdir()) / f"story_video_{uuid.uuid4().hex}"
TMPDIR.mkdir(parents=True, exist_ok=True)