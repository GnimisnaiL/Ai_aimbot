from utils.utils import BaseEngine
import numpy as np
import cv2
import time
import os
import threading
import queue  
import argparse
import win32api
import win32con
import sys
import dxcam
from concurrent.futures import ThreadPoolExecutor


from pathlib import Path

#滚轮检测
from pynput import mouse
#旧画面捕捉
#from utils.grabscreen import grab_screen
#键盘码
from utils.keybinds import *
#画面预处理
from utils.utils import letterbox
from utils.utils import letterbox_gpu
#画面截图
from utils.capture import capture
#雷蛇控制
from utils.rzctl import RZCONTROL
#罗技控制
#from utils.logitech_mouse import *
#配置文件
from utils.config_watcher import cfg


class Predictor(BaseEngine):
    def __init__(self, engine_path):
        super(Predictor, self).__init__(engine_path)
        self.n_classes = 1  # your model classes

class DisplayThread(threading.Thread):
    def __init__(self, window_size=(320, 320)):
        super().__init__()
        self.image_queue = queue.Queue(maxsize=1)
        self.running = True
        self.daemon = True
        self.window_size = window_size  # 保存窗口尺寸
        self.window_created = False    # 标记窗口是否已创建
    def run(self):
        print("显示线程启动")
        window_name = 'view'
        
        while self.running:
            try:
                # 如果窗口还没创建，先创建窗口
                if not self.window_created:
                    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(window_name, self.window_size[0], self.window_size[1])
                    self.window_created = True
                    print(f"窗口已创建，尺寸: {self.window_size}")
                # 非阻塞获取图像
                img = self.image_queue.get_nowait()
                # 显示图像
                cv2.imshow(window_name, img)
                # 处理窗口事件（必须在显示线程内）
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("检测到Q键退出")
                    self.running = False
                    break
            except queue.Empty:
                # 没有新图像时，也要维持窗口响应
                if self.window_created:
                    cv2.waitKey(1)
                time.sleep(0.001)
            except Exception as e:
                print(f"显示线程错误: {e}")
                time.sleep(0.01)
        # 清理资源
        if self.window_created:
            cv2.destroyAllWindows()
        print("显示线程结束")
    def update_image(self, img):
        """更新显示图像（非阻塞）"""
        if not self.running:
            return
        if img is None:
            return 
        try:
            # 清空队列，只保留最新帧
            while not self.image_queue.empty():
                try:
                    self.image_queue.get_nowait()
                except queue.Empty:
                    break        
            self.image_queue.put_nowait(img)
        except Exception as e:
            print(f"更新图像错误: {e}")
    def stop(self):
        self.running = False

# =================================================
# 配置
# =================================================
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv11根目录
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # 相对路径
#显示器和截图窗口参数
screen_x, screen_y = cfg.screen_x, cfg.screen_y  # 显示器分辨率
window_x, window_y = cfg.window_x, cfg.window_y  # 截图窗口尺寸
#模型输入尺寸
model_x=cfg.detection_window_width 
model_y=cfg.detection_window_height


#@torch.no_grad()
def find_target(
        weights=ROOT / 'best.trt',  # 模型路径
        conf_thres=0.5,                    # 置信度阈值
        device='0',                        # 使用设备
):
    global mouse_wheel_up,mouse_wheel_down,speed_x,speed_y,auto_trigger

    # 初始化TRT模型
    pred = Predictor(engine_path=str(weights))

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

    

    # 创建线程池，全局只创建一次
    executor = ThreadPoolExecutor(max_workers=5)  # 最多同时运行 5 个任务
    #初始化FPS统计变量
    last_time = time.time()
    frame_count = 0
    prev_img=0
    data=None
    img0=None
    # 主循环
    while True:

        #屏幕截图
        #if img0 is None:
        #    img0=capture.get_new_frame()
        img0=capture.get_new_frame()


        if img0 is None:
            print("错误：输入图像为空！")
            continue

        if prev_img is not None and np.array_equal(img0, prev_img):
            continue  # 如果图像没有变化，跳过
        prev_img = img0.copy()  # 保存当前帧
        

        #fps统计
        frame_count += 1
        
        # 图像预处理 缩放后的图像（img）、缩放比例（ratio）1.0和填充的像素值（dwdh）0.0
        img, ratio, dwdh = letterbox_gpu(img0, new_shape=(model_x, model_y))
        # 执行推理
        #if data is None:
        data = pred.infer(img)

        #目标数量 检测框的坐标 置信度分数 类别索引
        num, final_boxes, final_scores, final_cls_inds  = data

                    
        #fps计数
        current_time = time.time()
        if current_time - last_time >= 1.0:
            fps = frame_count / (current_time - last_time)
            print(f"====================={fps:>3.0f} ")
            frame_count = 0
            last_time = current_time





if __name__ == '__main__':
    try:
        find_target()
    finally:
        #确保程序退出时释放鼠标资源
        #mouse_close()
        print('end')