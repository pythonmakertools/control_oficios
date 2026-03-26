# dialogs/reasignar_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class DialogoReasignar(tk.Toplevel):
    def __init__(self, parent, db, notificador, oficio_id, usuario_actual):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.notificador = notificador
        self.oficio_id = oficio_id
        self.usuario_actual = usuario_actual
        
        self.title("Reasignar Oficio")
        self.geometry("550x500")
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.cargar_datos()
        self.crear_interfaz()
    
    def cargar_datos(self):
        """Carga datos del oficio y usuarios"""
        self.oficio = self.db.get_oficio_by_id(self.oficio_id)
        self.usuarios = self.db.get_usuarios_no_admin()
        
        # Usuario actual asignado
        self.usuario_actual_asignado = None
        if self.oficio['usuario_asignado_id']:
            self.usuario_actual_asignado = next(
                (u for u in self.usuarios if u['id'] == self.oficio['usuario_asignado_id']), 
                None
            )
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="REASIGNAR OFICIO", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Datos del oficio
        info_frame = ttk.LabelFrame(main_frame, text="Datos del Oficio", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"Número: {self.oficio['numero_oficio']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Asunto: {self.oficio['asunto']}").pack(anchor=tk.W, pady=5)
        
        if self.usuario_actual_asignado:
            ttk.Label(info_frame, 
                     text=f"Actualmente asignado a: {self.usuario_actual_asignado['nombre_completo']}",
                     foreground="blue").pack(anchor=tk.W, pady=5)
        
        # Selección de nuevo usuario
        ttk.Label(main_frame, text="Seleccione nuevo usuario:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10,5))
        
        # Frame para lista con scroll
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para usuarios
        columns = ('ID', 'Usuario', 'Nombre', 'Email')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Usuario', text='Usuario')
        self.tree.heading('Nombre', text='Nombre Completo')
        self.tree.heading('Email', text='Email')
        
        self.tree.column('ID', width=50)
        self.tree.column('Usuario', width=100)
        self.tree.column('Nombre', width=200)
        self.tree.column('Email', width=150)
        
        # Scrollbar
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar usuarios (excluyendo el actual)
        for u in self.usuarios:
            if u['id'] != self.oficio['usuario_asignado_id']:
                self.tree.insert('', tk.END, values=(
                    u['id'],
                    u['username'],
                    u['nombre_completo'],
                    u['email'] or ''
                ))
        
        # Opciones de notificación
        notif_frame = ttk.LabelFrame(main_frame, text="Opciones de notificación", padding="10")
        notif_frame.pack(fill=tk.X, pady=10)
        
        self.notificar_anterior = tk.BooleanVar(value=True)
        ttk.Checkbutton(notif_frame, text="Notificar al usuario anterior", 
                       variable=self.notificar_anterior).pack(anchor=tk.W)
        
        self.notificar_nuevo = tk.BooleanVar(value=True)
        ttk.Checkbutton(notif_frame, text="Notificar al nuevo usuario", 
                       variable=self.notificar_nuevo).pack(anchor=tk.W, pady=5)
        
        self.adjuntar_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(notif_frame, text="Adjuntar archivo del oficio", 
                       variable=self.adjuntar_var).pack(anchor=tk.W)
        
        ttk.Label(notif_frame, text="Mensaje adicional:").pack(anchor=tk.W, pady=5)
        self.mensaje = tk.Text(notif_frame, height=2, width=50)
        self.mensaje.pack(fill=tk.X)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Reasignar", command=self.reasignar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def reasignar(self):
        """Realiza la reasignación"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un usuario")
            return
        
        item = self.tree.item(seleccion[0])
        nuevo_usuario_id = item['values'][0]
        nuevo_usuario = next((u for u in self.usuarios if u['id'] == nuevo_usuario_id), None)
        
        if not nuevo_usuario:
            return
        
        # Obtener archivo si es necesario
        contenido = None
        nombre_archivo = None
        if self.adjuntar_var.get():
            archivo = self.db.get_archivo(self.oficio_id, 'oficio')
            if archivo:
                contenido = archivo['contenido']
                nombre_archivo = archivo['nombre_archivo']
        
        # Reasignar en BD
        self.db.asignar_oficio(self.oficio_id, nuevo_usuario_id)
        
        # Notificaciones
        mensaje_adicional = self.mensaje.get('1.0', tk.END).strip()
        
        if self.notificar_anterior.get() and self.usuario_actual_asignado:
            asunto = f"Oficio reasignado: {self.oficio['numero_oficio']}"
            mensaje = f"""
Hola {self.usuario_actual_asignado['nombre_completo']},

El oficio {self.oficio['numero_oficio']} ha sido reasignado a {nuevo_usuario['nombre_completo']}.

Asunto: {self.oficio['asunto']}
"""
            if mensaje_adicional:
                mensaje += f"\nMensaje: {mensaje_adicional}\n"
            
            mensaje += f"\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            self.notificador.enviar(self.usuario_actual_asignado['email'], asunto, mensaje)
        
        if self.notificar_nuevo.get() and nuevo_usuario:
            self.notificador.enviar_asignacion(
                nuevo_usuario,
                {'id': self.oficio_id,
                 'numero_oficio': self.oficio['numero_oficio'],
                 'asunto': self.oficio['asunto'],
                 'contenido': contenido,
                 'nombre_archivo': nombre_archivo},
                mensaje_adicional,
                self.adjuntar_var.get()
            )
        
        messagebox.showinfo("Éxito", "Oficio reasignado correctamente")
        self.destroy()