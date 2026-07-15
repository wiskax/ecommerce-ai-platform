import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from ai_customer_service.config import settings


class EcommerceRAGService:
    """电商 AI 客服（完全独立）"""

    def __init__(self):
        self.kb_dir = settings.KB_PERSIST_DIR
        self.vectorstore = None

        self.embeddings = OpenAIEmbeddings(
            base_url="https://open.bigmodel.cn/api/paas/v4",
            api_key=settings.ZHIPU_API_KEY,
            model=settings.EMBEDDING_MODEL
        )

        self.llm = ChatOpenAI(
            base_url="https://open.bigmodel.cn/api/paas/v4",
            api_key=settings.ZHIPU_API_KEY,
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE
        )

        if os.path.exists(self.kb_dir):
            self.vectorstore = Chroma(
                collection_name="ecommerce_kb",
                embedding_function=self.embeddings,
                persist_directory=self.kb_dir
            )
            print(f"✅ 加载知识库: {self.kb_dir}")
        else:
            print("⚠️ 知识库不存在，请先运行 kb_builder.py")

    def ask(self, query: str, top_k: int = None):
        if top_k is None:
            top_k = settings.TOP_K

        if not self.vectorstore:
            return {"answer": "知识库未就绪，请先构建", "sources": []}

        docs = self.vectorstore.similarity_search_with_score(query, k=top_k)

        if not docs:
            return {"answer": "抱歉，我暂时没有找到相关信息。", "sources": []}

        context = "\n\n".join([doc.page_content for doc, _ in docs])
        sources = [{"content": doc.page_content, "score": float(score)} for doc, score in docs]

        prompt = f"""你是一个电商客服助手。请根据以下知识库内容回答用户问题。

知识库内容：
{context}

用户问题：{query}

请给出准确、友好的回答："""

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "sources": sources
        }


if __name__ == "__main__":
    service = EcommerceRAGService()
    if service.vectorstore:
        result = service.ask("这个商品多少钱？")
        print(f"回答: {result['answer']}")