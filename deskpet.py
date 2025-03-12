import sys
import os
import glob
import google.generativeai as genai
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer

# 读取 API Key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 选择 Gemini AI 模型
MODEL_NAME = "gemini-1.5-pro-latest"

# AI 对话函数
def chat_with_ai(user_message):
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(user_message)
    return response.text

# 主窗口（聊天窗口 + 动画）
class DeskPet(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI 桌宠")
        self.setGeometry(100, 100, 400, 500)

        # 创建界面布局
        layout = QVBoxLayout()
        
        # 桌宠动画 QLabel
        self.pet_label = QLabel(self)
        layout.addWidget(self.pet_label)

        # 载入图片帧（使用你的 `Default\Happy\1` 目录）
        self.image_folder = r"D:\vscode\C\pet\images\Default\Happy\1"
        self.image_paths = sorted(glob.glob(os.path.join(self.image_folder, "*.png")))  # 读取所有 PNG 图片
        self.current_frame = 0

        # 设置定时器，每 100ms 切换一张图片
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)  # 控制动画速度

        # 创建聊天窗口
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_box = QLineEdit(self)
        layout.addWidget(self.input_box)

        send_button = QPushButton("发送", self)
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        self.setLayout(layout)

        # 先显示第一张图片
        self.update_frame()

    def update_frame(self):
        """ 切换到下一张图片 """
        if self.image_paths:
            pixmap = QPixmap(self.image_paths[self.current_frame])
            self.pet_label.setPixmap(pixmap)
            self.current_frame = (self.current_frame + 1) % len(self.image_paths)  # 循环切换

    def send_message(self):
        user_text = self.input_box.text().strip()
        if not user_text:
            return
        
        # 显示用户输入
        self.chat_display.append(f"我: {user_text}")

        # 获取 AI 回复
        response = chat_with_ai(user_text)
        self.chat_display.append(f"桌宠: {response}")

        # 清空输入框
        self.input_box.clear()

# 托盘图标（右键菜单）
class DeskPetTray(QSystemTrayIcon):
    def __init__(self, app, window):
        super().__init__()

        self.app = app
        self.window = window
        self.setIcon(QIcon("icon.png"))  # 你可以替换成自己的桌宠图标
        self.setToolTip("AI 桌宠")

        # 创建菜单
        menu = QMenu()
        open_action = QAction("打开聊天", self)
        open_action.triggered.connect(self.window.show)
        menu.addAction(open_action)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.app.quit)
        menu.addAction(exit_action)

        self.setContextMenu(menu)

# 运行应用
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建聊天窗口
    pet_window = DeskPet()

    # 创建系统托盘图标
    tray_icon = DeskPetTray(app, pet_window)
    tray_icon.show()

    pet_window.show()
    sys.exit(app.exec_())
