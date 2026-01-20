"""
可视化显示线程模块
用于显示推理结果
"""
import cv2
import queue
import threading
import time

class DisplayThread(threading.Thread):
    def __init__(self, window_size=(320, 320)):
        """
        初始化显示线程
        
        Args:
            window_size: 窗口尺寸，默认为(320, 320)
        """
        super().__init__()
        self.image_queue = queue.Queue(maxsize=1)
        self.running = True
        self.daemon = True
        self.window_size = window_size
        self.window_created = False
        self.window_name = 'view'
    
    def run(self):
        """
        显示线程主循环
        """
        while self.running:
            try:
                # 如果窗口还没创建，先创建窗口
                if not self.window_created:
                    cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(self.window_name, self.window_size[0], self.window_size[1])
                    self.window_created = True
                
                # 非阻塞获取图像
                img = self.image_queue.get_nowait()
                
                # 显示图像
                cv2.imshow(self.window_name, img)
                
                # 处理窗口事件
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("检测到Q键退出")
                    self.running = False
                    break
                    
            except queue.Empty:
                # 没有新图像时，也要维持窗口响应
                if self.window_created:
                    cv2.waitKey(1)
                time.sleep(0.001)
            except Exception as e:
                print(f"显示线程错误: {e}")
                time.sleep(0.01)
        
        # 清理资源
        self.cleanup()
        print("显示线程结束")
    
    def update_image(self, img):
        """
        更新显示图像（非阻塞）
        
        Args:
            img: 要显示的图像
        """
        if not self.running or img is None:
            return 
        
        try:
            # 清空队列，只保留最新帧
            while not self.image_queue.empty():
                try:
                    self.image_queue.get_nowait()
                except queue.Empty:
                    break        
            self.image_queue.put_nowait(img)
        except Exception as e:
            print(f"更新图像错误: {e}")
    
    def cleanup(self):
        """清理窗口资源"""
        if self.window_created:
            cv2.destroyWindow(self.window_name)
            self.window_created = False
    
    def stop(self):
        """停止显示线程"""
        self.running = False
    
    def is_window_created(self):
        """检查窗口是否已创建"""
        return self.window_created
    
    def resize_window(self, width, height):
        """
        调整窗口大小
        
        Args:
            width: 新宽度
            height: 新高度
        """
        if self.window_created:
            cv2.resizeWindow(self.window_name, width, height)
            self.window_size = (width, height)
    
    def get_window_size(self):
        """获取当前窗口尺寸"""
        return self.window_size

