# oficios_gestion.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from .dialogs.oficios_dialog import DialogoOficio
from .dialogs.estado_dialog import DialogoCambiarEstado
from .dialogs.detalle_dialog import DialogoDetalle
from .dialogs.reasignar_dialog import DialogoReasignar
from .dialogs.acuse_dialog import DialogoRegistrarAcuse

import logging
logger = logging.getLogger(__name__)


class GestionOficios:
    def __init__(self, parent, db, usuario_actual, config, notificador, archivos_gestion):
        self.parent = parent
        self.db = db
        self.usuario_actual = usuario_actual
        self.config = config
        self.notificador = notificador
        self.archivos_gestion = archivos_gestion
        self.tree = None
        self.filtros = {}
        self.filtro_estado = tk.StringVar(value="Todos")
        self.filtro_usuario = tk.StringVar(value="Todos")
        self.busqueda = tk.StringVar()
        self.solo_activos = tk.BooleanVar(value=False)
        
    def crear_pestana(self, notebook):
        """Crea la pestaña de gestión de oficios"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📋 Gestión de Oficios")
        
        # Filtros
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(filter_frame, text="Filtrar por estado:").pack(side=tk.LEFT, padx=5)
        self.estado_combo = ttk.Combobox(filter_frame, textvariable=self.filtro_estado,
                                        values=['Todos', 'En Proceso', 'Atendido', 'Archivado'],
                                        width=15, state='readonly')
        self.estado_combo.pack(side=tk.LEFT, padx=5)
        self.estado_combo.bind('<<ComboboxSelected>>', lambda e: self.cargar_oficios())
        
        ttk.Label(filter_frame, text="Usuario:").pack(side=tk.LEFT, padx=5)
        self.usuario_combo = ttk.Combobox(filter_frame, textvariable=self.filtro_usuario,
                                        values=['Todos'], width=20, state='readonly')
        self.usuario_combo.pack(side=tk.LEFT, padx=5)
        self.usuario_combo.bind('<<ComboboxSelected>>', lambda e: self.cargar_oficios())
        
        # ✅ Llamar al método para cargar usuarios
        self.cargar_usuarios_combo()
        
        ttk.Label(filter_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(filter_frame, textvariable=self.busqueda, width=25).pack(side=tk.LEFT, padx=5)
        self.busqueda.trace('w', lambda *args: self.cargar_oficios())
        
        ttk.Button(filter_frame, text="🔄 Actualizar", command=self.cargar_oficios).pack(side=tk.RIGHT, padx=5)
        
        # TreeView
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(tree_frame)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Columnas del servidor
        columns = ('Número de Oficio', 'Fecha de Ingreso', 'Fecha de Respuesta', 'Asunto', 'Estado', 'Prioridad', 'Nota')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                yscrollcommand=vsb.set, xscrollcommand=hsb.set, height=20)
        
        widths = [150, 100, 100, 400, 120, 90, 200]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.bind('<Double-Button-1>', self.ver_detalle)
        self.tree.bind('<Button-3>', self.mostrar_menu_contextual)
        
        # Menú contextual
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="👁️ Ver detalle", command=lambda: self.ver_detalle(None))
        self.context_menu.add_command(label="✏️ Editar", command=self.editar_seleccionado)
        self.context_menu.add_command(label="🔄 Reasignar", command=self.reasignar_seleccionado)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Eliminar", command=self.eliminar_seleccionado)

    def cargar_usuarios_combo(self):
        """Carga los usuarios en el combobox de filtro"""
        try:
            usuarios = self.db.get_usuarios(solo_activos=True)
            valores = ['Todos']
            for u in usuarios:
                valores.append(f"{u['id']} - {u['nombre_completo']}")
            self.usuario_combo['values'] = valores
            self.usuario_combo.current(0)
        except Exception as e:
            logger.error(f"Error cargando usuarios: {e}")
    
    def crear_treeview(self, parent):
        """Crea el TreeView principal"""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Número', 'Fecha', 'Remitente', 'Asunto', 'Estado', 'Prioridad', 'Acuse', 'Asignado', 'Días')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        widths = [50, 120, 100, 150, 250, 100, 80, 60, 100, 60]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bindings
        self.tree.bind('<Double-Button-1>', self.ver_detalle)
        self.tree.bind('<Button-3>', self.mostrar_menu_contextual)
        
        # Menú contextual - simplificado
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="👁️ Ver detalle", command=lambda: self.ver_detalle(None))
        self.context_menu.add_command(label="✏️ Editar", command=self.editar_seleccionado)
        self.context_menu.add_command(label="🔄 Reasignar", command=self.reasignar_seleccionado)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Eliminar", command=self.eliminar_seleccionado)
        
        # Configurar tags para colores
        self.tree.tag_configure('vencido', background='#ffcccc')
        self.tree.tag_configure('proceso', background='#fff3cd')
        self.tree.tag_configure('atendido', background='#d4edda')
    
    def crear_botones_accion(self, parent):
        """Crea botones de acción - simplificado"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="👁️ Ver detalle", 
                  command=lambda: self.ver_detalle(None)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏️ Editar", 
                  command=self.editar_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Reasignar", 
                  command=self.reasignar_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📁 Ver Archivo", 
                  command=self.ver_archivo_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Actualizar", 
                  command=self.cargar_oficios).pack(side=tk.RIGHT, padx=2)
    
    def actualizar_combo_usuarios(self):
        """Actualiza el combobox de usuarios"""
        usuarios = self.db.get_usuarios(solo_activos=True)
        valores = ['Todos'] + [u['username'] for u in usuarios]
        self.filtro_usuario_combo['values'] = valores
    
    def cargar_oficios(self):
        """Carga los oficios en el TreeView con nota resumida"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        query = """
            SELECT o.*, u.nombre_completo as asignado_nombre,
                (SELECT COUNT(*) FROM archivos_binarios WHERE oficio_id = o.id AND tipo = 'oficio') as tiene_archivo,
                (SELECT COUNT(*) FROM archivos_binarios WHERE oficio_id = o.id AND tipo = 'acuse') as tiene_acuse
            FROM oficios o 
            LEFT JOIN usuarios u ON o.usuario_asignado_id = u.id
            WHERE 1=1
        """
        params = []
        
        if self.filtro_estado.get() != "Todos":
            query += " AND o.estado = %s"
            params.append(self.filtro_estado.get())
        
        if self.filtro_usuario.get() != "Todos":
            usuario_id = int(self.filtro_usuario.get().split(' - ')[0])
            query += " AND o.usuario_asignado_id = %s"
            params.append(usuario_id)
        
        if self.busqueda.get():
            query += " AND (o.numero_oficio ILIKE %s OR o.remitente ILIKE %s OR o.asunto ILIKE %s)"
            busqueda = f"%{self.busqueda.get()}%"
            params.extend([busqueda, busqueda, busqueda])
        
        query += " ORDER BY o.fecha_creacion DESC"
        
        self.db.cursor.execute(query, params)
        oficios = self.db.cursor.fetchall()
        
        for o in oficios:
            # Fecha de respuesta
            fecha_respuesta = ""
            if o['fecha_atendido']:
                fecha_respuesta = o['fecha_atendido'].strftime('%d/%m/%Y')
            
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
            elif o['estado'] == 'Archivado':
                tags = ('archivado',)
            
            self.tree.insert('', tk.END, values=(
                o['numero_oficio'],
                o['fecha_oficio'].strftime('%d/%m/%Y') if o['fecha_oficio'] else '',
                fecha_respuesta,
                o['asunto'][:60] + ('...' if len(o['asunto']) > 60 else ''),
                o['estado'],
                o['prioridad'],
                nota_resumida
            ), tags=tags)
        
        self.tree.tag_configure('atendido', background='#d4edda')
        self.tree.tag_configure('proceso', background='#fff3cd')
        self.tree.tag_configure('archivado', background='#e2e3e5')
    def editar_seleccionado(self):
        """Edita el oficio seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Info", "Seleccione un oficio")
            return
        
        item = self.tree.item(seleccion[0])
        oficio_id = item['values'][0]
        
        from .dialogs.oficios_dialog import DialogoOficio
        
        dialog = DialogoOficio(self.parent, self.db, self.usuario_actual, 
                               self.archivos_gestion, modo='editar', oficio_id=oficio_id)
        self.parent.wait_window(dialog)
        self.cargar_oficios()
    
    def reasignar_seleccionado(self):
        """Reasigna el oficio seleccionado a otro usuario"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Info", "Seleccione un oficio")
            return
        
        item = self.tree.item(seleccion[0])
        oficio_id = item['values'][0]
        
        from .dialogs.reasignar_dialog import DialogoReasignar
        
        dialog = DialogoReasignar(self.parent, self.db, self.notificador, 
                                   oficio_id, self.usuario_actual)
        self.parent.wait_window(dialog)
        self.cargar_oficios()
    
    def eliminar_seleccionado(self):
        """Elimina el oficio seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        oficio_id = item['values'][0]
        numero = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar oficio {numero}?"):
            try:
                self.db.delete_oficio(oficio_id)
                messagebox.showinfo("Éxito", "Oficio eliminado")
                self.cargar_oficios()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")
    
    def ver_archivo_seleccionado(self):
        """Abre el archivo del oficio seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        oficio_id = item['values'][0]
        
        self.archivos_gestion.ver_archivo(oficio_id)
    
    def ver_detalle(self, event):
        """Muestra detalle del oficio seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        # ✅ CORRECCIÓN: Obtener número de oficio y buscar ID real
        oficio_numero = item['values'][0]  # Primera columna es "Número de Oficio"
        
        # Buscar el ID real por número de oficio
        self.db.cursor.execute("SELECT id FROM oficios WHERE numero_oficio = %s", (oficio_numero,))
        resultado = self.db.cursor.fetchone()
        if not resultado:
            messagebox.showerror("Error", f"No se encontró el oficio {oficio_numero}")
            return
        
        oficio_id = resultado['id']
        
        from .dialogs.detalle_dialog import DialogoDetalle
        DialogoDetalle(self.parent, self.db, oficio_id)

    def editar_seleccionado(self):
        """Edita el oficio seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Info", "Seleccione un oficio")
            return
        
        item = self.tree.item(seleccion[0])
        oficio_numero = item['values'][0]  # ✅ Número de oficio
        
        # Buscar ID real
        self.db.cursor.execute("SELECT id FROM oficios WHERE numero_oficio = %s", (oficio_numero,))
        resultado = self.db.cursor.fetchone()
        if not resultado:
            messagebox.showerror("Error", f"No se encontró el oficio {oficio_numero}")
            return
        
        oficio_id = resultado['id']
        
        from .dialogs.oficios_dialog import DialogoOficio
        
        dialog = DialogoOficio(self.parent, self.db, self.usuario_actual, 
                            self.archivos_gestion, modo='editar', oficio_id=oficio_id)
        self.parent.wait_window(dialog)
        self.cargar_oficios()

    def reasignar_seleccionado(self):
        """Reasigna el oficio seleccionado a otro usuario"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Info", "Seleccione un oficio")
            return
        
        item = self.tree.item(seleccion[0])
        oficio_numero = item['values'][0]  # ✅ Número de oficio
        
        # Buscar ID real
        self.db.cursor.execute("SELECT id FROM oficios WHERE numero_oficio = %s", (oficio_numero,))
        resultado = self.db.cursor.fetchone()
        if not resultado:
            messagebox.showerror("Error", f"No se encontró el oficio {oficio_numero}")
            return
        
        oficio_id = resultado['id']
        
        from .dialogs.reasignar_dialog import DialogoReasignar
        
        dialog = DialogoReasignar(self.parent, self.db, self.notificador, 
                                oficio_id, self.usuario_actual)
        self.parent.wait_window(dialog)
        self.cargar_oficios()

    def eliminar_seleccionado(self):
        """Elimina el oficio seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        oficio_numero = item['values'][0]  # ✅ Número de oficio
        
        # Buscar ID real
        self.db.cursor.execute("SELECT id FROM oficios WHERE numero_oficio = %s", (oficio_numero,))
        resultado = self.db.cursor.fetchone()
        if not resultado:
            messagebox.showerror("Error", f"No se encontró el oficio {oficio_numero}")
            return
        
        oficio_id = resultado['id']
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar oficio {oficio_numero}?"):
            try:
                self.db.delete_oficio(oficio_id)
                messagebox.showinfo("Éxito", "Oficio eliminado")
                self.cargar_oficios()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def ver_archivo_seleccionado(self):
        """Abre el archivo del oficio seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        oficio_numero = item['values'][0]  # ✅ Número de oficio
        
        # Buscar ID real
        self.db.cursor.execute("SELECT id FROM oficios WHERE numero_oficio = %s", (oficio_numero,))
        resultado = self.db.cursor.fetchone()
        if not resultado:
            messagebox.showerror("Error", f"No se encontró el oficio {oficio_numero}")
            return
        
        oficio_id = resultado['id']
        
        self.archivos_gestion.ver_archivo(oficio_id)
    
    def mostrar_menu_contextual(self, event):
        """Muestra menú contextual"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def limpiar_filtros(self):
        """Limpia los filtros"""
        self.filtro_estado.set("Todos")
        self.filtro_usuario.set("Todos")
        self.busqueda.set("")
        self.solo_activos.set(False)
        self.cargar_oficios()