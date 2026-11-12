from pathlib import Path
import json
import math
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
SCENES_DIR = OUT / "scenes"
DATA = json.loads((ROOT / "content" / "video.json").read_text(encoding="utf-8"))
W, H = 1080, 1920
FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"

def font(size, bold=False):
    path = FONT_BOLD_PATH if bold and Path(FONT_BOLD_PATH).exists() else FONT_PATH
    return ImageFont.truetype(path, size)

def gradient(top, bottom):
    im = Image.new("RGB", (W, H))
    p = im.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(top[i] * (1-t) + bottom[i] * t) for i in range(3))
        for x in range(W):
            p[x, y] = c
    return im

def centered(draw, text, y, fnt, fill, spacing=18):
    lines = []
    for para in text.split("\n"):
        lines.extend(textwrap.wrap(para, width=23) or [""])
    block_h = sum(draw.textbbox((0,0), line, font=fnt)[3] for line in lines) + spacing*(len(lines)-1)
    yy = y - block_h//2
    for line in lines:
        box = draw.textbbox((0,0), line, font=fnt)
        draw.text(((W-(box[2]-box[0]))//2, yy), line, font=fnt, fill=fill, stroke_width=1, stroke_fill=(8,15,35))
        yy += (box[3]-box[1]) + spacing

def draw_visual(draw, kind, idx):
    cx, cy = W//2, 770
    if kind in ("question", "ending"):
        for r, col in [(300,(20,60,100)),(230,(23,91,139)),(155,(37,130,175))]:
            draw.ellipse((cx-r,cy-r,cx+r,cy+r), outline=col, width=5)
        draw.ellipse((cx-78,cy-78,cx+78,cy+78), fill=(110,190,230))
        for k in range(12):
            a = math.pi*2*k/12
            x1,y1=cx+105*math.cos(a),cy+105*math.sin(a)
            x2,y2=cx+285*math.cos(a),cy+285*math.sin(a)
            draw.line((x1,y1,x2,y2),fill=(80,155,205),width=5)
    elif kind == "spectrum":
        colors=[(110,50,210),(45,95,230),(35,175,220),(50,190,120),(235,205,65),(240,135,55),(220,65,65)]
        for i,c in enumerate(colors):
            x=180+i*105
            draw.rounded_rectangle((x,cy-180,x+78,cy+180),radius=32,fill=c)
        draw.ellipse((cx-250,cy-260,cx-130,cy-140),fill=(255,230,140))
        draw.line((cx-140,cy-200,cx-70,cy-90),fill=(255,250,215),width=12)
    elif kind == "molecules":
        pts=[(cx-190,cy-130),(cx+10,cy-200),(cx+190,cy-70),(cx-80,cy+65),(cx+130,cy+155),(cx-240,cy+210)]
        for x,y in pts:
            draw.ellipse((x-45,y-45,x+45,y+45),fill=(65,150,210),outline=(180,225,255),width=5)
        for i in range(len(pts)-1):
            draw.line((*pts[i],*pts[i+1]),fill=(100,160,200),width=7)
        for k in range(9):
            x=120+k*105
            draw.line((x,cy-300,x+75,cy-230),fill=(90,165,245),width=8)
    elif kind == "blue_sky":
        draw.rectangle((120,cy-230,960,cy+220),fill=(28,110,195),outline=(110,190,245),width=6)
        draw.ellipse((cx+170,cy-310,cx+300,cy-180),fill=(255,220,130))
        for k in range(8):
            x=180+k*95
            draw.line((x,cy-80,x-35,cy+100),fill=(140,205,255),width=8)
        draw.arc((180,cy-330,900,cy+320),190,350,fill=(175,220,255),width=7)
    elif kind == "sunset":
        draw.rectangle((120,cy-220,960,cy+220),fill=(30,35,75),outline=(110,130,190),width=6)
        for j,c in enumerate([(255,115,70),(245,150,75),(255,205,115)]):
            r=170-j*38
            draw.ellipse((cx-r,cy-r-70,cx+r,cy+r-70),fill=c)
        draw.rectangle((120,cy+80,960,cy+220),fill=(25,35,65))
        for x in range(180,950,95):
            draw.line((x,cy+120,x+65,cy+120),fill=(235,130,90),width=6)

def make_card(scene, idx, total):
    im=gradient((7,15,39),(12,48,78))
    d=ImageDraw.Draw(im)
    # subtle stars and framing
    for k in range(45):
        x=(k*193+idx*71)%W
        y=(k*317+idx*43)%H
        d.ellipse((x,y,x+4,y+4),fill=(90,135,170))
    d.rounded_rectangle((54,70,W-54,H-70),radius=42,outline=(52,105,145),width=3)
    d.text((92,112),"RAAZVERSE HINDI",font=font(38,True),fill=(190,220,240))
    d.text((92,176),f"SCIENCE FILE  /  0{idx+1}",font=font(24),fill=(105,180,220))
    draw_visual(d,scene.get("visual","question"),idx)
    centered(d,scene["heading"],1120,font(66,True),(245,210,130))
    centered(d,scene["text"],1400,font(54),(245,248,255))
    d.rounded_rectangle((92,H-190,W-92,H-178),radius=6,fill=(65,145,190))
    d.text((92,H-145),f"{idx+1} / {total}",font=font(28),fill=(165,205,225))
    return im

def main():
    OUT.mkdir(exist_ok=True)
    SCENES_DIR.mkdir(exist_ok=True)
    if not DATA.get("scenes") or not DATA.get("narration"):
        raise SystemExit("content/video.json needs narration and scenes")
    narration = DATA["narration"]
    (OUT/"script.txt").write_text(narration,encoding="utf-8")
    voice = DATA.get("voice","hi-IN-MadhurNeural")
    subprocess.run([
        "edge-tts","--voice",voice,"--text",narration,
        "--write-media",str(OUT/"narration.mp3")
    ],check=True)
    total=len(DATA["scenes"])
    images=[]
    for i,scene in enumerate(DATA["scenes"]):
        path=SCENES_DIR/f"scene_{i+1:02d}.jpg"
        make_card(scene,i,total).save(path,quality=94)
        images.append(path)
    # Determine narration duration for scene pacing
    probe=subprocess.check_output([
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(OUT/"narration.mp3")
    ],text=True).strip()
    duration=float(probe)
    per_scene=max(2.5,duration/total)
    concat=OUT/"concat.txt"
    with concat.open("w",encoding="utf-8") as f:
        for p in images:
            f.write(f"file '{p.resolve()}'\n")
            f.write(f"duration {per_scene:.3f}\n")
        f.write(f"file '{images[-1].resolve()}'\n")
    # Timed captions, one scene caption per card
    srt=[]
    start=0.0
    for i,scene in enumerate(DATA["scenes"],1):
        end=min(duration,start+per_scene)
        def stamp(t):
            ms=int(round(t*1000)); h=ms//3600000; ms%=3600000
            m=ms//60000; ms%=60000; sec=ms//1000; milli=ms%1000
            return f"{h:02}:{m:02}:{sec:02},{milli:03}"
        srt.append(f"{i}\n{stamp(start)} --> {stamp(end)}\n{scene['text']}\n")
        start=end
    (OUT/"captions.srt").write_text("\n".join(srt),encoding="utf-8")
    # burn subtitles with Devanagari font and render 9:16
    srt_path=str((OUT/"captions.srt").resolve()).replace("\\\\","/").replace(":","\\\\:")
    vf=f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0007,1.06)':d=1:s=1080x1920:fps=30,subtitles='{srt_path}':force_style='FontName=Noto Sans Devanagari,FontSize=18,Outline=2,Shadow=1,Alignment=2,MarginV=180'"
    video=OUT/"raazverse_short.mp4"
    subprocess.run([
        "ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),
        "-i",str(OUT/"narration.mp3"),"-vf",vf,
        "-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","veryfast",
        "-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
        "-shortest","-movflags","+faststart",str(video)
    ],check=True)
    # Thumbnail from first card
    Image.open(images[0]).convert("RGB").save(OUT/"thumbnail.jpg",quality=95)
    print("SUCCESS: created",video)

if __name__=="__main__":
    main()
