import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Select a supported Gemini model
MODEL_NAME = "gemini-1.5-pro-latest"

# AI chat function
def chat_with_ai(user_message):
    model = genai.GenerativeModel(MODEL_NAME)  # Use the new model name
    response = model.generate_content(user_message)
    return response.text

# Test interaction
if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = chat_with_ai(user_input)
        print("AI Desk Pet:", response)
