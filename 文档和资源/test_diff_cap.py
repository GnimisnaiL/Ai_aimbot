from utils.utils import BaseEngine
import numpy as np
import time
import os
import queue  
import sys
import cv2
import threading
from pathlib import Path
#键盘码
from utils.keybinds import *
#画面预处理
from utils.utils import letterbox
#雷蛇控制
from utils.rzctl import RZCONTROL
#罗技控制
#from utils.logitech_mouse import *
#配置文件
import win32api
import win32con
import bettercam
import mss


# =================================================
# 配置
# =================================================
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
class Predictor(BaseEngine):
    def __init__(self, engine_path):
        super(Predictor, self).__init__(engine_path)
        self.n_classes = 1  # your model classes
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv11根目录
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # 相对路径
#显示器和截图窗口参数
screen_x, screen_y = 2560,1440  # 显示器分辨率
window_x, window_y = 426,426  # 截图窗口尺寸
#模型输入尺寸
model_x=320
model_y=320
#截图坐标
a=(screen_x-window_x)/2
b=(screen_y-window_y)/2-20
c=(screen_x-window_x)/2+window_x
d=(screen_y-window_y)/2+window_y-20




def find_target(
        weights=ROOT / 'best.trt',  # 模型路径
        capture_method=1 #0:bc 1:mss 
):
    
    

    if capture_method==0:
        #初始化bettercam
        bc = bettercam.create(output_color="BGR",region=(int(a),int(b),int(c),int(d)),max_buffer_len=1)
        bc.start(target_fps=80,video_mode=True)
    else:
        # MSS初始化 - 在循环外创建实例
        sct = mss.mss()
        left, top, width, height = (int(a),int(b),int(window_x),int(window_y))
        monitor = {"left": left, "top": top, "width": width, "height": height}


    # 初始化TRT模型
    pred = Predictor(engine_path=str(weights))

    #初始化FPS统计变量
    last_time = time.time()
    loop_count=0
    frame_count=0
    prev_img=0
    #可视化
    show_view=0
    f11_key=0
    display_thread = None
    data=None
    img0=None

    # 主循环
    while True:
        if f11_key==0 and show_view==0 and win32api.GetAsyncKeyState(win32con.VK_F11) & 0x8000 != 0:
            show_view=1
            f11_key=1
            # 创建显示线程c
            if display_thread is None:
                display_thread = DisplayThread(window_size=(model_x, model_y))
                display_thread.start()
                print("可视化开 - 显示线程已启动")
        if f11_key==0 and show_view==1 and win32api.GetAsyncKeyState(win32con.VK_F11) & 0x8000 != 0:
            show_view=0
            f11_key=1
            # 停止显示线程
            if display_thread is not None:
                display_thread.stop()
                display_thread = None
                print("可视化关 - 显示线程已停止")
        if f11_key==1 and win32api.GetAsyncKeyState(win32con.VK_F11)&0x8000==0:
            f11_key=0

        #屏幕截图
        #if img0 is None:
        #    img0=capture.get_new_frame()

        if img0 is None:
            if capture_method==0:
                img0=bc.get_latest_frame()
            else:
                # 使用已有的sct实例，避免重复创建
                screenshot = sct.grab(monitor)
                img0 = np.asarray(screenshot)[:,:,:3]

            #with mss.mss() as sct:
            #    screenshot = sct.grab(monitor)
            #    raw = screenshot.bgra
            #   img_array = np.frombuffer(raw, dtype=np.uint8).reshape((screenshot.height, screenshot.width, 4))
            #    img0=cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
             
         #img0=capture.get_new_frame()

        # 如果图像没有，跳过
        if img0 is None:
            print("错误：输入图像为空！")
            continue

        # 如果图像没有变化，跳过
        #if np.array_equal(img0, prev_img):
        #    loop_count += 1
        #    continue  
        #prev_img = img0.copy()  # 保存当前帧
        
        #可视化
        if show_view==1:
            resized_display = cv2.resize(img0, (int(model_x), int(model_y)))

        #fps统计
        loop_count += 1
        frame_count += 1
        
        # 图像预处理 缩放后的图像（img）、缩放比例（ratio）1.0和填充的像素值（dwdh）0.0
        img, ratio, dwdh = letterbox(img0, new_shape=(model_x, model_y))
        # 执行推理
        #if data is None:
        data = pred.infer(img)

        #目标数量 检测框的坐标 置信度分数 类别索引
        #num, final_boxes, final_scores, final_cls_inds  = data
                   
        #fps计数
        current_time = time.time()
        if current_time - last_time >= 1.0:
            fps = frame_count / (current_time - last_time)
            lps = loop_count / (current_time - last_time)
            print(f"fps:{fps:>3.0f}===========lps:{lps:>3.0f} ")
            frame_count = 0
            loop_count = 0
            last_time = current_time

        # 可视化
        if show_view==1:
            cv2.putText(resized_display, f'{fps:>3.0f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            # 非阻塞更新显示
            display_thread.update_image(resized_display.copy())



if __name__ == '__main__':
    try:
        find_target()
    finally:
        print('程序结束')