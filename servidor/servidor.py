#!/usr/bin/env python
"""
SERVIDOR DE GESTIÓN DE OFICIOS - VERSIÓN MODULAR
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime, timedelta  # ✅ IMPORTACIÓN CORREGIDA
from pathlib import Path
from dotenv import load_dotenv

# Módulos propios
from .config import Config
from .database import DatabaseManager
from .notificaciones import Notificador
from .archivos_gestion import ArchivosGestion
from .graficas import GraficasManager
from .oficios_gestion import GestionOficios
from .usuarios_gestion import GestionUsuarios
from .login import LoginDialog
from .recepcion import RecepcionTab

load_dotenv()

class ServidorOficios:
    def __init__(self):
        # Configuración
        self.config = Config
        self.config.crear_carpetas()
        
        # Logging
        log_file = self.config.LOG_FILE
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=log_file,
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Base de datos
        self.db = DatabaseManager()
        if not self.db.conectar():
            messagebox.showerror("Error", "No se pudo conectar a la BD")
            sys.exit(1)
        
        # Módulos
        self.notificador = Notificador(self.config)
        self.archivos_gestion = ArchivosGestion(self.db, self.config)
        
        # Ventana principal
        self.root = tk.Tk()
        self.root.title("CONTROL DE OFICIOS - SERVIDOR")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')
        
        self.usuario_actual = None
        
        # Variables
        self.filtro_estado = tk.StringVar(value="Todos")
        self.filtro_usuario = tk.StringVar(value="Todos")
        self.busqueda = tk.StringVar()
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def run(self):
        """Ejecuta la aplicación"""
        # Login
        login = LoginDialog(self.root, self.db)  # Pasa root como padre
        self.root.wait_window(login)
        
        if login.usuario:
            self.usuario_actual = login.usuario
            self.mostrar_principal()
            self.root.mainloop()
        else:
            self.root.destroy()
        
        self.db.cerrar()
    
    def login(self):
        """Ventana de login"""
        login_win = tk.Toplevel(self.root)
        login_win.title("Login Administrador")
        login_win.geometry("400x350")
        login_win.transient(self.root)
        login_win.grab_set()
        
        # Centrar
        login_win.update_idletasks()
        x = (login_win.winfo_screenwidth() // 2) - (400 // 2)
        y = (login_win.winfo_screenheight() // 2) - (350 // 2)
        login_win.geometry(f'+{x}+{y}')
        
        frame = ttk.Frame(login_win, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="CONTROL DE OFICIOS", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Estado de notificaciones
        if self.notificador.notificaciones_activas:
            ttk.Label(frame, text="✅ Notificaciones activas", 
                     foreground="green").pack()
        else:
            ttk.Label(frame, text="⚠️ Notificaciones desactivadas", 
                     foreground="orange").pack()
        
        ttk.Label(frame, text="Inicio de Sesión - Administrador",
                 font=('Arial', 10)).pack(pady=10)
        
        ttk.Label(frame, text="Usuario:").pack(anchor=tk.W, pady=(10,0))
        username = ttk.Entry(frame, width=30)
        username.pack(fill=tk.X, pady=5)
        username.focus()
        
        ttk.Label(frame, text="Contraseña:").pack(anchor=tk.W, pady=(10,0))
        password = ttk.Entry(frame, width=30, show="*")
        password.pack(fill=tk.X, pady=5)
        
        def validar():
            user_val = username.get()
            pass_val = password.get()
            
            self.db.cursor.execute("""
                SELECT * FROM usuarios 
                WHERE username = %s AND password = %s AND activo = TRUE AND es_admin = TRUE
            """, (user_val, pass_val))
            
            usuario = self.db.cursor.fetchone()
            if usuario:
                self.usuario_actual = usuario
                
                # Registrar sesión
                import secrets
                token = secrets.token_urlsafe(32)
                self.db.cursor.execute("""
                    INSERT INTO sesiones_activas 
                    (usuario_id, token_sesion, dispositivo, ip_address, fecha_expiracion, activa)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                """, (usuario['id'], token, "Servidor Admin", 'localhost', 
                      datetime.now() + timedelta(hours=8)))  # ✅ AHORA timedelta ESTÁ DEFINIDO
                
                login_win.destroy()
                self.mostrar_principal()
                self.logger.info(f"Login admin exitoso: {user_val}")
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos, o no es administrador")
        
        password.bind('<Return>', lambda e: validar())
        ttk.Button(frame, text="Ingresar", command=validar).pack(pady=20)
        
        self.root.wait_window(login_win)
    
    # En servidor.py - Modificar mostrar_principal()

    def mostrar_principal(self):
        """Ventana principal del administrador"""
        # Limpiar
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Barra título (igual)
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, 
                text=f"SERVIDOR DE OFICIOS - ADMIN: {self.usuario_actual['nombre_completo']}", 
                fg='white', bg='#2c3e50', font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=20, pady=10)
        
        if self.notificador.notificaciones_activas:
            tk.Label(title_frame, text="📧 Notificaciones activas", 
                    fg='lightgreen', bg='#2c3e50', font=('Arial', 10)).pack(side=tk.RIGHT, padx=20)
        else:
            tk.Label(title_frame, text="⚠️ Notificaciones desactivadas", 
                    fg='yellow', bg='#2c3e50', font=('Arial', 10)).pack(side=tk.RIGHT, padx=20)
        
        # Menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Importar archivos históricos", command=self.importar_historicos)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Probar correo", command=self.probar_correo)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.quit)

        # ✅ MENÚ AYUDA CON ACERCA DE
        ayuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
        ayuda_menu.add_command(label="Acerca de", command=self.acerca_de)
        
        # Notebook principal
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña 1: RECEPCIÓN
        from .recepcion import RecepcionTab
        self.recepcion_tab = RecepcionTab(notebook, self.db, self.usuario_actual, self.config, self.archivos_gestion)
        
        # Pestaña 2: GESTIÓN DE OFICIOS
        from .oficios_gestion import GestionOficios
        self.oficios_gestion = GestionOficios(self.root, self.db, self.usuario_actual, 
                                            self.config, self.notificador, self.archivos_gestion)
        self.oficios_gestion.crear_pestana(notebook)
        
        # Pestaña 3: REPORTES GRÁFICOS
        from .graficas import GraficasManager
        self.graficas = GraficasManager(self.db)
        self.graficas.crear_pestana(notebook)
        
        # Pestaña 4: USUARIOS
        from .usuarios_gestion import GestionUsuarios
        self.usuarios_gestion = GestionUsuarios(self.root, self.db, self.usuario_actual)
        self.usuarios_gestion.crear_pestana(notebook)
        
        # ✅ Evento para actualizar al cambiar de pestaña
        def on_tab_change(event):
            current_tab = notebook.index(notebook.select())
            if current_tab == 0:  # Recepción
                if hasattr(self, 'recepcion_tab'):
                    self.recepcion_tab.actualizar_lista()
            elif current_tab == 1:  # Gestión de oficios
                if hasattr(self, 'oficios_gestion'):
                    self.oficios_gestion.cargar_oficios()
            elif current_tab == 2:  # Gráficas
                if hasattr(self, 'graficas'):
                    self.graficas.actualizar_graficas()
            elif current_tab == 3:  # Usuarios
                if hasattr(self, 'usuarios_gestion'):
                    self.usuarios_gestion.cargar_usuarios()
            
            self.status_label.config(text=f"Actualizado: {datetime.now().strftime('%H:%M:%S')}")
        
        notebook.bind('<<NotebookTabChanged>>', on_tab_change)
        
        # Barra de estado
        status_frame = tk.Frame(self.root, bg='#34495e', height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_frame, 
                                    text=f"Servidor: {self.config.SERVER_IP} | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                    fg='white', bg='#34495e', anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10)

    
    def acerca_de(self):
        """Muestra información acerca del sistema"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de - Servidor de Oficios")
        about_window.geometry("600x550")
        about_window.transient(self.root)
        about_window.grab_set()
        about_window.resizable(False, False)
        
        # Centrar
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (about_window.winfo_screenheight() // 2) - (550 // 2)
        about_window.geometry(f'+{x}+{y}')
        
        # Canvas con scroll
        canvas = tk.Canvas(about_window)
        scrollbar = ttk.Scrollbar(about_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenido dentro del scroll
        frame = ttk.Frame(scrollable_frame, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="SERVIDOR DE OFICIOS", font=('Arial', 18, 'bold')).pack(pady=10)
        ttk.Label(frame, text="Sistema de administración de oficios", font=('Arial', 10)).pack()
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Información
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text="Versión:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text="2.0.0").grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(info_frame, text="Desarrollado por:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text="PythonMakerTools").grid(row=1, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(info_frame, text="Contacto:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text="L.S.C. José Jesús Hernández Hernández").grid(row=2, column=1, sticky=tk.W, padx=10)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Estado de desarrollo
        dev_frame = ttk.Frame(frame)
        dev_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(dev_frame, text="⚠️ Estado:", font=('Arial', 10, 'bold'), foreground='orange').grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(dev_frame, text="Aplicación en Desarrollo", font=('Arial', 10), foreground='orange').grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Reporte de errores y recomendaciones
        reporte_frame = ttk.LabelFrame(frame, text="📧 Reportar Problemas o Sugerencias", padding=10)
        reporte_frame.pack(fill=tk.X, pady=10)
        
        # Información del remitente (usuario actual)
        remitente_info = ttk.Frame(reporte_frame)
        remitente_info.pack(fill=tk.X, pady=5)
        
        ttk.Label(remitente_info, text="Enviado por:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Label(remitente_info, text=f"{self.usuario_actual['nombre_completo']} ({self.usuario_actual['email'] or 'sin email'})", 
                font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        mensaje_reporte = tk.Text(reporte_frame, height=5, width=50, font=('Arial', 9))
        mensaje_reporte.pack(fill=tk.BOTH, pady=5)
        mensaje_reporte.insert(tk.END, "Describe el error o recomendación aquí...")
        
        # Frame para instrucciones
        instrucciones_frame = ttk.Frame(reporte_frame)
        instrucciones_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(instrucciones_frame, text="📸 Recomendación:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        ttk.Label(instrucciones_frame, text="Adjuntar captura de pantalla del error en el correo de confirmación", 
                font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        
        # Variable para estado de envío
        enviando = tk.BooleanVar(value=False)
        
        # Función para enviar reporte usando el Notificador
        def enviar_reporte():
            if enviando.get():
                messagebox.showinfo("Info", "Ya se está enviando un reporte, espere un momento...")
                return
            
            mensaje = mensaje_reporte.get("1.0", tk.END).strip()
            
            if not mensaje or mensaje == "Describe el error o recomendación aquí...":
                messagebox.showwarning("Campo Vacío", 
                                    "Por favor escribe una descripción del error o recomendación antes de enviar.")
                return
            
            enviando.set(True)
            
            # Crear el cuerpo del correo
            asunto = f"[REPORTE] Servidor - {self.usuario_actual['nombre_completo']}"
            cuerpo = f"""
    Reporte enviado desde el Servidor de Gestión de Oficios

    ----------------------------------------------------------------
    DATOS DEL REPORTE
    ----------------------------------------------------------------
    Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    Usuario: {self.usuario_actual['nombre_completo']} (ID: {self.usuario_actual['id']})
    Email: {self.usuario_actual['email'] or 'No configurado'}
    Versión: 2.0.0

    ----------------------------------------------------------------
    MENSAJE
    ----------------------------------------------------------------
    {mensaje}

    ----------------------------------------------------------------
    FIN DEL REPORTE
    ----------------------------------------------------------------
    """
            
            # Usar el Notificador
            try:
                if not self.notificador.notificaciones_activas:
                    respuesta = messagebox.askyesno(
                        "Notificaciones desactivadas",
                        "La configuración de correo no está activa.\n\n"
                        "¿Desea abrir su cliente de correo para enviar el reporte manualmente?"
                    )
                    if respuesta:
                        import webbrowser
                        import urllib.parse
                        destinatario = "pythonmakertools@gmail.com"
                        asunto_codificado = urllib.parse.quote(asunto)
                        cuerpo_codificado = urllib.parse.quote(cuerpo)
                        url = f"mailto:{destinatario}?subject={asunto_codificado}&body={cuerpo_codificado}"
                        webbrowser.open(url)
                        messagebox.showinfo("Reporte", "Se ha abierto su cliente de correo.\n\n"
                                        "Por favor, adjunte la captura de pantalla si es necesario y envíe el correo.")
                    enviando.set(False)
                    return
                
                # Mostrar indicador de envío
                btn_enviar.config(text="📧 Enviando...", state='disabled')
                about_window.update_idletasks()
                
                # Enviar correo
                exito = self.notificador.enviar(
                    destinatario="pythonmakertools@gmail.com",
                    asunto=asunto,
                    mensaje=cuerpo,
                    archivos_adjuntos=[]
                )
                
                if exito:
                    messagebox.showinfo("Reporte Enviado", 
                                    "Su reporte ha sido enviado correctamente.\n\n"
                                    "¡Gracias por ayudarnos a mejorar la aplicación!")
                    mensaje_reporte.delete("1.0", tk.END)
                    mensaje_reporte.insert(tk.END, "Describe el error o recomendación aquí...")
                else:
                    messagebox.showerror("Error de envío", 
                                        "No se pudo enviar el reporte.\n\n"
                                        "Verifique la configuración de correo o intente más tarde.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al enviar reporte: {e}")
            finally:
                enviando.set(False)
                btn_enviar.config(text="📧 Enviar Reporte", state='normal')
        
        # Frame para botones
        botones_frame = ttk.Frame(reporte_frame)
        botones_frame.pack(fill=tk.X, pady=10)
        
        btn_enviar = ttk.Button(botones_frame, text="📧 Enviar Reporte", command=enviar_reporte, width=20)
        btn_enviar.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(botones_frame, text="🗑️ Limpiar", 
                command=lambda: [mensaje_reporte.delete("1.0", tk.END), 
                                mensaje_reporte.insert(tk.END, "Describe el error o recomendación aquí...")], 
                width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        ttk.Label(frame, text="© 2024 - Todos los derechos reservados", font=('Arial', 9), foreground='gray').pack()
        
        # Frame para botón cerrar
        cerrar_frame = ttk.Frame(frame)
        cerrar_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(cerrar_frame, text="Cerrar", command=about_window.destroy, width=15).pack()

    def importar_historicos(self):
        """Abre diálogo para importar archivos históricos"""
        from .dialogs.importar_historicos import DialogoImportarHistoricos
        dialog = DialogoImportarHistoricos(self.root, self.db, self.usuario_actual, self.archivos_gestion)
    
    def actualizar_todo(self):
        """Actualiza todas las vistas"""
        if hasattr(self, 'oficios_gestion'):
            self.oficios_gestion.cargar_oficios()
        if hasattr(self, 'graficas'):
            self.graficas.actualizar_graficas()
        if hasattr(self, 'usuarios_gestion'):
            self.usuarios_gestion.cargar_usuarios()
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"Actualizado: {datetime.now().strftime('%H:%M:%S')}")
    
    def probar_correo(self):
        """Prueba el envío de correos"""
        if not self.notificador.notificaciones_activas:
            messagebox.showwarning("Correo", "Notificaciones desactivadas")
            return
        
        self.notificador.enviar_prueba(self.usuario_actual)

def main():
    app = ServidorOficios()
    app.run()

if __name__ == "__main__":
    main()