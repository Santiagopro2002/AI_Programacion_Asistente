import os
import requests
from dotenv import load_dotenv

load_dotenv()

def obtener_respuesta_claude(pregunta):
    api_key = os.getenv("CLAUDE_API_KEY")
    url = "https://api.anthropic.com/v1/messages"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    data = {
        "model": "claude-3-haiku-20240307",  # Modelo gratuito
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": pregunta}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        json_data = response.json()

        if response.status_code == 200:
            return json_data["content"][0]["text"]
        else:
            return f"❌ Claude API Error {response.status_code}: {json_data.get('error', {}).get('message', 'Sin mensaje')}"
    except Exception as e:
        return f"❌ Error al conectar con Claude: {str(e)}"
