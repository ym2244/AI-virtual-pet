import google.generativeai as genai
import os
from dotenv import load_dotenv

# 读取 API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 选择一个支持的 Gemini 模型
MODEL_NAME = "gemini-1.5-pro-latest"

# AI 聊天函数
def chat_with_ai(user_message):
    model = genai.GenerativeModel(MODEL_NAME)  # 使用新模型名称
    response = model.generate_content(user_message)
    return response.text

# 测试交互
if __name__ == "__main__":
    while True:
        user_input = input("你: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = chat_with_ai(user_input)
        print("AI 桌宠:", response)
