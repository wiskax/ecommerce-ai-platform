import os
import base64
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime


def generate_product_image(prompt: str, output_dir: str = "./generated_images") -> str:
    """
    生成商品主图（使用免费的 AI 图片生成 API）
    这里使用 Pollinations.ai 免费 API，无需 API Key
    """
    os.makedirs(output_dir, exist_ok=True)

    # 构建更具体的图片生成提示词
    image_prompt = f"电商商品主图，白色背景，专业摄影风格，商品展示：{prompt}，高清，4K"

    # 使用 Pollinations.ai 免费 API
    url = f"https://image.pollinations.ai/prompt/{image_prompt.replace(' ', '%20')}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # 保存图片
            filename = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
        else:
            print(f"⚠️ 图片生成失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ 图片生成异常: {e}")
        return None


def generate_image_with_stability(prompt: str, output_dir: str = "./generated_images") -> str:
    """
    备用方案：使用 Stability AI 等付费 API
    需要配置 STABILITY_API_KEY
    """
    # 留空，后续可根据需要实现
    pass