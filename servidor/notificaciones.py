# notificaciones.py
import smtplib
import logging
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from tkinter import messagebox
import tempfile
from pathlib import Path

class Notificador:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.notificaciones_activas = bool(config.SMTP_USER and config.SMTP_PASSWORD)
    
# En servidor/notificaciones.py

    def enviar(self, destinatario, asunto, mensaje, archivos_adjuntos=None):
        """Envía notificación por correo"""
        if not self.notificaciones_activas:
            self.logger.warning(f"Notificaciones desactivadas - No se envió a {destinatario}")
            return False
        
        if archivos_adjuntos is None:
            archivos_adjuntos = []
        elif isinstance(archivos_adjuntos, str):
            archivos_adjuntos = [archivos_adjuntos]
        
        def enviar_thread():
            try:
                msg = MIMEMultipart()
                msg['From'] = self.config.SMTP_USER
                msg['To'] = destinatario
                msg['Subject'] = asunto
                msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))
                
                # Adjuntar archivos
                adjuntos_validos = 0
                for archivo in archivos_adjuntos:
                    if archivo and os.path.exists(archivo):
                        with open(archivo, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{os.path.basename(archivo)}"'
                            )
                            msg.attach(part)
                            adjuntos_validos += 1
                
                # Enviar
                server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT, timeout=30)
                server.starttls()
                server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
                server.send_message(msg)
                server.quit()
                
                self.logger.info(f"Correo enviado a {destinatario} con {adjuntos_validos} adjuntos")
                
            except Exception as e:
                self.logger.error(f"Error enviando correo: {e}")
        
        thread = threading.Thread(target=enviar_thread, daemon=True)
        thread.start()
        return True
    
    def enviar_asignacion(self, usuario, oficio, mensaje_adicional="", adjuntar_archivo=False, contenido_archivo=None, nombre_archivo=None):
        """Envía notificación de asignación de oficio con archivo adjunto"""
        if not usuario.get('email'):
            self.logger.warning(f"Usuario {usuario['nombre_completo']} no tiene email configurado")
            return False
        
        asunto = f"Nuevo oficio asignado: {oficio['numero_oficio']}"
        
        # ✅ MENSAJE CORREGIDO - SIN DUPLICACIÓN
        mensaje = f"""
Hola {usuario['nombre_completo']},

Se le ha asignado un nuevo oficio:

Número: {oficio['numero_oficio']}
Asunto: {oficio['asunto']}
Remitente: {mensaje_adicional.split('Remitente: ')[1] if 'Remitente: ' in mensaje_adicional else 'No especificado'}

Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Para ver el detalle, ingrese al sistema.

Saludos cordiales,
Administración del Sistema
"""
        
        archivos = []
        if adjuntar_archivo and contenido_archivo:
            try:
                # Crear archivo temporal para adjuntar
                temp_dir = Path(tempfile.gettempdir()) / "gestion_oficios_adjuntos"
                temp_dir.mkdir(exist_ok=True)
                
                nombre_final = nombre_archivo or f"oficio_{oficio['id']}.pdf"
                archivo_temp = temp_dir / nombre_final
                
                with open(archivo_temp, 'wb') as f:
                    f.write(contenido_archivo)
                
                archivos.append(str(archivo_temp))
                self.logger.info(f"Archivo temporal creado para adjuntar: {archivo_temp}")
                
            except Exception as e:
                self.logger.error(f"Error creando archivo temporal: {e}")
        
        return self.enviar(usuario['email'], asunto, mensaje, archivos)
    
    def enviar_prueba(self, usuario):
        """Envía correo de prueba"""
        if not usuario.get('email'):
            messagebox.showwarning("Correo", "El usuario no tiene email configurado")
            return False
        
        asunto = "Prueba de configuración de correo"
        mensaje = f"""
Hola {usuario['nombre_completo']},

Este es un correo de prueba del sistema de gestión de oficios.

Configuración SMTP:
- Servidor: {self.config.SMTP_SERVER}
- Puerto: {self.config.SMTP_PORT}
- Usuario: {self.config.SMTP_USER}

Si recibes este mensaje, la configuración es correcta.

Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Saludos.
"""
        return self.enviar(usuario['email'], asunto, mensaje)