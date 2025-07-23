from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_connection
#from ia_gemini import obtener_respuesta_gemini
#from ia_openai import obtener_respuesta_chatgpt 
#from ia_claude import obtener_respuesta_claude
#from ia_cohere import obtener_respuesta_cohere
from orquestador import obtener_respuesta_unificada  


from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file
import io
from flask import send_from_directory
import os

#from mensajeria import enviar_email

#from flask_mail import Mail, Message
#from itsdangerous import URLSafeTimedSerializer
#from werkzeug.security import generate_password_hash

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

#mail = Mail(app)
#app = Flask(__name__)
#mail.init_app(app) 
#------------------------------------------------
#import random
#import string
#from datetime import datetime, timedelta

# Diccionario en memoria para tokens
#reset_tokens = {}

# Ruta para enviar enlace de recuperación
#@app.route("/api/enviar-enlace-recuperacion", methods=["POST"])
#def enviar_enlace_recuperacion():
#    data = request.get_json()
#    email = data.get("email")
#
#    if not email:
#        return jsonify({"message": "Correo es obligatorio"}), 400

    # Aquí deberías buscar si el correo está registrado (puedes hacer una consulta en la base de datos)
    # Suponiendo que el correo está registrado...

    # Generar token aleatorio
#    token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
#    reset_tokens[token] = {
#        "email": email,
#        "expira": datetime.now() + timedelta(minutes=30)
#    }

    # Construir enlace de recuperación
#    enlace = f"http://localhost:5000/reset_password.html?token={token}"

    # Enviar correo
#    asunto = "Recuperación de contraseña"
#    mensaje = f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n{enlace}\n\nEste enlace expira en 30 minutos."

#    enviar_email(email, asunto, mensaje)  # función que tú ya tienes

#    return jsonify({"message": "Se ha enviado un enlace a tu correo electrónico."})


# ---------- Configuración del correo ----------
#app.config['SECRET_KEY'] = 'clave-secreta'  # cambia esto por algo seguro
#app.config['MAIL_SERVER'] = 'smtp.gmail.com'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USERNAME'] = 'tuhackerfav9@gmail.com'  # cambia esto
#app.config['MAIL_PASSWORD'] = 'nkmw ecsx yqnt qqsj'  # clave generada en Google
#app.config['MAIL_DEFAULT_SENDER'] = 'tuhackerfav9@gmail.com'

#mail = Mail(app)
#serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

#-----------------------------preguntas------

