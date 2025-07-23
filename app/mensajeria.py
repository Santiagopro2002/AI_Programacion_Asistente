# mensajeria.py

from flask_mail import Message
from flask import current_app
from main import mail  # Asegúrate de que 'main.py' tiene la instancia mail = Mail(app)

def enviar_email(destinatario, asunto, cuerpo):
    """
    Envía un correo electrónico al destinatario especificado.
    
    :param destinatario: Dirección de correo del receptor
    :param asunto: Asunto del mensaje
    :param cuerpo: Cuerpo del mensaje (texto plano)
    """
    try:
        with current_app.app_context():
            msg = Message(
                subject=asunto,
                recipients=[destinatario],
                body=cuerpo,
                sender=current_app.config.get("MAIL_USERNAME")  # Usa el remitente configurado
            )
            mail.send(msg)
            print(f"[OK] Correo enviado a {destinatario}")
    except Exception as e:
        print(f"[ERROR] Fallo al enviar correo: {e}")
        raise
