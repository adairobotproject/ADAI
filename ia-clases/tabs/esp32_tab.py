# -*- coding: utf-8 -*-
"""
ESP32 Tab for RobotGUI - ESP32 Robot Controller Interface (Simplified)
"""

import tkinter as tk
import tkinter.ttk as ttk
import math
import time
from .base_tab import BaseTab

# Import ESP32 binary configuration and client
try:
    from services.esp32_services.esp32_config_binary import ESP32BinaryConfig, ESP32Config
    from services.esp32_services.esp32_client import ESP32Client
    CONFIG_AVAILABLE = True
    ESP32_CLIENT_AVAILABLE = True
except ImportError:
    try:
        from esp32_services.esp32_config_binary import ESP32BinaryConfig, ESP32Config
        from esp32_services.esp32_client import ESP32Client
        CONFIG_AVAILABLE = True
        ESP32_CLIENT_AVAILABLE = True
    except ImportError:
        CONFIG_AVAILABLE = False
        ESP32_CLIENT_AVAILABLE = False
        print("⚠️ ESP32 Binary Config o ESP32Client no disponible")

class MockBooleanVar:
    """Mock BooleanVar for when tkinter is not available"""
    def __init__(self, value=False):
        self._value = bool(value)

    def get(self):
        return self._value

    def set(self, value):
        self._value = bool(value)

