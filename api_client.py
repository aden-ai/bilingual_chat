import requests
import json

def call_ollama(prompt: str) -> str:
    """
    Calls Ollama using the HTTP API (most stable method on Windows).
    """
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=120)

        if response.status_code != 200:
            print("Ollama HTTP error:", response.text)
            return "Error: Ollama call failed."

        data = response.json()
        return data.get("response", "").strip()

    except requests.exceptions.Timeout:
        return "Error: Ollama request timed out."

    except Exception as e:
        print("Ollama HTTP exception:", e)
        return "Error: Ollama call failed."