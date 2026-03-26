# archivos_gestion.py
import os
import shutil
import tempfile
import hashlib
import mimetypes
from pathlib import Path
from tkinter import messagebox, filedialog
from datetime import datetime
class ArchivosGestion:
    def __init__(self, db, config):
        self.db = db
        self.config = config
    
    def guardar_archivo_local(self, ruta_origen, carpeta_destino, nuevo_nombre=None):
        """Guarda una copia física del archivo"""
        Path(carpeta_destino).mkdir(parents=True, exist_ok=True)
        
        if nuevo_nombre:
            nombre = nuevo_nombre
        else:
            nombre = os.path.basename(ruta_origen)
        
        destino = os.path.join(carpeta_destino, nombre)
        shutil.copy2(ruta_origen, destino)
        return destino
    
    def archivo_a_bytes(self, ruta_archivo):
        """Convierte archivo a bytes"""
        try:
            with open(ruta_archivo, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"Error leyendo archivo: {e}")
            return None
    
    def calcular_hash(self, contenido_bytes):
        """Calcula hash MD5"""
        return hashlib.md5(contenido_bytes).hexdigest()
    
    def guardar_en_bd(self, oficio_id, tipo, ruta_archivo, usuario_id):
        """Guarda archivo en BD"""
        contenido = self.archivo_a_bytes(ruta_archivo)
        if not contenido:
            return False
        
        nombre = os.path.basename(ruta_archivo)
        return self.db.guardar_archivo(oficio_id, tipo, nombre, contenido, usuario_id)
    
    def ver_archivo(self, oficio_id, tipo='oficio'):
        """Extrae y abre un archivo de la BD"""
        try:
            archivo = self.db.get_archivo(oficio_id, tipo)
            
            if not archivo:
                messagebox.showerror("Error", "No se encontró archivo")
                return
            
            # Crear archivo temporal
            temp_dir = Path(tempfile.gettempdir()) / "gestion_oficios"
            temp_dir.mkdir(exist_ok=True)
            
            ruta_temp = temp_dir / archivo['nombre_archivo']
            
            # Si ya existe, agregar sufijo
            if ruta_temp.exists():
                base = ruta_temp.stem
                ext = ruta_temp.suffix
                ruta_temp = temp_dir / f"{base}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            
            # Guardar archivo temporal
            with open(ruta_temp, 'wb') as f:
                f.write(archivo['contenido'])
            
            # Abrir con programa predeterminado
            os.startfile(str(ruta_temp))
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir archivo: {e}")

    # servidor/archivos_gestion.py - Agregar este método si no existe

    def guardar_archivo_oficio(self, oficio_id, ruta_archivo, usuario_id, tipo='oficio'):
        """Guarda un archivo en la base de datos"""
        import mimetypes
        import hashlib
        import psycopg2
        
        with open(ruta_archivo, 'rb') as f:
            contenido = f.read()
        
        nombre_archivo = os.path.basename(ruta_archivo)
        mime_type = mimetypes.guess_type(ruta_archivo)[0] or 'application/octet-stream'
        hash_md5 = hashlib.md5(contenido).hexdigest()
        
        self.db.cursor.execute("""
            INSERT INTO archivos_binarios 
            (oficio_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id, hash_md5)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (oficio_id, tipo, nombre_archivo, psycopg2.Binary(contenido), 
            mime_type, len(contenido), usuario_id, hash_md5))
    
    def seleccionar_archivo(self, titulo="Seleccionar archivo"):
        """Abre diálogo para seleccionar archivo"""
        return filedialog.askopenfilename(
            title=titulo,
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("PDF files", "*.pdf"),
                ("Excel files", "*.xlsx;*.xls"),
                ("Word files", "*.docx;*.doc"),
                ("Imágenes", "*.jpg;*.jpeg;*.png")
            ]
        )