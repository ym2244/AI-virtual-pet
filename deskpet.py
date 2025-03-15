import sys
import os
import glob
import google.generativeai as genai
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal

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


# === 线程类（处理动画，不影响 UI） ===
class AnimationThread(QThread):
    update_pixmap = pyqtSignal(QPixmap)

    def __init__(self, image_folder):
        super().__init__()
        self.image_paths = sorted(glob.glob(os.path.join(image_folder, "*.png")))
        self.current_frame = 0
        self.running = True

    def run(self):
        """ 在独立线程中持续更新动画 """
        while self.running:
            pixmap = QPixmap(self.image_paths[self.current_frame])
            self.update_pixmap.emit(pixmap)
            self.current_frame = (self.current_frame + 1) % len(self.image_paths)
            self.msleep(100)  # 控制动画速度（100ms）

    def stop(self):
        """ 停止动画线程 """
        self.running = False
        self.quit()
        self.wait()


# === 桌宠窗口（透明 + 可拖动 + 置顶） ===
class DeskPet(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI 桌宠")
        self.setGeometry(100, 100, 400, 400)

        # 设置无边框 & 透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 创建 QLabel 作为动画窗口
        self.pet_label = QLabel(self)
        self.pet_label.setGeometry(0, 0, 400, 400)
        self.pet_label.setScaledContents(False)

        # 启动动画线程
        self.image_folder = r"D:\vscode\C\pet\images\Default\Happy\1"
        self.animation_thread = AnimationThread(self.image_folder)
        self.animation_thread.update_pixmap.connect(self.update_frame)
        self.animation_thread.start()

        # 记录聊天窗口
        self.chat_window = None
        self.locked = False
        self.old_pos = None

    def update_frame(self, pixmap):
        """ 更新动画帧 """
        scaled_pixmap = pixmap.scaled(
            self.pet_label.width(),
            self.pet_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.pet_label.setPixmap(scaled_pixmap)

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
            
            if self.locked and self.chat_window:
                self.chat_window.move(self.chat_window.x() + delta.x(), self.chat_window.y() + delta.y())

            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """ 释放鼠标 """
        self.old_pos = None

    def showEvent(self, event):
        """ 确保桌宠始终在最上层 """
        if not self.locked:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            self.show()


# === 聊天窗口（支持锁定 & 最小化同步桌宠） ===
class ChatWindow(QWidget):
    def __init__(self, pet_window):
        super().__init__()

        self.setWindowTitle("AI 桌宠对话框")
        self.setGeometry(500, 100, 400, 300)
        self.pet_window = pet_window
        self.locked = False
        self.old_pos = None

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

        self.chat_display.append(f"我: {user_text}")

        response = chat_with_ai(user_text)
        self.chat_display.append(f"桌宠: {response}")

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

            if self.locked:
                self.pet_window.move(self.pet_window.x() + delta.x(), self.pet_window.y() + delta.y())

            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """ 释放鼠标 """
        self.old_pos = None

    def changeEvent(self, event):
        """ 最小化/恢复时，桌宠窗口也跟随 """
        if event.type() == 105:  # 105 = QEvent.WindowStateChange
            if self.windowState() == Qt.WindowMinimized and self.locked:
                self.pet_window.setWindowState(Qt.WindowMinimized)
            elif self.windowState() == Qt.WindowNoState and self.locked:
                self.pet_window.setWindowState(Qt.WindowNoState)
                self.pet_window.show()


# === 运行应用 ===
if __name__ == "__main__":
    app = QApplication(sys.argv)

    pet_window = DeskPet()
    chat_window = ChatWindow(pet_window)
    pet_window.set_chat_window(chat_window)

    pet_window.show()
    chat_window.show()
    
    sys.exit(app.exec_())
