import numpy as np  # 如果要支持数组输入，建议导入numpy

def logistic(x, L=1.2, U=0.2, k=1.0, x0=1.1):
        """
        广义 Logistic 函数（S型曲线）
    
        参数:
            x     : 输入值（可以是标量或 numpy 数组）
            L     : 下渐近线（x → -∞ 时的极限值）
            U     : 上渐近线（x → +∞ 时的极限值）
            k     : 增长速率（越大越陡，k<0 时为下降型）
            x0    : 拐点位置（曲线中间点）
    
        返回:
            y 值（与 x 相同形状）
        """
        return L + (U - L) / (1 + np.exp(-k * (x - x0)))

def dynamic_factor(xy,n):
    if xy==0:
        if n<2:
            return 1
        elif 2<=n:
            return 1/(n*2)
    else:
        if n<3:
            return 1
        elif 2<=n:
            return 1/(n*2)

class SmoothMouse:
    def __init__(self, a=0.9):
        self.a = a
        self.last_move = 0
        self.last_last_move = 0

    def update(self, current_move):
        smooth = self.last_move * self.a + current_move/4 * ( 1 - self.a)
        self.last_move = smooth
        return int(smooth)

    def update2(self, current_move):
        smooth = self.last_last_move*0.63 + self.last_move*0.33 + current_move/4 * 0.13
        self.last_last_move = self.last_move
        self.last_move = smooth
        return int(smooth)

    def clean(self):
        self.last_move = 0
        self.last_last_move = 0

    def inc_smooth(self):
        self.a +=0.05
        print("smooth:",self.a)

    def dec_smooth(self):
        self.a -=0.05
        print("smooth:",self.a)


    