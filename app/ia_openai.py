import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def obtener_respuesta_chatgpt(pregunta):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": pregunta}
            ]
        )
        respuesta_texto = response.choices[0].message.content
        return respuesta_texto
    except Exception as e:
        return f"Error llamando a ChatGPT: {e}"
