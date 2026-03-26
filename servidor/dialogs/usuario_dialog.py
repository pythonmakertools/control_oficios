# dialogs/usuario_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox

class DialogoUsuario(tk.Toplevel):
    def __init__(self, parent, db, modo='nuevo', usuario_id=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.modo = modo
        self.usuario_id = usuario_id
        
        titulo = "Nuevo Usuario" if modo == 'nuevo' else "Editar Usuario"
        self.title(titulo)
        self.geometry("500x550")
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.datos = {}
        if modo == 'editar' and usuario_id:
            self.cargar_datos()
        
        self.crear_interfaz()
    
    def cargar_datos(self):
        """Carga datos del usuario para edición"""
        self.datos = self.db.get_usuario_by_id(self.usuario_id)
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = "NUEVO USUARIO" if self.modo == 'nuevo' else f"EDITAR USUARIO: {self.datos.get('username', '')}"
        ttk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Campos
        campos_frame = ttk.LabelFrame(main_frame, text="Datos del usuario", padding="15")
        campos_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Usuario
        ttk.Label(campos_frame, text="Usuario:*").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.username = ttk.Entry(campos_frame, width=35)
        self.username.grid(row=0, column=1, pady=8, padx=5)
        if self.datos.get('username'):
            self.username.insert(0, self.datos['username'])
        
        # Contraseña
        ttk.Label(campos_frame, text="Contraseña:*").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.password = ttk.Entry(campos_frame, width=35, show="*")
        self.password.grid(row=1, column=1, pady=8, padx=5)
        
        # Confirmar contraseña
        ttk.Label(campos_frame, text="Confirmar:*").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.confirmar = ttk.Entry(campos_frame, width=35, show="*")
        self.confirmar.grid(row=2, column=1, pady=8, padx=5)
        
        # Nombre completo
        ttk.Label(campos_frame, text="Nombre completo:*").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.nombre = ttk.Entry(campos_frame, width=35)
        self.nombre.grid(row=3, column=1, pady=8, padx=5)
        if self.datos.get('nombre_completo'):
            self.nombre.insert(0, self.datos['nombre_completo'])
        
        # Email
        ttk.Label(campos_frame, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=8)
        self.email = ttk.Entry(campos_frame, width=35)
        self.email.grid(row=4, column=1, pady=8, padx=5)
        if self.datos.get('email'):
            self.email.insert(0, self.datos['email'])
        
        # Teléfono
        ttk.Label(campos_frame, text="Teléfono:").grid(row=5, column=0, sticky=tk.W, pady=8)
        self.telefono = ttk.Entry(campos_frame, width=35)
        self.telefono.grid(row=5, column=1, pady=8, padx=5)
        if self.datos.get('telefono'):
            self.telefono.insert(0, self.datos['telefono'])
        
        # Checkboxes
        check_frame = ttk.Frame(campos_frame)
        check_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        self.es_admin = tk.BooleanVar(value=self.datos.get('es_admin', False))
        ttk.Checkbutton(check_frame, text="Es administrador", 
                       variable=self.es_admin).pack(side=tk.LEFT, padx=10)
        
        if self.modo == 'editar':
            self.activo = tk.BooleanVar(value=self.datos.get('activo', True))
            ttk.Checkbutton(check_frame, text="Activo", 
                           variable=self.activo).pack(side=tk.LEFT, padx=10)
        
        # Nota para edición
        if self.modo == 'editar':
            ttk.Label(campos_frame, text="(Dejar contraseña vacía para mantener la actual)",
                     foreground="gray").grid(row=7, column=0, columnspan=2, pady=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def guardar(self):
        """Guarda el usuario"""
        # Validaciones
        if not self.username.get().strip():
            messagebox.showerror("Error", "El usuario es obligatorio")
            return
        
        if not self.nombre.get().strip():
            messagebox.showerror("Error", "El nombre completo es obligatorio")
            return
        
        if self.modo == 'nuevo':
            if not self.password.get().strip():
                messagebox.showerror("Error", "La contraseña es obligatoria")
                return
            
            if self.password.get() != self.confirmar.get():
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            # Verificar si ya existe
            existente = self.db.get_usuario_by_username(self.username.get().strip())
            if existente:
                messagebox.showerror("Error", "El nombre de usuario ya existe")
                return
        
        if self.modo == 'editar' and self.password.get().strip():
            if self.password.get() != self.confirmar.get():
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
        
        # Preparar datos
        datos = {
            'username': self.username.get().strip(),
            'nombre_completo': self.nombre.get().strip(),
            'email': self.email.get().strip() or None,
            'telefono': self.telefono.get().strip() or None,
            'es_admin': self.es_admin.get()
        }
        
        if self.modo == 'editar':
            datos['activo'] = self.activo.get() if hasattr(self, 'activo') else True
        
        if self.password.get().strip():
            datos['password'] = self.password.get().strip()
        
        try:
            if self.modo == 'nuevo':
                self.db.insert_usuario(datos)
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
            else:
                self.db.update_usuario(self.usuario_id, datos)
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")