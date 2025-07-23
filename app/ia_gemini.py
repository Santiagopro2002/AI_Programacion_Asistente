import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def obtener_respuesta_gemini(pregunta):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)

        # Usamos el modelo más reciente y rápido: gemini-1.5-flash-latest
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        response = model.generate_content(pregunta)

        return response.text
    except Exception as e:
        return f"Error llamando a Gemini: {e}"
