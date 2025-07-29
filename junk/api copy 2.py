
import requests

API_KEY = "sk-cd19cc45e8d3498eb530f4a9fbb38da7"  # Replace with your actual API key
API_URL = "https://api.deepseek.com/v1/chat/completions"  # Example endpoint (check actual URL)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",  # Check available models
    "messages": [
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ]
}

response = requests.post(API_URL, headers=headers, json=data)
print(response.json())

