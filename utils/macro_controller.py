# 文件路径: utils/macro_controller.py
import time
import os
import win32api
import win32con
#雷蛇控制
from utils.rzctl import RZCONTROL
#罗技控制
from utils.logitech_mouse import *
from utils.virtual_gamepad import VirtualGamepad


class MacroController:
    def __init__(self,mouse_driver):
        """
        初始化控制器
        """
        self.mouse_driver=mouse_driver

        #初始化 Razer 鼠标
        dll_path =  str("./utils/rzctl.dll")  # 确保路径正确

        if not os.path.exists(dll_path):
            print(f"错误：雷蛇dll文件不存在 - {dll_path}")

        self.rzr = RZCONTROL(dll_path)

        if not self.rzr.init():  # 检查是否初始化成功
            print("错误：无法初始化 Razer 鼠标控制！")

        if self.mouse_driver==1:
            mouse_open() #打开罗技鼠标设备
            print("罗技鼠标控制已初始化")
        elif self.mouse_driver==2:
            self.virtual_gamepad=VirtualGamepad()


    def high_precision_sleep(self,duration):
        """
        使用 perf_counter 进行忙等待，实现微秒级精度
        """
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < duration:
            pass

    # 鼠标移动控制器
    def mouse_driver_move(self,x,y):
        if abs(round(x))<2 and abs(round(y))<2:
            return
        if self.mouse_driver==0:
            self.rzr.mouse_move(round(x),round(y),True)
        elif self.mouse_driver==1:
            if abs(round(x))>127:
                print("鼠标行程超标")
                x=127
            if abs(round(y))>127:
                print("鼠标行程超标")
                y=127
            mouse_move(0, round(y), round(y), 0)
        elif self.mouse_driver==2:
            self.virtual_gamepad.set_right_stick(x/80,-y/80)


    # 批量获取按键状态
    def get_keys_less(self):
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
            'tab': win32api.GetAsyncKeyState(win32con.VK_TAB) & 0x8000 !=0,
            'insert': win32api.GetAsyncKeyState(win32con.VK_INSERT) & 0x8000 != 0,
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
            '0': 0,
            '9': 0,
            '8': 0,
            '7': 0
        }
        return keys
    def get_keys_more(self):
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
            'tab': win32api.GetAsyncKeyState(win32con.VK_TAB) & 0x8000 !=0,
            'insert': win32api.GetAsyncKeyState(win32con.VK_INSERT) & 0x8000 != 0,
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
            '0': 0,
            '9': 0,
            '8': 0,
            '7': 0

        }
        return keys
    def get_keys_all(self):
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
            'tab': win32api.GetAsyncKeyState(win32con.VK_TAB) & 0x8000 !=0,
            'insert': win32api.GetAsyncKeyState(win32con.VK_INSERT) & 0x8000 !=0,
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
            '0': win32api.GetAsyncKeyState(0x30) & 0x8000 != 0,
            '9': win32api.GetAsyncKeyState(0x39) & 0x8000 != 0,
            '8': win32api.GetAsyncKeyState(0x38) & 0x8000 != 0,
            '7': win32api.GetAsyncKeyState(0x37) & 0x8000 != 0
        }
        return keys

    # 自动扳机触发函数 按键J
    def trigger_key(self):
        self.rzr.keyboard_input(36, 0)
        time.sleep(0.001)
        self.rzr.keyboard_input(36, 1)


    # 夜魔侠格挡 按键R
    def daredevil_R_macro(self):
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.1)
        self.rzr.keyboard_input(19, 1)
    
    # 夜魔侠1
    def daredevil_LCRF_macro(self):
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.01)
        self.rzr.keyboard_input(38, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(46, 0) #C
        time.sleep(0.01)
        self.rzr.keyboard_input(46, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.01)
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 0) #F
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 1)

    # 夜魔侠2
    def daredevil_LCEF_macro(self):
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.01)
        self.rzr.keyboard_input(38, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(46, 0) #C
        time.sleep(0.01)
        self.rzr.keyboard_input(46, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(18, 0) #E
        time.sleep(0.01)
        self.rzr.keyboard_input(18, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 0) #F
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 1)

    # 蜘蛛侠
    def spiderman_KRE_macro(self):
        self.rzr.keyboard_input(37, 0) #K
        time.sleep(0.01)
        self.rzr.keyboard_input(37, 1)
        time.sleep(0.09)
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.22) 
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01) 
        self.rzr.keyboard_input(18, 0) #E
        time.sleep(0.01) 
        self.rzr.keyboard_input(18, 1)

    # 蜘蛛侠E
    def spiderman_E_macro(self):
        self.rzr.keyboard_input(18, 0) #E
        time.sleep(0.01) 
        self.rzr.keyboard_input(18, 1)


    # 蜘蛛侠 shift-右键
    def spiderman_KR_macro(self):
        self.rzr.keyboard_input(37, 0) #K
        time.sleep(0.1)
        self.rzr.keyboard_input(37, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.1) 
        self.rzr.keyboard_input(19, 1)
        

    # 蜘蛛侠
    def spiderman_ELRF_macro(self):
        self.rzr.keyboard_input(18, 0) #E
        time.sleep(0.01) 
        self.rzr.keyboard_input(18, 1)
        time.sleep(0.1)
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.01) 
        self.rzr.keyboard_input(38, 1)
        time.sleep(0.2)
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.1) 
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 0) #F
        time.sleep(0.1) 
        self.rzr.keyboard_input(33, 1)

    # 蜘蛛侠 
    def spiderman_RELRF_macro(self):
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.1) 
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(18, 0) #E
        time.sleep(0.01) 
        self.rzr.keyboard_input(18, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.187)
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.03)  
        self.rzr.keyboard_input(38, 1)
        time.sleep(0.18) 
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01) 
        self.rzr.keyboard_input(33, 0) #F
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 1)

    # 蜘蛛侠
    def spiderman_RFKRE_macro(self):
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.1) 
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 0) #F
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 1)
        time.sleep(0.3)
        self.rzr.keyboard_input(37, 0) #K
        time.sleep(0.01)
        self.rzr.keyboard_input(37, 1)
        time.sleep(0.09)
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.22) 
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01) 
        self.rzr.keyboard_input(18, 0) #E
        time.sleep(0.01) 
        self.rzr.keyboard_input(18, 1)


    # 蜘蛛侠
    def spiderman_LRFKRE_macro(self):
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.187) 
        self.rzr.keyboard_input(38, 1)
        time.sleep(0.01) 
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.1) 
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 0) #F
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 1)
        time.sleep(0.3)
        self.rzr.keyboard_input(37, 0) #K
        time.sleep(0.01)
        self.rzr.keyboard_input(37, 1)
        time.sleep(0.09)
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.22) 
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01) 
        self.rzr.keyboard_input(18, 0) #E
        time.sleep(0.01) 
        self.rzr.keyboard_input(18, 1)

    # 蜘蛛侠
    def spiderman_LRFKR_macro(self):
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.187) 
        self.rzr.keyboard_input(38, 1)
        time.sleep(0.01) 
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.1) 
        self.rzr.keyboard_input(19, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 0) #F
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 1)
        time.sleep(0.3)
        self.rzr.keyboard_input(37, 0) #K
        time.sleep(0.01)
        self.rzr.keyboard_input(37, 1)
        time.sleep(0.09)
        self.rzr.keyboard_input(19, 0) #R
        time.sleep(0.1) 
        self.rzr.keyboard_input(19, 1)

    # 蜘蛛侠 跳+上勾拳
    def spiderman_JF_macro(self):
        self.rzr.keyboard_input(36, 0) #J
        time.sleep(0.01)
        self.rzr.keyboard_input(36, 1)
        time.sleep(0.01)
        self.rzr.keyboard_input(33, 0) #F
        time.sleep(0.1)
        self.rzr.keyboard_input(33, 1)

    # 蜘蛛侠 c
    def spiderman_C_macro(self):
        self.rzr.keyboard_input(46, 0) #C
        self.high_precision_sleep(0.01)
        self.rzr.keyboard_input(46, 1)


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

    # RTSS限制帧数 alt+8
    def rtss_set_framerate_to_80(self):
        self.rzr.keyboard_input(56, 0)
        self.rzr.keyboard_input(9, 0)
        time.sleep(1)
        self.rzr.keyboard_input(56, 1)
        self.rzr.keyboard_input(9, 1)

    # RTSS接触限制帧数 alt+0
    def rtss_set_framerate_to_100(self):
        self.rzr.keyboard_input(56, 0)
        self.rzr.keyboard_input(11, 0)
        time.sleep(1)
        self.rzr.keyboard_input(56, 1)
        self.rzr.keyboard_input(11, 1)

    # RTSS接触限制帧数 alt+F8
    def rtss_set_framerate_to_0(self):
        self.rzr.keyboard_input(56, 0)
        self.rzr.keyboard_input(66, 0)
        time.sleep(1)
        self.rzr.keyboard_input(56, 1)
        self.rzr.keyboard_input(66, 1)

    # cd提示
    def notice_cd(self):
        self.rzr.keyboard_input(4, 0) #3
        time.sleep(0.01)
        self.rzr.keyboard_input(4, 1)

    # 开门
    def strange_opendoor(self):
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.01) 
        self.rzr.keyboard_input(38, 1)

    # 毒液
    def venom_utl(self):
        self.rzr.keyboard_input(16, 0) #Q
        time.sleep(0.03) 
        self.rzr.keyboard_input(16, 1)
        time.sleep(0.6)
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.1) 
        self.rzr.keyboard_input(38, 1)
        time.sleep(0.1)
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.1) 
        self.rzr.keyboard_input(38, 1)
    # 毒液
    def venom_health(self):
        self.rzr.keyboard_input(46, 0) #C
        time.sleep(0.01) 
        self.rzr.keyboard_input(46, 1)

     # 毒液开大提示
    def venom_notice(self):
        self.rzr.keyboard_input(5, 0) #4
        time.sleep(0.01) 
        self.rzr.keyboard_input(5, 1)

    #按下I
    def press_I(self):
        self.rzr.keyboard_input(23, 0) #I
        time.sleep(1)

    #放开I
    def release_I(self):
        self.rzr.keyboard_input(23, 1) #I

    def phoenix_J_macro(self):
        self.rzr.keyboard_input(36, 0) #J
        time.sleep(0.01)
        self.rzr.keyboard_input(36, 1)

    def hawkeye_L_macro(self):
        self.rzr.keyboard_input(38, 0) #L
        time.sleep(0.03) 
        self.rzr.keyboard_input(38, 1)

    def blackpanther_M_macro(self):
        self.rzr.keyboard_input(50, 0) #M
        time.sleep(0.01) 
        self.rzr.keyboard_input(50, 1)



