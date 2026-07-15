import uuid
import time
import threading
import requests
from typing import Dict, Optional


class AgentWrapper:
    """
    Agent 包装器：自动注册到集群，发送心跳
    """
    
    def __init__(self, service_name: str, host: str, port: int, 
                 registry_url: str = "http://localhost:8500"):
        self.service_name = service_name
        self.instance_id = f"{service_name}-{uuid.uuid4().hex[:8]}"
        self.host = host
        self.port = port
        self.registry_url = registry_url
        self._running = False
        self._heartbeat_thread = None
    
    def register(self, metadata: Dict = None):
        """注册到集群"""
        try:
            response = requests.post(
                f"{self.registry_url}/register",
                json={
                    "service_name": self.service_name,
                    "instance_id": self.instance_id,
                    "host": self.host,
                    "port": self.port,
                    "metadata": metadata or {}
                },
                timeout=5.0
            )
            if response.status_code == 200:
                print(f"✅ 注册成功: {self.service_name} ({self.instance_id})")
                return True
            else:
                print(f"❌ 注册失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 注册异常: {e}")
            return False
    
    def deregister(self):
        """从集群注销"""
        try:
            response = requests.post(
                f"{self.registry_url}/deregister",
                json={
                    "service_name": self.service_name,
                    "instance_id": self.instance_id
                },
                timeout=5.0
            )
            print(f"🗑️ 注销成功: {self.service_name} ({self.instance_id})")
            return True
        except Exception as e:
            print(f"❌ 注销异常: {e}")
            return False
    
    def _heartbeat_loop(self):
        """心跳循环"""
        while self._running:
            try:
                response = requests.post(
                    f"{self.registry_url}/heartbeat",
                    json={
                        "service_name": self.service_name,
                        "instance_id": self.instance_id
                    },
                    timeout=5.0
                )
            except Exception:
                pass
            time.sleep(10)  # 每10秒发送一次心跳
    
    def start(self, metadata: Dict = None):
        """启动 Agent（注册 + 心跳）"""
        if self._running:
            return
        
        self.register(metadata)
        self._running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        print(f"🚀 Agent 已启动: {self.service_name}")
    
    def stop(self):
        """停止 Agent"""
        self._running = False
        self.deregister()
        print(f"🛑 Agent 已停止: {self.service_name}")
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()