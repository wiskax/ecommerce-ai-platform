import os
import sys
import subprocess
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_material_center.models import material_center, Material

app = FastAPI(title="直播切片", version="1.0.0")



UPLOAD_DIR = "./live_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)
SLICE_DIR = "./live_slices"
os.makedirs(SLICE_DIR, exist_ok=True)

FFMPEG_PATH = r"E:\ffmpeg\bin\ffmpeg.exe"

# ✅ 挂载视频目录，让前端可以访问视频文件
app.mount("/live_videos", StaticFiles(directory=UPLOAD_DIR), name="live_videos")
app.mount("/live_slices", StaticFiles(directory=SLICE_DIR), name="live_slices")
app.mount("/live_videos", StaticFiles(directory=UPLOAD_DIR), name="live_videos")

@app.get("/")
async def index():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {"message": "请先创建 index.html"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_id = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_id)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"file_id": file_id, "file_path": file_path}


@app.post("/detect_products")
async def detect_products(request: dict):
    """检测视频中的商品介绍片段"""
    file_path = request.get("file_path", "")
    print(f"🔍 检测视频: {file_path}")
    
    return {
        "segments": [
            {"product_id": "p001", "start": 6, "end": 30},
            {"product_id": "p002", "start": 32, "end": 55},
            {"product_id": "p003", "start": 58, "end": 80},
        ]
    }


@app.post("/slice")
async def create_slice(request: dict):
    """按商品切片"""
    file_path = request.get("file_path", "")
    product_id = request.get("product_id", "")
    start_time = request.get("start_time", 0)
    end_time = request.get("end_time", 0)

    print(f"📂 接收到的路径: {file_path}")

    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    print(f"📂 绝对路径: {file_path}")

    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return {"error": f"视频文件不存在: {file_path}"}

    slice_filename = f"slice_{product_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    slice_path = os.path.join(os.getcwd(), SLICE_DIR, slice_filename)
    os.makedirs(os.path.dirname(slice_path), exist_ok=True)

    cmd = [
        FFMPEG_PATH,
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", file_path,
        "-c", "copy",
        slice_path,
        "-y"
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ 切片生成: {slice_path}")

        material = Material(
            id=f"slice_{product_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_id=product_id,
            material_type="video",
            content=slice_path,
            source="live_slicing"
        )
        material_center.add_material(material)

        return {
            "product_id": product_id,
            "slice_path": slice_path,
            "start": start_time,
            "end": end_time,
            "status": "success"
        }
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg 错误: {e.stderr}")
        return {"error": f"切片失败: {e.stderr}"}


@app.get("/slices/{product_id}")
async def get_slices(product_id: str):
    pm = material_center.get_product_materials(product_id)
    if not pm:
        return {"product_id": product_id, "slices": []}
    slices_list = [m for m in pm.materials if m.source == "live_slicing" and m.material_type == "video"]
    return {"product_id": product_id, "slices": slices_list}


@app.get("/slices/all")
async def get_all_slices():
    """获取所有切片"""
    slices_list = []
    for pid, pm in material_center._product_materials.items():
        for m in pm.materials:
            if m.source == "live_slicing" and m.material_type == "video":
                slices_list.append({
                    "product_id": pid,
                    "slice_path": m.content,
                    "start": getattr(m, 'start_time', 0),
                    "end": getattr(m, 'end_time', 0),
                })
    return {"slices": slices_list}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)