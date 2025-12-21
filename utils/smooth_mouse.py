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