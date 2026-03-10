#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class Progress Widget - Widget de progreso de clase para Robot GUI
================================================================

Widget para mostrar el progreso actual de una clase en ejecución
"""

import tkinter as tk
from tkinter import ttk
import threading
import time

class ClassProgressWidget:
    """Widget de progreso de clase"""
    
    def __init__(self, parent, class_manager):
        self.parent = parent
        self.class_manager = class_manager
        self.update_thread = None
        self.running = False
        
        # Crear el widget
        self.create_widget()
        
        # Iniciar actualizaciones
        self.start_updates()
    
    def create_widget(self):
        """Crear el widget de progreso"""
        # Frame principal
        self.main_frame = tk.LabelFrame(self.parent, text="📚 Progreso de Clase", 
                                       font=('Arial', 12, 'bold'),
                                       bg='#2d2d2d', fg='#ffffff')
        self.main_frame.pack(fill="x", padx=10, pady=5)
        
        # Estado inicial (sin clase activa)
        self.create_idle_state()
    
    def create_idle_state(self):
        """Crear estado inactivo"""
        # Limpiar frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Mensaje de estado inactivo
        self.idle_label = tk.Label(self.main_frame, 
                                 text="No hay clase en ejecución",
                                 font=('Arial', 10),
                                 bg='#2d2d2d', fg='#888888')
        self.idle_label.pack(pady=20)
    
    def create_active_state(self, progress_info):
        """Crear estado activo con información de progreso"""
        # Limpiar frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Información de la clase
        class_frame = tk.Frame(self.main_frame, bg='#2d2d2d')
        class_frame.pack(fill="x", padx=10, pady=5)
        
        # Nombre de la clase
        class_name = progress_info.get('class_name', 'Clase desconocida')
        self.class_name_label = tk.Label(class_frame, 
                                       text=f"🎓 {class_name}",
                                       font=('Arial', 11, 'bold'),
                                       bg='#2d2d2d', fg='#4CAF50')
        self.class_name_label.pack(anchor="w")
        
        # Fase actual
        phase_frame = tk.Frame(self.main_frame, bg='#2d2d2d')
        phase_frame.pack(fill="x", padx=10, pady=5)
        
        phase_emoji = progress_info.get('phase_emoji', '❓')
        current_phase = progress_info.get('current_phase', 'Fase desconocida')
        self.phase_label = tk.Label(phase_frame, 
                                  text=f"{phase_emoji} {current_phase}",
                                  font=('Arial', 10, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        self.phase_label.pack(anchor="w")
        
        # Sub-fase
        sub_phase = progress_info.get('sub_phase', '')
        if sub_phase:
            self.sub_phase_label = tk.Label(phase_frame, 
                                          text=f"   {sub_phase}",
                                          font=('Arial', 9),
                                          bg='#2d2d2d', fg='#cccccc')
            self.sub_phase_label.pack(anchor="w")
        
        # Barra de progreso
        progress_frame = tk.Frame(self.main_frame, bg='#2d2d2d')
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        progress_percentage = progress_info.get('progress_percentage', 0)
        self.progress_var = tk.DoubleVar(value=progress_percentage)
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                          variable=self.progress_var,
                                          maximum=100,
                                          length=200,
                                          mode='determinate')
        self.progress_bar.pack(fill="x", pady=2)
        
        # Porcentaje
        self.percentage_label = tk.Label(progress_frame, 
                                       text=f"{progress_percentage}%",
                                       font=('Arial', 9),
                                       bg='#2d2d2d', fg='#ffffff')
        self.percentage_label.pack(anchor="e")
        
        # Información de tiempo
        time_frame = tk.Frame(self.main_frame, bg='#2d2d2d')
        time_frame.pack(fill="x", padx=10, pady=5)
        
        elapsed_time = progress_info.get('elapsed_time', '0s')
        remaining_time = progress_info.get('remaining_time', '0s')
        
        self.time_label = tk.Label(time_frame, 
                                 text=f"⏱️ Tiempo: {elapsed_time} / Restante: {remaining_time}",
                                 font=('Arial', 9),
                                 bg='#2d2d2d', fg='#cccccc')
        self.time_label.pack(anchor="w")
        
        # Paso actual
        step_frame = tk.Frame(self.main_frame, bg='#2d2d2d')
        step_frame.pack(fill="x", padx=10, pady=5)
        
        step = progress_info.get('step', 0)
        total_steps = progress_info.get('total_steps', 0)
        
        self.step_label = tk.Label(step_frame, 
                                 text=f"📋 Paso {step} de {total_steps}",
                                 font=('Arial', 9),
                                 bg='#2d2d2d', fg='#cccccc')
        self.step_label.pack(anchor="w")
        
        # Estado
        status_frame = tk.Frame(self.main_frame, bg='#2d2d2d')
        status_frame.pack(fill="x", padx=10, pady=5)
        
        status = progress_info.get('status', 'Estado desconocido')
        status_color = '#4CAF50' if progress_info.get('is_active', False) else '#ff9800'
        
        self.status_label = tk.Label(status_frame, 
                                   text=f"🔄 {status}",
                                   font=('Arial', 9),
                                   bg='#2d2d2d', fg=status_color)
        self.status_label.pack(anchor="w")
        
        # Detalles adicionales
        details = progress_info.get('details', '')
        if details:
            self.details_label = tk.Label(status_frame, 
                                        text=f"   {details}",
                                        font=('Arial', 8),
                                        bg='#2d2d2d', fg='#888888',
                                        wraplength=250)
            self.details_label.pack(anchor="w", pady=2)
    
    def update_progress(self):
        """Actualizar información de progreso"""
        try:
            if not self.class_manager:
                return
            
            # Obtener información de progreso
            progress_info = self.class_manager.get_class_progress()
            
            # Verificar si hay clase activa
            is_active = progress_info.get('is_active', False)
            class_name = progress_info.get('class_name')
            
            if not is_active or not class_name:
                # No hay clase activa
                if hasattr(self, 'idle_label'):
                    return  # Ya está en estado inactivo
                self.create_idle_state()
            else:
                # Hay clase activa
                self.create_active_state(progress_info)
                
        except Exception as e:
            print(f"Error actualizando progreso: {e}")
    
    def start_updates(self):
        """Iniciar actualizaciones automáticas"""
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
    
    def stop_updates(self):
        """Detener actualizaciones"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
    
    def _update_loop(self):
        """Loop de actualización"""
        while self.running:
            try:
                # Actualizar en el hilo principal
                self.parent.after(0, self.update_progress)
                time.sleep(2)  # Actualizar cada 2 segundos
            except Exception as e:
                print(f"Error en loop de actualización: {e}")
                time.sleep(5)  # Esperar más tiempo si hay error
    
    def destroy(self):
        """Destruir el widget"""
        self.stop_updates()
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
