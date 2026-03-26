# graficas.py
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
from pathlib import Path

class GraficasManager:
    def __init__(self, db):
        self.db = db
        self.figuras = {}
        self.canvas = {}
        self.axes = {}
        self.stats_labels = {}
        self.periodo_var = tk.StringVar(value="30 días")
    
    def crear_pestana(self, notebook):
        """Crea la pestaña de gráficas"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📊 Reportes Gráficos")
        
        # Panel de control superior
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(control_frame, text="ESTADÍSTICAS VISUALES", 
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(control_frame, text="🔄 Actualizar Gráficas", 
                  command=self.actualizar_graficas,
                  width=20).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(control_frame, text="📋 Ver Datos", 
                  command=self.mostrar_datos_estadisticos,
                  width=15).pack(side=tk.RIGHT, padx=5)
        
        # Notebook para diferentes tipos de gráficas
        graficas_notebook = ttk.Notebook(frame)
        graficas_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña 1: Gráfica de Pastel - Distribución
        self.crear_pestana_distribucion(graficas_notebook)
        
        # Pestaña 2: Gráfica de Estado por Usuario
        self.crear_pestana_estado_usuarios(graficas_notebook)
        
        # Pestaña 3: Gráfica de Tendencias
        self.crear_pestana_tendencias(graficas_notebook)
        
        # Frame para estadísticas rápidas
        stats_frame = ttk.LabelFrame(frame, text="Estadísticas Rápidas", padding="5")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        stats = ['Total Oficios:', 'En Proceso:', 'Atendidos:', 'Archivados:', 'Vencidos:', 'Eficiencia:']
        
        for i, stat in enumerate(stats):
            ttk.Label(stats_frame, text=stat, font=('Arial', 9, 'bold')).grid(row=0, column=i*2, padx=(10,2))
            self.stats_labels[stat] = ttk.Label(stats_frame, text="0", font=('Arial', 9))
            self.stats_labels[stat].grid(row=0, column=i*2+1, padx=(0,15))
        
        # Inicializar gráficas
        self.actualizar_graficas()
    
    def crear_pestana_distribucion(self, notebook):
        """Crea pestaña con gráfica de pastel - Distribución"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🥧 Distribución")
        
        fig = Figure(figsize=(10, 6), dpi=80)
        ax = fig.add_subplot(111)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Guardar referencias
        self.figuras['distribucion'] = fig
        self.axes['distribucion'] = ax
        self.canvas['distribucion'] = canvas
        
        toolbar_frame = ttk.Frame(frame)
        toolbar_frame.pack(fill=tk.X)
        
        ttk.Button(toolbar_frame, text="Guardar Gráfica", 
                  command=lambda: self.guardar_grafica('distribucion', "distribucion_pastel.png")).pack(side=tk.LEFT, padx=5)
    
    def crear_pestana_estado_usuarios(self, notebook):
        """Crea pestaña con gráfica de estado por usuario (colores semáforo)"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🚦 Estado Usuarios")
        
        fig = Figure(figsize=(10, 6), dpi=80)
        ax = fig.add_subplot(111)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Guardar referencias
        self.figuras['estado_usuarios'] = fig
        self.axes['estado_usuarios'] = ax
        self.canvas['estado_usuarios'] = canvas
        
        # Panel de leyenda
        leyenda_frame = ttk.Frame(frame)
        leyenda_frame.pack(fill=tk.X, pady=5)
        
        # Crear leyenda visual
        colores = [
            ("🟢 Verde", "#28A745", "Sin oficios asignados"),
            ("🟠 Naranja", "#FFA500", "Con oficios en proceso (<=3 días)"),
            ("🔴 Rojo", "#DC3545", "Con oficios vencidos (>3 días)")
        ]
        
        for i, (texto, color, desc) in enumerate(colores):
            frame_color = tk.Frame(leyenda_frame, bg=color, width=20, height=20)
            frame_color.pack(side=tk.LEFT, padx=(20 if i>0 else 5, 2))
            frame_color.pack_propagate(False)
            ttk.Label(leyenda_frame, text=f"{texto} - {desc}").pack(side=tk.LEFT, padx=5)
        
        toolbar_frame = ttk.Frame(frame)
        toolbar_frame.pack(fill=tk.X)
        
        ttk.Button(toolbar_frame, text="Guardar Gráfica", 
                  command=lambda: self.guardar_grafica('estado_usuarios', "estado_usuarios.png")).pack(side=tk.LEFT, padx=5)
    
    def crear_pestana_tendencias(self, notebook):
        """Crea pestaña con gráfica de tendencias temporales"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📈 Tendencias")
        
        fig = Figure(figsize=(10, 6), dpi=80)
        ax = fig.add_subplot(111)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Guardar referencias
        self.figuras['tendencias'] = fig
        self.axes['tendencias'] = ax
        self.canvas['tendencias'] = canvas
        
        # Selector de período
        periodo_frame = ttk.Frame(frame)
        periodo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(periodo_frame, text="Período:").pack(side=tk.LEFT, padx=5)
        periodo_combo = ttk.Combobox(periodo_frame, textvariable=self.periodo_var,
                                     values=['7 días', '15 días', '30 días', '90 días', 'Todos'],
                                     width=15, state='readonly')
        periodo_combo.pack(side=tk.LEFT, padx=5)
        periodo_combo.bind('<<ComboboxSelected>>', lambda e: self.actualizar_tendencias())
        
        ttk.Button(periodo_frame, text="Actualizar", 
                  command=self.actualizar_tendencias).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(periodo_frame, text="Guardar Gráfica", 
                  command=lambda: self.guardar_grafica('tendencias', "tendencias.png")).pack(side=tk.RIGHT, padx=5)
    
    def obtener_datos_estadisticos(self):
        """Obtiene datos estadísticos de la BD"""
        try:
            # Totales por estado
            self.db.cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN estado = 'En Proceso' THEN 1 END) as en_proceso,
                    COUNT(CASE WHEN estado = 'Atendido' THEN 1 END) as atendidos,
                    COUNT(CASE WHEN estado = 'Archivado' THEN 1 END) as archivados,
                    COUNT(CASE 
                        WHEN estado = 'En Proceso' 
                        AND fecha_asignacion IS NOT NULL 
                        AND EXTRACT(DAY FROM (NOW() - fecha_asignacion)) > 3 
                        THEN 1 
                    END) as vencidos
                FROM oficios
            """)
            totales = self.db.cursor.fetchone()
            
            # Datos por usuario para el semáforo
            self.db.cursor.execute("""
                SELECT 
                    u.id,
                    u.nombre_completo,
                    u.color_manual,
                    COUNT(o.id) as total_asignados,
                    COUNT(CASE WHEN o.estado = 'En Proceso' THEN 1 END) as en_proceso,
                    COUNT(CASE WHEN o.estado = 'Atendido' THEN 1 END) as atendidos,
                    COUNT(CASE WHEN o.estado = 'Archivado' THEN 1 END) as archivados,
                    COUNT(CASE 
                        WHEN o.estado = 'En Proceso' 
                        AND o.fecha_asignacion IS NOT NULL 
                        AND EXTRACT(DAY FROM (NOW() - o.fecha_asignacion)) > 3 
                        THEN 1 
                    END) as vencidos,
                    MAX(CASE 
                        WHEN o.estado = 'En Proceso' 
                        AND o.fecha_asignacion IS NOT NULL 
                        AND EXTRACT(DAY FROM (NOW() - o.fecha_asignacion)) > 3 
                        THEN 1 
                        ELSE 0 
                    END) as tiene_vencidos
                FROM usuarios u
                LEFT JOIN oficios o ON u.id = o.usuario_asignado_id
                WHERE u.activo = TRUE AND u.es_admin = FALSE
                GROUP BY u.id, u.nombre_completo, u.color_manual
                ORDER BY u.nombre_completo
            """)
            datos_usuarios = self.db.cursor.fetchall()
            
            # Tendencias temporales
            dias_map = {
                '7 días': 7,
                '15 días': 15,
                '30 días': 30,
                '90 días': 90,
                'Todos': 365
            }
            periodo = dias_map.get(self.periodo_var.get(), 30)
            
            self.db.cursor.execute("""
                SELECT 
                    DATE(fecha_creacion) as fecha,
                    COUNT(*) as total,
                    COUNT(CASE WHEN estado = 'En Proceso' THEN 1 END) as proceso,
                    COUNT(CASE WHEN estado = 'Atendido' THEN 1 END) as atendido
                FROM oficios
                WHERE fecha_creacion >= CURRENT_DATE - %s::integer
                GROUP BY DATE(fecha_creacion)
                ORDER BY fecha
            """, (periodo,))
            tendencias = self.db.cursor.fetchall()
            
            return {
                'totales': totales,
                'usuarios': datos_usuarios,
                'tendencias': tendencias
            }
        except Exception as e:
            print(f"Error obteniendo datos estadísticos: {e}")
            return None
    
    def actualizar_graficas(self):
        """Actualiza todas las gráficas con datos actuales"""
        datos = self.obtener_datos_estadisticos()
        if not datos:
            return
        
        totales = datos['totales']
        
        # Actualizar estadísticas rápidas
        total = totales['total'] or 0
        proceso = totales['en_proceso'] or 0
        atendidos = totales['atendidos'] or 0
        archivados = totales['archivados'] or 0
        vencidos = totales['vencidos'] or 0
        eficiencia = (atendidos / total * 100) if total > 0 else 0
        
        if 'Total Oficios:' in self.stats_labels:
            self.stats_labels['Total Oficios:'].config(text=str(total))
            self.stats_labels['En Proceso:'].config(text=str(proceso))
            self.stats_labels['Atendidos:'].config(text=str(atendidos))
            self.stats_labels['Archivados:'].config(text=str(archivados))
            self.stats_labels['Vencidos:'].config(text=str(vencidos))
            self.stats_labels['Eficiencia:'].config(text=f"{eficiencia:.1f}%")
        
        # Actualizar gráfica de distribución (pastel)
        self.actualizar_grafica_distribucion(totales)
        
        # Actualizar gráfica de estado por usuario (semáforo)
        self.actualizar_grafica_estado_usuarios(datos['usuarios'])
        
        # Actualizar tendencias
        self.actualizar_tendencias()
    
    def actualizar_grafica_distribucion(self, totales):
        """Actualiza la gráfica de pastel - Distribución"""
        if 'distribucion' not in self.axes:
            return
        
        ax = self.axes['distribucion']
        ax.clear()
        
        labels = ['En Proceso', 'Atendido', 'Archivado']
        valores = [
            totales['en_proceso'] or 0,
            totales['atendidos'] or 0,
            totales['archivados'] or 0
        ]
        colores = ['#FFA500', '#28A745', '#6C757D']  # Naranja, Verde, Gris
        
        # Filtrar valores cero
        datos = [(l, v, c) for l, v, c in zip(labels, valores, colores) if v > 0]
        if not datos:
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', fontsize=14)
            self.canvas['distribucion'].draw()
            return
        
        labels_filt, valores_filt, colores_filt = zip(*datos)
        
        # Crear gráfica de pastel
        wedges, texts, autotexts = ax.pie(
            valores_filt, 
            labels=labels_filt, 
            autopct=lambda pct: f'{pct:.1f}%' if pct > 0 else '',
            colors=colores_filt,
            startangle=90,
            textprops={'fontweight': 'bold'}
        )
        
        # Mejorar formato de porcentajes
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
        
        ax.set_title('Distribución de Oficios por Estado', fontsize=14, fontweight='bold')
        ax.axis('equal')
        
        self.canvas['distribucion'].draw()
    
    def actualizar_grafica_estado_usuarios(self, datos_usuarios):
        """Actualiza la gráfica de estado por usuario (colores semáforo)"""
        if 'estado_usuarios' not in self.axes:
            return
        
        ax = self.axes['estado_usuarios']
        ax.clear()
        
        if not datos_usuarios:
            ax.text(0.5, 0.5, 'Sin datos de usuarios', 
                                         ha='center', va='center', fontsize=14)
            self.canvas['estado_usuarios'].draw()
            return
        
        # Preparar datos
        nombres = []
        colores = []
        totales_usuario = []
        
        for u in datos_usuarios:
            nombre = u['nombre_completo'][:20] + ('...' if len(u['nombre_completo']) > 20 else '')
            nombres.append(nombre)
            total_asignados = u['total_asignados'] or 0
            totales_usuario.append(total_asignados)
            
            # Determinar color según reglas:
            tiene_vencidos = u['tiene_vencidos'] or 0
            en_proceso = u['en_proceso'] or 0
            
            if u['color_manual'] == 'verde':
                color = '#28A745'  # Verde (forzado)
            elif tiene_vencidos > 0:
                color = '#DC3545'  # Rojo
            elif en_proceso > 0:
                color = '#FFA500'  # Naranja
            else:
                color = '#28A745'  # Verde
            
            colores.append(color)
        
        # Crear barras
        x = np.arange(len(nombres))
        barras = ax.bar(x, totales_usuario, color=colores, 
                                             edgecolor='black', linewidth=1.5)
        
        # Añadir valores en las barras
        for barra, total in zip(barras, totales_usuario):
            height = barra.get_height()
            if height > 0:
                ax.text(barra.get_x() + barra.get_width()/2., height,
                                             f'{int(height)}', ha='center', va='bottom', 
                                             fontweight='bold', fontsize=10)
        
        # Configurar ejes
        ax.set_xlabel('Usuarios', fontsize=12)
        ax.set_ylabel('Cantidad de Oficios', fontsize=12)
        ax.set_title('Estado por Usuario (Semáforo)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, rotation=45, ha='right', fontsize=9)
        
        # Configurar eje Y
        max_valor = max(totales_usuario) if totales_usuario else 0
        y_max = max(10, max_valor + 1)
        ax.set_ylim(0, y_max)
        ax.set_yticks(range(0, int(y_max) + 1))
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # Añadir leyenda de colores
        verde_patch = mpatches.Patch(color='#28A745', label='Verde - Sin oficios / Concluido')
        naranja_patch = mpatches.Patch(color='#FFA500', label='Naranja - En proceso (<=3 días)')
        rojo_patch = mpatches.Patch(color='#DC3545', label='Rojo - Con vencidos (>3 días)')
        
        ax.legend(handles=[verde_patch, naranja_patch, rojo_patch], 
                                        loc='upper right', fontsize=8)
        
        self.canvas['estado_usuarios'].draw()
    
    def actualizar_tendencias(self, event=None):
        """Actualiza la gráfica de tendencias temporales"""
        if 'tendencias' not in self.axes:
            return
        
        datos = self.obtener_datos_estadisticos()
        if not datos or not datos['tendencias']:
            ax = self.axes['tendencias']
            ax.clear()
            ax.text(0.5, 0.5, 'Sin datos para el período seleccionado', 
                                   ha='center', va='center', fontsize=14)
            self.canvas['tendencias'].draw()
            return
        
        tendencias = datos['tendencias']
        
        ax = self.axes['tendencias']
        ax.clear()
        
        fechas = [t['fecha'].strftime('%d/%m') for t in tendencias]
        totales = [t['total'] for t in tendencias]
        proceso = [t['proceso'] for t in tendencias]
        atendido = [t['atendido'] for t in tendencias]
        
        ax.plot(fechas, totales, marker='o', label='Total', linewidth=2, color='#007BFF')
        ax.plot(fechas, proceso, marker='s', label='En Proceso', linewidth=2, color='#FFA500')
        ax.plot(fechas, atendido, marker='^', label='Atendido', linewidth=2, color='#28A745')
        
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Cantidad de Oficios', fontsize=12)
        ax.set_title(f'Tendencia - Últimos {self.periodo_var.get()}', 
                                     fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(axis='x', rotation=45)
        
        # Ajustar layout
        ax.figure.tight_layout()
        
        self.canvas['tendencias'].draw()
    
    def guardar_grafica(self, tipo, nombre_archivo):
        """Guarda la gráfica como archivo de imagen"""
        if tipo not in self.figuras:
            return
        
        try:
            from .config import Config
            # Crear carpeta de reportes si no existe
            carpeta_reportes = Path(Config.CARPETA_BASE) / ".." / "graficas"
            carpeta_reportes.mkdir(exist_ok=True)
            
            # Generar nombre único
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_completo = carpeta_reportes / f"{timestamp}_{nombre_archivo}"
            
            # Guardar figura
            self.figuras[tipo].savefig(nombre_completo, dpi=100, bbox_inches='tight', facecolor='white')
            
            messagebox.showinfo("Éxito", f"Gráfica guardada como:\n{nombre_completo}")
            
            # Preguntar si quiere abrir la carpeta
            if messagebox.askyesno("Abrir", "¿Desea abrir la carpeta de gráficas?"):
                import os
                os.startfile(str(carpeta_reportes))
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la gráfica:\n{str(e)}")
    
    def mostrar_datos_estadisticos(self):
        """Muestra ventana con datos estadísticos detallados"""
        datos = self.obtener_datos_estadisticos()
        if not datos:
            return
        
        totales = datos['totales']
        
        dialog = tk.Toplevel()
        dialog.title("Datos Estadísticos Detallados")
        dialog.geometry("600x500")
        dialog.transient()
        
        # Crear texto con estadísticas
        texto = tk.Text(dialog, wrap=tk.WORD, font=('Courier', 10), padx=10, pady=10)
        texto.pack(fill=tk.BOTH, expand=True)
        
        # Encabezado
        texto.insert(tk.END, "="*60 + "\n")
        texto.insert(tk.END, "ESTADÍSTICAS DETALLADAS\n")
        texto.insert(tk.END, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        texto.insert(tk.END, "="*60 + "\n\n")
        
        # Totales generales
        texto.insert(tk.END, "RESUMEN GENERAL\n")
        texto.insert(tk.END, "-"*40 + "\n")
        texto.insert(tk.END, f"Total de oficios:     {totales['total'] or 0}\n")
        texto.insert(tk.END, f"En Proceso:           {totales['en_proceso'] or 0}\n")
        texto.insert(tk.END, f"Atendidos:            {totales['atendidos'] or 0}\n")
        texto.insert(tk.END, f"Archivados:           {totales['archivados'] or 0}\n")
        texto.insert(tk.END, f"Vencidos (+3 días):   {totales['vencidos'] or 0}\n\n")
        
        # Porcentajes
        total = totales['total'] or 0
        if total > 0:
            p_proceso = (totales['en_proceso'] or 0) / total * 100
            p_atendidos = (totales['atendidos'] or 0) / total * 100
            p_archivados = (totales['archivados'] or 0) / total * 100
            
            texto.insert(tk.END, "PORCENTAJES\n")
            texto.insert(tk.END, "-"*40 + "\n")
            texto.insert(tk.END, f"En Proceso:  {p_proceso:.1f}%\n")
            texto.insert(tk.END, f"Atendidos:   {p_atendidos:.1f}%\n")
            texto.insert(tk.END, f"Archivados:  {p_archivados:.1f}%\n")
            texto.insert(tk.END, f"Eficiencia:  {(totales['atendidos'] or 0)/total*100:.1f}%\n\n")
        
        # Estado por usuario
        texto.insert(tk.END, "\nESTADO POR USUARIO (SEMÁFORO)\n")
        texto.insert(tk.END, "-"*60 + "\n")
        texto.insert(tk.END, f"{'Usuario':<30} {'Total':<8} {'Proceso':<8} {'Atend.':<8} {'Venc.':<6} {'Estado':<10}\n")
        texto.insert(tk.END, "-"*60 + "\n")
        
        for u in datos['usuarios']:
            total_u = u['total_asignados'] or 0
            proceso_u = u['en_proceso'] or 0
            atendidos_u = u['atendidos'] or 0
            vencidos_u = u['vencidos'] or 0
            
            # Determinar estado visual
            if u['color_manual'] == 'verde':
                estado = "🟢 VERDE"
            elif vencidos_u > 0:
                estado = "🔴 ROJO"
            elif proceso_u > 0:
                estado = "🟠 NARANJA"
            else:
                estado = "🟢 VERDE"
            
            texto.insert(tk.END, f"{u['nombre_completo'][:30]:<30} "
                                 f"{total_u:<8} "
                                 f"{proceso_u:<8} "
                                 f"{atendidos_u:<8} "
                                 f"{vencidos_u:<6} "
                                 f"{estado}\n")
        
        # Hacer el texto de solo lectura
        texto.config(state=tk.DISABLED)
        
        # Botón para cerrar
        ttk.Button(dialog, text="Cerrar", command=dialog.destroy).pack(pady=5)