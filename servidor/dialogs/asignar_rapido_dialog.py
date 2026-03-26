# dialogs/asignar_rapido_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class DialogoAsignarRapido(tk.Toplevel):
    def __init__(self, parent, db, usuario_actual):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.usuario_actual = usuario_actual
        
        self.title("Asignación Rápida de Oficios")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.cargar_datos()
        self.crear_interfaz()
    
    def cargar_datos(self):
        """Carga oficios sin asignar y usuarios"""
        # Oficios sin asignar
        self.db.cursor.execute("""
            SELECT o.id, o.numero_oficio, o.asunto, o.fecha_creacion,
                   EXTRACT(DAY FROM (NOW() - o.fecha_creacion)) as dias
            FROM oficios o
            WHERE o.usuario_asignado_id IS NULL
            ORDER BY o.fecha_creacion
        """)
        self.oficios = self.db.cursor.fetchall()
        
        # Usuarios activos
        self.usuarios = self.db.get_usuarios_no_admin()
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="ASIGNACIÓN RÁPIDA DE OFICIOS", 
                 font=('Arial', 14, 'bold')).pack(pady=5)
        
        # Panel superior - Resumen
        resumen_frame = ttk.Frame(main_frame)
        resumen_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(resumen_frame, 
                 text=f"Oficios sin asignar: {len(self.oficios)}").pack(side=tk.LEFT, padx=10)
        ttk.Label(resumen_frame, 
                 text=f"Usuarios disponibles: {len(self.usuarios)}").pack(side=tk.LEFT, padx=10)
        
        # Panel principal con dos listas
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Lista de oficios
        oficios_frame = ttk.LabelFrame(paned, text="Oficios pendientes", padding="10")
        paned.add(oficios_frame, weight=1)
        
        self.crear_lista_oficios(oficios_frame)
        
        # Lista de usuarios
        usuarios_frame = ttk.LabelFrame(paned, text="Usuarios", padding="10")
        paned.add(usuarios_frame, weight=1)
        
        self.crear_lista_usuarios(usuarios_frame)
        
        # Panel de asignación
        asignacion_frame = ttk.LabelFrame(main_frame, text="Asignación", padding="10")
        asignacion_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(asignacion_frame, text="Usuario seleccionado:").grid(row=0, column=0, sticky=tk.W)
        self.usuario_seleccionado = ttk.Label(asignacion_frame, text="Ninguno", foreground="blue")
        self.usuario_seleccionado.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(asignacion_frame, text="Oficios seleccionados:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.oficios_seleccionados = ttk.Label(asignacion_frame, text="0")
        self.oficios_seleccionados.grid(row=1, column=1, sticky=tk.W, padx=10)
        
        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Asignar seleccionados", 
                  command=self.asignar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Asignar todos", 
                  command=self.asignar_todos).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cerrar", 
                  command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def crear_lista_oficios(self, parent):
        """Crea la lista de oficios"""
        # Treeview
        columns = ('ID', 'Número', 'Asunto', 'Días')
        self.tree_oficios = ttk.Treeview(parent, columns=columns, show='headings', height=12)
        
        self.tree_oficios.heading('ID', text='ID')
        self.tree_oficios.heading('Número', text='Número')
        self.tree_oficios.heading('Asunto', text='Asunto')
        self.tree_oficios.heading('Días', text='Días')
        
        self.tree_oficios.column('ID', width=50)
        self.tree_oficios.column('Número', width=120)
        self.tree_oficios.column('Asunto', width=200)
        self.tree_oficios.column('Días', width=50)
        
        # Scrollbar
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree_oficios.yview)
        self.tree_oficios.configure(yscrollcommand=vsb.set)
        
        self.tree_oficios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar oficios
        for o in self.oficios:
            dias = int(o['dias']) if o['dias'] else 0
            tags = ('vencido',) if dias > 3 else ()
            self.tree_oficios.insert('', tk.END, values=(
                o['id'],
                o['numero_oficio'],
                o['asunto'][:50],
                dias
            ), tags=tags)
        
        self.tree_oficios.tag_configure('vencido', background='#ffcccc')
        
        # Bind para selección
        self.tree_oficios.bind('<<TreeviewSelect>>', self.actualizar_contadores)
    
    def crear_lista_usuarios(self, parent):
        """Crea la lista de usuarios"""
        # Treeview
        columns = ('ID', 'Usuario', 'Nombre', 'Email')
        self.tree_usuarios = ttk.Treeview(parent, columns=columns, show='headings', height=12)
        
        self.tree_usuarios.heading('ID', text='ID')
        self.tree_usuarios.heading('Usuario', text='Usuario')
        self.tree_usuarios.heading('Nombre', text='Nombre')
        self.tree_usuarios.heading('Email', text='Email')
        
        self.tree_usuarios.column('ID', width=50)
        self.tree_usuarios.column('Usuario', width=100)
        self.tree_usuarios.column('Nombre', width=150)
        self.tree_usuarios.column('Email', width=150)
        
        # Scrollbar
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=vsb.set)
        
        self.tree_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar usuarios
        for u in self.usuarios:
            self.tree_usuarios.insert('', tk.END, values=(
                u['id'],
                u['username'],
                u['nombre_completo'],
                u['email'] or ''
            ))
        
        # Bind para selección
        self.tree_usuarios.bind('<<TreeviewSelect>>', self.actualizar_contadores)
    
    def actualizar_contadores(self, event=None):
        """Actualiza los contadores de selección"""
        # Usuario seleccionado
        usuario_sel = self.tree_usuarios.selection()
        if usuario_sel:
            item = self.tree_usuarios.item(usuario_sel[0])
            self.usuario_seleccionado.config(text=item['values'][2])
        else:
            self.usuario_seleccionado.config(text="Ninguno")
        
        # Oficios seleccionados
        oficios_sel = len(self.tree_oficios.selection())
        self.oficios_seleccionados.config(text=str(oficios_sel))
    
    def asignar(self):
        """Asigna los oficios seleccionados al usuario seleccionado"""
        usuario_sel = self.tree_usuarios.selection()
        if not usuario_sel:
            messagebox.showerror("Error", "Seleccione un usuario")
            return
        
        oficios_sel = self.tree_oficios.selection()
        if not oficios_sel:
            messagebox.showerror("Error", "Seleccione al menos un oficio")
            return
        
        usuario_item = self.tree_usuarios.item(usuario_sel[0])
        usuario_id = usuario_item['values'][0]
        usuario_nombre = usuario_item['values'][2]
        
        count = 0
        for item in oficios_sel:
            oficio_id = self.tree_oficios.item(item)['values'][0]
            self.db.asignar_oficio(oficio_id, usuario_id)
            count += 1
            self.tree_oficios.delete(item)
        
        messagebox.showinfo("Éxito", f"{count} oficios asignados a {usuario_nombre}")
        self.actualizar_contadores()
    
    def asignar_todos(self):
        """Asigna todos los oficios al usuario seleccionado"""
        usuario_sel = self.tree_usuarios.selection()
        if not usuario_sel:
            messagebox.showerror("Error", "Seleccione un usuario")
            return
        
        if not self.tree_oficios.get_children():
            messagebox.showinfo("Info", "No hay oficios para asignar")
            return
        
        usuario_item = self.tree_usuarios.item(usuario_sel[0])
        usuario_id = usuario_item['values'][0]
        usuario_nombre = usuario_item['values'][2]
        
        count = 0
        for item in self.tree_oficios.get_children():
            oficio_id = self.tree_oficios.item(item)['values'][0]
            self.db.asignar_oficio(oficio_id, usuario_id)
            count += 1
        
        # Limpiar lista
        for item in self.tree_oficios.get_children():
            self.tree_oficios.delete(item)
        
        messagebox.showinfo("Éxito", f"{count} oficios asignados a {usuario_nombre}")