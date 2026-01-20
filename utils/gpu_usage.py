#pip install nvidia-ml-py
#pip install psutil

# 帧数控制 要在RTSS里 Setup——>plugins 启用HotkeyHandler.dll
import pynvml
import psutil

def get_gpu_usage():
    # 初始化
    pynvml.nvmlInit()
    
    # 获取显卡句柄（0代表第一块显卡）
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    
    # 获取显卡名称（可选）
    #device_name = pynvml.nvmlDeviceGetName(handle)
    
    # 获取利用率
    # .gpu 是计算核心占用率，.memory 是显存带宽占用率
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    
    # 获取显存信息
    #mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
    #mem_used_percent = (mem.used / mem.total) * 100
    
    pynvml.nvmlShutdown() # 使用完记得关闭
    
    return util.gpu

def get_cpu_usage(interval=1.0):
    """
    获取CPU总使用率
    interval: 采样间隔（秒），建议0.5-1.0秒
    """
    # interval=1.0表示统计最近1秒的CPU使用率
    cpu_percent = psutil.cpu_percent(interval=0.1)
    #print("CPU使用率::",cpu_percent)
    print(f"         CPU使用率: {cpu_percent:.0f}%")

# 测试输出
#gpu_util, mem_util = get_gpu_usage()
#print(f"GPU 计算核心占用: {gpu_util}%")
#print(f"显存占用率: {mem_util:.2f}%")