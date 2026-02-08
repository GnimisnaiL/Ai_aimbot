# 文件路径: utils/mode_manager.py

import time
import threading
#获取技能cd
from utils.skill_cd import *
#可视化线程
from utils.show_view import DisplayThread
#读取cfg文件
from utils.config_watcher import cfg


#改变值
def change_value(name,value,delta,is_sleep=True):
    value+=delta
    print(f"{name}: {value:.3f}")
    if is_sleep:
        time.sleep(0.2)
    return value


#值锁存
def key_toggle(state, key_pressed):
    if state == 0 and key_pressed:
        return 1, True
    if state == 1 and not key_pressed:
        return 0, False
    return state, None


class ModeContext:
    def __init__(self, now):
        self.afk = False #挂机
        self.aimbot_enable = True #自瞄开关
        self.skill_cd = 1 #技能cd
        self.get_train_pic = False #获取训练图片
        
        self.show_view = False #可视化
        self.display_thread = None #可视线程
        self.prev_check = None #上一帧切片
        self.test_aim = False #测试
        
        self.dist_fix = True #距离补偿
        self.dist_standard_speed = 3.92 #标准距离单位速度
        self.move_fix = True #移动补偿
        self.move_time_threshold = 0.13 #移动补偿启动时间
        self.last_move_direction = 0 #记录上一次移动方向
        self.delay_fix = False #延迟补偿
        self.delay_threshold = 0.04 #推理弃用延迟时间ms

        #ai每秒循环速度控制
        self.fps_control=cfg.fps_control #ai速率控制
        self.frame_interval=1.0/cfg.capture_fps #每帧时间

        self.key_insert = 0
        self.key_f10 = 0
        self.key_f11 = 0
        self.key_f12 = 0
        self.key_x2 = 0
        self.key_0 = 0
        self.key_9 = 0
        self.key_8 = 0
        self.key_7 = 0

        self.last_afk_time = now #上一轮挂机时间
        self.last_key_time = now #按键检测分频时间
        self.last_print_time = now #打印时间
        self.last_capture_time = now #fps控制
        self.last_get_picture_time = now #获取训练图片控制频率
        self.last_round_time = None #计算每轮循环时间
        self.move_time = now #移动补偿时间

        #数据统计
        self.fps=0
        self.tip=0
        self.total_frame=0
        self.total_infer_delay=0

        self.reset(now)
        

    def reset(self, now):
        self.afk = False
        self.aimbot_enable = True

        self.key_rb = 0
        self.key_mb = 0
        self.key_x1 = 0
        self.key_ctrl = 0


        self.last_mb_time = now
        self.last_ctrl_time = now
        self.last_combo_time = now


        #蜘蛛
        self.spiderman1_key = 0
        self.spiderman2_key = 0
        self.spiderman3_key = 0

        #毒液
        self.venom = 0
        self.venom_rb_time = now
        self.venom_health_count = 0

        #奇异
        self.strange_opendoor = 0


