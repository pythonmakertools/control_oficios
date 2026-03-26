# dialogs/oficios_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class DialogoOficio(tk.Toplevel):
    def __init__(self, parent, db, usuario_actual, archivos_gestion, modo='nuevo', oficio_id=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.usuario_actual = usuario_actual
        self.archivos_gestion = archivos_gestion
        self.modo = modo
        self.oficio_id = oficio_id
        self.resultado = None
        
        titulo = "Nuevo Oficio" if modo == 'nuevo' else "Editar Oficio"
        self.title(titulo)
        self.geometry("600x650")
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (650 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.datos = {}
        if modo == 'editar' and oficio_id:
            self.cargar_datos()
        
        self.crear_interfaz()
    
    def cargar_datos(self):
        """Carga datos del oficio para edición"""
        self.datos = self.db.get_oficio_by_id(self.oficio_id)
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = "NUEVO OFICIO" if self.modo == 'nuevo' else f"EDITAR OFICIO: {self.datos.get('numero_oficio', '')}"
        ttk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Campos en un canvas con scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Crear campos
        self.crear_campos(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def crear_campos(self, parent):
        """Crea los campos del formulario"""
        campos = [
            ('Número de Oficio:*', 'numero_oficio'),
            ('Fecha:', 'fecha_oficio'),
            ('Remitente:*', 'remitente'),
            ('Destinatario:', 'destinatario'),
            ('Asunto:*', 'asunto'),
            ('Tipo:', 'tipo_oficio'),
            ('Prioridad:', 'prioridad'),
            ('Estado:', 'estado'),
        ]
        
        self.entries = {}
        
        for i, (label, campo) in enumerate(campos):
            ttk.Label(parent, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            
            if campo == 'tipo_oficio':
                var = tk.StringVar(value=self.datos.get(campo, 'Oficio'))
                combo = ttk.Combobox(parent, textvariable=var, 
                                    values=['Oficio', 'Memorandum', 'Circular', 'Acuerdo'],
                                    width=40, state='readonly')
                combo.grid(row=i, column=1, pady=5, padx=5)
                self.entries[campo] = var
            elif campo == 'prioridad':
                var = tk.StringVar(value=self.datos.get(campo, 'Normal'))
                combo = ttk.Combobox(parent, textvariable=var,
                                    values=['Alta', 'Normal', 'Baja'],
                                    width=40, state='readonly')
                combo.grid(row=i, column=1, pady=5, padx=5)
                self.entries[campo] = var
            elif campo == 'estado':
                var = tk.StringVar(value=self.datos.get(campo, 'En Proceso'))
                combo = ttk.Combobox(parent, textvariable=var,
                                    values=['En Proceso', 'Atendido', 'Archivado'],
                                    width=40, state='readonly')
                combo.grid(row=i, column=1, pady=5, padx=5)
                self.entries[campo] = var
            elif campo == 'fecha_oficio':
                var = tk.StringVar(value=self.datos.get(campo, datetime.now().strftime('%Y-%m-%d')))
                entry = ttk.Entry(parent, textvariable=var, width=40)
                entry.grid(row=i, column=1, pady=5, padx=5)
                self.entries[campo] = var
            else:
                var = tk.StringVar(value=self.datos.get(campo, ''))
                entry = ttk.Entry(parent, textvariable=var, width=40)
                entry.grid(row=i, column=1, pady=5, padx=5)
                self.entries[campo] = var
        
        # Notas
        ttk.Label(parent, text="Notas:").grid(row=len(campos), column=0, sticky=tk.W, pady=5, padx=5)
        self.notas = tk.Text(parent, height=5, width=40)
        self.notas.grid(row=len(campos), column=1, pady=5, padx=5)
        if self.datos.get('notas'):
            self.notas.insert('1.0', self.datos['notas'])
        
        # Archivo (solo para nuevo)
        if self.modo == 'nuevo':
            self.crear_campo_archivo(parent, len(campos) + 1)
    
    def crear_campo_archivo(self, parent, row):
        """Crea campo para seleccionar archivo"""
        ttk.Label(parent, text="Archivo:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.archivo_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.archivo_var, width=30).pack(side=tk.LEFT)
        ttk.Button(frame, text="Examinar", command=self.seleccionar_archivo).pack(side=tk.LEFT, padx=5)
    
    def seleccionar_archivo(self):
        """Selecciona archivo"""
        filename = self.archivos_gestion.seleccionar_archivo()
        if filename:
            self.archivo_var.set(filename)
    
    def guardar(self):
        """Guarda el oficio"""
        # Validar campos obligatorios
        obligatorios = ['numero_oficio', 'remitente', 'asunto']
        for campo in obligatorios:
            if not self.entries[campo].get().strip():
                messagebox.showerror("Error", f"El campo {campo} es obligatorio")
                return
        
        # Recoger datos
        datos = {}
        for campo, var in self.entries.items():
            datos[campo] = var.get().strip()
        
        if self.notas.get('1.0', tk.END).strip():
            datos['notas'] = self.notas.get('1.0', tk.END).strip()
        
        try:
            if self.modo == 'nuevo':
                # Insertar oficio
                oficio_id = self.db.insert_oficio(datos, self.usuario_actual['id'])
                
                # Guardar archivo si hay
                if hasattr(self, 'archivo_var') and self.archivo_var.get():
                    self.archivos_gestion.guardar_en_bd(oficio_id, 'oficio', 
                                                        self.archivo_var.get(), 
                                                        self.usuario_actual['id'])
                
                messagebox.showinfo("Éxito", "Oficio creado correctamente")
            else:
                # Actualizar oficio
                self.db.update_oficio(self.oficio_id, datos)
                messagebox.showinfo("Éxito", "Oficio actualizado correctamente")
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")