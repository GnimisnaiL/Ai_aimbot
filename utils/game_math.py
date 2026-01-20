import time

#根据高度和 宽度 估算角色距离 
def get_approx_distance(target_w, target_h):
    #体型修正
    aspect = target_w/max(target_h, 1)
    #if aspect>0.6:
    #    print("体型异常，宽高比为",aspect)
    aspect = max(0.20, min(0.60, aspect))
                
    #基础距离（高度主导）
    base=1100/max(target_w/aspect, 1)
    #输出位 aspect ≈ 0.38，作为中性参考
    correction=1+0.9*(aspect-0.38)
    estimatedTargetDistance=base*correction
    
    return estimatedTargetDistance

#计算距离补偿系数
def get_dist_factor(estimatedTargetDistance, standard_dist_speed):
    return ((8.2/estimatedTargetDistance)+3.5)/standard_dist_speed

#计算距离修正值
def get_correction_value(estimatedTargetDistance):
    return 150/(estimatedTargetDistance + 1.5)

#计算移动补偿值
def get_move_fix_value(now, a_pressed, d_pressed, dist, move_time, move_time_threshold,):
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
        return 0,now
    
    # 只按A键
    elif a_pressed and not d_pressed:
        
        if elapsed_time > move_time_threshold:
            return get_correction_value(dist),move_time
        else:
            return 0,move_time
        # else:
        #     # 线性插值：从0到最终值
        #     base_value = get_correction_value(dist)
        #     t = elapsed_time / move_time_threshold  # 归一化时间 [0, 1]
        #     return base_value * t,move_fix_time
        
            
    
    # 只按D键
    elif d_pressed and not a_pressed:
        if elapsed_time > move_time_threshold:
            return -1 * get_correction_value(dist),move_time
        else:
            return 0,move_time
        # else:
        #     # 线性插值：从0到最终值
        #     base_value = get_correction_value(dist)
        #     t = elapsed_time / move_time_threshold  # 归一化时间 [0, 1]
        #     return -1 * base_value * t,move_fix_time
        
    
    # 其他情况（理论上不会执行到这里）
    return 0,now

#平滑锁头位置
def smooth_headshot_position(dist, headshot_dist, headshot_pos, position_y):
    lower = headshot_dist - 0.5
    upper = headshot_dist + 0.5
    if dist <= lower:
        return headshot_pos
    elif dist >= upper:
        return position_y
    else:
        # 线性插值
        ratio = (dist - lower) / (upper - lower)  
        return headshot_pos + ratio * (position_y - headshot_pos)

#根据目标体型或者距离 进行速度限制或者平滑
def smooth_poccess(move_x, move_y, dist, factorX, factorY, smooth, target, smoothX ,smoothY):
    
    #if dist<10:
    #    return move_x,move_y
    if smooth==1: #平滑1 取上次输出值平滑
        if abs(factorX)>2.7: # 平滑左右分界点2.7
            move_x=smoothX.update(move_x)
        else:
            smoothX.clean()
        if abs(factorY)>3: # 平滑上下分界点3
            move_y=smoothY.update(move_y)     
        else:
            smoothX.clean()

    elif smooth==2: #平滑2
        if factorX>1.5:
            move_x=target[2]*1.5/2
        if factorX<-1.5:
            move_x=-target[2]*1.5/2

        if factorY>2:
            move_y=target[2]*1.5/2
        if factorY<-2:
            move_y=-target[2]*1.5/2

    elif smooth==3: #平滑3
        if factorX>5:
            move_x=move_x*0.8
        if factorX<-5:
            move_x=move_x*0.8

        if factorY>5:
            move_y=move_y*0.8
        if factorX<-5:
            move_y=move_y*0.8
    return move_x,move_y

