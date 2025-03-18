import os
import glob

# 获取当前文件的路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 拼接启动动画路径
folder_path = os.path.join(BASE_DIR, "images", "StartUP", "Nomal")

# 获取 PNG 文件
images = sorted(glob.glob(os.path.join(folder_path, "*.png")))

print("加载的图片文件:", images)
