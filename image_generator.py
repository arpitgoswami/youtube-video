"""
Image generation module for the story video maker
"""

import requests
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Dict
from config import config, TMPDIR

def save_image_placeholder(scene_idx: int, prompt: str, out_path: Path) -> Path:
    """Creates a placeholder image with prompt text."""
    w, h = config["resolution"]
    img = Image.new("RGB", (w, h), (240, 240, 245))
    draw = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("arial.ttf", 24)
    except:
        fnt = ImageFont.load_default()
    draw.text((20, 20), f"Scene {scene_idx+1}", font=fnt, fill=(0, 0, 0))
    y = 60
    for line in prompt.split(", "):
        draw.text((20, y), line, font=fnt, fill=(60, 60, 60))
        y += 30
    img.save(out_path)
    return out_path

def generate_image_a4f(scene_idx: int, prompt: str, out_path: Path) -> Path:
    """Generate an image using A4F API."""
    a4f_base_url = "https://api.a4f.co/v1"
    headers = {
        "Authorization": f"Bearer {config['a4f_api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "provider-1/FLUX.1-schnell",
        "prompt": prompt,
        "num_images": 1,
        "size": f"{config['resolution'][0]}x{config['resolution'][1]}"
    }
    response = requests.post(f"{a4f_base_url}/images/generations", headers=headers, json=data, timeout=60)
    if response.status_code == 200:
        image_url = response.json()["data"][0]["url"]
        r2 = requests.get(image_url, timeout=60)
        r2.raise_for_status()
        out_path.write_bytes(r2.content)
        return out_path
    else:
        raise RuntimeError(f"A4F image generation failed: {response.status_code} - {response.text}")

def generate_image(prompt: str, output_path: str) -> Path:
    """Select image backend and generate image."""
    out_path = Path(output_path)
    if config["image_backend"] == "a4f":
        try:
            return generate_image_a4f(0, prompt, out_path)  # scene_idx not needed anymore
        except Exception as e:
            print(f"[warn] A4F image failed: {e}. Using placeholder.")
            return save_image_placeholder(0, prompt, out_path)  # scene_idx not needed anymore
    else:
        return save_image_placeholder(0, prompt, out_path)  # scene_idx not needed anymore