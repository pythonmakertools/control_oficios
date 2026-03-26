# dialogs/acuse_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime

class DialogoRegistrarAcuse(tk.Toplevel):
    def __init__(self, parent, db, archivos_gestion, oficio_id, usuario_actual):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.archivos_gestion = archivos_gestion
        self.oficio_id = oficio_id
        self.usuario_actual = usuario_actual
        
        self.title("Registrar Acuse")
        self.geometry("500x450")
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (450 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.oficio = self.db.get_oficio_by_id(oficio_id)
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="REGISTRAR ACUSE", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Datos del oficio
        info_frame = ttk.LabelFrame(main_frame, text="Oficio", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"Número: {self.oficio['numero_oficio']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Asunto: {self.oficio['asunto']}").pack(anchor=tk.W, pady=5)
        
        # Campos del acuse
        campos_frame = ttk.LabelFrame(main_frame, text="Datos del Acuse", padding="10")
        campos_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(campos_frame, text="Número de acuse:*").pack(anchor=tk.W)
        self.num_acuse = ttk.Entry(campos_frame, width=40)
        self.num_acuse.pack(fill=tk.X, pady=5)
        self.num_acuse.focus()
        
        ttk.Label(campos_frame, text="Fecha de acuse:").pack(anchor=tk.W, pady=(10,0))
        self.fecha_acuse = ttk.Entry(campos_frame, width=20)
        self.fecha_acuse.pack(fill=tk.X, pady=5)
        self.fecha_acuse.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        ttk.Label(campos_frame, text="Archivo de acuse:").pack(anchor=tk.W, pady=(10,0))
        
        archivo_frame = ttk.Frame(campos_frame)
        archivo_frame.pack(fill=tk.X, pady=5)
        
        self.archivo_var = tk.StringVar()
        ttk.Entry(archivo_frame, textvariable=self.archivo_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(archivo_frame, text="Examinar", 
                  command=self.seleccionar_archivo).pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(campos_frame, text="Observaciones:").pack(anchor=tk.W, pady=(10,0))
        self.observaciones = tk.Text(campos_frame, height=3, width=40)
        self.observaciones.pack(fill=tk.X, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Registrar", command=self.registrar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def seleccionar_archivo(self):
        """Selecciona archivo de acuse"""
        filename = self.archivos_gestion.seleccionar_archivo()
        if filename:
            self.archivo_var.set(filename)
    
    def registrar(self):
        """Registra el acuse"""
        if not self.num_acuse.get().strip():
            messagebox.showerror("Error", "El número de acuse es obligatorio")
            return
        
        # Preparar notas
        notas = f"[ACUSE] Folio: {self.num_acuse.get().strip()} - Fecha: {self.fecha_acuse.get()}"
        if self.observaciones.get('1.0', tk.END).strip():
            notas += f" - {self.observaciones.get('1.0', tk.END).strip()}"
        
        try:
            # Actualizar oficio
            self.db.update_oficio(self.oficio_id, {
                'acuse_recibido': True,
                'notas': f"{self.oficio.get('notas', '')}\n{notas}" if self.oficio.get('notas') else notas
            })
            
            # Guardar archivo si existe
            if self.archivo_var.get():
                self.archivos_gestion.guardar_en_bd(
                    self.oficio_id, 
                    'acuse', 
                    self.archivo_var.get(), 
                    self.usuario_actual['id']
                )
                
                # También guardar copia física
                from ..config import Config
                nombre = f"ACUSE_{self.oficio_id}_{datetime.now().strftime('%Y%m%d')}_{os.path.basename(self.archivo_var.get())}"
                self.archivos_gestion.guardar_archivo_local(
                    self.archivo_var.get(),
                    Config.CARPETA_ACUSES,
                    nombre
                )
            
            messagebox.showinfo("Éxito", "Acuse registrado correctamente")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar acuse: {e}")