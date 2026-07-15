import os
import subprocess
from datetime import datetime

# FFmpeg 完整路径
FFMPEG_PATH = r"E:\ffmpeg\bin\ffmpeg.exe"


def create_product_video(
    image_path: str,
    title: str,
    description: str,
    price: str = "",
    output_dir: str = "./generated_videos"
) -> str:
    """
    生成真实感的商品宣传视频
    包含：慢缩放 + 柔光 + 渐变字幕 + 背景音乐
    """
    os.makedirs(output_dir, exist_ok=True)

    filename = f"product_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    filepath = os.path.join(output_dir, filename)

    print(f"🎬 生成商品视频: {filepath}")

    if not os.path.exists(image_path):
        print(f"⚠️ 图片不存在: {image_path}")
        return None

    # ---- 1. 创建 ASS 字幕（含动画效果） ----
    subtitle_file = os.path.join(output_dir, "temp_subtitle.ass")
    subtitle_file_ffmpeg = subtitle_file.replace("\\", "/")

    with open(subtitle_file, "w", encoding="utf-8") as f:
        f.write(f"""
[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Microsoft YaHei,52,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,7,10,10,30,1
Style: Desc,Microsoft YaHei,32,&H00E0E0E0,&H0000FFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,7,10,10,70,1
Style: Price,Microsoft YaHei,44,&H00FFD700,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,7,10,10,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.30,0:00:04.80,Title,,0,0,0,,{{\\fad(300,300)}}{title}
Dialogue: 0,0:00:00.80,0:00:04.80,Desc,,0,0,0,,{{\\fad(300,300)}}{description}
Dialogue: 0,0:00:01.50,0:00:04.50,Price,,0,0,0,,{{\\fad(300,300)}}💰 {price}
""")

    # ---- 2. 下载或使用内置背景音乐 ----
    music_path = get_background_music(output_dir)

    # ---- 3. FFmpeg 命令 ----
    # 镜头效果：缓慢缩放 + 柔光 + 字幕 + 背景音乐
    cmd = [
        FFMPEG_PATH,
        "-loop", "1",
        "-i", image_path,
        "-i", music_path,
        "-filter_complex",
        f"""
        [0:v]scale=1280:720:force_original_aspect_ratio=decrease,
        pad=1280:720:(ow-iw)/2:(oh-ih)/2,
        format=yuv420p,
        zoompan=z='min(zoom+0.0012,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=1280x720,
        boxblur=5:enable='between(t,0,1)',
        ass={subtitle_file_ffmpeg}[v]
        """,
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-t", "5",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        filepath,
        "-y"
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ 视频生成成功")
        if os.path.exists(subtitle_file):
            os.remove(subtitle_file)
        return filepath
    except subprocess.CalledProcessError as e:
        print(f"❌ 视频生成失败: {e.stderr}")
        if os.path.exists(subtitle_file):
            os.remove(subtitle_file)
        return None


def get_background_music(output_dir: str) -> str:
    """获取背景音乐（本地或下载）"""
    music_path = os.path.join(output_dir, "background_music.mp3")

    # 如果已经存在，直接返回
    if os.path.exists(music_path):
        return music_path

    # 下载免费背景音乐（使用 FFmpeg 生成简单的环境音）
    # 这里生成一段 5 秒的纯音乐（钢琴音效）
    cmd = [
        FFMPEG_PATH,
        "-f", "lavfi",
        "-i", "sine=frequency=440:duration=5:sample_rate=44100",
        "-c:a", "libmp3lame",
        music_path,
        "-y"
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"🎵 背景音乐已生成: {music_path}")
        return music_path
    except:
        # 如果生成失败，返回空路径（FFmpeg 会忽略）
        return r"anullsrc"