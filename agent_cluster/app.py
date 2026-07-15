import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from gateway import APIGateway
from registry import registry


# 创建网关
gateway = APIGateway()
app = gateway.get_app()


def register_services():
    """注册现有服务"""
    # 清空已有注册
    registry._services = {}
    registry.register("ai-customer-service", "ai-customer-service-1", "localhost", 8001)
    registry.register("operation-agent", "operation-agent-1", "localhost", 8002)
    registry.register("live-slicing", "live-slicing-1", "localhost", 8003)
    print("📋 已注册服务:", registry.get_all_services())


if __name__ == "__main__":
    register_services()
    uvicorn.run(app, host="0.0.0.0", port=8500)