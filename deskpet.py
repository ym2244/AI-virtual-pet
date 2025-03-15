import sys
import os
import glob
import google.generativeai as genai
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QPoint

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

# 桌宠窗口（正方形，透明，可拖动）
class DeskPet(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI 桌宠")
        self.setGeometry(100, 100, 400, 400)  # 让窗口是正方形

        # 设置无边框 & 透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 创建 QLabel 作为动画窗口
        self.pet_label = QLabel(self)
        self.pet_label.setGeometry(0, 0, 400, 400)  # 让 QLabel 也是正方形
        self.pet_label.setScaledContents(False)  # 禁止自动缩放，避免图片拉伸

        # 载入 PNG 动画帧
        self.image_folder = r"D:\vscode\C\pet\images\Default\Happy\1"
        self.image_paths = sorted(glob.glob(os.path.join(self.image_folder, "*.png")))
        self.current_frame = 0

        # 设置定时器，每 100ms 切换一张图片
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)  # 控制动画速度

        # 先显示第一张图片
        self.update_frame()

        # 启用鼠标拖动
        self.old_pos = None
        self.chat_window = None  # 记录聊天窗口
        self.locked = False  # 默认不锁定

    def update_frame(self):
        """ 切换到下一张图片 """
        if self.image_paths:
            pixmap = QPixmap(self.image_paths[self.current_frame])
            scaled_pixmap = pixmap.scaled(
                self.pet_label.width(),  # 让图片适应 QLabel
                self.pet_label.height(),
                Qt.KeepAspectRatio,  # 保持比例，不拉伸
                Qt.SmoothTransformation  # 让缩放更平滑
            )
            self.pet_label.setPixmap(scaled_pixmap)
            self.current_frame = (self.current_frame + 1) % len(self.image_paths)  # 循环切换

    def set_chat_window(self, chat_window):
        """ 关联聊天窗口 """
        self.chat_window = chat_window

    def toggle_lock(self):
        """ 切换锁定状态 """
        self.locked = not self.locked

    def mousePressEvent(self, event):
        """ 允许鼠标拖动桌宠 """
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """ 拖动窗口，并在锁定时同时移动聊天窗口 """
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            
            # 如果锁定了，则同步移动聊天窗口
            if self.locked and self.chat_window:
                self.chat_window.move(self.chat_window.x() + delta.x(), self.chat_window.y() + delta.y())

            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """ 释放鼠标 """
        self.old_pos = None


# 独立对话窗口
class ChatWindow(QWidget):
    def __init__(self, pet_window):
        super().__init__()

        self.setWindowTitle("AI 桌宠对话框")
        self.setGeometry(500, 100, 400, 300)  # 设定位置 & 大小
        self.pet_window = pet_window  # 记录桌宠窗口
        self.locked = False  # 默认不锁定
        self.old_pos = None  # 记录鼠标位置

        layout = QVBoxLayout()

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_box = QLineEdit(self)
        layout.addWidget(self.input_box)

        send_button = QPushButton("发送", self)
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        # 添加 "锁定/解锁" 按钮
        self.lock_button = QPushButton("🔒 锁定", self)
        self.lock_button.clicked.connect(self.toggle_lock)
        layout.addWidget(self.lock_button)

        self.setLayout(layout)

    def toggle_lock(self):
        """ 切换锁定状态 """
        self.locked = not self.locked
        self.pet_window.toggle_lock()
        self.lock_button.setText("🔓 解锁" if self.locked else "🔒 锁定")

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

    def mousePressEvent(self, event):
        """ 允许鼠标拖动聊天窗口 """
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """ 拖动窗口，并在锁定时同时移动桌宠 """
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())

            # 如果锁定了，则同步移动桌宠窗口
            if self.locked:
                self.pet_window.move(self.pet_window.x() + delta.x(), self.pet_window.y() + delta.y())

            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """ 释放鼠标 """
        self.old_pos = None


# 运行应用
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建桌宠窗口
    pet_window = DeskPet()

    # 创建对话窗口
    chat_window = ChatWindow(pet_window)
    pet_window.set_chat_window(chat_window)  # 关联聊天窗口

    # 显示窗口
    pet_window.show()
    chat_window.show()
    
    sys.exit(app.exec_())