@app.route('/preguntas', methods=['POST'])
def insertar_pregunta():
    try:
        data = request.json
        id_usuario = data['id_usuario']
        id_sesion = data.get('id_sesion')  # <-- Nuevo
        pregunta_texto = data['pregunta']

        conn = get_connection()
        cursor = conn.cursor()

        # Insertar pregunta con id_sesion
        sql = "INSERT INTO preguntas (id_usuario, pregunta, id_sesion) VALUES (%s, %s, %s)"
        cursor.execute(sql, (id_usuario, pregunta_texto, id_sesion))
        pregunta_id = cursor.lastrowid
        conn.commit()

        # Llamar a la IA
        #respuesta_ia = obtener_respuesta_gemini(pregunta_texto)
        #respuesta_ia = obtener_respuesta_chatgpt(pregunta_texto)
        #respuesta_ia = obtener_respuesta_claude(pregunta_texto)
        #respuesta_ia = obtener_respuesta_cohere(pregunta_texto)
        #respuesta_ia = obtener_respuesta_unificada(pregunta_texto)
        #respuesta_ia = obtener_respuesta_unificada(pregunta_texto, id_sesion)# ya piensa solo
        respuesta_ia = obtener_respuesta_unificada(pregunta_texto, id_usuario, id_sesion)


        # Insertar respuesta con id_sesion
        sql_respuesta = "INSERT INTO respuestas (id_pregunta, origen_ia, respuesta, id_sesion) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_respuesta, (pregunta_id, 'IA Unificada', respuesta_ia, id_sesion))
        #cursor.execute(sql_respuesta, (pregunta_id, 'Cohere', respuesta_ia, id_sesion))
        #cursor.execute(sql_respuesta, (pregunta_id, 'chatgpt', respuesta_ia, id_sesion))
        #cursor.execute(sql_respuesta, (pregunta_id, 'Gemini', respuesta_ia, id_sesion))
        #cursor.execute(sql_respuesta, (pregunta_id, 'Claude', respuesta_ia, id_sesion))
        conn.commit()

        return jsonify({
            "message": "Pregunta y respuesta guardadas correctamente",
            "respuesta": respuesta_ia
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#------------------------historial--------
@app.route('/historial/<int:id_usuario>/<int:id_sesion>', methods=['GET'])
def obtener_historial(id_usuario, id_sesion):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT p.pregunta, r.respuesta, p.fecha_pregunta
            FROM preguntas p
            JOIN respuestas r ON p.id = r.id_pregunta
            WHERE p.id_usuario = %s AND p.id_sesion = %s
            ORDER BY p.fecha_pregunta ASC
        """
        cursor.execute(sql, (id_usuario, id_sesion))
        historial = cursor.fetchall()

        return jsonify(historial), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#-------------crear secion-----------

@app.route('/crear_sesion', methods=['POST'])
def crear_sesion():
    try:
        data = request.json
        id_usuario = data['id_usuario']
        nombre_sesion = data.get('nombre_sesion', 'Nuevo chat')

        conn = get_connection()
        cursor = conn.cursor()

        sql = "INSERT INTO sesiones (id_usuario, nombre_sesion) VALUES (%s, %s)"
        cursor.execute(sql, (id_usuario, nombre_sesion))
        conn.commit()

        # Obtiene el ID de la nueva sesión
        id_sesion = cursor.lastrowid

        return jsonify({"message": "Sesión creada correctamente", "id_sesion": id_sesion}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#-------------------listar secion pro usuario------------------
@app.route('/listar_sesiones/<int:id_usuario>', methods=['GET'])
def listar_sesiones(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT id, nombre_sesion, fecha_creacion FROM sesiones WHERE id_usuario = %s ORDER BY fecha_creacion DESC"
        cursor.execute(sql, (id_usuario,))
        sesiones = cursor.fetchall()

        return jsonify(sesiones), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#-----------------------rutas--------------

@app.route('/<path:filename>')
def servir_frontend(filename):
    return send_from_directory('../frontend', filename)

#@app.route('/preguntas')
#def ruta_preguntas():
#    return send_from_directory('../frontend', 'preguntas.html')
#
#@app.route('/registro')
#def ruta_registro():
#    return send_from_directory('../frontend', 'registro.html')
#
#@app.route('/index')
#def ruta_index():
#    return send_from_directory('../frontend', 'index.html')

#-----------------------exportar archivos txt--------------

@app.route('/exportar/<int:id_usuario>', methods=['GET'])
def exportar_historial(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener todas las preguntas y respuestas de este usuario
        sql = """
            SELECT p.pregunta, r.respuesta
            FROM preguntas p
            JOIN respuestas r ON p.id = r.id_pregunta
            WHERE p.id_usuario = %s
            ORDER BY p.fecha_pregunta ASC
        """
        cursor.execute(sql, (id_usuario,))
        historial = cursor.fetchall()

        # Crear el contenido del archivo
        contenido = f"Historial de Preguntas y Respuestas - Usuario {id_usuario}\n\n"
        for item in historial:
            contenido += f"Pregunta: {item['pregunta']}\n"
            contenido += f"Respuesta IA: {item['respuesta']}\n"
            contenido += "-"*50 + "\n"

        # Convertir a archivo .txt en memoria
        buffer = io.BytesIO()
        buffer.write(contenido.encode('utf-8'))
        buffer.seek(0)

        return send_file(buffer, as_attachment=True, download_name=f"historial_usuario_{id_usuario}.txt", mimetype='text/plain')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------registro-----------
@app.route('/registro', methods=['POST'])
def registro():
    try:
        data = request.json
        nombre_usuario = data['nombre_usuario']
        correo = data['correo']
        contrasena = data['contrasena']

        password_hash = generate_password_hash(contrasena)

        conn = get_connection()
        cursor = conn.cursor()

        sql = "INSERT INTO usuarios (nombre_usuario, correo, contrasena) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre_usuario, correo, password_hash))
        conn.commit()

        return jsonify({"message": "Usuario registrado con éxito"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ------------------------login------------

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        correo = data['correo']
        contrasena = data['contrasena']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT * FROM usuarios WHERE correo = %s"
        cursor.execute(sql, (correo,))
        usuario = cursor.fetchone()

        if usuario and check_password_hash(usuario['contrasena'], contrasena):
            return jsonify({
                "message": "Login exitoso",
                "id_usuario": usuario['id'],
                "nombre_usuario": usuario['nombre_usuario']  # <-- AÑADE ESTO
            }), 200

        else:
            return jsonify({"error": "Credenciales inválidas"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
  
# ------------------------ Editar Credenciales ------------------------

@app.route('/editar_usuario/<int:id_usuario>', methods=['PUT'])
def editar_usuario(id_usuario):
    try:
        data = request.json
        nombre_usuario = data.get('nombre_usuario')
        correo = data.get('correo')
        contrasena = data.get('contrasena')

        if not nombre_usuario or not correo:
            return jsonify({"error": "Nombre y correo son obligatorios"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        if contrasena:  # Si quiere cambiar la contraseña
            password_hash = generate_password_hash(contrasena)
            sql = """
                UPDATE usuarios
                SET nombre_usuario = %s, correo = %s, contrasena = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nombre_usuario, correo, password_hash, id_usuario))
        else:  # Si no cambia contraseña, deja la anterior
            sql = """
                UPDATE usuarios
                SET nombre_usuario = %s, correo = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nombre_usuario, correo, id_usuario))

        conn.commit()
        return jsonify({"message": "Usuario actualizado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------ Obtener Datos de un Usuario ------------------------

@app.route('/obtener_usuario/<int:id_usuario>', methods=['GET'])
def obtener_usuario(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT nombre_usuario, correo FROM usuarios WHERE id = %s"
        cursor.execute(sql, (id_usuario,))
        usuario = cursor.fetchone()

        if usuario:
            return jsonify(usuario), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------
#from flask import Flask, request, jsonify
#from flask_mail import Mail, Message
#from itsdangerous import URLSafeTimedSerializer
#from werkzeug.security import generate_password_hash
#from app.db import get_connection  # Asegúrate que esta función esté bien definida

#app = Flask(__name__)


# ---------- Ruta para enviar enlace ----------
#@app.route('/enviar_reset', methods=['POST'])
#def enviar_reset():
#    data = request.json
#    correo = data.get('correo')
#
#    if not correo:
#        return jsonify({"error": "Correo requerido"}), 400
#
#    conn = get_connection()
#    cursor = conn.cursor()
#    cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
#    usuario = cursor.fetchone()
#
#    if not usuario:
#        return jsonify({"error": "Correo no registrado"}), 404
#
#    token = serializer.dumps(correo, salt='recuperar-contrasena')
#    enlace = f"http://localhost:5000/reset_password/{token}"  # O tu dominio
#
#    msg = Message("Recuperar tu contraseña", recipients=[correo])
#    msg.body = f"Hola,\n\nHaz clic en el siguiente enlace para recuperar tu contraseña:\n{enlace}\n\nEste enlace expira en 1 hora."
#    mail.send(msg)
#
#    return jsonify({"message": "Correo de recuperación enviado"}), 200

# ---------- Ruta para cambiar contraseña con token ----------
#@app.route('/reset_password/<token>', methods=['POST'])
#def reset_password(token):
#    try:
#        correo = serializer.loads(token, salt='recuperar-contrasena', max_age=3600)
#    except Exception:
#        return jsonify({"error": "Token inválido o expirado"}), 400
#
#    data = request.json
#    nueva_contrasena = data.get('nueva_contrasena')
#
#    if not nueva_contrasena:
#        return jsonify({"error": "Contraseña requerida"}), 400
#
#    hash = generate_password_hash(nueva_contrasena)
#    conn = get_connection()
#    cursor = conn.cursor()
#    cursor.execute("UPDATE usuarios SET contrasena = %s WHERE correo = %s", (hash, correo))
#    conn.commit()
#
#    return jsonify({"message": "Contraseña actualizada correctamente"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
