import tkinter as tk
import threading
import queue

class SkillOverlay:
    def __init__(self):
        self.cmd_queue = queue.Queue()
        self._running = False
        self.pos_x = 1265
        self.pos_y = 778
        self.radius = 15

    def _setup_window(self):
        try:
            self.root = tk.Tk()
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            
            size = (self.radius * 2) + 4
            x = self.pos_x - self.radius
            y = self.pos_y - self.radius
            self.root.geometry(f"{size}x{size}+{x}+{y}")

            self.root.config(bg='black')
            self.root.attributes("-transparentcolor", "black")
            
            # Windows 鼠标穿透
            try:
                from ctypes import windll
                hwnd = windll.user32.GetParent(self.root.winfo_id())
                style = windll.user32.GetWindowLongW(hwnd, -20)
                windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)
            except:
                pass

            self.canvas = tk.Canvas(self.root, width=size, height=size, 
                                    bg='black', highlightthickness=0)
            self.canvas.pack()

            self.circle = self.canvas.create_oval(
                2, 2, size-2, size-2, 
                fill="black", outline="black", width=2
            )
            
            # 【核心逻辑】子线程自己循环处理队列里的任务
            def process_queue():
                try:
                    while True:
                        # 非阻塞获取队列里的最新指令
                        cmd, value = self.cmd_queue.get_nowait()
                        if cmd == "update":
                            if value == "red":
                                self.canvas.itemconfig(self.circle, fill="red", outline="white")
                            else:
                                self.canvas.itemconfig(self.circle, fill="black", outline="black")
                        elif cmd == "close":
                            self.root.destroy()
                            return # 退出循环
                except queue.Empty:
                    pass
                
                if self._running:
                    self.root.after(10, process_queue) # 10ms检查一次，延迟极低

            self.root.after(10, process_queue)
            self.root.mainloop()
        except Exception as e:
            print(f"Overlay Thread Error: {e}")
        finally:
            self._running = False

    def show(self):
        """主线程调用：开启"""
        if not self._running:
            self._running = True
            # 清空旧队列
            while not self.cmd_queue.empty():
                self.cmd_queue.get()
            threading.Thread(target=self._setup_window, daemon=True).start()

    def update(self, color):
        """主线程调用：发指令到队列，不直接碰UI"""
        if self._running:
            self.cmd_queue.put(("update", color))

    def close(self):
        """主线程调用：发关闭指令"""
        if self._running:
            self.cmd_queue.put(("close", None))
            self._running = False