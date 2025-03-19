import sys
import os
import glob
import google.generativeai as genai
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QPixmap, QIcon, QTextCursor
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from pet_ai import DeskPetAI  # 引入 AI 逻辑
from PyQt5.QtWidgets import QProgressBar, QHBoxLayout



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
        print(f"当前动画路径是：{self.image_folder}")
        print(f"找到的图片数量：{len(self.image_paths)}")

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
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        self.default_animation = os.path.join(BASE_DIR, "images", "Default", "Happy", "1")
        self.speaking_animation = os.path.join(BASE_DIR, "images", "Say", "Shining", "B_2")
        self.startup_animation = os.path.join(BASE_DIR, "images", "StartUP", "Nomal")
        self.raised_animation = os.path.join(BASE_DIR, "images", "Raise", "Raised_Dynamic", "Happy")
        self.head_touch_start = os.path.join(BASE_DIR, "images", "Touch_Head", "A_Nomal")
        self.head_touch_loop = os.path.join(BASE_DIR, "images", "Touch_Head", "B_Nomal")
        self.head_touch_end = os.path.join(BASE_DIR, "images", "Touch_Head", "C_Nomal")
        self.normal_animation = os.path.join(BASE_DIR, "images", "Default", "Nomal", "2")
        self.sad_animation = os.path.join(BASE_DIR, "images", "Default", "PoorCondition", "2")
        self.speaking_normal_animation = os.path.join(BASE_DIR, "images", "Say", "Serious", "B")
        self.speaking_sad_animation = os.path.join(BASE_DIR, "images", "Say", "Self", "B_3")

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
        self.play_mode = False
        self.head_touching = False

        self.animation_thread = AnimationThread(self.startup_animation, loop=False)
        self.animation_thread.update_pixmap.connect(self.update_frame)
        self.animation_thread.finished.connect(self.switch_to_default_animation)
        self.animation_thread.start()

        self.play_mode_button = QPushButton("Play Mode", self)
        self.play_mode_button.setGeometry(10, 10, 100, 30)
        self.play_mode_button.clicked.connect(self.toggle_play_mode)

    def update_frame(self, pixmap):
        scaled_pixmap = pixmap.scaled(
            self.pet_label.width(),
            self.pet_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.pet_label.setPixmap(scaled_pixmap)

    def switch_to_default_animation(self):
        self.set_animation_by_mood(speaking=False)

    # 🌟 统一动画切换函数（新增加的统一动画函数）
    def set_animation_by_mood(self, speaking=False):
        self.animation_thread.stop()
        mood = self.chat_window.ai.mood_score if self.chat_window else 80

        if self.being_dragged:
            folder = self.raised_animation
        elif speaking:
            if mood > 80:
                folder = self.speaking_animation
            elif mood > 40:
                folder = self.speaking_normal_animation
            else:
                folder = self.speaking_sad_animation
        else:
            if mood > 80:
                folder = self.default_animation
            elif mood > 40:
                folder = self.normal_animation
            else:
                folder = self.sad_animation

        self.animation_thread = AnimationThread(folder, loop=True)
        self.animation_thread.update_pixmap.connect(self.update_frame)
        self.animation_thread.start()

    def set_chat_window(self, chat_window):
        self.chat_window = chat_window

    def toggle_lock(self):
        self.locked = not self.locked

    def toggle_play_mode(self):
        self.play_mode = not self.play_mode
        self.play_mode_button.setText("Exit Play Mode" if self.play_mode else "Play Mode")

    def ensure_top(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()

    def mousePressEvent(self, event):
        if self.play_mode:
            return
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.being_dragged = True
            self.set_animation_by_mood(speaking=False)  #🌟修改调用到统一函数

    def mouseMoveEvent(self, event):
        if self.play_mode:
            if event.y() < self.height() // 3 and not self.head_touching:
                self.head_touching = True
                self.animation_thread.set_image_folder(self.head_touch_start, loop=False)
                QTimer.singleShot(len(self.animation_thread.image_paths)*100, self.start_head_touch_loop)
            return
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            if self.locked and self.chat_window:
                self.chat_window.move(self.chat_window.x() + delta.x(), self.chat_window.y() + delta.y())
            self.old_pos = event.globalPos()

    def start_head_touch_loop(self):
        self.animation_thread.set_image_folder(self.head_touch_loop)

    def mouseReleaseEvent(self, event):
        if self.play_mode and self.head_touching:
            self.head_touching = False
            self.animation_thread.set_image_folder(self.head_touch_end, loop=False)
            QTimer.singleShot(len(self.animation_thread.image_paths)*100, self.switch_to_default_animation)
            return
        self.old_pos = None
        self.being_dragged = False
        self.set_animation_by_mood(speaking=False)  #🌟修改调用到统一函数

# 🗑️ 删除了原DeskPet类和类外的 change_animation 及 change_animation_based_on_mood 方法



class ChatWindow(QWidget):
    def __init__(self, pet_window):
        super().__init__()

        self.setWindowTitle("AI 桌宠对话框")
        self.setGeometry(500, 100, 400, 300)
        self.pet_window = pet_window
        self.ai = DeskPetAI()  # 使用 AI 模块
        self.locked = False
        self.old_pos = None

        main_layout = QHBoxLayout()
        layout = QVBoxLayout()

        # 心情进度条
        self.mood_bar = QProgressBar(self)
        self.mood_bar.setOrientation(Qt.Vertical)
        self.mood_bar.setMinimum(0)
        self.mood_bar.setMaximum(100)
        self.mood_bar.setValue(self.ai.mood_score)
        self.mood_bar.setFormat("心情\n%d%%")

        # 布局设置
        main_layout.addLayout(layout, stretch=4)
        main_layout.addWidget(self.mood_bar, stretch=1)
        self.setLayout(main_layout)


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

        # 添加 "切换宠物模式" 按钮
        self.pet_mode_button = QPushButton("切换宠物模式", self)
        self.pet_mode_button.clicked.connect(self.toggle_pet_mode)
        layout.addWidget(self.pet_mode_button)


    def toggle_lock(self):
        self.locked = not self.locked
        self.pet_window.toggle_lock()
        self.lock_button.setText("🔓 解锁" if self.locked else "🔒 锁定")

    def toggle_pet_mode(self):
        """ 切换 AI 进入 'Pet Mode'（宠物模式） """
        self.ai.toggle_pet_mode()
        mode_text = "宠物模式 ON" if self.ai.pet_mode else "宠物模式 OFF"
        self.chat_display.append(f"🌟 {mode_text}")



    def update_mood_bar(self):
        """实时更新心情进度条的数值"""
        self.mood_bar.setValue(self.ai.mood_score)


    def send_message(self):
        user_text = self.input_box.text().strip()
        if not user_text:
            return

        self.chat_display.append(f"我: {user_text}")

        #🌟更新调用到统一动画函数
        self.pet_window.set_animation_by_mood(speaking=True)

        ai_response = (self.ai.chat_with_ai(user_text) if self.ai.pet_mode else
                       genai.GenerativeModel("gemini-1.5-pro-latest").generate_content(user_text).text)

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
        self.timer.start(100)  # important: how fast the program react to the mouse

    def add_next_character(self):
        if self.current_index < len(self.current_text):
            self.chat_display.insertPlainText(self.current_text[self.current_index])
            self.chat_display.moveCursor(QTextCursor.End)
            self.current_index += 1
        else:
            self.timer.stop()
            # 🌟更新调用到统一动画函数
            self.pet_window.set_animation_by_mood(speaking=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pet_window = DeskPet()
    chat_window = ChatWindow(pet_window)
    pet_window.set_chat_window(chat_window)

    pet_window.show()
    chat_window.show()

    sys.exit(app.exec_())
