# dialogs/detalle_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import tempfile
from pathlib import Path
from datetime import datetime

class DialogoDetalle(tk.Toplevel):
    def __init__(self, parent, db, oficio_id):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.oficio_id = oficio_id
        
        self.title("Detalle de Oficio")
        self.geometry("700x600")
        self.transient(parent)
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f'+{x}+{y}')
        
        self.oficio = self.db.get_oficio_by_id(oficio_id)
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(title_frame, text="DETALLE DE OFICIO", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # Botón cerrar
        ttk.Button(title_frame, text="Cerrar", command=self.destroy).pack(side=tk.RIGHT)
        
        # Área de texto para detalles
        texto_frame = ttk.Frame(main_frame)
        texto_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        texto = tk.Text(texto_frame, wrap=tk.WORD, font=('Courier', 10))
        texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(texto_frame, orient=tk.VERTICAL, command=texto.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        texto.configure(yscrollcommand=scrollbar.set)
        
        # Insertar datos
        self.insertar_datos(texto)
        texto.config(state=tk.DISABLED)
        
        # Botones de acción
        self.crear_botones(main_frame)
    
    def insertar_datos(self, texto):
        """Inserta los datos del oficio"""
        o = self.oficio
        
        texto.insert(tk.END, "="*60 + "\n")
        texto.insert(tk.END, f"OFICIO: {o['numero_oficio']}\n")
        texto.insert(tk.END, "="*60 + "\n\n")
        
        texto.insert(tk.END, "DATOS GENERALES\n")
        texto.insert(tk.END, "-"*40 + "\n")
        texto.insert(tk.END, f"ID:               {o['id']}\n")
        texto.insert(tk.END, f"Fecha:            {o['fecha_oficio']}\n")
        texto.insert(tk.END, f"Remitente:        {o['remitente']}\n")
        texto.insert(tk.END, f"Destinatario:     {o['destinatario'] or 'N/A'}\n")
        texto.insert(tk.END, f"Asunto:           {o['asunto']}\n")
        texto.insert(tk.END, f"Tipo:             {o['tipo_oficio']}\n")
        texto.insert(tk.END, f"Prioridad:        {o['prioridad']}\n\n")
        
        texto.insert(tk.END, "ESTADO ACTUAL\n")
        texto.insert(tk.END, "-"*40 + "\n")
        texto.insert(tk.END, f"Estado:           {o['estado']}\n")
        texto.insert(tk.END, f"Acuse:            {'✅ Recibido' if o['acuse_recibido'] else '❌ Pendiente'}\n")
        
        if o.get('fecha_inicio_tramite'):
            texto.insert(tk.END, f"Inicio trámite:   {o['fecha_inicio_tramite']}\n")
        if o.get('fecha_atendido'):
            texto.insert(tk.END, f"Atendido:         {o['fecha_atendido']}\n")
        if o.get('fecha_asignacion'):
            texto.insert(tk.END, f"Asignación:       {o['fecha_asignacion']}\n\n")
        
        texto.insert(tk.END, "ASIGNACIÓN\n")
        texto.insert(tk.END, "-"*40 + "\n")
        texto.insert(tk.END, f"Asignado a:       {o['asignado'] or 'Sin asignar'}\n")
        if o.get('email_asignado'):
            texto.insert(tk.END, f"Email:            {o['email_asignado']}\n")
        texto.insert(tk.END, f"Creado por:       {o['creador']}\n\n")
        
        if o.get('oficio_respuesta'):
            texto.insert(tk.END, f"Oficio respuesta: {o['oficio_respuesta']}\n")
        
        if o.get('notas'):
            texto.insert(tk.END, "\nNOTAS:\n")
            texto.insert(tk.END, "-"*40 + "\n")
            texto.insert(tk.END, f"{o['notas']}\n")
    
    def crear_botones(self, parent):
        """Crea botones de acción"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Verificar archivos
        archivo = self.db.get_archivo(self.oficio_id, 'oficio')
        if archivo:
            ttk.Button(btn_frame, text="📄 Ver Oficio", 
                      command=self.ver_archivo).pack(side=tk.LEFT, padx=2)
        
        acuse = self.db.get_archivo(self.oficio_id, 'acuse')
        if acuse:
            ttk.Button(btn_frame, text="📄 Ver Acuse", 
                      command=self.ver_acuse).pack(side=tk.LEFT, padx=2)
    
    def ver_archivo(self):
        """Abre el archivo del oficio"""
        self.abrir_archivo_tipo('oficio')
    
    def ver_acuse(self):
        """Abre el archivo de acuse"""
        self.abrir_archivo_tipo('acuse')
    
    def abrir_archivo_tipo(self, tipo):
        """Abre archivo temporal"""
        archivo = self.db.get_archivo(self.oficio_id, tipo)
        if not archivo:
            messagebox.showerror("Error", f"No se encontró archivo de {tipo}")
            return
        
        try:
            temp_dir = Path(tempfile.gettempdir()) / "gestion_oficios"
            temp_dir.mkdir(exist_ok=True)
            
            ruta_temp = temp_dir / archivo['nombre_archivo']
            
            if ruta_temp.exists():
                base = ruta_temp.stem
                ext = ruta_temp.suffix
                ruta_temp = temp_dir / f"{base}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            
            with open(ruta_temp, 'wb') as f:
                f.write(archivo['contenido'])
            
            os.startfile(str(ruta_temp))
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")