import os
import tkinter as tk
from pynput import mouse
from utils.rzctl import RZCONTROL
import time
import threading
class Application:
    def __init__(self):
        self.init_razer()
        self.create_double_border_box()
        self.start_mouse_listener()

    def init_razer(self):
        """初始化Razer鼠标控制"""
        dll_path = r"F:\0326aimbotyolo11n\aimbot\utils\rzctl.dll"
        if not os.path.exists(dll_path):
            print(f"错误：文件不存在 - {dll_path}")
            exit()
        print("DLL 文件存在，准备加载")
        self.rzr = RZCONTROL(dll_path)
    
        

    def precise_sleep(self,delay):
        """高精度睡眠（忙等待）"""
        start = time.perf_counter()
        while time.perf_counter() - start < delay:
            pass


    def create_double_border_box(self):
        """创建双边框窗口"""
        # 外层边框参数（绿色）
        outer_x, outer_y = 1120, 540  # 内部区域起始坐标
        outer_inner_w, outer_inner_h = 320, 320  # 内部区域尺寸
        outer_border = 3  # 边框粗细
        
        # 内层边框参数（红色）
        inner_inner_w, inner_inner_h = 160, 160  # 内部区域尺寸
        inner_border = 2  # 边框粗细
        
        # 计算内层边框位置（居中）
        inner_x = (outer_inner_w - inner_inner_w) // 2
        inner_y = (outer_inner_h - inner_inner_h) // 2

        # 计算窗口总大小（外层边框外部尺寸）
        total_width = outer_inner_w + 2 * outer_border
        total_height = outer_inner_h + 2 * outer_border
        
        # 窗口位置（补偿外层边框）
        window_x = outer_x - outer_border
        window_y = outer_y - outer_border

        # 创建透明窗口
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.geometry(f"{total_width}x{total_height}+{window_x}+{window_y}")
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'black')

        # 创建画布
        canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        # 绘制外层绿色边框（确保内部320x320）
        canvas.create_rectangle(
            outer_border, outer_border,
            outer_border + outer_inner_w, outer_border + outer_inner_h,
            outline='#00FF00', width=outer_border, fill=''
        )

        # 绘制内层红色边框（确保内部160x160）
        canvas.create_rectangle(
            outer_border + inner_x, outer_border + inner_y,
            outer_border + inner_x + inner_inner_w, outer_border + inner_y + inner_inner_h,
            outline='red', width=inner_border, fill=''
        )

        # 绑定键盘事件
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.focus_set()
        print("双边框已显示（外绿内红），按 Q 键关闭")

    def start_mouse_listener(self):
        """启动鼠标监听"""
        print("监听鼠标右键点击中...")
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        self.root.mainloop()
    
        #32143
    def on_click(self, x, y, button, pressed):
        # 定义触发函数
        def trigger_key():
            self.rzr.mouse_move(int(100), 0, True)
            self.precise_sleep(0.1)
            self.rzr.mouse_move(-int(100), 0, True)
        """鼠标点击回调"""
        if button == mouse.Button.right and pressed:
            print(f"鼠标右键点击在 ({x}, {y})")
            # 示例：延迟 100 微秒（0.1 ms）   1ms=1000us=0.001
            #precise_sleep(0.0001)  # 100 μs
            threading.Thread(target=trigger_key).start()  # 非阻塞执行
            #self.precise_sleep(1)
            #self.rzr.keyboard_input(29,0)
            #self.precise_sleep(0.01)
            #self.rzr.keyboard_input(29,1)
            #self.precise_sleep(0.01)
            

            #self.rzr.keyboard_input(38,0)
            

    def on_key_press(self, event):
        """键盘按键回调"""
        if event.keysym.lower() == 'q':
            print("正在关闭程序...")
            self.listener.stop()
            self.root.destroy()
            exit()

if __name__ == "__main__":
    app = Application()