# servidor/dialogs/importar_historicos.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import psycopg2
import mimetypes
import hashlib
from datetime import datetime
from pathlib import Path

class DialogoImportarHistoricos(tk.Toplevel):
    def __init__(self, parent, db, usuario_actual, archivos_gestion):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.usuario_actual = usuario_actual
        self.archivos_gestion = archivos_gestion
        
        self.title("Importar Archivos Históricos")
        self.geometry("900x700")
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.archivos_seleccionados = []
        self.check_vars = {}
        
        self.crear_interfaz()

    def crear_interfaz(self):
        """Crea la interfaz del diálogo con scroll"""
        # Configurar tamaño de la ventana más amplio para evitar scroll horizontal
        self.geometry("1200x700")  # Aumentado de 900 a 1200
        self.minsize(1000, 600)    # Mínimo aumentado de 800 a 1000
        
        # Contenedor principal con scroll (solo vertical ahora)
        main_canvas = tk.Canvas(self)
        v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=v_scrollbar.set)
        
        main_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side="right", fill="y")
        
        # Frame principal dentro del scroll
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="IMPORTAR ARCHIVOS HISTÓRICOS", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Label(main_frame, text="Seleccione archivos PDF/Excel/Word que ya fueron atendidos",
                font=('Arial', 10)).pack(pady=5)
        
        # Frame para botones de selección
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📂 Seleccionar archivos", 
                command=self.seleccionar_archivos).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🗑️ Limpiar selección", 
                command=self.limpiar_seleccion).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(btn_frame, text=f"Total: 0 archivos", font=('Arial', 9, 'bold'), 
                foreground='blue').pack(side=tk.RIGHT, padx=10)
        
        # Frame para lista de archivos (con scroll vertical)
        list_frame = ttk.LabelFrame(main_frame, text="Archivos seleccionados", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas con scroll para lista (solo vertical)
        list_canvas = tk.Canvas(list_frame)
        list_v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=list_canvas.yview)
        scrollable_list_frame = ttk.Frame(list_canvas)
        
        scrollable_list_frame.bind(
            "<Configure>",
            lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all"))
        )
        
        list_canvas.create_window((0, 0), window=scrollable_list_frame, anchor="nw")
        list_canvas.configure(yscrollcommand=list_v_scrollbar.set)
        
        list_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        list_v_scrollbar.pack(side="right", fill="y")
        
        self.lista_frame = scrollable_list_frame
        
        # Frame para datos del oficio (sin scroll interno)
        datos_frame = ttk.LabelFrame(main_frame, text="Datos del oficio (para todos los archivos)", padding="10")
        datos_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame interno para los datos
        datos_interno = ttk.Frame(datos_frame)
        datos_interno.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Campos comunes
        row = 0
        
        # Número de oficio
        ttk.Label(datos_interno, text="Número de oficio (base):", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=5)
        self.numero_base = ttk.Entry(datos_interno, width=80)
        self.numero_base.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W)
        ttk.Label(datos_interno, text="Ej: OF-2024-", font=('Arial', 8), foreground='gray').grid(
            row=row, column=2, sticky=tk.W, padx=5)
        row += 1
        
        # Destinatario
        ttk.Label(datos_interno, text="Destinatario:*", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=5)
        self.destinatario = ttk.Entry(datos_interno, width=80)
        self.destinatario.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W, columnspan=2)
        self.destinatario.insert(0, "Por definir")
        row += 1
        
        # Asunto
        ttk.Label(datos_interno, text="Asunto:*", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=5)
        self.asunto = tk.Text(datos_interno, height=4, width=80, font=('Arial', 10))
        self.asunto.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W, columnspan=2)
        row += 1
        
        # Fecha de oficio
        ttk.Label(datos_interno, text="Fecha de oficio:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=5)
        self.fecha = ttk.Entry(datos_interno, width=80)
        self.fecha.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W, columnspan=2)
        self.fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        row += 1
        
        # Usuario asignado
        ttk.Label(datos_interno, text="Usuario asignado:*", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=5)
        self.usuario_combo = ttk.Combobox(datos_interno, width=77, state='readonly')
        self.usuario_combo.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W, columnspan=2)
        self.cargar_usuarios()
        row += 1
        
        # Checkbox para indicar que ya fue atendido
        self.atendido_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(datos_interno, text="Marcar como ya atendido", 
                    variable=self.atendido_var).grid(row=row, column=0, columnspan=3, pady=10, sticky=tk.W)
        row += 1
        
        # Nota adicional
        ttk.Label(datos_interno, text="Nota adicional:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=8, padx=5)
        self.nota = tk.Text(datos_interno, height=3, width=80, font=('Arial', 10))
        self.nota.grid(row=row, column=1, pady=8, padx=10, sticky=tk.W, columnspan=2)
        row += 1
        
        # Configurar el peso de las columnas
        datos_interno.grid_columnconfigure(1, weight=1)
        
        # Botones de acción
        btn_acciones = ttk.Frame(main_frame)
        btn_acciones.pack(fill=tk.X, pady=15)
        
        ttk.Button(btn_acciones, text="💾 Importar seleccionados", 
                command=self.importar_seleccionados,
                width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_acciones, text="📦 Importar todos", 
                command=self.importar_todos,
                width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_acciones, text="❌ Cancelar", 
                command=self.destroy,
                width=15).pack(side=tk.RIGHT, padx=5)
        
        # Agregar un frame inferior para dar espacio
        ttk.Frame(main_frame, height=20).pack()
    
    def cargar_usuarios(self):
        """Carga los usuarios en el combobox"""
        self.db.cursor.execute("""
            SELECT id, nombre_completo FROM usuarios 
            WHERE activo = TRUE AND es_admin = FALSE
            ORDER BY nombre_completo
        """)
        usuarios = self.db.cursor.fetchall()
        valores = [f"{u['id']} - {u['nombre_completo']}" for u in usuarios]
        self.usuario_combo['values'] = valores
        if valores:
            self.usuario_combo.current(0)
    
    def seleccionar_archivos(self):
        """Selecciona archivos para importar"""
        archivos = filedialog.askopenfilenames(
            title="Seleccionar archivos históricos",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Excel files", "*.xlsx *.xls"),
                ("Word files", "*.docx *.doc"),
                ("All files", "*.*")
            ]
        )
        
        for archivo in archivos:
            if archivo not in self.archivos_seleccionados:
                self.archivos_seleccionados.append(archivo)
        
        self.actualizar_lista()
    
    def limpiar_seleccion(self):
        """Limpia la selección de archivos"""
        self.archivos_seleccionados = []
        self.actualizar_lista()
    
    def actualizar_lista(self):
        """Actualiza la lista de archivos seleccionados"""
        # Limpiar frame
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        
        self.check_vars = {}
        
        # Actualizar contador
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                for frame in child.winfo_children():
                    if isinstance(frame, ttk.Frame):
                        for btn_frame in frame.winfo_children():
                            if isinstance(btn_frame, ttk.Frame):
                                for label in btn_frame.winfo_children():
                                    if isinstance(label, ttk.Label) and "Total:" in label.cget("text"):
                                        label.config(text=f"Total: {len(self.archivos_seleccionados)} archivos")
        
        for archivo in self.archivos_seleccionados:
            var = tk.BooleanVar(value=True)
            self.check_vars[archivo] = var
            
            file_frame = ttk.Frame(self.lista_frame)
            file_frame.pack(fill=tk.X, pady=2)
            
            cb = ttk.Checkbutton(file_frame, text=os.path.basename(archivo), variable=var)
            cb.pack(side=tk.LEFT, anchor=tk.W)
    
    def importar_seleccionados(self):
        """Importa los archivos seleccionados"""
        seleccionados = [archivo for archivo, var in self.check_vars.items() if var.get()]
        
        if not seleccionados:
            messagebox.showerror("Error", "Seleccione al menos un archivo")
            return
        
        if not self.asunto.get('1.0', tk.END).strip():
            messagebox.showerror("Error", "Complete el asunto")
            return
        
        if not self.destinatario.get().strip():
            messagebox.showerror("Error", "Complete el destinatario")
            return
        
        if not self.usuario_combo.get():
            messagebox.showerror("Error", "Seleccione un usuario asignado")
            return
        
        usuario_id = int(self.usuario_combo.get().split(' - ')[0])
        numero_base = self.numero_base.get().strip()
        
        self.importar_archivos(seleccionados, usuario_id, numero_base)
    
    def importar_todos(self):
        """Importa todos los archivos"""
        if not self.archivos_seleccionados:
            messagebox.showerror("Error", "No hay archivos seleccionados")
            return
        
        if not self.asunto.get('1.0', tk.END).strip():
            messagebox.showerror("Error", "Complete el asunto")
            return
        
        if not self.destinatario.get().strip():
            messagebox.showerror("Error", "Complete el destinatario")
            return
        
        if not self.usuario_combo.get():
            messagebox.showerror("Error", "Seleccione un usuario asignado")
            return
        
        usuario_id = int(self.usuario_combo.get().split(' - ')[0])
        numero_base = self.numero_base.get().strip()
        
        self.importar_archivos(self.archivos_seleccionados, usuario_id, numero_base)
    
    def importar_archivos(self, archivos, usuario_id, numero_base):
        """Importa los archivos a la base de datos"""
        importados = 0
        errores = []
        asunto_text = self.asunto.get('1.0', tk.END).strip()
        destinatario_text = self.destinatario.get().strip()
        remitente_fijo = "Archivo Histórico - Importación"
        
        for archivo in archivos:
            try:
                nombre_archivo = os.path.basename(archivo)
                nombre_sin_ext = os.path.splitext(nombre_archivo)[0]
                
                # Generar número de oficio
                if numero_base:
                    numero_oficio = f"{numero_base}{nombre_sin_ext}"
                else:
                    numero_oficio = nombre_sin_ext
                
                # Leer contenido
                with open(archivo, 'rb') as f:
                    contenido = f.read()
                
                # Verificar si ya existe
                self.db.cursor.execute(
                    "SELECT id FROM oficios WHERE numero_oficio = %s", 
                    (numero_oficio,)
                )
                oficio_existente = self.db.cursor.fetchone()
                
                nota_adicional = self.nota.get('1.0', tk.END).strip()
                nota_completa = f"[IMPORTADO HISTÓRICO] Archivo: {nombre_archivo}"
                if nota_adicional:
                    nota_completa += f" - {nota_adicional}"
                
                if oficio_existente:
                    # Si existe, solo agregar archivo binario
                    mime_type = mimetypes.guess_type(archivo)[0] or 'application/octet-stream'
                    hash_md5 = hashlib.md5(contenido).hexdigest()
                    
                    self.db.cursor.execute("""
                        INSERT INTO archivos_binarios 
                        (oficio_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id, hash_md5)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (oficio_existente['id'], 'acuse', nombre_archivo, 
                          psycopg2.Binary(contenido), mime_type, len(contenido), 
                          self.usuario_actual['id'], hash_md5))
                    
                    # Actualizar nota
                    self.db.cursor.execute("""
                        UPDATE oficios 
                        SET notas = CONCAT(COALESCE(notas, ''), '\n', %s)
                        WHERE id = %s
                    """, (nota_completa, oficio_existente['id']))
                    
                else:
                    # Crear nuevo oficio
                    mime_type = mimetypes.guess_type(archivo)[0] or 'application/octet-stream'
                    hash_md5 = hashlib.md5(contenido).hexdigest()
                    
                    # Insertar oficio - estado Atendido para que aparezca en el cliente
                    self.db.cursor.execute("""
                        INSERT INTO oficios 
                        (numero_oficio, fecha_oficio, remitente, destinatario, asunto, 
                         tipo_oficio, prioridad, estado, usuario_asignado_id, 
                         created_by, notas, fecha_atendido, acuse_recibido)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        numero_oficio,
                        self.fecha.get(),
                        remitente_fijo,
                        destinatario_text,
                        asunto_text,
                        'Oficio',
                        'Normal',
                        'Atendido',  # ✅ Estado Atendido para que aparezca en el cliente
                        usuario_id,
                        self.usuario_actual['id'],
                        nota_completa,
                        datetime.now(),
                        True  # ✅ acuse_recibido = TRUE
                    ))
                    
                    oficio_id = self.db.cursor.fetchone()['id']
                    
                    # Guardar archivo como acuse
                    self.db.cursor.execute("""
                        INSERT INTO archivos_binarios 
                        (oficio_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id, hash_md5)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (oficio_id, 'acuse', nombre_archivo, 
                          psycopg2.Binary(contenido), mime_type, len(contenido), 
                          self.usuario_actual['id'], hash_md5))
                
                importados += 1
                
            except Exception as e:
                errores.append(f"{nombre_archivo}: {str(e)}")
        
        # Mostrar resultado
        mensaje = f"✅ Importados: {importados} archivos"
        if errores:
            mensaje += f"\n❌ Errores: {len(errores)}\n" + "\n".join(errores[:5])
        
        messagebox.showinfo("Resultado de importación", mensaje)
        
        if importados > 0:
            self.destroy()
            # Actualizar vistas
            if hasattr(self.parent, 'actualizar_todo'):
                self.parent.actualizar_todo()