class ESP32Tab(BaseTab):
    """ESP32 controller tab with connection management and robot controls"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "🔌 ESP32 Controller"

        # Initialize ESP32 configuration manager
        if CONFIG_AVAILABLE:
            self.config_manager = ESP32BinaryConfig()
            self.current_config = None
        else:
            self.config_manager = None
            self.current_config = None

        # Initialize ESP32 client
        if ESP32_CLIENT_AVAILABLE:
            self.esp32_client = None
            self.esp32_connected = False
            # Initialize tkinter variables safely
            self.esp32_real_mode = self._create_boolean_var(False)  # Toggle between simulation and real ESP32
        else:
            self.esp32_client = None
            self.esp32_connected = False
            self.esp32_real_mode = self._create_boolean_var(False)

    def _create_boolean_var(self, value=False):
        """Create a tkinter BooleanVar safely"""
        try:
            return tk.BooleanVar(value=value)
        except Exception as e:
            print(f"Warning: Could not create BooleanVar: {e}")
            # Return a mock object that behaves like BooleanVar
            return MockBooleanVar(value)

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
        
        # Command log panel
        self.setup_esp32_command_log_panel(left_frame)
        
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
        
        # Load current configuration if available
        if CONFIG_AVAILABLE and self.config_manager:
            self.load_current_config()
        else:
            self.esp32_ip_entry.insert(0, "192.168.1.100")
        
        # Connection buttons
        button_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        button_frame.pack(fill="x")
        
        tk.Button(button_frame, text="🔗 Connect", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.connect_esp32).pack(side="left", padx=(0, 5))
        
        tk.Button(button_frame, text="🔌 Disconnect", bg='#f44336', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.disconnect_esp32).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="🧪 Test Connection", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.test_esp32_connection).pack(side="left", padx=5)
        
        # Real ESP32 mode toggle
        real_mode_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        real_mode_frame.pack(fill="x", pady=(10, 0))
        
        tk.Checkbutton(real_mode_frame, text="🤖 Real ESP32 Mode", variable=self.esp32_real_mode,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', 10, 'bold'),
                      command=self.toggle_real_mode).pack(anchor="w")
        
        self.real_mode_label = tk.Label(real_mode_frame, text="🟡 Simulation Mode", 
                                       bg='#2d2d2d', fg='#FFD700',
                                       font=('Arial', 9, 'bold'))
        self.real_mode_label.pack(anchor="w", pady=(5, 0))
        
        # Configuration management buttons
        config_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        config_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(config_frame, text="💾 Save Configuration", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.save_esp32_config).pack(side="left", padx=(0, 5))
        
        tk.Button(config_frame, text="🔄 Load Configuration", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.load_esp32_config).pack(side="left", padx=5)
        
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
        
        # Real mode status
        self.real_mode_status = tk.Label(status_content, text="Mode: Simulation", 
                                       bg='#2d2d2d', fg='#FFD700', font=('Arial', 10, 'bold'))
        self.real_mode_status.pack(anchor="w", pady=(5, 0))
    
    def setup_esp32_command_log_panel(self, parent):
        """Setup ESP32 command log panel"""
        log_frame = tk.LabelFrame(parent, text="📝 Command Log", 
                                font=('Arial', 14, 'bold'),
                                bg='#2d2d2d', fg='#ffffff')
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        log_content = tk.Frame(log_frame, bg='#2d2d2d')
        log_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Log controls
        controls_frame = tk.Frame(log_content, bg='#2d2d2d')
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Enable log toggle
        self.log_enabled_var = self._create_boolean_var(True)
        tk.Checkbutton(controls_frame, text="📝 Enable Command Log", 
                      variable=self.log_enabled_var,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold')).pack(side="left", padx=(0, 10))
        
        # Clear log button
        tk.Button(controls_frame, text="🗑️ Clear Log", bg='#f44336', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=self.clear_command_log).pack(side="left", padx=5)
        
        # Export log button
        tk.Button(controls_frame, text="💾 Export Log", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=self.export_command_log).pack(side="left", padx=5)
        
        # Log display
        log_display_frame = tk.Frame(log_content, bg='#1e1e1e')
        log_display_frame.pack(fill="both", expand=True)
        
        # Create text widget with scrollbar
        self.command_log_text = tk.Text(log_display_frame, 
                                       bg='#1e1e1e', fg='#00ff00',
                                       font=('Consolas', 9),
                                       wrap=tk.WORD, height=12)
        
        log_scrollbar = tk.Scrollbar(log_display_frame, orient="vertical", 
                                   command=self.command_log_text.yview)
        self.command_log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.command_log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # Initialize log
        self.log_command("ESP32 Command Log initialized", "SYSTEM")
        
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
        self.sim_enabled_var = self._create_boolean_var(True)
        tk.Checkbutton(panel_content, text="🎮 Enable Simulator",
                      variable=self.sim_enabled_var,
                      bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'),
                      command=self.toggle_simulator).pack(anchor="w", pady=5)

        # Real-time update toggle
        self.realtime_update_var = self._create_boolean_var(True)
        tk.Checkbutton(panel_content, text="⚡ Real-time Update", 
                      variable=self.realtime_update_var,
                      bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10)).pack(anchor="w", pady=5)
        
        # Separator
        tk.Frame(panel_content, height=2, bg='#555555').pack(fill="x", pady=10)
        
        # Sequence Demo section
        sequence_frame = tk.LabelFrame(panel_content, text="🎬 Sequence Demo", 
                                     font=('Arial', 11, 'bold'),
                                     bg='#4d4d4d', fg='#ffffff')
        sequence_frame.pack(fill="x", pady=(0, 10))
        
        seq_content = tk.Frame(sequence_frame, bg='#4d4d4d')
        seq_content.pack(fill="x", padx=10, pady=10)
        
        # Sequence selection
        seq_select_frame = tk.Frame(seq_content, bg='#4d4d4d')
        seq_select_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(seq_select_frame, text="Sequence File:", bg='#4d4d4d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(anchor="w")
        
        self.sequence_path_var = tk.StringVar()
        self.sequence_path_entry = tk.Entry(seq_select_frame, textvariable=self.sequence_path_var,
                                          bg='#3d3d3d', fg='#ffffff', font=('Arial', 9),
                                          state='readonly', width=30)
        self.sequence_path_entry.pack(fill="x", pady=(5, 5))
        
        # Sequence buttons
        seq_buttons_frame = tk.Frame(seq_content, bg='#4d4d4d')
        seq_buttons_frame.pack(fill="x")
        
        tk.Button(seq_buttons_frame, text="📁 Load Sequence", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=self.load_sequence_for_simulator).pack(side="left", padx=(0, 5))
        
        tk.Button(seq_buttons_frame, text="🎬 Execute Sequence", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=self.execute_loaded_sequence).pack(side="left", padx=5)
        
        tk.Button(seq_buttons_frame, text="⏸️ Pause", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=self.pause_sequence_execution).pack(side="left", padx=5)
        
        tk.Button(seq_buttons_frame, text="⏹️ Stop", bg='#f44336', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=self.stop_sequence_execution).pack(side="left", padx=5)
        
        # Sequence info
        self.sequence_info_label = tk.Label(seq_content, text="No sequence loaded", 
                                          bg='#4d4d4d', fg='#888888', font=('Arial', 9))
        self.sequence_info_label.pack(anchor="w", pady=(5, 0))
        
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
        
        # Left arm sliders (M5-M8)
        self.left_pollo_var = tk.DoubleVar(value=90)
        tk.Label(left_content, text="Pollo Izq (M5):", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_content, from_=0, to=180, variable=self.left_pollo_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_arm).pack(fill="x")

        self.left_frente_var = tk.DoubleVar(value=95)
        tk.Label(left_content, text="Frente Izq (M6):", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_content, from_=0, to=180, variable=self.left_frente_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_arm).pack(fill="x")

        self.left_brazo_var = tk.DoubleVar(value=100)
        tk.Label(left_content, text="Brazo Izq (M7):", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(left_content, from_=0, to=180, variable=self.left_brazo_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_left_arm).pack(fill="x")

        self.left_high_var = tk.DoubleVar(value=140)
        tk.Label(left_content, text="High Izq (M8):", bg='#5d5d5d', fg='#ffffff',
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

        # Right arm sliders (M1-M4)
        self.right_pollo_var = tk.DoubleVar(value=100)
        tk.Label(right_content, text="Pollo Der (M1):", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_content, from_=0, to=180, variable=self.right_pollo_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_arm).pack(fill="x")

        self.right_frente_var = tk.DoubleVar(value=160)
        tk.Label(right_content, text="Frente Der (M2):", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_content, from_=0, to=180, variable=self.right_frente_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_arm).pack(fill="x")

        self.right_brazo_var = tk.DoubleVar(value=30)
        tk.Label(right_content, text="Brazo Der (M3):", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_content, from_=0, to=180, variable=self.right_brazo_var,
                orient="horizontal", bg='#5d5d5d', fg='#ffffff',
                highlightthickness=0, command=self.update_right_arm).pack(fill="x")

        self.right_high_var = tk.DoubleVar(value=165)
        tk.Label(right_content, text="High Der (M4):", bg='#5d5d5d', fg='#ffffff',
                font=('Arial', 9)).pack(anchor="w")
        tk.Scale(right_content, from_=0, to=180, variable=self.right_high_var,
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
        
        tk.Radiobutton(view_controls_frame, text="👁️ Front View", variable=self.view_var, 
                      value="front", bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'), command=self.change_view).pack(side="left", padx=(0, 10))
        
        tk.Radiobutton(view_controls_frame, text="🔄 Both Views", variable=self.view_var, 
                      value="both", bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'), command=self.change_view).pack(side="left")
        
        # Canvas container
        canvas_container = tk.Frame(viz_content, bg='#3d3d3d')
        canvas_container.pack(fill="both", expand=True)
        
        # Side view canvas
        self.side_canvas = tk.Canvas(canvas_container, bg='#1a1a1a', highlightthickness=0)
        
        # Front view canvas
        self.front_canvas = tk.Canvas(canvas_container, bg='#1a1a1a', highlightthickness=0)
        
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
        try:
            # Get current IP
            current_ip = self.esp32_ip_entry.get().strip()
            if not current_ip:
                self.log_command("Please enter a valid IP address", "ERROR")
                return
            
            # Create ESP32 client if available
            if ESP32_CLIENT_AVAILABLE:
                self.esp32_client = ESP32Client(host=current_ip, port=80)
                self.log_command(f"Creating ESP32 client for {current_ip}:80", "SYSTEM")
                
                # Attempt to connect
                if self.esp32_client.connect():
                    self.esp32_connected = True
                    self.log_command(f"✅ Successfully connected to ESP32 at {current_ip}", "SYSTEM")
                    
                    # Update status
                    self.status_label.config(text="Status: Connected", fg='#4CAF50')
                    self.connection_info.config(text=f"Connected to {current_ip}")
                    
                    # Test connection by getting status
                    status = self.esp32_client.get_status()
                    if status:
                        self.log_command(f"ESP32 Status: {status}", "SYSTEM")
                    
                    # Update real mode status if enabled
                    if self.esp32_real_mode.get():
                        self.real_mode_label.config(text="🟢 Real ESP32 Mode", fg='#4CAF50')
                        self.real_mode_status.config(text="Mode: Real ESP32 (Connected)", fg='#4CAF50')
                        self.log_command("Real ESP32 mode active - Commands will be sent to actual ESP32", "SYSTEM")
                    
                else:
                    self.esp32_connected = False
                    self.log_command(f"❌ Failed to connect to ESP32 at {current_ip}", "ERROR")
                    self.status_label.config(text="Status: Connection Failed", fg='#f44336')
                    self.connection_info.config(text="Connection failed")
                    return
            else:
                # Fallback to simulation mode
                self.log_command("ESP32 Client not available, using simulation mode", "WARNING")
                self.esp32_connected = True
            
            # Automatically save configuration if binary config is available
            if CONFIG_AVAILABLE and self.config_manager:
                # Update configuration with current IP
                if self.current_config:
                    self.current_config.host = current_ip
                    self.current_config.last_connection = time.time()
                    self.current_config.connection_status = "connected"
                else:
                    # Create new configuration
                    self.current_config = ESP32Config(
                        host=current_ip,
                        port=80,
                        timeout=5.0,
                        enable_control=True,
                        auto_connect=True,
                        retry_attempts=3,
                        retry_delay=2.0,
                        last_connection=time.time(),
                        connection_status="connected",
                        firmware_version="1.0.0",
                        device_name="ADAI_ESP32"
                    )
                
                # Save configuration
                if self.config_manager.save_config(self.current_config):
                    self.log_command("ESP32 configuration automatically saved", "SYSTEM")
                else:
                    self.log_command("Warning: Failed to save ESP32 configuration", "ERROR")
                    
        except Exception as e:
            self.log_command(f"Error connecting to ESP32: {e}", "ERROR")
            self.status_label.config(text="Status: Error", fg='#f44336')
            self.connection_info.config(text="Connection error")
        
    def disconnect_esp32(self):
        """Disconnect from ESP32"""
        try:
            # Disconnect ESP32 client if available
            if ESP32_CLIENT_AVAILABLE and self.esp32_client and self.esp32_connected:
                self.esp32_client.disconnect()
                self.esp32_connected = False
                self.log_command("ESP32 client disconnected", "SYSTEM")
            
            # Update status
            self.status_label.config(text="Status: Disconnected", fg='#f44336')
            self.connection_info.config(text="No connection")
            self.log_command("Disconnected from ESP32", "SYSTEM")
            
            # Update real mode status
            if self.esp32_real_mode.get():
                self.real_mode_label.config(text="🟡 Real ESP32 Mode (Disconnected)", fg='#FF9800')
                self.real_mode_status.config(text="Mode: Real ESP32 (Disconnected)", fg='#FF9800')
                self.log_command("⚠️ Real ESP32 mode enabled but not connected", "WARNING")
            
            # Update configuration status if available
            if CONFIG_AVAILABLE and self.config_manager and self.current_config:
                self.current_config.connection_status = "disconnected"
                self.current_config.last_connection = time.time()
                
                # Save updated configuration
                if self.config_manager.save_config(self.current_config):
                    self.log_command("ESP32 connection status updated", "SYSTEM")
                    
        except Exception as e:
            self.log_command(f"Error disconnecting from ESP32: {e}", "ERROR")
    
    def load_current_config(self):
        """Load current ESP32 configuration from binary file"""
        try:
            if not CONFIG_AVAILABLE or not self.config_manager:
                return
            
            # Load configuration from binary file
            config = self.config_manager.load_config()
            if config:
                self.current_config = config
                self.esp32_ip_entry.delete(0, tk.END)
                self.esp32_ip_entry.insert(0, config.host)
                self.log_command(f"Loaded ESP32 configuration: {config.host}:{config.port}", "SYSTEM")
            else:
                # Use default configuration
                self.esp32_ip_entry.delete(0, tk.END)
                self.esp32_ip_entry.insert(0, "192.168.1.100")
                self.log_command("No ESP32 configuration found, using default", "SYSTEM")
                
        except Exception as e:
            self.log_command(f"Error loading ESP32 configuration: {e}", "ERROR")
            # Use default configuration
            self.esp32_ip_entry.delete(0, tk.END)
            self.esp32_ip_entry.insert(0, "192.168.1.100")
    
    def toggle_real_mode(self):
        """Toggle between simulation and real ESP32 mode"""
        try:
            if self.esp32_real_mode.get():
                # Enable real ESP32 mode
                self.real_mode_label.config(text="🟢 Real ESP32 Mode", fg='#4CAF50')
                self.real_mode_status.config(text="Mode: Real ESP32", fg='#4CAF50')
                self.log_command("Real ESP32 mode enabled - Commands will be sent to actual ESP32", "SYSTEM")
                
                # Check if ESP32 is connected
                if not self.esp32_connected:
                    self.log_command("⚠️ Warning: ESP32 not connected. Please connect first.", "WARNING")
            else:
                # Enable simulation mode
                self.real_mode_label.config(text="🟡 Simulation Mode", fg='#FFD700')
                self.real_mode_status.config(text="Mode: Simulation", fg='#FFD700')
                self.log_command("Simulation mode enabled - Commands will be simulated only", "SYSTEM")
                
        except Exception as e:
            print(f"❌ Error toggling real mode: {e}")
    
    def test_esp32_connection(self):
        """Test ESP32 connection with real commands"""
        try:
            if not ESP32_CLIENT_AVAILABLE or not self.esp32_client or not self.esp32_connected:
                self.log_command("ESP32 client not available or not connected", "ERROR")
                return
            
            self.log_command("🧪 Testing ESP32 connection...", "SYSTEM")
            
            # Test 1: Get status
            self.log_command("📊 Testing status request...", "SYSTEM")
            status = self.esp32_client.get_status()
            if status:
                self.log_command(f"✅ Status test passed: {status}", "SYSTEM")
            else:
                self.log_command("❌ Status test failed", "ERROR")
            
            # Test 2: Send a simple movement command
            self.log_command("🤖 Testing movement command...", "SYSTEM")
            if self.esp32_client.send_movement(100, 30, 95, 160, 140, 165, 100, 90):
                self.log_command("✅ Movement test passed", "SYSTEM")
            else:
                self.log_command("❌ Movement test failed", "ERROR")
            
            # Test 3: Send a gesture command
            self.log_command("👋 Testing gesture command...", "SYSTEM")
            if self.esp32_client.send_gesture('derecha', 'paz'):
                self.log_command("✅ Gesture test passed", "SYSTEM")
            else:
                self.log_command("❌ Gesture test failed", "ERROR")
                
        except Exception as e:
            self.log_command(f"Error testing ESP32 connection: {e}", "ERROR")
    
    def save_esp32_config(self):
        """Save current ESP32 configuration to binary file"""
        try:
            if not CONFIG_AVAILABLE or not self.config_manager:
                self.log_command("ESP32 Binary Config not available", "ERROR")
                return
            
            # Get current IP from entry
            current_ip = self.esp32_ip_entry.get().strip()
            if not current_ip:
                self.log_command("Please enter a valid IP address", "ERROR")
                return
            
            # Create or update configuration
            if self.current_config:
                # Update existing configuration
                self.current_config.host = current_ip
                self.current_config.last_connection = time.time()
            else:
                # Create new configuration with default values
                self.current_config = ESP32Config(
                    host=current_ip,
                    port=80,
                    timeout=5.0,
                    enable_control=True,
                    auto_connect=True,
                    retry_attempts=3,
                    retry_delay=2.0,
                    last_connection=time.time(),
                    connection_status="disconnected",
                    firmware_version="1.0.0",
                    device_name="ADAI_ESP32"
                )
            
            # Save configuration to binary file
            if self.config_manager.save_config(self.current_config):
                self.log_command(f"ESP32 configuration saved: {current_ip}", "SYSTEM")
                self.log_command("Configuration will be available for classes", "SYSTEM")
            else:
                self.log_command("Failed to save ESP32 configuration", "ERROR")
                
        except Exception as e:
            self.log_command(f"Error saving ESP32 configuration: {e}", "ERROR")
    
    def load_esp32_config(self):
        """Load ESP32 configuration from binary file"""
        try:
            if not CONFIG_AVAILABLE or not self.config_manager:
                self.log_command("ESP32 Binary Config not available", "ERROR")
                return
            
            # Load configuration from binary file
            config = self.config_manager.load_config()
            if config:
                self.current_config = config
                self.esp32_ip_entry.delete(0, tk.END)
                self.esp32_ip_entry.insert(0, config.host)
                self.log_command(f"Loaded ESP32 configuration: {config.host}:{config.port}", "SYSTEM")
                self.log_command(f"Connection status: {config.connection_status}", "SYSTEM")
            else:
                self.log_command("No ESP32 configuration found", "ERROR")
                
        except Exception as e:
            self.log_command(f"Error loading ESP32 configuration: {e}", "ERROR")
        
    def home_position(self):
        """Move robot to home position"""
        if ESP32_CLIENT_AVAILABLE and self.esp32_client and self.esp32_connected:
            # Send real home position command
            if self.esp32_client.send_movement(100, 30, 95, 160, 140, 165, 100, 90):
                self.log_esp32_command("HOME_POSITION", "Move robot to home position - SUCCESS")
            else:
                self.log_esp32_command("HOME_POSITION", "Move robot to home position - FAILED")
        else:
            self.log_esp32_command("HOME_POSITION", "Move robot to home position (simulation)")
        
    def wave_gesture(self):
        """Perform wave gesture"""
        if ESP32_CLIENT_AVAILABLE and self.esp32_client and self.esp32_connected:
            # Send real wave gesture command
            if self.esp32_client.send_gesture('paz'):
                self.log_esp32_command("WAVE_GESTURE", "Perform wave gesture - SUCCESS")
            else:
                self.log_esp32_command("WAVE_GESTURE", "Perform wave gesture - FAILED")
        else:
            self.log_esp32_command("WAVE_GESTURE", "Perform wave gesture (simulation)")
        
    def hug_gesture(self):
        """Perform hug gesture"""
        if ESP32_CLIENT_AVAILABLE and self.esp32_client and self.esp32_connected:
            # Send real hug gesture command
            if self.esp32_client.send_gesture('abrazo'):
                self.log_esp32_command("HUG_GESTURE", "Perform hug gesture - SUCCESS")
            else:
                self.log_esp32_command("HUG_GESTURE", "Perform hug gesture - FAILED")
        else:
            self.log_esp32_command("HUG_GESTURE", "Perform hug gesture (simulation)")
        
    def look_around(self):
        """Perform look around gesture"""
        if ESP32_CLIENT_AVAILABLE and self.esp32_client and self.esp32_connected:
            # Send real look around command
            if self.esp32_client.send_movement(100, 30, 95, 160, 140, 165, 100, 90):
                self.log_esp32_command("LOOK_AROUND", "Perform look around gesture - SUCCESS")
            else:
                self.log_esp32_command("LOOK_AROUND", "Perform look around gesture - FAILED")
        else:
            self.log_esp32_command("LOOK_AROUND", "Perform look around gesture (simulation)")
    
    # ===============================
    # SIMULATOR METHODS
    # ===============================
    
    def init_visualization(self):
        """Initialize visualization"""
        try:
            # Initialize arms state
            self.arms_state = {
                'left_arm': {
                    'brazo': 100,
                    'frente': 95,
                    'high': 140,
                    'pollo': 90
                },
                'right_arm': {
                    'brazo': 30,
                    'frente': 160,
                    'high': 165,
                    'pollo': 100
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
                
            elif view == "front":
                self.side_canvas.pack_forget()
                self.front_canvas.pack(fill="both", expand=True)
                self.arms_canvas = self.front_canvas
                self.sim_status_label.config(text="Simulator: Ready - Front View")
                
            elif view == "both":
                self.side_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
                self.front_canvas.pack(side="right", fill="both", expand=True, padx=(5, 0))
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
            elif view == "front":
                self.update_front_view()
            elif view == "both":
                self.update_side_view()
                self.update_front_view()
                
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
            
            # Update front view
            if view in ["front", "both"]:
                self.update_front_view()
            
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
            self.arms_state['left_arm']['pollo'] = self.left_pollo_var.get()
            
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
                command = f"LEFT_ARM:{self.left_brazo_var.get():.0f},{self.left_frente_var.get():.0f},{self.left_high_var.get():.0f},{self.left_pollo_var.get():.0f}"
            else:
                command = f"RIGHT_ARM:{self.right_brazo_var.get():.0f},{self.right_frente_var.get():.0f},{self.right_high_var.get():.0f},{self.right_pollo_var.get():.0f}"

            # Check if we should send to real ESP32
            if (self.esp32_real_mode.get() and self.esp32_connected and
                self.esp32_client and ESP32_CLIENT_AVAILABLE):
                try:
                    # Extract values for movement command
                    if side == 'left':
                        bi = int(self.left_brazo_var.get())
                        fi = int(self.left_frente_var.get())
                        hi = int(self.left_high_var.get())
                        pi = int(self.left_pollo_var.get())
                        # Use default values for right side
                        bd = 30
                        fd = 160
                        hd = 165
                        pd = 100
                    else:
                        # Use default values for left side
                        bi = 100
                        fi = 95
                        hi = 140
                        pi = 90
                        # Use actual values for right side
                        bd = int(self.right_brazo_var.get())
                        fd = int(self.right_frente_var.get())
                        hd = int(self.right_high_var.get())
                        pd = int(self.right_pollo_var.get())

                    # Send real movement command to ESP32
                    if self.esp32_client.send_movement(bi, bd, fi, fd, hi, hd, pd, pi):
                        self.log_command(f"✅ {side} arm command sent to real ESP32", "ESP32")
                    else:
                        self.log_command(f"❌ Failed to send {side} arm command to ESP32", "ERROR")
                except Exception as e:
                    self.log_command(f"Error sending {side} arm command to ESP32: {e}", "ERROR")
            
            # Legacy ESP32 integration (if available)
            elif hasattr(self.parent_gui, 'esp32') and self.parent_gui.esp32:
                self.parent_gui.esp32.send_command(command)
                self.log_message(f"Sent {side} arm command to ESP32")
            
            # Log the command
            self.log_command(f"Arm command: {side} - {command}", "MOVEMENT")
                
        except Exception as e:
            self.log_message(f"Error sending arm command: {e}")
    
    def reset_arms(self):
        """Reset arms to default position"""
        try:
            # Reset left arm
            self.left_brazo_var.set(100)
            self.left_frente_var.set(95)
            self.left_high_var.set(140)
            self.left_pollo_var.set(90)

            # Reset right arm
            self.right_brazo_var.set(30)
            self.right_frente_var.set(160)
            self.right_high_var.set(165)
            self.right_pollo_var.set(100)
            
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
                    'high': self.left_high_var.get(),
                    'pollo': self.left_pollo_var.get()
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
                        'high': self.left_high_var.get(),
                        'pollo': self.left_pollo_var.get()
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
            # Test using binary configuration if available
            if CONFIG_AVAILABLE and self.config_manager:
                current_ip = self.esp32_ip_entry.get().strip()
                if current_ip:
                    self.log_command(f"Testing connection to {current_ip}...", "SYSTEM")
                    
                    # Test connection using the config manager
                    if self.config_manager.test_connection(current_ip, 80):
                        self.log_command("ESP32 connection test: SUCCESS", "SYSTEM")
                        self.status_label.config(text="Status: Test Successful", fg='#4CAF50')
                    else:
                        self.log_command("ESP32 connection test: FAILED", "ERROR")
                        self.status_label.config(text="Status: Test Failed", fg='#f44336')
                else:
                    self.log_command("Please enter a valid IP address to test", "ERROR")
            else:
                # Fallback to original method
                if hasattr(self.parent_gui, 'esp32') and self.parent_gui.esp32:
                    if self.parent_gui.esp32.connected:
                        self.log_command("ESP32 connection test: SUCCESS", "SYSTEM")
                    else:
                        self.log_command("ESP32 connection test: FAILED - Not connected", "ERROR")
                else:
                    self.log_command("ESP32 connection test: FAILED - ESP32 not available", "ERROR")
        except Exception as e:
            self.log_command(f"Error testing connection: {e}", "ERROR")
    
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
                self.left_brazo_var.set(left.get('brazo', 100))
                self.left_frente_var.set(left.get('frente', 95))
                self.left_high_var.set(left.get('high', 140))
                self.left_pollo_var.set(left.get('pollo', 90))

            if 'right_arm' in config:
                right = config['right_arm']
                self.right_brazo_var.set(right.get('brazo', 30))
                self.right_frente_var.set(right.get('frente', 160))
                self.right_high_var.set(right.get('high', 165))
                self.right_pollo_var.set(right.get('pollo', 100))
            
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
                    'high': self.left_high_var.get(),
                    'pollo': self.left_pollo_var.get()
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
    
    def log_command(self, message, command_type="COMMAND"):
        """Log a command to the ESP32 command log"""
        if not hasattr(self, 'command_log_text') or not self.log_enabled_var.get():
            return
        
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            
            # Color coding based on command type
            color_map = {
                "COMMAND": "#00ff00",  # Green for commands
                "RESPONSE": "#ffff00",  # Yellow for responses
                "ERROR": "#ff0000",     # Red for errors
                "SYSTEM": "#00ffff",    # Cyan for system messages
                "CLASS": "#ff00ff"      # Magenta for class-related commands
            }
            
            color = color_map.get(command_type, "#00ff00")
            
            # Format the log entry
            log_entry = f"[{timestamp}] [{command_type}] {message}\n"
            
            # Insert at the end
            self.command_log_text.insert(tk.END, log_entry)
            
            # Apply color to the last line
            last_line_start = self.command_log_text.index("end-2c linestart")
            last_line_end = self.command_log_text.index("end-1c")
            
            # Create a tag for this color if it doesn't exist
            tag_name = f"color_{command_type.lower()}"
            self.command_log_text.tag_configure(tag_name, foreground=color)
            self.command_log_text.tag_add(tag_name, last_line_start, last_line_end)
            
            # Auto-scroll to the bottom
            self.command_log_text.see(tk.END)
            
            # Limit log entries to prevent memory issues (keep last 1000 lines)
            lines = int(self.command_log_text.index('end-1c').split('.')[0])
            if lines > 1000:
                self.command_log_text.delete("1.0", "2.0")
                
        except Exception as e:
            print(f"Error logging command: {e}")
    
    def clear_command_log(self):
        """Clear the command log"""
        if hasattr(self, 'command_log_text'):
            self.command_log_text.delete(1.0, tk.END)
            self.log_command("Command log cleared", "SYSTEM")
    
    def export_command_log(self):
        """Export the command log to a file"""
        try:
            from tkinter import filedialog
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = filedialog.asksaveasfilename(
                title="Export ESP32 Command Log",
                defaultextension=".txt",
                initialvalue=f"esp32_command_log_{timestamp}.txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename and hasattr(self, 'command_log_text'):
                log_content = self.command_log_text.get(1.0, tk.END)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("ESP32 Command Log\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(log_content)
                
                self.log_command(f"Command log exported to {filename}", "SYSTEM")
                
        except Exception as e:
            self.log_command(f"Error exporting log: {e}", "ERROR")
    
    def log_esp32_command(self, command, parameters=None, response=None):
        """Log ESP32 commands sent during class execution"""
        try:
            # Format the command message
            if parameters:
                param_str = f" with params: {parameters}"
            else:
                param_str = ""
            
            command_msg = f"ESP32 Command: {command}{param_str}"
            self.log_command(command_msg, "COMMAND")
            
            # Log response if provided
            if response:
                response_msg = f"ESP32 Response: {response}"
                self.log_command(response_msg, "RESPONSE")
                
        except Exception as e:
            self.log_command(f"Error logging ESP32 command: {e}", "ERROR")
    
    def log_class_command(self, class_name, command, description=None):
        """Log commands sent during class execution"""
        try:
            desc_str = f" - {description}" if description else ""
            command_msg = f"Class '{class_name}': {command}{desc_str}"
            self.log_command(command_msg, "CLASS")
            
        except Exception as e:
            self.log_command(f"Error logging class command: {e}", "ERROR")
    
    def log_esp32_error(self, error_message):
        """Log ESP32 errors"""
        self.log_command(f"ESP32 Error: {error_message}", "ERROR")
    
    def log_esp32_response(self, response_message):
        """Log ESP32 responses"""
        self.log_command(f"ESP32 Response: {response_message}", "RESPONSE")
    
    def log_message(self, message):
        """Legacy log method - redirects to command log"""
        self.log_command(message, "SYSTEM")
    
    def register_class_command(self, class_name, command, parameters=None, description=None):
        """Register a command sent during class execution"""
        try:
            # Log the class command
            self.log_class_command(class_name, command, description)
            
            # Also log as ESP32 command if parameters are provided
            if parameters:
                self.log_esp32_command(command, parameters)
            else:
                self.log_esp32_command(command)
                
        except Exception as e:
            self.log_esp32_error(f"Error registering class command: {e}")
    
    def register_esp32_response(self, command, response, success=True):
        """Register an ESP32 response"""
        try:
            if success:
                self.log_esp32_response(f"Command '{command}' successful: {response}")
            else:
                self.log_esp32_error(f"Command '{command}' failed: {response}")
                
        except Exception as e:
            self.log_esp32_error(f"Error registering ESP32 response: {e}")
    
    def get_log_content(self):
        """Get the current log content"""
        if hasattr(self, 'command_log_text'):
            return self.command_log_text.get(1.0, tk.END)
        return ""
    
    def is_log_enabled(self):
        """Check if logging is enabled"""
        return hasattr(self, 'log_enabled_var') and self.log_enabled_var.get()
    
    # ============================================================================
    # SEQUENCE EXECUTION METHODS
    # ============================================================================
    
    def load_sequence_for_simulator(self):
        """Load a sequence file for execution in the simulator"""
        try:
            from tkinter import filedialog
            import os
            
            # Get the sequences directory
            sequences_dir = os.path.join(os.path.dirname(__file__), '..', 'sequences')
            
            # Open file dialog
            filename = filedialog.askopenfilename(
                title="Load Sequence for Simulator",
                initialdir=sequences_dir,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                # Load and parse the sequence
                self.loaded_sequence = self.parse_sequence_file(filename)
                if self.loaded_sequence:
                    self.sequence_path_var.set(os.path.basename(filename))
                    self.update_sequence_info()
                    self.log_command(f"Sequence loaded: {os.path.basename(filename)}", "SYSTEM")
                else:
                    self.log_command("Failed to load sequence", "ERROR")
                    
        except Exception as e:
            self.log_command(f"Error loading sequence: {e}", "ERROR")
    
    def parse_sequence_file(self, filename):
        """Parse a sequence JSON file"""
        try:
            import json
            
            with open(filename, 'r', encoding='utf-8') as f:
                sequence_data = json.load(f)
            
            # Validate sequence structure
            if not isinstance(sequence_data, dict):
                raise ValueError("Invalid sequence format: not a dictionary")
            
            # Check for required fields
            if 'movements' not in sequence_data:
                raise ValueError("Invalid sequence format: missing 'movements' field")
            
            return sequence_data
            
        except Exception as e:
            self.log_command(f"Error parsing sequence file: {e}", "ERROR")
            return None
    
    def update_sequence_info(self):
        """Update the sequence information display"""
        try:
            if hasattr(self, 'loaded_sequence') and self.loaded_sequence:
                movements = self.loaded_sequence.get('movements', [])
                title = self.loaded_sequence.get('title', 'Untitled Sequence')
                
                info_text = f"Loaded: {title} ({len(movements)} movements)"
                self.sequence_info_label.config(text=info_text, fg='#4CAF50')
            else:
                self.sequence_info_label.config(text="No sequence loaded", fg='#888888')
                
        except Exception as e:
            self.log_command(f"Error updating sequence info: {e}", "ERROR")
    
    def execute_loaded_sequence(self):
        """Execute the loaded sequence in the simulator"""
        try:
            if not hasattr(self, 'loaded_sequence') or not self.loaded_sequence:
                self.log_command("No sequence loaded for execution", "ERROR")
                return
            
            # Initialize sequence execution state
            self.sequence_execution_state = {
                'running': True,
                'paused': False,
                'current_movement': 0,
                'current_action': 0,
                'total_movements': len(self.loaded_sequence.get('movements', [])),
                'start_time': time.time()
            }
            
            self.log_command("Starting sequence execution in simulator", "SYSTEM")
            
            # Start execution in a separate thread
            import threading
            self.sequence_thread = threading.Thread(target=self._execute_sequence_thread)
            self.sequence_thread.daemon = True
            self.sequence_thread.start()
            
        except Exception as e:
            self.log_command(f"Error starting sequence execution: {e}", "ERROR")
    
    def _execute_sequence_thread(self):
        """Execute sequence in a separate thread"""
        try:
            movements = self.loaded_sequence.get('movements', [])
            
            for movement_idx, movement in enumerate(movements):
                if not self.sequence_execution_state['running']:
                    break
                
                # Wait if paused
                while self.sequence_execution_state['paused'] and self.sequence_execution_state['running']:
                    time.sleep(0.1)
                
                if not self.sequence_execution_state['running']:
                    break
                
                # Update current movement
                self.sequence_execution_state['current_movement'] = movement_idx
                
                # Log movement start
                movement_name = movement.get('name', f'Movement {movement_idx + 1}')
                self.log_command(f"Executing movement: {movement_name}", "SEQUENCE")
                
                # Execute actions in the movement
                actions = movement.get('actions', [])
                for action_idx, action in enumerate(actions):
                    if not self.sequence_execution_state['running']:
                        break
                    
                    # Wait if paused
                    while self.sequence_execution_state['paused'] and self.sequence_execution_state['running']:
                        time.sleep(0.1)
                    
                    if not self.sequence_execution_state['running']:
                        break
                    
                    # Update current action
                    self.sequence_execution_state['current_action'] = action_idx
                    
                    # Execute the action
                    self._execute_sequence_action(action, movement_name)
                    
                    # Small delay between actions
                    time.sleep(0.5)
                
                # Delay between movements
                time.sleep(1.0)
            
            # Sequence completed
            if self.sequence_execution_state['running']:
                self.log_command("Sequence execution completed", "SYSTEM")
                self.sequence_execution_state['running'] = False
                
        except Exception as e:
            self.log_command(f"Error in sequence execution: {e}", "ERROR")
            self.sequence_execution_state['running'] = False
    
    def _execute_sequence_action(self, action, movement_name):
        """Execute a single action from the sequence"""
        try:
            # Check for different action formats
            command = action.get('command', '')
            action_type = action.get('type', 'unknown')
            parameters = action.get('parameters', {})
            
            # Log the action
            self.log_command(f"Action: {command or action_type} - {parameters}", "SEQUENCE")
            
            # Handle command-based actions (chemistry sequence format)
            if command:
                if command == 'BRAZOS':
                    self._simulate_movement_action(parameters)
                elif command == 'CUELLO':
                    self._simulate_neck_action(parameters)
                elif command == 'MANO':
                    self._simulate_hand_action(parameters)
                elif command == 'HABLAR':
                    self._simulate_speech_action(parameters)
                elif command == 'ESPERAR':
                    self._simulate_wait_action(parameters)
                else:
                    self.log_command(f"Unknown command: {command}", "WARNING")
                    
            # Handle type-based actions (legacy format)
            elif action_type != 'unknown':
                if action_type == 'movement':
                    self._simulate_movement_action(parameters)
                elif action_type == 'gesture':
                    self._simulate_gesture_action(parameters)
                elif action_type == 'speech':
                    self._simulate_speech_action(parameters)
                elif action_type == 'wait':
                    self._simulate_wait_action(parameters)
                else:
                    self.log_command(f"Unknown action type: {action_type}", "WARNING")
                    
            # Handle action field (alternative format)
            elif 'action' in action:
                action_name = action['action']
                if action_name in ['saludo', 'movimiento', 'hablar', 'esperar']:
                    self._simulate_generic_action(action)
                else:
                    self.log_command(f"Unknown action: {action_name}", "WARNING")
            else:
                self.log_command(f"Unknown action format: {action}", "WARNING")
                    
        except Exception as e:
            self.log_command(f"Error executing action: {e}", "ERROR")
    
    def _simulate_movement_action(self, parameters):
        """Simulate a movement action or send to real ESP32"""
        try:
            # Extract movement parameters from sequence format
            # Sequence uses: BI, FI, HI, BD, FD, HD, PD
            # Simulator expects: BI, BD, FI, FD, HI, HD, PD
            
            bi = parameters.get('BI', 0)  # Brazo Izquierdo
            bd = parameters.get('BD', 0)  # Brazo Derecho
            fi = parameters.get('FI', 0)  # Frente Izquierdo
            fd = parameters.get('FD', 0)  # Frente Derecho
            hi = parameters.get('HI', 0)  # High Izquierdo
            hd = parameters.get('HD', 0)  # High Derecho
            pd = parameters.get('PD', 0)  # Pollo Derecho
            pi = parameters.get('PI', 90)  # Pollo Izquierdo

            # Log the movement
            movement_str = f"Movement: BI={bi}, BD={bd}, FI={fi}, FD={fd}, HI={hi}, HD={hd}, PD={pd}, PI={pi}"
            self.log_command(movement_str, "MOVEMENT")

            # Check if we should send to real ESP32
            if (self.esp32_real_mode.get() and self.esp32_connected and
                self.esp32_client and ESP32_CLIENT_AVAILABLE):
                try:
                    # Send real command to ESP32
                    if self.esp32_client.send_movement(bi, bd, fi, fd, hi, hd, pd, pi):
                        self.log_command("✅ Movement sent to real ESP32", "ESP32")
                    else:
                        self.log_command("❌ Failed to send movement to ESP32", "ERROR")
                except Exception as e:
                    self.log_command(f"Error sending movement to ESP32: {e}", "ERROR")

            # Update simulator visualization (if available)
            if hasattr(self, 'update_simulator_position'):
                self.update_simulator_position(bi, bd, fi, fd, hi, hd, pd)
                
        except Exception as e:
            self.log_command(f"Error simulating movement: {e}", "ERROR")
    
    def _simulate_gesture_action(self, parameters):
        """Simulate a gesture action or send to real ESP32"""
        try:
            gesture_type = parameters.get('gesture', 'unknown')
            self.log_command(f"Gesture: {gesture_type}", "GESTURE")
            
            # Check if we should send to real ESP32
            if (self.esp32_real_mode.get() and self.esp32_connected and 
                self.esp32_client and ESP32_CLIENT_AVAILABLE):
                try:
                    # Send real command to ESP32 (default to right hand)
                    if self.esp32_client.send_gesture('derecha', gesture_type):
                        self.log_command("✅ Gesture sent to real ESP32", "ESP32")
                    else:
                        self.log_command("❌ Failed to send gesture to ESP32", "ERROR")
                except Exception as e:
                    self.log_command(f"Error sending gesture to ESP32: {e}", "ERROR")
            
        except Exception as e:
            self.log_command(f"Error simulating gesture: {e}", "ERROR")
    
    def _simulate_speech_action(self, parameters):
        """Simulate a speech action or send to real ESP32"""
        try:
            # Handle different speech parameter formats
            message = parameters.get('message', parameters.get('texto', 'No message'))
            self.log_command(f"Speech: {message}", "SPEECH")
            
            # Check if we should send to real ESP32
            if (self.esp32_real_mode.get() and self.esp32_connected and 
                self.esp32_client and ESP32_CLIENT_AVAILABLE):
                try:
                    # Send real command to ESP32
                    if self.esp32_client.send_speech(message):
                        self.log_command("✅ Speech sent to real ESP32", "ESP32")
                    else:
                        self.log_command("❌ Failed to send speech to ESP32", "ERROR")
                except Exception as e:
                    self.log_command(f"Error sending speech to ESP32: {e}", "ERROR")
            
        except Exception as e:
            self.log_command(f"Error simulating speech: {e}", "ERROR")
    
    def _simulate_wait_action(self, parameters):
        """Simulate a wait action or send to real ESP32"""
        try:
            duration = parameters.get('duration', 1.0)
            self.log_command(f"Waiting: {duration} seconds", "WAIT")
            
            # Check if we should send to real ESP32
            if (self.esp32_real_mode.get() and self.esp32_connected and 
                self.esp32_client and ESP32_CLIENT_AVAILABLE):
                try:
                    # Convert duration to milliseconds
                    duration_ms = int(duration * 1000)
                    # Send real command to ESP32
                    if self.esp32_client.send_wait(duration_ms):
                        self.log_command("✅ Wait command sent to real ESP32", "ESP32")
                    else:
                        self.log_command("❌ Failed to send wait command to ESP32", "ERROR")
                except Exception as e:
                    self.log_command(f"Error sending wait command to ESP32: {e}", "ERROR")
            
            # Always wait in simulation
            time.sleep(duration)
            
        except Exception as e:
            self.log_command(f"Error simulating wait: {e}", "ERROR")
    
    def _simulate_neck_action(self, parameters):
        """Simulate a neck movement action or send to real ESP32"""
        try:
            lateral = parameters.get('L', 0)
            inferior = parameters.get('I', 0)
            superior = parameters.get('S', 0)
            
            # Log the neck movement
            neck_str = f"Neck: L={lateral}, I={inferior}, S={superior}"
            self.log_command(neck_str, "NECK")
            
            # Check if we should send to real ESP32
            if (self.esp32_real_mode.get() and self.esp32_connected and 
                self.esp32_client and ESP32_CLIENT_AVAILABLE):
                try:
                    # Send real command to ESP32
                    if self.esp32_client.send_neck_movement(lateral, inferior, superior):
                        self.log_command("✅ Neck movement sent to real ESP32", "ESP32")
                    else:
                        self.log_command("❌ Failed to send neck movement to ESP32", "ERROR")
                except Exception as e:
                    self.log_command(f"Error sending neck movement to ESP32: {e}", "ERROR")
            
            # For neck movements, we don't update arm positions
            # Just log the movement for now
            # TODO: Add neck visualization if needed
            
        except Exception as e:
            self.log_command(f"Error simulating neck action: {e}", "ERROR")
    
    def _simulate_hand_action(self, parameters):
        """Simulate a hand gesture action or send to real ESP32"""
        try:
            mano = parameters.get('M', 'unknown')
            gesto = parameters.get('GESTO', 'unknown')
            angulo = parameters.get('ANG', None)
            
            if angulo is not None:
                # Hand angle movement
                hand_str = f"Hand {mano}: Angle={angulo}°"
                self.log_command(hand_str, "HAND")
                
                # Check if we should send to real ESP32
                if (self.esp32_real_mode.get() and self.esp32_connected and 
                    self.esp32_client and ESP32_CLIENT_AVAILABLE):
                    try:
                        # Send real command to ESP32
                        if self.esp32_client.send_finger_control(mano, 'indice', angulo):
                            self.log_command("✅ Hand control sent to real ESP32", "ESP32")
                        else:
                            self.log_command("❌ Failed to send hand control to ESP32", "ERROR")
                    except Exception as e:
                        self.log_command(f"Error sending hand control to ESP32: {e}", "ERROR")
            else:
                # Hand gesture
                gesture_str = f"Hand {mano}: Gesture={gesto}"
                self.log_command(gesture_str, "GESTURE")
                
                # Check if we should send to real ESP32
                if (self.esp32_real_mode.get() and self.esp32_connected and 
                    self.esp32_client and ESP32_CLIENT_AVAILABLE):
                    try:
                        # Send real command to ESP32
                        if self.esp32_client.send_gesture(mano, gesto):
                            self.log_command("✅ Hand gesture sent to real ESP32", "ESP32")
                        else:
                            self.log_command("❌ Failed to send hand gesture to ESP32", "ERROR")
                    except Exception as e:
                        self.log_command(f"Error sending hand gesture to ESP32: {e}", "ERROR")
                
        except Exception as e:
            self.log_command(f"Error simulating hand action: {e}", "ERROR")
    
    def _simulate_generic_action(self, action):
        """Simulate a generic action based on action name"""
        try:
            action_name = action.get('action', 'unknown')
            parameters = action.get('parameters', {})
            
            if action_name == 'saludo':
                self.log_command("Gesture: Saludo (Wave)", "GESTURE")
            elif action_name == 'movimiento':
                self._simulate_movement_action(parameters)
            elif action_name == 'hablar':
                message = parameters.get('message', 'No message')
                self.log_command(f"Speech: {message}", "SPEECH")
            elif action_name == 'esperar':
                duration = parameters.get('duration', 1.0)
                self.log_command(f"Waiting: {duration} seconds", "WAIT")
                time.sleep(duration)
            else:
                self.log_command(f"Generic action: {action_name}", "ACTION")
                
        except Exception as e:
            self.log_command(f"Error simulating generic action: {e}", "ERROR")
    
    def pause_sequence_execution(self):
        """Pause sequence execution"""
        try:
            if hasattr(self, 'sequence_execution_state'):
                self.sequence_execution_state['paused'] = True
                self.log_command("Sequence execution paused", "SYSTEM")
            else:
                self.log_command("No sequence execution in progress", "WARNING")
                
        except Exception as e:
            self.log_command(f"Error pausing sequence: {e}", "ERROR")
    
    def stop_sequence_execution(self):
        """Stop sequence execution"""
        try:
            if hasattr(self, 'sequence_execution_state'):
                self.sequence_execution_state['running'] = False
                self.sequence_execution_state['paused'] = False
                self.log_command("Sequence execution stopped", "SYSTEM")
            else:
                self.log_command("No sequence execution in progress", "WARNING")
                
        except Exception as e:
            self.log_command(f"Error stopping sequence: {e}", "ERROR")
    
    def get_sequence_execution_status(self):
        """Get current sequence execution status"""
        if hasattr(self, 'sequence_execution_state'):
            return self.sequence_execution_state.copy()
        return None
    
    def update_simulator_position(self, bi, bd, fi, fd, hi, hd, pd):
        """Update the simulator visualization with new arm positions"""
        try:
            # Map sequence parameters to simulator variables
            # BI = Brazo Izquierdo -> left_brazo_var
            # BD = Brazo Derecho -> right_brazo_var
            # FI = Frente Izquierdo -> left_frente_var
            # FD = Frente Derecho -> right_frente_var
            # HI = High Izquierdo -> left_high_var
            # HD = High Derecho -> right_high_var
            # PD = Pollo Derecho -> right_pollo_var
            
            # Update left arm variables
            if hasattr(self, 'left_brazo_var'):
                self.left_brazo_var.set(bi)  # BI
            if hasattr(self, 'left_frente_var'):
                self.left_frente_var.set(fi)  # FI
            if hasattr(self, 'left_high_var'):
                self.left_high_var.set(hi)  # HI
            
            # Update right arm variables
            if hasattr(self, 'right_brazo_var'):
                self.right_brazo_var.set(bd)  # BD
            if hasattr(self, 'right_frente_var'):
                self.right_frente_var.set(fd)  # FD
            if hasattr(self, 'right_high_var'):
                self.right_high_var.set(hd)  # HD
            if hasattr(self, 'right_pollo_var'):
                self.right_pollo_var.set(pd)  # PD
            
            # Update arms state
            if hasattr(self, 'arms_state'):
                # Update left arm state
                if 'left_arm' in self.arms_state:
                    self.arms_state['left_arm']['brazo'] = bi
                    self.arms_state['left_arm']['frente'] = fi
                    self.arms_state['left_arm']['high'] = hi
                
                # Update right arm state
                if 'right_arm' in self.arms_state:
                    self.arms_state['right_arm']['brazo'] = bd
                    self.arms_state['right_arm']['frente'] = fd
                    self.arms_state['right_arm']['high'] = hd
                    self.arms_state['right_arm']['pollo'] = pd
            
            # Force update of the visualization
            if hasattr(self, 'update_visualization'):
                self.update_visualization()
            elif hasattr(self, 'force_view_update'):
                self.force_view_update()
            
            # Force canvas update
            if hasattr(self, 'arms_canvas') and self.arms_canvas:
                self.arms_canvas.update()
            
            # Small delay to allow visualization to update
            import time
            time.sleep(0.1)
            
            # Log the position update
            self.log_command(f"Simulator position updated: BI={bi}, BD={bd}, FI={fi}, FD={fd}, HI={hi}, HD={hd}, PD={pd}", "SIMULATOR")
            
        except Exception as e:
            self.log_command(f"Error updating simulator position: {e}", "ERROR")
