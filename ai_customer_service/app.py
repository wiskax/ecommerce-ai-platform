import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from ai_customer_service.rag_service import EcommerceRAGService

app = FastAPI(title="电商 AI 客服", version="1.0.0")
rag = EcommerceRAGService()


@app.get("/")
async def index():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>电商 AI 客服</title></head>
    <body style="font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px;">
        <h1>🛒 电商 AI 客服</h1>
        <form onsubmit="ask(event)">
            <input id="q" type="text" placeholder="输入问题..." style="width:70%; padding:10px;">
            <button type="submit" style="padding:10px 20px;">提问</button>
        </form>
        <div id="result" style="margin-top:20px;"></div>
        <script>
            async function ask(e) {
                e.preventDefault();
                const q = document.getElementById('q').value;
                const res = await fetch(`/ask?query=${encodeURIComponent(q)}`);
                const data = await res.json();
                document.getElementById('result').innerHTML =
                    `<h3>回答：</h3><p>${data.answer}</p>`;
            }
        </script>
    </body>
    </html>
    """)


@app.get("/ask")
async def ask(query: str = Query(..., description="用户问题")):
    result = rag.ask(query)
    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)