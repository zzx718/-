import time
import multiprocessing
import threading
import sys
import math
import os
import psutil

def cpu_stress():
    """让单核CPU满载的死循环运算，但降低优先级防卡死其他服务"""
    # 设为最低优先级 (Linux nice=19)。
    # 效果：监控显示 CPU 100%，但只要 Dify / 并发请求一进来，它就会立刻让出资源。
    if hasattr(os, 'nice'):
        try:
            os.nice(19)
        except:
            pass
    while True:
        math.factorial(1000)

def mem_leak():
    """持续吃内存，但触发告警线后保持稳定，防止把 Dify 搞错崩溃"""
    leak = []
    print("开始消耗内存...")
    try:
        while True:
            # 只要内存不到 92%，就继续吃（告警线是 90%）
            # 这样既能触发告警，又不会引发 Linux 底层的 OOM Killer 去杀掉 Dify 容器
            if psutil.virtual_memory().percent < 92:
                leak.append(' ' * 10 * 1024 * 1024)
            time.sleep(0.5)
    except MemoryError:
        print("内存已耗尽！")

if __name__ == "__main__":
    print("=======================================")
    print("⚠️ 警告: 正在进行极限多核压测实验")
    print("按 Ctrl+C 可以随时终止本程序，系统即刻恢复正常")
    print("=======================================")
    
    # 获取系统核心数，留0个直接全打满以保证告警触发
    import os
    cores = os.cpu_count() or 4
    
    print(f"检测到 {cores} 个 CPU 核心，启动 {cores} 个进程强制拉满...")
    
    # Python 多线程(threading)有 GIL 锁，无法吃满多核 CPU。改用多进程(multiprocessing)
    processes = []
    for _ in range(cores):
        p = multiprocessing.Process(target=cpu_stress, daemon=True)
        p.start()
        processes.append(p)
        
    print("启动 1 个 内存泄漏测试线程...")
    threading.Thread(target=mem_leak, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n压测结束，释放资源！")
        for p in processes:
            p.terminate()
        sys.exit(0)
