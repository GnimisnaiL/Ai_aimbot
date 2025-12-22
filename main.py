import os
import sys
import cv2
import time
import queue
import win32api
import win32con
import threading
import numpy as np
from pathlib import Path
from utils.utils import BaseEngine
from concurrent.futures import ThreadPoolExecutor
#配置文件
from utils.config_watcher import cfg
#滚轮检测
from pynput import mouse
#旧画面捕捉
#from utils.grabscreen import grab_screen
#键盘码
from utils.keybinds import *
#画面预处理
from utils.utils import letterbox
#画面截图
from utils.capture import capture
#雷蛇控制
from utils.rzctl import RZCONTROL
#罗技控制
from utils.logitech_mouse import *
#鼠标平滑器
from utils.smooth_mouse import SmoothMouse

#获取根目录
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv11根目录
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # 相对路径

#定义全局变量
mouse_wheel_up = False #用于存储滚轮状态 弃用
mouse_wheel_down = False
aim_range=0 #林蝶
mouse_driver=cfg.mouse_driver #鼠标选择 #0为罗技 1为雷蛇

#初始化推理模型    
class Predictor(BaseEngine): 
    def __init__(self, engine_path):
        super(Predictor, self).__init__(engine_path)
        self.n_classes = 1  # your model classes

#可视化线程
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

