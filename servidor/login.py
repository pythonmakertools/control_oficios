# login.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import secrets

class LoginDialog(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.usuario = None
        
        self.title("Login Administrador")
        self.geometry("400x350")
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (350 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz de login"""
        frame = ttk.Frame(self, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="CONTROL DE OFICIOS", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Label(frame, text="Inicio de Sesión - Administrador",
                 font=('Arial', 10)).pack(pady=10)
        
        # Usuario
        ttk.Label(frame, text="Usuario:").pack(anchor=tk.W, pady=(10,0))
        self.username = ttk.Entry(frame, width=30)
        self.username.pack(fill=tk.X, pady=5)
        self.username.focus()
        
        # Contraseña
        ttk.Label(frame, text="Contraseña:").pack(anchor=tk.W, pady=(10,0))
        self.password = ttk.Entry(frame, width=30, show="*")
        self.password.pack(fill=tk.X, pady=5)
        self.password.bind('<Return>', lambda e: self.validar())
        
        # Botón
        ttk.Button(frame, text="Ingresar", command=self.validar).pack(pady=20)
    
    def validar(self):
        """Valida las credenciales"""
        user = self.username.get()
        pwd = self.password.get()
        
        usuario = self.db.login_usuario(user, pwd, admin_required=True)
        
        if usuario:
            self.usuario = usuario
            
            # Registrar sesión
            token = secrets.token_urlsafe(32)
            self.db.cursor.execute("""
                INSERT INTO sesiones_activas 
                (usuario_id, token_sesion, dispositivo, ip_address, fecha_expiracion, activa)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            """, (usuario['id'], token, "Servidor Admin", 'localhost', 
                  datetime.now() + timedelta(hours=8)))
            
            self.destroy()
        else:
            messagebox.showerror("Error", "Usuario/contraseña incorrectos o no es administrador")
            self.password.delete(0, tk.END)
            self.username.focus()