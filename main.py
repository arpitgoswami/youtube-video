"""
Story Video Maker main script
Orchestrates the video creation process using:
1. Image generation from prompts
2. Text-to-speech narration
3. Video assembly with synchronized audio
"""

from tqdm import tqdm
from config import config, story_scenes, TMPDIR
from image_generator import generate_image
from tts_generator import generate_tts
from video_assembler import assemble_video

def main():
    print("🎬 Starting Story Video Maker...")
    scene_files = []
    
    for i, scene in enumerate(tqdm(story_scenes, desc="Scenes")):
        print(f"\n[Scene {i+1}] Generating image...")
        img_path = generate_image(i, scene["prompt"])
        print(f"  ✅ Image saved: {img_path}")
        
        print("  🎤 Generating narration...")
        audio_path = generate_tts(i, scene["narration"])
        print(f"  ✅ Audio saved: {audio_path}")
        
        scene_files.append({"image": img_path, "audio": audio_path})
    
    print("\n📹 Assembling final video...")
    assemble_video(scene_files, config["output_file"], 
                  resolution=config["resolution"], 
                  fps=config["fps"])
    
    print(f"\n✅ Done! Video saved to {config['output_file']}")
    print(f"🗂 Temp files in {TMPDIR}")

if __name__ == "__main__":
    main()
