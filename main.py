import cv2
import time
import random
import numpy as np


#线程池
from concurrent.futures import ThreadPoolExecutor
#配置文件
from utils.config_watcher import cfg
print('模型初始化')
#模型初始化
from utils.utils import Predictor
print('模型初始化结束')
#画面预处理
from utils.utils import letterbox
#画面截图
from utils.capture import capture
#鼠标平滑器
from utils.smooth_mouse import *
#宏配置
from utils.macro_controller import MacroController
#模式配置
from utils.mode_manager import ModeManager
#模式上下文
from utils.mode_manager import ModeContext
#游戏数学计算
from utils.game_math import *

#旧画面捕捉
#from utils.grabscreen import grab_screen
#键盘码
#from utils.keybinds import *
#叠加层
#from utils.overlay import SkillOverlay
#显卡使用率
#from utils.gpu_usage import *

#主函数
def find_target():
    #在函数开头加入进程伪装
    import ctypes
    #修改控制台标题
    kernel32 = ctypes.windll.kernel32
    #从预设的伪装列表中随机选择
    fake_titles = ["svchost.exe", "RuntimeBroker.exe", "taskhostw.exe", "dllhost.exe", "conhost.exe"]
    title = random.choice(fake_titles)
    kernel32.SetConsoleTitleW(title)

    # 初始化TRT模型
    print("开始加载模型")
    enemy_pred = Predictor(engine_path=str( './enemy320_v2.trt'))
    ally_pred = Predictor(engine_path=str( './ally.trt'))
    print("模型加载完毕")

    #初始化宏控制器，0为启用雷蛇鼠标控制 1为罗技 2为手柄
    macro_ctl=MacroController(cfg.mouse_driver)
    #初始化模式配置
    mode_mgr=ModeManager()
    #初始化上下文
    ctx=ModeContext(time.time())
    #创建线程池，全局只创建一次 最多同时运行任务 
    executor=ThreadPoolExecutor(max_workers=30)
    #模型输入尺寸 
    model_x,model_y=cfg.model_x,cfg.model_y 
    #平滑
    smoothX,smoothY=SmoothMouse(),SmoothMouse()
    #实验性东西
    debug=cfg.debug #debug模式
    #ai每秒循环速度控制
    fps_control=cfg.fps_control #ai速率控制
    frame_interval=1.0/cfg.capture_fps #每帧时间
    
    #初始参数
    mode=mode_mgr.mode_config.get('星爵').copy()
    #主循环
    while True:
        #循环开始时间
        now=time.time()
        #按键检测分频
        if debug:
            keys=macro_ctl.get_keys_all()
        else:
            if now-ctx.last_key_time>0.1: #每0.1秒
                keys=macro_ctl.get_keys_more()    
                ctx.last_key_time=now
            else:
                keys=macro_ctl.get_keys_less()
        
        #获取模式配置
        new_mode = mode_mgr.get_mode_config(keys)

        #切换模式
        if new_mode:
            mode=new_mode
            #重置上下文
            ctx.reset(now)
        
        #执行英雄操作
        mode=mode_mgr.hero_action(now,mode,keys,ctx,executor,macro_ctl)

        #执行功能操作
        if mode_mgr.special_action(now,mode,keys,ctx,executor,macro_ctl,fps_control,frame_interval): continue

        #调试配置
        if debug:
            if mode_mgr.debug_action(mode,keys,ctx,model_x,model_y): continue
          
        #获取瞄准状态
        aiming=mode_mgr.get_aim_status(mode['fire'],keys)

        
        
        #截图
        img0=capture.get_new_frame()
        #输入图像为空跳过
        if img0 is None: continue 
        #图像没有变化跳过 
        curr_check=img0.ravel()[:1000] #极简对比逻辑：拉平数组取前1000个值
        if ctx.prev_check is not None and np.array_equal(curr_check, ctx.prev_check): continue              
        ctx.prev_check = curr_check.copy()
        #截图遮蔽
        cv2.rectangle(img0, (0, 126), (25, 426), (255, 0, 0),  -1 )
        #可视化
        if ctx.show_view: resized_display = cv2.resize(img0, (int(model_x), int(model_y)))
        #图像预处理 缩放后的图像img、缩放比例ratio和填充的像素值dwdh
        img, ratio, dwdh = letterbox(img0, new_shape=(model_x, model_y)) 
        #开始推理 奶妈使用另外的模型
        if mode['id']==17:
            data = ally_pred.infer(img)
        else:
            data = enemy_pred.infer(img)
        infer_delay=(time.time()-now)*1000
        #推理延迟过高 弃用
        if infer_delay>ctx.delay_threshold: 
            print('   延迟太高 丢弃   ')
            continue

        
        #延迟修正
        if ctx.delay_fix:
            if ctx.last_round_time is None:
                ctx.last_round_time=time.time()
                delay_factor=1
            else:
                ctx.this_round_time=time.time()
                round_delay=(ctx.this_round_time-ctx.last_round_time)*1000
                ctx.last_round_time=ctx.this_round_time
                round_delay_factor=min(round_delay/10,4)
                infer_delay_factor=-0.02*infer_delay+1.162
                delay_factor=round_delay_factor*infer_delay_factor
        else:
            delay_factor=1


        #数量 坐标 置信度 索引
        num, final_boxes, final_scores, final_cls_inds  = data 
        #如果识别到目标
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
            target_xywhd_list = []
            target_distance_list = []

            #遍历所有检测目标
            for i in range(len(final_boxes)):
                box = final_boxes[i]
                score = final_scores[i]
                #可信度过滤
                if mode_mgr.confidence_filter(score,mode): continue
                #将边界框的坐标格式从(左上角+右下角)转换为(中心点+宽高)+深度
                x1, y1, x2, y2 = box
                xywhd=[(x1+x2)/2, (y1+y2)/2, (x2-x1), (y2-y1), 0]

                #估算目标距离
                dist=get_approx_distance(xywhd[2],xywhd[3])
                percent_x=xywhd[2]/model_x
                #如果触碰到上下边界，则特殊设置 
                if xywhd[1]+xywhd[3]/2>(model_y-3) or xywhd[1]-xywhd[3]/2<3:
                    if percent_x<=0.49:
                        dist=4
                    elif percent_x<=0.57:
                        dist=3
                    else:
                        dist=2
                xywhd[4]=dist

                #可视化
                if ctx.show_view:
                    #绘制边界框
                    cv2.rectangle(resized_display, (int(x1), int(y1)), (int(x2),int(y2)), (0, 255, 0), 1)
                    # 绘制文本
                    #text = f"{(xywhd[0]- model_x/2)/(xywhd[2]/2):.1f},{(xywhd[1]- model_y/2- mode['Py'] * xywhd[3])/(xywhd[2]/2):.1f}"
                    #text = f'{round(xywhd[2]):.0f},{round(xywhd[3]):.0f}' #目标上下占比\
                    text = f'{xywhd[4]:.2f}' #目标上下占比
                    #text = f'{score:.2f}' #置信度
                    #获取文本尺寸
                    (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    # 判断上方是否有足够空间显示文本
                    if y1 - text_height - 10 > 0:  # 上方有足够空间
                        #上文本背景
                        cv2.rectangle(resized_display, (int(x1), int(y1) - text_height - 5),(int(x1) + text_width, int(y1) - 5),(0, 255, 0), -1)
                        #上文本内容
                        cv2.putText(resized_display, text,(int(x1), int(y1) - 7),cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 0, 0), 1)
                    else:
                        #下文本背景
                        cv2.rectangle(resized_display, (int(x1), int(y2) + 5),(int(x1) + text_width, int(y2) + text_height + 5),(0, 255, 0), -1)
                        #下文本内容
                        cv2.putText(resized_display, text,(int(x1), int(y2) + text_height + 5),cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 0, 0), 1)
                    #瞄准点
                    if mode['id']==17:#奶妈特调
                        cv2.circle(resized_display, (int(xywhd[0]-mode['Px']*xywhd[2]), int(xywhd[1]+mode['Py'])), 2, (0, 0, 255), -1)
                    else:
                        cv2.circle(resized_display, (int(xywhd[0]+mode['Px']*xywhd[2]), int(xywhd[1]-mode['Py']*xywhd[3])), 1, (0, 0, 255), -1)

                #目标距离计算
                if mode['id']==17:#奶妈特调
                    target_distance=(xywhd[0] - model_x/2)**2 + (xywhd[1]+ mode['Py'] - model_y/2)**2
                else:
                    target_distance=(xywhd[0] - model_x/2)**2 + (xywhd[1]- (mode['Py'] * xywhd[3])- model_y/2)**2

                #特殊目标处理
                if xywhd[3]>0.97*model_y: #防止锁大树
                    continue
                elif mode['name']=='毒液': #跳过远距离的敌人
                    if xywhd[3]*xywhd[2]<1100:
                        continue
                elif mode['id']==9.5: #蜘蛛侠
                    if xywhd[3]*xywhd[2]<4000:
                        continue

                target_xywhd_list.append(xywhd)
                target_distance_list.append(target_distance)
        
        
        #选取最近目标
        if num>0 and target_xywhd_list: 
            min_index=target_distance_list.index(min(target_distance_list))
            target=target_xywhd_list[min_index]
            target_x=target[0]
            target_y=target[1]
            target_w=target[2]
            target_h=target[3]
            target_d=target[4]
            

            #寡妇自动扳机
            if mode['name']=='寡妇':
                l=(target_x-target_w/2)
                r=(target_x+target_w/2)
                t=(target_y-0.95*target_h/2)
                b=(target_y+0.95*target_h/2)
                if l<model_x/2<r and t<model_y/2<b:
                    if keys['rb']==0 and keys['mb']==0 and keys['shift']==0:
                        executor.submit(macro_ctl.trigger_key)

            
            #距离补偿
            if ctx.dist_fix:
                #估算速度系数
                dist_factor=get_dist_factor(target_d,ctx.dist_standard_speed)
            else:
                dist_factor=1

            
            #移动补偿
            if ctx.move_fix: 
                move_fix_value,ctx.move_time=get_move_fix_value(now, keys['a'], keys['d'], target_d, ctx.move_time, ctx.move_time_threshold)                                   
                #根据角色修正
                move_fix_value*=mode['move_fix_adjust']

                if mode['id']==9: #蜘蛛侠 宽度大于60 修正补偿
                    if percent_x>0.3:
                        move_fix_value*=0.5
            else:
                move_fix_value=0
            
             
            #最终x向量
            final_x=target_x-model_x/2+mode['Px']*target_w+move_fix_value

            #Y动态调整
            shift_Py=mode['Py'] #提前写在这里 防止自适应锁头不生效
            #自适应锁头 平滑锁头位置
            if mode['headshot']: #and target_w<target_h: 
                shift_Py=smooth_headshot_position(target_d,mode['headshot_dist'],mode['headshot_pos'],mode['Py']) 
            #获取特殊Y向量
            shift_Py=mode_mgr.get_special_Py(mode,keys,shift_Py)
            #最终y向量
            final_y=target_y-model_y/2-shift_Py*target_h


            #奶妈特殊Y向量调整
            if mode['id']==17:
                if target_w>=0.6*model_x: #血条宽度太宽 
                    continue
                elif model_x/2<=target_w<0.6*model_x:
                    shift_Py=mode['Py']-(model_x/2-target_w)*2
                elif target_w<model_x/2:
                    shift_Py=mode['Py']
                final_y=target_y-model_y/2+shift_Py

            #计算系数
            factorX=final_x/(target_w/2)
            factorY=final_y/(target_w/2)

            #发送输入
            if aiming:
                if debug:
                    if mode['id']==27.5:#测试
                        #final_x=target_x-model_x/2-100
                        final_y=target_y-model_y/2-100
                    if mode['id']==27:
                        #final_y=0
                        final_x=0

                move_x,move_y=final_x * mode['Sx'] * delay_factor * dist_factor , final_y * mode['Sy'] * delay_factor * dist_factor
            
                if mode['id']==9: #蜘蛛侠 宽度大于60 直接应用原速度
                    if percent_x>0.3:
                        move_x,move_y=final_x * delay_factor * dist_factor , final_y * delay_factor * dist_factor

                if mode['name']=='测试':
                    if ctx.test_aim==0:
                        macro_ctl.mouse_driver_move(int(move_x),int(move_y))
                        ctx.test_aim=1
                        print(final_x,move_x,mode['Sx'])
                        print(move_x)
                        continue
                    else:
                        continue

                move_x,move_y=smooth_poccess(move_x, move_y, target_d, factorX, factorY, mode['smooth'], target, smoothX, smoothY)

                #方式一
                #距离小于8 不管身位了 也不平滑了
                #距离8以上 平滑

                
                #瞄准疲劳
                #if aim_tired:
                #    if not aiming:
                #        aiming=not aiming
                #        start_aim_time=now

                #    if now-start_aim_time>3:
                #        #print("瞄准超过3秒")
                #        random_aim_change=last_random_aim+(random.random()*2-1)*0.1
                #        random_aim_change = max(-1, min(1, random_aim_change))
                #        move_x+=random_aim_change*target_w/4
                #        last_random_aim=random_aim_change
                      

                #判断是否允许移动
                if mode_mgr.is_movable(keys,mode,factorX,factorY):
                    macro_ctl.mouse_driver_move(move_x,move_y)
            else:
                #如果识别到敌人 却没有开锁 重置平滑
                if mode['smooth']==1:
                    smoothX.clean()
                    smoothY.clean()

                #瞄准疲劳
                #if aim_tired and aiming:
                #    aiming=not aiming
                #    last_random_aim=0

                if debug:
                    if mode['name']=='测试' and ctx.test_aim==1:
                        ctx.test_aim=0

        #数据统计
        ctx.total_frame+=1
        ctx.total_infer_delay+=infer_delay
        if now-ctx.last_print_time>=1.0:
            ctx.fps=ctx.total_frame/(now-ctx.last_print_time)
            avg_infer_delay=round(ctx.total_infer_delay/ctx.total_frame)
            ctx.total_infer_delay=0
            ctx.total_frame=0
            ctx.last_print_time=now

            print(f"{'录制中 ' if ctx.get_train_pic else ''}"
                  f"m{mode['id']} "
                  f"{'Debug ' if debug else ''}"
                  f"{'滑' if mode['smooth'] else ''}"
                  f"{'锁' if mode['headshot'] else ''}"
                  f"{' '}"
                  f"{ctx.fps:>3.0f}({avg_infer_delay}) "
                  f"{'延' if ctx.delay_fix else ''}"
                  f"{'距' if ctx.dist_fix else ''}"
                  f"{'移' if ctx.move_fix else ''}"
                  f"{f'延迟补偿{delay_factor:.1f}' if ctx.delay_fix else ''}")
   
            #游戏提示
            if ctx.tip%12==0: 
                print("")
                print("   对面谁的大招需要提防")
                print("   自己的大招要怎么开")
                print("")
            ctx.tip+=1
        
         #可视化
        if ctx.show_view:
            cv2.putText(resized_display, f"mode:{mode['id']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            ctx.display_thread.update_image(resized_display)

if __name__ == '__main__':
    try:
        find_target()
    finally:
        #确保程序退出时释放鼠标资源
        print('end')