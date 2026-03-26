# dialogs/carga_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
from datetime import datetime
import psycopg2
import hashlib
import mimetypes

class DialogoCargaArchivos(tk.Toplevel):
    def __init__(self, parent, archivos, carpeta_origen, carpeta_destino, db, usuario_actual, callback=None):
        """
        callback: función a llamar después de cargar (para actualizar listas)
        """
        super().__init__(parent)
        self.parent = parent
        self.archivos = archivos
        self.carpeta_origen = carpeta_origen
        self.carpeta_destino = carpeta_destino
        self.db = db
        self.usuario_actual = usuario_actual
        self.callback = callback  # Guardamos el callback
        
        self.title("Cargar Archivos a BD")
        self.geometry("650x600")
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="CARGAR ARCHIVOS A BD", 
                 font=('Arial', 14, 'bold')).pack(pady=5)
        
        # Instrucciones
        ttk.Label(main_frame, 
                 text="Seleccione los archivos a cargar y complete los datos:",
                 font=('Arial', 10)).pack(pady=5)
        
        # Panel dividido
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Panel izquierdo - Lista de archivos
        left_frame = ttk.LabelFrame(paned, text="Archivos disponibles", padding="10")
        paned.add(left_frame, weight=1)
        
        # Lista con checkboxes
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.check_vars = {}
        for archivo in self.archivos:
            var = tk.BooleanVar(value=True)
            self.check_vars[archivo] = var
            cb = ttk.Checkbutton(scrollable_frame, text=archivo, variable=var)
            cb.pack(anchor=tk.W, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones de selección rápida
        sel_frame = ttk.Frame(left_frame)
        sel_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(sel_frame, text="Seleccionar todos", 
                  command=self.seleccionar_todos).pack(side=tk.LEFT, padx=2)
        ttk.Button(sel_frame, text="Deseleccionar todos", 
                  command=self.deseleccionar_todos).pack(side=tk.LEFT, padx=2)
        
        # Panel derecho - Datos del oficio
        right_frame = ttk.LabelFrame(paned, text="Datos del oficio", padding="10")
        paned.add(right_frame, weight=1)
        
        # Campos
        ttk.Label(right_frame, text="Remitente:*").pack(anchor=tk.W, pady=(5,0))
        self.remitente = ttk.Entry(right_frame, width=35)
        self.remitente.pack(fill=tk.X, pady=5)
        self.remitente.insert(0, "Por definir")
        
        ttk.Label(right_frame, text="Destinatario:").pack(anchor=tk.W, pady=(5,0))
        self.destinatario = ttk.Entry(right_frame, width=35)
        self.destinatario.pack(fill=tk.X, pady=5)
        self.destinatario.insert(0, "Por definir")
        
        ttk.Label(right_frame, text="Asunto:*").pack(anchor=tk.W, pady=(5,0))
        self.asunto = ttk.Entry(right_frame, width=35)
        self.asunto.pack(fill=tk.X, pady=5)
        
        ttk.Label(right_frame, text="Tipo:").pack(anchor=tk.W, pady=(5,0))
        self.tipo = ttk.Combobox(right_frame, 
                                 values=['Oficio', 'Memorandum', 'Circular', 'Acuerdo'],
                                 width=33, state='readonly')
        self.tipo.pack(fill=tk.X, pady=5)
        self.tipo.set('Oficio')
        
        ttk.Label(right_frame, text="Prioridad:").pack(anchor=tk.W, pady=(5,0))
        self.prioridad = ttk.Combobox(right_frame, 
                                      values=['Alta', 'Normal', 'Baja'],
                                      width=33, state='readonly')
        self.prioridad.pack(fill=tk.X, pady=5)
        self.prioridad.set('Normal')
        
        ttk.Label(right_frame, text="Fecha:").pack(anchor=tk.W, pady=(5,0))
        self.fecha = ttk.Entry(right_frame, width=35)
        self.fecha.pack(fill=tk.X, pady=5)
        self.fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Opciones
        opciones_frame = ttk.LabelFrame(main_frame, text="Opciones", padding="10")
        opciones_frame.pack(fill=tk.X, pady=10)
        
        self.mover_archivos = tk.BooleanVar(value=True)
        ttk.Checkbutton(opciones_frame, text="Mover archivos a carpeta de asignados", 
                       variable=self.mover_archivos).pack(anchor=tk.W)
        
        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Cargar seleccionados", 
                  command=self.cargar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def seleccionar_todos(self):
        """Selecciona todos los archivos"""
        for var in self.check_vars.values():
            var.set(True)
    
    def deseleccionar_todos(self):
        """Deselecciona todos los archivos"""
        for var in self.check_vars.values():
            var.set(False)
    
    def cargar(self):
        """Carga los archivos seleccionados"""
        seleccionados = [archivo for archivo, var in self.check_vars.items() if var.get()]
        
        if not seleccionados:
            messagebox.showerror("Error", "Seleccione al menos un archivo")
            return
        
        if not self.remitente.get().strip() or not self.asunto.get().strip():
            messagebox.showerror("Error", "Complete remitente y asunto")
            return
        
        count = 0
        errores = []
        
        for archivo in seleccionados:
            try:
                # Extraer número del nombre del archivo
                nombre_sin_ext = os.path.splitext(archivo)[0]
                ruta_completa = os.path.join(self.carpeta_origen, archivo)
                
                # Leer archivo
                with open(ruta_completa, 'rb') as f:
                    contenido = f.read()
                
                # Insertar oficio
                datos = {
                    'numero_oficio': nombre_sin_ext,
                    'fecha_oficio': self.fecha.get(),
                    'remitente': self.remitente.get().strip(),
                    'destinatario': self.destinatario.get().strip(),
                    'asunto': self.asunto.get().strip(),
                    'tipo_oficio': self.tipo.get(),
                    'prioridad': self.prioridad.get(),
                    'ruta_archivo': ruta_completa,
                    'estado': 'En Proceso'
                }
                
                oficio_id = self.db.insert_oficio(datos, self.usuario_actual['id'])
                
                # Guardar archivo en BD
                mime_type = mimetypes.guess_type(archivo)[0] or 'application/octet-stream'
                hash_md5 = hashlib.md5(contenido).hexdigest()
                
                self.db.cursor.execute("""
                    INSERT INTO archivos_binarios 
                    (oficio_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id, hash_md5)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    oficio_id, 'oficio', archivo, 
                    psycopg2.Binary(contenido), mime_type, 
                    len(contenido), self.usuario_actual['id'], hash_md5
                ))
                
                # Mover archivo si se solicita
                if self.mover_archivos.get():
                    shutil.move(ruta_completa, 
                              os.path.join(self.carpeta_destino, archivo))
                
                count += 1
                
            except Exception as e:
                errores.append(f"{archivo}: {str(e)}")
        
        # Mostrar resultado
        if errores:
            messagebox.showwarning("Carga parcial", 
                                 f"Se cargaron {count} archivos.\nErrores:\n" + "\n".join(errores))
        else:
            messagebox.showinfo("Éxito", f"{count} archivos cargados correctamente")
        
        # ✅ CORREGIDO: Llamar al callback si existe
        if self.callback:
            self.callback()
        
        self.destroy()