import os
import sys
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma  # 使用独立包
from ai_customer_service.config import settings


class EcommerceKBBuilder:
    """电商知识库构建器"""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            base_url="https://open.bigmodel.cn/api/paas/v4",
            api_key=settings.ZHIPU_API_KEY,
            model=settings.EMBEDDING_MODEL
        )
        self.persist_dir = settings.KB_PERSIST_DIR
        self.collection_name = "ecommerce_kb"

    def build_from_faqs(self, faq_path: str):
        """从 FAQ CSV 构建知识库"""
        df = pd.read_csv(faq_path)
        print(f"📊 加载 {len(df)} 条 FAQ")

        documents = []
        for _, row in df.iterrows():
            question = row.get("question", "")
            answer = row.get("answer", "")
            if not question or not answer:
                continue

            content = f"问题：{question}\n回答：{answer}"
            doc = Document(
                page_content=content,
                metadata={
                    "question": question,
                    "answer": answer,
                    "intent": row.get("intent", "general")
                }
            )
            documents.append(doc)

        # 切分
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(documents)

        # 构建向量库（新版本自动持久化，不需要 persist()）
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_dir,
            collection_name=self.collection_name
        )
        # ❌ 删除这行：vectorstore.persist()
        # ✅ 新版本 Chroma 自动保存

        print(f"✅ 知识库构建完成: {len(chunks)} 个文档块")
        return vectorstore


if __name__ == "__main__":
    settings.ensure_dirs()
    builder = EcommerceKBBuilder()
    faq_path = os.path.join(settings.ANNOTATED_DATA_DIR, "faqs.csv")

    if os.path.exists(faq_path):
        builder.build_from_faqs(faq_path)
    else:
        print(f"⚠️ FAQ 文件不存在: {faq_path}")
        print("请先运行 annotator.py 生成标注数据")