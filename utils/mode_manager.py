# 文件路径: utils/aim_mode.py
from utils.config_watcher import cfg

class ModeManager:

    def get_mode_config(self, key):
        
        config=None
        if key['f1']:
            config={
                'name': "林蝶模式", 
                'aim_mode': 1, 
                'fire_mode': 1, 
                'aimbot_enable': True,
                'auto_trigger': False,
                'x_portion': cfg.x_portion, 
                'y_portion': 0.13, 
                'speed_x': cfg.speed_x,
                'speed_y': cfg.speed_y,
                'aim_range': 4, 
                'smooth_enable': True,
                'auto_headshot' : False
            }
        if key['f2']:
            config={
                'name': "普通长枪模式", 
                'aim_mode': 2, 
                'fire_mode': 2, 
                'aimbot_enable': True,
                'auto_trigger': False,
                'x_portion': cfg.x_portion, 
                'y_portion': cfg.y_portion, 
                'speed_x': cfg.speed_x,
                'speed_y': cfg.speed_y,
                'aim_range': 4, 
                'smooth_enable': True,
                'auto_headshot' : True
            }
        if key['f3']:
            config={
                'name': "凤凰飞天模式", 
                'aim_mode': 3, 
                'fire_mode': 2, 
                'aimbot_enable': True,
                'auto_trigger': False,
                'x_portion': cfg.x_portion, 
                'y_portion': 0.1, 
                'speed_x': cfg.speed_x,
                'speed_y': cfg.speed_y,
                'aim_range': 4, 
                'smooth_enable': True,
                'auto_headshot' : True
            }
        if key['f5']:
            config={
                'name': "黑寡妇模式", 
                'aim_mode': 5, 
                'fire_mode': 3, 
                'aimbot_enable': True,
                'auto_trigger': True,
                'x_portion': cfg.x_portion, 
                'y_portion': 0.4, 
                'speed_x': cfg.speed_x,
                'speed_y': cfg.speed_y,
                'aim_range': 3.5, 
                'smooth_enable': True,
                'auto_headshot' : False
            }
        if key['f6']:
            config={
                'name': "夜魔侠模式", 
                'aim_mode': 6, 
                'fire_mode': 6, 
                'aimbot_enable': True,
                'auto_trigger': False,
                'x_portion': cfg.x_portion, 
                'y_portion': cfg.y_portion, 
                'speed_x': cfg.speed_x,
                'speed_y': cfg.speed_y,
                'aim_range': 6, 
                'smooth_enable': False,
                'auto_headshot' : False
            }
        if key['f7']:
            config={
                'name': "奶妈模式", 
                'aim_mode': 7, 
                'fire_mode': 1, 
                'aimbot_enable': True,
                'auto_trigger': False,
                'x_portion': 0, 
                'y_portion': 55, 
                'speed_x': cfg.speed_x,
                'speed_y': cfg.speed_y,
                'aim_range': 1, 
                'smooth_enable': True,
                'auto_headshot' : False
            }
        if key['f10']:
            config={
                'name': "近战模式", 
                'aim_mode': 10, 
                'fire_mode': 10, 
                'aimbot_enable': True,
                'auto_trigger': False,
                'x_portion': 0.1, 
                'y_portion': 0.2, 
                'speed_x': cfg.speed_x/2,
                'speed_y': cfg.speed_y/2,
                'aim_range': 3, 
                'smooth_enable': False,
                'auto_headshot' : False
            }
        if key['x2'] and key['f2']:
            config={
                'name': "暴力锁头模式", 
                'aim_mode': 22, 
                'fire_mode': 2, 
                'aimbot_enable': True,
                'auto_trigger': False,
                'x_portion': cfg.x_portion, 
                'y_portion': 0.37, 
                'speed_x': cfg.speed_x,
                'speed_y': cfg.speed_y,
                'aim_range': 4, 
                'smooth_enable': True,
                'auto_headshot' : False
            }
        return config