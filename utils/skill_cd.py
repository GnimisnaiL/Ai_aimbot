import mss
import cv2
import numpy as np
import time
import os

#from overlay import SkillOverlay

monitor = {"left": 1842, "top": 1085, "width": 9, "height": 16}

def quick_capture_with_preview():
    # 1. 创建保存文件夹
    save_path = "debug_images"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 2. 定义截图区域 (请确保坐标在你的显示器范围内)
    # 如果是 1080p 屏幕，想截中心：left=800, top=380
    #monitor = {"left": 1842, "top": 1085, "width": 9, "height": 16} 
    #monitor = {"left": 1918, "top": 1085, "width": 9, "height": 16} 
    print("正在启动实时预览...")
    print("操作说明:")
    print(" - [S] 键：手动保存当前图片到本地")
    print(" - [Q] 键：退出预览并停止")

    with mss.mss() as sct:
        try:
            while True:
                # 3. 截图
                screenshot = sct.grab(monitor)
                
                # 4. 转换格式 (MSS -> Numpy -> BGR)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                pixel_bgra = img[0, 0]
                print(pixel_bgra)
                # 5. 实时显示
                # 放大 4 倍预览，方便看清数字和变动的背景
                preview_img = cv2.resize(img, (450, 800), interpolation=cv2.INTER_NEAREST)
                
                # 在窗口上显示当前坐标信息
                cv2.putText(preview_img, f"Pos: {monitor['left']},{monitor['top']}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow("Real-time Preview (S to Save, Q to Quit)", preview_img)

                # 6. 按键监听
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'):
                    # 手动保存
                    filename = os.path.join(save_path, f"manual_{int(time.time()*1000)}.png")
                    cv2.imwrite(filename, img)
                    print(f"手动保存成功: {filename}")
                
                elif key == ord('q'):
                    print("用户退出。")
                    break
                
                # 每 0.2 秒截取一次的逻辑
                # 如果你想让预览非常顺滑，可以把这里的 sleep 调小或去掉
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n程序停止。")
        finally:
            cv2.destroyAllWindows()

def get_psylocke_cd():
    """
    截图并返回指定坐标 (1847, 1087) 的 BGR 颜色值
    """
    with mss.mss() as sct:
        # 1. 截图
        pixel1 = sct.grab({"left": 1847, "top": 1087, "width": 1, "height": 1} ).pixel(0, 0)[0]
        
        if pixel1==0:
            return 2
        elif pixel1==255:
            return 0
        else:
            pixel1=1
        return pixel1

def get_spiderman_cd():
    """
    截图并返回指定坐标 (1847, 1087) 的 BGR 颜色值
    """
    with mss.mss() as sct:
        # 1. 截图
        pixel1 = sct.grab({"left": 1923, "top": 1087, "width": 1, "height": 1}).pixel(0, 0)[0]
        pixel2 = sct.grab({"left": 1919, "top": 1099, "width": 1, "height": 1}).pixel(0, 0)[0]
        
        #print(pixel1,pixel2)
        if pixel1==0:
            return 3
        elif pixel1!=255:
            return 1
        else:
            if pixel2==255:
                return 2
            else:
                return 0

def get_strange_countdown():

    with mss.mss() as sct:
        # 1. 截图
        pixel1 = sct.grab({"left": 1276, "top": 229, "width": 1, "height": 1}).pixel(0, 0)

        return pixel1==(254,222,50)

def get_venom():

    with mss.mss() as sct:
        # 1. 截图
        pixel1 = sct.grab({"left": 1151, "top": 1171, "width": 1, "height": 1}).pixel(0, 0)[0]

        return pixel1!=255


if __name__ == "__main__":
    #quick_capture_with_preview()
    
    if 0:
        #overlay = SkillOverlay()
        #overlay.show()
        while True:
           get_strange_countdown()
            