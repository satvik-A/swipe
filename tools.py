import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.getenv("GROQ_API_KEY")
# print("🔑 GROQ_API_KEY loaded:", API_KEY)

def query_groq(messages, model="llama3-8b-8192"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Ensure a system prompt is always first
    system_message = {
        "role": "system",
        "content": "You are a helpful assistant that suggests personalized experience gifts."
    }

    full_messages = [system_message] + messages

    payload = {
        "model": model,
        "messages": full_messages
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"GROQ API error: {response.status_code} - {response.text}")