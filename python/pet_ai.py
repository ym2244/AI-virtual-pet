# pet_ai.py (单独的AI处理和情绪调整模块）
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-pro-latest"

class DeskPetAI:
    def __init__(self):
        self.pet_mode = False
        self.mood_score = 81

    def toggle_pet_mode(self):
        self.pet_mode = not self.pet_mode

    def chat_with_ai(self, user_message):
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = (f"你是一个可爱的宠物，你会分析用户说的话对你的心情产生的影响（0~100之间）。"
                  f"你目前的心情值是{self.mood_score}/100，如果用户的话让你开心则提高心情值，如果让你难过则降低心情值。"
                  "你的回复后必须以格式 (+x)或(-x) 明确表示你的心情变化值。\n"
                  f"用户：{user_message}")

        response = model.generate_content(prompt).text
        self.adjust_mood(response)  # 更新心情值
        return response.split('(')[0]  # 返回纯文本回复给界面

    def adjust_mood(self, ai_response):
        mood_change_match = re.search(r"\(([+-]\d+)\)", ai_response)
        if mood_change_match:
            mood_change = int(mood_change_match.group(1))
            self.mood_score = max(0, min(100, self.mood_score + mood_change))
            print(f"心情值变化了: {mood_change}, 当前心情值为: {self.mood_score}")
        else:
            print("⚠️ AI未返回明确心情变化值，心情不变。")

    def simple_chat(self, user_message):
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(user_message)
        return response.text
