# pet_ai.py (Standalone AI processing and mood adjustment module)
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
        prompt = (f"You are a cute pet, and you will analyze the user's words to determine their impact on your mood (between 0 and 100). "
                  f"Your current mood score is {self.mood_score}/100. If the user's words make you happy, increase your mood score; if they make you sad, decrease it. "
                  "Your reply must clearly indicate the mood change value in the format (+x) or (-x) at the end.\n"
                  f"User: {user_message}")

        response = model.generate_content(prompt).text
        self.adjust_mood(response)  # Update mood score
        return response.split('(')[0]  # Return plain text reply to the interface

    def adjust_mood(self, ai_response):
        mood_change_match = re.search(r"\(([+-]\d+)\)", ai_response)
        if mood_change_match:
            mood_change = int(mood_change_match.group(1))
            self.mood_score = max(0, min(100, self.mood_score + mood_change))
            print(f"Mood score changed by: {mood_change}, current mood score is: {self.mood_score}")
        else:
            print("⚠️ AI did not return a clear mood change value, mood remains unchanged.")

    def simple_chat(self, user_message):
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(user_message)
        return response.text
