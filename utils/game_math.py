import time

#给指定坐标 计算中心值到该坐标的向量
def move_to(x, cx):
    return x-cx


#根据高度和 宽度 估算角色距离 
def get_approx_distance(xywhd, model_x, model_y):
    #体型修正 分母大于1
    aspect = xywhd[2]/max(xywhd[3], 1)
    #if aspect>0.6:
    #    print("体型异常，宽高比为",aspect)
    fix_aspect = max(0.20, min(0.60, aspect))
                
    #基础距离（高度主导）
    base=1100/max(xywhd[2]/fix_aspect, 1)
    #输出位 aspect ≈ 0.38，作为中性参考
    correction=1+0.9*(fix_aspect-0.38)
    estimatedTargetDistance=base*correction

    percent_x=xywhd[2]/model_x
    #如果触碰到上下边界，则特殊设置 
    if xywhd[1]+xywhd[3]/2>(model_y-3) or xywhd[1]-xywhd[3]/2<3:
        if percent_x<=0.49:
            estimatedTargetDistance=4
        elif percent_x>=0.57:
            estimatedTargetDistance=2
        else:
            estimatedTargetDistance=-25*percent_x+16.25
            #estimatedTargetDistance=166.67*(percent_x**2)-195*percent_x+58.83
    

    return estimatedTargetDistance

#计算速度距离补偿系数
def get_dist_factor(estimatedTargetDistance, standard_dist_speed):
    return ((8.2/estimatedTargetDistance)+3.5)/standard_dist_speed

#计算移动补偿值
def get_move_fix_value(now, a_pressed, d_pressed, dist, move_time, move_time_threshold, last_move_direction):
    """
    计算移动修正值
    
    参数:
    a_pressed: A键是否按下
    d_pressed: D键是否按下
    dist: 距离参数
    move_fix_time: 上次修正时间
    now: 当前时间
    move_time_threshold: 时间阈值（需要在外部定义）
    
    返回:
    修正值
    """
    elapsed_time = now - move_time
    # 同时按A和D，或者都不按
    if (a_pressed == 0 and d_pressed == 0) or (a_pressed and d_pressed):
        return 0,now,0
    
    # 只按A键
    elif a_pressed and not d_pressed:
        if last_move_direction==2:
            return 0,now,0
        if elapsed_time > move_time_threshold:
            return get_correction_value(dist),move_time,1
        else:
            return 0,move_time,1   
              
    # 只按D键
    elif d_pressed and not a_pressed:
        if last_move_direction==1:
            return 0,now,0
        if elapsed_time > move_time_threshold:
            return -1 * get_correction_value(dist),move_time,2
        else:
            return 0,move_time,2
        
    # 其他情况（理论上不会执行到这里）
    return 0,now

#计算移动补偿距离修正值
def get_correction_value(estimatedTargetDistance):
    return 150/(estimatedTargetDistance + 1.5)

#根据距离获取锁头位置
def get_headshot_position_by_dist(headshot, dist, headshot_dist, headshot_pos, Py):
    #print(dist)
    if headshot:
        lower = headshot_dist
        upper = headshot_dist+3
        if dist <= lower:
            return headshot_pos
        elif dist >= upper:
            return Py
        else:
            # 线性插值
            ratio = (dist - lower) / (upper - lower)  
            return headshot_pos + ratio * (Py - headshot_pos)
    else:
        return Py


#根据目标体型或者距离 进行速度限制或者平滑
def smooth_poccess(target, final_x, final_y, Sx, Sy, delay_factor, dist_factor, smooth):
    factorX=final_x/(target[2]/2)
    factorY=final_y/(target[2]/2)
    

    #if dist<10:
    #    return move_x,move_y
    
    # if smooth: #平滑1 取上次输出值平滑
    #     if abs(factorX)>2.7: # 平滑左右分界点2.7
    #         move_x=smoothX.update(move_x)
    #     else:
    #         smoothX.update(move_x)
    #     if abs(factorY)>3: # 平滑上下分界点3
    #         move_y=smoothY.update(move_y)     
    #     else:
    #         smoothY.update(move_y)  

    if smooth: #平滑2
        if factorX>2.7:
            final_x=target[2]*1.35
        if factorX<-2.7:
            final_x=-target[2]*1.35

        if factorY>3:
            final_y=target[2]*1.5
        if factorY<-3:
            final_y=-target[2]*1.5

    # elif smooth==3: #平滑3
    #     if factorX>5:
    #         move_x=move_x*0.8
    #     if factorX<-5:
    #         move_x=move_x*0.8

    #     if factorY>5:
    #         move_y=move_y*0.8
    #     if factorX<-5:
    #         move_y=move_y*0.8
    move_x,move_y=final_x * Sx * delay_factor * dist_factor , final_y * Sy * delay_factor * dist_factor

    return move_x,move_y

