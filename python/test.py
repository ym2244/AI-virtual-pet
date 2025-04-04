import os
import glob

# Get the path of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the startup animation path
folder_path = os.path.join(BASE_DIR, "images", "StartUP", "Nomal")

# Get PNG files
images = sorted(glob.glob(os.path.join(folder_path, "*.png")))

print("Loaded image files:", images)
