# -*- coding: utf-8 -*-
"""
Simulator Tab for RobotGUI - Robot Arms Simulator
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .base_tab import BaseTab
import time
import threading

class SimulatorTab(BaseTab):
    """Robot arms simulator tab"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "🦾 Simulador"
        
        # Initialize simulator variables
        self.arms_canvas = None
        self.arms_canvas_size = (800, 600)
        self.arms_update_interval = 50  # ms
        self.arms_history = []
        self.arms_tracking_enabled = tk.BooleanVar(value=True)
        self.arms_show_trajectory = tk.BooleanVar(value=True)
        self.arms_real_time_update = tk.BooleanVar(value=True)
        
        # 3D visualization variables
        self.arms_fig = None
        self.arms_ax = None
        self.arms_canvas_widget = None
        self.arms_3d_enabled = True
        
        # Robot arms state tracking
        self.robot_arms_state = {
            'left_arm': {
                'brazo_izq': 100,   # BI - Brazo Izquierdo (M7)
                'frente_izq': 95,   # FI - Frente Izquierdo (M6)
                'high_izq': 140,    # HI - High Izquierdo (M8)
                'pollo_izq': 90     # PI - Pollo Izquierdo (M5)
            },
            'right_arm': {
                'brazo_der': 30,    # BD - Brazo Derecho (M3)
                'frente_der': 160,  # FD - Frente Derecho (M2)
                'high_der': 165,    # HD - High Derecho (M4)
                'pollo_der': 100    # PD - Pollo Derecho (M1)
            },
            'timestamp': time.time()
        }
        
        # Labels for status display
        self.left_arm_labels = {}
        self.right_arm_labels = {}
        
    def setup_tab_content(self):
        """Setup the simulator tab content"""
        # Title for simulator tab
        simulator_title = tk.Label(self.tab_frame, text="Simulador de Brazos del Robot", 
                                  font=('Arial', 18, 'bold'), 
                                  bg='#1e1e1e', fg='#ffffff')
        simulator_title.pack(pady=(10, 20))
        
        # Main content area
        main_content = tk.Frame(self.tab_frame, bg='#1e1e1e')
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Top controls panel
        controls_frame = tk.LabelFrame(main_content, text="Controles del Simulador", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Controls content
        controls_content = tk.Frame(controls_frame, bg='#2d2d2d')
        controls_content.pack(fill="x", padx=10, pady=10)
        
        # Control buttons row 1
        buttons_row1 = tk.Frame(controls_content, bg='#2d2d2d')
        buttons_row1.pack(fill="x", pady=5)
        
        tk.Checkbutton(buttons_row1, text="Rastreo Activo", variable=self.arms_tracking_enabled,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#4CAF50',
                      font=('Arial', 12), command=self.toggle_arms_tracking).pack(side="left", padx=10)
        
        tk.Checkbutton(buttons_row1, text="Mostrar Trayectoria", variable=self.arms_show_trajectory,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#4CAF50',
                      font=('Arial', 12), command=self.update_arms_display).pack(side="left", padx=10)
        
        tk.Checkbutton(buttons_row1, text="Actualización en Tiempo Real", variable=self.arms_real_time_update,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#4CAF50',
                      font=('Arial', 12)).pack(side="left", padx=10)
        
        # Control buttons row 2
        buttons_row2 = tk.Frame(controls_content, bg='#2d2d2d')
        buttons_row2.pack(fill="x", pady=5)
        
        tk.Button(buttons_row2, text="Limpiar Historial", bg='#f44336', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.clear_arms_history).pack(side="left", padx=10)
        
        tk.Button(buttons_row2, text="Posición de Descanso", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.set_arms_rest_position).pack(side="left", padx=10)
        
        tk.Button(buttons_row2, text="Centrar Vista", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.center_arms_view).pack(side="left", padx=10)
        
        # Simulator canvas area
        canvas_frame = tk.LabelFrame(main_content, text="Visualización de Brazos 3D", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        canvas_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create 3D matplotlib figure
        if self.check_matplotlib_available():
            self.setup_3d_arms_plot(canvas_frame)
        else:
            # Fallback to 2D canvas if matplotlib not available
            self.arms_canvas = tk.Canvas(canvas_frame, bg='#1e1e1e', 
                                       width=self.arms_canvas_size[0], 
                                       height=self.arms_canvas_size[1])
            self.arms_canvas.pack(padx=10, pady=10)
        
        # Status panel
        status_frame = tk.LabelFrame(main_content, text="Estado de los Brazos", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        status_frame.pack(fill="x")
        
        # Status content
        status_content = tk.Frame(status_frame, bg='#2d2d2d')
        status_content.pack(fill="x", padx=10, pady=10)
        
        # Left arm status
        left_arm_frame = tk.Frame(status_content, bg='#2d2d2d')
        left_arm_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        tk.Label(left_arm_frame, text="Brazo Izquierdo", bg='#2d2d2d', fg='#4CAF50',
                font=('Arial', 12, 'bold')).pack()
        
        for servo in ['brazo_izq', 'frente_izq', 'high_izq', 'pollo_izq']:
            label = tk.Label(left_arm_frame, text=f"{servo}: 0°", bg='#2d2d2d', fg='#ffffff',
                           font=('Arial', 10))
            label.pack()
            self.left_arm_labels[servo] = label
        
        # Right arm status
        right_arm_frame = tk.Frame(status_content, bg='#2d2d2d')
        right_arm_frame.pack(side="right", fill="x", expand=True, padx=10)
        
        tk.Label(right_arm_frame, text="Brazo Derecho", bg='#2d2d2d', fg='#2196F3',
                font=('Arial', 12, 'bold')).pack()
        
        for servo in ['brazo_der', 'frente_der', 'high_der', 'pollo_der']:
            label = tk.Label(right_arm_frame, text=f"{servo}: 0°", bg='#2d2d2d', fg='#ffffff',
                           font=('Arial', 10))
            label.pack()
            self.right_arm_labels[servo] = label
        
        # Start arms update timer if tracking is enabled
        if self.arms_tracking_enabled.get():
            self.start_arms_tracking()
    
    def check_matplotlib_available(self):
        """Check if matplotlib is available for 3D visualization"""
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            return True
        except ImportError:
            return False
    
    def setup_3d_arms_plot(self, parent):
        """Setup 3D matplotlib plot for arms visualization"""
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib
            matplotlib.use('TkAgg')
            
            # Create figure and 3D axis
            self.arms_fig = plt.figure(figsize=(10, 8))
            self.arms_ax = self.arms_fig.add_subplot(111, projection='3d')
            
            # Create canvas widget
            self.arms_canvas_widget = FigureCanvasTkAgg(self.arms_fig, parent)
            self.arms_canvas_widget.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
            # Initial plot
            self.update_arms_3d_plot()
            
        except Exception as e:
            self.log_message(f"Error setting up 3D plot: {e}")
            # Fallback to 2D canvas
            self.arms_3d_enabled = False
            self.arms_canvas = tk.Canvas(parent, bg='#1e1e1e', 
                                       width=self.arms_canvas_size[0], 
                                       height=self.arms_canvas_size[1])
            self.arms_canvas.pack(padx=10, pady=10)
    
    def update_arms_3d_plot(self):
        """Update the 3D arms plot"""
        if not self.arms_3d_enabled or self.arms_ax is None:
            return
            
        try:
            # Clear previous plot
            self.arms_ax.clear()
            
            # Get current arm positions
            left_arm = self.robot_arms_state['left_arm']
            right_arm = self.robot_arms_state['right_arm']
            
            # Draw left arm (simplified 3D representation)
            left_x = [0, -50, -100, -150]
            left_y = [0, 0, 0, 0]
            left_z = [0, left_arm['high_izq'], left_arm['frente_izq'], left_arm['brazo_izq']]
            
            self.arms_ax.plot(left_x, left_y, left_z, 'b-', linewidth=3, label='Left Arm')
            self.arms_ax.scatter(left_x, left_y, left_z, c='blue', s=50)
            
            # Draw right arm
            right_x = [0, 50, 100, 150]
            right_y = [0, 0, 0, 0]
            right_z = [0, right_arm['high_der'], right_arm['frente_der'], right_arm['brazo_der']]
            
            self.arms_ax.plot(right_x, right_y, right_z, 'r-', linewidth=3, label='Right Arm')
            self.arms_ax.scatter(right_x, right_y, right_z, c='red', s=50)
            
            # Set labels and title
            self.arms_ax.set_xlabel('X')
            self.arms_ax.set_ylabel('Y')
            self.arms_ax.set_zlabel('Z')
            self.arms_ax.set_title('Robot Arms 3D Visualization')
            self.arms_ax.legend()
            
            # Set view limits
            self.arms_ax.set_xlim(-200, 200)
            self.arms_ax.set_ylim(-50, 50)
            self.arms_ax.set_zlim(0, 200)
            
            # Update canvas
            if self.arms_canvas_widget:
                self.arms_canvas_widget.draw()
                
        except Exception as e:
            self.log_message(f"Error updating 3D plot: {e}")
    
    def toggle_arms_tracking(self):
        """Toggle arms tracking on/off"""
        if self.arms_tracking_enabled.get():
            self.start_arms_tracking()
            self.log_message("Arms tracking enabled")
        else:
            self.stop_arms_tracking()
            self.log_message("Arms tracking disabled")
    
    def start_arms_tracking(self):
        """Start arms tracking timer"""
        if not hasattr(self, 'arms_tracking_active') or not self.arms_tracking_active:
            self.arms_tracking_active = True
            self.update_arms_position()
    
    def stop_arms_tracking(self):
        """Stop arms tracking timer"""
        self.arms_tracking_active = False
    
    def update_arms_position(self):
        """Update arms position (called by timer)"""
        if not self.arms_tracking_active:
            return
            
        try:
            # Simulate arm movement (in real implementation, this would get data from ESP32)
            import math
            current_time = time.time()
            
            # Update left arm positions with some movement
            self.robot_arms_state['left_arm']['brazo_izq'] = 100 + 5 * math.sin(current_time * 0.5)
            self.robot_arms_state['left_arm']['frente_izq'] = 95 + 10 * math.sin(current_time * 0.3)
            self.robot_arms_state['left_arm']['high_izq'] = 140 + 5 * math.cos(current_time * 0.4)
            self.robot_arms_state['left_arm']['pollo_izq'] = 90 + 3 * math.sin(current_time * 0.6)

            # Update right arm positions
            self.robot_arms_state['right_arm']['brazo_der'] = 30 + 8 * math.sin(current_time * 0.6)
            self.robot_arms_state['right_arm']['frente_der'] = 160 + 12 * math.sin(current_time * 0.2)
            self.robot_arms_state['right_arm']['high_der'] = 165 + 6 * math.cos(current_time * 0.5)
            self.robot_arms_state['right_arm']['pollo_der'] = 100 + 3 * math.sin(current_time * 0.7)
            
            self.robot_arms_state['timestamp'] = current_time
            
            # Update display
            self.update_arms_display()
            
            # Schedule next update
            if self.arms_tracking_active:
                self.tab_frame.after(self.arms_update_interval, self.update_arms_position)
                
        except Exception as e:
            self.log_message(f"Error updating arms position: {e}")
    
    def update_arms_display(self):
        """Update the arms display"""
        try:
            # Update 3D plot if available
            if self.arms_3d_enabled:
                self.update_arms_3d_plot()
            
            # Update status labels
            left_arm = self.robot_arms_state['left_arm']
            right_arm = self.robot_arms_state['right_arm']
            
            for servo, value in left_arm.items():
                if servo in self.left_arm_labels:
                    self.left_arm_labels[servo].config(text=f"{servo}: {value:.1f}°")
            
            for servo, value in right_arm.items():
                if servo in self.right_arm_labels:
                    self.right_arm_labels[servo].config(text=f"{servo}: {value:.1f}°")
            
            # Add to history if trajectory is enabled
            if self.arms_show_trajectory.get():
                self.arms_history.append(self.robot_arms_state.copy())
                if len(self.arms_history) > 100:  # Keep last 100 positions
                    self.arms_history.pop(0)
                    
        except Exception as e:
            self.log_message(f"Error updating arms display: {e}")
    
    def clear_arms_history(self):
        """Clear arms movement history"""
        self.arms_history.clear()
        self.log_message("Arms history cleared")
    
    def set_arms_rest_position(self):
        """Set arms to rest position"""
        try:
            # Set rest positions
            self.robot_arms_state['left_arm'] = {
                'brazo_izq': 0,
                'frente_izq': 0,
                'high_izq': 0
            }
            
            self.robot_arms_state['right_arm'] = {
                'brazo_der': 0,
                'frente_der': 0,
                'high_der': 0,
                'pollo_der': 0
            }
            
            self.update_arms_display()
            self.log_message("Arms set to rest position")
            
        except Exception as e:
            self.log_message(f"Error setting rest position: {e}")
    
    def center_arms_view(self):
        """Center the arms view"""
        try:
            if self.arms_3d_enabled and self.arms_ax:
                self.arms_ax.view_init(elev=20, azim=45)
                if self.arms_canvas_widget:
                    self.arms_canvas_widget.draw()
            
            self.log_message("Arms view centered")
            
        except Exception as e:
            self.log_message(f"Error centering view: {e}")
    
    def get_arms_state(self):
        """Get current arms state"""
        return self.robot_arms_state.copy()
    
    def set_arms_state(self, new_state):
        """Set arms state from external source"""
        try:
            if 'left_arm' in new_state:
                self.robot_arms_state['left_arm'].update(new_state['left_arm'])
            if 'right_arm' in new_state:
                self.robot_arms_state['right_arm'].update(new_state['right_arm'])
            
            self.update_arms_display()
            
        except Exception as e:
            self.log_message(f"Error setting arms state: {e}")
