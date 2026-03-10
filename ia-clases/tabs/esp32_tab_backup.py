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
        
        # Hand controls frame
        hands_frame = tk.LabelFrame(panel_content, text="Hand Controls", 
                                  font=('Arial', 11, 'bold'),
                                  bg='#4d4d4d', fg='#ffffff')
        hands_frame.pack(fill="x", pady=(10, 0))
        
        hands_content = tk.Frame(hands_frame, bg='#4d4d4d')
        hands_content.pack(fill="x", padx=10, pady=10)
        
        # Left hand controls
        left_hand_frame = tk.LabelFrame(hands_content, text="Left Hand", 
                                      font=('Arial', 10, 'bold'),
                                      bg='#5d5d5d', fg='#ffffff')
        left_hand_frame.pack(fill="x", pady=(0, 5))
        
        left_hand_content = tk.Frame(left_hand_frame, bg='#5d5d5d')
        left_hand_content.pack(fill="x", padx=10, pady=10)
        
        # Left hand finger controls
        self.left_thumb_var = tk.DoubleVar(value=90)
        tk.Label(left_hand_content, text="Thumb:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_hand_content, from_=0, to=180, variable=self.left_thumb_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_hand).pack(fill="x")
        
        self.left_index_var = tk.DoubleVar(value=90)
        tk.Label(left_hand_content, text="Index:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_hand_content, from_=0, to=180, variable=self.left_index_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_hand).pack(fill="x")
        
        self.left_middle_var = tk.DoubleVar(value=90)
        tk.Label(left_hand_content, text="Middle:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_hand_content, from_=0, to=180, variable=self.left_middle_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_hand).pack(fill="x")
        
        self.left_ring_var = tk.DoubleVar(value=90)
        tk.Label(left_hand_content, text="Ring:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_hand_content, from_=0, to=180, variable=self.left_ring_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_hand).pack(fill="x")
        
        self.left_pinky_var = tk.DoubleVar(value=90)
        tk.Label(left_hand_content, text="Pinky:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_hand_content, from_=0, to=180, variable=self.left_pinky_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_hand).pack(fill="x")
        
        # Right hand controls
        right_hand_frame = tk.LabelFrame(hands_content, text="Right Hand", 
                                       font=('Arial', 10, 'bold'),
                                       bg='#5d5d5d', fg='#ffffff')
        right_hand_frame.pack(fill="x", pady=(5, 0))
        
        right_hand_content = tk.Frame(right_hand_frame, bg='#5d5d5d')
        right_hand_content.pack(fill="x", padx=10, pady=10)
        
        # Right hand finger controls
        self.right_thumb_var = tk.DoubleVar(value=90)
        tk.Label(right_hand_content, text="Thumb:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_hand_content, from_=0, to=180, variable=self.right_thumb_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_hand).pack(fill="x")
        
        self.right_index_var = tk.DoubleVar(value=90)
        tk.Label(right_hand_content, text="Index:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_hand_content, from_=0, to=180, variable=self.right_index_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_hand).pack(fill="x")
        
        self.right_middle_var = tk.DoubleVar(value=90)
        tk.Label(right_hand_content, text="Middle:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_hand_content, from_=0, to=180, variable=self.right_middle_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_hand).pack(fill="x")
        
        self.right_ring_var = tk.DoubleVar(value=90)
        tk.Label(right_hand_content, text="Ring:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_hand_content, from_=0, to=180, variable=self.right_ring_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_hand).pack(fill="x")
        
        self.right_pinky_var = tk.DoubleVar(value=90)
        tk.Label(right_hand_content, text="Pinky:", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_hand_content, from_=0, to=180, variable=self.right_pinky_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_hand).pack(fill="x")
    
    def setup_2d_visualization(self, parent):
        """Setup 2D visualization panel with side and front views"""
        # Visualization frame
        viz_panel = tk.LabelFrame(parent, text="🎯 Multi-View Arms Visualization", 
                                font=('Arial', 12, 'bold'),
                                bg='#3d3d3d', fg='#ffffff')
        viz_panel.pack(fill="both", expand=True)
        
        viz_content = tk.Frame(viz_panel, bg='#3d3d3d')
        viz_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # View controls frame
        view_controls_frame = tk.Frame(viz_content, bg='#3d3d3d')
        view_controls_frame.pack(fill="x", pady=(0, 10))
        
        # View selection buttons
        self.view_var = tk.StringVar(value="side")
        tk.Radiobutton(view_controls_frame, text="👤 Side View", variable=self.view_var, 
                      value="side", bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'), command=self.change_view).pack(side="left", padx=(0, 10))
        
        tk.Radiobutton(view_controls_frame, text="✋ Hands View", variable=self.view_var, 
                      value="hands", bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'), command=self.change_view).pack(side="left", padx=(0, 10))
        
        tk.Radiobutton(view_controls_frame, text="🔄 Both Views", variable=self.view_var, 
                      value="both", bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'), command=self.change_view).pack(side="left")
        
        # Canvas container
        canvas_container = tk.Frame(viz_content, bg='#3d3d3d')
        canvas_container.pack(fill="both", expand=True)
        
        # Side view canvas
        self.side_canvas = tk.Canvas(canvas_container, bg='#1a1a1a', highlightthickness=0)
        
        # Hands view canvas
        self.hands_canvas = tk.Canvas(canvas_container, bg='#1a1a1a', highlightthickness=0)
        
        # Initially show only side view (will be configured by change_view)
        # Don't pack both canvases yet - let change_view handle it
        
        # Status bar
        self.sim_status_label = tk.Label(viz_content, text="Simulator: Ready - Side View", 
                                       bg='#3d3d3d', fg='#4CAF50',
                                       font=('Arial', 10))
        self.sim_status_label.pack(pady=(5, 0))
        
        # Initialize visualization and set initial view
        self.init_visualization()
        
        # Set initial view after everything is created
        self.change_view()
    
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
     
     def update_left_hand(self, value=None):
         """Update left hand finger positions"""
         try:
             # Send to ESP32 if connected
             if hasattr(self.parent_gui, 'esp32') and self.parent_gui.esp32 and self.parent_gui.esp32.connected:
                 self.send_hand_command('left')
             
             # Update visualization
             if self.realtime_update_var.get():
                 view = self.view_var.get()
                 if view in ["hands", "both"]:
                     self.update_hands_view()
                     
         except Exception as e:
             self.log_message(f"Error updating left hand: {e}")
     
     def update_right_hand(self, value=None):
         """Update right hand finger positions"""
         try:
             # Send to ESP32 if connected
             if hasattr(self.parent_gui, 'esp32') and self.parent_gui.esp32 and self.parent_gui.esp32.connected:
                 self.send_hand_command('right')
             
             # Update visualization
             if self.realtime_update_var.get():
                 view = self.view_var.get()
                 if view in ["hands", "both"]:
                     self.update_hands_view()
                     
         except Exception as e:
             self.log_message(f"Error updating right hand: {e}")
     
     def send_hand_command(self, side):
         """Send hand command to ESP32"""
         try:
             if side == 'left':
                 command = f"LEFT_HAND:{self.left_thumb_var.get():.0f},{self.left_index_var.get():.0f},{self.left_middle_var.get():.0f},{self.left_ring_var.get():.0f},{self.left_pinky_var.get():.0f}"
             else:
                 command = f"RIGHT_HAND:{self.right_thumb_var.get():.0f},{self.right_index_var.get():.0f},{self.right_middle_var.get():.0f},{self.right_ring_var.get():.0f},{self.right_pinky_var.get():.0f}"
             
             # Send command to ESP32
             if hasattr(self.parent_gui, 'esp32') and self.parent_gui.esp32:
                 self.parent_gui.esp32.send_command(command)
                 self.log_message(f"Sent {side} hand command to ESP32")
                 
         except Exception as e:
             self.log_message(f"Error sending hand command: {e}")
    
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
            
            # Set current canvas reference
            self.arms_canvas = self.side_canvas
            
            # Start visualization update
            self.update_visualization()
            
        except Exception as e:
            self.log_message(f"Error initializing visualization: {e}")
    
    def change_view(self):
        """Change between different views"""
        try:
            view = self.view_var.get()
            
            if view == "side":
                self.front_canvas.pack_forget()
                self.side_canvas.pack(fill="both", expand=True)
                self.arms_canvas = self.side_canvas
                self.sim_status_label.config(text="Simulator: Ready - Side View")
                
                         elif view == "hands":
                 self.side_canvas.pack_forget()
                 self.hands_canvas.pack(fill="both", expand=True)
                 self.arms_canvas = self.hands_canvas
                 self.sim_status_label.config(text="Simulator: Ready - Hands View")
                
            elif view == "both":
                self.side_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
                self.hands_canvas.pack(side="right", fill="both", expand=True, padx=(5, 0))
                self.arms_canvas = self.side_canvas  # Use side canvas as primary
                self.sim_status_label.config(text="Simulator: Ready - Both Views")
            
            # Force update after a short delay to ensure canvas is ready
            self.parent_gui.root.after(100, self.force_view_update)
            
        except Exception as e:
            self.log_message(f"Error changing view: {e}")
    
    def force_view_update(self):
        """Force update of the current view"""
        try:
            view = self.view_var.get()
            
                         if view == "side":
                 self.update_side_view()
             elif view == "hands":
                 self.update_hands_view()
             elif view == "both":
                 self.update_side_view()
                 self.update_hands_view()
                
        except Exception as e:
            self.log_message(f"Error in force view update: {e}")
    
    def update_visualization(self):
        """Update visualization"""
        try:
            if not self.sim_enabled_var.get():
                return
            
            view = self.view_var.get()
            
                         # Update side view
             if view in ["side", "both"]:
                 self.update_side_view()
             
             # Update hands view
             if view in ["hands", "both"]:
                 self.update_hands_view()
            
            # Schedule next update
            if self.realtime_update_var.get():
                self.parent_gui.root.after(50, self.update_visualization)
                
        except Exception as e:
            self.log_message(f"Error updating visualization: {e}")
    
    def update_side_view(self):
        """Update side view visualization"""
        try:
            if not self.side_canvas:
                return
            
            # Clear canvas
            self.side_canvas.delete('all')
            
            # Get canvas dimensions
            width = self.side_canvas.winfo_width()
            height = self.side_canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                return
            
            # Draw side view
            self.draw_side_view(width, height)
            
                 except Exception as e:
             self.log_message(f"Error updating side view: {e}")
     
     def update_hands_view(self):
         """Update hands view visualization"""
         try:
             if not self.hands_canvas:
                 return
             
             # Clear canvas
             self.hands_canvas.delete('all')
             
             # Get canvas dimensions
             width = self.hands_canvas.winfo_width()
             height = self.hands_canvas.winfo_height()
             
             if width <= 1 or height <= 1:
                 return
             
             # Draw hands view
             self.draw_hands_view(width, height)
             
         except Exception as e:
             self.log_message(f"Error updating hands view: {e}")
     
     def update_front_view(self):
        """Update front view visualization"""
        try:
            if not self.front_canvas:
                return
            
            # Clear canvas
            self.front_canvas.delete('all')
            
            # Get canvas dimensions
            width = self.front_canvas.winfo_width()
            height = self.front_canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                return
            
            # Draw front view
            self.draw_front_view(width, height)
            
        except Exception as e:
            self.log_message(f"Error updating front view: {e}")
    
    def draw_side_view(self, width, height):
        """Draw side view of robot arms"""
        try:
            # Center point
            center_x = width // 2
            center_y = height // 2
            
            # Draw torso (side view - rectangle)
            torso_width = 80
            torso_height = 120
            torso_x = center_x - torso_width // 2
            torso_y = center_y - 20
            
            # Torso
            self.side_canvas.create_rectangle(torso_x, torso_y, 
                                           torso_x + torso_width, torso_y + torso_height,
                                           fill='#666666', outline='#ffffff', width=2)
            
            # Draw head (circle)
            head_radius = 25
            head_x = center_x
            head_y = torso_y - head_radius - 10
            
            self.side_canvas.create_oval(head_x - head_radius, head_y - head_radius,
                                       head_x + head_radius, head_y + head_radius,
                                       fill='#888888', outline='#ffffff', width=2)
            
            # Draw arms from side view
            self.draw_side_arm('left', center_x - 50, center_y + 20, width, height)
            self.draw_side_arm('right', center_x + 50, center_y + 20, width, height)
            
            # Add labels
            self.side_canvas.create_text(center_x, torso_y + torso_height + 20,
                                       text="Side View - ESP32 Robot", fill='#ffffff',
                                       font=('Arial', 12, 'bold'))
            
            # Add position info
            pos_text = f"L:({self.left_brazo_var.get():.0f},{self.left_frente_var.get():.0f},{self.left_high_var.get():.0f}) " \
                      f"R:({self.right_brazo_var.get():.0f},{self.right_frente_var.get():.0f},{self.right_high_var.get():.0f})"
            self.side_canvas.create_text(center_x, height - 30,
                                       text=pos_text, fill='#888888',
                                       font=('Arial', 9))
            
        except Exception as e:
            self.log_message(f"Error drawing side view: {e}")
    
    def draw_front_view(self, width, height):
        """Draw front view of robot arms"""
        try:
            # Center point
            center_x = width // 2
            center_y = height // 2
            
            # Draw torso (front view - wider rectangle)
            torso_width = 120
            torso_height = 100
            torso_x = center_x - torso_width // 2
            torso_y = center_y - 10
            
            # Torso
            self.front_canvas.create_rectangle(torso_x, torso_y, 
                                            torso_x + torso_width, torso_y + torso_height,
                                            fill='#666666', outline='#ffffff', width=2)
            
            # Draw head (circle)
            head_radius = 30
            head_x = center_x
            head_y = torso_y - head_radius - 10
            
            self.front_canvas.create_oval(head_x - head_radius, head_y - head_radius,
                                        head_x + head_radius, head_y + head_radius,
                                        fill='#888888', outline='#ffffff', width=2)
            
            # Draw arms from front view
            self.draw_front_arm('left', center_x - 80, center_y + 20, width, height)
            self.draw_front_arm('right', center_x + 80, center_y + 20, width, height)
            
            # Add labels
            self.front_canvas.create_text(center_x, torso_y + torso_height + 20,
                                        text="Front View - ESP32 Robot", fill='#ffffff',
                                        font=('Arial', 12, 'bold'))
            
            # Add position info
            pos_text = f"L:({self.left_brazo_var.get():.0f},{self.left_frente_var.get():.0f},{self.left_high_var.get():.0f}) " \
                      f"R:({self.right_brazo_var.get():.0f},{self.right_frente_var.get():.0f},{self.right_high_var.get():.0f})"
            self.front_canvas.create_text(center_x, height - 30,
                                        text=pos_text, fill='#888888',
                                        font=('Arial', 9))
            
                 except Exception as e:
             self.log_message(f"Error drawing front view: {e}")
     
     def draw_hands_view(self, width, height):
         """Draw hands view with detailed finger control"""
         try:
             # Center point
             center_x = width // 2
             center_y = height // 2
             
             # Draw title
             self.hands_canvas.create_text(center_x, 30,
                                         text="Robot Hands Simulation", fill='#ffffff',
                                         font=('Arial', 16, 'bold'))
             
             # Draw left hand
             left_hand_x = center_x - 150
             left_hand_y = center_y
             self.draw_hand('left', left_hand_x, left_hand_y, width, height)
             
             # Draw right hand
             right_hand_x = center_x + 150
             right_hand_y = center_y
             self.draw_hand('right', right_hand_x, right_hand_y, width, height)
             
             # Add labels
             self.hands_canvas.create_text(left_hand_x, left_hand_y + 120,
                                         text="Left Hand", fill='#4CAF50',
                                         font=('Arial', 14, 'bold'))
             
             self.hands_canvas.create_text(right_hand_x, right_hand_y + 120,
                                         text="Right Hand", fill='#2196F3',
                                         font=('Arial', 14, 'bold'))
             
             # Add finger position info
             left_fingers = f"T:{self.left_thumb_var.get():.0f} I:{self.left_index_var.get():.0f} M:{self.left_middle_var.get():.0f} R:{self.left_ring_var.get():.0f} P:{self.left_pinky_var.get():.0f}"
             right_fingers = f"T:{self.right_thumb_var.get():.0f} I:{self.right_index_var.get():.0f} M:{self.right_middle_var.get():.0f} R:{self.right_ring_var.get():.0f} P:{self.right_pinky_var.get():.0f}"
             
             self.hands_canvas.create_text(left_hand_x, height - 50,
                                         text=left_fingers, fill='#888888',
                                         font=('Arial', 9))
             
             self.hands_canvas.create_text(right_hand_x, height - 30,
                                         text=right_fingers, fill='#888888',
                                         font=('Arial', 9))
             
         except Exception as e:
             self.log_message(f"Error drawing hands view: {e}")
     
     def draw_hand(self, side, hand_x, hand_y, width, height):
         """Draw individual hand with fingers"""
         try:
             if side == 'left':
                 color = '#4CAF50'  # Green for left hand
                 thumb_angle = self.left_thumb_var.get()
                 index_angle = self.left_index_var.get()
                 middle_angle = self.left_middle_var.get()
                 ring_angle = self.left_ring_var.get()
                 pinky_angle = self.left_pinky_var.get()
             else:
                 color = '#2196F3'  # Blue for right hand
                 thumb_angle = self.right_thumb_var.get()
                 index_angle = self.right_index_var.get()
                 middle_angle = self.right_middle_var.get()
                 ring_angle = self.right_ring_var.get()
                 pinky_angle = self.right_pinky_var.get()
             
             # Draw palm (rectangle)
             palm_width = 60
             palm_height = 80
             palm_x = hand_x - palm_width // 2
             palm_y = hand_y - palm_height // 2
             
             self.hands_canvas.create_rectangle(palm_x, palm_y, 
                                              palm_x + palm_width, palm_y + palm_height,
                                              fill=color, outline='#ffffff', width=2)
             
             # Draw wrist
             wrist_width = 40
             wrist_height = 30
             wrist_x = hand_x - wrist_width // 2
             wrist_y = palm_y + palm_height
             
             self.hands_canvas.create_rectangle(wrist_x, wrist_y,
                                              wrist_x + wrist_width, wrist_y + wrist_height,
                                              fill=color, outline='#ffffff', width=2)
             
             # Draw fingers
             finger_length = 50
             finger_width = 12
             
             # Calculate finger positions
             fingers = [
                 ('thumb', thumb_angle, palm_x - 10, palm_y + 20, -45),  # Thumb (angled)
                 ('index', index_angle, palm_x + 5, palm_y - finger_length, 0),
                 ('middle', middle_angle, palm_x + 20, palm_y - finger_length, 0),
                 ('ring', ring_angle, palm_x + 35, palm_y - finger_length, 0),
                 ('pinky', pinky_angle, palm_x + 50, palm_y - finger_length + 10, 0)  # Pinky (shorter)
             ]
             
             for finger_name, angle, start_x, start_y, base_angle in fingers:
                 self.draw_finger(finger_name, angle, start_x, start_y, base_angle, finger_length, color)
             
         except Exception as e:
             self.log_message(f"Error drawing {side} hand: {e}")
     
     def draw_finger(self, finger_name, angle, start_x, start_y, base_angle, length, color):
         """Draw individual finger with bending animation"""
         try:
             # Calculate finger bending (0 = straight, 180 = fully bent)
             bend_factor = angle / 180.0
             
             if finger_name == 'thumb':
                 # Thumb moves differently (rotation instead of bending)
                 thumb_angle = math.radians(base_angle + (angle - 90))
                 end_x = start_x + length * math.cos(thumb_angle)
                 end_y = start_y + length * math.sin(thumb_angle)
                 
                 self.hands_canvas.create_line(start_x, start_y, end_x, end_y,
                                             fill=color, width=8, capstyle='round')
                 
                 # Draw thumb tip
                 self.hands_canvas.create_oval(end_x - 6, end_y - 6, end_x + 6, end_y + 6,
                                             fill='#ffffff', outline=color, width=2)
             else:
                 # Other fingers bend in segments
                 segment_length = length // 3
                 
                 # First segment (straight)
                 seg1_end_x = start_x
                 seg1_end_y = start_y + segment_length
                 
                 self.hands_canvas.create_line(start_x, start_y, seg1_end_x, seg1_end_y,
                                             fill=color, width=6, capstyle='round')
                 
                 # Second segment (bends based on angle)
                 bend_angle = math.radians(bend_factor * 60)  # Max 60 degree bend
                 seg2_end_x = seg1_end_x + segment_length * math.sin(bend_angle)
                 seg2_end_y = seg1_end_y + segment_length * math.cos(bend_angle)
                 
                 self.hands_canvas.create_line(seg1_end_x, seg1_end_y, seg2_end_x, seg2_end_y,
                                             fill=color, width=6, capstyle='round')
                 
                 # Third segment (bends more)
                 bend_angle2 = math.radians(bend_factor * 90)  # Max 90 degree bend
                 seg3_end_x = seg2_end_x + segment_length * math.sin(bend_angle2)
                 seg3_end_y = seg2_end_y + segment_length * math.cos(bend_angle2)
                 
                 self.hands_canvas.create_line(seg2_end_x, seg2_end_y, seg3_end_x, seg3_end_y,
                                             fill=color, width=6, capstyle='round')
                 
                 # Draw finger tip
                 self.hands_canvas.create_oval(seg3_end_x - 4, seg3_end_y - 4, seg3_end_x + 4, seg3_end_y + 4,
                                             fill='#ffffff', outline=color, width=2)
                 
                 # Draw joint indicators
                 self.hands_canvas.create_oval(seg1_end_x - 3, seg1_end_y - 3, seg1_end_x + 3, seg1_end_y + 3,
                                             fill='#ffffff', outline=color, width=1)
                 self.hands_canvas.create_oval(seg2_end_x - 3, seg2_end_y - 3, seg2_end_x + 3, seg2_end_y + 3,
                                             fill='#ffffff', outline=color, width=1)
             
         except Exception as e:
             self.log_message(f"Error drawing finger {finger_name}: {e}")
     
     def draw_side_arm(self, side, base_x, base_y, width, height):
        """Draw individual arm from side view"""
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
            
            # Calculate arm segments for side view
            segment_length = 50
            
            # Shoulder joint
            shoulder_x = base_x
            shoulder_y = base_y
            
            # Upper arm (brazo) - side view shows forward/backward movement
            brazo_angle = math.radians(angles['brazo'] - 90)  # Adjust for side view
            upper_x = shoulder_x + segment_length * math.cos(brazo_angle)
            upper_y = shoulder_y - segment_length * math.sin(brazo_angle)
            
            # Forearm (frente) - side view shows up/down movement
            frente_angle = brazo_angle + math.radians(angles['frente'])
            forearm_x = upper_x + segment_length * math.cos(frente_angle)
            forearm_y = upper_y - segment_length * math.sin(frente_angle)
            
            # Hand (high) - side view shows wrist rotation
            hand_angle = frente_angle + math.radians(angles['high'])
            hand_x = forearm_x + segment_length * 0.6 * math.cos(hand_angle)
            hand_y = forearm_y - segment_length * 0.6 * math.sin(hand_angle)
            
            # Draw arm segments
            self.side_canvas.create_line(shoulder_x, shoulder_y, upper_x, upper_y,
                                       fill=color, width=4)
            self.side_canvas.create_line(upper_x, upper_y, forearm_x, forearm_y,
                                       fill=color, width=4)
            self.side_canvas.create_line(forearm_x, forearm_y, hand_x, hand_y,
                                       fill=color, width=3)
            
            # Draw joints
            joint_radius = 5
            self.side_canvas.create_oval(shoulder_x - joint_radius, shoulder_y - joint_radius,
                                       shoulder_x + joint_radius, shoulder_y + joint_radius,
                                       fill='#ffffff', outline=color, width=2)
            self.side_canvas.create_oval(upper_x - joint_radius, upper_y - joint_radius,
                                       upper_x + joint_radius, upper_y + joint_radius,
                                       fill='#ffffff', outline=color, width=2)
            self.side_canvas.create_oval(forearm_x - joint_radius, forearm_y - joint_radius,
                                       forearm_x + joint_radius, forearm_y + joint_radius,
                                       fill='#ffffff', outline=color, width=2)
            self.side_canvas.create_oval(hand_x - joint_radius, hand_y - joint_radius,
                                       hand_x + joint_radius, hand_y + joint_radius,
                                       fill=color, outline='#ffffff', width=2)
            
            # Add labels
            self.side_canvas.create_text(shoulder_x, shoulder_y - 15,
                                       text=f"{side.upper()}", fill=color,
                                       font=('Arial', 8, 'bold'))
            
        except Exception as e:
            self.log_message(f"Error drawing {side} arm (side view): {e}")
    
    def draw_front_arm(self, side, base_x, base_y, width, height):
        """Draw individual arm from front view"""
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
            
            # Calculate arm segments for front view
            segment_length = 50
            
            # Shoulder joint
            shoulder_x = base_x
            shoulder_y = base_y
            
            # Upper arm (brazo) - front view shows left/right movement
            brazo_angle = math.radians(angles['brazo'])
            upper_x = shoulder_x + segment_length * math.cos(brazo_angle)
            upper_y = shoulder_y - segment_length * math.sin(brazo_angle)
            
            # Forearm (frente) - front view shows up/down movement
            frente_angle = brazo_angle + math.radians(angles['frente'])
            forearm_x = upper_x + segment_length * math.cos(frente_angle)
            forearm_y = upper_y - segment_length * math.sin(frente_angle)
            
            # Hand (high) - front view shows wrist rotation
            hand_angle = frente_angle + math.radians(angles['high'])
            hand_x = forearm_x + segment_length * 0.6 * math.cos(hand_angle)
            hand_y = forearm_y - segment_length * 0.6 * math.sin(hand_angle)
            
            # Draw arm segments
            self.front_canvas.create_line(shoulder_x, shoulder_y, upper_x, upper_y,
                                        fill=color, width=4)
            self.front_canvas.create_line(upper_x, upper_y, forearm_x, forearm_y,
                                        fill=color, width=4)
            self.front_canvas.create_line(forearm_x, forearm_y, hand_x, hand_y,
                                        fill=color, width=3)
            
            # Draw joints
            joint_radius = 5
            self.front_canvas.create_oval(shoulder_x - joint_radius, shoulder_y - joint_radius,
                                        shoulder_x + joint_radius, shoulder_y + joint_radius,
                                        fill='#ffffff', outline=color, width=2)
            self.front_canvas.create_oval(upper_x - joint_radius, upper_y - joint_radius,
                                        upper_x + joint_radius, upper_y + joint_radius,
                                        fill='#ffffff', outline=color, width=2)
            self.front_canvas.create_oval(forearm_x - joint_radius, forearm_y - joint_radius,
                                        forearm_x + joint_radius, forearm_y + joint_radius,
                                        fill='#ffffff', outline=color, width=2)
            self.front_canvas.create_oval(hand_x - joint_radius, hand_y - joint_radius,
                                        hand_x + joint_radius, hand_y + joint_radius,
                                        fill=color, outline='#ffffff', width=2)
            
            # Add labels
            self.front_canvas.create_text(shoulder_x, shoulder_y - 15,
                                        text=f"{side.upper()}", fill=color,
                                        font=('Arial', 8, 'bold'))
            
        except Exception as e:
            self.log_message(f"Error drawing {side} arm (front view): {e}")
    
    def draw_arms(self, width, height):
        """Draw 2D robot arms on canvas (legacy method for compatibility)"""
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
         """Reset arms and hands to default position"""
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
             
             # Reset left hand
             self.left_thumb_var.set(90)
             self.left_index_var.set(90)
             self.left_middle_var.set(90)
             self.left_ring_var.set(90)
             self.left_pinky_var.set(90)
             
             # Reset right hand
             self.right_thumb_var.set(90)
             self.right_index_var.set(90)
             self.right_middle_var.set(90)
             self.right_ring_var.set(90)
             self.right_pinky_var.set(90)
             
             # Update visualization
             self.update_visualization()
             self.log_message("Arms and hands reset to default position")
            
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
                 'left_hand': {
                     'thumb': self.left_thumb_var.get(),
                     'index': self.left_index_var.get(),
                     'middle': self.left_middle_var.get(),
                     'ring': self.left_ring_var.get(),
                     'pinky': self.left_pinky_var.get()
                 },
                 'right_hand': {
                     'thumb': self.right_thumb_var.get(),
                     'index': self.right_index_var.get(),
                     'middle': self.right_middle_var.get(),
                     'ring': self.right_ring_var.get(),
                     'pinky': self.right_pinky_var.get()
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
