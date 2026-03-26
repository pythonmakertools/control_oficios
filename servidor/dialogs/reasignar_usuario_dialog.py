# dialogs/reasignar_usuario_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox

class DialogoReasignarUsuario(tk.Toplevel):
    def __init__(self, parent, db, usuario_id, username):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.usuario_id = usuario_id
        self.username = username
        
        self.title("Reasignar Oficios antes de Eliminar")
        self.geometry("650x500")
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.cargar_datos()
        self.crear_interfaz()
    
    def cargar_datos(self):
        """Carga los oficios del usuario y otros usuarios"""
        # Obtener oficios del usuario
        self.db.cursor.execute("""
            SELECT id, numero_oficio, asunto, fecha_creacion 
            FROM oficios 
            WHERE usuario_asignado_id = %s
            ORDER BY fecha_creacion DESC
        """, (self.usuario_id,))
        self.oficios = self.db.cursor.fetchall()
        
        # Obtener otros usuarios
        self.db.cursor.execute("""
            SELECT id, nombre_completo, username 
            FROM usuarios 
            WHERE id != %s AND activo = TRUE
            ORDER BY nombre_completo
        """, (self.usuario_id,))
        self.otros_usuarios = self.db.cursor.fetchall()
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="REASIGNAR OFICIOS", 
                 font=('Arial', 14, 'bold')).pack(pady=5)
        
        ttk.Label(main_frame, 
                 text=f"El usuario {self.username} tiene {len(self.oficios)} oficios asignados",
                 font=('Arial', 10)).pack(pady=5)
        
        # Selección de usuario destino
        destino_frame = ttk.LabelFrame(main_frame, text="Reasignar a:", padding="10")
        destino_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(destino_frame, text="Usuario destino:").pack(anchor=tk.W)
        
        self.usuario_destino = ttk.Combobox(destino_frame, 
                                           values=[f"{u['id']} - {u['nombre_completo']} (@{u['username']})" 
                                                  for u in self.otros_usuarios],
                                           width=60, state='readonly')
        self.usuario_destino.pack(fill=tk.X, pady=5)
        
        # Lista de oficios
        oficios_frame = ttk.LabelFrame(main_frame, text="Oficios a reasignar", padding="10")
        oficios_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para oficios
        tree_frame = ttk.Frame(oficios_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Número', 'Asunto', 'Fecha')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Número', text='Número')
        self.tree.heading('Asunto', text='Asunto')
        self.tree.heading('Fecha', text='Fecha')
        
        self.tree.column('ID', width=50)
        self.tree.column('Número', width=150)
        self.tree.column('Asunto', width=300)
        self.tree.column('Fecha', width=100)
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar oficios
        for o in self.oficios:
            self.tree.insert('', tk.END, values=(
                o['id'],
                o['numero_oficio'],
                o['asunto'][:60],
                o['fecha_creacion'].strftime('%d/%m/%Y')
            ))
        
        # Seleccionar todos por defecto
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        
        # Opciones
        opciones_frame = ttk.Frame(main_frame)
        opciones_frame.pack(fill=tk.X, pady=5)
        
        self.mover_todos = tk.BooleanVar(value=True)
        ttk.Checkbutton(opciones_frame, text="Mover todos los oficios", 
                       variable=self.mover_todos,
                       command=self.toggle_seleccion).pack(anchor=tk.W)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(btn_frame, text="Reasignar y Eliminar", 
                  command=self.reasignar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def toggle_seleccion(self):
        """Selecciona/deselecciona todos los oficios"""
        if self.mover_todos.get():
            for item in self.tree.get_children():
                self.tree.selection_add(item)
        else:
            for item in self.tree.get_children():
                self.tree.selection_remove(item)
    
    def reasignar(self):
        """Reasigna los oficios seleccionados"""
        if not self.usuario_destino.get():
            messagebox.showerror("Error", "Seleccione un usuario destino")
            return
        
        seleccionados = self.tree.selection()
        if not seleccionados:
            messagebox.showerror("Error", "Seleccione al menos un oficio para reasignar")
            return
        
        usuario_destino_id = int(self.usuario_destino.get().split(' - ')[0])
        
        try:
            # Reasignar cada oficio seleccionado
            for item in seleccionados:
                oficio_id = self.tree.item(item)['values'][0]
                self.db.asignar_oficio(oficio_id, usuario_destino_id)
            
            # Eliminar usuario
            self.db.delete_usuario(self.usuario_id)
            
            messagebox.showinfo("Éxito", 
                              f"{len(seleccionados)} oficios reasignados y usuario eliminado")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al reasignar: {e}")