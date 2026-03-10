# -*- coding: utf-8 -*-
"""
Classes Manager Tab for RobotGUI
===============================

Tab para gestionar las clases generadas por el Class Builder.
Permite ver, ejecutar, pausar, continuar y detener clases desde la interfaz principal.
Incluye sistema completo de progreso en tiempo real.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .base_tab import BaseTab
import os
import json
import threading
import time

class ClassesManagerTab(BaseTab):
    """Tab para gestionar clases generadas con sistema de progreso completo"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "📚 Classes Manager"
        
        # Variables
        self.classes_list = []
        self.selected_class = None
        self.refresh_timer = None
        self.progress_update_timer = None
        self.current_progress = None
        
        # Progress tracking
        self.is_class_running = False
        self.current_class_name = None
        
    def setup_tab_content(self):
        """Setup the classes manager tab content with progress system"""
        # Create scrollable frame
        main_content, canvas, container = self.create_scrollable_frame(self.tab_frame)
        
        # Title
        title_label = tk.Label(main_content, text="📚 Gestor de Clases ADAI", 
                              font=('Arial', 18, 'bold'), 
                              bg='#1e1e1e', fg='#ffffff')
        title_label.pack(pady=(10, 20))
        
        # Subtitle
        subtitle = tk.Label(main_content, text="Gestiona y ejecuta las clases con control completo de progreso", 
                           font=('Arial', 11), 
                           bg='#1e1e1e', fg='#888888')
        subtitle.pack(pady=(0, 20))
        
        # Main container
        main_container = tk.Frame(main_content, bg='#1e1e1e')
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Classes list
        left_frame = tk.Frame(main_container, bg='#1e1e1e')
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Classes list header
        list_header = tk.Frame(left_frame, bg='#2d2d2d')
        list_header.pack(fill="x", pady=(0, 10))
        
        tk.Label(list_header, text="📋 Clases Disponibles", 
                font=('Arial', 14, 'bold'),
                bg='#2d2d2d', fg='#ffffff').pack(side="left")
        
        # Refresh button
        refresh_btn = tk.Button(list_header, text="🔄 Refrescar", 
                               bg='#2196F3', fg='#ffffff',
                               font=('Arial', 10, 'bold'),
                               command=self.refresh_classes)
        refresh_btn.pack(side="right")
        
        # Classes listbox with scrollbar
        list_frame = tk.Frame(left_frame, bg='#2d2d2d')
        list_frame.pack(fill="both", expand=True)
        
        # Listbox
        self.classes_listbox = tk.Listbox(list_frame, bg='#3d3d3d', fg='#ffffff',
                                         font=('Arial', 11), height=15,
                                         selectmode=tk.SINGLE)
        self.classes_listbox.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        list_scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.classes_listbox.yview)
        list_scrollbar.pack(side="right", fill="y")
        self.classes_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Bind selection event
        self.classes_listbox.bind('<<ListboxSelect>>', self.on_class_select)
        
        # Right side - Class details, progress and actions
        right_frame = tk.Frame(main_container, bg='#1e1e1e')
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        
        # Class details frame
        details_frame = tk.LabelFrame(right_frame, text="📖 Detalles de la Clase", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        details_frame.pack(fill="x", pady=(0, 15))
        
        # Details text area
        self.details_text = tk.Text(details_frame, bg='#3d3d3d', fg='#ffffff',
                                   font=('Arial', 10), wrap=tk.WORD, 
                                   height=8, width=40)
        self.details_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Progress frame
        progress_frame = tk.LabelFrame(right_frame, text="📊 Progreso de la Clase", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#2d2d2d', fg='#ffffff')
        progress_frame.pack(fill="x", pady=(0, 15))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', 
                                           length=300, style='TProgressbar')
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))
        
        # Progress info
        self.progress_info = tk.Label(progress_frame, text="No hay clase ejecutándose", 
                                     bg='#3d3d3d', fg='#888888',
                                     font=('Arial', 10))
        self.progress_info.pack(fill="x", padx=10, pady=(0, 5))
        
        # Progress details
        self.progress_details = tk.Label(progress_frame, text="", 
                                        bg='#3d3d3d', fg='#cccccc',
                                        font=('Arial', 9))
        self.progress_details.pack(fill="x", padx=10, pady=(0, 10))
        
        # Control buttons frame
        control_frame = tk.LabelFrame(right_frame, text="🎮 Control de Ejecución", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        control_frame.pack(fill="x", pady=(0, 15))
        
        # Control buttons
        self.execute_btn = tk.Button(control_frame, text="▶️ Ejecutar Clase", 
                                    bg='#4CAF50', fg='#ffffff',
                                    font=('Arial', 11, 'bold'),
                                    command=self.execute_selected_class)
        self.execute_btn.pack(fill="x", padx=10, pady=5)
        
        self.pause_btn = tk.Button(control_frame, text="⏸️ Pausar Clase", 
                                  bg='#FF9800', fg='#ffffff',
                                  font=('Arial', 11, 'bold'),
                                  command=self.pause_current_class,
                                  state="disabled")
        self.pause_btn.pack(fill="x", padx=10, pady=5)
        
        self.resume_btn = tk.Button(control_frame, text="▶️ Continuar Clase", 
                                   bg='#2196F3', fg='#ffffff',
                                   font=('Arial', 11, 'bold'),
                                   command=self.resume_current_class,
                                   state="disabled")
        self.resume_btn.pack(fill="x", padx=10, pady=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Detener Clase", 
                                 bg='#f44336', fg='#ffffff',
                                 font=('Arial', 11, 'bold'),
                                 command=self.stop_current_class,
                                 state="disabled")
        self.stop_btn.pack(fill="x", padx=10, pady=5)
        
        # Actions frame
        actions_frame = tk.LabelFrame(right_frame, text="⚡ Acciones", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        actions_frame.pack(fill="x", pady=(0, 15))
        
        # Action buttons
        self.delete_btn = tk.Button(actions_frame, text="🗑️ Eliminar Clase", 
                                   bg='#f44336', fg='#ffffff',
                                   font=('Arial', 11, 'bold'),
                                   command=self.delete_selected_class)
        self.delete_btn.pack(fill="x", padx=10, pady=5)
        
        # Status frame
        status_frame = tk.LabelFrame(right_frame, text="📊 Estado", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#2d2d2d', fg='#ffffff')
        status_frame.pack(fill="x")
        
        self.status_label = tk.Label(status_frame, text="Listo para gestionar clases", 
                                    bg='#3d3d3d', fg='#4CAF50',
                                    font=('Arial', 10))
        self.status_label.pack(fill="x", padx=10, pady=10)
        
        # Load initial classes
        self.refresh_classes()
        
        # Start progress monitoring
        self.start_progress_monitoring()
        
        # Auto-refresh every 30 seconds
        self.start_auto_refresh()
    
    def start_progress_monitoring(self):
        """Start monitoring class progress"""
        def update_progress():
            try:
                if hasattr(self.parent_gui, 'class_manager') and self.parent_gui.class_manager:
                    # Get current progress
                    progress_info = self.parent_gui.class_manager.get_class_progress()
                    
                    if progress_info and progress_info.get('is_active', False):
                        self.update_progress_display(progress_info)
                        self.is_class_running = True
                        self.current_class_name = progress_info.get('class_name')
                        self.update_control_buttons(True)
                    else:
                        self.clear_progress_display()
                        self.is_class_running = False
                        self.current_class_name = None
                        self.update_control_buttons(False)
                
                # Schedule next update (every 2 seconds)
                self.progress_update_timer = self.parent_gui.root.after(2000, update_progress)
                
            except Exception as e:
                print(f"Error in progress monitoring: {e}")
                # Continue monitoring even if there's an error
                self.progress_update_timer = self.parent_gui.root.after(2000, update_progress)
        
        # Start the monitoring
        update_progress()
    
    def update_progress_display(self, progress_info):
        """Update the progress display with current information"""
        try:
            # Update progress bar
            percentage = progress_info.get('progress_percentage', 0)
            self.progress_bar['value'] = percentage
            
            # Update progress info
            class_name = progress_info.get('class_name', 'Desconocida')
            current_phase = progress_info.get('current_phase', 'Desconocida')
            phase_emoji = progress_info.get('phase_emoji', '📊')
            
            self.progress_info.config(
                text=f"{phase_emoji} {current_phase} - {percentage}%",
                fg='#4CAF50'
            )
            
            # Update progress details
            elapsed_time = progress_info.get('elapsed_time', '0s')
            remaining_time = progress_info.get('remaining_time', '0s')
            status = progress_info.get('status', 'Ejecutando')
            
            details_text = f"⏱️ Tiempo: {elapsed_time} | ⏳ Restante: {remaining_time}\n📊 Estado: {status}"
            self.progress_details.config(text=details_text)
            
        except Exception as e:
            print(f"Error updating progress display: {e}")
    
    def clear_progress_display(self):
        """Clear the progress display"""
        try:
            self.progress_bar['value'] = 0
            self.progress_info.config(text="No hay clase ejecutándose", fg='#888888')
            self.progress_details.config(text="")
        except Exception as e:
            print(f"Error clearing progress display: {e}")
    
    def update_control_buttons(self, class_running):
        """Update control buttons based on class execution state"""
        try:
            if class_running:
                # Class is running - keep execute enabled to allow starting another class
                # Enable pause, resume, stop
                self.execute_btn.config(state="normal")  # Siempre habilitado
                self.pause_btn.config(state="normal")
                self.resume_btn.config(state="normal")
                self.stop_btn.config(state="normal")
            else:
                # No class running - enable execute, disable others
                self.execute_btn.config(state="normal")
                self.pause_btn.config(state="disabled")
                self.resume_btn.config(state="disabled")
                self.stop_btn.config(state="disabled")
        except Exception as e:
            print(f"Error updating control buttons: {e}")
    
    def execute_selected_class(self):
        """Execute the selected class"""
        try:
            if not self.selected_class:
                messagebox.showwarning("Sin selección", "Por favor selecciona una clase")
                return
            
            class_name = self.selected_class.get('name')
            class_title = self.selected_class.get('title', 'Clase')
            
            # Check if there's already a class running
            if self.is_class_running and self.current_class_name:
                # Ask if user wants to stop current class and start new one
                response = messagebox.askyesnocancel(
                    "Clase en Ejecución", 
                    f"Ya hay una clase ejecutándose: '{self.current_class_name}'\n\n"
                    f"¿Deseas detener la clase actual e iniciar '{class_title}'?\n\n"
                    f"• Sí: Detener clase actual e iniciar nueva\n"
                    f"• No: Cancelar y mantener clase actual\n"
                    f"• Cancelar: No hacer nada"
                )
                
                if response is None:  # Cancel
                    return
                elif response:  # Yes - stop current and start new
                    self.update_status(f"⏹️ Deteniendo clase actual...")
                    if hasattr(self.parent_gui, 'class_manager') and self.parent_gui.class_manager:
                        self.parent_gui.class_manager.stop_class_execution()
                        # Wait a bit for the class to stop
                        import time
                        time.sleep(1)
                    self.is_class_running = False
                    self.current_class_name = None
                    self.clear_progress_display()
                else:  # No - cancel
                    return
            else:
                # No class running, confirm execution normally
                if not messagebox.askyesno("Confirmar Ejecución", 
                                         f"¿Ejecutar la clase '{class_title}'?"):
                    return
            
            self.update_status(f"🚀 Ejecutando {class_title}...")
            
            # Execute class
            if hasattr(self.parent_gui, 'class_manager') and self.parent_gui.class_manager:
                success = self.parent_gui.class_manager.execute_class(class_name)
                
                if success:
                    self.update_status(f"✅ {class_title} iniciada")
                    self.is_class_running = True
                    self.current_class_name = class_name
                    self.update_control_buttons(True)
                    messagebox.showinfo("Éxito", f"Clase '{class_title}' iniciada correctamente")
                else:
                    self.update_status(f"❌ Error ejecutando {class_title}")
                    messagebox.showerror("Error", f"Error ejecutando la clase '{class_title}'")
            else:
                self.update_status("❌ Class Manager no disponible")
                messagebox.showerror("Error", "Class Manager no está disponible")
                
        except Exception as e:
            self.update_status(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error ejecutando clase: {e}")
    
    def pause_current_class(self):
        """Pause the currently running class"""
        try:
            if not self.is_class_running or not self.current_class_name:
                messagebox.showwarning("Sin clase activa", "No hay ninguna clase ejecutándose")
                return
            
            # Pause class using progress manager
            if hasattr(self.parent_gui, 'class_manager') and self.parent_gui.class_manager:
                if hasattr(self.parent_gui.class_manager, 'progress_manager') and self.parent_gui.class_manager.progress_manager:
                    self.parent_gui.class_manager.progress_manager.pause_class()
                    self.update_status("⏸️ Clase pausada")
                    messagebox.showinfo("Pausada", "La clase ha sido pausada")
                else:
                    self.update_status("❌ Progress Manager no disponible")
                    messagebox.showerror("Error", "Progress Manager no está disponible")
            else:
                self.update_status("❌ Class Manager no disponible")
                messagebox.showerror("Error", "Class Manager no está disponible")
                
        except Exception as e:
            self.update_status(f"❌ Error pausando: {e}")
            messagebox.showerror("Error", f"Error pausando la clase: {e}")
    
    def resume_current_class(self):
        """Resume the currently paused class"""
        try:
            if not self.is_class_running or not self.current_class_name:
                messagebox.showwarning("Sin clase activa", "No hay ninguna clase ejecutándose")
                return
            
            # Resume class using progress manager
            if hasattr(self.parent_gui, 'class_manager') and self.parent_gui.class_manager:
                if hasattr(self.parent_gui.class_manager, 'progress_manager') and self.parent_gui.class_manager.progress_manager:
                    self.parent_gui.class_manager.progress_manager.resume_class()
                    self.update_status("▶️ Clase reanudada")
                    messagebox.showinfo("Reanudada", "La clase ha sido reanudada")
                else:
                    self.update_status("❌ Progress Manager no disponible")
                    messagebox.showerror("Error", "Progress Manager no está disponible")
            else:
                self.update_status("❌ Class Manager no disponible")
                messagebox.showerror("Error", "Class Manager no está disponible")
                
        except Exception as e:
            self.update_status(f"❌ Error reanudando: {e}")
            messagebox.showerror("Error", f"Error reanudando la clase: {e}")
    
    def stop_current_class(self):
        """Stop the currently running class"""
        try:
            if not self.is_class_running or not self.current_class_name:
                messagebox.showwarning("Sin clase activa", "No hay ninguna clase ejecutándose")
                return
            
            # Confirm stop
            if not messagebox.askyesno("Confirmar Detención", 
                                     f"¿Detener la clase '{self.current_class_name}'?\n\nEsta acción detendrá completamente la ejecución."):
                return
            
            # Stop class
            if hasattr(self.parent_gui, 'class_manager') and self.parent_gui.class_manager:
                success = self.parent_gui.class_manager.stop_class_execution()
                
                if success:
                    self.update_status("⏹️ Clase detenida")
                    self.is_class_running = False
                    self.current_class_name = None
                    self.update_control_buttons(False)
                    self.clear_progress_display()
                    messagebox.showinfo("Detenida", "La clase ha sido detenida correctamente")
                else:
                    self.update_status("❌ Error deteniendo la clase")
                    messagebox.showerror("Error", "Error deteniendo la clase")
            else:
                self.update_status("❌ Class Manager no disponible")
                messagebox.showerror("Error", "Class Manager no está disponible")
                
        except Exception as e:
            self.update_status(f"❌ Error deteniendo: {e}")
            messagebox.showerror("Error", f"Error deteniendo la clase: {e}")

    def refresh_classes(self):
        """Refresh the list of available classes"""
        try:
            self.update_status("🔄 Refrescando clases...")
            
            # Get classes from class manager
            if hasattr(self.parent_gui, 'class_manager') and self.parent_gui.class_manager:
                self.classes_list = self.parent_gui.class_manager.refresh_classes()
            else:
                self.classes_list = []
            
            # Clear listbox
            self.classes_listbox.delete(0, tk.END)
            
            # Add classes to listbox
            for cls in self.classes_list:
                display_text = f"{cls.get('title', 'Sin título')} ({cls.get('subject', 'Sin materia')})"
                self.classes_listbox.insert(tk.END, display_text)
            
            self.update_status(f"✅ {len(self.classes_list)} clases cargadas")
            
        except Exception as e:
            self.update_status(f"❌ Error refrescando: {e}")
            print(f"Error refreshing classes: {e}")
    
    def on_class_select(self, event):
        """Handle class selection in listbox"""
        try:
            selection = self.classes_listbox.curselection()
            if selection:
                index = selection[0]
                if index < len(self.classes_list):
                    self.selected_class = self.classes_list[index]
                    self.show_class_details()
                else:
                    self.selected_class = None
                    self.clear_details()
            else:
                self.selected_class = None
                self.clear_details()
        except Exception as e:
            print(f"Error selecting class: {e}")
    
    def show_class_details(self):
        """Show details of selected class"""
        try:
            if not self.selected_class:
                self.clear_details()
                return
            
            # Clear details text
            self.details_text.delete(1.0, tk.END)
            
            # Format class details
            details = f"""📚 Título: {self.selected_class.get('title', 'Sin título')}
📖 Materia: {self.selected_class.get('subject', 'Sin materia')}
📝 Descripción: {self.selected_class.get('description', 'Sin descripción')}
⏱️ Duración: {self.selected_class.get('duration', 'Sin especificar')}
📁 Archivo: {self.selected_class.get('name', 'Sin nombre')}
📅 Creada: {self.selected_class.get('created_at', 'Sin fecha')}
📊 Tamaño: {self.selected_class.get('size', 0)} bytes
🔄 Modificada: {self.selected_class.get('modified', 'Sin fecha')}"""
            
            self.details_text.insert(1.0, details)
            
            # Enable action buttons - execute always enabled now
            self.execute_btn.config(state="normal")
            self.delete_btn.config(state="normal")
            
        except Exception as e:
            print(f"Error showing class details: {e}")
    
    def clear_details(self):
        """Clear class details"""
        self.details_text.delete(1.0, tk.END)
        # Don't disable execute button - it should always be available
        self.delete_btn.config(state="disabled")
    
    def delete_selected_class(self):
        """Delete the selected class"""
        try:
            if not self.selected_class:
                messagebox.showwarning("Sin selección", "Por favor selecciona una clase")
                return
            
            class_name = self.selected_class.get('name')
            class_title = self.selected_class.get('title', 'Clase')
            
            # Check if class is currently running
            if self.is_class_running and self.current_class_name == class_name:
                messagebox.showwarning("Clase en ejecución", 
                                     f"No se puede eliminar la clase '{class_title}' mientras está ejecutándose.\n\nDetén la clase primero.")
                return
            
            # Confirm deletion
            if not messagebox.askyesno("Confirmar Eliminación", 
                                     f"¿Eliminar la clase '{class_title}'?\n\nEsta acción no se puede deshacer."):
                return
            
            self.update_status(f"🗑️ Eliminando {class_title}...")
            
            # Delete class
            if hasattr(self.parent_gui, 'class_manager') and self.parent_gui.class_manager:
                success = self.parent_gui.class_manager.delete_class(class_name)
                
                if success:
                    self.update_status(f"✅ {class_title} eliminada")
                    messagebox.showinfo("Éxito", f"Clase '{class_title}' eliminada correctamente")
                    self.refresh_classes()
                    self.clear_details()
                else:
                    self.update_status(f"❌ Error eliminando {class_title}")
                    messagebox.showerror("Error", f"Error eliminando la clase '{class_title}'")
            else:
                self.update_status("❌ Class Manager no disponible")
                messagebox.showerror("Error", "Class Manager no está disponible")
                
        except Exception as e:
            self.update_status(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error eliminando clase: {e}")
    
    def update_status(self, message):
        """Update status label"""
        try:
            self.status_label.config(text=message)
            
            # Color coding
            if "✅" in message:
                self.status_label.config(fg='#4CAF50')
            elif "❌" in message:
                self.status_label.config(fg='#f44336')
            elif "🔄" in message:
                self.status_label.config(fg='#2196F3')
            elif "🚀" in message:
                self.status_label.config(fg='#FF9800')
            elif "⏸️" in message:
                self.status_label.config(fg='#FF9800')
            elif "▶️" in message:
                self.status_label.config(fg='#2196F3')
            elif "⏹️" in message:
                self.status_label.config(fg='#f44336')
            else:
                self.status_label.config(fg='#ffffff')
                
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def start_auto_refresh(self):
        """Start automatic refresh timer"""
        try:
            # Cancel existing timer
            if self.refresh_timer:
                self.parent_gui.root.after_cancel(self.refresh_timer)
            
            # Schedule next refresh (30 seconds)
            self.refresh_timer = self.parent_gui.root.after(30000, self.auto_refresh)
            
        except Exception as e:
            print(f"Error starting auto refresh: {e}")
    
    def auto_refresh(self):
        """Auto refresh classes list"""
        try:
            self.refresh_classes()
            # Schedule next refresh
            self.start_auto_refresh()
        except Exception as e:
            print(f"Error in auto refresh: {e}")
    
    def on_resize(self, width, height):
        """Handle window resize"""
        try:
            # Update responsive elements if needed
            pass
        except Exception as e:
            print(f"Error in resize handler: {e}")
    
    def cleanup(self):
        """Cleanup resources when tab is destroyed"""
        try:
            # Cancel timers
            if self.refresh_timer:
                self.parent_gui.root.after_cancel(self.refresh_timer)
            if self.progress_update_timer:
                self.parent_gui.root.after_cancel(self.progress_update_timer)
        except Exception as e:
            print(f"Error in cleanup: {e}")
