#!/usr/bin/env python
"""
CLIENTE DE GESTIÓN DE OFICIOS - VERSIÓN FINAL
Estados: En Proceso, Atendido, Archivado
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import secrets
from pathlib import Path
from dotenv import load_dotenv
import tempfile
import mimetypes
import platform
import subprocess

from pathlib import Path

# Asegurar que existe el directorio de configuración
config_dir = Path.home() / ".gestion_oficios"
config_dir.mkdir(exist_ok=True)

load_dotenv()

class ClienteOficios:
    def __init__(self):
        self.server_ip = os.getenv('SERVER_IP', 'localhost')
        self.db_config = {
            'host': self.server_ip,
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'gestion_oficios'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres123')
        }
        
        self.conn = None
        self.cursor = None
        self.usuario_actual = None
        self.token_file = Path.home() / '.gestion_oficios_token'
        
        self.root = tk.Tk()
        self.root.title("GESTIÓN DE OFICIOS - USUARIO")
        self.root.geometry("1300x750")
        self.root.configure(bg='#f0f0f0')
        
        self.filtro_estado = tk.StringVar(value="Todos")
        self.busqueda = tk.StringVar()
    
    def conectar_bd(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            return True
        except Exception as e:
            print(f"Error BD: {e}")
            return False
    
    def login(self):
        """Ventana de login"""
        login_win = tk.Toplevel(self.root)
        login_win.title("Login Usuario")
        login_win.geometry("450x350")
        login_win.transient(self.root)
        login_win.grab_set()
        
        # Centrar
        login_win.update_idletasks()
        x = (login_win.winfo_screenwidth() // 2) - (450 // 2)
        y = (login_win.winfo_screenheight() // 2) - (350 // 2)
        login_win.geometry(f'+{x}+{y}')
        
        frame = ttk.Frame(login_win, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="GESTIÓN DE OFICIOS", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Estado BD
        if self.conectar_bd():
            ttk.Label(frame, text="✅ Conectado a BD", 
                     foreground="green").pack()
        else:
            ttk.Label(frame, text="❌ Error de BD", 
                     foreground="red").pack()
            ttk.Button(frame, text="Reintentar", 
                      command=lambda: [login_win.destroy(), self.login()]).pack()
            return
        
        ttk.Label(frame, text="Usuario:", font=('Arial', 10)).pack(anchor=tk.W, pady=(15,0))
        username = ttk.Entry(frame, width=30, font=('Arial', 11))
        username.pack(fill=tk.X, pady=5)
        username.focus()
        
        ttk.Label(frame, text="Contraseña:", font=('Arial', 10)).pack(anchor=tk.W, pady=(10,0))
        password = ttk.Entry(frame, width=30, show="*", font=('Arial', 11))
        password.pack(fill=tk.X, pady=5)
        
        def validar():
            user_val = username.get()
            pass_val = password.get()
            
            self.cursor.execute("""
                SELECT * FROM usuarios 
                WHERE username = %s AND password = %s AND activo = TRUE
            """, (user_val, pass_val))
            
            usuario = self.cursor.fetchone()
            if usuario:
                self.usuario_actual = usuario
                
                # Guardar token
                token = secrets.token_urlsafe(32)
                self.cursor.execute("""
                    INSERT INTO sesiones_activas 
                    (usuario_id, token_sesion, fecha_expiracion, activa, dispositivo, ip_address)
                    VALUES (%s, %s, %s, TRUE, %s, %s)
                """, (usuario['id'], token, datetime.now() + timedelta(days=30), 
                      f"Cliente {os.environ.get('COMPUTERNAME', 'PC')}", 'localhost'))
                
                with open(self.token_file, 'w') as f:
                    f.write(token)
                login_win.destroy()
                self.mostrar_principal()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        
        password.bind('<Return>', lambda e: validar())
        ttk.Button(frame, text="Ingresar", command=validar, width=20).pack(pady=20)
        
        self.root.wait_window(login_win)
    
    # En cliente.py - Modificar mostrar_principal()

    def mostrar_principal(self):
        """Ventana principal del usuario"""
        # Limpiar
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Barra título
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, 
                text=f"GESTIÓN DE OFICIOS - {self.usuario_actual['nombre_completo']}", 
                fg='white', bg='#2c3e50', font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=20, pady=15)
        
        # Botón Mi Perfil
        ttk.Button(title_frame, text="👤 Mi Perfil", 
                command=self.mi_perfil).pack(side=tk.RIGHT, padx=10)
        
        # Menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Salir", command=self.root.quit)
        
        perfil_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Perfil", menu=perfil_menu)
        perfil_menu.add_command(label="Mi Perfil", command=self.mi_perfil)
        perfil_menu.add_command(label="Cambiar Contraseña", command=self.cambiar_mi_password)
        
        # ✅ MENÚ AYUDA CON ACERCA DE
        ayuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
        ayuda_menu.add_command(label="Acerca de", command=self.acerca_de)
        
        # Búsqueda
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Buscar:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        ttk.Entry(search_frame, textvariable=self.busqueda, width=35, font=('Arial', 11)).pack(side=tk.LEFT, padx=10)
        self.busqueda.trace('w', lambda *args: self.cargar_mis_oficios())
        
        # Notebook principal
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de oficios
        self.crear_pestana_oficios(notebook)
        
        # Pestaña de informales
        self.crear_pestana_informales(notebook)
        
        # Evento para actualizar al cambiar de pestaña
        def on_tab_change(event):
            current_tab = notebook.index(notebook.select())
            if current_tab == 0:
                self.cargar_mis_oficios()
            elif current_tab == 1:
                self.cargar_informales()
        
        notebook.bind('<<NotebookTabChanged>>', on_tab_change)
        
        # Barra de estado
        status_frame = tk.Frame(self.root, bg='#34495e', height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_frame, 
                                    text=f"Usuario: {self.usuario_actual['nombre_completo']} | Servidor: {self.server_ip}",
                                    fg='white', bg='#34495e', font=('Arial', 9), anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Cargar datos iniciales
        self.cargar_mis_oficios()
    
    def acerca_de(self):
        """Muestra información acerca del sistema"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de - Gestión de Oficios")
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
        ttk.Label(frame, text="GESTIÓN DE OFICIOS", font=('Arial', 18, 'bold')).pack(pady=10)
        ttk.Label(frame, text="Sistema de control y seguimiento de oficios", font=('Arial', 10)).pack()
        
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
            asunto = f"[REPORTE] Cliente - {self.usuario_actual['nombre_completo']}"
            cuerpo = f"""
    Reporte enviado desde el Cliente de Gestión de Oficios

    ----------------------------------------------------------------
    DATOS DEL REPORTE
    ----------------------------------------------------------------
    Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    Usuario: {self.usuario_actual['nombre_completo']} (ID: {self.usuario_actual['id']})
    Email: {self.usuario_actual['email'] or 'No configurado'}
    Servidor: {self.server_ip}
    Versión: 2.0.0

    ----------------------------------------------------------------
    MENSAJE
    ----------------------------------------------------------------
    {mensaje}

    ----------------------------------------------------------------
    FIN DEL REPORTE
    ----------------------------------------------------------------
    """
            
            # Usar el Notificador para enviar el correo
            # Importar desde servidor (puede necesitar ajuste de importación)
            try:
                # Intentar importar desde servidor
                import sys
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from servidor.config import Config
                from servidor.notificaciones import Notificador
                
                config = Config()
                notificador = Notificador(config)
                
                # Verificar si las notificaciones están activas
                if not notificador.notificaciones_activas:
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
                exito = notificador.enviar(
                    destinatario="pythonmakertools@gmail.com",
                    asunto=asunto,
                    mensaje=cuerpo,
                    archivos_adjuntos=[]
                )
                
                if exito:
                    messagebox.showinfo("Reporte Enviado", 
                                    "Su reporte ha sido enviado correctamente.\n\n"
                                    "¡Gracias por ayudarnos a mejorar la aplicación!")
                    # Limpiar el campo después de enviar
                    mensaje_reporte.delete("1.0", tk.END)
                    mensaje_reporte.insert(tk.END, "Describe el error o recomendación aquí...")
                else:
                    messagebox.showerror("Error de envío", 
                                        "No se pudo enviar el reporte.\n\n"
                                        "Verifique la configuración de correo o intente más tarde.")
                
            except ImportError:
                # Si no se puede importar, usar método alternativo con cliente de correo
                respuesta = messagebox.askyesno(
                    "Configuración no disponible",
                    "No se pudo cargar la configuración de correo.\n\n"
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

    ##########

    def crear_pestana_oficios(self, notebook):
        """Pestaña de oficios asignados"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📋 Mis Oficios")
        
        # Filtros
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(filter_frame, text="Filtrar por estado:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        estado_combo = ttk.Combobox(filter_frame, textvariable=self.filtro_estado,
                                values=['Todos', 'En Proceso', 'Atendido', 'Informativo'],
                                width=20, state='readonly', font=('Arial', 10))
        estado_combo.pack(side=tk.LEFT, padx=5)
        estado_combo.bind('<<ComboboxSelected>>', lambda e: self.cargar_mis_oficios())
        
        ttk.Button(filter_frame, text="🔄 Actualizar", 
                command=self.limpiar_filtros).pack(side=tk.LEFT, padx=20)
        
        # TreeView
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(tree_frame)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ✅ NUEVAS COLUMNAS CLIENTE
        columns = ('Número de Oficio', 'Fecha de Ingreso', 'Asunto', 'Estado', 'Prioridad', 'Nota')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set, xscrollcommand=hsb.set, height=20)
        
        widths = [150, 100, 400, 120, 90, 200]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.bind('<Double-Button-1>', self.ver_detalle)
        self.tree.bind('<Button-3>', self.mostrar_menu_contextual)
    
    def crear_pestana_informales(self, notebook):
        """Pestaña de oficios nuevos - con botón para crear"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📝 Oficios Nuevos")
        
        # Toolbar con botón para nuevo oficio
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(toolbar, text="➕ Nuevo Oficio", 
                command=self.abrir_formulario_nuevo_oficio,
                width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar, text="🔄 Actualizar", 
                command=self.cargar_informales,
                width=15).pack(side=tk.RIGHT, padx=5)
        
        # TreeView para lista de oficios nuevos
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(tree_frame)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ('ID', 'Número', 'Fecha Ingreso', 'Asunto', 'Canal', 'Estado', 'Fecha Respuesta')
        self.tree_informales = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                        yscrollcommand=vsb.set, height=15)
        
        widths = [50, 120, 100, 300, 100, 100, 100]
        for col, width in zip(columns, widths):
            self.tree_informales.heading(col, text=col)
            self.tree_informales.column(col, width=width)
        
        self.tree_informales.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree_informales.yview)
        
        # Double-click para ver detalle y marcar atendido
        self.tree_informales.bind('<Double-Button-1>', self.ver_detalle_informal)
        
        # Menú contextual para informales
        self.tree_informales.bind('<Button-3>', self.mostrar_menu_contextual_informal)
        
        # Cargar datos
        self.cargar_informales()

    def mostrar_menu_contextual_informal(self, event):
        """Muestra menú contextual para oficios informales"""
        item = self.tree_informales.identify_row(event.y)
        if not item:
            return
        
        self.tree_informales.selection_set(item)
        
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Ver detalle", command=self.ver_detalle_informal)
        context_menu.post(event.x_root, event.y_root)

    def abrir_formulario_nuevo_oficio(self):
        """Abre el formulario para registrar un nuevo oficio"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Registrar Nuevo Oficio")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, True)
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="REGISTRAR NUEVO OFICIO", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Canvas con scroll
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Campos
        row = 0
        
        # Número de Oficio
        tk.Label(scrollable_frame, text="Número de Oficio:*", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=8, padx=5)
        nuevo_numero = ttk.Entry(scrollable_frame, width=40, font=('Arial', 11))
        nuevo_numero.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W)
        row += 1
        
        # Fecha de Ingreso
        tk.Label(scrollable_frame, text="Fecha de Ingreso:*", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=8, padx=5)
        nuevo_fecha = ttk.Entry(scrollable_frame, width=40, font=('Arial', 11))
        nuevo_fecha.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W)
        nuevo_fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        row += 1
        
        # Asunto
        tk.Label(scrollable_frame, text="Asunto:*", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=8, padx=5)
        nuevo_asunto = tk.Text(scrollable_frame, height=4, width=40, font=('Arial', 11))
        nuevo_asunto.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W)
        row += 1
        
        # Canal
        tk.Label(scrollable_frame, text="Canal:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=8, padx=5)
        nuevo_canal = ttk.Combobox(scrollable_frame, values=['WhatsApp', 'Teléfono', 'Email', 'Presencial', 'Otro'],
                                width=37, font=('Arial', 11))
        nuevo_canal.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W)
        nuevo_canal.set('WhatsApp')
        row += 1
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ✅ FUNCIÓN GUARDAR CON INDENTACIÓN CORRECTA
        def guardar():
            numero = nuevo_numero.get().strip()
            fecha = nuevo_fecha.get().strip()
            asunto = nuevo_asunto.get('1.0', tk.END).strip()
            canal = nuevo_canal.get()
            
            if not numero or not asunto:
                messagebox.showerror("Error", "Complete los campos obligatorios (*)")
                return
            
            if not fecha:
                fecha = datetime.now().strftime('%Y-%m-%d')
            
            # Verificar conexión antes de ejecutar
            try:
                self.cursor.execute("SELECT 1")
            except Exception as e:
                messagebox.showerror("Error de conexión", 
                    "No se puede conectar al servidor.\n\n"
                    "Por favor, verifique que:\n"
                    "1. El servidor de base de datos esté activo\n"
                    "2. Su conexión a internet esté disponible\n"
                    "3. El servicio de PostgreSQL esté corriendo\n\n"
                    "Intente nuevamente más tarde.")
                return
            
            try:
                self.cursor.execute("""
                    INSERT INTO oficios_informales 
                    (usuario_id, numero_oficio, fecha_recepcion, asunto, canal, estado)
                    VALUES (%s, %s, %s, %s, %s, 'Pendiente')
                """, (self.usuario_actual['id'], numero, fecha, asunto, canal))
                
                messagebox.showinfo("Éxito", "Oficio registrado correctamente")
                dialog.destroy()
                self.cargar_informales()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
        
        ttk.Button(frame, text="💾 Guardar", command=guardar, width=20).pack(pady=15)
    
    def cargar_mis_oficios(self):
        """Carga los oficios del usuario actual con nota resumida"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        query = """
            SELECT o.*, u.nombre_completo as asignado_nombre,
                (SELECT COUNT(*) FROM archivos_binarios WHERE oficio_id = o.id AND tipo = 'oficio') as tiene_archivo,
                (SELECT COUNT(*) FROM archivos_binarios WHERE oficio_id = o.id AND tipo = 'acuse') as tiene_acuse,
                CASE 
                    WHEN o.estado = 'En Proceso' AND o.fecha_asignacion IS NOT NULL 
                    THEN EXTRACT(DAY FROM (NOW() - o.fecha_asignacion))
                    ELSE 0
                END as dias_proceso
            FROM oficios o 
            LEFT JOIN usuarios u ON o.usuario_asignado_id = u.id
            WHERE o.usuario_asignado_id = %s
        """
        params = [self.usuario_actual['id']]
        
        if self.filtro_estado.get() != "Todos":
            estado_filtro = self.filtro_estado.get()
            if estado_filtro == "Informativo":
                estado_filtro = "Archivado"
            query += " AND o.estado = %s"
            params.append(estado_filtro)
        
        if self.busqueda.get():
            query += " AND (o.numero_oficio ILIKE %s OR o.remitente ILIKE %s OR o.asunto ILIKE %s)"
            busqueda = f"%{self.busqueda.get()}%"
            params.extend([busqueda, busqueda, busqueda])
        
        query += " ORDER BY o.fecha_creacion DESC"
        
        self.cursor.execute(query, params)
        oficios = self.cursor.fetchall()
        
        for o in oficios:
            estado_mostrar = o['estado']
            if estado_mostrar == "Archivado":
                estado_mostrar = "Informativo"
            
            # ✅ NOTA RESUMIDA MEJORADA
            nota_completa = o['notas'] or ''
            nota_resumida = ""
            
            if nota_completa:
                # Verificar si es OMISIÓN
                if 'OMISIÓN' in nota_completa:
                    import re
                    match = re.search(r'Respuesta programada: (\d{4}-\d{2}-\d{2})', nota_completa)
                    if match:
                        nota_resumida = f"⚠️ OMISIÓN (resp: {match.group(1)})"
                    else:
                        nota_resumida = "⚠️ OMISIÓN"
                # Verificar si está ATENDIDO con oficio respuesta
                elif 'ATENDIDO' in nota_completa and o['oficio_respuesta'] and o['oficio_respuesta'] != 'PENDIENTE':
                    # Extraer solo el número de oficio respuesta
                    import re
                    match = re.search(r'Oficio respuesta: ([A-Z0-9\-]+)', nota_completa)
                    if match:
                        nota_resumida = f"✅ Atendido (resp: {match.group(1)})"
                    else:
                        nota_resumida = "✅ Atendido"
                # Si es Atendido normal sin omisión
                elif o['estado'] == 'Atendido' and o['oficio_respuesta']:
                    nota_resumida = f"✅ Atendido (resp: {o['oficio_respuesta'][:30]})"
                # Si es Atendido sin oficio respuesta
                elif o['estado'] == 'Atendido':
                    nota_resumida = "✅ Atendido"
                # Otros casos: mostrar primeros 40 caracteres
                else:
                    nota_resumida = nota_completa[:40] + ('...' if len(nota_completa) > 40 else '')
            
            tags = []
            if o['estado'] == 'Atendido':
                tags = ('atendido',)
            elif o['estado'] == 'En Proceso':
                tags = ('proceso',)
                if o['dias_proceso'] > 3:
                    tags = ('vencido',)
            elif o['estado'] == 'Archivado':
                tags = ('informativo',)
            
            self.tree.insert('', tk.END, values=(
                o['numero_oficio'],
                o['fecha_oficio'].strftime('%d/%m/%Y') if o['fecha_oficio'] else '',
                o['asunto'][:60] + ('...' if len(o['asunto']) > 60 else ''),
                estado_mostrar,
                o['prioridad'],
                nota_resumida
            ), tags=tags)
        
        self.tree.tag_configure('atendido', background='#d4edda')
        self.tree.tag_configure('proceso', background='#fff3cd')
        self.tree.tag_configure('vencido', background='#ffcccc')
        self.tree.tag_configure('informativo', background='#cce5ff')

    def cargar_informales(self):
        """Carga oficios informales"""
        for item in self.tree_informales.get_children():
            self.tree_informales.delete(item)
        
        self.cursor.execute("""
            SELECT id, numero_oficio, fecha_recepcion, asunto, canal, estado, fecha_respuesta
            FROM oficios_informales 
            WHERE usuario_id = %s 
            ORDER BY fecha_creacion DESC
        """, (self.usuario_actual['id'],))
        
        for o in self.cursor.fetchall():
            fecha_respuesta = o['fecha_respuesta'].strftime('%d/%m/%Y') if o['fecha_respuesta'] else ''
            
            self.tree_informales.insert('', tk.END, values=(
                o['id'],
                o['numero_oficio'] or '',
                o['fecha_recepcion'].strftime('%d/%m/%Y') if o['fecha_recepcion'] else '',
                o['asunto'][:50] + ('...' if len(o['asunto']) > 50 else ''),
                o['canal'],
                o['estado'],
                fecha_respuesta
            ))
    
    def ver_detalle_informal(self, event=None):
            """Muestra detalle de oficio informal con opciones de estado"""
            sel = self.tree_informales.selection()
            if not sel:
                return
            
            item = self.tree_informales.item(sel[0])
            oficio_id = item['values'][0]
            
            self.cursor.execute("""
                SELECT * FROM oficios_informales WHERE id = %s
            """, (oficio_id,))
            
            oficio = self.cursor.fetchone()
            
            if not oficio:
                messagebox.showerror("Error", "No se encontró el oficio")
                return
            
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Detalle de Oficio - {oficio['numero_oficio'] or 'Nuevo'}")
            dialog.geometry("550x600")
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.resizable(True, True)
            
            # Centrar
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
            y = (dialog.winfo_screenheight() // 2) - (600 // 2)
            dialog.geometry(f'+{x}+{y}')
            
            main_frame = ttk.Frame(dialog, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            ttk.Label(main_frame, text="DETALLE DE OFICIO", font=('Arial', 14, 'bold')).pack(pady=5)
            
            # Estado actual
            estado_color = {'Pendiente': 'orange', 'En Proceso': 'orange', 'Atendido': 'green', 'Archivado': 'gray'}
            color = estado_color.get(oficio['estado'], 'black')
            
            estado_frame = ttk.Frame(main_frame)
            estado_frame.pack(fill=tk.X, pady=10)
            ttk.Label(estado_frame, text="Estado:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
            ttk.Label(estado_frame, text=oficio['estado'], font=('Arial', 12, 'bold'),
                    foreground=color).pack(side=tk.LEFT, padx=10)
            
            # Datos del oficio
            datos_frame = ttk.LabelFrame(main_frame, text="Datos del Oficio", padding="10")
            datos_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            row = 0
            campos = [
                ('Número:', oficio['numero_oficio'] or 'No especificado'),
                ('Fecha Ingreso:', oficio['fecha_recepcion'].strftime('%d/%m/%Y') if oficio['fecha_recepcion'] else ''),
                ('Asunto:', oficio['asunto']),
                ('Canal:', oficio['canal']),
                ('Fecha Respuesta:', oficio['fecha_respuesta'].strftime('%d/%m/%Y %H:%M') if oficio['fecha_respuesta'] else 'Pendiente'),
            ]
            
            for label, valor in campos:
                ttk.Label(datos_frame, text=label, font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
                ttk.Label(datos_frame, text=valor, font=('Arial', 10), wraplength=350).grid(row=row, column=1, sticky=tk.W, pady=5, padx=10)
                row += 1
            
            # Sección de acciones
            if oficio['estado'] != 'Atendido':
                acciones_frame = ttk.LabelFrame(main_frame, text="Cambiar Estado", padding="10")
                acciones_frame.pack(fill=tk.X, pady=10)
                
                estado_var = tk.StringVar(value=oficio['estado'])
                
                radio_frame = ttk.Frame(acciones_frame)
                radio_frame.pack(fill=tk.X, pady=5)
                
                ttk.Radiobutton(radio_frame, text="En Proceso", variable=estado_var, 
                            value="En Proceso").pack(side=tk.LEFT, padx=10)
                ttk.Radiobutton(radio_frame, text="Atendido", variable=estado_var, 
                            value="Atendido").pack(side=tk.LEFT, padx=10)
                ttk.Radiobutton(radio_frame, text="Archivado", variable=estado_var, 
                            value="Archivado").pack(side=tk.LEFT, padx=10)
                
                # Campos para Atendido
                atendido_frame = ttk.Frame(acciones_frame)
                atendido_frame.pack(fill=tk.X, pady=5)
                
                ttk.Label(atendido_frame, text="Oficio respuesta:", font=('Arial', 10)).pack(anchor=tk.W)
                oficio_respuesta_entry = ttk.Entry(atendido_frame, width=50, font=('Arial', 11))
                oficio_respuesta_entry.pack(fill=tk.X, pady=5)
                
                ttk.Label(atendido_frame, text="Archivo de acuse:", font=('Arial', 10)).pack(anchor=tk.W)
                archivo_frame = ttk.Frame(atendido_frame)
                archivo_frame.pack(fill=tk.X, pady=5)
                
                archivo_var = tk.StringVar()
                ttk.Entry(archivo_frame, textvariable=archivo_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
                ttk.Button(archivo_frame, text="Examinar...",
                        command=lambda: self.seleccionar_archivo(archivo_var)).pack(side=tk.RIGHT, padx=5)
                
                ttk.Label(atendido_frame, text="Comentarios:", font=('Arial', 10)).pack(anchor=tk.W)
                comentarios_text = tk.Text(atendido_frame, height=3, width=50, font=('Arial', 10))
                comentarios_text.pack(fill=tk.X, pady=5)
                
                # Ocultar/mostrar según estado
                def on_estado_change_informal(*args):
                    if estado_var.get() == "Atendido":
                        atendido_frame.pack(fill=tk.X, pady=5)
                    else:
                        atendido_frame.pack_forget()
                
                estado_var.trace('w', on_estado_change_informal)
                on_estado_change_informal()
                
                def aplicar_cambio_informal():
                    nuevo_estado = estado_var.get()
                    
                    if nuevo_estado == 'Atendido':
                        if not oficio_respuesta_entry.get().strip():
                            messagebox.showerror("Error", "Debe ingresar el número de oficio respuesta")
                            return
                        
                        # Leer archivo
                        contenido_bytes = None
                        nombre_archivo = None
                        if archivo_var.get():
                            try:
                                with open(archivo_var.get(), 'rb') as f:
                                    contenido_bytes = f.read()
                                nombre_archivo = os.path.basename(archivo_var.get())
                            except Exception as e:
                                messagebox.showerror("Error", f"No se pudo leer archivo: {e}")
                                return
                        
                        comentario_text = comentarios_text.get('1.0', tk.END).strip()
                        nota = f"[ATENDIDO] Oficio respuesta: {oficio_respuesta_entry.get()}"
                        if comentario_text:
                            nota += f" - {comentario_text}"
                        
                        self.cursor.execute("""
                            UPDATE oficios_informales 
                            SET estado = %s,
                                fecha_respuesta = NOW(),
                                oficio_respuesta = %s,
                                notas = CONCAT(COALESCE(notas, ''), '\n', %s)
                            WHERE id = %s
                        """, (nuevo_estado, oficio_respuesta_entry.get(), nota, oficio_id))
                        
                        if contenido_bytes:
                            mime_type = mimetypes.guess_type(nombre_archivo)[0] or 'application/octet-stream'
                            self.cursor.execute("""
                                INSERT INTO archivos_binarios 
                                (oficio_informal_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (oficio_id, 'acuse_informal', nombre_archivo,
                                psycopg2.Binary(contenido_bytes), mime_type,
                                len(contenido_bytes), self.usuario_actual['id']))
                    else:
                        self.cursor.execute("""
                            UPDATE oficios_informales SET estado = %s WHERE id = %s
                        """, (nuevo_estado, oficio_id))
                    
                    messagebox.showinfo("Éxito", f"Estado cambiado a: {nuevo_estado}")
                    dialog.destroy()
                    self.cargar_informales()
                
                ttk.Button(acciones_frame, text="✅ Aplicar Cambio", 
                        command=aplicar_cambio_informal,
                        width=20).pack(pady=10)
            
            ttk.Button(main_frame, text="❌ Cerrar", command=dialog.destroy, width=15).pack(pady=10)
        
    # cliente.py - Función ver_detalle completa con notas editables

    def ver_detalle(self, event=None):
        """Muestra detalle del oficio con notas editables y opción de omisión"""
        sel = self.tree.selection()
        if not sel:
            return
        
        item = self.tree.item(sel[0])
        oficio_numero = item['values'][0]
        
        self.cursor.execute("SELECT id FROM oficios WHERE numero_oficio = %s", (oficio_numero,))
        oficio_data = self.cursor.fetchone()
        if not oficio_data:
            messagebox.showerror("Error", "No se encontró el oficio")
            return
        
        oficio_id = oficio_data['id']
        
        self.cursor.execute("""
            SELECT o.*, u.nombre_completo as asignado, u2.nombre_completo as creador,
                u.email as email_asignado,
                (SELECT COUNT(*) FROM archivos_binarios WHERE oficio_id = o.id AND tipo = 'oficio') as tiene_archivo,
                (SELECT COUNT(*) FROM archivos_binarios WHERE oficio_id = o.id AND tipo = 'acuse') as tiene_acuse,
                CASE 
                    WHEN o.estado = 'En Proceso' AND o.fecha_asignacion IS NOT NULL 
                    THEN EXTRACT(DAY FROM (NOW() - o.fecha_asignacion))
                    ELSE 0
                END as dias_proceso,
                CASE 
                    WHEN o.notas LIKE '%%OMISIÓN%%' AND o.oficio_respuesta LIKE 'PENDIENTE%%' THEN TRUE
                    ELSE FALSE
                END as es_omision_pendiente
            FROM oficios o
            LEFT JOIN usuarios u ON o.usuario_asignado_id = u.id
            LEFT JOIN usuarios u2 ON o.created_by = u2.id
            WHERE o.id = %s
        """, (oficio_id,))
        
        oficio = self.cursor.fetchone()
        
        if not oficio:
            messagebox.showerror("Error", "No se encontraron datos del oficio")
            return
        
        # Crear ventana con tamaño inicial y autoajustable
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Detalle de Oficio - {oficio['numero_oficio']}")
        dialog.geometry("900x700")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, True)
        
        # Configurar grid para que se expanda
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        
        # CARGAR CONFIGURACIÓN GUARDADA
        try:
            config_file = Path.home() / ".gestion_oficios" / f"cliente_detalle_{oficio_id}.conf"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    w, h, x, y = map(int, f.read().split(','))
                    dialog.geometry(f"{w}x{h}+{x}+{y}")
        except:
            pass
        
        def al_cerrar():
            try:
                config_dir = Path.home() / ".gestion_oficios"
                config_dir.mkdir(exist_ok=True)
                config_file = config_dir / f"cliente_detalle_{oficio_id}.conf"
                with open(config_file, 'w') as f:
                    f.write(f"{dialog.winfo_width()},{dialog.winfo_height()},{dialog.winfo_x()},{dialog.winfo_y()}")
            except:
                pass
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", al_cerrar)
        
        # Centrar si es primera vez
        dialog.update_idletasks()
        if not hasattr(self, '_detalle_config_cargada'):
            x = (dialog.winfo_screenwidth() // 2) - (900 // 2)
            y = (dialog.winfo_screenheight() // 2) - (700 // 2)
            dialog.geometry(f'+{x}+{y}')
            self._detalle_config_cargada = True
        
        # ========== CONTENEDOR PRINCIPAL CON SCROLL ==========
        main_canvas = tk.Canvas(dialog)
        main_scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=main_canvas.yview)
        main_scrollable_frame = ttk.Frame(main_canvas)
        
        main_scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=main_scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.grid(row=0, column=0, sticky="nsew")
        main_scrollbar.grid(row=0, column=1, sticky="ns")
        
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        
        # ========== CONTENIDO DENTRO DEL SCROLL ==========
        main_frame = ttk.Frame(main_scrollable_frame, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text=f"DETALLE DE OFICIO", font=('Arial', 16, 'bold')).pack(pady=5)
        ttk.Label(main_frame, text=f"Número: {oficio['numero_oficio']}", font=('Arial', 12)).pack()
        
        # Estado
        estado_mostrar = oficio['estado']
        if estado_mostrar == "Archivado":
            estado_mostrar = "Informativo"
        
        estado_color = {'En Proceso': 'orange', 'Atendido': 'green', 'Archivado': 'gray'}
        color = estado_color.get(oficio['estado'], 'black')
        
        estado_frame = ttk.Frame(main_frame)
        estado_frame.pack(fill=tk.X, pady=10)
        ttk.Label(estado_frame, text="Estado:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        ttk.Label(estado_frame, text=estado_mostrar, font=('Arial', 12, 'bold'), 
                foreground=color).pack(side=tk.LEFT, padx=10)
        
        if oficio['acuse_recibido']:
            ttk.Label(estado_frame, text="✅ ACUSE RECIBIDO", font=('Arial', 11, 'bold'),
                    foreground='green').pack(side=tk.LEFT, padx=20)
        
        if oficio['dias_proceso'] > 3:
            ttk.Label(estado_frame, text=f"⚠️ {oficio['dias_proceso']} DÍAS", 
                    font=('Arial', 11, 'bold'), foreground='red').pack(side=tk.LEFT, padx=20)
        
        # Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Pestaña 1: Datos (con scroll interno)
        datos_frame = ttk.Frame(notebook, padding="15")
        notebook.add(datos_frame, text="📋 Datos Generales")
        
        # Scroll para datos
        datos_canvas = tk.Canvas(datos_frame)
        datos_scrollbar = ttk.Scrollbar(datos_frame, orient="vertical", command=datos_canvas.yview)
        datos_scrollable = ttk.Frame(datos_canvas)
        
        datos_scrollable.bind("<Configure>", lambda e: datos_canvas.configure(scrollregion=datos_canvas.bbox("all")))
        datos_canvas.create_window((0, 0), window=datos_scrollable, anchor="nw")
        datos_canvas.configure(yscrollcommand=datos_scrollbar.set)
        
        datos_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        datos_scrollbar.pack(side="right", fill="y")
        
        row = 0
        campos = [
            ('ID:', str(oficio['id'])),
            ('Fecha Oficio:', oficio['fecha_oficio'].strftime('%d/%m/%Y') if oficio['fecha_oficio'] else ''),
            ('Remitente:', oficio['remitente']),
            ('Destinatario:', oficio['destinatario']),
            ('Asunto:', oficio['asunto']),
            ('Tipo:', oficio['tipo_oficio']),
            ('Prioridad:', oficio['prioridad']),
            ('Asignado a:', oficio['asignado'] or 'Sin asignar'),
            ('Fecha asignación:', oficio['fecha_asignacion'].strftime('%d/%m/%Y %H:%M') if oficio['fecha_asignacion'] else ''),
        ]
        
        for label, valor in campos:
            ttk.Label(datos_scrollable, text=label, font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
            ttk.Label(datos_scrollable, text=valor, font=('Arial', 10), wraplength=450).grid(row=row, column=1, sticky=tk.W, pady=5, padx=10)
            row += 1
        
        # Pestaña 2: Seguimiento (con scroll)
        seguimiento_frame = ttk.Frame(notebook, padding="15")
        notebook.add(seguimiento_frame, text="⏱️ Seguimiento")
        
        seg_canvas = tk.Canvas(seguimiento_frame)
        seg_scrollbar = ttk.Scrollbar(seguimiento_frame, orient="vertical", command=seg_canvas.yview)
        seg_scrollable = ttk.Frame(seg_canvas)
        
        seg_scrollable.bind("<Configure>", lambda e: seg_canvas.configure(scrollregion=seg_canvas.bbox("all")))
        seg_canvas.create_window((0, 0), window=seg_scrollable, anchor="nw")
        seg_canvas.configure(yscrollcommand=seg_scrollbar.set)
        
        seg_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        seg_scrollbar.pack(side="right", fill="y")
        
        row = 0
        seguimiento_campos = [
            ('Fecha inicio trámite:', oficio['fecha_inicio_tramite'].strftime('%d/%m/%Y %H:%M') if oficio['fecha_inicio_tramite'] else 'No iniciado'),
            ('Fecha atendido:', oficio['fecha_atendido'].strftime('%d/%m/%Y %H:%M') if oficio['fecha_atendido'] else 'Pendiente'),
            ('Oficio respuesta:', oficio['oficio_respuesta'] or 'No especificado'),
            ('Acuse recibido:', 'SÍ' if oficio['acuse_recibido'] else 'NO'),
            ('Días en proceso:', str(oficio['dias_proceso']) if oficio['dias_proceso'] > 0 else 'N/A'),
        ]
        
        for label, valor in seguimiento_campos:
            ttk.Label(seg_scrollable, text=label, font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
            ttk.Label(seg_scrollable, text=valor, font=('Arial', 10), wraplength=450).grid(row=row, column=1, sticky=tk.W, pady=5, padx=10)
            row += 1
        
        # Pestaña 3: Notas (EDITABLE) - ya tiene scroll interno
        notas_frame = ttk.Frame(notebook, padding="15")
        notebook.add(notas_frame, text="📝 Notas")
        
        notas_container = ttk.Frame(notas_frame)
        notas_container.pack(fill=tk.BOTH, expand=True)
        
        notas_text = tk.Text(notas_container, height=12, width=70, font=('Arial', 10))
        notas_text.pack(fill=tk.BOTH, expand=True)
        notas_text.insert('1.0', oficio['notas'] or '')
        
        notas_scroll = ttk.Scrollbar(notas_container, orient=tk.VERTICAL, command=notas_text.yview)
        notas_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        notas_text.config(yscrollcommand=notas_scroll.set)
        
        def guardar_notas():
            nuevas_notas = notas_text.get('1.0', tk.END).strip()
            if nuevas_notas != (oficio['notas'] or ''):
                self.cursor.execute("""
                    UPDATE oficios SET notas = %s WHERE id = %s
                """, (nuevas_notas, oficio_id))
                oficio['notas'] = nuevas_notas
                messagebox.showinfo("Éxito", "Notas guardadas correctamente")
        
        ttk.Button(notas_frame, text="💾 Guardar Notas", 
                command=guardar_notas, width=20).pack(pady=10)
        
        # ========== SECCIÓN DE ACCIONES (con scroll) ==========
        acciones_frame = ttk.LabelFrame(main_frame, text="📌 Acciones", padding="10")
        acciones_frame.pack(fill=tk.X, pady=10)
        
        es_omision_pendiente = oficio.get('es_omision_pendiente', False)
        
        # SECCIÓN PARA COMPLETAR OMISIÓN
        if es_omision_pendiente:
            omision_frame = ttk.LabelFrame(acciones_frame, text="⚠️ COMPLETAR OMISIÓN", padding="10")
            omision_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(omision_frame, text="Este oficio fue marcado por omisión. Complete con el oficio de respuesta cuando esté disponible.",
                    font=('Arial', 9), foreground='orange').pack(anchor=tk.W, pady=5)
            
            # Extraer fecha programada de la nota
            fecha_programada = ""
            if oficio['notas']:
                import re
                match = re.search(r'Respuesta programada: (\d{4}-\d{2}-\d{2})', oficio['notas'])
                if match:
                    fecha_programada = match.group(1)
                    ttk.Label(omision_frame, text=f"Fecha programada: {fecha_programada}",
                            font=('Arial', 9, 'bold'), foreground='blue').pack(anchor=tk.W, pady=2)
            
            respuesta_frame = ttk.Frame(omision_frame)
            respuesta_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(respuesta_frame, text="Oficio de respuesta:*", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            oficio_respuesta_entry = ttk.Entry(respuesta_frame, width=50, font=('Arial', 11))
            oficio_respuesta_entry.pack(fill=tk.X, pady=5)
            
            ttk.Label(respuesta_frame, text="Archivo de acuse (opcional):", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
            archivo_frame = ttk.Frame(respuesta_frame)
            archivo_frame.pack(fill=tk.X, pady=5)
            
            archivo_var = tk.StringVar()
            ttk.Entry(archivo_frame, textvariable=archivo_var, width=40, font=('Arial', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
            ttk.Button(archivo_frame, text="Examinar...",
                    command=lambda: self.seleccionar_archivo(archivo_var)).pack(side=tk.RIGHT, padx=5)
            
            ttk.Label(respuesta_frame, text="Comentarios:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,0))
            comentarios_text = tk.Text(respuesta_frame, height=3, width=50, font=('Arial', 10))
            comentarios_text.pack(fill=tk.X, pady=5)
            
            def completar_omision():
                oficio_respuesta = oficio_respuesta_entry.get().strip()
                if not oficio_respuesta:
                    messagebox.showerror("Error", "Debe ingresar el número de oficio respuesta")
                    return

                ######
                comentario = comentarios_text.get('1.0', tk.END).strip()
                # ✅ NOTA MEJORADA PARA OMISIÓN COMPLETADA
                nota = f"\n[OMISIÓN COMPLETADA] Oficio respuesta: {oficio_respuesta} - Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                if comentario:
                    nota += f" - {comentario}"
                
                self.cursor.execute("""
                    UPDATE oficios 
                    SET oficio_respuesta = %s,
                        notas = CONCAT(COALESCE(notas, ''), %s)
                    WHERE id = %s
                """, (oficio_respuesta, nota, oficio_id))
                ####
                
                if archivo_var.get():
                    try:
                        with open(archivo_var.get(), 'rb') as f:
                            contenido = f.read()
                        nombre_archivo = os.path.basename(archivo_var.get())
                        mime_type = mimetypes.guess_type(nombre_archivo)[0] or 'application/octet-stream'
                        
                        self.cursor.execute("""
                            INSERT INTO archivos_binarios 
                            (oficio_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (oficio_id, 'acuse', nombre_archivo,
                            psycopg2.Binary(contenido), mime_type,
                            len(contenido), self.usuario_actual['id']))
                        
                        self.cursor.execute("""
                            UPDATE oficios SET acuse_recibido = TRUE WHERE id = %s
                        """, (oficio_id,))
                        
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo guardar archivo: {e}")
                
                messagebox.showinfo("Éxito", "Omisión completada. Oficio de respuesta registrado.")
                dialog.destroy()
                self.cargar_mis_oficios()
            
            ttk.Button(omision_frame, text="✅ Completar Omisión", 
                    command=completar_omision,
                    width=20).pack(pady=10)
        
        # SECCIÓN PARA CAMBIAR ESTADO
        if oficio['estado'] not in ['Atendido', 'Archivado']:
            estado_seleccionado = tk.StringVar(value=oficio['estado'])
            
            acciones_inner = ttk.Frame(acciones_frame)
            acciones_inner.pack(fill=tk.X, pady=5)
            
            radio_frame = ttk.Frame(acciones_inner)
            radio_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(radio_frame, text="Cambiar estado:", font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
            
            ttk.Radiobutton(radio_frame, text="En Proceso", variable=estado_seleccionado, 
                        value="En Proceso").pack(side=tk.LEFT, padx=10)
            
            rb_atendido = ttk.Radiobutton(radio_frame, text="Atendido", variable=estado_seleccionado, 
                                        value="Atendido")
            rb_atendido.pack(side=tk.LEFT, padx=10)
            
            omision_var = tk.BooleanVar(value=False)
            cb_omision = ttk.Checkbutton(radio_frame, text="Omisión (requiere fecha respuesta)", 
                                        variable=omision_var, state='disabled')
            cb_omision.pack(side=tk.LEFT, padx=10)
            
            fecha_futura_frame = ttk.Frame(acciones_inner)
            fecha_futura_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(fecha_futura_frame, text="Fecha respuesta programada:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
            fecha_futura_entry = ttk.Entry(fecha_futura_frame, width=15, font=('Arial', 10))
            fecha_futura_entry.pack(side=tk.LEFT, padx=5)
            fecha_futura_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
            fecha_futura_frame.pack_forget()
            
            ttk.Radiobutton(radio_frame, text="Informativo", variable=estado_seleccionado, 
                        value="Archivado").pack(side=tk.LEFT, padx=10)
            
            def on_estado_change(*args):
                if estado_seleccionado.get() == "Atendido":
                    cb_omision.config(state='normal')
                    fecha_futura_frame.pack(fill=tk.X, pady=5)
                else:
                    omision_var.set(False)
                    cb_omision.config(state='disabled')
                    fecha_futura_frame.pack_forget()
            
            estado_seleccionado.trace('w', on_estado_change)
            
            def aplicar_cambio():
                nuevo_estado = estado_seleccionado.get()
                
                if nuevo_estado == 'Atendido' and omision_var.get():
                    fecha_futura = fecha_futura_entry.get().strip()
                    if not fecha_futura:
                        messagebox.showerror("Error", "Debe ingresar una fecha de respuesta programada")
                        return
                    
                    try:
                        datetime.strptime(fecha_futura, '%Y-%m-%d')
                    except ValueError:
                        messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                        return
                    
                    nota_omision = f"\n[OMISIÓN] Atendido por omisión el {datetime.now().strftime('%Y-%m-%d %H:%M')}. Respuesta programada: {fecha_futura}"
                    
                    self.cursor.execute("""
                        UPDATE oficios 
                        SET estado = 'Atendido',
                            fecha_atendido = NOW(),
                            notas = CONCAT(COALESCE(notas, ''), %s),
                            oficio_respuesta = %s
                        WHERE id = %s
                    """, (nota_omision, f"PENDIENTE - Respuesta programada: {fecha_futura}", oficio_id))
                    
                    messagebox.showinfo("Omisión", 
                        f"Oficio marcado como Atendido por omisión.\n"
                        f"Respuesta programada: {fecha_futura}\n"
                        f"Puede completar la omisión en cualquier momento desde el detalle del oficio.")
                    dialog.destroy()
                    self.cargar_mis_oficios()
                else:
                    self.aplicar_cambio_estado(oficio_id, nuevo_estado, dialog)
            
            ttk.Button(radio_frame, text="✅ Aplicar", 
                    command=aplicar_cambio,
                    width=15).pack(side=tk.LEFT, padx=20)
        
        # Botones de archivos
        archivo_frame = ttk.Frame(acciones_frame)
        archivo_frame.pack(fill=tk.X, pady=5)
        
        if oficio['tiene_archivo'] > 0:
            ttk.Label(archivo_frame, text="Archivo oficio:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
            ttk.Button(archivo_frame, text="📄 Ver Oficio", 
                    command=lambda: self.abrir_archivo_oficio(oficio['id'], 'oficio'),
                    width=15).pack(side=tk.LEFT, padx=5)
        
        if oficio['tiene_acuse'] > 0:
            ttk.Label(archivo_frame, text="Acuse:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
            ttk.Button(archivo_frame, text="📄 Ver Acuse", 
                    command=lambda: self.abrir_archivo_oficio(oficio['id'], 'acuse'),
                    width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(main_frame, text="❌ Cerrar", command=al_cerrar, width=15).pack(pady=10)
        
    def abrir_archivo_oficio(self, oficio_id, tipo='oficio'):
        """Abre un archivo de la BD (lo extrae a temporal y lo abre)"""
        try:
            # Obtener el archivo de la BD
            self.cursor.execute("""
                SELECT nombre_archivo, contenido FROM archivos_binarios 
                WHERE oficio_id = %s AND tipo = %s
                ORDER BY fecha_subida DESC LIMIT 1
            """, (oficio_id, tipo))
            
            archivo = self.cursor.fetchone()
            
            if not archivo:
                messagebox.showerror("Error", f"No se encontró archivo de {tipo}")
                return
            
            # Crear archivo temporal
            temp_dir = Path(tempfile.gettempdir()) / "gestion_oficios"
            temp_dir.mkdir(exist_ok=True)
            
            ruta_temp = temp_dir / archivo['nombre_archivo']
            
            # Si ya existe, agregar sufijo
            if ruta_temp.exists():
                base = ruta_temp.stem
                ext = ruta_temp.suffix
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                ruta_temp = temp_dir / f"{base}_{timestamp}{ext}"
            
            # Guardar archivo temporal
            with open(ruta_temp, 'wb') as f:
                f.write(archivo['contenido'])
            
            # Abrir con el programa predeterminado
            if platform.system() == 'Windows':
                os.startfile(str(ruta_temp))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(ruta_temp)])
            else:  # Linux
                subprocess.run(['xdg-open', str(ruta_temp)])
            
            self.status_label.config(text=f"Archivo abierto: {archivo['nombre_archivo']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

    def aplicar_cambio_estado(self, oficio_id, nuevo_estado, parent_dialog):
        """Aplica cambio de estado"""
        if nuevo_estado == 'Atendido':
            self.marcar_atendido(oficio_id, parent_dialog)
        else:
            update_fields = ["estado = %s"]
            params = [nuevo_estado]
            
            if nuevo_estado == 'En Proceso':
                update_fields.append("fecha_inicio_tramite = NOW()")
            
            params.append(oficio_id)
            
            query = f"UPDATE oficios SET {', '.join(update_fields)} WHERE id = %s"
            self.cursor.execute(query, params)
            
            messagebox.showinfo("Éxito", f"Estado cambiado a: {nuevo_estado}")
            parent_dialog.destroy()
            self.cargar_mis_oficios()

    def marcar_atendido(self, oficio_id, parent_dialog):
        """Marca oficio como atendido y permite subir acuse a BD"""
        dialog = tk.Toplevel(parent_dialog)
        dialog.title("Marcar como Atendido")
        dialog.geometry("600x500")
        dialog.transient(parent_dialog)
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f'+{x}+{y}')
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="MARCAR COMO ATENDIDO", font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Label(frame, text="Número de oficio respuesta:*", font=('Arial', 10)).pack(anchor=tk.W)
        num_respuesta = ttk.Entry(frame, width=40, font=('Arial', 11))
        num_respuesta.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Archivo de acuse (opcional):", font=('Arial', 10)).pack(anchor=tk.W, pady=(10,0))
        
        archivo_frame = ttk.Frame(frame)
        archivo_frame.pack(fill=tk.X, pady=5)
        
        archivo_var = tk.StringVar()
        ttk.Entry(archivo_frame, textvariable=archivo_var, width=35, font=('Arial', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(archivo_frame, text="Examinar...", 
                command=lambda: self.seleccionar_archivo(archivo_var)).pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(frame, text="Comentarios:", font=('Arial', 10)).pack(anchor=tk.W, pady=(10,0))
        comentarios = tk.Text(frame, height=4, width=40, font=('Arial', 10))
        comentarios.pack(fill=tk.X, pady=5)
        
        def confirmar():
            if not num_respuesta.get():
                messagebox.showerror("Error", "Debe ingresar el número de oficio respuesta")
                return
            
            # Leer archivo si se seleccionó
            contenido_bytes = None
            nombre_archivo = None
            if archivo_var.get():
                try:
                    with open(archivo_var.get(), 'rb') as f:
                        contenido_bytes = f.read()
                    nombre_archivo = os.path.basename(archivo_var.get())
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
                    return
            
            # ✅ NOTA MEJORADA - Formato más limpio
            comentario_text = comentarios.get('1.0', tk.END).strip()
            nota = f"[ATENDIDO] Oficio respuesta: {num_respuesta.get()}"
            if comentario_text:
                nota += f" - {comentario_text}"
            
            try:
                self.cursor.execute("""
                    UPDATE oficios 
                    SET estado = 'Atendido', 
                        fecha_atendido = NOW(),
                        oficio_respuesta = %s,
                        notas = CONCAT(COALESCE(notas, ''), '\n', %s)
                    WHERE id = %s
                    RETURNING id
                """, (num_respuesta.get(), nota, oficio_id))
                
                # Guardar archivo binario si existe
                if contenido_bytes:
                    mime_type = mimetypes.guess_type(nombre_archivo)[0] or 'application/octet-stream'
                    
                    self.cursor.execute("""
                        INSERT INTO archivos_binarios 
                        (oficio_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        oficio_id,
                        'acuse',
                        nombre_archivo,
                        psycopg2.Binary(contenido_bytes),
                        mime_type,
                        len(contenido_bytes),
                        self.usuario_actual['id']
                    ))
                
                messagebox.showinfo("Éxito", "Oficio marcado como atendido y acuse guardado")
                dialog.destroy()
                parent_dialog.destroy()
                self.cargar_mis_oficios()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {e}")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Guardar", command=confirmar, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)

    def mostrar_menu_contextual(self, event):
        """Muestra menú contextual dinámico"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        self.tree.selection_set(item)
        valores = self.tree.item(item)['values']
        estado = valores[3]  # Estado está en índice 3
        oficio_numero = valores[0]  # Número de oficio en índice 0
        
        # Obtener ID real por número de oficio
        self.cursor.execute("SELECT id FROM oficios WHERE numero_oficio = %s", (oficio_numero,))
        oficio_data = self.cursor.fetchone()
        if not oficio_data:
            return
        oficio_id = oficio_data['id']
        
        # Crear menú contextual
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Ver detalle", command=lambda: self.ver_detalle(None))
        
        if estado == 'En Proceso':
            context_menu.add_command(label="✅ Marcar atendido", 
                                    command=lambda: self.marcar_atendido(oficio_id, None))
            context_menu.add_command(label="📦 Marcar informativo", 
                                    command=lambda: self.aplicar_cambio_estado(oficio_id, 'Archivado', None))
        
        context_menu.add_command(label="📄 Abrir archivo", 
                                command=lambda: self.abrir_archivo_oficio(oficio_id, 'oficio'))
        
        context_menu.post(event.x_root, event.y_root)
    
    def nuevo_informal(self):
        """Crea nuevo oficio informal"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Oficio")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # HACER LA VENTANA REDIMENSIONABLE
        dialog.resizable(True, True)
        
        # CARGAR CONFIGURACIÓN GUARDADA
        try:
            from pathlib import Path
            config_file = Path.home() / ".gestion_oficios" / "cliente_informal.conf"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    w, h, x, y = map(int, f.read().split(','))
                    dialog.geometry(f"{w}x{h}+{x}+{y}")
        except:
            pass
        
        # FUNCIÓN PARA GUARDAR AL CERRAR
        def al_cerrar():
            try:
                from pathlib import Path
                config_dir = Path.home() / ".gestion_oficios"
                config_dir.mkdir(exist_ok=True)
                config_file = config_dir / "cliente_informal.conf"
                with open(config_file, 'w') as f:
                    f.write(f"{dialog.winfo_width()},{dialog.winfo_height()},{dialog.winfo_x()},{dialog.winfo_y()}")
            except:
                pass
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", al_cerrar)
        
        # Centrar si es primera vez
        dialog.update_idletasks()
        if not hasattr(self, '_informal_config_cargada'):
            x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
            y = (dialog.winfo_screenheight() // 2) - (500 // 2)
            dialog.geometry(f'+{x}+{y}')
            self._informal_config_cargada = True
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Usar Label de tk en lugar de ttk para el título (soporta font)
        tk.Label(frame, text="NUEVO Oficio", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Canvas con scroll para los campos
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Crear campos en el frame scrolleable - USAR tk.Label en lugar de ttk.Label para los textos con fuente
        tk.Label(scrollable_frame, text="Fecha recepción:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        fecha = ttk.Entry(scrollable_frame, width=40, font=('Arial', 11))
        fecha.grid(row=0, column=1, pady=8, padx=10, sticky=tk.W)
        fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Label(scrollable_frame, text="Remitente:*", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        remitente = ttk.Entry(scrollable_frame, width=40, font=('Arial', 11))
        remitente.grid(row=1, column=1, pady=8, padx=10, sticky=tk.W)
        
        tk.Label(scrollable_frame, text="Contacto:", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        contacto = ttk.Entry(scrollable_frame, width=40, font=('Arial', 11))
        contacto.grid(row=2, column=1, pady=8, padx=10, sticky=tk.W)
        
        tk.Label(scrollable_frame, text="Asunto:*", font=('Arial', 10)).grid(row=3, column=0, sticky=tk.W, pady=8)
        asunto = ttk.Entry(scrollable_frame, width=50, font=('Arial', 11))
        asunto.grid(row=3, column=1, pady=8, padx=10, sticky=tk.W)
        
        tk.Label(scrollable_frame, text="Canal:", font=('Arial', 10)).grid(row=4, column=0, sticky=tk.W, pady=8)
        canal = ttk.Combobox(scrollable_frame, values=['WhatsApp', 'Teléfono', 'Email', 'Presencial', 'Otro'], 
                            width=37, font=('Arial', 11))
        canal.grid(row=4, column=1, pady=8, padx=10, sticky=tk.W)
        canal.set('WhatsApp')
        
        tk.Label(scrollable_frame, text="Descripción:", font=('Arial', 10)).grid(row=5, column=0, sticky=tk.W, pady=8)
        descripcion = tk.Text(scrollable_frame, height=5, width=40, font=('Arial', 11))
        descripcion.grid(row=5, column=1, pady=8, padx=10, sticky=tk.W)
        
        requiere_var = tk.BooleanVar()
        # Para el Checkbutton, usamos tk.Checkbutton en lugar de ttk.Checkbutton para soportar font
        tk.Checkbutton(scrollable_frame, text="Requiere seguimiento", 
                    variable=requiere_var, font=('Arial', 10)).grid(row=6, column=0, columnspan=2, pady=10)
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def guardar():
            if not remitente.get() or not asunto.get():
                messagebox.showerror("Error", "Complete los campos obligatorios (*)")
                return
            
            self.cursor.execute("""
                INSERT INTO oficios_informales 
                (usuario_id, fecha_recepcion, remitente, contacto, asunto, descripcion,
                canal, requiere_seguimiento, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pendiente')
            """, (self.usuario_actual['id'], fecha.get(), remitente.get(), 
                contacto.get(), asunto.get(), descripcion.get('1.0', tk.END).strip(),
                canal.get(), requiere_var.get()))
            
            messagebox.showinfo("Éxito", "Oficio informal registrado")
            al_cerrar()
            self.cargar_informales()
        
        ttk.Button(frame, text="Guardar", command=guardar, width=20).pack(pady=10)
        
    def mi_perfil(self):
        """Editar perfil"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Mi Perfil")
        dialog.geometry("550x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # ✅ HACER LA VENTANA REDIMENSIONABLE
        dialog.resizable(True, True)
        
        # ✅ CARGAR CONFIGURACIÓN GUARDADA
        try:
            from pathlib import Path
            config_file = Path.home() / ".gestion_oficios" / "cliente_perfil.conf"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    w, h, x, y = map(int, f.read().split(','))
                    dialog.geometry(f"{w}x{h}+{x}+{y}")
        except:
            pass
        
        # ✅ FUNCIÓN PARA GUARDAR AL CERRAR
        def al_cerrar():
            try:
                from pathlib import Path
                config_dir = Path.home() / ".gestion_oficios"
                config_dir.mkdir(exist_ok=True)
                config_file = config_dir / "cliente_perfil.conf"
                with open(config_file, 'w') as f:
                    f.write(f"{dialog.winfo_width()},{dialog.winfo_height()},{dialog.winfo_x()},{dialog.winfo_y()}")
            except:
                pass
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", al_cerrar)
        
        # Centrar si es primera vez
        dialog.update_idletasks()
        if not hasattr(self, '_perfil_config_cargada'):
            x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
            y = (dialog.winfo_screenheight() // 2) - (450 // 2)
            dialog.geometry(f'+{x}+{y}')
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="MI PERFIL", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Canvas con scroll
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        campos = [
            ('Username:', self.usuario_actual['username'], True),
            ('Nombre completo:', self.usuario_actual['nombre_completo'], False),
            ('Email:', self.usuario_actual['email'] or '', False),
            ('Teléfono:', self.usuario_actual['telefono'] or '', False),
            ('Rol:', 'Administrador' if self.usuario_actual['es_admin'] else 'Usuario', True)
        ]
        
        entries = {}
        for i, (label, valor, readonly) in enumerate(campos):
            ttk.Label(scrollable_frame, text=label, font=('Arial', 10)).grid(row=i, column=0, sticky=tk.W, pady=8, padx=5)
            entry = ttk.Entry(scrollable_frame, width=40, font=('Arial', 11))
            entry.grid(row=i, column=1, pady=8, padx=10, sticky=tk.W)
            entry.insert(0, valor)
            if readonly:
                entry.config(state='readonly')
            if not readonly:
                entries[label] = entry
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def guardar():
            self.cursor.execute("""
                UPDATE usuarios 
                SET nombre_completo = %s, email = %s, telefono = %s
                WHERE id = %s
            """, (entries['Nombre completo:'].get(), entries['Email:'].get(), 
                entries['Teléfono:'].get(), self.usuario_actual['id']))
            
            self.usuario_actual['nombre_completo'] = entries['Nombre completo:'].get()
            self.usuario_actual['email'] = entries['Email:'].get()
            self.usuario_actual['telefono'] = entries['Teléfono:'].get()
            
            messagebox.showinfo("Éxito", "Perfil actualizado")
            al_cerrar()
            self.mostrar_principal()
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Guardar Cambios", command=guardar, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cambiar Contraseña", 
                command=lambda: [al_cerrar(), self.cambiar_mi_password()], width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=al_cerrar, width=15).pack(side=tk.LEFT, padx=5)
    
    def cambiar_mi_password(self):
        """Cambiar contraseña"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cambiar Contraseña")
        dialog.geometry("450x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # ✅ HACER LA VENTANA REDIMENSIONABLE
        dialog.resizable(True, True)
        
        # ✅ CARGAR CONFIGURACIÓN GUARDADA
        try:
            from pathlib import Path
            config_file = Path.home() / ".gestion_oficios" / "cliente_password.conf"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    w, h, x, y = map(int, f.read().split(','))
                    dialog.geometry(f"{w}x{h}+{x}+{y}")
        except:
            pass
        
        # ✅ FUNCIÓN PARA GUARDAR AL CERRAR
        def al_cerrar():
            try:
                from pathlib import Path
                config_dir = Path.home() / ".gestion_oficios"
                config_dir.mkdir(exist_ok=True)
                config_file = config_dir / "cliente_password.conf"
                with open(config_file, 'w') as f:
                    f.write(f"{dialog.winfo_width()},{dialog.winfo_height()},{dialog.winfo_x()},{dialog.winfo_y()}")
            except:
                pass
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", al_cerrar)
        
        # Centrar si es primera vez
        dialog.update_idletasks()
        if not hasattr(self, '_password_config_cargada'):
            x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
            y = (dialog.winfo_screenheight() // 2) - (300 // 2)
            dialog.geometry(f'+{x}+{y}')
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="CAMBIAR CONTRASEÑA", font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Label(frame, text="Contraseña actual:", font=('Arial', 10)).pack(anchor=tk.W)
        actual = ttk.Entry(frame, width=30, show="*", font=('Arial', 11))
        actual.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Nueva contraseña:", font=('Arial', 10)).pack(anchor=tk.W, pady=(10,0))
        nueva = ttk.Entry(frame, width=30, show="*", font=('Arial', 11))
        nueva.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Confirmar:", font=('Arial', 10)).pack(anchor=tk.W, pady=(10,0))
        confirmar = ttk.Entry(frame, width=30, show="*", font=('Arial', 11))
        confirmar.pack(fill=tk.X, pady=5)
        
        def guardar():
            self.cursor.execute("SELECT password FROM usuarios WHERE id = %s",
                            (self.usuario_actual['id'],))
            pass_actual_bd = self.cursor.fetchone()['password']
            
            if actual.get() != pass_actual_bd:
                messagebox.showerror("Error", "Contraseña actual incorrecta")
                return
            
            if not nueva.get():
                messagebox.showerror("Error", "La nueva contraseña no puede estar vacía")
                return
            
            if nueva.get() != confirmar.get():
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            self.cursor.execute("UPDATE usuarios SET password = %s WHERE id = %s",
                            (nueva.get(), self.usuario_actual['id']))
            
            messagebox.showinfo("Éxito", "Contraseña actualizada")
            al_cerrar()
        
        ttk.Button(frame, text="Cambiar Contraseña", command=guardar, width=25).pack(pady=20)
    
    def limpiar_filtros(self):
        """Limpia filtros"""
        self.filtro_estado.set("Todos")
        self.busqueda.set("")
        self.cargar_mis_oficios()
    
    def seleccionar_archivo(self, var):
        """Selecciona archivo"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("PDF files", "*.pdf"), ("Excel files", "*.xlsx"), ("Word files", "*.docx"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)
    
    def run(self):
        """Ejecuta la aplicación"""
        if not self.conectar_bd():
            messagebox.showerror("Error", "No se pudo conectar al servidor")
            return
        
        self.login()
        self.root.mainloop()
        
        if self.conn:
            self.conn.close()

def main():
    app = ClienteOficios()
    app.run()

if __name__ == "__main__":
    main()