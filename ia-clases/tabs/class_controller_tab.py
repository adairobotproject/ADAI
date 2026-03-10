# -*- coding: utf-8 -*-
"""
Class Controller Tab for RobotGUI - Class and Sequence Controller
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .base_tab import BaseTab
import threading
import time

# Import progress widget
try:
    from .class_progress_widget import ClassProgressWidget
    PROGRESS_WIDGET_AVAILABLE = True
except ImportError:
    PROGRESS_WIDGET_AVAILABLE = False
    print("⚠️ Progress Widget no disponible")

class ClassControllerTab(BaseTab):
    """Class and sequence controller tab"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "🎓 Class Controller"
        
        # Initialize controller variables
        self.current_class = None
        self.class_running = False
        self.current_sequence = []
        self.sequence_position = 0
        
        # UI components
        self.class_status_label = None
        self.progress_bar = None
        self.sequence_listbox = None
        self.control_buttons = {}
        
        # Progress widget
        self.progress_widget = None
        
    def setup_tab_content(self):
        """Setup the class controller tab content"""
        # Title
        title = tk.Label(self.tab_frame, text="🎓 Controlador de Clases y Secuencias", 
                        font=('Arial', 18, 'bold'), 
                        bg='#1e1e1e', fg='#ffffff')
        title.pack(pady=(10, 20))
        
        # Main content area
        main_content = tk.Frame(self.tab_frame, bg='#1e1e1e')
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Class Control
        self.setup_class_control(main_content)
        
        # Right panel - Sequence Control
        self.setup_sequence_control(main_content)
        
        # Bottom panel - Status and Progress
        self.setup_status_panel(main_content)
        
    def setup_class_control(self, parent):
        """Setup class control panel"""
        left_panel = tk.LabelFrame(parent, text="Control de Clases", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Class selection
        selection_frame = tk.Frame(left_panel, bg='#2d2d2d')
        selection_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(selection_frame, text="Clase Actual:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        self.class_var = tk.StringVar(value="Ninguna clase seleccionada")
        class_combo = ttk.Combobox(selection_frame, textvariable=self.class_var,
                                  values=["Robots Médicos", "Exoesqueletos", "IoMT", "Robótica Industrial"], 
                                  state="readonly")
        class_combo.pack(fill="x", pady=(5, 15))
        class_combo.bind('<<ComboboxSelected>>', self.on_class_selected)
        
        # Class controls
        controls_frame = tk.Frame(left_panel, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        self.control_buttons['start'] = tk.Button(controls_frame, text="▶️ Iniciar Clase", 
                                                 bg='#4CAF50', fg='#ffffff',
                                                 font=('Arial', 12, 'bold'), 
                                                 command=self.start_class)
        self.control_buttons['start'].pack(fill="x", pady=2)
        
        self.control_buttons['pause'] = tk.Button(controls_frame, text="⏸️ Pausar", 
                                                 bg='#FF9800', fg='#ffffff',
                                                 font=('Arial', 12, 'bold'), 
                                                 command=self.pause_class)
        self.control_buttons['pause'].pack(fill="x", pady=2)
        
        self.control_buttons['stop'] = tk.Button(controls_frame, text="⏹️ Detener", 
                                                bg='#f44336', fg='#ffffff',
                                                font=('Arial', 12, 'bold'), 
                                                command=self.stop_class)
        self.control_buttons['stop'].pack(fill="x", pady=2)
        
        self.control_buttons['emergency'] = tk.Button(controls_frame, text="🚨 EMERGENCIA", 
                                                     bg='#FF0000', fg='#ffffff',
                                                     font=('Arial', 12, 'bold'), 
                                                     command=self.emergency_stop)
        self.control_buttons['emergency'].pack(fill="x", pady=(10, 2))
        
        # Class parameters
        params_frame = tk.LabelFrame(left_panel, text="Parámetros de Clase", 
                                   font=('Arial', 11, 'bold'),
                                   bg='#3d3d3d', fg='#ffffff')
        params_frame.pack(fill="x", padx=10, pady=10)
        
        params_content = tk.Frame(params_frame, bg='#3d3d3d')
        params_content.pack(fill="x", padx=10, pady=10)
        
        # Speed control
        tk.Label(params_content, text="Velocidad:", bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(anchor="w")
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = tk.Scale(params_content, from_=0.5, to=2.0, resolution=0.1,
                              variable=self.speed_var, orient="horizontal",
                              bg='#3d3d3d', fg='#ffffff', highlightthickness=0)
        speed_scale.pack(fill="x", pady=(5, 10))
        
        # Auto mode
        self.auto_mode_var = tk.BooleanVar(value=True)
        tk.Checkbutton(params_content, text="Modo Automático", 
                      variable=self.auto_mode_var, bg='#3d3d3d', fg='#ffffff', 
                      selectcolor='#4CAF50', font=('Arial', 10)).pack(anchor="w")
        
    def setup_sequence_control(self, parent):
        """Setup sequence control panel"""
        right_panel = tk.LabelFrame(parent, text="Control de Secuencias", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Current sequence display
        sequence_frame = tk.Frame(right_panel, bg='#2d2d2d')
        sequence_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(sequence_frame, text="Secuencia Actual:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        # Sequence listbox
        list_frame = tk.Frame(sequence_frame, bg='#2d2d2d')
        list_frame.pack(fill="both", expand=True, pady=(5, 10))
        
        self.sequence_listbox = tk.Listbox(list_frame, bg='#3d3d3d', fg='#ffffff',
                                         font=('Arial', 10), selectbackground='#4CAF50')
        seq_scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.sequence_listbox.config(yscrollcommand=seq_scrollbar.set)
        seq_scrollbar.config(command=self.sequence_listbox.yview)
        
        self.sequence_listbox.pack(side="left", fill="both", expand=True)
        seq_scrollbar.pack(side="right", fill="y")
        
        # Sequence controls
        seq_controls = tk.Frame(sequence_frame, bg='#2d2d2d')
        seq_controls.pack(fill="x")
        
        tk.Button(seq_controls, text="⏮️ Anterior", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.previous_step).pack(side="left", padx=(0, 5))
        
        tk.Button(seq_controls, text="⏯️ Paso", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.next_step).pack(side="left", padx=5)
        
        tk.Button(seq_controls, text="⏭️ Siguiente", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.skip_step).pack(side="left", padx=5)
        
        tk.Button(seq_controls, text="🔄 Repetir", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.repeat_step).pack(side="left", padx=5)
        
    def setup_status_panel(self, parent):
        """Setup status and progress panel"""
        status_panel = tk.LabelFrame(parent, text="Estado y Progreso", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        status_panel.pack(fill="x", pady=(10, 0))
        
        status_content = tk.Frame(status_panel, bg='#2d2d2d')
        status_content.pack(fill="x", padx=10, pady=10)
        
        # Status label
        self.class_status_label = tk.Label(status_content, text="Estado: Listo", 
                                         bg='#2d2d2d', fg='#4CAF50', 
                                         font=('Arial', 12, 'bold'))
        self.class_status_label.pack(anchor="w", pady=(0, 10))
        
        # Progress widget (if available)
        if PROGRESS_WIDGET_AVAILABLE and hasattr(self.parent_gui, 'class_manager'):
            try:
                self.progress_widget = ClassProgressWidget(status_content, self.parent_gui.class_manager)
            except Exception as e:
                print(f"Error creando progress widget: {e}")
        
        # Progress bar (fallback)
        progress_frame = tk.Frame(status_content, bg='#2d2d2d')
        progress_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(progress_frame, text="Progreso:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill="x", pady=(5, 0))
        
        # Statistics
        stats_frame = tk.Frame(status_content, bg='#2d2d2d')
        stats_frame.pack(fill="x")
        
        self.stats_labels = {}
        stats_data = [
            ("Tiempo Transcurrido", "elapsed_time"),
            ("Paso Actual", "current_step"),
            ("Pasos Totales", "total_steps"),
            ("Tiempo Estimado", "estimated_time")
        ]
        
        for i, (label_text, key) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(stats_frame, bg='#2d2d2d')
            stat_frame.grid(row=row, column=col, sticky="ew", padx=(0, 10), pady=2)
            
            tk.Label(stat_frame, text=f"{label_text}:", bg='#2d2d2d', fg='#ffffff',
                    font=('Arial', 10)).pack(side="left")
            
            value_label = tk.Label(stat_frame, text="--", bg='#2d2d2d', fg='#4CAF50',
                                 font=('Arial', 10, 'bold'))
            value_label.pack(side="right")
            
            self.stats_labels[key] = value_label
        
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        
    def on_class_selected(self, event=None):
        """Handle class selection"""
        selected_class = self.class_var.get()
        self.current_class = selected_class
        
        # Load sequence for selected class
        self.load_class_sequence(selected_class)
        self.update_status(f"Clase seleccionada: {selected_class}")
        
    def load_class_sequence(self, class_name):
        """Load sequence for the selected class"""
        # Sample sequences for different classes
        sequences = {
            "Robots Médicos": [
                "1. Introducción a robots médicos",
                "2. Mostrar QR de evaluación diagnóstica",
                "3. Explicar tipos de robots médicos",
                "4. Demostración práctica",
                "5. Preguntas y respuestas",
                "6. Mostrar QR de examen final"
            ],
            "Exoesqueletos": [
                "1. Introducción a exoesqueletos",
                "2. Evaluación diagnóstica",
                "3. Tipos de exoesqueletos",
                "4. Aplicaciones médicas",
                "5. Demostración",
                "6. Evaluación final"
            ],
            "IoMT": [
                "1. Internet of Medical Things",
                "2. Evaluación inicial",
                "3. Conceptos básicos IoMT",
                "4. Casos de uso",
                "5. Tecnologías involucradas",
                "6. Examen final"
            ]
        }
        
        self.current_sequence = sequences.get(class_name, ["Sin secuencia definida"])
        self.sequence_position = 0
        
        # Update sequence listbox
        self.sequence_listbox.delete(0, tk.END)
        for i, step in enumerate(self.current_sequence):
            self.sequence_listbox.insert(tk.END, step)
            
        # Update statistics
        self.stats_labels['total_steps'].config(text=str(len(self.current_sequence)))
        self.stats_labels['current_step'].config(text="0")
        
    def start_class(self):
        """Start the selected class"""
        if not self.current_class:
            messagebox.showwarning("Sin Clase", "Por favor selecciona una clase primero")
            return
            
        if self.class_running:
            messagebox.showinfo("Clase en Ejecución", "Ya hay una clase ejecutándose")
            return
            
        self.class_running = True
        self.sequence_position = 0
        self.update_status("Estado: Ejecutando clase...")
        
        # Update button states
        self.control_buttons['start'].config(state='disabled')
        self.control_buttons['pause'].config(state='normal')
        self.control_buttons['stop'].config(state='normal')
        
        # Start class execution in background
        if self.auto_mode_var.get():
            threading.Thread(target=self.run_class_automatically, daemon=True).start()
        
        self.log_message(f"Clase iniciada: {self.current_class}")
        
    def pause_class(self):
        """Pause the current class"""
        if self.class_running:
            self.class_running = False
            self.update_status("Estado: Pausado")
            self.control_buttons['start'].config(state='normal', text="▶️ Reanudar")
            self.log_message("Clase pausada")
        
    def stop_class(self):
        """Stop the current class"""
        self.class_running = False
        self.sequence_position = 0
        self.update_status("Estado: Detenido")
        
        # Reset button states
        self.control_buttons['start'].config(state='normal', text="▶️ Iniciar Clase")
        self.control_buttons['pause'].config(state='disabled')
        self.control_buttons['stop'].config(state='disabled')
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.stats_labels['current_step'].config(text="0")
        
        self.log_message("Clase detenida")
        
    def emergency_stop(self):
        """Emergency stop - immediately halt all operations"""
        self.stop_class()
        self.update_status("Estado: PARADA DE EMERGENCIA")
        self.log_message("🚨 PARADA DE EMERGENCIA ACTIVADA")
        messagebox.showwarning("Emergencia", "Parada de emergencia activada")
        
    def run_class_automatically(self):
        """Run class automatically in background"""
        start_time = time.time()
        
        while self.class_running and self.sequence_position < len(self.current_sequence):
            # Update current step
            self.root.after(0, lambda: self.stats_labels['current_step'].config(
                text=str(self.sequence_position + 1)))
            
            # Update progress
            progress = ((self.sequence_position + 1) / len(self.current_sequence)) * 100
            self.root.after(0, lambda p=progress: setattr(self.progress_bar, 'value', p))
            
            # Update elapsed time
            elapsed = int(time.time() - start_time)
            self.root.after(0, lambda e=elapsed: self.stats_labels['elapsed_time'].config(
                text=f"{e//60}:{e%60:02d}"))
            
            # Simulate step execution time
            step_duration = 5.0 / self.speed_var.get()  # Base 5 seconds, adjusted by speed
            time.sleep(step_duration)
            
            self.sequence_position += 1
            
        # Class completed
        if self.class_running:
            self.root.after(0, self.on_class_completed)
            
    def on_class_completed(self):
        """Handle class completion"""
        self.class_running = False
        self.update_status("Estado: Clase completada")
        self.progress_bar['value'] = 100
        
        # Reset button states
        self.control_buttons['start'].config(state='normal', text="▶️ Iniciar Clase")
        self.control_buttons['pause'].config(state='disabled')
        self.control_buttons['stop'].config(state='disabled')
        
        self.log_message("✅ Clase completada exitosamente")
        messagebox.showinfo("Completado", "¡Clase completada exitosamente!")
        
    def next_step(self):
        """Move to next step manually"""
        if self.sequence_position < len(self.current_sequence):
            self.sequence_position += 1
            self.stats_labels['current_step'].config(text=str(self.sequence_position))
            
            progress = (self.sequence_position / len(self.current_sequence)) * 100
            self.progress_bar['value'] = progress
            
            self.log_message(f"Avanzado al paso {self.sequence_position}")
            
    def previous_step(self):
        """Move to previous step"""
        if self.sequence_position > 0:
            self.sequence_position -= 1
            self.stats_labels['current_step'].config(text=str(self.sequence_position))
            
            progress = (self.sequence_position / len(self.current_sequence)) * 100
            self.progress_bar['value'] = progress
            
            self.log_message(f"Retrocedido al paso {self.sequence_position}")
            
    def skip_step(self):
        """Skip current step"""
        self.next_step()
        self.log_message("Paso omitido")
        
    def repeat_step(self):
        """Repeat current step"""
        self.log_message(f"Repitiendo paso {self.sequence_position}")
        
    def update_status(self, status_text):
        """Update status label"""
        if self.class_status_label:
            self.class_status_label.config(text=status_text)
            
            # Color coding
            if "Ejecutando" in status_text:
                self.class_status_label.config(fg='#4CAF50')
            elif "Pausado" in status_text:
                self.class_status_label.config(fg='#FF9800')
            elif "Detenido" in status_text or "EMERGENCIA" in status_text:
                self.class_status_label.config(fg='#f44336')
            elif "Completado" in status_text:
                self.class_status_label.config(fg='#2196F3')
            else:
                self.class_status_label.config(fg='#ffffff')
