import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from registry import registry


class APIGateway:
    def __init__(self):
        self.app = FastAPI(title="Agent 集群网关", version="1.0.0")
        self._setup_routes()
    
    def _setup_routes(self):
        
        @self.app.get("/")
        async def index():
            return {
                "service": "Agent 集群网关",
                "version": "1.0.0",
                "registered_services": registry.get_all_services()
            }
        
        @self.app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def proxy_request(service_name: str, path: str, request: Request):
            print(f"📥 收到请求: service_name={service_name}, path={path}")
            
            if service_name not in registry.get_all_services():
                print(f"❌ 服务不存在: {service_name}")
                return JSONResponse(
                    status_code=404,
                    content={"error": f"服务不存在: {service_name}"}
                )
            
            instance = registry.get_instance(service_name, "round_robin")
            print(f"📦 找到实例: {instance}")
            
            if not instance:
                print(f"❌ 服务不可用: {service_name}")
                return JSONResponse(
                    status_code=503,
                    content={"error": f"服务不可用: {service_name}"}
                )
            
            # 构建目标 URL
            base_url = f"http://{instance['host']}:{instance['port']}"
            target_url = f"{base_url}/{path}"
            
            query_string = str(request.url.query)
            if query_string:
                target_url += f"?{query_string}"
            
            print(f"🔄 转发: {request.method} {target_url}")
            
            body = await request.body()
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.request(
                        method=request.method,
                        url=target_url,
                        headers=headers,
                        content=body if body else None,
                    )
                    
                    print(f"✅ 转发成功: {response.status_code}")
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                except Exception as e:
                    print(f"❌ 转发失败: {e}")
                    return JSONResponse(
                        status_code=500,
                        content={"error": str(e)}
                    )
        
        @self.app.get("/health")
        async def health():
            return {"status": "ok", "services": registry.get_all_services()}
    
    def get_app(self):
        return self.app