# dialogs/asignar_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
import fitz  # PyMuPDF para PDF
import openpyxl
from PIL import Image, ImageTk
import io
import psycopg2
import hashlib
import mimetypes
import threading
import json
from pathlib import Path
# Al inicio del archivo, asegurar:
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

class DialogoAsignarOficios(tk.Toplevel):
    def __init__(self, parent, archivos, carpeta_origen, db, usuario_actual, archivos_gestion, callback=None):
        super().__init__(parent)
        self.parent = parent
        self.archivos = archivos
        self.carpeta_origen = carpeta_origen
        self.db = db
        self.usuario_actual = usuario_actual
        self.archivos_gestion = archivos_gestion
        self.callback = callback
        
        self.title("Asignar Oficios")
        self.geometry("1300x750")
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1300 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.archivo_actual = 0
        self.check_vars = {}
        self.preview_images = []
        self.current_page = 0
        self.max_pages = 0
        self.preview_loading = False
        self.current_preview_archivo = None
        self.sashes_guardadas = None
        
        self.cargar_configuracion_ventana()
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)
        
        self.crear_interfaz()
        self.cargar_lista_archivos()
    
    # ==================== INTERFAZ ====================
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        # Frame principal
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior para el contenido
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear PanedWindow horizontal
        self.paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo - Lista de archivos
        self.left_frame = ttk.LabelFrame(self.paned, text="Archivos a asignar", padding="10")
        self.paned.add(self.left_frame, weight=10)
        
        # Panel central - Previsualización
        self.preview_frame = ttk.LabelFrame(self.paned, text="Previsualización", padding="10")
        self.paned.add(self.preview_frame, weight=50)
        
        # Panel derecho - Datos del oficio
        self.right_frame = ttk.LabelFrame(self.paned, text="Datos del oficio", padding="10")
        self.paned.add(self.right_frame, weight=40)
        
        # Crear el contenido de cada panel
        self.crear_lista_archivos(self.left_frame)
        self.crear_previsualizacion(self.preview_frame)
        self.crear_datos_oficio_con_scroll(self.right_frame)
        
        # Frame inferior para botones
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        self.crear_botones(button_frame)
        
        # Aplicar sashes guardadas después de crear la interfaz
        self.after(200, self.aplicar_sashes_guardadas)
    
    def crear_lista_archivos(self, parent):
        """Crea la lista de archivos con checkboxes"""
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.checkbox_frame = scrollable_frame
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def crear_previsualizacion(self, parent):
        """Crea el área de previsualización"""
        preview_container = ttk.Frame(parent)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(preview_container, highlightthickness=0, bg='white')
        v_scrollbar = ttk.Scrollbar(preview_container, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(preview_container, orient="horizontal", command=canvas.xview)
        
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.preview_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.preview_frame, anchor="nw")
        
        self.preview_label = ttk.Label(self.preview_frame, 
                                       text="Seleccione un archivo para previsualizar",
                                       font=('Arial', 10))
        self.preview_label.pack()
        
        self.preview_frame.bind("<Configure>", 
                                lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
        
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(nav_frame, text="◀ Anterior", 
                  command=self.pagina_anterior,
                  width=10).pack(side=tk.LEFT, padx=5)
        
        self.page_label = ttk.Label(nav_frame, text="Página 0/0", width=15)
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(nav_frame, text="Siguiente ▶", 
                  command=self.pagina_siguiente,
                  width=10).pack(side=tk.LEFT, padx=5)
    
    def crear_datos_oficio_con_scroll(self, parent):
        """Crea los campos para los datos del oficio con scroll"""
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.crear_campos_datos(scrollable_frame)
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def crear_campos_datos(self, parent):
        """Crea todos los campos de datos del oficio - SOLO DESTINATARIO"""
        ttk.Label(parent, text="Asignar a:*", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(5,0))
        self.usuario_combo = ttk.Combobox(parent, width=30, state='readonly')
        self.usuario_combo.pack(fill=tk.X, pady=5)
        self.cargar_usuarios()
        
        # ✅ SOLO DESTINATARIO (a quién debe responder el usuario)
        ttk.Label(parent, text="Destinatario:*", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(5,0))
        self.destinatario = ttk.Entry(parent, width=30)
        self.destinatario.pack(fill=tk.X, pady=5)
        self.destinatario.insert(0, "Por definir")
        
        ttk.Label(parent, text="Asunto:*", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(5,0))
        self.asunto = tk.Text(parent, height=5, width=30, font=('Arial', 9))
        self.asunto.pack(fill=tk.X, pady=5)
        
        ttk.Label(parent, text="Tipo:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(5,0))
        self.tipo = ttk.Combobox(parent, values=['Oficio', 'Memorandum', 'Circular', 'Acuerdo'],
                                width=28, state='readonly')
        self.tipo.pack(fill=tk.X, pady=5)
        self.tipo.set('Oficio')
        
        ttk.Label(parent, text="Prioridad:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(5,0))
        self.prioridad = ttk.Combobox(parent, values=['Alta', 'Normal', 'Baja'],
                                    width=28, state='readonly')
        self.prioridad.pack(fill=tk.X, pady=5)
        self.prioridad.set('Normal')
        
        ttk.Label(parent, text="Fecha:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(5,0))
        self.fecha = ttk.Entry(parent, width=30)
        self.fecha.pack(fill=tk.X, pady=5)
        self.fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
    
    def crear_botones(self, parent):
        """Crea los botones de acción en la parte inferior"""
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=5)
        
        button_row = ttk.Frame(parent)
        button_row.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_row, text="Seleccionar todos", 
                  command=self.seleccionar_todos,
                  width=15).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_row, text="Asignar seleccionados", 
                  command=self.asignar_seleccionados,
                  width=20).pack(side=tk.LEFT, padx=20)
        
        ttk.Button(button_row, text="Asignar todos", 
                  command=self.asignar_todos,
                  width=15).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_row, text="Cancelar", 
                  command=self.destroy,
                  width=15).pack(side=tk.RIGHT, padx=2)
    
    # ==================== FUNCIONALIDAD ====================
    
    def cargar_usuarios(self):
        """Carga los usuarios en el combobox"""
        usuarios = self.db.get_usuarios_no_admin()
        valores = [f"{u['id']} - {u['nombre_completo']}" for u in usuarios]
        self.usuario_combo['values'] = valores
        if valores:
            self.usuario_combo.current(0)
    
    def cargar_lista_archivos(self):
        """Carga la lista de archivos con checkboxes"""
        for i, archivo in enumerate(self.archivos):
            var = tk.BooleanVar(value=(i == 0))
            self.check_vars[archivo] = var
            
            file_frame = ttk.Frame(self.checkbox_frame)
            file_frame.pack(fill=tk.X, pady=1)
            
            cb = ttk.Checkbutton(file_frame, text=archivo, variable=var)
            cb.pack(side=tk.LEFT, anchor=tk.W)
            
            cb.archivo = archivo
            cb.bind('<Button-1>', self.on_checkbutton_click)
            
            if i == 0:
                self.cargar_previsualizacion_async(archivo)
    
    def on_checkbutton_click(self, event):
        """Maneja el clic en un checkbox - carga previsualización"""
        cb = event.widget
        if hasattr(cb, 'archivo'):
            self.cargar_previsualizacion_async(cb.archivo)
    
    def cargar_previsualizacion_async(self, archivo):
        """Carga la previsualización en un hilo separado"""
        if self.preview_loading or self.current_preview_archivo == archivo:
            return
        
        self.current_preview_archivo = archivo
        self.preview_loading = True
        
        self.preview_label.config(text="Cargando previsualización...")
        self.update_idletasks()
        
        thread = threading.Thread(target=self._cargar_previsualizacion, args=(archivo,))
        thread.daemon = True
        thread.start()
    
    def _cargar_previsualizacion(self, archivo):
        """Carga la previsualización (ejecutar en hilo)"""
        try:
            ruta = os.path.join(self.carpeta_origen, archivo)
            images = []
            max_pages = 0
            
            if archivo.lower().endswith('.pdf'):
                doc = fitz.open(ruta)
                max_pages = len(doc)
                for page_num in range(min(max_pages, 5)):
                    page = doc.load_page(page_num)
                    mat = fitz.Matrix(1.2, 1.2)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail((600, 700))
                    images.append(ImageTk.PhotoImage(img))
                doc.close()
            
            self.after(0, self._mostrar_previsualizacion, images, max_pages, archivo)
            
        except Exception as e:
            self.after(0, self._mostrar_error_previsualizacion, str(e), archivo)
    
    def _mostrar_previsualizacion(self, images, max_pages, archivo):
        """Muestra la previsualización en la UI"""
        self.preview_images = images
        self.max_pages = max_pages
        self.current_page = 0
        self.preview_loading = False
        
        if images:
            self.mostrar_pagina(0)
        else:
            self.preview_label.config(text=f"No se puede previsualizar {archivo}")
            self.page_label.config(text="")
    
    def _mostrar_error_previsualizacion(self, error, archivo):
        """Muestra error de previsualización"""
        self.preview_loading = False
        self.preview_label.config(text=f"Error al previsualizar {archivo}: {error}")
        self.page_label.config(text="")
    
    def mostrar_pagina(self, pagina):
        """Muestra una página específica del PDF"""
        if 0 <= pagina < len(self.preview_images):
            self.current_page = pagina
            self.preview_label.config(image=self.preview_images[pagina])
            self.page_label.config(text=f"Página {pagina + 1}/{self.max_pages}")
    
    def pagina_anterior(self):
        """Navega a la página anterior"""
        if self.current_page > 0:
            self.mostrar_pagina(self.current_page - 1)
    
    def pagina_siguiente(self):
        """Navega a la página siguiente"""
        if self.current_page < len(self.preview_images) - 1:
            self.mostrar_pagina(self.current_page + 1)
    
    def seleccionar_todos(self):
        """Selecciona todos los archivos"""
        for var in self.check_vars.values():
            var.set(True)
    
    def asignar_seleccionados(self):
        """Asigna los archivos seleccionados - SOLO DESTINATARIO"""
        seleccionados = [archivo for archivo, var in self.check_vars.items() if var.get()]
        
        if not seleccionados:
            messagebox.showerror("Error", "Seleccione al menos un archivo")
            return
        
        # Validar solo asunto y destinatario
        if not self.asunto.get('1.0', tk.END).strip():
            messagebox.showerror("Error", "Complete el asunto")
            return
        
        if not self.destinatario.get().strip():
            messagebox.showerror("Error", "Complete el destinatario (a quién debe responder)")
            return
        
        if not self.usuario_combo.get():
            messagebox.showerror("Error", "Seleccione un usuario para asignar")
            return
        
        usuario_id = int(self.usuario_combo.get().split(' - ')[0])
        self.db.cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
        usuario_destino = self.db.cursor.fetchone()
        
        if not usuario_destino or not usuario_destino.get('email'):
            messagebox.showerror("Error", "El usuario no tiene email configurado")
            return
        
        # Remitente fijo
        remitente_fijo = "Administración - Recepción de Oficios"
        
        # Verificar todos los duplicados
        duplicados = []
        for archivo in seleccionados:
            nombre_sin_ext = os.path.splitext(archivo)[0]
            self.db.cursor.execute("SELECT id FROM oficios WHERE numero_oficio = %s", (nombre_sin_ext,))
            if self.db.cursor.fetchone():
                duplicados.append(nombre_sin_ext)
        
        # Si hay duplicados, preguntar qué hacer
        sobrescribir_todos = False
        omitir_todos = False
        decisiones_individuales = {}
        
        if duplicados:
            if len(duplicados) == 1:
                respuesta = messagebox.askyesnocancel(
                    "Oficio duplicado",
                    f"El oficio '{duplicados[0]}' ya existe en la base de datos.\n\n"
                    f"• Sí: Sobrescribir este oficio\n"
                    f"• No: Omitir este oficio\n"
                    f"• Cancelar: Detener la operación"
                )
                if respuesta is None:
                    return
                decisiones_individuales[duplicados[0]] = respuesta
            else:
                lista_duplicados = "\n".join([f"• {d}" for d in duplicados])
                respuesta = messagebox.askyesnocancel(
                    "Múltiples oficios duplicados",
                    f"Los siguientes oficios ya existen:\n\n{lista_duplicados}\n\n"
                    f"• Sí: Sobrescribir TODOS\n"
                    f"• No: Omitir TODOS\n"
                    f"• Cancelar: Detener la operación"
                )
                if respuesta is None:
                    return
                sobrescribir_todos = respuesta
                omitir_todos = not respuesta
        
        # Procesar los archivos
        oficios_asignados = []
        archivos_adjuntos = []
        errores = []
        omitidos = []
        
        import tempfile
        from pathlib import Path
        
        for archivo in seleccionados:
            try:
                nombre_sin_ext = os.path.splitext(archivo)[0]
                ruta_completa = os.path.join(self.carpeta_origen, archivo)
                
                # Verificar duplicados
                es_duplicado = nombre_sin_ext in duplicados
                procesar = True
                
                if es_duplicado:
                    if omitir_todos:
                        omitidos.append(nombre_sin_ext)
                        procesar = False
                    elif not sobrescribir_todos:
                        if len(duplicados) == 1:
                            if not decisiones_individuales.get(nombre_sin_ext, False):
                                omitidos.append(nombre_sin_ext)
                                procesar = False
                        else:
                            respuesta = messagebox.askyesno(
                                "Oficio duplicado",
                                f"El oficio '{nombre_sin_ext}' ya existe.\n¿Sobrescribir?"
                            )
                            if not respuesta:
                                omitidos.append(nombre_sin_ext)
                                procesar = False
                
                if not procesar:
                    continue
                
                # Sobrescribir si es necesario
                if es_duplicado:
                    self.db.cursor.execute("DELETE FROM archivos_binarios WHERE oficio_id IN (SELECT id FROM oficios WHERE numero_oficio = %s)", (nombre_sin_ext,))
                    self.db.cursor.execute("DELETE FROM oficios WHERE numero_oficio = %s", (nombre_sin_ext,))
                    logger.info(f"Oficio {nombre_sin_ext} sobrescrito")
                
                with open(ruta_completa, 'rb') as f:
                    contenido = f.read()
                
                # Insertar oficio
                datos = {
                    'numero_oficio': nombre_sin_ext,
                    'fecha_oficio': self.fecha.get(),
                    'remitente': remitente_fijo,
                    'destinatario': self.destinatario.get().strip(),
                    'asunto': self.asunto.get('1.0', tk.END).strip(),
                    'tipo_oficio': self.tipo.get(),
                    'prioridad': self.prioridad.get(),
                    'estado': 'En Proceso'
                }
                
                oficio_id = self.db.insert_oficio(datos, self.usuario_actual['id'])
                self.db.asignar_oficio(oficio_id, usuario_id)
                
                # Guardar en BD
                import mimetypes
                import hashlib
                import psycopg2
                
                mime_type = mimetypes.guess_type(archivo)[0] or 'application/octet-stream'
                hash_md5 = hashlib.md5(contenido).hexdigest()
                
                self.db.cursor.execute("""
                    INSERT INTO archivos_binarios 
                    (oficio_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id, hash_md5)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (oficio_id, 'oficio', archivo, psycopg2.Binary(contenido), mime_type, 
                    len(contenido), self.usuario_actual['id'], hash_md5))
                
                # Acumular datos
                oficios_asignados.append({
                    'id': oficio_id,
                    'numero': nombre_sin_ext,
                    'asunto': self.asunto.get('1.0', tk.END).strip()
                })
                
                # Crear archivo temporal
                temp_dir = Path(tempfile.gettempdir()) / "gestion_oficios_adjuntos"
                temp_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]
                archivo_temp = temp_dir / f"{nombre_sin_ext}_{timestamp}.pdf"
                
                with open(archivo_temp, 'wb') as f:
                    f.write(contenido)
                
                archivos_adjuntos.append(str(archivo_temp))
                os.remove(ruta_completa)
                
            except Exception as e:
                errores.append(f"{archivo}: {str(e)}")
                logger.error(f"Error procesando {archivo}: {e}")
        
        # ENVIAR CORREO CON TODOS LOS ADJUNTOS
        if oficios_asignados and usuario_destino and usuario_destino.get('email'):
            from ..notificaciones import Notificador
            from ..config import Config
            
            notificador = Notificador(Config)
            
            lista_oficios = "\n".join([f"• {o['numero']} - {o['asunto']}" for o in oficios_asignados])
            
            nota_duplicados = ""
            if duplicados and (sobrescribir_todos or any(decisiones_individuales.values())):
                nota_duplicados = f"\n\nNOTA: Se sobrescribieron oficios que ya existían."
            
            # ✅ CORRECCIÓN: Usar condición correcta para el artículo
            articulo = "n" if len(oficios_asignados) > 1 else ""
            
            mensaje = f"""
    Hola {usuario_destino['nombre_completo']},

    Se le ha{articulo} asignado {len(oficios_asignados)} nuevo(s) oficio(s):

    {lista_oficios}

    {'📨' if len(oficios_asignados) == 1 else '📨📨'} El oficio debe ser respondido a:
    {self.destinatario.get().strip()}

    📅 Fecha de recepción: {self.fecha.get()}{nota_duplicados}

    📎 Se adjuntan {len(archivos_adjuntos)} archivo(s).

    Saludos cordiales,
    Administración del Sistema
    """
            
            exito = notificador.enviar(
                usuario_destino['email'],
                f"Asignación de {len(oficios_asignados)} oficios",
                mensaje,
                archivos_adjuntos
            )
            
            if exito:
                logger.info(f"Correo enviado con {len(archivos_adjuntos)} adjuntos")
            else:
                logger.error("Error al enviar correo")
        
        # Mostrar resultado
        mensaje_resultado = f"✅ Asignados: {len(oficios_asignados)}"
        if omitidos:
            mensaje_resultado += f"\n⏭️ Omitidos: {len(omitidos)}"
        if errores:
            mensaje_resultado += f"\n❌ Errores: {len(errores)}"
        
        if oficios_asignados:
            messagebox.showinfo("Resultado de asignación", mensaje_resultado)
        elif errores:
            messagebox.showerror("Error en asignación", mensaje_resultado)
        
        if self.callback:
            self.callback()
        
        self.destroy()
        

    def asignar_todos(self):
        """Selecciona todos los archivos y asigna en UN SOLO CORREO con múltiples adjuntos"""
        # Seleccionar todos los archivos
        for var in self.check_vars.values():
            var.set(True)
        
        # Obtener la lista completa de archivos
        todos_archivos = list(self.check_vars.keys())
        
        if not todos_archivos:
            messagebox.showerror("Error", "No hay archivos para asignar")
            return
        
        # Validar solo asunto y destinatario
        if not self.asunto.get('1.0', tk.END).strip():
            messagebox.showerror("Error", "Complete el asunto")
            return
        
        if not self.destinatario.get().strip():
            messagebox.showerror("Error", "Complete el destinatario (a quién debe responder)")
            return
        
        if not self.usuario_combo.get():
            messagebox.showerror("Error", "Seleccione un usuario para asignar")
            return
        
        usuario_id = int(self.usuario_combo.get().split(' - ')[0])
        
        self.db.cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
        usuario_destino = self.db.cursor.fetchone()
        
        if not usuario_destino or not usuario_destino.get('email'):
            messagebox.showerror("Error", "El usuario no tiene email configurado")
            return
        
        # Remitente fijo
        remitente_fijo = "Administración - Recepción de Oficios"
        
        # Verificar duplicados primero
        duplicados = []
        for archivo in todos_archivos:
            nombre_sin_ext = os.path.splitext(archivo)[0]
            self.db.cursor.execute("SELECT id FROM oficios WHERE numero_oficio = %s", (nombre_sin_ext,))
            if self.db.cursor.fetchone():
                duplicados.append(nombre_sin_ext)
        
        # Manejar duplicados
        sobrescribir_todos = False
        if duplicados:
            if len(duplicados) == 1:
                respuesta = messagebox.askyesno(
                    "Oficio duplicado",
                    f"El oficio '{duplicados[0]}' ya existe.\n¿Desea sobrescribirlo?"
                )
                if not respuesta:
                    messagebox.showinfo("Operación cancelada", "No se realizó ninguna asignación")
                    return
            else:
                lista = "\n".join([f"• {d}" for d in duplicados])
                respuesta = messagebox.askyesno(
                    "Múltiples oficios duplicados",
                    f"Los siguientes oficios ya existen:\n\n{lista}\n\n"
                    f"¿Desea sobrescribirlos TODOS?"
                )
                if not respuesta:
                    messagebox.showinfo("Operación cancelada", "No se realizó ninguna asignación")
                    return
            sobrescribir_todos = True
        
        # Variables para acumular
        oficios_asignados = []
        archivos_adjuntos = []
        errores = []
        
        import tempfile
        from pathlib import Path
        
        for archivo in todos_archivos:
            try:
                nombre_sin_ext = os.path.splitext(archivo)[0]
                ruta_completa = os.path.join(self.carpeta_origen, archivo)
                
                # Si hay duplicados y se eligió sobrescribir, eliminar el existente
                if sobrescribir_todos and nombre_sin_ext in duplicados:
                    self.db.cursor.execute(
                        "DELETE FROM archivos_binarios WHERE oficio_id IN (SELECT id FROM oficios WHERE numero_oficio = %s)", 
                        (nombre_sin_ext,)
                    )
                    self.db.cursor.execute(
                        "DELETE FROM oficios WHERE numero_oficio = %s", 
                        (nombre_sin_ext,)
                    )
                    logger.info(f"Oficio {nombre_sin_ext} sobrescrito")
                
                with open(ruta_completa, 'rb') as f:
                    contenido = f.read()
                
                # Insertar oficio
                datos = {
                    'numero_oficio': nombre_sin_ext,
                    'fecha_oficio': self.fecha.get(),
                    'remitente': remitente_fijo,
                    'destinatario': self.destinatario.get().strip(),
                    'asunto': self.asunto.get('1.0', tk.END).strip(),
                    'tipo_oficio': self.tipo.get(),
                    'prioridad': self.prioridad.get(),
                    'estado': 'En Proceso'
                }
                
                oficio_id = self.db.insert_oficio(datos, self.usuario_actual['id'])
                self.db.asignar_oficio(oficio_id, usuario_id)
                
                # Guardar en BD
                import mimetypes
                import hashlib
                import psycopg2
                
                mime_type = mimetypes.guess_type(archivo)[0] or 'application/octet-stream'
                hash_md5 = hashlib.md5(contenido).hexdigest()
                
                self.db.cursor.execute("""
                    INSERT INTO archivos_binarios 
                    (oficio_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id, hash_md5)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (oficio_id, 'oficio', archivo, psycopg2.Binary(contenido), mime_type, 
                    len(contenido), self.usuario_actual['id'], hash_md5))
                
                # Acumular para el correo
                oficios_asignados.append({
                    'id': oficio_id,
                    'numero': nombre_sin_ext,
                    'asunto': self.asunto.get('1.0', tk.END).strip()
                })
                
                # Crear archivo temporal para adjuntar
                temp_dir = Path(tempfile.gettempdir()) / "gestion_oficios_adjuntos"
                temp_dir.mkdir(exist_ok=True)
                
                archivo_temp = temp_dir / f"{nombre_sin_ext}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                
                with open(archivo_temp, 'wb') as f:
                    f.write(contenido)
                
                archivos_adjuntos.append(str(archivo_temp))
                os.remove(ruta_completa)
                
            except Exception as e:
                errores.append(f"{archivo}: {str(e)}")
                logger.error(f"Error procesando {archivo}: {e}")
        
        # ENVIAR UN SOLO CORREO CON TODOS LOS ADJUNTOS
        if oficios_asignados:
            from ..notificaciones import Notificador
            from ..config import Config
            
            notificador = Notificador(Config)
            
            lista_oficios = "\n".join([f"• {o['numero']} - {o['asunto']}" for o in oficios_asignados])
            
            nota_duplicados = ""
            if sobrescribir_todos and duplicados:
                nota_duplicados = f"\n\nNOTA: Se sobrescribieron {len(duplicados)} oficios que ya existían."
            
            # ✅ CORRECCIÓN: Usar condición correcta para el artículo
            articulo = "n" if len(oficios_asignados) > 1 else ""
            
            mensaje = f"""
    Hola {usuario_destino['nombre_completo']},

    Se le ha{articulo} asignado {len(oficios_asignados)} nuevo(s) oficio(s):

    {lista_oficios}

    {'📨' if len(oficios_asignados) == 1 else '📨📨'} El oficio debe ser respondido a:
    {self.destinatario.get().strip()}

    📅 Fecha de recepción: {self.fecha.get()}{nota_duplicados}

    📎 Se adjuntan {len(archivos_adjuntos)} archivo(s).

    Saludos cordiales,
    Administración del Sistema
    """
            
            exito = notificador.enviar(
                usuario_destino['email'],
                f"Asignación masiva de {len(oficios_asignados)} oficios",
                mensaje,
                archivos_adjuntos
            )
            
            if exito:
                logger.info(f"Correo único enviado con {len(archivos_adjuntos)} adjuntos a {usuario_destino['email']}")
            else:
                logger.error("Error al enviar correo con múltiples adjuntos")
        
        # Mostrar resultado
        mensaje_resultado = f"✅ Asignados correctamente: {len(oficios_asignados)}"
        if errores:
            mensaje_resultado += f"\n❌ Errores: {len(errores)}\n" + "\n".join(errores[:3])
            if len(errores) > 3:
                mensaje_resultado += f"\n... y {len(errores) - 3} errores más"
        
        if oficios_asignados:
            messagebox.showinfo("Resultado de asignación masiva", mensaje_resultado)
        elif errores:
            messagebox.showerror("Error en asignación", mensaje_resultado)
        
        if self.callback:
            self.callback()
        
        self.destroy()
    # ==================== CONFIGURACIÓN ===================
    
    def guardar_configuracion_completa(self):
        """Guarda configuración completa incluyendo sashes"""
        try:
            sash1_pos = self.paned.sashpos(0)
            sash2_pos = self.paned.sashpos(1)
            
            if sash1_pos >= 0 and sash2_pos >= 0:
                config = {
                    'width': self.winfo_width(),
                    'height': self.winfo_height(),
                    'x': self.winfo_x(),
                    'y': self.winfo_y(),
                    'sash1': sash1_pos,
                    'sash2': sash2_pos
                }
                
                config_dir = Path.home() / ".gestion_oficios"
                config_dir.mkdir(exist_ok=True)
                
                with open(config_dir / "asignar_completo.conf", 'w') as f:
                    json.dump(config, f, indent=2)
                    
                logger.info(f"Configuración guardada: {config}")
            else:
                logger.warning("No se pudieron obtener posiciones de sashes")
                
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def cargar_configuracion_ventana(self):
        """Carga la configuración guardada"""
        try:
            config_file = Path.home() / ".gestion_oficios" / "asignar_completo.conf"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                if all(k in config for k in ['width', 'height', 'x', 'y']):
                    self.geometry(f"{config['width']}x{config['height']}+{config['x']}+{config['y']}")
                
                if 'sash1' in config and 'sash2' in config:
                    self.sashes_guardadas = (config['sash1'], config['sash2'])
                    
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
    
    def aplicar_sashes_guardadas(self):
        """Aplica las posiciones de sashes guardadas"""
        try:
            if self.sashes_guardadas and hasattr(self, 'paned'):
                sash1, sash2 = self.sashes_guardadas
                # Asegurar que los valores sean válidos
                ancho_total = self.paned.winfo_width()
                if ancho_total > 0 and sash1 < ancho_total and sash2 < ancho_total:
                    self.paned.sashpos(0, sash1)
                    self.paned.sashpos(1, sash2)
                    logger.info(f"Sashes aplicadas: {sash1}, {sash2}")
                    
        except Exception as e:
            logger.error(f"Error aplicando sashes: {e}")
    
    def al_cerrar(self):
        """Función llamada al cerrar la ventana"""
        self.guardar_configuracion_completa()
        self.destroy()