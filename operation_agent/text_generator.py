import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from ai_customer_service.config import settings

llm = ChatOpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=settings.ZHIPU_API_KEY,
    model=settings.MODEL_NAME,
    temperature=0.7
)


def generate_product_copy(product_info: dict) -> dict:
    """
    生成商品文案
    product_info: {"name": "商品名", "category": "类目", "price": 价格, "features": "卖点"}
    """
    prompt = f"""你是一个电商文案专家。根据以下商品信息生成营销文案。

商品名称：{product_info.get('name', '未知商品')}
商品类目：{product_info.get('category', '未知')}
商品价格：{product_info.get('price', '未知')}
商品卖点：{product_info.get('features', '无')}

请生成以下内容：
1. 商品标题（15字以内，吸引眼球）
2. 商品描述（50字以内，突出卖点）
3. 三个核心卖点（每条10字以内）

输出格式：
标题：xxx
描述：xxx
卖点：xxx | xxx | xxx
"""

    response = llm.invoke(prompt)
    content = response.content.strip()

    # 解析
    result = {"title": "", "description": "", "bullet_points": []}
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("标题：") or line.startswith("标题:"):
            result["title"] = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
        elif line.startswith("描述：") or line.startswith("描述:"):
            result["description"] = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
        elif line.startswith("卖点："):
            parts = line.split("：")[-1].strip() if "：" in line else line.split(":")[-1].strip()
            result["bullet_points"] = [p.strip() for p in parts.split("|") if p.strip()]

    return result