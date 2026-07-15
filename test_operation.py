import requests

print("=" * 50)
print("🧪 测试网关连通性")
print("=" * 50)

# 1. 测试网关状态
print("\n1️⃣ 测试网关状态...")
try:
    r = requests.get("http://localhost:8500/", timeout=5)
    print(f"   ✅ 网关状态: {r.status_code}")
    print(f"   📋 已注册服务: {r.json().get('registered_services', [])}")
except Exception as e:
    print(f"   ❌ 网关连接失败: {e}")

# 2. 测试 AI 客服直接访问
print("\n2️⃣ 测试 AI 客服直接访问 (8001)...")
try:
    r = requests.get("http://localhost:8001/ask?query=你好", timeout=5)
    print(f"   ✅ AI 客服状态: {r.status_code}")
    print(f"   📝 回答: {r.json().get('answer', '')[:50]}...")
except Exception as e:
    print(f"   ❌ AI 客服连接失败: {e}")

# 3. 测试通过网关访问 AI 客服
print("\n3️⃣ 测试通过网关访问 AI 客服 (8500)...")
try:
    r = requests.get("http://localhost:8500/ai-customer-service/ask?query=你好", timeout=5)
    print(f"   ✅ 网关转发状态: {r.status_code}")
    if r.status_code == 200:
        print(f"   📝 回答: {r.json().get('answer', '')[:50]}...")
    else:
        print(f"   ❌ 错误: {r.text}")
except Exception as e:
    print(f"   ❌ 网关转发失败: {e}")

# 4. 测试运营 Agent 通过网关
print("\n4️⃣ 测试运营 Agent 通过网关 (8500)...")
try:
    r = requests.post(
        "http://localhost:8500/operation-agent/generate",
        json={"product_id": "p001", "name": "蓝牙耳机", "category": "数码", "price": "199", "features": "降噪+续航20小时"},
        timeout=10
    )
    print(f"   ✅ 网关转发状态: {r.status_code}")
    if r.status_code == 200:
        print(f"   📝 商品: {r.json().get('product_name', '')}")
    else:
        print(f"   ❌ 错误: {r.text}")
except Exception as e:
    print(f"   ❌ 网关转发失败: {e}")

print("\n" + "=" * 50)