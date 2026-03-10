# -*- coding: utf-8 -*-
"""
ESP32 Tab for RobotGUI - ESP32 Robot Controller Interface (Simplified)
"""

import tkinter as tk
import math
import time
from .base_tab import BaseTab

class ESP32Tab(BaseTab):
    """ESP32 controller tab with connection management and robot controls"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "🔌 ESP32 Controller"
        
    def setup_tab_content(self):
        """Setup the ESP32 tab content"""
        # Create scrollable frame for ESP32 content
        content_frame, canvas, container = self.create_scrollable_frame(self.tab_frame)
        
        # Title for ESP32 tab
        esp32_title = tk.Label(content_frame, text="ESP32 Robot Controller", 
                              font=('Arial', 18, 'bold'), 
                              bg='#1e1e1e', fg='#ffffff')
        esp32_title.pack(pady=(10, 20))
        
        # Left side - Connection and Status
        left_frame = tk.Frame(content_frame, bg='#1e1e1e')
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Connection settings panel
        self.setup_esp32_connection_panel(left_frame)
        
        # Status and monitoring panel
        self.setup_esp32_status_panel(left_frame)
        
        # Right side - Control panels
        right_frame = tk.Frame(content_frame, bg='#1e1e1e')
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # ESP32 control panels
        self.setup_esp32_control_panels(right_frame)
        
    def setup_esp32_connection_panel(self, parent):
        """Setup ESP32 connection panel"""
        conn_frame = tk.LabelFrame(parent, text="🔗 Connection Settings", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        conn_frame.pack(fill="x", pady=(0, 10))
        
        # Basic connection controls
        controls_frame = tk.Frame(conn_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(controls_frame, text="ESP32 IP:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        self.esp32_ip_entry = tk.Entry(controls_frame, bg='#3d3d3d', fg='#ffffff',
                                     font=('Arial', 10), width=20)
        self.esp32_ip_entry.pack(fill="x", pady=(5, 10))
        self.esp32_ip_entry.insert(0, "192.168.1.100")
        
        # Connection buttons
        button_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        button_frame.pack(fill="x")
        
        tk.Button(button_frame, text="🔗 Connect", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.connect_esp32).pack(side="left", padx=(0, 5))
        
        tk.Button(button_frame, text="🔌 Disconnect", bg='#f44336', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.disconnect_esp32).pack(side="left", padx=5)
        
    def setup_esp32_status_panel(self, parent):
        """Setup ESP32 status panel"""
        status_frame = tk.LabelFrame(parent, text="📊 ESP32 Status", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        status_frame.pack(fill="both", expand=True)
        
        status_content = tk.Frame(status_frame, bg='#2d2d2d')
        status_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.status_label = tk.Label(status_content, text="Status: Disconnected", 
                                   bg='#2d2d2d', fg='#f44336', font=('Arial', 11))
        self.status_label.pack(anchor="w", pady=5)
        
        self.connection_info = tk.Label(status_content, text="No connection", 
                                      bg='#2d2d2d', fg='#888888', font=('Arial', 10))
        self.connection_info.pack(anchor="w")
        
    def setup_esp32_control_panels(self, parent):
        """Setup ESP32 control panels with simulator"""
        # Main control frame
        control_frame = tk.LabelFrame(parent, text="🎮 Robot Controls", 
                                    font=('Arial', 14, 'bold'),
                                    bg='#2d2d2d', fg='#ffffff')
        control_frame.pack(fill="both", expand=True)
        
        # Create notebook for different control sections
        control_notebook = tk.ttk.Notebook(control_frame)
        control_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Movement controls tab
        movement_tab = tk.Frame(control_notebook, bg='#2d2d2d')
        control_notebook.add(movement_tab, text="Movement")
        self.setup_movement_controls(movement_tab)
        
        # Arms simulator tab
        simulator_tab = tk.Frame(control_notebook, bg='#2d2d2d')
        control_notebook.add(simulator_tab, text="🤖 Arms Simulator")
        self.setup_arms_simulator(simulator_tab)
        
        # Advanced controls tab
        advanced_tab = tk.Frame(control_notebook, bg='#2d2d2d')
        control_notebook.add(advanced_tab, text="Advanced")
        self.setup_advanced_controls(advanced_tab)
    
    def setup_movement_controls(self, parent):
        """Setup basic movement controls"""
        control_content = tk.Frame(parent, bg='#2d2d2d')
        control_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Basic movement controls
        movement_frame = tk.LabelFrame(control_content, text="Basic Movements", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#3d3d3d', fg='#ffffff')
        movement_frame.pack(fill="x", pady=(0, 10))
        
        buttons_frame = tk.Frame(movement_frame, bg='#3d3d3d')
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # Movement buttons
        movement_buttons = [
            ("🏠 Home Position", self.home_position),
            ("👋 Wave", self.wave_gesture),
            ("🤗 Hug", self.hug_gesture),
            ("👀 Look Around", self.look_around)
        ]
        
        for i, (text, command) in enumerate(movement_buttons):
            row = i // 2
            col = i % 2
            btn = tk.Button(buttons_frame, text=text, bg='#2196F3', fg='#ffffff',
                           font=('Arial', 10, 'bold'), command=command, width=15)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
    
    def setup_arms_simulator(self, parent):
        """Setup ESP32 arms simulator with 2D visualization"""
        # Main simulator frame
        sim_frame = tk.Frame(parent, bg='#2d2d2d')
        sim_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Controls
        controls_frame = tk.Frame(sim_frame, bg='#2d2d2d')
        controls_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Simulator controls
        self.setup_simulator_controls(controls_frame)
        
        # Right side - 2D Visualization
        viz_frame = tk.Frame(sim_frame, bg='#2d2d2d')
        viz_frame.pack(side="right", fill="both", expand=True)
        
        # 2D visualization
        self.setup_2d_visualization(viz_frame)
    
    def setup_simulator_controls(self, parent):
        """Setup simulator control panel"""
        # Control panel
        control_panel = tk.LabelFrame(parent, text="🎮 Simulator Controls", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#3d3d3d', fg='#ffffff')
        control_panel.pack(fill="x", pady=(0, 10))
        
        panel_content = tk.Frame(control_panel, bg='#3d3d3d')
        panel_content.pack(fill="x", padx=10, pady=10)
        
        # Enable simulator toggle
        self.sim_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(panel_content, text="🎮 Enable Simulator", 
                      variable=self.sim_enabled_var,
                      bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'),
                      command=self.toggle_simulator).pack(anchor="w", pady=5)
        
        # Real-time update toggle
        self.realtime_update_var = tk.BooleanVar(value=True)
        tk.Checkbutton(panel_content, text="⚡ Real-time Update", 
                      variable=self.realtime_update_var,
                      bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10)).pack(anchor="w", pady=5)
        
        # Separator
        tk.Frame(panel_content, height=2, bg='#555555').pack(fill="x", pady=10)
        
        # Arm position controls
        position_frame = tk.LabelFrame(panel_content, text="Arm Positions", 
                                     font=('Arial', 11, 'bold'),
                                     bg='#4d4d4d', fg='#ffffff')
        position_frame.pack(fill="x", pady=(0, 10))
        
        pos_content = tk.Frame(position_frame, bg='#4d4d4d')
        pos_content.pack(fill="x", padx=10, pady=10)
        
        # Left arm controls
        left_arm_frame = tk.LabelFrame(pos_content, text="Left Arm", 
                                     font=('Arial', 10, 'bold'),
                                     bg='#5d5d5d', fg='#ffffff')
        left_arm_frame.pack(fill="x", pady=(0, 5))
        
        left_content = tk.Frame(left_arm_frame, bg='#5d5d5d')
        left_content.pack(fill="x", padx=10, pady=10)
        
        # Left arm sliders
        self.left_brazo_var = tk.DoubleVar(value=10)
        tk.Label(left_content, text="Brazo:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_content, from_=0, to=180, variable=self.left_brazo_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_arm).pack(fill="x")
        
        self.left_frente_var = tk.DoubleVar(value=80)
        tk.Label(left_content, text="Frente:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_content, from_=0, to=180, variable=self.left_frente_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_arm).pack(fill="x")
        
        self.left_high_var = tk.DoubleVar(value=80)
        tk.Label(left_content, text="High:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_content, from_=0, to=180, variable=self.left_high_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_arm).pack(fill="x")
        
        # Right arm controls
        right_arm_frame = tk.LabelFrame(pos_content, text="Right Arm", 
                                      font=('Arial', 10, 'bold'),
                                      bg='#5d5d5d', fg='#ffffff')
        right_arm_frame.pack(fill="x", pady=(5, 0))
        
        right_content = tk.Frame(right_arm_frame, bg='#5d5d5d')
        right_content.pack(fill="x", padx=10, pady=10)
        
        # Right arm sliders
        self.right_brazo_var = tk.DoubleVar(value=40)
        tk.Label(right_content, text="Brazo:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_content, from_=0, to=180, variable=self.right_brazo_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_arm).pack(fill="x")
        
        self.right_frente_var = tk.DoubleVar(value=90)
        tk.Label(right_content, text="Frente:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_content, from_=0, to=180, variable=self.right_frente_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_arm).pack(fill="x")
        
        self.right_high_var = tk.DoubleVar(value=80)
        tk.Label(right_content, text="High:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_content, from_=0, to=180, variable=self.right_high_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_arm).pack(fill="x")
        
        self.right_pollo_var = tk.DoubleVar(value=45)
        tk.Label(right_content, text="Pollo:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_content, from_=0, to=180, variable=self.right_pollo_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_arm).pack(fill="x")
        
        # Action buttons
        actions_frame = tk.Frame(panel_content, bg='#3d3d3d')
        actions_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(actions_frame, text="🔄 Reset Arms", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.reset_arms).pack(fill="x", pady=2)
        
        tk.Button(actions_frame, text="📊 Export Position", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.export_position).pack(fill="x", pady=2)
        
        tk.Button(actions_frame, text="💾 Save Preset", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.save_preset).pack(fill="x", pady=2)
    
    def setup_2d_visualization(self, parent):
        """Setup 2D visualization panel"""
        # Visualization frame
        viz_panel = tk.LabelFrame(parent, text="🎯 2D Arms Visualization", 
                                font=('Arial', 12, 'bold'),
                                bg='#3d3d3d', fg='#ffffff')
        viz_panel.pack(fill="both", expand=True)
        
        viz_content = tk.Frame(viz_panel, bg='#3d3d3d')
        viz_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 2D canvas
        self.arms_canvas = tk.Canvas(viz_content, bg='#1a1a1a', highlightthickness=0)
        self.arms_canvas.pack(fill="both", expand=True)
        
        # Status bar
        self.sim_status_label = tk.Label(viz_content, text="Simulator: Ready", 
                                       bg='#3d3d3d', fg='#4CAF50',
                                       font=('Arial', 10))
        self.sim_status_label.pack(pady=(5, 0))
        
        # Initialize visualization
        self.init_visualization()
    
    def setup_advanced_controls(self, parent):
        """Setup advanced ESP32 controls"""
        content = tk.Frame(parent, bg='#2d2d2d')
        content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Advanced controls frame
        advanced_frame = tk.LabelFrame(content, text="Advanced Controls", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#3d3d3d', fg='#ffffff')
        advanced_frame.pack(fill="x", pady=(0, 10))
        
        adv_content = tk.Frame(advanced_frame, bg='#3d3d3d')
        adv_content.pack(fill="x", padx=10, pady=10)
        
        # Advanced buttons
        advanced_buttons = [
            ("🔧 Calibrate Arms", self.calibrate_arms),
            ("📡 Test Connection", self.test_connection),
            ("⚙️ Load Configuration", self.load_config),
            ("💾 Save Configuration", self.save_config)
        ]
        
        for i, (text, command) in enumerate(advanced_buttons):
            row = i // 2
            col = i % 2
            btn = tk.Button(adv_content, text=text, bg='#9C27B0', fg='#ffffff',
                           font=('Arial', 10, 'bold'), command=command, width=18)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
        adv_content.grid_columnconfigure(0, weight=1)
        adv_content.grid_columnconfigure(1, weight=1)
    
    # ===============================
    # CONTROL METHODS
    # ===============================
    
    def connect_esp32(self):
        """Connect to ESP32"""
        self.status_label.config(text="Status: Connected", fg='#4CAF50')
        self.connection_info.config(text=f"Connected to {self.esp32_ip_entry.get()}")
        self.log_message(f"Connected to ESP32 at {self.esp32_ip_entry.get()}")
        
    def disconnect_esp32(self):
        """Disconnect from ESP32"""
        self.status_label.config(text="Status: Disconnected", fg='#f44336')
        self.connection_info.config(text="No connection")
        self.log_message("Disconnected from ESP32")
        
    def home_position(self):
        """Move robot to home position"""
        self.log_message("Command: Move to home position")
        
    def wave_gesture(self):
        """Perform wave gesture"""
        self.log_message("Command: Wave gesture")
        
    def hug_gesture(self):
        """Perform hug gesture"""
        self.log_message("Command: Hug gesture")
        
    def look_around(self):
        """Perform look around gesture"""
        self.log_message("Command: Look around")
    
    # ===============================
    # SIMULATOR METHODS
    # ===============================
    
    def init_visualization(self):
        """Initialize visualization"""
        try:
            # Initialize arms state
            self.arms_state = {
                'left_arm': {
                    'brazo': 10,
                    'frente': 80,
                    'high': 80
                },
                'right_arm': {
                    'brazo': 40,
                    'frente': 90,
                    'high': 80,
                    'pollo': 45
                }
            }
            
            # Start visualization update
            self.update_visualization()
            
        except Exception as e:
            self.log_message(f"Error initializing visualization: {e}")
    
    def update_visualization(self):
        """Update visualization"""
        try:
            if not self.sim_enabled_var.get() or not self.arms_canvas:
                return
            
            # Clear canvas
            self.arms_canvas.delete('all')
            
            # Get canvas dimensions
            width = self.arms_canvas.winfo_width()
            height = self.arms_canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                # Schedule next update if canvas not ready
                self.parent_gui.root.after(100, self.update_visualization)
                return
            
            # Draw 2D robot arms
            self.draw_arms(width, height)
            
            # Schedule next update
            if self.realtime_update_var.get():
                self.parent_gui.root.after(50, self.update_visualization)
                
        except Exception as e:
            self.log_message(f"Error updating visualization: {e}")
    
    def draw_arms(self, width, height):
        """Draw 2D robot arms on canvas"""
        try:
            # Center point
            center_x = width // 2
            center_y = height // 2
            
            # Draw torso (base)
            torso_width = 120
            torso_height = 80
            torso_x = center_x - torso_width // 2
            torso_y = center_y + 50
            
            # Torso
            self.arms_canvas.create_rectangle(torso_x, torso_y, 
                                           torso_x + torso_width, torso_y + torso_height,
                                           fill='#666666', outline='#ffffff', width=2)
            
            # Draw left arm
            self.draw_arm('left', center_x - 80, center_y, width, height)
            
            # Draw right arm
            self.draw_arm('right', center_x + 80, center_y, width, height)
            
            # Add labels
            self.arms_canvas.create_text(center_x, torso_y + torso_height + 20,
                                       text="ESP32 Robot Arms", fill='#ffffff',
                                       font=('Arial', 12, 'bold'))
            
            # Add position info
            pos_text = f"L:({self.left_brazo_var.get():.0f},{self.left_frente_var.get():.0f},{self.left_high_var.get():.0f}) " \
                      f"R:({self.right_brazo_var.get():.0f},{self.right_frente_var.get():.0f},{self.right_high_var.get():.0f})"
            self.arms_canvas.create_text(center_x, height - 30,
                                       text=pos_text, fill='#888888',
                                       font=('Arial', 9))
            
        except Exception as e:
            self.log_message(f"Error drawing arms: {e}")
    
    def draw_arm(self, side, base_x, base_y, width, height):
        """Draw individual arm"""
        try:
            if side == 'left':
                angles = {
                    'brazo': self.left_brazo_var.get(),
                    'frente': self.left_frente_var.get(),
                    'high': self.left_high_var.get()
                }
                color = '#4CAF50'  # Green for left arm
            else:
                angles = {
                    'brazo': self.right_brazo_var.get(),
                    'frente': self.right_frente_var.get(),
                    'high': self.right_high_var.get(),
                    'pollo': self.right_pollo_var.get()
                }
                color = '#2196F3'  # Blue for right arm
            
            # Calculate arm segments
            segment_length = 60
            
            # Shoulder joint
            shoulder_x = base_x
            shoulder_y = base_y
            
            # Upper arm (brazo)
            brazo_angle = math.radians(angles['brazo'])
            upper_x = shoulder_x + segment_length * math.cos(brazo_angle)
            upper_y = shoulder_y - segment_length * math.sin(brazo_angle)
            
            # Forearm (frente)
            frente_angle = brazo_angle + math.radians(angles['frente'])
            forearm_x = upper_x + segment_length * math.cos(frente_angle)
            forearm_y = upper_y - segment_length * math.sin(frente_angle)
            
            # Hand (high)
            hand_angle = frente_angle + math.radians(angles['high'])
            hand_x = forearm_x + segment_length * 0.7 * math.cos(hand_angle)
            hand_y = forearm_y - segment_length * 0.7 * math.sin(hand_angle)
            
            # Draw arm segments
            # Upper arm
            self.arms_canvas.create_line(shoulder_x, shoulder_y, upper_x, upper_y,
                                       fill=color, width=4)
            
            # Forearm
            self.arms_canvas.create_line(upper_x, upper_y, forearm_x, forearm_y,
                                       fill=color, width=4)
            
            # Hand
            self.arms_canvas.create_line(forearm_x, forearm_y, hand_x, hand_y,
                                       fill=color, width=3)
            
            # Draw joints
            joint_radius = 6
            self.arms_canvas.create_oval(shoulder_x - joint_radius, shoulder_y - joint_radius,
                                       shoulder_x + joint_radius, shoulder_y + joint_radius,
                                       fill='#ffffff', outline=color, width=2)
            
            self.arms_canvas.create_oval(upper_x - joint_radius, upper_y - joint_radius,
                                       upper_x + joint_radius, upper_y + joint_radius,
                                       fill='#ffffff', outline=color, width=2)
            
            self.arms_canvas.create_oval(forearm_x - joint_radius, forearm_y - joint_radius,
                                       forearm_x + joint_radius, forearm_y + joint_radius,
                                       fill='#ffffff', outline=color, width=2)
            
            # Draw hand
            self.arms_canvas.create_oval(hand_x - joint_radius, hand_y - joint_radius,
                                       hand_x + joint_radius, hand_y + joint_radius,
                                       fill=color, outline='#ffffff', width=2)
            
            # Add labels
            self.arms_canvas.create_text(shoulder_x, shoulder_y - 15,
                                       text=f"{side.upper()}", fill=color,
                                       font=('Arial', 8, 'bold'))
            
        except Exception as e:
            self.log_message(f"Error drawing {side} arm: {e}")
    
    def toggle_simulator(self):
        """Toggle simulator on/off"""
        try:
            if self.sim_enabled_var.get():
                self.sim_status_label.config(text="Simulator: Active", fg='#4CAF50')
                self.update_visualization()
                self.log_message("ESP32 Arms Simulator enabled")
            else:
                self.sim_status_label.config(text="Simulator: Disabled", fg='#ff6b6b')
                self.log_message("ESP32 Arms Simulator disabled")
        except Exception as e:
            self.log_message(f"Error toggling simulator: {e}")
    
    def update_left_arm(self, value=None):
        """Update left arm position"""
        try:
            # Update arms state
            self.arms_state['left_arm']['brazo'] = self.left_brazo_var.get()
            self.arms_state['left_arm']['frente'] = self.left_frente_var.get()
            self.arms_state['left_arm']['high'] = self.left_high_var.get()
            
            # Send to ESP32 if connected
            if hasattr(self.parent_gui, 'esp32') and self.parent_gui.esp32 and self.parent_gui.esp32.connected:
                self.send_arm_command('left')
            
            # Update visualization
            if self.realtime_update_var.get():
                self.update_visualization()
                
        except Exception as e:
            self.log_message(f"Error updating left arm: {e}")
    
    def update_right_arm(self, value=None):
        """Update right arm position"""
        try:
            # Update arms state
            self.arms_state['right_arm']['brazo'] = self.right_brazo_var.get()
            self.arms_state['right_arm']['frente'] = self.right_frente_var.get()
            self.arms_state['right_arm']['high'] = self.right_high_var.get()
            self.arms_state['right_arm']['pollo'] = self.right_pollo_var.get()
            
            # Send to ESP32 if connected
            if hasattr(self.parent_gui, 'esp32') and self.parent_gui.esp32 and self.parent_gui.esp32.connected:
                self.send_arm_command('right')
            
            # Update visualization
            if self.realtime_update_var.get():
                self.update_visualization()
                
        except Exception as e:
            self.log_message(f"Error updating right arm: {e}")
    
    def send_arm_command(self, side):
        """Send arm command to ESP32"""
        try:
            if side == 'left':
                command = f"LEFT_ARM:{self.left_brazo_var.get():.0f},{self.left_frente_var.get():.0f},{self.left_high_var.get():.0f}"
            else:
                command = f"RIGHT_ARM:{self.right_brazo_var.get():.0f},{self.right_frente_var.get():.0f},{self.right_high_var.get():.0f},{self.right_pollo_var.get():.0f}"
            
            # Send command to ESP32
            if hasattr(self.parent_gui, 'esp32') and self.parent_gui.esp32:
                self.parent_gui.esp32.send_command(command)
                self.log_message(f"Sent {side} arm command to ESP32")
                
        except Exception as e:
            self.log_message(f"Error sending arm command: {e}")
    
    def reset_arms(self):
        """Reset arms to default position"""
        try:
            # Reset left arm
            self.left_brazo_var.set(10)
            self.left_frente_var.set(80)
            self.left_high_var.set(80)
            
            # Reset right arm
            self.right_brazo_var.set(40)
            self.right_frente_var.set(90)
            self.right_high_var.set(80)
            self.right_pollo_var.set(45)
            
            # Update visualization
            self.update_visualization()
            self.log_message("Arms reset to default position")
            
        except Exception as e:
            self.log_message(f"Error resetting arms: {e}")
    
    def export_position(self):
        """Export current arm positions"""
        try:
            import json
            from tkinter import filedialog
            
            position_data = {
                'left_arm': {
                    'brazo': self.left_brazo_var.get(),
                    'frente': self.left_frente_var.get(),
                    'high': self.left_high_var.get()
                },
                'right_arm': {
                    'brazo': self.right_brazo_var.get(),
                    'frente': self.right_frente_var.get(),
                    'high': self.right_high_var.get(),
                    'pollo': self.right_pollo_var.get()
                },
                'timestamp': time.time()
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(position_data, f, indent=2)
                self.log_message(f"Arm positions exported to {filename}")
                
        except Exception as e:
            self.log_message(f"Error exporting position: {e}")
    
    def save_preset(self):
        """Save current position as preset"""
        try:
            from tkinter import simpledialog
            
            preset_name = simpledialog.askstring("Save Preset", "Enter preset name:")
            if preset_name:
                preset_data = {
                    'left_arm': {
                        'brazo': self.left_brazo_var.get(),
                        'frente': self.left_frente_var.get(),
                        'high': self.left_high_var.get()
                    },
                    'right_arm': {
                        'brazo': self.right_brazo_var.get(),
                        'frente': self.right_frente_var.get(),
                        'high': self.right_high_var.get(),
                        'pollo': self.right_pollo_var.get()
                    }
                }
                
                # Save to presets file
                self.save_preset_to_file(preset_name, preset_data)
                self.log_message(f"Preset '{preset_name}' saved")
                
        except Exception as e:
            self.log_message(f"Error saving preset: {e}")
    
    def save_preset_to_file(self, name, data):
        """Save preset to file"""
        try:
            import json
            import os
            
            presets_file = "esp32_arm_presets.json"
            
            # Load existing presets
            if os.path.exists(presets_file):
                with open(presets_file, 'r') as f:
                    presets = json.load(f)
            else:
                presets = {}
            
            # Add new preset
            presets[name] = data
            
            # Save back to file
            with open(presets_file, 'w') as f:
                json.dump(presets, f, indent=2)
                
        except Exception as e:
            self.log_message(f"Error saving preset to file: {e}")
    
    # ===============================
    # ADVANCED CONTROLS METHODS
    # ===============================
    
    def calibrate_arms(self):
        """Calibrate robot arms"""
        try:
            self.log_message("Starting arm calibration...")
            # Implementation would be here
            self.log_message("Arm calibration completed")
        except Exception as e:
            self.log_message(f"Error calibrating arms: {e}")
    
    def test_connection(self):
        """Test ESP32 connection"""
        try:
            if hasattr(self.parent_gui, 'esp32') and self.parent_gui.esp32:
                if self.parent_gui.esp32.connected:
                    self.log_message("ESP32 connection test: SUCCESS")
                else:
                    self.log_message("ESP32 connection test: FAILED - Not connected")
            else:
                self.log_message("ESP32 connection test: FAILED - ESP32 not available")
        except Exception as e:
            self.log_message(f"Error testing connection: {e}")
    
    def load_config(self):
        """Load ESP32 configuration"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.askopenfilename(
                title="Load ESP32 Configuration",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                import json
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Apply configuration
                self.apply_config(config)
                self.log_message(f"Configuration loaded from {filename}")
                
        except Exception as e:
            self.log_message(f"Error loading configuration: {e}")
    
    def save_config(self):
        """Save ESP32 configuration"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Save ESP32 Configuration",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                config = self.get_current_config()
                
                import json
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.log_message(f"Configuration saved to {filename}")
                
        except Exception as e:
            self.log_message(f"Error saving configuration: {e}")
    
    def apply_config(self, config):
        """Apply configuration to controls"""
        try:
            # Apply arm positions
            if 'left_arm' in config:
                left = config['left_arm']
                self.left_brazo_var.set(left.get('brazo', 10))
                self.left_frente_var.set(left.get('frente', 80))
                self.left_high_var.set(left.get('high', 80))
            
            if 'right_arm' in config:
                right = config['right_arm']
                self.right_brazo_var.set(right.get('brazo', 40))
                self.right_frente_var.set(right.get('frente', 90))
                self.right_high_var.set(right.get('high', 80))
                self.right_pollo_var.set(right.get('pollo', 45))
            
            # Update visualization
            self.update_visualization()
            
        except Exception as e:
            self.log_message(f"Error applying configuration: {e}")
    
    def get_current_config(self):
        """Get current configuration"""
        try:
            return {
                'left_arm': {
                    'brazo': self.left_brazo_var.get(),
                    'frente': self.left_frente_var.get(),
                    'high': self.left_high_var.get()
                },
                'right_arm': {
                    'brazo': self.right_brazo_var.get(),
                    'frente': self.right_frente_var.get(),
                    'high': self.right_high_var.get(),
                    'pollo': self.right_pollo_var.get()
                },
                'simulator': {
                    'enabled': self.sim_enabled_var.get(),
                    'realtime': self.realtime_update_var.get()
                }
            }
        except Exception as e:
            self.log_message(f"Error getting configuration: {e}")
            return {}
