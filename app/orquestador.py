from ia_gemini import obtener_respuesta_gemini
from ia_claude import obtener_respuesta_claude
from ia_cohere import obtener_respuesta_cohere

from memoria import guardar_en_memoria, recuperar_memoria



def obtener_respuesta_unificada(pregunta, id_usuario=None, id_sesion=None):
    try:
        # Recuperar memoria previa
        historial = list(recuperar_memoria(id_usuario, id_sesion, limite=6)) if id_usuario and id_sesion else []
        contexto = ""
        for tipo, contenido in historial:
            prefix = "Usuario: " if tipo == "user" else "IA: "
            contexto += f"{prefix}{contenido}\n"

        contexto += f"Usuario: {pregunta}\nIA:"

        # Consultar a cada IA
        respuesta1 = obtener_respuesta_gemini(contexto)
        respuesta2 = obtener_respuesta_claude(contexto)
        respuesta3 = obtener_respuesta_cohere(contexto)

        # Combinar las respuestas
        prompt_juez = f"""
Tengo tres respuestas a la misma pregunta dentro de este contexto:

1. {respuesta1}
2. {respuesta2}
3. {respuesta3}

Analiza las tres respuestas, elige la mejor o fusiona las ideas clave en una sola respuesta clara, útil y directa:
"""
        respuesta_final = obtener_respuesta_claude(prompt_juez)

        # Guardar en memoria
        if id_usuario and id_sesion:
            guardar_en_memoria(id_usuario, id_sesion, 'user', pregunta)
            guardar_en_memoria(id_usuario, id_sesion, 'ia', respuesta_final)

        return respuesta_final

    except Exception as e:
        return f"❌ Error en el orquestador: {e}"
