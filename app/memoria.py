# memoria.py
import redis
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Usa redis-memoria si estás en Docker, localhost si fuera
redis_host = os.getenv("REDIS_HOST", "redis-memoria")
redis_port = int(os.getenv("REDIS_PORT", 6379))

#r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
r = redis.Redis(host='redis-memoria', port=6379, decode_responses=True)

def guardar_en_memoria(id_usuario, id_sesion, tipo, contenido):
    clave = f"memoria:{id_sesion}"
    mensaje = f"{tipo}:{contenido}"
    r.rpush(clave, mensaje)

def recuperar_memoria(id_usuario, id_sesion, limite=6):
    clave = f"memoria:{id_sesion}"
    historial = r.lrange(clave, -limite * 2, -1)
    resultado = []
    for item in historial:
        tipo, contenido = item.split(":", 1)
        resultado.append((tipo, contenido))
    return resultado
