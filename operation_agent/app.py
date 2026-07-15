import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from operation_agent.text_generator import generate_product_copy
from operation_agent.image_generator import generate_product_image
from operation_agent.video_generator import create_product_video
from ai_material_center.models import material_center, Material
from datetime import datetime

app = FastAPI(title="运营 Agent", version="1.0.0")


class ProductRequest(BaseModel):
    product_id: str
    name: str
    category: str = "未分类"
    price: str = "价格待定"
    features: str = "暂无"


@app.post("/generate")
async def generate_product_materials(request: ProductRequest):
    """
    为商品生成完整素材（文案 + 图片 + 视频）
    """
    print(f"📦 开始生成商品素材: {request.name}")

    # 1. 生成文案
    copy = generate_product_copy(request.model_dump())
    print(f"   ✅ 文案生成完成")

    # 2. 生成主图
    image_prompt = f"{request.name}，{request.category}，{request.features}"
    image_path = generate_product_image(image_prompt)
    print(f"   ✅ 图片生成完成: {image_path}")

    # 3. 生成视频（用图片 + 文案 + 价格）
    video_path = None
    if image_path and copy:
        video_path = create_product_video(
            image_path=image_path,
            title=copy.get("title", request.name),
            description=copy.get("description", request.features),
            price=request.price
        )
        print(f"   ✅ 视频生成完成: {video_path}")

    # 4. 存入素材中心
    materials = []
    
    # 存入文案
    if copy:
        materials.append(Material(
            id=f"text_{request.product_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_id=request.product_id,
            material_type="text",
            content=copy.get("description", ""),
            source="operation_agent"
        ))

    # 存入图片
    if image_path:
        materials.append(Material(
            id=f"image_{request.product_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_id=request.product_id,
            material_type="image",
            content=image_path,
            source="operation_agent"
        ))

    # 存入视频
    if video_path:
        materials.append(Material(
            id=f"video_{request.product_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            product_id=request.product_id,
            material_type="video",
            content=video_path,
            source="operation_agent"
        ))

    # 所有素材存入素材中心
    for m in materials:
        material_center.add_material(m)

    # 更新商品信息
    pm = material_center._product_materials.get(request.product_id)
    if pm:
        pm.product_name = request.name
        pm.main_image = image_path
        pm.description = copy.get("description", "")
        pm.video_url = video_path

    print(f"✅ 素材已存入素材中心，共 {len(materials)} 条")

    return {
        "product_id": request.product_id,
        "product_name": request.name,
        "copy": copy,
        "image_path": image_path,
        "video_path": video_path,
        "materials_count": len(materials)
    }


@app.get("/materials/{product_id}")
async def get_product_materials(product_id: str):
    """获取商品的素材"""
    pm = material_center.get_product_materials(product_id)
    if not pm:
        raise HTTPException(status_code=404, detail="商品不存在")
    return pm.model_dump()


@app.get("/export/{product_id}")
async def export_to_data_platform(product_id: str):
    """导出到数据中台"""
    data = material_center.export_to_data_platform(product_id)
    if not data:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {
        "message": "导出成功，可用于 RAG 知识库",
        "data": data
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)