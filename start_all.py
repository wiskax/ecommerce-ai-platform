import subprocess
import sys
import os
import time
import threading
import signal


def run_service(name, command):
    """在子进程中运行服务"""
    print(f"🚀 启动 {name}...")
    return subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )


def print_output(process, name):
    """打印服务输出"""
    for line in process.stdout:
        print(f"[{name}] {line}", end="")


def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    print("\n🛑 正在停止所有服务...")
    for name, proc in processes:
        proc.terminate()
        print(f"  停止 {name}")
    print("✅ 所有服务已停止")
    sys.exit(0)


if __name__ == "__main__":
    # 切换到项目目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("🚀 启动电商 AI 平台所有服务")
    print("=" * 60)
    
    # 服务列表: (名称, 命令)
    services = [
        ("AI 客服", "python ai_customer_service/app.py"),
        ("运营 Agent", "python operation_agent/app.py"),
        ("直播切片", "python live_slicing/app.py"),
        ("集群网关", "python agent_cluster/app.py"),
    ]
    
    processes = []
    
    # 注册 Ctrl+C 信号处理
    signal.signal(signal.SIGINT, signal_handler)
    
    # 启动所有服务
    for name, cmd in services:
        try:
            proc = run_service(name, cmd)
            processes.append((name, proc))
            time.sleep(1.5)  # 等待服务启动
        except Exception as e:
            print(f"❌ 启动 {name} 失败: {e}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ 所有服务已启动！")
    print("📋 访问入口:")
    print("   🌐 网关: http://localhost:8500")
    print("   💬 AI 客服: http://localhost:8500/ai-customer-service/ask?query=你好")
    print("   🎨 运营 Agent: http://localhost:8500/operation-agent/")
    print("   ✂️ 直播切片: http://localhost:8500/live-slicing/")
    print("=" * 60)
    print("按 Ctrl+C 停止所有服务...\n")
    
    try:
        # 启动所有线程打印日志
        threads = []
        for name, proc in processes:
            t = threading.Thread(target=print_output, args=(proc, name), daemon=True)
            t.start()
            threads.append(t)
        
        # 等待所有进程结束
        for name, proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)