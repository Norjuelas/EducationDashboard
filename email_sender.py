import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import datetime

# Cargar variables de entorno del archivo .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_task_reminder_email(receiver_email, task_name, responsible_name, due_date):
    """
    Envía un correo de recordatorio para una tarea específica.

    Args:
        receiver_email (str): El correo del responsable de la tarea.
        task_name (str): El nombre de la tarea.
        responsible_name (str): El nombre del responsable.
        due_date (datetime): La fecha de vencimiento de la tarea.

    Returns:
        bool: True si el correo se envió con éxito, False en caso contrario.
    """
    # Credenciales de correo desde variables de entorno
    sender_email = os.environ.get("EMAIL_SENDER")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    # Verificación de configuración básica
    if not all([sender_email, smtp_username, smtp_password]):
        logger.error("La configuración de correo está incompleta. Revisa las variables de entorno.")
        return False

    if not receiver_email or '@' not in receiver_email:
        logger.error(f"Correo del destinatario inválido: {receiver_email}")
        return False

    # Crear el mensaje
    message = MIMEMultipart()
    message["Subject"] = f"Recordatorio: Tarea Pendiente - {task_name}"
    message["From"] = f"Gestor de Proyectos <{sender_email}>"
    message["To"] = receiver_email
    year = datetime.datetime.now().year

    # --- CUERPO DEL CORREO EN HTML ---
    # Este es el template que solicita la confirmación y el archivo de comprobación.
    email_body_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); overflow: hidden; }}
            .header {{ background-color: #004AAD; color: #ffffff; padding: 20px; text-align: center; }}
            .header h2 {{ margin: 0; }}
            .content {{ padding: 30px; line-height: 1.6; color: #333333; }}
            .task-details {{ background-color: #f9f9f9; border-left: 4px solid #004AAD; padding: 15px; margin: 20px 0; }}
            .task-details p {{ margin: 5px 0; }}
            .footer {{ background-color: #f4f4f4; color: #777777; padding: 20px; text-align: center; font-size: 12px; }}
            .action-request {{ margin-top: 25px; padding: 15px; background-color: #FFFBEB; border: 1px solid #FFD600; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Recordatorio de Tarea Pendiente</h2>
            </div>
            <div class="content">
                <p>Hola {responsible_name},</p>
                <p>Este es un recordatorio amistoso sobre la siguiente tarea que tienes asignada:</p>
                
                <div class="task-details">
                    <p><strong>Tarea:</strong> {task_name}</p>
                    <p><strong>Fecha de Vencimiento:</strong> {due_date.strftime('%d de %B de %Y')}</p>
                </div>

                <div class="action-request">
                    <p><strong>Acción Requerida:</strong></p>
                    <p>Por favor, al finalizar la tarea, responde a este correo para <strong>confirmar que ha sido completada</strong> y adjunta cualquier <strong>archivo de comprobación</strong> relevante (captura de pantalla, documento, etc.).</p>
                </div>
                
                <p>Gracias por tu colaboración para mantener el proyecto en marcha.</p>
                <p>Saludos,<br>El Equipo de Gestión de Proyectos</p>
            </div>
            <div class="footer">
                <p>&copy; {year} Tu Compañía. Todos los derechos reservados.</p>
                <p>Este es un correo automático, pero puedes responder directamente para contactarnos.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    message.attach(MIMEText(email_body_html, "html"))

    # Enviar el correo
    try:
        logger.info(f"Intentando enviar recordatorio a {receiver_email} para la tarea '{task_name}'...")
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        logger.info(f"Recordatorio enviado con éxito a {receiver_email}.")
        return True
    except Exception as e:
        logger.error(f"Error al enviar el correo: {e}")
        return False