
import requests

API_KEY = "sk-cd19cc45e8d3498eb530f4a9fbb38da7"  # Replace with your actual API key
import requests

DEEPSEEK_API_KEY = "sk-cd19cc45e8d3498eb530f4a9fbb38da7"  # 🔑 Replace with your actual key
API_URL = "https://api.deepseek.com/v1/chat/completions"  # Check actual URL in docs

headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-chat",  # Or another available model
    "messages": [
        {"role": "user", "content": "Write a Python function to reverse a string."}
    ],
    "temperature": 0.7
}

response = requests.post(API_URL, headers=headers, json=payload)

if response.status_code == 200:
    print(response.json()["choices"][0]["message"]["content"])
else:
    print("Error:", response.text)