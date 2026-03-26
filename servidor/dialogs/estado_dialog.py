# dialogs/estado_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class DialogoCambiarEstado(tk.Toplevel):
    def __init__(self, parent, db, oficio_id, nuevo_estado):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.oficio_id = oficio_id
        self.nuevo_estado = nuevo_estado
        
        self.title(f"Cambiar a {nuevo_estado}")
        self.geometry("450x350")
        self.transient(parent)
        self.grab_set()
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (350 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.oficio = self.db.get_oficio_by_id(oficio_id)
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text=f"MARCAR COMO {self.nuevo_estado.upper()}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Datos del oficio
        info_frame = ttk.LabelFrame(main_frame, text="Oficio", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"Número: {self.oficio['numero_oficio']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Asunto: {self.oficio['asunto']}").pack(anchor=tk.W, pady=5)
        ttk.Label(info_frame, text=f"Estado actual: {self.oficio['estado']}").pack(anchor=tk.W)
        
        # Campos adicionales
        campos_frame = ttk.LabelFrame(main_frame, text="Información adicional", padding="10")
        campos_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(campos_frame, text="Número de respuesta:").pack(anchor=tk.W)
        self.num_respuesta = ttk.Entry(campos_frame, width=40)
        self.num_respuesta.pack(fill=tk.X, pady=5)
        
        ttk.Label(campos_frame, text="Notas / Comentarios:").pack(anchor=tk.W, pady=(10,0))
        self.notas = tk.Text(campos_frame, height=4, width=40)
        self.notas.pack(fill=tk.X, pady=5)
        
        # Fecha (solo para atendido)
        if self.nuevo_estado == 'Atendido':
            ttk.Label(campos_frame, text="Fecha de atención:").pack(anchor=tk.W, pady=(10,0))
            self.fecha_atencion = ttk.Entry(campos_frame, width=20)
            self.fecha_atencion.pack(fill=tk.X, pady=5)
            self.fecha_atencion.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def guardar(self):
        """Guarda el cambio de estado"""
        datos = {'estado': self.nuevo_estado}
        
        if self.nuevo_estado == 'Atendido' and hasattr(self, 'fecha_atencion'):
            datos['fecha_atendido'] = self.fecha_atencion.get()
        
        if self.num_respuesta.get().strip():
            datos['oficio_respuesta'] = self.num_respuesta.get().strip()
        
        if self.notas.get('1.0', tk.END).strip():
            notas_actuales = self.oficio.get('notas', '')
            nueva_nota = f"[{datetime.now().strftime('%d/%m/%Y')}] Cambio a {self.nuevo_estado}: {self.notas.get('1.0', tk.END).strip()}"
            datos['notas'] = f"{notas_actuales}\n{nueva_nota}" if notas_actuales else nueva_nota
        
        try:
            self.db.update_oficio(self.oficio_id, datos)
            messagebox.showinfo("Éxito", f"Oficio marcado como {self.nuevo_estado}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {e}")