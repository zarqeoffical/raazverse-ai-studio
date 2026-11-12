from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
IMG_DIR = ROOT / "assets" / "images"
AUDIO = ROOT / "assets" / "audio" / "narration.mp3"
SRT = ROOT / "content" / "captions.srt"
OUT_DIR = ROOT / "output"
OUT = OUT_DIR / "raazverse_short.mp4"

def run(command):
    subprocess.run(command, check=True)

def main():
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ERROR: ffmpeg is not installed.")

    images = sorted(
        p for p in IMG_DIR.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )
    if not images:
        raise SystemExit("ERROR: Upload at least one image to assets/images/.")

    OUT_DIR.mkdir(exist_ok=True)
    concat_file = OUT_DIR / "images.txt"

    with concat_file.open("w", encoding="utf-8") as handle:
        for img in images:
            safe = str(img.resolve()).replace("\\", "/").replace("'", "'\\''")
            handle.write(f"file '{safe}'\n")
            handle.write("duration 5\n")
        safe = str(images[-1].resolve()).replace("\\", "/").replace("'", "'\\''")
        handle.write(f"file '{safe}'\n")

    video_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1,fps=30,format=yuv420p"
    )
    if SRT.exists() and SRT.stat().st_size:
        srt_path = str(SRT.resolve()).replace("\\", "/").replace(":", "\\:")
        video_filter += f",subtitles='{srt_path}'"

    command = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-vf", video_filter, "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "23", "-pix_fmt", "yuv420p"
    ]

    if AUDIO.exists():
        command += [
            "-i", str(AUDIO), "-map", "0:v:0", "-map", "1:a:0",
            "-c:a", "aac", "-b:a", "160k", "-shortest"
        ]
    else:
        command += ["-an"]

    command += ["-movflags", "+faststart", str(OUT)]
    run(command)
    print(f"SUCCESS: Created {OUT}")

if __name__ == "__main__":
    main()
