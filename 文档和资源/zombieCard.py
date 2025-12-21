import pytesseract
from PIL import Image


import numpy as np
import cv2
import time
import os
import threading
import argparse
import win32api
import win32con
import sys
from pathlib import Path

# 设置Tesseract路径（如果自动检测失败）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# 还需要安装 Tesseract-OCR 软件

#旧画面捕捉
from utils.grabscreen import grab_screen
#键盘码
from utils.keybinds import *
#画面预处理
from utils.utils import letterbox
#画面截图
from utils.capture import capture
#雷蛇控制
from utils.rzctl import RZCONTROL
#罗技控制
#from utils.logitech_mouse import *
#配置文件
from utils.config_watcher import cfg


# =================================================
# 文件路径配置
# =================================================
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv11根目录
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # 相对路径


#显示器和截图窗口参数
screen_x, screen_y = cfg.screen_x, cfg.screen_y  # 显示器分辨率
window_x, window_y = cfg.window_x, cfg.window_y  # 截图窗口尺寸
show_view=1


def has_golden_pixels_hsv(image):
    """
    使用HSV颜色空间检测金色像素
    """
    # 将BGR转换为HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 金色的HSV范围（需要根据实际颜色调整）
    # 金色通常在高饱和度、中高亮度的黄色-橙色范围
    lower_gold1 = np.array([15, 100, 100])   # 偏橙的金色
    upper_gold1 = np.array([25, 255, 255])
    
    lower_gold2 = np.array([20, 100, 100])   # 偏黄的金色
    upper_gold2 = np.array([35, 255, 255])
    
    # 创建掩码
    mask1 = cv2.inRange(hsv, lower_gold1, upper_gold1)
    mask2 = cv2.inRange(hsv, lower_gold2, upper_gold2)
    golden_mask = cv2.bitwise_or(mask1, mask2)
    
    # 计算金色像素数量
    golden_pixel_count = cv2.countNonZero(golden_mask)
    total_pixels = image.shape[0] * image.shape[1]
    golden_ratio = golden_pixel_count / total_pixels
    
    print(f"金色像素数量: {golden_pixel_count}/{total_pixels} ({golden_ratio:.2%})")
    
    return golden_pixel_count > 150  # 至少10个金色像素



def find_target():
    global mouse_wheel_up,mouse_wheel_down,speed_x,speed_y
    print("已安装的语言包:", pytesseract.get_languages())

    # 初始化 Razer 鼠标控制
    dll_path =  str(ROOT / "utils" / "rzctl.dll")  # 确保路径正确
    if not os.path.exists(dll_path):
        print(f"错误：文件不存在 - {dll_path}")
    else:
        print("DLL 文件存在，准备加载")
    rzr = RZCONTROL(dll_path)
    if not rzr.init():  # 检查是否初始化成功
        print("错误：无法初始化 Razer 鼠标控制！")
        return
    print("Razer 鼠标控制已初始化")

    
    # 创建显示窗口
    if show_view==1:
        cv2.namedWindow('imgView', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('imgView', 200, 20)

    # 定义自动扳机触发函数
    def trigger_key():
        rzr.keyboard_input(57, 0)
        time.sleep(0.01)  # 这个延迟会在后台线程执行，不会阻塞主循环
        rzr.keyboard_input(57, 1)


    #初始化FPS统计变量
    last_time = time.time()
    frame_count = 0
    pick_enable=1
    prev_img=0

    # 主循环
    while True:
        if win32api.GetAsyncKeyState(win32con.VK_F1)& 0x8000 !=0:
            pick_enable=1
            print("pick已开启")
        if win32api.GetAsyncKeyState(win32con.VK_DELETE)& 0x8000 !=0:
            pick_enable=0
            print("pick已关闭")
        if pick_enable==0:
            time.sleep(0.1)
            continue

       

        #屏幕截图
        #img0=capture.get_new_frame()
        
        img0=grab_screen([1160,910,1300,930])
        if img0 is None:
            print("错误：输入图像为空！")
            continue

        if show_view==1:
            resized_display = cv2.resize(img0, (int(100), int(20)))
        
        
        # 简单判断图像是否变化
        #if prev_img is not None and np.array_equal(img0, prev_img):
        #    continue  # 如果图像没有变化，跳过后续处理
        #prev_img = img0.copy()  # 保存当前帧

        if has_golden_pixels_hsv(img0):
            print("发现金色！")
            threading.Thread(target=trigger_key).start()
            pick_enable=0

        #fps统计
        frame_count += 1

        #截图遮蔽
        cv2.rectangle(img0, (0, 126), (25, 426), (255, 0, 0),  -1 )


      
        # 可视化
        if show_view==1:
            cv2.imshow('imgView', resized_display)
            # 退出检测（按Q键退出）
            if cv2.waitKey(1)&0xFF==ord('q'):
                break


        #fps计数
        current_time = time.time()
        if current_time - last_time >= 1.0:
            fps = frame_count / (current_time - last_time)
            print(f"{fps:.2f}")
            frame_count = 0
            last_time = current_time



if __name__ == '__main__':
    try:
        find_target()
    finally:
		#确保程序退出时释放鼠标资源
        #mouse_close()
        print('end')