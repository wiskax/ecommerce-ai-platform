# 电商 AI 智能化平台

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://github.com/langchain-ai/langchain)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 一套覆盖电商全链路的 AI 智能化平台，涵盖 RAG 客服、运营素材生成、直播切片等核心模块，通过 Agent 集群统一调度。

---

## ✨ 核心特性

- 🧠 **RAG 知识库**：机器清洗 + 人工标注 + ChromaDB 向量存储，回答有依据、可溯源
- 💬 **AI 智能客服**：基于检索增强生成的智能问答，支持多用户隔离
- 🎨 **运营 Agent**：自动生成商品文案、主图、宣传视频，素材自动关联商品 ID
- ✂️ **直播切片**：Whisper AI 检测 + 人工审核 + FFmpeg 精准切割
- 📦 **AI 素材中心**：统一管理多模态素材，支持商品 ID 关联
- 🏗️ **Agent 集群**：服务注册、发现、负载均衡，统一网关入口
- 🚀 **一键启动**：所有服务一键启动，快速验证

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI, Uvicorn |
| AI 框架 | LangChain, LangGraph |
| 向量数据库 | ChromaDB |
| LLM 接口 | 智谱AI (ChatGLM) |
| 语音识别 | Whisper (OpenAI) |
| 视频处理 | FFmpeg |
| 认证 | JWT |
| 前端 | HTML + CSS + JavaScript |
| 部署 | Docker, Docker Compose |

---

## 📊 系统架构
用户 → 集群网关 (:8500)
├── AI 客服 (:8001) → RAG 问答
├── 运营 Agent (:8002) → 文案/图片/视频
└── 直播切片 (:8003) → 视频切片
↓
┌─────────────────────┐
│ AI 素材中心 │
│ 数据中台 / ChromaDB │
└─────────────────────┘


---

## 🚀 快速开始

### 前置要求

- Python 3.11+
- FFmpeg（视频生成用）
- 智谱AI API Key

### 安装依赖

```bash
# 1. 克隆仓库
git clone https://github.com/wiskax/ecommerce-ai-platform.git
cd ecommerce-ai-platform

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 ZHIPU_API_KEY
一键启动所有服务

python start_all.py
访问入口
服务	地址
网关首页	http://localhost:8500
AI 客服	http://localhost:8500/ai-customer-service/
直播切片	http://localhost:8500/live-slicing/
健康检查	http://localhost:8500/health
测试问答

curl "http://localhost:8500/ai-customer-service/ask?query=这个商品多少钱？"
📂 项目结构

ecommerce-ai-platform/
├── data_platform/           # 数据中台（清洗/标注/知识库）
├── ai_customer_service/     # AI 客服（RAG 问答）
├── operation_agent/         # 运营 Agent（文案/图片/视频生成）
├── ai_material_center/      # AI 素材中心
├── live_slicing/            # 直播切片
├── agent_cluster/           # Agent 集群网关
├── start_all.py             # 一键启动脚本
├── requirements.txt         # 依赖列表
└── README.md               # 项目文档

📡 API 接口
服务	接口	说明
AI 客服	GET /ask?query=xxx	RAG 智能问答
运营 Agent	POST /generate	生成商品素材
运营 Agent	GET /materials/{id}	查询商品素材
直播切片	POST /upload	上传视频
直播切片	POST /detect_products	AI 检测商品片段
直播切片	POST /slice	切片生成

🎯 项目亮点
全链路覆盖：从数据采集到 AI 客服、素材生成、直播切片，电商 AI 完整闭环
RAG 知识库：机器清洗 + 人工标注 + 向量检索，回答有依据
多 Agent 协作：运营 Agent 自动生成文案/图片/视频
AI 直播切片：Whisper + 人工审核，精准按商品维度切片

集群架构：服务注册/发现/负载均衡，支持水平扩展

📄 License
MIT License

🙏 致谢
FastAPI
LangChain
ChromaDB
智谱AI
如果这个项目对你有帮助，欢迎 Star ⭐！
联系邮箱：1054422081@qq.com