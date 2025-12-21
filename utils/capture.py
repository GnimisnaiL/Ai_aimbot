import cv2
import mss
import bettercam
import threading
import queue
import numpy as np
import time
from utils.config_watcher import cfg

class Capture(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.name = "图书馆管理"

        self.running = True        
        self.frame_queue = queue.Queue(maxsize=1)


        if cfg.Bettercam_capture:
            self.setup_bettercam()
        elif cfg.Obs_capture:
            self.setup_obs()
        elif cfg.mss_capture:
            self.setup_mss()
    

    def calculate_screen_offset():
        a=(cfg.screen_x-cfg.window_x)/2
        b=(cfg.screen_y-cfg.window_y)/2-cfg.y_correction_factor
        c=(cfg.screen_x-cfg.window_x)/2+cfg.window_x
        d=(cfg.screen_y-cfg.window_y)/2+cfg.window_y-cfg.y_correction_factor
        return(int(a),int(b),int(c),int(d))


    def calculate_mss_offset(self):
        a=(cfg.screen_x-cfg.window_x)/2
        b=(cfg.screen_y-cfg.window_y)/2-cfg.y_correction_factor
        c=(cfg.screen_x-cfg.window_x)/2+cfg.window_x
        d=(cfg.screen_y-cfg.window_y)/2+cfg.window_y-cfg.y_correction_factor

        return int(a), int(b), int(cfg.window_x), int(cfg.window_x)

    def setup_bettercam(self):
        self.bc = bettercam.create(
            device_idx=cfg.bettercam_monitor_id,
            output_idx=cfg.bettercam_gpu_id,
            output_color="BGR",
            max_buffer_len=1,
            region=self.calculate_screen_offset(),
            nvidia_gpu= False

        )
        if not self.bc.is_capturing:
            self.bc.start(
                region=self.calculate_screen_offset(),
                target_fps=cfg.capture_fps,
                video_mode=True
            )

    def setup_obs(self):
        camera_id = self.find_obs_virtual_camera() if cfg.Obs_camera_id == 'auto' else int(cfg.Obs_camera_id) if cfg.Obs_camera_id.isdigit() else None
        if camera_id is None:
            print('[Capture] OBS Virtual Camera not found')
            exit(0)
        
        self.obs_camera = cv2.VideoCapture(camera_id)
        self.obs_camera.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.detection_window_width)
        self.obs_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.detection_window_height)
        self.obs_camera.set(cv2.CAP_PROP_FPS, cfg.capture_fps)

    def setup_mss(self):
        left, top, width, height = self.calculate_mss_offset()
        self.monitor = {"left": left, "top": top, "width": width, "height": height}



    def run(self):
        while self.running:
            frame = self.capture_frame()
            if frame is not None:
                if self.frame_queue.full():
                    self.frame_queue.get()
                self.frame_queue.put(frame)

            
    def capture_frame(self):
        #start = time.time()
        if cfg.Bettercam_capture:
            #计算每秒录制帧数
            self.current_time = time.time()
            self.frame_count=self.frame_count+1
            if self.current_time - self.last_time >= 1.0:
                fps = self.frame_count / (self.current_time - self.last_time)
                print(f"{fps:>3.0f}")
                self.frame_count = 0
                self.last_time = self.current_time
            return self.bc.get_latest_frame()
        
        if cfg.Obs_capture:
            ret_val, img = self.obs_camera.read()
            return img if ret_val else None

        if cfg.mss_capture:
            with mss.mss() as sct:
                screenshot = sct.grab(self.monitor)
                raw = screenshot.bgra
                img = np.frombuffer(raw, dtype=np.uint8).reshape((screenshot.height, screenshot.width, 4))
            #    #print("capture_frame time:", (time.time() - start) * 1000, "ms")
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)


    def get_new_frame(self):
        try:
            return self.frame_queue.get(timeout=1)
        except queue.Empty:
            return None

    
    def restart(self):
        if cfg.Bettercam_capture:
            self.bc.stop()
            del self.bc
            self.setup_bettercam()

            print('[Capture] Capture reloaded')
          
            
   
    def find_obs_virtual_camera(self):
        max_tested = 20
        obs_camera_name = 'DSHOW'
        
        for i in range(max_tested):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if not cap.isOpened():
                continue
            if cap.getBackendName() == obs_camera_name:
                print(f'[Capture] OBS Virtual Camera found at index {i}')
                cap.release()
                return i
            cap.release()
        return -1
    

    
    def Quit(self):
        self.running = False
        if cfg.Bettercam_capture and hasattr(self, 'bc') and self.bc.is_capturing:
            self.bc.stop()
        if cfg.Obs_capture and hasattr(self, 'obs_camera'):
            self.obs_camera.release()
        self.join()

capture = Capture()
capture.start()