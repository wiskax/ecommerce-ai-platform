import json
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class Material(BaseModel):
    """素材模型"""
    id: str
    product_id: str
    material_type: str  # image / text / video
    content: str        # 文本内容 或 文件路径/URL
    source: str         # operation_agent / live_slicing
    status: str = "active"  # active / inactive
    created_at: datetime = datetime.now()


class ProductMaterials(BaseModel):
    """商品关联素材"""
    product_id: str
    product_name: str
    main_image: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    tags: List[str] = []
    materials: List[Material] = []


class MaterialCenter:
    """素材中心（内存版，后续可替换为数据库）"""

    def __init__(self):
        self._materials: List[Material] = []
        self._product_materials: dict[str, ProductMaterials] = {}

    def add_material(self, material: Material):
        """添加素材"""
        self._materials.append(material)

        # 关联到商品
        if material.product_id not in self._product_materials:
            self._product_materials[material.product_id] = ProductMaterials(
                product_id=material.product_id,
                product_name="",
                materials=[]
            )
        self._product_materials[material.product_id].materials.append(material)

    def get_product_materials(self, product_id: str) -> ProductMaterials:
        """获取商品的所有素材"""
        return self._product_materials.get(product_id)

    def get_all_products(self) -> List[str]:
        """获取所有商品ID"""
        return list(self._product_materials.keys())

    def export_to_data_platform(self, product_id: str) -> dict:
        """导出到数据中台（供 RAG 使用）"""
        pm = self._product_materials.get(product_id)
        if not pm:
            return {}
        return {
            "product_id": product_id,
            "product_name": pm.product_name,
            "main_image": pm.main_image,
            "description": pm.description,
            "video_url": pm.video_url,
            "materials": [
                {"type": m.material_type, "content": m.content}
                for m in pm.materials
            ]
        }


# 全局单例
material_center = MaterialCenter()