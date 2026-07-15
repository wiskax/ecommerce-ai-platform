import json
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime


class ServiceRegistry:
    """
    服务注册中心（内存版）
    """
    
    def __init__(self):
        self._services: Dict[str, List[Dict]] = {}
        self._lock = threading.Lock()
        
    def register(self, service_name: str, instance_id: str, host: str, port: int, metadata: Dict = None):
        """注册服务实例"""
        with self._lock:
            if service_name not in self._services:
                self._services[service_name] = []
            
            # 移除已存在的相同实例
            self._services[service_name] = [
                s for s in self._services[service_name] 
                if s["instance_id"] != instance_id
            ]
            
            instance = {
                "instance_id": instance_id,
                "service_name": service_name,
                "host": host,
                "port": port,
                "metadata": metadata or {},
                "status": "healthy",
                "registered_at": datetime.now().isoformat(),
                "last_heartbeat": time.time()
            }
            self._services[service_name].append(instance)
            print(f"✅ 服务注册: {service_name}/{instance_id} @ {host}:{port}")
    
    def deregister(self, service_name: str, instance_id: str):
        """注销服务实例"""
        with self._lock:
            if service_name in self._services:
                self._services[service_name] = [
                    s for s in self._services[service_name] 
                    if s["instance_id"] != instance_id
                ]
                print(f"🗑️ 服务注销: {service_name}/{instance_id}")
    
    def heartbeat(self, service_name: str, instance_id: str):
        """心跳更新"""
        with self._lock:
            if service_name in self._services:
                for s in self._services[service_name]:
                    if s["instance_id"] == instance_id:
                        s["last_heartbeat"] = time.time()
                        s["status"] = "healthy"
                        return True
        return False
    
    def discover(self, service_name: str) -> List[Dict]:
        """发现服务实例"""
        with self._lock:
            if service_name not in self._services:
                return []
            
            now = time.time()
            healthy = []
            for s in self._services[service_name]:
                if now - s["last_heartbeat"] < 30:
                    s["status"] = "healthy"
                    healthy.append(s)
                else:
                    s["status"] = "unhealthy"
            
            return healthy
    
    def get_all_services(self) -> List[str]:
        """获取所有服务名称"""
        with self._lock:
            return list(self._services.keys())
    
    def get_instance(self, service_name: str, strategy: str = "round_robin") -> Optional[Dict]:
        """获取一个服务实例"""
        with self._lock:
            if service_name not in self._services:
                print(f"❌ 服务 {service_name} 未注册")
                return None
            
            instances = self._services[service_name]
            print(f"🔍 服务 {service_name} 的实例: {instances}")
            
            # 直接返回第一个实例
            if instances:
                return instances[0]
            return None


# 全局注册中心
registry = ServiceRegistry()