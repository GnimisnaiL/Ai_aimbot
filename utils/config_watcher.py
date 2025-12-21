import configparser
import random

class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.window_name = self.get_random_window_name()
        self.Read(verbose=False)
    
    def Read(self, verbose=False):
        try:
            with open("config.ini", "r", encoding="utf-8",) as f:
                self.config.read_file(f)
        except FileNotFoundError:
            print("Config file not found!")
            quit()

        # main
        self.main = self.config["main"]
        self.screen_x=int(self.main["screen_x"])
        self.screen_y=int(self.main["screen_y"])
        self.window_x=int(self.main["window_x"])
        self.window_y=int(self.main["window_y"])
        self.model_x=int(self.main["model_x"])
        self.model_y=int(self.main["model_y"])
        self.y_correction_factor=int(self.main["y_correction_factor"])
        self.x_portion=float(self.main["x_portion"])
        self.y_portion=float(self.main["y_portion"])
        self.speed_x=float(self.main["speed_x"])
        self.speed_y=float(self.main["speed_y"])
        self.mouse_driver=int(self.main["mouse_driver"])
        self.debug=int(self.main["debug"])

        # Capture Methods]
        self.capture_methods = self.config["Capture Methods"]
        self.fps_control = int(self.capture_methods["fps_control"])
        self.capture_fps = int(self.capture_methods["capture_fps"])
        self.Bettercam_capture = self.capture_methods.getboolean("Bettercam_capture")
        self.bettercam_monitor_id = int(self.capture_methods["bettercam_monitor_id"])
        self.bettercam_gpu_id = int(self.capture_methods["bettercam_gpu_id"])
        self.Obs_capture = self.capture_methods.getboolean("Obs_capture")
        self.Obs_camera_id = str(self.capture_methods["Obs_camera_id"])
        self.mss_capture = self.capture_methods.getboolean("mss_capture")
             
        if verbose:
            print("[Config] Config reloaded")
            
    def get_random_window_name(self):
        try:
            with open("window_names.txt", "r", encoding="utf-8") as file:
                window_names = file.read().splitlines()
            return random.choice(window_names) if window_names else "Calculator"
        except FileNotFoundError:
            #print("window_names.txt file not found, using default window name.")
            return "Calculator"

cfg = Config()