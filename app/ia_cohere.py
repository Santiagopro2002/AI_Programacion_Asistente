import os
import cohere
from dotenv import load_dotenv

load_dotenv()

def obtener_respuesta_cohere(pregunta):
    try:
        api_key = os.getenv("COHERE_API_KEY")
        co = cohere.Client(api_key)

        respuesta = co.chat(
            message=pregunta,
            model="command-r-plus",
            temperature=0.5,
            max_tokens=1000
        )

        return respuesta.text
    except Exception as e:
        return f"❌ Error llamando a Cohere: {e}"