class ModeManager:
    def  __init__(self):

        self.mode_config={
            '灵蝶':
                    {'name':"灵蝶",'id':1,   'fire':1, 'Px':cfg.Px, 'Py':0.14,  'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,6,0],      'smooth':0, 'headshot':False,'headshot_dist':8, 'headshot_pos':0.25,'move_fix_adjust':1},
            '灵蝶隐身':
                    {'name':"灵蝶",'id':1.5, 'fire':0, 'Px':cfg.Px, 'Py':0.14,  'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-3,3,-6,6,0],      'smooth':0, 'headshot':False,'headshot_dist':8, 'headshot_pos':0.25,'move_fix_adjust':1},

            "鹰眼":
                    {'name':"鹰眼",'id':11,  'fire':11,'Px':cfg.Px, 'Py':0.35,  'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,4,0],      'smooth':0, 'headshot':True, 'headshot_dist':12,'headshot_pos':0.2, 'move_fix_adjust':0.85},
            "鹰眼连射":
                    {'name':"鹰眼",'id':11.5,'fire':11,'Px':cfg.Px, 'Py':0.4,   'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,4,0],      'smooth':0, 'headshot':False,'headshot_dist':0, 'headshot_pos':0,   'move_fix_adjust':0.95},

            "默认":
                    {'name':"默认",'id':2,   'fire':2, 'Px':cfg.Px, 'Py':cfg.Py,'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,6,1],      'smooth':0, 'headshot':False,'headshot_dist':15,'headshot_pos':0.37,'move_fix_adjust':1},
            "暴力":
                    {'name':"暴力",'id':22,  'fire':2, 'Px':cfg.Px, 'Py':0.37,  'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,6,1],      'smooth':0, 'headshot':False,'headshot_dist':0, 'headshot_pos':0.37,'move_fix_adjust':1},

            "凤凰":
                    {'name':"凤凰",'id':3,   'fire':2, 'Px':cfg.Px, 'Py':0.1,   'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,4,0],      'smooth':1, 'headshot':True, 'headshot_dist':13,'headshot_pos':0.4, 'move_fix_adjust':1},
            "飞天":
                    {'name':"飞天",'id':13,  'fire':2, 'Px':cfg.Px, 'Py':0.14,  'Sx':cfg.Sx*1.1,'Sy':cfg.Sy*1.1,'lrud':[-4,4,-5,4,0],      'smooth':1, 'headshot':False,'headshot_dist':-9,'headshot_pos':0.1, 'move_fix_adjust':1},

            
            "奇异":
                    {'name':"奇异",'id':15,  'fire':-1,'Px':cfg.Px, 'Py':cfg.Py,'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,4,0],      'smooth':0, 'headshot':False,'headshot_dist':-9,'headshot_pos':0,   'move_fix_adjust':1},                    
            "寡妇":
                    {'name':"寡妇",'id':25,  'fire':25,'Px':0,      'Py':0.4,   'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-3,3,-5,3,0],      'smooth':1, 'headshot':False,'headshot_dist':-9,'headshot_pos':0.4, 'move_fix_adjust':0.6},

            "夜魔":
                    {'name':"夜魔",'id':6,   'fire':6, 'Px':0.1,    'Py':cfg.Py,'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,6,1],      'smooth':0, 'headshot':False,'headshot_dist':4, 'headshot_pos':0.3, 'move_fix_adjust':1},
            "铁拳":
                    {'name':"铁拳",'id':16,  'fire':16,'Px':cfg.Px, 'Py':cfg.Py,'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,6,1],      'smooth':0, 'headshot':True, 'headshot_dist':4, 'headshot_pos':0.35, 'move_fix_adjust':1},
            "金刚":
                    {'name':"金刚",'id':26,  'fire':26,'Px':cfg.Px, 'Py':cfg.Py,'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,6,1],      'smooth':0, 'headshot':False,'headshot_dist':4, 'headshot_pos':0.3, 'move_fix_adjust':1},

            "奶妈":
                    {'name':"奶妈",'id':17,  'fire':1, 'Px':0,      'Py':55,    'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-0.7,0.7,-1,0.8,0],'smooth':1, 'headshot':False,'headshot_dist':-9,'headshot_pos':0,   'move_fix_adjust':0},
            "奶妈锁敌":
                    {'name':"奶妈",'id':17.5,'fire':2, 'Px':cfg.Px, 'Py':cfg.Py,'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,4,0],      'smooth':1, 'headshot':False,'headshot_dist':0, 'headshot_pos':0,   'move_fix_adjust':1},
            '测试':
                    {'name':"测试",'id':27,  'fire':2, 'Px':0,      'Py':0,     'Sx':4,         'Sy':4,         'lrud':[-99,99,-99,99,0],  'smooth':0, 'headshot':False,'headshot_dist':0, 'headshot_pos':0,   'move_fix_adjust':0},

            "蜘蛛":
                    {'name':"蜘蛛",'id':9,   'fire':9, 'Px':0.1,    'Py':0.14,  'Sx':cfg.Sx/1.5,'Sy':cfg.Sy/1.5,'lrud':[-3,3,-3,3,0],      'smooth':0, 'headshot':False,'headshot_dist':-9,'headshot_pos':0,   'move_fix_adjust':1.5},
            "蜘蛛近战":
                    {'name':"蜘蛛",'id':9.5, 'fire':9, 'Px':0.1,    'Py':cfg.Py,'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,4,1],      'smooth':0, 'headshot':False,'headshot_dist':-9,'headshot_pos':0,   'move_fix_adjust':1},
            "毒液":
                    {'name':"毒液",'id':19,  'fire':19,'Px':0,      'Py':0.4,   'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,6,1],      'smooth':0, 'headshot':True, 'headshot_dist':6, 'headshot_pos':0.2, 'move_fix_adjust':1},
                    
            "死侍":
                    {'name':"死侍",'id':10,  'fire':2, 'Px':cfg.Px, 'Py':cfg.Py,'Sx':cfg.Sx,    'Sy':cfg.Sy,    'lrud':[-4,4,-6,4,1],      'smooth':0, 'headshot':True, 'headshot_dist':15,'headshot_pos':0.37,'move_fix_adjust':1}
            
        }

    #根据按键获取模式配置
    def get_mode_config(self, keys):
        config=None
        
        if keys['f1']:
            config = self.mode_config.get('灵蝶').copy()
        if keys['x1'] and keys['f1']:
            config = self.mode_config.get('鹰眼').copy()
        if keys['f2']:
            config = self.mode_config.get('默认').copy()
        if keys['x2'] and keys['f2']:
            config = self.mode_config.get('暴力').copy()
        if keys['f3']:
            config = self.mode_config.get('凤凰').copy()
        if keys['x1'] and keys['f3']:
            config = self.mode_config.get('飞天').copy()

        if keys['x1'] and keys['f5']:
            config = self.mode_config.get('奇异').copy()
        if keys['x2'] and keys['f5']:
            config = self.mode_config.get('寡妇').copy()

        if keys['f6']:
            config = self.mode_config.get('夜魔').copy()
        if keys['x1'] and keys['f6']:
            config = self.mode_config.get('铁拳').copy()
        if keys['x2'] and keys['f6']:
            config = self.mode_config.get('金刚').copy()

        if keys['x1'] and keys['f7']:
            config = self.mode_config.get('奶妈').copy()
        if keys['x2'] and keys['f7']:
            config = self.mode_config.get('测试').copy()
        if keys['f9']:
            config = self.mode_config.get('蜘蛛').copy()
        if keys['x1'] and keys['f9']:
            config = self.mode_config.get('毒液').copy()
        if keys['f10']:
            config = self.mode_config.get('死侍').copy()


        #打印信息
        if config is not None:
            print(f"{config['name']} ({config['Px']}-{config['Py']}-{config['headshot_pos']}) ({config['lrud'][0]},{config['lrud'][1]},{config['lrud'][2]},{config['lrud'][3]},{config['lrud'][4]}) 爆头距离:{config['headshot_dist']}")

        return config

    #根据瞄准配置获取瞄准状态
    def get_aim_status(self, fire, keys):

        if fire==-1:
            aiming=0
        elif fire==0:
            aiming=keys['shift']==0
        elif fire==1:
            aiming=(keys['lb'] or keys['x1']) and keys['shift']==0
        elif fire==11:
            aiming=(keys['lb'] or keys['rb']) and keys['x1']==0
        elif fire==2:
            aiming=keys['x1']
        elif fire==25:
            aiming=(keys['x2'] or keys['rb'] or keys['lb']) and keys['mb']==0 and keys['shift']==0

        elif fire==6:
            aiming=keys['x1'] or keys['x2']
        elif fire==16:
            aiming=keys['x1'] 
        elif fire==26:
            aiming=keys['lb'] and keys['ctrl']==0

        elif fire==9:
            aiming=keys['shift']==0
        elif fire==19:
            aiming=keys['x1'] and keys['shift']==0 and keys['ctrl']==0
        else:
            aiming=0
            print("错误:无效的瞄准配置")
        return aiming

    #可信度过滤
    def confidence_filter(self, score, mode):
        if (mode['id']==1.5 or mode['name']=='寡妇' or mode['name']=='蜘蛛') and score < 0.6: 
            return True
        else:
            return False

    #执行特殊英雄操作
    def hero_action(self, now, mode, keys, context, executor, macro_ctl):
        if mode['name']=='灵蝶':
            #隐身自瞄常开
            if mode['id']==1 and keys['mb']: #隐身模式
                mode=self.mode_config.get('灵蝶隐身').copy()
            if mode['id']==1.5 and (keys['lb'] or keys['x1']): #短枪模式
                mode=self.mode_config.get('灵蝶').copy()


        if mode['name']=='鹰眼':
            if mode['id']==11 and keys['rb']: 
                mode=self.mode_config.get('鹰眼连射').copy()
                context.reset(now)
            if mode['id']==11.5 and keys['rb']==0: 
                mode=self.mode_config.get('鹰眼').copy()
                context.reset(now)     
            if keys['rb']: #连射模式
                if now-context.last_combo_time>0.05:
                    executor.submit(macro_ctl.hawkeye_L_macro)
                    context.last_combo_time=now

        if mode['name']=='凤凰':
            context.key_mb, toggled = key_toggle(context.key_mb, keys['mb'])
            if toggled is True:
                executor.submit(macro_ctl.phoenix_J_macro) #凤凰女中键跳一下
                print("J")

        if mode['name']=='夜魔':
            #夜魔侠格挡前防止卡住
            context.key_mb, toggled = key_toggle(context.key_mb, keys['mb'])
            if toggled is True:
                executor.submit(macro_ctl.daredevil_R_macro)
                print("R")
            #夜魔侠连招1
            if keys['x1'] and keys['lb'] and keys['mb']==0: 
                if now-context.last_combo_time>0.05:
                    executor.submit(macro_ctl.daredevil_LCRF_macro)
                    #print("LCRF")
                    context.last_combo_time=now
            #夜魔侠连招2
            if keys['x2'] and keys['lb'] and keys['mb']==0: 
                if now-context.last_combo_time>0.05:
                    executor.submit(macro_ctl.daredevil_LCEF_macro)
                    #print("LCEF")
                    context.last_combo_time=now

        if mode['name']=='奶妈':
            if mode['id']==17 and keys['x1']: #x1锁敌
                mode=self.mode_config.get('奶妈锁敌').copy()
                context.reset(now)
            if mode['id']==17.5 and keys['x1']==0: #左键奶人
                mode=self.mode_config.get('奶妈').copy()
                context.reset(now)

        if mode['name']=='蜘蛛':
            #蜘蛛侠按左键就切换近战模式 瞄准速度提升
            if mode['id']==9 and (keys['lb'] or keys['mb']):
                mode=self.mode_config.get('蜘蛛近战').copy()
                context.reset(now)
            if mode['id']==9.5 and (keys['lb']==0 and keys['mb']==0):
                mode=self.mode_config.get('蜘蛛').copy()
                context.reset(now)

            #蜘蛛侠连招1 中键
            if context.spiderman1_key==0 and keys['mb'] and keys['x1']==0: 
                if keys['ctrl']:
                    context.spiderman1_key=1
                    executor.submit(macro_ctl.spiderman_E_macro)
                    #print("E")
                else:
                    context.spiderman1_key=1
                    executor.submit(macro_ctl.spiderman_KR_macro)
                    #print("KR")      
            if context.spiderman1_key==1 and keys['mb']==0:
                context.spiderman1_key=0

            #蜘蛛侠连招2 侧键1
            if context.spiderman2_key==0 and keys['x1']: 
                if keys['lb']: 
                    context.skill_cd=get_spiderman_cd()
                    if context.skill_cd<1: print("技能还在CD中")
                    context.spiderman2_key=1
                    executor.submit(macro_ctl.spiderman_RFKRE_macro)
                    #print("RFKRE")
                # if keys['mb']: #蜘蛛侠连招2
                #     if context.skill_cd>1:
                #         context.spiderman2_key=1
                #         executor.submit(macro_ctl.spiderman_LRFKRE_macro)
                #         print("LRFKRE")
                #     else:
                #         context.spiderman2_key=1
                #         executor.submit(macro_ctl.spiderman_LRFKR_macro)
                #         print("LRFKR")
            if context.spiderman2_key==1 and keys['x1']==0:
                context.spiderman2_key=0

            # #蜘蛛侠连招3 侧键2
            # if context.spiderman3_key==0 and keys['x2']: 
            #     context.spiderman3_key=1
            #     executor.submit(macro_ctl.spiderman_JF_macro)
            # if context.spiderman3_key==1 and keys['x2']==0:
            #     context.spiderman3_key=0


            #蜘蛛侠锁敌
            if keys['ctrl']:
                if now-context.last_ctrl_time>0.1:
                    executor.submit(macro_ctl.spiderman_C_macro)
                    context.last_ctrl_time=now
            
        if mode['name']=='毒液':
            #记录上一次右键按下时间
            context.key_rb, toggled = key_toggle(context.key_rb, keys['rb'])
            if toggled is True:
                context.venom_rb_time = now  # 记录按下时间

            #按住q后左键
            context.key_ctrl, toggled = key_toggle(context.key_ctrl, (keys['x1'] and keys['ctrl']) and now - context.venom_rb_time > 3.18)
            if toggled is True:
                executor.submit(macro_ctl.venom_L)
                print('毒液放大')

            #检测生命
            context.venom_health_count+=1
            if context.venom_health_count%3==0:
                if get_venom() and keys['x1'] and keys['tab']==0:
                    executor.submit(macro_ctl.venom_health)

        if mode['name']=='死侍':
            context.key_x1, toggled = key_toggle(context.key_x1, keys['x1'] and keys['mb'])
            if toggled is True:
                executor.submit(macro_ctl.deadpool_upgrade_macro)
                print('升级')

        return mode
        

    #判断目标是否符合资格
    def target_qualify(self, mode, xywhd, model_x, model_y):
        if xywhd[3]>0.97*model_y: #防止锁大树
            return True
        if mode['id']==9.5: #蜘蛛侠近战 目标太小 忽略
            if xywhd[4]>15:
                return True
        return False

    #计算目标优先级
    def get_target_priority(self, mode, xywhd, model_x, model_y):
        if mode['id']==17:#奶妈特调
            target_priority=(xywhd[0]-model_x/2)**2 + (xywhd[1]+55-model_y/2)**2
        elif mode['name']=='金刚':#金刚特调
            target_priority=xywhd[4]
        else:
            target_priority=(xywhd[0]+(mode['Px']*xywhd[2])-model_x/2)**2 + (xywhd[1]-(mode['Py']*xywhd[3])-model_y/2)**2

        return target_priority

    #获取特殊偏移x
    def get_special_Px(self, mode, keys, shift_Px):
        special_Px=shift_Px


        return special_Px

    #根据距离调整x
    def change_Px_by_dist(self, mode, dist):
        if mode['name']=='铁拳' or mode['name']=='金刚':
            if dist<=4:
                return 0.2
            elif dist>=7:
                return mode['Px']
            else:
                # 线性插值
                ratio = (dist - 3) / 3
                return 0.2 - ratio * (0.2 - mode['Px'])

        else:
            return mode['Px'] 


    #获取特殊偏移y
    def get_special_Py(self, mode, keys, shift_Py):
        special_Py=shift_Py

        if mode['name']=='鹰眼' and keys['shift']: #鹰眼锁身体
            special_Py=0.44
        if mode['name']=='默认' and keys['rb']: #星爵右键
            special_Py=0.2
        if mode['name']=='默认' and keys['shift']: #海拉锁头
            special_Py=0.37
        if mode['name']=='默认' and keys['mb']: #海拉中键
            special_Py=0.2
        if mode['name']=='凤凰' and keys['shift']: #凤凰锁头
            special_Py=0.4
        if mode['name']=='凤凰' and keys['mb']: #凤凰砸地
            special_Py=-0.6
        if mode['name']=='寡妇' and keys['lb']: #黑寡妇左键
            special_Py=0.4
#        if mode['name']=='毒液' and keys['mb']: #毒液中键
#            special_Py=0.15
        if mode['name']=='暴力' and (keys['rb'] or keys['mb'] or keys['shift']): # 暴力锁头 右键按下时瞄准中间 海拉默认右键 
            special_Py=0.2 
        if mode['name']=='死侍' and keys['shift']:  
            special_Py=0.4 

        return special_Py

    #根据目标信息判断是否允许移动
    def is_movable(self, keys, mode, final_x, final_y, target):
        allow=False

        lrud=mode['lrud']

        #计算系数
        factorX=final_x/(target[2]/2)
        factorY=final_y/(target[2]/2)

        if mode['name']=='凤凰' and keys['mb']: #凤凰模式
            if lrud[0]<factorX<lrud[1] and abs(factorY)<10:
                allow=True

        if mode['name']=='寡妇' and (keys['lb'] and not keys['rb']): #黑寡妇
            if abs(factorX)<10 and abs(factorY)<10:
                    allow=True

        if lrud[4]:
            if target[4]<6.5:
                allow=True

        
        if lrud[0]<factorX<lrud[1] and lrud[2]<factorY<lrud[3]:
            allow=True

        
        return allow

    #执行特殊功能操作
    def special_action(self, now, mode, keys, context, executor, macro_ctl):
        if mode['name']=='奇异':
            if context.strange_opendoor==0 and (keys['x1'] or keys['x2']):
                if get_strange_countdown():
                    context.strange_opendoor=1
                    context.strange_opendoor_time=now
            if context.strange_opendoor==1 and now-context.strange_opendoor_time>5.15 and keys['x1'] and not keys['mb']:
                print('开门5.15')
                executor.submit(macro_ctl.strange_opendoor)
                context.strange_opendoor=2
            if context.strange_opendoor==1 and now-context.strange_opendoor_time>5.20 and keys['x1'] and keys['mb']:
                print('开门')
                executor.submit(macro_ctl.strange_opendoor)
                context.strange_opendoor=2
            return True

        #防误触
        if (mode['name']=='蜘蛛' or mode['name']=='寡妇' or context.afk) and keys['alt'] and keys['tab']:
            context.afk=0
            context.aimbot_enable=False
            mode['id']=0
            mode['name']="关闭"
            print("防误触开启")

        #挂机
        context.key_insert, toggled = key_toggle(context.key_insert, keys['insert'] and keys['x1'])
        if toggled is True:
            context.afk=not context.afk
            if context.afk:
                context.last_afk_time=now 
                print("开始挂机")
            else:
                print("结束挂机")

        #挂机
        if context.afk:
            if now - context.last_afk_time < 2:
                return True  
            context.last_afk_time=now
            executor.submit(macro_ctl.afk_macro)
            return True

        #长按麦克风
        if keys['f7'] and not keys['x1'] and not keys['x2'] :
            print('按下I键')
            executor.submit(macro_ctl.press_I)

        
        #平滑
        context.key_f12, toggled = key_toggle(context.key_f12, keys['f12'])
        if toggled is True:
            mode['smooth'] = not mode['smooth']
            if mode['smooth']:
                print("打开平滑")
            else:
                print("关闭平滑")

        #锁头
        context.key_x2, toggled = key_toggle(context.key_x2, keys['x2'])
        if toggled is True:
            mode['headshot'] = not mode['headshot']
            if mode['headshot']:
                print("打开锁头")
            else:
                print("关闭锁头")
            if mode['name']=='测试':
                if mode['id']==27:
                    mode['id']=27.5
                    print(27.5)
                    mode['headshot']=0
                else:
                    mode['id']=27
                    print(27)
                    mode['headshot']=0

        #关闭自瞄
        if keys['delete']:
            context.aimbot_enable=False
            mode['id']=0
            mode['name']="关闭"
            print("aimbot已关闭")
        if not context.aimbot_enable:
            time.sleep(0.1)
            return True

          
        #获取模型训练图片
        if context.get_train_pic: 
            if self.get_aim_status(mode['fire'],keys):
                if now-context.last_get_picture_time>2:
                    executor.submit(macro_ctl.nvidia_capture)
                    context.last_get_picture_time=now    
        return False
   


    #debug
    def debug_action(self, mode, keys, context, model_x, model_y):
        #显示线程
        context.key_f11, toggled = key_toggle(context.key_f11, keys['f11'])
        if toggled is True:
            context.show_view=not context.show_view
            if context.show_view:
                if context.display_thread is None:
                    context.display_thread = DisplayThread(window_size=(int(model_x), int(model_y)))
                    context.display_thread.start()
                    print("显示线程已启动")
            else:
                if context.display_thread is not None:
                    context.display_thread.stop()
                    context.display_thread.join()
                    context.display_thread = None
                    print(" 显示线程已停止")

        
        if keys['up']:
            mode['Py']=change_value("y偏移",mode['Py'],0.01)
        if keys['down']:
            mode['Py']=change_value("y偏移",mode['Py'],-0.01)
        if keys['right']:
            #move_time_threshold=change_value("移动补偿阈值",move_time_threshold,0.01)
            #mode['move_fix_adjust']=change_value("移动补偿修正",mode['move_fix_adjust'],0.01)
            mode['Px']=change_value("x偏移",mode['Px'],0.01)
        if keys['left']:
            #move_time_threshold=change_value("移动补偿阈值",move_time_threshold,-0.01)
            #mode['move_fix_adjust']=change_value("移动补偿修正",mode['move_fix_adjust'],-0.01)
            mode['Px']=change_value("x偏移",mode['Px'],-0.01)
        if keys['next']:
            mode['Sx']=change_value("速度x",mode['Sx'],-0.01)
            mode['Sy']=change_value("速度y",mode['Sy'],-0.01,False)
            #mode['headshot_dist']=change_value("爆头距离",mode['headshot_dist'],0.5)
        if keys['prior']:
            mode['Sx']=change_value("速度x",mode['Sx'],0.01)
            mode['Sy']=change_value("速度y",mode['Sy'],0.01,False)
            #mode['headshot_dist']=change_value("爆头距离",mode['headshot_dist'],-0.5)
        
        #移动补偿
        context.key_0, toggled = key_toggle(context.key_0, keys['0'])
        if toggled is True:
            context.move_fix=not context.move_fix
            if context.move_fix:
                print("开启移动补偿")
            else:
                print("关闭移动补偿")

        #距离补偿
        context.key_9, toggled = key_toggle(context.key_9, keys['9'])
        if toggled is True:
            context.dist_fix=not context.dist_fix
            if context.dist_fix:
                print("开启距离补偿")
            else:
                print("关闭距离补偿")

        #延迟补偿
        context.key_8, toggled = key_toggle(context.key_8, keys['8'])
        if toggled is True:
            context.delay_fix=not context.delay_fix
            if context.delay_fix:
                print("开启延迟补偿")
            else:
                print("关闭延迟补偿")

        #获取训练图片
        context.key_7, toggled = key_toggle(context.key_7, keys['7'])
        if toggled is True:
            context.get_train_pic=not context.get_train_pic
            if context.get_train_pic:
                print("开启获取截图")
            else:
                print("关闭获取截图")

