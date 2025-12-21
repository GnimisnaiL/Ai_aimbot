from pynput import mouse
from utils.rzctl import RZCONTROL
import os
import time
import threading
#罗技控制
from utils.logitech_mouse import *


# 初始化罗技驱动（必须）
if not mouse_open():
    print("罗技鼠标驱动打开失败！请以管理员运行并确保G HUB已启动")
    exit()
print("罗技驱动加载成功")

# 初始化 Razer 鼠标控制
dll_path =  r"D:\0326aimbotyolo11n\aimbot\utils\rzctl.dll"  # 确保路径正确
if not os.path.exists(dll_path):
    print(f"错误：文件不存在 - {dll_path}")
else:
    print("DLL 文件存在，准备加载")
rzr = RZCONTROL(dll_path)

def precise_sleep(delay):
    """高精度睡眠（忙等待）"""
    start = time.perf_counter()
    while time.perf_counter() - start < delay:
        pass

a=0
# 28571.5 360度
# 32143 0.64 360度
#1845/32143*360
#   
def on_click(x, y, button, pressed):
    global a
    """
    鼠标点击回调函数
    """
    if button == mouse.Button.x1 and pressed:
        print(f"雷蛇")
        #mouse_move(0,12500,0,0)
        rzr.mouse_move(-100,0,True)


    if button == mouse.Button.middle and pressed:
        print(a)
        a+=1
        mouse_move(0,100,0,0)
    

# 启动鼠标监听
with mouse.Listener(on_click=on_click) as listener:
    print("监听鼠标左键点击中...按ESC键退出")
    listener.join()