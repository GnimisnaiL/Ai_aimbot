# 文件路径: utils/macro_controller.py
import time
import win32api
import win32con

class MacroController:
    def __init__(self, rzr_instance):
        """
        初始化控制器
        :param rzr_instance: 传入主程序初始化好的 rzr 实例
        """
        self.rzr = rzr_instance

        # 批量获取按键状态
    def get_key_less(self):
        keys = {
            'f1': 0,
            'f2': 0,
            'f3': 0,
            'f5': 0,
            'f6': 0,
            'f7':  0,
            'f9':  0,
            'f10': 0,
            'f11': 0,
            'f12': 0,
            'up': 0,
            'down': 0,
            'left': 0,
            'right': 0,
            'prior': 0,
            'next': 0,
            'alt': 0,
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
    def get_key_more(self):
        keys = {
            'f1': win32api.GetAsyncKeyState(win32con.VK_F1) & 0x8000 != 0,
            'f2': win32api.GetAsyncKeyState(win32con.VK_F2) & 0x8000 != 0,
            'f3': win32api.GetAsyncKeyState(win32con.VK_F3) & 0x8000 != 0,
            'f5': win32api.GetAsyncKeyState(win32con.VK_F5) & 0x8000 != 0,
            'f6': win32api.GetAsyncKeyState(win32con.VK_F6) & 0x8000 != 0,
            'f7': win32api.GetAsyncKeyState(win32con.VK_F7) & 0x8000 != 0,
            'f9': win32api.GetAsyncKeyState(win32con.VK_F9) & 0x8000 != 0,
            'f10': win32api.GetAsyncKeyState(win32con.VK_F10) & 0x8000 != 0,
            'f11': win32api.GetAsyncKeyState(win32con.VK_F11) & 0x8000 != 0,
            'f12': win32api.GetAsyncKeyState(win32con.VK_F12) & 0x8000 != 0,
            'up': 0,
            'down': 0,
            'left': 0,
            'right': 0,
            'prior': 0,
            'next': 0,
            'alt': win32api.GetAsyncKeyState(win32con.VK_MENU) & 0x8000 !=0,
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
    def get_key_all(self):
        keys = {
            'f1': win32api.GetAsyncKeyState(win32con.VK_F1) & 0x8000 != 0,
            'f2': win32api.GetAsyncKeyState(win32con.VK_F2) & 0x8000 != 0,
            'f3': win32api.GetAsyncKeyState(win32con.VK_F3) & 0x8000 != 0,
            'f5': win32api.GetAsyncKeyState(win32con.VK_F5) & 0x8000 != 0,
            'f6': win32api.GetAsyncKeyState(win32con.VK_F6) & 0x8000 != 0,
            'f7': win32api.GetAsyncKeyState(win32con.VK_F7) & 0x8000 != 0,
            'f9': win32api.GetAsyncKeyState(win32con.VK_F9) & 0x8000 != 0,
            'f10': win32api.GetAsyncKeyState(win32con.VK_F10) & 0x8000 != 0,
            'f11': win32api.GetAsyncKeyState(win32con.VK_F11) & 0x8000 != 0,
            'f12': win32api.GetAsyncKeyState(win32con.VK_F12) & 0x8000 != 0,
            'up': win32api.GetAsyncKeyState(win32con.VK_UP) & 0x8000 !=0,
            'down': win32api.GetAsyncKeyState(win32con.VK_DOWN) & 0x8000 !=0,
            'left': win32api.GetAsyncKeyState(win32con.VK_LEFT) & 0x8000 !=0,
            'right': win32api.GetAsyncKeyState(win32con.VK_RIGHT) & 0x8000 !=0,
            'prior': win32api.GetAsyncKeyState(win32con.VK_PRIOR) & 0x8000 !=0,
            'next': win32api.GetAsyncKeyState(win32con.VK_NEXT) & 0x8000 !=0,
            'alt': win32api.GetAsyncKeyState(win32con.VK_MENU) & 0x8000 !=0,
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

    # 自动扳机触发函数 按键J
    def trigger_key(self):
        self.rzr.keyboard_input(36, 0)
        time.sleep(0.001)
        self.rzr.keyboard_input(36, 1)

    # 蜘蛛侠取消后摇 按键JK
    def spideman_macro(self):
        self.rzr.keyboard_input(36, 0)
        time.sleep(0.1)
        self.rzr.keyboard_input(36, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(37, 0)
        time.sleep(0.1) 
        self.rzr.keyboard_input(37, 1)

    # daredevil格挡 按键9
    def daredevil_macro(self):
        self.rzr.keyboard_input(10, 0)
        time.sleep(0.01)
        self.rzr.keyboard_input(10, 1)
    
    # daredevil连招 按键7890
    def daredevil_combot(self):
        self.rzr.keyboard_input(8, 0)
        time.sleep(0.01)
        self.rzr.keyboard_input(8, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(9, 0)
        time.sleep(0.01)
        self.rzr.keyboard_input(9, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(10, 0)
        time.sleep(0.01)
        self.rzr.keyboard_input(10, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(11, 0)
        time.sleep(0.01)
        self.rzr.keyboard_input(11, 1)

    # daredevil连招2按键7860
    def daredevil2_combot(self):
        self.rzr.keyboard_input(8, 0)
        time.sleep(0.01)
        self.rzr.keyboard_input(8, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(9, 0)
        time.sleep(0.01)
        self.rzr.keyboard_input(9, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(7, 0)
        time.sleep(0.01)
        self.rzr.keyboard_input(7, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(11, 0)
        time.sleep(0.01)
        self.rzr.keyboard_input(11, 1)

    # 挂机宏 按键空格
    def afk_macro(self):
        self.rzr.keyboard_input(57, 0)
        time.sleep(0.1)
        self.rzr.keyboard_input(57, 1)

    # 英伟达截图 按键F4
    def nvidia_capture(self):
        self.rzr.keyboard_input(62, 0)
        time.sleep(0.1)
        self.rzr.keyboard_input(62, 1)