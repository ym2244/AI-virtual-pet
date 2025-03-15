import sys
import os
import glob
import google.generativeai as genai
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QPixmap, QIcon, QTextCursor
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

class AnimationThread(QThread):
    update_pixmap = pyqtSignal(QPixmap)

    def __init__(self, image_folder, loop=True):
        super().__init__()
        self.image_folder = image_folder
        self.image_paths = sorted(glob.glob(os.path.join(image_folder, "*.png")))
        self.current_frame = 0
        self.running = True
        self.loop = loop

    def run(self):
        if not self.image_paths:
            print(f"⚠️ 警告：{self.image_folder} 目录为空，无法播放动画！")
            return
        frames_played = 0
        while self.running:
            pixmap = QPixmap(self.image_paths[self.current_frame])
            self.update_pixmap.emit(pixmap)
            self.current_frame += 1
            frames_played += 1
            if self.current_frame >= len(self.image_paths):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.running = False
            self.msleep(100)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

    def set_image_folder(self, new_folder, loop=True):
        self.image_folder = new_folder
        self.image_paths = sorted(glob.glob(os.path.join(new_folder, "*.png")))
        self.current_frame = 0
        self.loop = loop

class DeskPet(QWidget):
    def __init__(self):
        super().__init__()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        self.default_animation = os.path.join(BASE_DIR, "images", "Default", "Happy", "1")
        self.speaking_animation = os.path.join(BASE_DIR, "images", "Say", "Shining", "B_2")
        self.startup_animation = os.path.join(BASE_DIR, "images", "StartUP", "Nomal")
        self.raised_animation = os.path.join(BASE_DIR, "images", "Raise", "Raised_Dynamic", "Happy")

        self.setWindowTitle("AI 桌宠")
        self.setGeometry(100, 100, 400, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.pet_label = QLabel(self)
        self.pet_label.setGeometry(0, 0, 400, 400)
        self.pet_label.setScaledContents(False)

        self.being_dragged = False
        self.old_pos = None
        self.chat_window = None
        self.locked = False

        self.animation_thread = AnimationThread(self.startup_animation, loop=False)
        self.animation_thread.update_pixmap.connect(self.update_frame)
        self.animation_thread.finished.connect(self.switch_to_default_animation)
        self.animation_thread.start()

    def update_frame(self, pixmap):
        scaled_pixmap = pixmap.scaled(
            self.pet_label.width(),
            self.pet_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.pet_label.setPixmap(scaled_pixmap)

    def switch_to_default_animation(self):
        self.animation_thread = AnimationThread(self.default_animation)
        self.animation_thread.update_pixmap.connect(self.update_frame)
        self.animation_thread.start()

    def set_chat_window(self, chat_window):
        self.chat_window = chat_window

    def toggle_lock(self):
        self.locked = not self.locked

    def change_animation(self, speaking):
        if self.being_dragged:
            self.animation_thread.set_image_folder(self.raised_animation)
        elif speaking:
            self.animation_thread.set_image_folder(self.speaking_animation)
        else:
            self.animation_thread.set_image_folder(self.default_animation)

    def ensure_top(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.being_dragged = True
            self.change_animation(False)

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            if self.locked and self.chat_window:
                self.chat_window.move(self.chat_window.x() + delta.x(), self.chat_window.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.being_dragged = False
        self.change_animation(False)

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

        self.lock_button = QPushButton("🔒 锁定", self)
        self.lock_button.clicked.connect(self.toggle_lock)
        layout.addWidget(self.lock_button)

        self.setLayout(layout)

    def toggle_lock(self):
        self.locked = not self.locked
        self.pet_window.toggle_lock()
        self.lock_button.setText("🔓 解锁" if self.locked else "🔒 锁定")

    def send_message(self):
        user_text = self.input_box.text().strip()
        if not user_text:
            return

        self.chat_display.append(f"我: {user_text}")
        self.pet_window.change_animation(True)
        ai_response = chat_with_ai(user_text)
        self.show_response_step_by_step(ai_response)
        self.input_box.clear()

    def changeEvent(self, event):
        if event.type() == event.WindowStateChange:
            if self.isMinimized():
                if self.locked:
                    self.pet_window.hide()
            else:
                self.pet_window.ensure_top()

    def show_response_step_by_step(self, response_text):
        self.current_text = response_text
        self.current_index = 0
        self.chat_display.append("桌宠: ")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.add_next_character)
        self.timer.start(50)

    def add_next_character(self):
        if self.current_index < len(self.current_text):
            self.chat_display.insertPlainText(self.current_text[self.current_index])
            self.chat_display.moveCursor(QTextCursor.End)
            self.current_index += 1
        else:
            self.timer.stop()
            self.pet_window.change_animation(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    pet_window = DeskPet()
    chat_window = ChatWindow(pet_window)
    pet_window.set_chat_window(chat_window)

    pet_window.show()
    chat_window.show()

    sys.exit(app.exec_())