# Scancode    Keyboard Key
# 1   ESC
# 2   1
# 3   2
# 4   3
# 5   4
# 6   5
# 7   6
# 8   7
# 9   8
# 10  9
# 11  0
# 12  -
# 13  =
# 14  bs
# 15  Tab
# 16  Q
# 17  W
# 18  E
# 19  R
# 20  T
# 21  Y
# 22  U
# 23  I
# 24  O
# 25  P
# 26  [
# 27  ]
# 28  Enter
# 29  CTRL
# 30  A
# 31  S
# 32  D
# 33  F
# 34  G
# 35  H
# 36  J
# 37  K
# 38  L
# 39  ;
# 40  '
# 41  `
# 42  LShift
# 43  \
# 44  Z
# 45  X
# 46  C
# 47  V
# 48  B
# 49  N
# 50  M
# 51  ,
# 52  .
# 53  /
# 54  RShift
# 55  PrtSc
# 56  Alt
# 57  Space
# 58  Caps
# 59  F1
# 60  F2
# 61  F3
# 62  F4
# 63  F5
# 64  F6
# 65  F7
# 66  F8
# 67  F9
# 68  F10
# 69  Num
# 70  Scroll
# 71  Home (7)
# 72  Up (8)
# 73  PgUp (9)
# 74  -
# 75  Left (4)
# 76  Center (5)
# 77  Right (6)
# 78  +
# 79  End (1)
# 80  Down (2)
# 81  PgDn (3)
# 82  Ins
# 83  Del