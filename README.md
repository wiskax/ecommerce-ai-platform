# 🛒 电商 AI 智能化平台

> 一套覆盖电商全链路的 AI 解决方案，从数据清洗、RAG 客服、运营素材自动生成到直播切片，通过 Agent 集群统一调度。

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://github.com/langchain-ai/langchain)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ 核心特性

- 🧠 **RAG 知识库**：机器清洗 + 人工标注 + ChromaDB 向量存储，回答有依据、可溯源
- 🤖 **AI 智能客服**：基于 RAG 的智能问答，支持多模态检索（文本+图片+视频）
- 🎨 **运营 Agent**：自动生成商品文案、AI 图片、宣传视频，素材自动关联商品 ID
- ✂️ **直播切片**：Whisper AI 检测 + 人工审核 + FFmpeg 精准切割
- 📦 **AI 素材中心**：统一管理多模态素材，按商品 ID 关联，注入数据中台
- 🏗️ **Agent 集群**：服务注册、发现、负载均衡，支持水平扩展
- 🚀 **一键启动**：一条命令启动全部服务


## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **Web 框架** | FastAPI, Uvicorn |
| **AI 框架** | LangChain, LangGraph |
| **向量数据库** | ChromaDB |
| **LLM 接口** | 智谱AI (ChatGLM) |
| **语音识别** | Whisper (OpenAI) |
| **视频处理** | FFmpeg |
| **数据库** | PostgreSQL + SQLAlchemy |
| **认证** | JWT (python-jose) |
| **前端** | HTML + CSS + Vanilla JS |
| **容器化** | Docker + Docker Compose |


## 📊 系统架构
┌─────────────────────────────────────────────────────────────────┐
│ 用户交互层 │
│ Web 界面 / API 请求 / 网关入口 │
└─────────────────────────┬───────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ MCP + Agent 集群网关 (:8500) │
│ 服务注册 / 服务发现 / 负载均衡 │
└─────────────────────────┬───────────────────────────────────────┘
│
┌─────────────────┼─────────────────┐
│ │ │
▼ ▼ ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ AI 客服 │ │ 运营 Agent │ │ 直播切片 │
│ (:8001) │ │ (:8002) │ │ (:8003) │
│ RAG 问答 │ │ 文案/图片/ │ │ AI检测/切片 │
│ 多模态检索 │ │ 视频生成 │ │ 人工审核 │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
│ │ │
└─────────────────┼─────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ 数据层 │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ 数据中台 │ │ AI素材中心 │ │ ChromaDB │ │
│ │ 清洗/标注 │ │ 商品ID关联 │ │ 向量存储 │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘



## 🚀 快速开始

### 前置要求

- Python 3.11+
- FFmpeg（视频合成需要）
- 智谱AI API Key

### 1️、克隆项目

```bash
git clone https://github.com/wiskax/ecommerce-ai-platform.git
cd ecommerce-ai-platform
2️、创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
3️、安装依赖
pip install -r requirements.txt
4️、配置环境变量
cp .env.example .env
编辑 .env，填入你的 API Key：
env
ZHIPU_API_KEY=your_zhipu_api_key_here

5️⃣ 构建知识库（可选）
python data_platform/cleaner.py
python data_platform/annotator.py
python data_platform/kb_builder.py
6️⃣ 一键启动所有服务
python start_all.py
7️⃣ 访问系统
打开浏览器访问：http://localhost:8500

📡 服务入口
服务	端口	地址
集群网关	8500	http://localhost:8500
AI 客服	8001	http://localhost:8500/ai-customer-service/
运营 Agent	8002	http://localhost:8500/operation-agent/
直播切片	8003	http://localhost:8500/live-slicing/

🧪 API 测试
AI 客服问答
curl "http://localhost:8500/ai-customer-service/ask?query=这个商品多少钱？"
运营 Agent 生成素材
curl -X POST "http://localhost:8500/operation-agent/generate" \
  -H "Content-Type: application/json" \
  -d '{"product_id":"p001","name":"蓝牙耳机","category":"数码","price":"199","features":"降噪+续航20小时"}'
查看商品素材
curl "http://localhost:8500/operation-agent/materials/p001"
直播切片 - 检测商品片段
curl -X POST "http://localhost:8500/live-slicing/detect_products" \
  -H "Content-Type: application/json" \
  -d '{"file_path":"./live_videos/xxx.mp4"}'

📂 项目结构
ecommerce-ai-platform/
├── data_platform/           # 数据中台
│   ├── cleaner.py           # 机器清洗
│   ├── annotator.py         # 人工标注
│   └── kb_builder.py        # 知识库构建
├── ai_customer_service/     # AI 客服
│   ├── rag_service.py       # RAG 服务
│   └── app.py               # API 服务
├── operation_agent/         # 运营 Agent
│   ├── text_generator.py    # 文案生成
│   ├── image_generator.py   # 图片生成
│   ├── video_generator.py   # 视频合成
│   └── app.py
├── ai_material_center/      # AI 素材中心
│   ├── models.py            # 数据模型
│   └── app.py
├── live_slicing/            # 直播切片
│   ├── app.py               # API 服务
│   └── index.html           # 前端页面
├── agent_cluster/           # Agent 集群
│   ├── registry.py          # 服务注册
│   ├── gateway.py           # API 网关
│   ├── app.py               # 启动入口
│   └── start_all.py         # 一键启动
├── data/                    # 数据目录
├── uploads/                 # 上传文件
├── generated_images/        # 生成的图片
├── generated_videos/        # 生成的视频
├── chroma_db/               # 向量数据库
├── ecommerce_kb/            # 电商知识库
├── .env.example             # 环境变量模板
├── requirements.txt         # 依赖列表
└── README.md                # 项目文档

🎯 模块说明
模块	功能	状态
数据中台	机器清洗 + 人工标注 + 知识库构建	✅
AI 客服	RAG 问答 + 多模态检索	✅
运营 Agent	文案/图片/视频生成	✅
AI 素材中心	素材管理 + 商品关联	✅
直播切片	AI 检测 + 人工审核 + 精准切割	✅
Agent 集群	服务注册/发现/负载均衡	✅

🖼️ 演示效果
功能	说明
AI 客服	基于 RAG 的知识问答，回答附参考来源
运营 Agent	自动生成商品文案、AI 图片、宣传视频
直播切片	视频上传 → AI 检测 → 人工审核 → 精准切片
素材中心	统一管理多模态素材，按商品 ID 关联
📄 License
MIT License

🙏 致谢
FastAPI
LangChain
ChromaDB
智谱AI
如果这个项目对你有帮助，欢迎 Star ⭐！

联系邮箱：1054422081@qq.com