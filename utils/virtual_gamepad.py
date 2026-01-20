# 安装: pip install vgamepad
from vgamepad import VX360Gamepad
import time

class VirtualGamepad:
    def __init__(self):
        self.gamepad = VX360Gamepad()
        
    def set_right_stick(self, x, y):
        """设置右摇杆位置 (-1.0 到 1.0)"""
        # 注意: vgamepad 期望值范围是 -32768 到 32768
        x = int(max(-32768, min(32768, x * 32768)))
        y = int(max(-32768, min(32768, y * 32768)))
        
        self.gamepad.right_joystick(x_value=x, y_value=y)
        self.gamepad.update()
        
    def press_button(self, button_name):
        """按下按键"""
        button_map = {
            'A': 'BUTTONS.A',
            'B': 'BUTTONS.B',
            'X': 'BUTTONS.X',
            'Y': 'BUTTONS.Y',
            'LB': 'BUTTONS.LEFT_SHOULDER',
            'RB': 'BUTTONS.RIGHT_SHOULDER',
            'START': 'BUTTONS.START',
            'BACK': 'BUTTONS.BACK',
            'LS': 'BUTTONS.LEFT_THUMB',
            'RS': 'BUTTONS.RIGHT_THUMB',
        }
        if button_name in button_map:
            getattr(self.gamepad, f'press_button')(eval(f'vgamepad.{button_map[button_name]}'))
            self.gamepad.update()
            
    def release_button(self, button_name):
        """释放按键"""
        if hasattr(self.gamepad, f'release_button'):
            getattr(self.gamepad, f'release_button')(eval(f'vgamepad.{button_map[button_name]}'))
            self.gamepad.update()
            
    def set_trigger(self, left=0.0, right=0.0):
        """设置扳机键 (0.0 到 1.0)"""
        self.gamepad.left_trigger_float(left)
        self.gamepad.right_trigger_float(right)
        self.gamepad.update()
        
    def reset(self):
        """重置所有输入"""
        self.gamepad.reset()
        self.gamepad.update()
        
    def close(self):
        self.gamepad.close()