#主函数
def find_target():
    global mouse_wheel_up,mouse_wheel_down,aim_range

    # 初始化TRT模型
    enemy_pred = Predictor(engine_path=str(ROOT / 'enemy320.trt'))
    ally_pred = Predictor(engine_path=str(ROOT / 'ally.trt'))
    debug=cfg.debug #debug模式
    executor = ThreadPoolExecutor(max_workers=100)  #创建线程池，全局只创建一次 最多同时运行任务
    screen_x,screen_y=cfg.screen_x,cfg.screen_y #显示器分辨率
    window_x,window_y=cfg.window_x,cfg.window_y #截图窗口尺寸
    model_x,model_y=cfg.model_x,cfg.model_y #模型输入尺寸
    aim_fix,aim_fix_time=1,0 #移动补偿
    #上一帧切片
    prev_check=None 
    #可视化
    show_view=0
    display_thread = None
    #时间数据寄存
    last_combot_time=0 #夜魔侠连招
    last_key_time=0 #按键检测分频
    last_afk_time=0 #挂机时间
    last_capture_time=0 #fps控制
    last_frame_time=0 #fps统计
    #fps数据统计
    frame_count=0
    loop_count=0
    #专用FPS控制
    fps_control=cfg.fps_control
    frame_interval=1.0/cfg.capture_fps  # 每帧时间
    # 启动鼠标滚轮监听线程
    #mouse_listener = mouse.Listener(on_scroll=on_scroll)
    #mouse_listener.start()
    #scroll_history=0
    #初始参数
    aim_mode=2 #模式
    fire_mode=2 #按键
    aimbot_enable=1 #开关
    auto_trigger=0 #扳机
    x_portion,y_portion=cfg.x_portion,cfg.y_portion #位置
    speed_x,speed_y=cfg.speed_x,cfg.speed_y #速度
    aim_range=4.5 #瞄准范围
    smooth_enable=1 #平滑
    #特殊按键锁存
    x2_key=0
    f11_key=0
    f12_key=0
    ins_key=0
    afk=0
    mb_key=0
    ctrl_key=0
    spiderman_key=0
    #英伟达截图
    get_train_pic=0
    last_get_picture_time=0
    #初始化平滑器
    smoothX=SmoothMouse()
    smoothY=SmoothMouse()

    #初始化 Razer 鼠标
    dll_path =  str(ROOT / "utils" / "rzctl.dll")  # 确保路径正确
    if not os.path.exists(dll_path):
        print(f"错误：文件不存在 - {dll_path}")
    rzr = RZCONTROL(dll_path)
    if not rzr.init():  # 检查是否初始化成功
        print("错误：无法初始化 Razer 鼠标控制！")
    if mouse_driver!=1:
        mouse_open() #打开罗技鼠标设备
        print("罗技鼠标控制已初始化")

    # 鼠标移动控制器
    def mouse_driver_move(x,y):
        if mouse_driver==1:
            rzr.mouse_move(x,y,True)
        else:
            if abs(x)>127:
                print("鼠标行程超标")
                x=127
            if abs(y)>127:
                print("鼠标行程超标")
                y=127
            mouse_move(0, x, y, 0)

    # 批量获取按键状态
    def get_key_less():
        keys = {
            'f1': 0,
            'f2': 0,
            'f3': 0,
            'f5': 0,
            'f6': 0,
            'f7':  0,
            'f10': 0,
            'f11': 0,
            'f12': 0,
            'up': 0,
            'down': 0,
            'left': 0,
            'right': 0,
            'prior': 0,
            'next': 0,
            'delete': win32api.GetAsyncKeyState(win32con.VK_DELETE) & 0x8000 !=0,
            'lb': win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000 != 0,
            'rb': win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000 != 0,
            'mb': win32api.GetAsyncKeyState(win32con.VK_MBUTTON) & 0x8000 != 0,
            'x1': win32api.GetAsyncKeyState(win32con.VK_XBUTTON1) & 0x8000 != 0,
            'x2': win32api.GetAsyncKeyState(win32con.VK_XBUTTON2) & 0x8000 != 0,
            'shift': win32api.GetAsyncKeyState(win32con.VK_SHIFT) & 0x8000 != 0,
            'ctrl' : win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000 != 0,
            'a': win32api.GetAsyncKeyState(0x41) & 0x8000 != 0,
            'd': win32api.GetAsyncKeyState(0x44) & 0x8000 != 0,
            'f': win32api.GetAsyncKeyState(0x46) & 0x8000 != 0,
            'insert': win32api.GetAsyncKeyState(win32con.VK_INSERT) & 0x8000 != 0
        }
        return keys
    def get_key_more():
        keys = {
            'f1': win32api.GetAsyncKeyState(win32con.VK_F1) & 0x8000 != 0,
            'f2': win32api.GetAsyncKeyState(win32con.VK_F2) & 0x8000 != 0,
            'f3': win32api.GetAsyncKeyState(win32con.VK_F3) & 0x8000 != 0,
            'f5': win32api.GetAsyncKeyState(win32con.VK_F5) & 0x8000 != 0,
            'f6': win32api.GetAsyncKeyState(win32con.VK_F6) & 0x8000 != 0,
            'f7': win32api.GetAsyncKeyState(win32con.VK_F7) & 0x8000 != 0,
            'f10': win32api.GetAsyncKeyState(win32con.VK_F10) & 0x8000 != 0,
            'f11': win32api.GetAsyncKeyState(win32con.VK_F11) & 0x8000 != 0,
            'f12': win32api.GetAsyncKeyState(win32con.VK_F12) & 0x8000 != 0,
            'up': 0,
            'down': 0,
            'left': 0,
            'right': 0,
            'prior': 0,
            'next': 0,
            'delete': win32api.GetAsyncKeyState(win32con.VK_DELETE) & 0x8000 !=0,
            'lb': win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000 != 0,
            'rb': win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000 != 0,
            'mb': win32api.GetAsyncKeyState(win32con.VK_MBUTTON) & 0x8000 != 0,
            'x1': win32api.GetAsyncKeyState(win32con.VK_XBUTTON1) & 0x8000 != 0,
            'x2': win32api.GetAsyncKeyState(win32con.VK_XBUTTON2) & 0x8000 != 0,
            'shift': win32api.GetAsyncKeyState(win32con.VK_SHIFT) & 0x8000 != 0,
            'ctrl' : win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000 != 0,
            'a': win32api.GetAsyncKeyState(0x41) & 0x8000 != 0,
            'd': win32api.GetAsyncKeyState(0x44) & 0x8000 != 0,
            'f': win32api.GetAsyncKeyState(0x46) & 0x8000 != 0,
            'insert': win32api.GetAsyncKeyState(win32con.VK_INSERT) & 0x8000 != 0
        }
        return keys
    def get_key_all():
        keys = {
            'f1': win32api.GetAsyncKeyState(win32con.VK_F1) & 0x8000 != 0,
            'f2': win32api.GetAsyncKeyState(win32con.VK_F2) & 0x8000 != 0,
            'f3': win32api.GetAsyncKeyState(win32con.VK_F3) & 0x8000 != 0,
            'f5': win32api.GetAsyncKeyState(win32con.VK_F5) & 0x8000 != 0,
            'f6': win32api.GetAsyncKeyState(win32con.VK_F6) & 0x8000 != 0,
            'f7': win32api.GetAsyncKeyState(win32con.VK_F7) & 0x8000 != 0,
            'f10': win32api.GetAsyncKeyState(win32con.VK_F10) & 0x8000 != 0,
            'f11': win32api.GetAsyncKeyState(win32con.VK_F11) & 0x8000 != 0,
            'f12': win32api.GetAsyncKeyState(win32con.VK_F12) & 0x8000 != 0,
            'up': win32api.GetAsyncKeyState(win32con.VK_UP) & 0x8000 !=0,
            'down': win32api.GetAsyncKeyState(win32con.VK_DOWN) & 0x8000 !=0,
            'left': win32api.GetAsyncKeyState(win32con.VK_LEFT) & 0x8000 !=0,
            'right': win32api.GetAsyncKeyState(win32con.VK_RIGHT) & 0x8000 !=0,
            'prior': win32api.GetAsyncKeyState(win32con.VK_PRIOR) & 0x8000 !=0,
            'next': win32api.GetAsyncKeyState(win32con.VK_NEXT) & 0x8000 !=0,
            'delete': win32api.GetAsyncKeyState(win32con.VK_DELETE) & 0x8000 !=0,
            'lb': win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000 != 0,
            'rb': win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000 != 0,
            'mb': win32api.GetAsyncKeyState(win32con.VK_MBUTTON) & 0x8000 != 0,
            'x1': win32api.GetAsyncKeyState(win32con.VK_XBUTTON1) & 0x8000 != 0,
            'x2': win32api.GetAsyncKeyState(win32con.VK_XBUTTON2) & 0x8000 != 0,
            'shift': win32api.GetAsyncKeyState(win32con.VK_SHIFT) & 0x8000 != 0,
            'ctrl' : win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000 != 0,
            'a': win32api.GetAsyncKeyState(0x41) & 0x8000 != 0,
            'd': win32api.GetAsyncKeyState(0x44) & 0x8000 != 0,
            'f': win32api.GetAsyncKeyState(0x46) & 0x8000 != 0,
            'insert': win32api.GetAsyncKeyState(win32con.VK_INSERT) & 0x8000 != 0
        }
        return keys

    # 鼠标滚轮监听回调函数 弃用
    def on_scroll(x, y, dx, dy):
        global mouse_wheel_up, mouse_wheel_down
        if dy > 0:  # 滚轮向上滚动
            mouse_wheel_up = True
            mouse_wheel_down = False
        elif dy < 0:  # 滚轮向下滚动
            mouse_wheel_up = False
            mouse_wheel_down = True

    # 灵蝶冲刺
    def psylocke_dash():
        global aim_range
        time.sleep(0.5)
        aim_range=4.5

    # 自动扳机触发函数 按键J
    def trigger_key():
        rzr.keyboard_input(36, 0)
        time.sleep(0.001)  # 这个延迟会在后台线程执行，不会阻塞主循环
        rzr.keyboard_input(36, 1)

    # 蜘蛛侠取消后摇 按键JK
    def spideman_macro():
        rzr.keyboard_input(36, 0)
        time.sleep(0.1)
        rzr.keyboard_input(36, 1)
        time.sleep(0.01)
        rzr.keyboard_input(37, 0)
        time.sleep(0.1) 
        rzr.keyboard_input(37, 1)

    # daredevil格挡 按键9
    def daredevil_macro():
        rzr.keyboard_input(10, 0)
        time.sleep(0.01)
        rzr.keyboard_input(10, 1)
    
    # daredevil连招 按键7890
    def daredevil_combot():
        rzr.keyboard_input(8, 0)
        time.sleep(0.01)
        rzr.keyboard_input(8, 1)
        time.sleep(0.01)
        rzr.keyboard_input(9, 0)
        time.sleep(0.01)
        rzr.keyboard_input(9, 1)
        time.sleep(0.01)
        rzr.keyboard_input(10, 0)
        time.sleep(0.01)
        rzr.keyboard_input(10, 1)
        time.sleep(0.01)
        rzr.keyboard_input(11, 0)
        time.sleep(0.01)
        rzr.keyboard_input(11, 1)

    #挂机宏 按键空格
    def afk_macro():
        rzr.keyboard_input(57, 0)
        time.sleep(0.1)
        rzr.keyboard_input(57, 1)

    #英伟达截图 按键F4
    def nvidia_capture():
        rzr.keyboard_input(62, 0)
        time.sleep(0.1)
        rzr.keyboard_input(62, 1)

    # 主循环
    while True:
        now=time.time()
        loop_count+=1
        
        if now-last_key_time>0.1:
            key = get_key_more()  #按键检测分频
            last_key_time=now
        elif debug==1:
            key=get_key_all()
        else:
            key=get_key_less()

        #模式配置
        if 1:
            if key['f1']:
                aim_mode=1
                fire_mode=1
                aimbot_enable=1
                auto_trigger=0
                x_portion=cfg.x_portion
                y_portion=0.13
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=4.5
                smooth_enable=1
                ctrl_key=0
                print("林蝶模式")
            if aim_mode==1 and key['mb']: #隐身模式
                fire_mode=0
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=2.5
                aim_mode=1.5
            if aim_mode==1.5 and (key['lb'] or key['x1']): #短枪模式
                fire_mode=1
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=4.5
                aim_mode=1
            if (aim_mode==1 or aim_mode==1.5):
                if ctrl_key==0 and key['ctrl']: #冲刺之后提升范围
                    ctrl_key=1
                    aim_range=10000
                    threading.Thread(target=psylocke_dash).start()
                if key['ctrl']==0:
                    ctrl_key=0  

            if key['f2']:
                aim_mode=2
                fire_mode=2
                aimbot_enable=1
                auto_trigger=0
                x_portion=cfg.x_portion
                y_portion=cfg.y_portion
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=4.5
                smooth_enable=1
                x2_key=0
                print("长枪模式")
            #if x2_key==0 and aim_mode==2 and key['4']: #封号警告
            #    x_portion=cfg.x_portion
            #    y_portion=0.37 
            #    aim_range=6
            #    x2_key=1
            #    aim_mode=2.5
            #if x2_key==0 and aim_mode==2.5 and key['4']:
            #    x_portion=cfg.x_portion
            #    y_portion=cfg.y_portion
            #    aim_range=5
            #    x2_key=1
            #    aim_mode=2               
            #if (aim_mode==2 or aim_mode==2.5) and x2_key==1 and key['4']==0:
            #    x2_key=0

            if key['f3']:
                aim_mode=3
                fire_mode=2
                aimbot_enable=1
                auto_trigger=0
                x_portion=cfg.x_portion
                y_portion=0.05
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=4
                smooth_enable=1
                print("凤凰飞天模式")

            if key['f5']:
                aim_mode=5
                fire_mode=3
                aimbot_enable=1
                auto_trigger=1
                x_portion=cfg.x_portion
                y_portion=0.4
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=3.5
                smooth_enable=1
                print("黑寡妇模式")

            if key['f6']:
                aim_mode=6
                fire_mode=2
                aimbot_enable=1
                auto_trigger=0
                x_portion=cfg.x_portion
                y_portion=cfg.y_portion
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=6
                smooth_enable=0
                mb_key=0
                print("夜魔侠模式")
            if aim_mode==6:
                if mb_key==0 and key['mb']: #夜魔侠格挡
                    executor.submit(daredevil_macro)
                    mb_key=1
                if mb_key==1 and key['mb']==0:
                    mb_key=0
                if key['lb'] and key['x1'] and key['mb']==0: #夜魔侠连招
                    if now-last_combot_time>0.1:
                        executor.submit(daredevil_combot)
                        last_combot_time=now

            if key['f7']:
                aim_mode=7
                fire_mode=1
                aimbot_enable=1
                auto_trigger=0
                x_portion=0
                y_portion=55 #另设
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=1
                smooth_enable=1
                print("奶妈模式")
            if aim_mode==7 and key['x1']: #按x1杀人
                aim_mode=7.5
                fire_mode=2
                x_portion=cfg.x_portion
                y_portion=cfg.y_portion 
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=4
            if aim_mode==7.5 and key['x1']==0: #按左键奶人
                aim_mode=7
                fire_mode=1
                x_portion=0
                y_portion=55 #另设
                speed_x=cfg.speed_x
                speed_y=cfg.speed_y
                aim_range=1

            if key['f10']:
                aim_mode=10
                fire_mode=10
                aimbot_enable=1
                auto_trigger = 0
                x_portion=0.1
                y_portion=0.2
                speed_x=cfg.speed_x/2
                speed_y=cfg.speed_y/2
                aim_range=3.5
                smooth_enable=0
                spiderman_key=0
                print("近战模式")
            if aim_mode==10:
                if spiderman_key==0 and key['mb']: #蜘蛛侠取消后摇连招
                    spiderman_key=1
                    threading.Thread(target=spideman_macro).start()
                    print("蜘蛛侠JK宏")
                if spiderman_key==1 and key['mb']==0:
                    spiderman_key=0


            if key['delete']:
                aimbot_enable=0
                aim_mode=0
                print("aimbot已关闭")
            if aimbot_enable==0:
                time.sleep(0.1)
                continue

            if afk==0 and ins_key==0 and key['insert']:
                afk=1
                ins_key=1
                print("开始挂机")
            if afk==1 and ins_key==0 and key['insert']:
                afk=0
                ins_key=1
                print("结束挂机")
            if ins_key==1 and key['insert']==0:
                ins_key=0
            if afk==1:
                if now - last_afk_time < 2:
                    continue  
                last_afk_time=now
                executor.submit(afk_macro)
                continue

        #debug配置
        if debug:
            if f11_key==0 and show_view==0 and key['f11']:
                show_view=1
                f11_key=1
                # 创建显示线程c
                if display_thread is None:
                    display_thread = DisplayThread(window_size=(int(model_x), int(model_y)))
                    display_thread.start()
                    print("可视化开 - 显示线程已启动")
            if f11_key==0 and show_view==1 and key['f11']:
                show_view=0
                f11_key=1
                # 停止显示线程
                if display_thread is not None:
                    display_thread.stop()
                    display_thread.join()
                    display_thread = None
                    print("可视化关 - 显示线程已停止")
            if f11_key==1 and key['f11']==0:
                f11_key=0
            if f12_key==0 and get_train_pic==0 and key['f12']:
                #smooth_enable=1
                f12_key=1
                #print("瞄准平滑开")
                get_train_pic=1
                print("开始获取训练图片")
            if f12_key==0 and get_train_pic==1 and key['f12']:
                #smooth_enable=0
                f12_key=1
                #print("瞄准平滑关")
                get_train_pic=0
                print("停止获取训练图片")
            if f12_key==1 and key['f12']==0:
                f12_key=0
            if key['up']:
                y_portion+=0.01
                print("y_portion:",y_portion)
                #aim_range+=0.5
                #print("aim_range:",aim_range)
                time.sleep(0.2)
            if key['down']:
                y_portion-=0.01
                print("y_portion:",y_portion)
                #aim_range-=0.5
                #print("aim_range:",aim_range)
                time.sleep(0.2)
            if key['left']:
                x_portion-=0.01
                print("y_portion:",x_portion)
                #smoothX.dec_smooth()
                #smoothY.dec_smooth()
                time.sleep(0.2)
            if key['right']:
                x_portion+=0.01
                print("y_portion:",x_portion)
                #smoothX.inc_smooth()
                #smoothY.inc_smooth()
                time.sleep(0.2)
            
            if key['prior']:
                speed_x+=0.05
                speed_y+=0.05
                print("speed:",speed_x)
                time.sleep(0.2)
            if key['next']:
                speed_x-=0.05
                speed_y-=0.05
                print("speed:",speed_x)
                time.sleep(0.2)

        #根据配置选择触发按键
        if fire_mode==-1:
            aim_mouse=0
        elif fire_mode==0:
            aim_mouse=key['shift']==0
        elif fire_mode==1:
            aim_mouse=(key['lb'] or key['x1']) and key['shift']==0
        elif fire_mode==2:
            aim_mouse=key['x1']
        elif fire_mode==3:
            aim_mouse=(key['x2'] or key['rb'] or key['lb']) and key['mb']==0 and key['shift']==0
        elif fire_mode==10:
            aim_mouse=key['shift']==0 and key['f']==0
        else:
            print("错误：无效的鼠标模式配置")
            break
        
        #获取模型训练图片
        if get_train_pic: 
            if aim_mouse:
                if now-last_get_picture_time>2:
                    executor.submit(nvidia_capture)
                    last_get_picture_time=now

        #截图
        if fps_control==1:
            if now - last_capture_time < frame_interval: #还没到下一帧的时间
                continue  
            last_capture_time = now
        img0=capture.get_new_frame()
        if img0 is None:
            print("错误：输入图像为空！")
            continue

        curr_check=img0.ravel()[:300] #极简对比逻辑：拉平数组取前300个值
        if prev_check is not None and np.array_equal(curr_check, prev_check): #如果图像没有变化，跳过
            continue  
        prev_check = curr_check.copy()
        
        #截图遮蔽
        cv2.rectangle(img0, (0, 126), (25, 426), (255, 0, 0),  -1 )
        #if aim_mode==10 :
        #    cv2.rectangle(img0, (25, 200), (100, 426), (255, 0, 0),  -1 )

        #可视化
        if show_view==1: 
            resized_display = cv2.resize(img0, (int(model_x), int(model_y)))

        ############################执行推理############################
        img, ratio, dwdh = letterbox(img0, new_shape=(model_x, model_y)) #图像预处理 缩放后的图像img、缩放比例ratio和填充的像素值dwdh
        if aim_mode==7: #奶妈使用另外的模型
            data = ally_pred.infer(img)
        else:
            data = enemy_pred.infer(img)
        frame_count += 1 #每秒推理次数统计
        num, final_boxes, final_scores, final_cls_inds  = data #数量 坐标 置信度 索引
        ################################################################

        
        #处理目标数据
        if num > 0:
            #图像缩放坐标还原
            dwdh = np.asarray(dwdh*2, dtype=np.float32)
            final_boxes -= dwdh
            #转换数据
            final_boxes = np.reshape(final_boxes/1, (-1, 4))
            final_scores = np.reshape(final_scores, (-1, 1))
            final_cls_inds = np.reshape(final_cls_inds, (-1, 1))
            #弃用dets = np.concatenate([np.array(final_boxes)[:int(num[0])], np.array(final_scores)[:int(num[0])], np.array(final_cls_inds)[:int(num[0])]], axis=-1)
            #先提取数字，再使用
            num_boxes = int(num[0].item())  # 或者 int(num.item())
            dets = np.concatenate([np.array(final_boxes)[:num_boxes], np.array(final_scores)[:num_boxes], np.array(final_cls_inds)[:num_boxes]], axis=-1)
            #边界框坐标、置信度分数和类别索引
            final_boxes, final_scores, final_cls_inds = dets[:, :4], dets[:, 4], dets[:, 5]

            #目标处理
            target_xywh_list = []
            target_distance_list = []
            #遍历所有检测目标
            for i in range(len(final_boxes)):
                box = final_boxes[i]
                score = final_scores[i]

                #可信度过滤
                if (aim_mode==1.5 or aim_mode==5 or aim_mode==10) and score < 0.6: 
                    continue
                    
                #将边界框的坐标格式从 (x1, y1, x2, y2)（左上角+右下角）转换为 (cx, cy, w, h)（中心点+宽高)
                x1, y1, x2, y2 = box
                xywh = [(x1+x2)/2, (y1+y2)/2, (x2-x1), (y2-y1)]
                target_xywh_list.append(xywh)

                #可视化
                if show_view==1:
                    #绘制边界框
                    cv2.rectangle(resized_display, (int(x1), int(y1)), (int(x2),int(y2)), (0, 255, 0), 1)
                    # 绘制文本
                    #text = f'{(xywh[0]- model_x/2)/(xywh[2]/2):.1f},{(xywh[1]- model_y/2- y_portion * target_xywh[3])/(xywh[2]/2):.1f}' #目标与中心距离比例
                    text = f'{xywh[2]:.0f},{score:.2f}' #目标
                    #text = f'{score:.2f}' #置信度
                    (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    #文本背景
                    cv2.rectangle(resized_display, (int(x1), int(y1) - text_height - 5),(int(x1) + text_width, int(y1) - 5),(0, 255, 0), -1)
                    #文本内容
                    cv2.putText(resized_display, text,(int(x1), int(y1) - 7),cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 0, 0), 1)
                    #瞄准点
                    if aim_mode==7:#奶妈特调
                        cv2.circle(resized_display, (int(xywh[0]-x_portion*xywh[2]), int(xywh[1]+y_portion)), 2, (0, 0, 255), -1)
                    else:
                        cv2.circle(resized_display, (int(xywh[0]+x_portion*xywh[2]), int(xywh[1]-y_portion * xywh[3])), 2, (0, 0, 255), -1)

                #目标优先级处理
                if aim_mode==7:#奶妈特调
                    target_distance=(xywh[0] - model_x/2)**2 + (xywh[1]+ y_portion - model_y/2)**2
                else:
                    target_distance=(xywh[0] - model_x/2)**2 + (xywh[1]- (y_portion * xywh[3])- model_y/2)**2
                target_distance_list.append(target_distance)
            
        #fps计数
        if now-last_frame_time >= 1.0:
            fps=frame_count/(now-last_frame_time)
            lps=loop_count/(now-last_frame_time)
            print(f"FPS:{fps:>3.0f} {'平滑' if smooth_enable == 1 else ''}m{aim_mode} |大招{lps:.0f}")
            frame_count=0
            loop_count=0
            last_frame_time=now

        # 可视化
        if show_view==1:
            cv2.putText(resized_display, f'{fps:>3.0f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            # 非阻塞更新显示
            display_thread.update_image(resized_display)
        
        #选取最近目标
        if num>0 and target_xywh_list:  
            min_index = target_distance_list.index(min(target_distance_list))
            target_xywh = target_xywh_list[min_index]

            #自动扳机
            if auto_trigger==1:
                a=(target_xywh[0]-1*target_xywh[2]/2)
                b=(target_xywh[0]+1*target_xywh[2]/2)
                c=(target_xywh[1]-0.95*target_xywh[3]/2)
                d=(target_xywh[1]+0.8*target_xywh[3]/2)
                if a<model_x/2<b and c<model_y/2<d:
                    if key['rb']==0 and key['mb']==0 and key['shift']==0:
                        executor.submit(trigger_key)
                        #threading.Thread(target=trigger_key).start()

            
            #X向量动态调整
            final_x = target_xywh[0] - model_x/2  + x_portion * target_xywh[2]
            if aim_fix==1 and key['a'] and key['d']==0 and aim_mode!=7: #移动补偿 按A要往右调 黑寡妇开镜调
                if now-aim_fix_time>0.2:
                    final_x=target_xywh[0] - model_x/2  + (x_portion+0.1) * target_xywh[2]               
            if aim_fix==1 and key['d'] and key['a']==0 and aim_mode!=7: #移动补偿 按D要往左调  
                if now-aim_fix_time>0.2:
                    final_x=target_xywh[0] - model_x/2  + (x_portion-0.2) * target_xywh[2]                                     
            if aim_fix==1 and (key['a']==0 and key['d']==0) or(key['a'] and key['d']) and aim_mode!=7: #同时按或者不按则还原
                aim_fix_time=now

            #Y向量动态调整             
            if aim_mode==2 and key['shift']: #长枪锁头
                shift_y_portion=0.37
            elif aim_mode==2.5 and (key['rb'] or key['mb'] or key['shift']): # 暴力锁头 右键按下时瞄准中间 海拉星爵右键 弃用
                shift_y_portion=0.2
            elif aim_mode==3 and key['shift']: #飞天锁头
                shift_y_portion=0.4
            elif aim_mode==3 and key['mb']: #飞天锁地
                shift_y_portion=-0.6
            elif aim_mode==5 and key['lb']: #黑寡妇左键
                shift_y_portion=0.4
            else:
                shift_y_portion=y_portion
            final_y = target_xywh[1]-model_y/2-shift_y_portion*target_xywh[3]

            #奶妈特殊参数
            if aim_mode==7:
                if target_xywh[2]>=0.6*model_x: #血条宽度太宽 不加入候选列表
                    continue
                elif model_x/2<=target_xywh[2]<0.6*model_x:
                    shift_y_portion=y_portion-(model_x/2-target_xywh[2])*2
                elif target_xywh[2]<model_x/2:
                    shift_y_portion=y_portion
                final_y = target_xywh[1]-model_y/2+shift_y_portion
                
            #计算系数
            factorX=abs(final_x/(target_xywh[2]/2))
            factorY=abs(final_y/(target_xywh[2]/2))

            #发送鼠标输入
            if aim_mouse:
                if smooth_enable==1: #平滑
                    move_x,move_y=int(final_x * speed_x),int(final_y * speed_y)
                    if factorX>2.7: # 平滑左右分界点2.7
                        move_x=smoothX.update(final_x * speed_x)
                    #else:
                        #smoothX.update(final_x * speed_x)
                    if factorY>3: # 平滑上下分界点3
                        move_y=smoothY.update(final_y * speed_y)     
                    #else:                            
                        #smoothY.update(final_y * speed_y)
                    smoothX.update2(final_x * speed_x)
                    smoothY.update2(final_y * speed_y)    
                else:
                    move_x,move_y=int(final_x * speed_x),int(final_y * speed_y)

                    
                if aim_mode==3: #飞天
                    if factorX<aim_range and factorY<4:
                        mouse_driver_move(move_x,move_y)

                elif aim_mode==5: #黑寡妇
                    if key['lb']:
                        if factorX<10 and factorY<10:
                            mouse_driver_move(move_x,move_y)
                    else:    
                        if  factorX<aim_range and -5<(final_y/(target_xywh[2]/2))<3: #原来是4 和 4
                            mouse_driver_move(move_x,move_y)

                elif aim_mode==7: #奶妈
                    if factorX<0.7 and -1<final_y/(target_xywh[2]/2)<0.8:
                        mouse_driver_move(move_x,move_y)

                elif aim_mode==10: #蜘蛛侠
                    if -aim_range-2<(final_x/(target_xywh[2]/2))<aim_range and factorY<4:
                        mouse_driver_move(move_x,move_y)

                else:
                    if factorX<aim_range and -6<(final_y/(target_xywh[2]/2))<4:
                        mouse_driver_move(move_x,move_y)
                        #executor.submit(mouse_driver_move,move_x,move_y)

            else:
                if smooth_enable==1:
                    smoothX.clean()
                    smoothY.clean()


if __name__ == '__main__':
    try:
        find_target()
    finally:
        #确保程序退出时释放鼠标资源
        if mouse_driver!=1:
            mouse_close()
        print('end')