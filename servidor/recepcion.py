# recepcion.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
from pathlib import Path

from .dialogs.asignar_dialog import DialogoAsignarOficios

class RecepcionTab:
    def __init__(self, notebook, db, usuario_actual, config, archivos_gestion):
        self.db = db
        self.usuario_actual = usuario_actual
        self.config = config
        self.archivos_gestion = archivos_gestion
        self.notebook = notebook
        
        self.crear_pestana(notebook)
    
    def crear_pestana(self, notebook):
        """Crea la pestaña de recepción"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📥 Recepción")
        
        self.parent = frame
        
        # Toolbar - solo un botón
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(toolbar, text="📂 Asignar Oficios", 
                  command=self.asignar_oficios,
                  width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar, text="🔄 Actualizar", 
                  command=self.actualizar_lista,
                  width=15).pack(side=tk.RIGHT, padx=5)
        
        # Panel de carpeta No Asignados
        carpetas_frame = ttk.LabelFrame(frame, text="ARCHIVOS PENDIENTES DE ASIGNAR", padding="10")
        carpetas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Solo No Asignados
        self.lista_no_asignados = tk.Listbox(carpetas_frame)
        self.lista_no_asignados.pack(fill=tk.BOTH, expand=True)
        self.lista_no_asignados.bind('<Double-Button-1>', 
                                    lambda e: self.abrir_archivo(self.lista_no_asignados))
    
    def actualizar_lista(self):
        """Actualiza la lista de archivos en No Asignados"""
        self.lista_no_asignados.delete(0, tk.END)
        if os.path.exists(self.config.CARPETA_NO_ASIGNADOS):
            for archivo in sorted(os.listdir(self.config.CARPETA_NO_ASIGNADOS)):
                if archivo.endswith(('.xlsx', '.xls', '.pdf', '.docx')):
                    self.lista_no_asignados.insert(tk.END, archivo)
    
    def abrir_archivo(self, listbox):
        """Abre archivo seleccionado"""
        sel = listbox.curselection()
        if not sel:
            return
        
        archivo = listbox.get(sel[0])
        ruta = os.path.join(self.config.CARPETA_NO_ASIGNADOS, archivo)
        
        if os.path.exists(ruta):
            os.startfile(ruta)
    
    def asignar_oficios(self):
        """Abre el diálogo unificado de asignación"""
        if not os.path.exists(self.config.CARPETA_NO_ASIGNADOS):
            messagebox.showerror("Error", "No existe la carpeta No Asignados")
            return
        
        archivos = [f for f in os.listdir(self.config.CARPETA_NO_ASIGNADOS) 
                   if f.endswith(('.xlsx', '.xls', '.pdf', '.docx'))]
        
        if not archivos:
            messagebox.showinfo("Info", "No hay archivos en No Asignados")
            return
        
        from .dialogs.asignar_dialog import DialogoAsignarOficios
        dialog = DialogoAsignarOficios(
            self.parent, 
            archivos, 
            self.config.CARPETA_NO_ASIGNADOS,
            self.db, 
            self.usuario_actual, 
            self.archivos_gestion,
            callback=self.actualizar_lista
        )