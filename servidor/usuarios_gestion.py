# usuarios_gestion.py
import tkinter as tk
from tkinter import ttk, messagebox

from .dialogs.usuario_dialog import DialogoUsuario
from .dialogs.reasignar_usuario_dialog import DialogoReasignarUsuario

class GestionUsuarios:
    def __init__(self, parent, db, usuario_actual):
        self.parent = parent
        self.db = db
        self.usuario_actual = usuario_actual
        self.tree = None
    
    def crear_pestana(self, notebook):
        """Crea la pestaña de gestión de usuarios"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="👥 Usuarios")
        
        # TreeView
        self.crear_treeview(frame)
        
        # Botones
        self.crear_botones(frame)
        
        # Cargar datos
        self.cargar_usuarios()
        
        return frame
    
    def crear_treeview(self, parent):
        """Crea el TreeView de usuarios"""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Username', 'Nombre', 'Email', 'Admin', 'Activo', 'Color Manual')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        widths = [50, 100, 200, 200, 60, 60, 80]
        headings = ['ID', 'Usuario', 'Nombre Completo', 'Email', 'Admin', 'Activo', 'Color Manual']
        
        for col, heading, width in zip(columns, headings, widths):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width)
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bindings
        self.tree.bind('<Double-Button-1>', self.editar_seleccionado)
        self.tree.bind('<Button-3>', self.mostrar_menu_contextual)
        
        # Menú contextual
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="✏️ Editar", command=self.editar_seleccionado)
        self.context_menu.add_command(label="🔄 Activar/Desactivar", command=self.toggle_estado)
        self.context_menu.add_command(label="🎨 Marcar Verde", command=self.marcar_verde)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Eliminar", command=self.eliminar_seleccionado)
    
    def crear_botones(self, parent):
        """Crea los botones de acción"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="➕ Nuevo Usuario", 
                  command=self.nuevo_usuario).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏️ Editar", 
                  command=self.editar_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Activar/Desactivar", 
                  command=self.toggle_estado).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🎨 Marcar Verde", 
                  command=self.marcar_verde).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="❌ Eliminar", 
                  command=self.eliminar_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Actualizar", 
                  command=self.cargar_usuarios).pack(side=tk.RIGHT, padx=2)
    
    def cargar_usuarios(self):
        """Carga los usuarios en el treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        usuarios = self.db.get_usuarios(solo_activos=False)
        
        for u in usuarios:
            admin = "✅" if u['es_admin'] else "❌"
            activo = "✅" if u['activo'] else "❌"
            color = u['color_manual'] or ''
            
            self.tree.insert('', tk.END, values=(
                u['id'],
                u['username'],
                u['nombre_completo'],
                u['email'] or '',
                admin,
                activo,
                color
            ))
    
    def nuevo_usuario(self):
        """Abre diálogo para nuevo usuario"""
        from .dialogs.usuario_dialog import DialogoUsuario
        
        dialog = DialogoUsuario(self.parent, self.db, modo='nuevo')
        self.parent.wait_window(dialog)
        self.cargar_usuarios()
    
    def editar_seleccionado(self, event=None):
        """Edita el usuario seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Info", "Seleccione un usuario")
            return
        
        item = self.tree.item(seleccion[0])
        user_id = item['values'][0]
        
        from .dialogs.usuario_dialog import DialogoUsuario
        
        dialog = DialogoUsuario(self.parent, self.db, modo='editar', usuario_id=user_id)
        self.parent.wait_window(dialog)
        self.cargar_usuarios()
    
    def toggle_estado(self):
        """Activa/Desactiva usuario"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        user_id = item['values'][0]
        username = item['values'][1]
        activo_actual = item['values'][5] == '✅'
        
        nuevo_estado = not activo_actual
        accion = "activar" if nuevo_estado else "desactivar"
        
        if messagebox.askyesno("Confirmar", f"¿{accion.capitalize()} usuario {username}?"):
            self.db.update_usuario(user_id, {'activo': nuevo_estado})
            self.cargar_usuarios()
    
    def marcar_verde(self):
        """Marca un usuario como verde (omisión)"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Info", "Seleccione un usuario")
            return
        
        item = self.tree.item(seleccion[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        if messagebox.askyesno("Confirmar", 
                              f"¿Marcar a {username} como verde en reportes?"):
            self.db.update_usuario(user_id, {'color_manual': 'verde'})
            self.cargar_usuarios()
            messagebox.showinfo("Éxito", "Usuario marcado como verde")
    
    def eliminar_seleccionado(self):
        """Elimina el usuario seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        # Verificar si tiene oficios
        self.db.cursor.execute("SELECT COUNT(*) as total FROM oficios WHERE usuario_asignado_id = %s", (user_id,))
        oficios_asignados = self.db.cursor.fetchone()['total']
        
        if oficios_asignados > 0:
            respuesta = messagebox.askyesno(
                "Confirmar eliminación",
                f"El usuario {username} tiene {oficios_asignados} oficios asignados.\n"
                "¿Desea reasignar esos oficios a otro usuario antes de eliminar?"
            )
            if respuesta:
                self.reasignar_antes_eliminar(user_id, username)
                return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar usuario {username}?"):
            try:
                self.db.delete_usuario(user_id)
                self.cargar_usuarios()
                messagebox.showinfo("Éxito", "Usuario eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")
    
    def reasignar_antes_eliminar(self, user_id, username):
        """Reasigna oficios antes de eliminar"""
        from .dialogs.reasignar_usuario_dialog import DialogoReasignarUsuario
        
        dialog = DialogoReasignarUsuario(self.parent, self.db, user_id, username)
        self.parent.wait_window(dialog)
        self.cargar_usuarios()
    
    def mostrar_menu_contextual(self, event):
        """Muestra menú contextual"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)