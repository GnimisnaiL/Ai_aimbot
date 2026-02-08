#main.py
import cv2
import time
import random
import numpy as np
import mss

#线程池
from concurrent.futures import ThreadPoolExecutor
#配置文件
from utils.config_watcher import cfg
print('模型初始化开始')
#模型初始化
from utils.utils import Predictor
print('模型初始化结束')
#画面预处理
from utils.utils import letterbox
from utils.utils import letterbox_fast426
#画面截图
from utils.capture import capture
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
    #ally_pred = Predictor(engine_path=str( './ally.trt'))
    print("模型加载完毕")

    #模型输入尺寸 
    model_x,model_y=cfg.model_x,cfg.model_y 
    #初始化宏控制器，0为启用雷蛇鼠标控制 1为罗技 2为手柄
    macro_ctl=MacroController(cfg.mouse_driver)
    #debug模式
    debug=cfg.debug 
    #初始化模式配置
    mode_mgr=ModeManager()
    #初始化上下文
    ctx=ModeContext(time.time())
    #创建线程池，全局只创建一次 最多同时运行任务 
    executor=ThreadPoolExecutor(max_workers=30)
    
    #初始参数
    mode=mode_mgr.mode_config.get('默认').copy()

    #主循环
    while True:
        #数据统计
        if time.time()-ctx.last_print_time>=1.0 and mode['id']!=0:
            if ctx.total_frame!=0:
                avg_infer_delay=round(ctx.total_infer_delay/ctx.total_frame*1000)
            
            print(f"{'挂机中 ' if ctx.afk else ''}"
                  f"{'录制中 ' if ctx.get_train_pic else ''}"
                  f"{'Debug ' if debug else ''}"
                  f"m{mode['id']}{mode['name']} "
                  f"{'平滑' if mode['smooth'] else ''}"
                  f"{'爆头' if mode['headshot'] else ''}"
                  f"{'近吸' if mode['lrud'][4] else ''}"
                  f"{' '}"
                  f"{ctx.total_frame:>3.0f}({avg_infer_delay if ctx.total_frame!=0 else '-'}) "
                  #f"{'延' if ctx.delay_fix else ''}"
                  #f"{'距' if ctx.dist_fix else ''}"
                  #f"{'移' if ctx.move_fix else ''}"
                  f"{f'延迟补偿{delay_factor:.1f}' if ctx.delay_fix else ''}")
   
            #游戏提示
            if ctx.tip%12==0: 
                print("")
                print("   对面谁的大招需要提防")
                print("   自己的大招要怎么开")
                print("")
                ctx.tip+=1

            ctx.tip+=1
            ctx.total_frame=0
            ctx.total_infer_delay=0
            ctx.last_print_time=time.time()

        #截图
        img0=capture.get_new_frame()
        if img0 is None: 
            print('获取图像为空')
            continue 
        else:
            #图像没有变化跳过
            curr_check=img0.ravel()[90000:92000] #极简对比逻辑
            if ctx.prev_check is not None and np.array_equal(curr_check, ctx.prev_check): 
                continue              
            ctx.prev_check=curr_check

        #图片开始处理时间
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
        new_mode=mode_mgr.get_mode_config(keys)
        #切换模式
        if new_mode:
            mode=new_mode
            #重置上下文
            ctx.reset(now)
        
        #执行英雄操作
        mode=mode_mgr.hero_action(now,mode,keys,ctx,executor,macro_ctl)
        #执行功能操作
        if mode_mgr.special_action(now,mode,keys,ctx,executor,macro_ctl): continue
        #调试配置
        if debug and mode_mgr.debug_action(mode,keys,ctx,model_x,model_y): continue
        #获取瞄准状态
        aiming=mode_mgr.get_aim_status(mode['fire'],keys)


        #截图遮蔽
        #cv2.rectangle(img0, (0, 126), (25, 426), (255, 0, 0),  -1 )
        #可视化
        if ctx.show_view: resized_display=cv2.resize(img0, (int(model_x), int(model_y)))

        #图像预处理 缩放后的图像img、缩放比例ratio和填充的像素值dwdh
        #img, ratio, dwdh=letterbox(img0, new_shape=(model_x, model_y))
        img, ratio, dwdh=letterbox_fast426(img0)
        #奶妈使用另外的模型
        if mode['id']==17:
            data = ally_pred.infer(img)
        else:
            data = enemy_pred.infer(img)

        #推理延迟过高 弃用  
        infer_delay=time.time()-now
        if infer_delay>ctx.delay_threshold: 
            print('延迟太高,丢弃')
            continue

        #数据统计
        ctx.total_frame+=1
        ctx.total_infer_delay+=infer_delay
        
        #延迟修正
        if ctx.delay_fix:
            if ctx.last_round_time is None:
                ctx.last_round_time=time.time()
                delay_factor=1
            else:
                ctx.this_round_time=time.time()
                round_delay=(ctx.this_round_time-ctx.last_round_time)*1000
                ctx.last_round_time=ctx.this_round_time
                if infer_delay<10:
                    #round_delay_factor=min(round_delay/10,4)
                    delay_factor=round_delay/10
                else:
                    delay_factor=1
        else:
            delay_factor=1


        #数量 坐标 置信度 索引
        num, final_boxes, final_scores, final_cls_inds=data 
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
            target_priority_list = []

            #遍历所有检测目标
            for i in range(len(final_boxes)):
                box = final_boxes[i]
                score = final_scores[i]
                #可信度过滤
                if mode_mgr.confidence_filter(score,mode): 
                    continue
                #将边界框的坐标格式从(左上角+右下角)转换为(中心点+宽高)+深度
                x1, y1, x2, y2 = box
                xywhd=[(x1+x2)/2, (y1+y2)/2, (x2-x1), (y2-y1), 0]

                #估算目标距离
                xywhd[4]=get_approx_distance(xywhd,model_x,model_y)

                #可视化
                if ctx.show_view:
                    #绘制边界框
                    cv2.rectangle(resized_display, (int(x1), int(y1)), (int(x2),int(y2)), (0, 255, 0), 1)
                    # 绘制文本
                    #text = f"{(xywhd[0]-model_x/2)/(xywhd[2]/2):.1f},{(xywhd[1]- model_y/2- mode['Py'] * xywhd[3])/(xywhd[2]/2):.1f}"
                    #text = f"{xywhd[0]-model_x/2:.0f},{xywhd[1]-model_x/2:.0f}" #目标上下占比\
                    text = f'{xywhd[4]:.2f},{xywhd[2]/xywhd[3]:.2f}' #距离
                    #text = f'{score:.2f}' #置信度
                    #text = f'{xywhd[3]/model_y:.2f}' #高度占比
                    #text = f'{xywhd[2]/model_x:.2f}' #宽度占比
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

                #目标优先级计算
                target_priority=mode_mgr.get_target_priority(mode,xywhd,model_x,model_y)

                #特殊目标处理 判断是否加入目标队列
                if mode_mgr.target_qualify(mode,xywhd,model_x,model_y): 
                    continue

                target_xywhd_list.append(xywhd)
                target_priority_list.append(target_priority)
        
        
        #选取最高优先级目标
        if num>0 and target_xywhd_list: 
            min_index=target_priority_list.index(min(target_priority_list))
            target=target_xywhd_list[min_index]

            #寡妇自动扳机
            if mode['name']=='寡妇':
                l=(target[0]-target[2]/2)
                r=(target[0]+target[2]/2)
                t=(target[1]-0.95*target[3]/2)
                b=(target[1]+0.95*target[3]/2)
                if l<model_x/2<r and t<model_y/2<b:
                    if keys['rb']==0 and keys['mb']==0 and keys['shift']==0:
                        executor.submit(macro_ctl.trigger_key)

            
            #距离补偿
            if ctx.dist_fix:
                #估算速度系数
                dist_factor=get_dist_factor(target[4],ctx.dist_standard_speed)
                #print(dist_factor)
                #黑寡妇开镜修正
                if mode['name']=='寡妇' and keys['rb']:
                    dist_factor=1
            else:
                dist_factor=1

            
            #移动补偿
            if ctx.move_fix: 
                move_fix_value,ctx.move_time,ctx.last_move_direction=get_move_fix_value(now, keys['a'], keys['d'], target[4], ctx.move_time, ctx.move_time_threshold,ctx.last_move_direction)                                   
                #根据角色修正
                move_fix_value*=mode['move_fix_adjust']
            else:
                move_fix_value=0
            
            #X调整
            #近身调整x
            shift_Px=mode_mgr.change_Px_by_dist(mode,target[4])
            shift_Px=mode_mgr.get_special_Px(mode,keys,shift_Px)
            #最终x向量
            final_x=move_to(target[0]+shift_Px*target[2],model_x/2)+move_fix_value


            #Y调整
            #自适应锁头锁头位置
            shift_Py=get_headshot_position_by_dist(mode,target[4],mode['Py']) 
            #如果目标宽比高大 则只锁中心
            #if target[2]>target[3]:
            #    shift_Py=0
            #获取特殊Y向量
            shift_Py=mode_mgr.get_special_Py(mode,keys,shift_Py)
            #最终y向量
            final_y=move_to(target[1]-shift_Py*target[3],model_y/2)



            #奶妈特殊Y向量调整
            if mode['id']==17:
                if target[2]>=0.6*model_x: #血条宽度太宽 
                    continue
                elif model_x/2<=target[2]<0.6*model_x:
                    shift_Py=mode['Py']-(model_x/2-target[2])*2
                elif target[2]<model_x/2:
                    shift_Py=mode['Py']
                final_y=target[1]-model_y/2+shift_Py


            #发送输入
            if aiming:
                # if debug:
                #     if mode['id']==27.5:#测试
                #         final_x=target[0]-model_x/2-100
                #         #final_y=target[1]-model_y/2-100
                #     if mode['id']==27:
                #         final_y=0
                #         #final_x=0

                            

                # if mode['name']=='测试':
                #     if ctx.test_aim==0:
                #         print("敌人位置",target[0]-model_x/2,"移动距离",round(move_x))
                #         macro_ctl.mouse_driver_move(int(move_x),int(move_y))
                #         ctx.test_aim=1
                #         #print(final_x,move_x,mode['Sx'])
                #         #print(move_x)
                #         continue
                #     else:
                #         continue

                ##像素值到鼠标移动值,平滑处理
                move_x,move_y=smooth_poccess(final_x, final_y, target, mode['Sx'], mode['Sy'], delay_factor, dist_factor, mode['smooth'])

                #判断是否允许输入
                if mode_mgr.is_movable(keys, mode, final_x, final_y, target):
                    macro_ctl.mouse_driver_move(move_x, move_y)
                

                #方式一
                #距离小于8 不管身位了 也不平滑了
                #距离8以上 平滑

                

                #鼠标输入滞后
                
                #冷启动 

                #随距离变化range

                # #ai速率控制
                #print("敌人位置",target[0]-model_x/2,"移动距离",round(move_x))

                
            #else:


                # if debug:
                #     if mode['name']=='测试' and ctx.test_aim==1:
                #         ctx.test_aim=0


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