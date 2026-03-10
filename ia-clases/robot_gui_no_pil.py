#!/usr/bin/env python3
"""
Robot GUI Application (No PIL Version)
=====================================

A comprehensive GUI application for the ADAI robot system with:
- Camera feed with arm simulation toggle
- Object detection list
- Statistics panel (past, current, future actions)
- Position information
- Connection status
- Uses only standard Tkinter (no PIL dependency)
"""

import cv2
import numpy as np
import time
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime
from collections import deque
from typing import Optional

try:
    from mrl_connector import MRLConnector, MRLConfig
except Exception:
    MRLConnector = None  # type: ignore
    MRLConfig = None  # type: ignore

class RobotGUINoPIL:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ADAI Robot System - Control Panel")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Robot parameters
        self.arm_simulation_enabled = tk.BooleanVar(value=False)
        self.camera_index = tk.IntVar(value=0)
        self.is_running = False
        self.cap = None
        
        # Robot state
        self.robot_position = (320, 240)
        self.target_position = (320, 240)
        self.is_moving = False
        self.arm_size = 80
        self.movement_speed = 0.1
        self.max_reach = 200
        self.max_distance = 2.0
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Detection data
        self.face_cascade = None
        self.detected_objects = []
        self.object_history = deque(maxlen=100)
        
        # Target objects configuration
        self.enabled_targets = {'faces'}  # Default enabled targets
        
        # Aruco detection
        self.aruco_detector = None
        self.aruco_dicts = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_6X6_100": cv2.aruco.DICT_6X6_100
        }
        
        # Target detection system
        self.targets = []  # List of validated targets
        self.target_detection_mode = False
        self.target_validation_frames = 0
        self.target_validation_threshold = 10  # Frames to validate target
        self.target_movement_mode = False
        self.selected_target_index = 0
        
        # Arguco definition system
        self.arguco_definitions = {}  # Dictionary of defined argucos
        self.arguco_definition_mode = False
        self.current_arguco_roi = None
        self.arguco_definition_frames = 0
        self.arguco_definition_threshold = 5  # Frames to capture arguco definition
        
        # Aruco builder system
        self.aruco_builder_window = None
        
        # MRL integration
        self.mrl_enabled = tk.BooleanVar(value=False)
        self.mrl_host = tk.StringVar(value="127.0.0.1")
        self.mrl_port = tk.IntVar(value=8888)
        self.mrl_service = tk.StringVar(value="i01")
        self.mrl_status_label: Optional[tk.Label] = None
        self.mrl: Optional[MRLConnector] = None
        # Statistics
        self.action_history = deque(maxlen=50)
        self.current_actions = []
        self.future_actions = []
        
        # Connection status
        self.camera_connected = False
        self.robot_connected = False
        self.network_connected = True
        
        # UI components
        self.video_label = None
        self.object_listbox = None
        self.stats_text = None
        self.position_label = None
        self.connection_labels = {}
        
        self.setup_ui()
        self.setup_camera()
        self.start_status_updates()
        
    def setup_ui(self):
        """Setup the user interface with the specified layout"""
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_container, text="ADAI Robot System - Control Panel", 
                              font=('Arial', 20, 'bold'), 
                              bg='#1e1e1e', fg='#ffffff')
        title_label.pack(pady=(0, 10))
        
        # InMoov simulator state (3D torso-up)
        self.inmoov_sim_enabled = tk.BooleanVar(value=True)
        self.inmoov_track_target = tk.BooleanVar(value=True)
        self.inmoov_canvas = None
        self.inmoov_canvas_size = (500, 350)
        self.inmoov_torso = {
            'width': 180.0,
            'height': 200.0,
            'depth': 80.0,
            'center': np.array([0.0, 110.0, 0.0], dtype=float)
        }
        self.inmoov_upper_len = 120.0
        self.inmoov_fore_len = 110.0
        self.inmoov_camera_z = 400.0
        self.inmoov_focal = 320.0
        self.inmoov_head_angles = {'yaw': 0.0, 'pitch': 0.0}
        self.inmoov_left_arm = {'yaw': -0.4, 'pitch': 0.3, 'elbow': 0.8}
        self.inmoov_right_arm = {'yaw': 0.4, 'pitch': 0.3, 'elbow': 0.8}
        # camera view controls
        self.inmoov_cam_yaw_deg = tk.DoubleVar(value=0.0)
        self.inmoov_cam_pitch_deg = tk.DoubleVar(value=0.0)
        self.inmoov_cam_dist = tk.DoubleVar(value=400.0)
        self.inmoov_cam_x = tk.DoubleVar(value=0.0)
        self.inmoov_cam_y = tk.DoubleVar(value=0.0)
        self.inmoov_cam_z = tk.DoubleVar(value=0.0)
        # mouse drag state
        self._inmoov_dragging = False
        self._inmoov_last_xy = None
        self._inmoov_start_yaw = 0.0
        self._inmoov_start_pitch = 0.0
        self._inmoov_panning = False
        self._inmoov_pan_last_xy = None
        self._inmoov_start_cam_x = 0.0
        self._inmoov_start_cam_y = 0.0

        # Top section (Camera + InMoov Sim + Object List)
        top_frame = tk.Frame(main_container, bg='#1e1e1e')
        top_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Left group: camera + InMoov
        left_group = tk.Frame(top_frame, bg='#1e1e1e')
        left_group.pack(side='left', fill='both', expand=True)

        # Left panel (Camera)
        self.setup_camera_panel(left_group)

        # Middle panel (InMoov Simulator)
        self.setup_inmoov_sim_panel(left_group)

        # Right panel (Object Detection)
        self.setup_object_panel(top_frame)
        
        # Bottom section (Statistics + Info)
        bottom_frame = tk.Frame(main_container, bg='#1e1e1e')
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Statistics panel
        self.setup_statistics_panel(bottom_frame)
        
        # Info panel (Position + Connections)
        self.setup_info_panel(bottom_frame)
        
    def setup_camera_panel(self, parent):
        """Setup the camera panel on the left"""
        camera_frame = tk.LabelFrame(parent, text="Camera Feed", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        camera_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Camera controls
        controls_frame = tk.Frame(camera_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Camera index
        tk.Label(controls_frame, text="Camera:", 
                bg='#2d2d2d', fg='#ffffff').pack(side="left")
        camera_entry = tk.Entry(controls_frame, textvariable=self.camera_index, 
                              width=5, bg='#3d3d3d', fg='#ffffff')
        camera_entry.pack(side="left", padx=5)
        
        # Start/Stop button
        self.start_stop_btn = tk.Button(controls_frame, text="Start Camera", 
                                       command=self.toggle_camera,
                                       bg='#4CAF50', fg='white', 
                                       font=('Arial', 10, 'bold'))
        self.start_stop_btn.pack(side="left", padx=10)
        
        # Arm simulation toggle
        self.arm_toggle = tk.Checkbutton(controls_frame, text="Arm Simulation", 
                                        variable=self.arm_simulation_enabled,
                                        bg='#2d2d2d', fg='#ffffff', 
                                        selectcolor='#3d3d3d',
                                        font=('Arial', 10))
        self.arm_toggle.pack(side="right", padx=10)
        
        # Video display
        video_frame = tk.Frame(camera_frame, bg='#2d2d2d')
        video_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.video_label = tk.Label(video_frame, text="Click 'Start Camera' to begin",
                                   bg='#2d2d2d', fg='#ffffff', font=('Arial', 12))
        self.video_label.pack(expand=True)

    def setup_inmoov_sim_panel(self, parent):
        """Setup the InMoov simulator panel next to the camera"""
        sim_frame = tk.LabelFrame(parent, text="InMoov 3D Simulator", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        sim_frame.pack(side="left", fill="both", expand=True, padx=(5, 5))

        # Controls
        controls = tk.Frame(sim_frame, bg='#2d2d2d')
        controls.pack(fill='x', padx=10, pady=5)

        tk.Checkbutton(controls, text="Enable", variable=self.inmoov_sim_enabled,
                       bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d').pack(side='left')
        tk.Checkbutton(controls, text="Track Closest Target", variable=self.inmoov_track_target,
                       bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d').pack(side='left', padx=10)

        tk.Button(controls, text="Center Pose", bg='#2196F3', fg='white',
                  command=self.center_inmoov_pose).pack(side='right')

        # Canvas
        canvas_w, canvas_h = self.inmoov_canvas_size
        self.inmoov_canvas = tk.Canvas(sim_frame, width=canvas_w, height=canvas_h,
                                       bg='#1b1b1b', highlightthickness=0)
        self.inmoov_canvas.pack(fill='both', expand=True, padx=10, pady=10)
        self._bind_inmoov_mouse_controls()

        # View controls
        view_frame = tk.Frame(sim_frame, bg='#2d2d2d')
        view_frame.pack(fill='x', padx=10, pady=(0,10))
        tk.Label(view_frame, text="View: Yaw", bg='#2d2d2d', fg='#ffffff').grid(row=0, column=0, sticky='w')
        tk.Scale(view_frame, from_=-120, to=120, orient='horizontal', resolution=1,
                 variable=self.inmoov_cam_yaw_deg, command=lambda _=None: self.update_inmoov_sim(),
                 bg='#2d2d2d', fg='#ffffff', highlightthickness=0).grid(row=0, column=1, sticky='ew')
        tk.Label(view_frame, text="Pitch", bg='#2d2d2d', fg='#ffffff').grid(row=1, column=0, sticky='w')
        tk.Scale(view_frame, from_=-60, to=60, orient='horizontal', resolution=1,
                 variable=self.inmoov_cam_pitch_deg, command=lambda _=None: self.update_inmoov_sim(),
                 bg='#2d2d2d', fg='#ffffff', highlightthickness=0).grid(row=1, column=1, sticky='ew')
        tk.Label(view_frame, text="Cam Z", bg='#2d2d2d', fg='#ffffff').grid(row=2, column=0, sticky='w')
        tk.Scale(view_frame, from_=-300, to=300, orient='horizontal', resolution=5,
                 variable=self.inmoov_cam_z, command=lambda _=None: self.update_inmoov_sim(),
                 bg='#2d2d2d', fg='#ffffff', highlightthickness=0).grid(row=2, column=1, sticky='ew')
        tk.Label(view_frame, text="Dist", bg='#2d2d2d', fg='#ffffff').grid(row=3, column=0, sticky='w')
        tk.Scale(view_frame, from_=250, to=900, orient='horizontal', resolution=5,
                 variable=self.inmoov_cam_dist, command=lambda _=None: self.update_inmoov_sim(),
                 bg='#2d2d2d', fg='#ffffff', highlightthickness=0).grid(row=3, column=1, sticky='ew')
        tk.Label(view_frame, text="Cam X", bg='#2d2d2d', fg='#ffffff').grid(row=4, column=0, sticky='w')
        tk.Scale(view_frame, from_=-300, to=300, orient='horizontal', resolution=1,
                 variable=self.inmoov_cam_x, command=lambda _=None: self.update_inmoov_sim(),
                 bg='#2d2d2d', fg='#ffffff', highlightthickness=0).grid(row=4, column=1, sticky='ew')
        tk.Label(view_frame, text="Cam Y", bg='#2d2d2d', fg='#ffffff').grid(row=5, column=0, sticky='w')
        tk.Scale(view_frame, from_=-300, to=300, orient='horizontal', resolution=1,
                 variable=self.inmoov_cam_y, command=lambda _=None: self.update_inmoov_sim(),
                 bg='#2d2d2d', fg='#ffffff', highlightthickness=0).grid(row=5, column=1, sticky='ew')
        view_frame.grid_columnconfigure(1, weight=1)
        tk.Button(view_frame, text="Reset View", bg='#616161', fg='white',
                  command=self.reset_inmoov_view).grid(row=0, column=2, rowspan=6, padx=10)

        # Initialize pose
        self.center_inmoov_pose()
        
    def setup_object_panel(self, parent):
        """Setup the object detection panel on the right"""
        object_frame = tk.LabelFrame(parent, text="Detected Objects", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        object_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Create horizontal split for objects list and target checklist
        object_split_frame = tk.Frame(object_frame, bg='#2d2d2d')
        object_split_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Object list
        list_frame = tk.Frame(object_split_frame, bg='#2d2d2d')
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(list_frame, bg='#2d2d2d')
        listbox_frame.pack(fill="both", expand=True)
        
        self.object_listbox = tk.Listbox(listbox_frame, 
                                        bg='#3d3d3d', fg='#ffffff',
                                        font=('Consolas', 10),
                                        selectmode='single')
        self.object_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        self.object_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.object_listbox.yview)
        
        # Right side - Target objects checklist
        target_frame = tk.Frame(object_split_frame, bg='#2d2d2d')
        target_frame.pack(side="right", fill="y", padx=(5, 0))
        
        # Target objects title
        tk.Label(target_frame, text="Target Objects", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Target object checkboxes
        self.target_objects = {
            'faces': tk.BooleanVar(value=True),
            'circles': tk.BooleanVar(value=False),
            'qr_codes': tk.BooleanVar(value=False),
            'cups': tk.BooleanVar(value=False),
            'argucos': tk.BooleanVar(value=False),
            'arucos': tk.BooleanVar(value=False)
        }
        
        # Create checkboxes for each target type
        for obj_type, var in self.target_objects.items():
            checkbox = tk.Checkbutton(target_frame, 
                                    text=obj_type.replace('_', ' ').title(), 
                                    variable=var,
                                    bg='#2d2d2d', fg='#ffffff', 
                                    selectcolor='#3d3d3d',
                                    font=('Arial', 10),
                                    command=self.update_target_objects)
            checkbox.pack(anchor="w", pady=2)
        
        # Target controls
        target_controls_frame = tk.Frame(target_frame, bg='#2d2d2d')
        target_controls_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(target_controls_frame, text="Select All", 
                 command=self.select_all_targets,
                 bg='#4CAF50', fg='white', 
                 font=('Arial', 9)).pack(side="left", padx=(0, 2))
        
        tk.Button(target_controls_frame, text="Clear All", 
                 command=self.clear_all_targets,
                 bg='#f44336', fg='white', 
                 font=('Arial', 9)).pack(side="right", padx=(2, 0))
        
        # Target detection controls
        target_detection_frame = tk.Frame(target_frame, bg='#2d2d2d')
        target_detection_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(target_detection_frame, text="Target Detection:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Target detection button
        self.target_detect_btn = tk.Button(target_detection_frame, text="Detect Targets", 
                                          command=self.toggle_target_detection,
                                          bg='#FF9800', fg='white', 
                                          font=('Arial', 9, 'bold'))
        self.target_detect_btn.pack(fill="x", pady=2)
        
        # Arguco definition controls
        arguco_definition_frame = tk.Frame(target_frame, bg='#2d2d2d')
        arguco_definition_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(arguco_definition_frame, text="Arguco Definition:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Arguco name entry
        name_frame = tk.Frame(arguco_definition_frame, bg='#2d2d2d')
        name_frame.pack(fill="x", pady=2)
        
        tk.Label(name_frame, text="Name:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 9)).pack(side="left")
        
        self.arguco_name_var = tk.StringVar(value="")
        self.arguco_name_entry = tk.Entry(name_frame, textvariable=self.arguco_name_var,
                                        bg='#3d3d3d', fg='#ffffff',
                                        font=('Arial', 9))
        self.arguco_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Define arguco button
        self.define_arguco_btn = tk.Button(arguco_definition_frame, text="Define Arguco", 
                                          command=self.define_arguco,
                                          bg='#9C27B0', fg='white', 
                                          font=('Arial', 9, 'bold'))
        self.define_arguco_btn.pack(fill="x", pady=2)
        
        # Clear arguco definitions button
        tk.Button(arguco_definition_frame, text="Clear Definitions", 
                 command=self.clear_arguco_definitions,
                 bg='#f44336', fg='white', 
                 font=('Arial', 9)).pack(fill="x", pady=2)
        
        # Aruco Builder section
        aruco_builder_frame = tk.Frame(target_frame, bg='#2d2d2d')
        aruco_builder_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(aruco_builder_frame, text="Aruco Builder:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Open Aruco Builder button
        self.open_aruco_builder_btn = tk.Button(aruco_builder_frame, text="Open Aruco Builder", 
                                               command=self.open_aruco_builder,
                                               bg='#9C27B0', fg='white', 
                                               font=('Arial', 9, 'bold'))
        self.open_aruco_builder_btn.pack(fill="x", pady=2)

        # MRL (InMoov2) controls
        mrl_frame = tk.Frame(target_frame, bg='#2d2d2d')
        mrl_frame.pack(fill='x', pady=(10, 0))
        tk.Label(mrl_frame, text="InMoov2 (MyRobotLab)", bg='#2d2d2d', fg='#ffffff', font=('Arial', 10, 'bold')).pack(anchor='w')
        host_row = tk.Frame(mrl_frame, bg='#2d2d2d'); host_row.pack(fill='x', pady=2)
        tk.Label(host_row, text="Host:", bg='#2d2d2d', fg='#ffffff').pack(side='left')
        tk.Entry(host_row, textvariable=self.mrl_host, width=12, bg='#3d3d3d', fg='#ffffff').pack(side='left', padx=5)
        tk.Label(host_row, text="Port:", bg='#2d2d2d', fg='#ffffff').pack(side='left')
        tk.Entry(host_row, textvariable=self.mrl_port, width=6, bg='#3d3d3d', fg='#ffffff').pack(side='left', padx=5)
        tk.Label(host_row, text="Service:", bg='#2d2d2d', fg='#ffffff').pack(side='left')
        tk.Entry(host_row, textvariable=self.mrl_service, width=8, bg='#3d3d3d', fg='#ffffff').pack(side='left', padx=5)
        tk.Checkbutton(mrl_frame, text="Enable Sync", variable=self.mrl_enabled, bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d').pack(anchor='w')
        controls_row = tk.Frame(mrl_frame, bg='#2d2d2d'); controls_row.pack(fill='x', pady=2)
        tk.Button(controls_row, text="Connect", bg='#4CAF50', fg='white', command=self.mrl_connect).pack(side='left')
        tk.Button(controls_row, text="Send Pose", bg='#2196F3', fg='white', command=self.mrl_send_pose).pack(side='left', padx=5)
        self.mrl_status_label = tk.Label(mrl_frame, text="MRL: Disconnected", bg='#2d2d2d', fg='#ff8888', font=('Consolas', 9))
        self.mrl_status_label.pack(anchor='w', pady=(2, 0))
        
        # Target movement controls
        target_movement_frame = tk.Frame(target_frame, bg='#2d2d2d')
        target_movement_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(target_movement_frame, text="Target Movement:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Target selection
        target_selection_frame = tk.Frame(target_movement_frame, bg='#2d2d2d')
        target_selection_frame.pack(fill="x", pady=2)
        
        tk.Label(target_selection_frame, text="Target:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 9)).pack(side="left")
        
        self.target_var = tk.StringVar(value="0")
        target_spinbox = tk.Spinbox(target_selection_frame, from_=0, to=9, 
                                   textvariable=self.target_var, width=5,
                                   bg='#3d3d3d', fg='#ffffff',
                                   command=self.update_selected_target)
        target_spinbox.pack(side="left", padx=5)
        
        # Move to target button
        self.move_to_target_btn = tk.Button(target_movement_frame, text="Move to Target", 
                                           command=self.move_to_selected_target,
                                           bg='#2196F3', fg='white', 
                                           font=('Arial', 9))
        self.move_to_target_btn.pack(fill="x", pady=2)
        
        # Clear targets button
        tk.Button(target_movement_frame, text="Clear All Targets", 
                 command=self.clear_all_targets_list,
                 bg='#f44336', fg='white', 
                 font=('Arial', 9)).pack(fill="x", pady=2)
        
        # Object controls
        controls_frame = tk.Frame(object_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(controls_frame, text="Clear List", 
                 command=self.clear_object_list,
                 bg='#f44336', fg='white', 
                 font=('Arial', 10)).pack(side="left")
        
        tk.Button(controls_frame, text="Export Data", 
                 command=self.export_object_data,
                 bg='#2196F3', fg='white', 
                 font=('Arial', 10)).pack(side="right")
        
    def setup_statistics_panel(self, parent):
        """Setup the statistics panel"""
        stats_frame = tk.LabelFrame(parent, text="Robot Statistics", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        stats_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Statistics text area
        text_frame = tk.Frame(stats_frame, bg='#2d2d2d')
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.stats_text = tk.Text(text_frame, 
                                 bg='#3d3d3d', fg='#ffffff',
                                 font=('Consolas', 9),
                                 wrap="word", height=8)
        self.stats_text.pack(side="left", fill="both", expand=True)
        
        stats_scrollbar = tk.Scrollbar(text_frame, orient="vertical")
        stats_scrollbar.pack(side="right", fill="y")
        
        self.stats_text.config(yscrollcommand=stats_scrollbar.set)
        stats_scrollbar.config(command=self.stats_text.yview)
        
    def setup_info_panel(self, parent):
        """Setup the information panel (position + connections)"""
        info_frame = tk.LabelFrame(parent, text="System Information", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        info_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Position information
        position_frame = tk.Frame(info_frame, bg='#2d2d2d')
        position_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(position_frame, text="Robot Position:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        self.position_label = tk.Label(position_frame, text="X: 320, Y: 240", 
                                     bg='#2d2d2d', fg='#00ff00',
                                     font=('Consolas', 10))
        self.position_label.pack(anchor="w", pady=2)
        
        # Connection status
        connection_frame = tk.Frame(info_frame, bg='#2d2d2d')
        connection_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(connection_frame, text="Connection Status:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        # Camera connection
        self.connection_labels['camera'] = tk.Label(connection_frame, 
                                                  text="Camera: Disconnected", 
                                                  bg='#2d2d2d', fg='#ff4444',
                                                  font=('Consolas', 10))
        self.connection_labels['camera'].pack(anchor="w", pady=1)
        
        # Robot connection
        self.connection_labels['robot'] = tk.Label(connection_frame, 
                                                 text="Robot: Disconnected", 
                                                 bg='#2d2d2d', fg='#ff4444',
                                                 font=('Consolas', 10))
        self.connection_labels['robot'].pack(anchor="w", pady=1)
        
        # Network connection
        self.connection_labels['network'] = tk.Label(connection_frame, 
                                                   text="Network: Connected", 
                                                   bg='#2d2d2d', fg='#44ff44',
                                                   font=('Consolas', 10))
        self.connection_labels['network'].pack(anchor="w", pady=1)
        
    def setup_camera(self):
        """Initialize camera and face detection"""
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.face_cascade.empty():
                messagebox.showerror("Error", "Failed to load face cascade classifier")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize face detection: {e}")
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        if not self.is_running:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index.get())
            if not self.cap.isOpened():
                messagebox.showerror("Error", f"Failed to open camera {self.camera_index.get()}")
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.is_running = True
            self.camera_connected = True
            self.start_stop_btn.configure(text="Stop Camera", bg='#f44336')
            self.connection_labels['camera'].configure(text="Camera: Connected", fg='#44ff44')
            
            # Start video thread
            self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.video_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {e}")
    
    def stop_camera(self):
        """Stop camera capture"""
        self.is_running = False
        self.camera_connected = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_stop_btn.configure(text="Start Camera", bg='#4CAF50')
        self.connection_labels['camera'].configure(text="Camera: Disconnected", fg='#ff4444')
        self.video_label.configure(text="Camera stopped")
    
    def video_loop(self):
        """Main video processing loop"""
        while self.is_running:
            if self.cap is None:
                break
                
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame = self.process_frame(frame)
            
            # Update video display (simplified without PIL)
            self.update_video_display_simple(processed_frame)
            
            # Update object list
            self.update_object_list()

            # Update InMoov simulator
            self.update_inmoov_sim()
            
            # Small delay
            time.sleep(0.03)  # ~30 FPS
    
    def process_frame(self, frame):
        """Process a single frame"""
        # Detect objects
        self.detected_objects = self.detect_objects(frame)
        
        # Validate targets if in detection mode
        self.validate_targets(self.detected_objects)
        
        # Capture arguco definition if in definition mode
        self.capture_arguco_definition(frame)
        
        # Update robot arm if simulation is enabled
        if self.arm_simulation_enabled.get():
            self.update_robot_arm(frame)
        
        # Draw everything
        if self.arm_simulation_enabled.get():
            self.draw_robot_arm(frame)
        self.draw_objects(frame)
        self.draw_targets(frame)
        self.draw_arguco_definition_ui(frame)
        self.draw_performance_info(frame)
        
        return frame

    def update_inmoov_sim(self):
        """Update and draw the InMoov 3D simulator (torso, head, both arms)"""
        try:
            if not self.inmoov_sim_enabled.get() or self.inmoov_canvas is None:
                return

            target3d = None
            if self.inmoov_track_target.get() and self.detected_objects:
                closest = min(self.detected_objects, key=lambda o: self.calculate_distance(o['size'][0]))
                target3d = self._map_camera_point_to_sim_3d(closest['center'])

                # Head tracking
                self._update_head_to_target(target3d)

                # Choose arm
                ls, rs = self._get_shoulder_positions()
                arm_choice = 'right' if target3d[0] >= 0 else 'left'
                if arm_choice == 'right':
                    yaw, pitch, elbow = self._ik_arm_3d(rs, target3d, self.inmoov_upper_len, self.inmoov_fore_len)
                    if yaw is not None:
                        self.inmoov_right_arm['yaw'] = yaw
                        self.inmoov_right_arm['pitch'] = pitch
                        self.inmoov_right_arm['elbow'] = elbow
                else:
                    yaw, pitch, elbow = self._ik_arm_3d(ls, target3d, self.inmoov_upper_len, self.inmoov_fore_len)
                    if yaw is not None:
                        self.inmoov_left_arm['yaw'] = yaw
                        self.inmoov_left_arm['pitch'] = pitch
                        self.inmoov_left_arm['elbow'] = elbow

            self.draw_inmoov_sim(target3d)

            # periodic MRL sync
            if self.mrl_enabled.get():
                now = time.time()
                if not hasattr(self, '_mrl_last_sent') or now - getattr(self, '_mrl_last_sent') > 0.2:
                    self._mrl_last_sent = now
                    self.mrl_send_pose(silent=True)
        except Exception as e:
            print(f"InMoov sim update error: {e}")

    def center_inmoov_pose(self):
        """Center/default pose for the simulator"""
        try:
            self.inmoov_head_angles = {'yaw': 0.0, 'pitch': 0.0}
            self.inmoov_left_arm = {'yaw': -0.4, 'pitch': 0.2, 'elbow': 0.8}
            self.inmoov_right_arm = {'yaw': 0.4, 'pitch': 0.2, 'elbow': 0.8}
            self.draw_inmoov_sim(None)
        except Exception as e:
            print(f"Center pose error: {e}")

    def reset_inmoov_view(self):
        self.inmoov_cam_yaw_deg.set(0.0)
        self.inmoov_cam_pitch_deg.set(0.0)
        self.inmoov_cam_dist.set(400.0)
        self.inmoov_cam_x.set(0.0)
        self.inmoov_cam_y.set(0.0)
        self.inmoov_cam_z.set(0.0)
        self.update_inmoov_sim()

    def _map_camera_point_to_sim_3d(self, point):
        cam_w, cam_h = 640.0, 480.0
        cx, cy = point
        dx = (cx - cam_w/2.0) / (cam_w/2.0)
        dy = ((cam_h/2.0) - cy) / (cam_h/2.0)
        torso = self.inmoov_torso
        center = torso['center']
        shoulder_y = center[1] + torso['height']*0.25
        x = dx * 160.0
        y = shoulder_y + dy * 140.0
        z = 250.0
        return np.array([x, y, z], dtype=float)

    def draw_inmoov_sim(self, target3d):
        """Draw torso, head, and both arms in simple 3D"""
        c = self.inmoov_canvas
        if c is None:
            return
        c.delete('all')

        torso = self.inmoov_torso
        center = torso['center']
        w, h, d = torso['width'], torso['height'], torso['depth']
        hw, hh, hd = w/2.0, h/2.0, d/2.0
        corners = [
            np.array([center[0]-hw, center[1]-hh, center[2]-hd]),
            np.array([center[0]+hw, center[1]-hh, center[2]-hd]),
            np.array([center[0]+hw, center[1]+hh, center[2]-hd]),
            np.array([center[0]-hw, center[1]+hh, center[2]-hd]),
            np.array([center[0]-hw, center[1]-hh, center[2]+hd]),
            np.array([center[0]+hw, center[1]-hh, center[2]+hd]),
            np.array([center[0]+hw, center[1]+hh, center[2]+hd]),
            np.array([center[0]-hw, center[1]+hh, center[2]+hd]),
        ]
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        pts2d = [self._project(p) for p in corners]
        for a,b in edges:
            self._line2d(c, pts2d[a], pts2d[b], '#444444', 2)

        neck = np.array([center[0], center[1]+hh-10.0, center[2]])
        head_center = neck + np.array([0.0, 30.0, 0.0])
        head_p = self._project(head_center)
        c.create_oval(head_p[0]-10, head_p[1]-10, head_p[0]+10, head_p[1]+10, outline='#FFFFFF')

        yaw, pitch = self.inmoov_head_angles['yaw'], self.inmoov_head_angles['pitch']
        nose_dir = self._dir_from_yaw_pitch(yaw, pitch)
        nose_tip = head_center + 30.0 * nose_dir
        self._line3d(c, head_center, nose_tip, '#FF9800', 2)

        ls, rs = self._get_shoulder_positions()
        l_sh, l_el, l_wr = self._arm_fk(ls, self.inmoov_left_arm['yaw'], self.inmoov_left_arm['pitch'], self.inmoov_left_arm['elbow'])
        self._line3d(c, l_sh, l_el, '#4CAF50', 6)
        self._line3d(c, l_el, l_wr, '#8BC34A', 6)
        r_sh, r_el, r_wr = self._arm_fk(rs, self.inmoov_right_arm['yaw'], self.inmoov_right_arm['pitch'], self.inmoov_right_arm['elbow'])
        self._line3d(c, r_sh, r_el, '#4CAF50', 6)
        self._line3d(c, r_el, r_wr, '#8BC34A', 6)

        if target3d is not None:
            tp = self._project(target3d)
            c.create_oval(tp[0]-4, tp[1]-4, tp[0]+4, tp[1]+4, outline='#FF5722')
            self._line3d(c, r_wr if target3d[0]>=0 else l_wr, target3d, '#FF5722', 1, dash=(3,3))

    def _get_shoulder_positions(self):
        torso = self.inmoov_torso
        center = torso['center']
        w, h = torso['width'], torso['height']
        shoulder_y = center[1] + h*0.25
        left = np.array([center[0]-w*0.5+20.0, shoulder_y, center[2]], dtype=float)
        right = np.array([center[0]+w*0.5-20.0, shoulder_y, center[2]], dtype=float)
        return left, right

    def _ik_arm_3d(self, shoulder_pos, target, L1, L2):
        v = target - shoulder_pos
        dx, dy, dz = float(v[0]), float(v[1]), float(v[2])
        yaw = math.atan2(dx, dz)
        cz = math.cos(-yaw)
        sz = math.sin(-yaw)
        xp = cz*dx + sz*dz
        yp = dy
        zp = -sz*dx + cz*dz
        r2 = yp*yp + zp*zp
        r = math.sqrt(max(1e-6, r2))
        r_clamped = max(1.0, min(r, L1 + L2 - 1.0))
        cos_elbow = (r_clamped*r_clamped - L1*L1 - L2*L2) / (2.0*L1*L2)
        cos_elbow = max(-1.0, min(1.0, cos_elbow))
        elbow = math.acos(cos_elbow)
        angle_to_p = math.atan2(zp, -yp)
        beta = math.atan2(L2*math.sin(elbow), L1 + L2*math.cos(elbow))
        pitch = angle_to_p - beta
        return yaw, pitch, elbow

    def _arm_fk(self, shoulder_pos, yaw, pitch, elbow):
        L1, L2 = self.inmoov_upper_len, self.inmoov_fore_len
        uy = -math.cos(pitch)
        uz = math.sin(pitch)
        upper_local = np.array([0.0, uy, uz])
        fore_local = np.array([0.0, -math.cos(pitch+elbow), math.sin(pitch+elbow)])
        cy = math.cos(yaw)
        sy = math.sin(yaw)
        Ry = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
        upper_dir = Ry @ upper_local
        elbow_pos = shoulder_pos + L1 * upper_dir
        fore_dir = Ry @ fore_local
        wrist_pos = elbow_pos + L2 * fore_dir
        return shoulder_pos, elbow_pos, wrist_pos

    def _dir_from_yaw_pitch(self, yaw, pitch):
        cy = math.cos(yaw)
        sy = math.sin(yaw)
        cp = math.cos(pitch)
        sp = math.sin(pitch)
        Ry = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
        forward = np.array([0.0, 0.0, 1.0])
        v = Ry @ forward
        Rx = np.array([[1.0, 0.0, 0.0], [0.0, cp, -sp], [0.0, sp, cp]])
        v = Rx @ v
        return v

    def _update_head_to_target(self, target):
        torso = self.inmoov_torso
        neck = np.array([torso['center'][0], torso['center'][1] + torso['height']/2 - 10.0, torso['center'][2]])
        dv = target - neck
        dx, dy, dz = float(dv[0]), float(dv[1]), float(dv[2])
        yaw = math.atan2(dx, dz)
        horiz = math.sqrt(dx*dx + dz*dz)
        pitch = math.atan2(dy, horiz)
        self.inmoov_head_angles['yaw'] = max(-1.2, min(1.2, yaw))
        self.inmoov_head_angles['pitch'] = max(-0.9, min(0.9, pitch))

    def _project(self, p3):
        # Camera parameters
        yaw = math.radians(self.inmoov_cam_yaw_deg.get())
        pitch = math.radians(self.inmoov_cam_pitch_deg.get())
        cam_dist = float(self.inmoov_cam_dist.get())
        cam_pos = np.array([
            float(self.inmoov_cam_x.get()),
            float(self.inmoov_cam_y.get()),
            -cam_dist + float(self.inmoov_cam_z.get())
        ], dtype=float)

        cy, sy = math.cos(-yaw), math.sin(-yaw)
        cp, sp = math.cos(-pitch), math.sin(-pitch)
        Ry = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
        Rx = np.array([[1.0, 0.0, 0.0], [0.0, cp, -sp], [0.0, sp, cp]])

        pw = np.array([float(p3[0]), float(p3[1]), float(p3[2])], dtype=float)
        pc = Rx @ (Ry @ (pw - cam_pos))

        z = pc[2]
        if z < 1.0:
            z = 1.0
        f = self.inmoov_focal
        u = f * pc[0] / z
        v = f * pc[1] / z
        cw, ch = self.inmoov_canvas_size
        cx, cy = cw/2.0, ch/2.0 + 40.0
        return (int(cx + u), int(cy - v))

    def _line2d(self, canvas, p1, p2, color, width, dash=None):
        if p1 is None or p2 is None:
            return
        canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=color, width=width, dash=dash)

    def _line3d(self, canvas, a3, b3, color, width, dash=None):
        p1 = self._project(a3)
        p2 = self._project(b3)
        self._line2d(canvas, p1, p2, color, width, dash)

    # ========== MRL integration methods ============
    def mrl_connect(self):
        if MRLConnector is None or MRLConfig is None:
            messagebox.showerror("MRL", "mrl_connector not available. Make sure mrl_connector.py is present.")
            return
        cfg = MRLConfig(host=self.mrl_host.get().strip(), port=int(self.mrl_port.get()), service=self.mrl_service.get().strip())
        self.mrl = MRLConnector(cfg)
        ok, msg = self.mrl.test_connection()
        if ok:
            if self.mrl_status_label:
                self.mrl_status_label.configure(text=f"MRL: Connected {cfg.host}:{cfg.port}", fg='#88ff88')
        else:
            if self.mrl_status_label:
                self.mrl_status_label.configure(text=f"MRL: {msg}", fg='#ff8888')

    def mrl_send_pose(self, silent: bool = False):
        if not self.mrl:
            if not silent:
                messagebox.showerror("MRL", "Not connected to MRL")
            return

        head_pitch_rad = self.inmoov_head_angles['pitch']
        head_yaw_rad = self.inmoov_head_angles['yaw']
        neck_deg = max(0.0, min(180.0, 90.0 - head_pitch_rad * 180.0 / math.pi))
        rothead_deg = max(0.0, min(180.0, 90.0 + head_yaw_rad * 180.0 / math.pi))

        r = self.inmoov_right_arm
        r_shoulder = max(0.0, min(180.0, 90.0 + r['pitch'] * 180.0 / math.pi))
        r_rotate = max(0.0, min(180.0, 90.0 + r['yaw'] * 180.0 / math.pi))
        r_bicep = 90.0
        r_elbow = max(0.0, min(180.0, 60.0 + r['elbow'] * 180.0 / math.pi))
        r_omoplate = 90.0

        l = self.inmoov_left_arm
        l_shoulder = max(0.0, min(180.0, 90.0 + l['pitch'] * 180.0 / math.pi))
        l_rotate = max(0.0, min(180.0, 90.0 + l['yaw'] * 180.0 / math.pi))
        l_bicep = 90.0
        l_elbow = max(0.0, min(180.0, 60.0 + l['elbow'] * 180.0 / math.pi))
        l_omoplate = 90.0

        ok1, msg1 = self.mrl.move_head(neck_deg, rothead_deg)
        ok2, msg2 = self.mrl.move_right_arm(r_shoulder, r_rotate, r_bicep, r_elbow, r_omoplate)
        ok3, msg3 = self.mrl.move_left_arm(l_shoulder, l_rotate, l_bicep, l_elbow, l_omoplate)

        if not all([ok1, ok2, ok3]):
            if not silent and self.mrl_status_label:
                self.mrl_status_label.configure(text=f"MRL: send pose fallback. Try in MRL: {msg1} ; {msg2} ; {msg3}", fg='#ffaa66')
        else:
            if not silent and self.mrl_status_label:
                self.mrl_status_label.configure(text="MRL: Pose sent", fg='#88ff88')

    def _bind_inmoov_mouse_controls(self):
        if self.inmoov_canvas is None:
            return
        self.inmoov_canvas.bind('<ButtonPress-1>', self._inmoov_on_mouse_down)
        self.inmoov_canvas.bind('<B1-Motion>', self._inmoov_on_mouse_move)
        self.inmoov_canvas.bind('<ButtonRelease-1>', self._inmoov_on_mouse_up)
        self.inmoov_canvas.bind('<MouseWheel>', self._inmoov_on_mouse_wheel)
        self.inmoov_canvas.bind('<ButtonPress-2>', self._inmoov_on_mid_down)
        self.inmoov_canvas.bind('<B2-Motion>', self._inmoov_on_mid_move)
        self.inmoov_canvas.bind('<ButtonRelease-2>', self._inmoov_on_mid_up)

    def _inmoov_on_mouse_down(self, event):
        self._inmoov_dragging = True
        self._inmoov_last_xy = (event.x, event.y)
        self._inmoov_start_yaw = float(self.inmoov_cam_yaw_deg.get())
        self._inmoov_start_pitch = float(self.inmoov_cam_pitch_deg.get())

    def _inmoov_on_mouse_move(self, event):
        if not self._inmoov_dragging or self._inmoov_last_xy is None:
            return
        dx = event.x - self._inmoov_last_xy[0]
        dy = event.y - self._inmoov_last_xy[1]
        sensitivity = 0.3
        new_yaw = self._inmoov_start_yaw + dx * sensitivity
        new_pitch = self._inmoov_start_pitch - dy * sensitivity
        new_yaw = max(-120.0, min(120.0, new_yaw))
        new_pitch = max(-60.0, min(60.0, new_pitch))
        self.inmoov_cam_yaw_deg.set(new_yaw)
        self.inmoov_cam_pitch_deg.set(new_pitch)
        self.update_inmoov_sim()

    def _inmoov_on_mouse_up(self, event):
        self._inmoov_dragging = False
        self._inmoov_last_xy = None

    def _inmoov_on_mouse_wheel(self, event):
        try:
            delta = int(event.delta)
        except Exception:
            delta = 0
        step = -delta / 120.0 * 20.0
        new_dist = float(self.inmoov_cam_dist.get()) + step
        new_dist = max(250.0, min(900.0, new_dist))
        self.inmoov_cam_dist.set(new_dist)
        self.update_inmoov_sim()

    def _inmoov_on_mid_down(self, event):
        self._inmoov_panning = True
        self._inmoov_pan_last_xy = (event.x, event.y)
        self._inmoov_start_cam_x = float(self.inmoov_cam_x.get())
        self._inmoov_start_cam_y = float(self.inmoov_cam_y.get())

    def _inmoov_on_mid_move(self, event):
        if not self._inmoov_panning or self._inmoov_pan_last_xy is None:
            return
        dx = event.x - self._inmoov_pan_last_xy[0]
        dy = event.y - self._inmoov_pan_last_xy[1]
        factor = 0.8
        new_x = self._inmoov_start_cam_x - dx * factor
        new_y = self._inmoov_start_cam_y + dy * factor
        new_x = max(-500.0, min(500.0, new_x))
        new_y = max(-500.0, min(500.0, new_y))
        self.inmoov_cam_x.set(new_x)
        self.inmoov_cam_y.set(new_y)
        self.update_inmoov_sim()

    def _inmoov_on_mid_up(self, event):
        self._inmoov_panning = False
        self._inmoov_pan_last_xy = None
    
    def detect_objects(self, frame):
        """Detect objects in the frame based on enabled targets"""
        objects = []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces if enabled
            if 'faces' in self.enabled_targets:
                detected_faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                for (x, y, w, h) in detected_faces:
                    face_info = {
                        'type': 'face',
                        'center': (x + w // 2, y + h // 2),
                        'rect': (x, y, w, h),
                        'size': (w, h),
                        'confidence': 0.9,
                        'timestamp': time.time()
                    }
                    objects.append(face_info)
            
            # Detect circles if enabled
            if 'circles' in self.enabled_targets:
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                         param1=50, param2=30, minRadius=10, maxRadius=100)
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for circle in circles[0, :]:
                        circle_info = {
                            'type': 'circle',
                            'center': (circle[0], circle[1]),
                            'rect': (circle[0] - circle[2], circle[1] - circle[2], 
                                   circle[2] * 2, circle[2] * 2),
                            'size': (circle[2] * 2, circle[2] * 2),
                            'confidence': 0.8,
                            'timestamp': time.time()
                        }
                        objects.append(circle_info)
            
            # Detect QR codes if enabled
            if 'qr_codes' in self.enabled_targets:
                qr_objects = self.detect_qr_codes(frame)
                objects.extend(qr_objects)
            
            # Detect cups/glasses if enabled
            if 'cups' in self.enabled_targets:
                cup_objects = self.detect_cups(frame)
                objects.extend(cup_objects)
            
            # Detect argucos if enabled
            if 'argucos' in self.enabled_targets:
                arguco_objects = self.detect_argucos(frame)
                objects.extend(arguco_objects)
                
                # Detect custom argucos (always enabled when definitions exist)
                custom_arguco_objects = self.detect_custom_argucos(frame)
                objects.extend(custom_arguco_objects)
            
            # Detect arucos if enabled
            if 'arucos' in self.enabled_targets:
                aruco_objects = self.detect_arucos(frame)
                objects.extend(aruco_objects)
            
            # Add to history
            if objects:
                self.object_history.extend(objects)
                
        except Exception as e:
            print(f"Object detection error: {e}")
        
        return objects
    
    def update_robot_arm(self, frame):
        """Update robot arm position based on detected objects"""
        if not self.detected_objects:
            return
        
        # Find closest object
        closest_object = None
        min_distance = float('inf')
        
        for obj in self.detected_objects:
            center = obj['center']
            width_pixels = obj['size'][0]
            distance = self.calculate_distance(width_pixels)
            
            if distance < min_distance and distance < self.max_distance:
                min_distance = distance
                closest_object = obj
        
        if closest_object:
            self.update_target(closest_object['center'], min_distance)
    
    def calculate_distance(self, object_width_pixels: float, 
                         known_width_meters: float = 0.1) -> float:
        """Calculate distance to object based on its size"""
        if object_width_pixels <= 0:
            return float('inf')
        distance = (known_width_meters * 1000.0) / object_width_pixels
        return min(distance, self.max_distance)
    
    def detect_cups(self, frame):
        """Detect cups/glasses in the frame"""
        cup_objects = []
        try:
            # Convert to HSV for color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for common cup colors (white, transparent, etc.)
            # White/transparent objects
            lower_white = np.array([0, 0, 200])
            upper_white = np.array([180, 30, 255])
            white_mask = cv2.inRange(hsv, lower_white, upper_white)
            
            # Find contours
            contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Minimum area threshold
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / float(h)
                    
                    # Check if it looks like a cup (reasonable aspect ratio)
                    if 0.5 < aspect_ratio < 2.0:
                        cup_info = {
                            'type': 'cup',
                            'center': (x + w // 2, y + h // 2),
                            'rect': (x, y, w, h),
                            'size': (w, h),
                            'confidence': 0.7,
                            'timestamp': time.time()
                        }
                        cup_objects.append(cup_info)
                        
        except Exception as e:
            print(f"Cup detection error: {e}")
        
        return cup_objects
    
    def detect_argucos(self, frame):
        """Detect argucos (specialized chemistry objects) in the frame"""
        arguco_objects = []
        try:
            # Convert to HSV for color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for argucos (typically blue, green, or red chemistry objects)
            # Blue argucos (common in chemistry)
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # Green argucos
            lower_green = np.array([40, 50, 50])
            upper_green = np.array([80, 255, 255])
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # Red argucos (handle red wrap-around in HSV)
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)
            
            # Combine all color masks
            color_mask = cv2.bitwise_or(blue_mask, green_mask)
            color_mask = cv2.bitwise_or(color_mask, red_mask)
            
            # Apply morphological operations to clean up the mask
            kernel = np.ones((5, 5), np.uint8)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 800:  # Minimum area threshold for argucos
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / float(h)
                    
                    # Check if it looks like an arguco (reasonable aspect ratio)
                    if 0.3 < aspect_ratio < 3.0:
                        # Determine arguco type based on color
                        roi = hsv[y:y+h, x:x+w]
                        if roi.size > 0:
                            # Calculate dominant color
                            blue_pixels = cv2.countNonZero(cv2.inRange(roi, lower_blue, upper_blue))
                            green_pixels = cv2.countNonZero(cv2.inRange(roi, lower_green, upper_green))
                            red_pixels = cv2.countNonZero(cv2.inRange(roi, lower_red1, upper_red1)) + \
                                       cv2.countNonZero(cv2.inRange(roi, lower_red2, upper_red2))
                            
                            total_pixels = roi.shape[0] * roi.shape[1]
                            if total_pixels > 0:
                                blue_ratio = blue_pixels / total_pixels
                                green_ratio = green_pixels / total_pixels
                                red_ratio = red_pixels / total_pixels
                                
                                # Determine arguco type
                                if blue_ratio > 0.3:
                                    arguco_type = "blue_arguco"
                                    confidence = 0.8
                                elif green_ratio > 0.3:
                                    arguco_type = "green_arguco"
                                    confidence = 0.8
                                elif red_ratio > 0.3:
                                    arguco_type = "red_arguco"
                                    confidence = 0.8
                                else:
                                    arguco_type = "unknown_arguco"
                                    confidence = 0.6
                                
                                arguco_info = {
                                    'type': 'arguco',
                                    'subtype': arguco_type,
                                    'center': (x + w // 2, y + h // 2),
                                    'rect': (x, y, w, h),
                                    'size': (w, h),
                                    'confidence': confidence,
                                    'timestamp': time.time(),
                                    'color_ratios': {
                                        'blue': blue_ratio,
                                        'green': green_ratio,
                                        'red': red_ratio
                                    }
                                }
                                arguco_objects.append(arguco_info)
                        
        except Exception as e:
            print(f"Arguco detection error: {e}")
        
        return arguco_objects
    
    def detect_qr_codes(self, frame):
        """Detect QR codes using multiple methods"""
        qr_objects = []
        try:
            # Try pyzbar first (most reliable)
            try:
                from pyzbar import pyzbar
                qr_codes = pyzbar.decode(frame)
                for qr in qr_codes:
                    qr_info = {
                        'type': 'qr_code',
                        'center': (qr.rect.left + qr.rect.width // 2, 
                                 qr.rect.top + qr.rect.height // 2),
                        'rect': (qr.rect.left, qr.rect.top, 
                               qr.rect.width, qr.rect.height),
                        'size': (qr.rect.width, qr.rect.height),
                        'confidence': 0.95,
                        'timestamp': time.time(),
                        'data': qr.data.decode('utf-8')
                    }
                    qr_objects.append(qr_info)
                return qr_objects
            except ImportError:
                print("pyzbar not available, trying OpenCV QR detector...")
            
            # Fallback to OpenCV QR detector
            try:
                qr_detector = cv2.QRCodeDetector()
                retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(frame)
                
                if retval and points is not None:
                    for i, (info, point) in enumerate(zip(decoded_info, points)):
                        if info:  # Only process if QR code was decoded
                            # Calculate bounding rectangle from points
                            x_coords = [p[0] for p in point]
                            y_coords = [p[1] for p in point]
                            x, y = min(x_coords), min(y_coords)
                            w = max(x_coords) - x
                            h = max(y_coords) - y
                            
                            qr_info = {
                                'type': 'qr_code',
                                'center': (x + w // 2, y + h // 2),
                                'rect': (x, y, w, h),
                                'size': (w, h),
                                'confidence': 0.9,
                                'timestamp': time.time(),
                                'data': info
                            }
                            qr_objects.append(qr_info)
            except Exception as e:
                print(f"OpenCV QR detection failed: {e}")
            
            # If both methods fail, try simple contour-based detection
            if not qr_objects:
                qr_objects = self.detect_qr_by_contours(frame)
                
        except Exception as e:
            print(f"QR code detection error: {e}")
        
        return qr_objects
    
    def detect_qr_by_contours(self, frame):
        """Simple QR code detection using contour analysis"""
        qr_objects = []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to find dark regions (QR codes are typically dark)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Minimum area for QR code
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / float(h)
                    
                    # QR codes are typically square or close to square
                    if 0.8 < aspect_ratio < 1.2:
                        # Check if it has the characteristic QR code pattern
                        roi = gray[y:y+h, x:x+w]
                        if roi.size > 0:
                            # Simple pattern check (QR codes have high contrast)
                            std_dev = np.std(roi)
                            if std_dev > 50:  # High contrast
                                qr_info = {
                                    'type': 'qr_code',
                                    'center': (x + w // 2, y + h // 2),
                                    'rect': (x, y, w, h),
                                    'size': (w, h),
                                    'confidence': 0.6,  # Lower confidence for contour method
                                    'timestamp': time.time(),
                                    'data': 'Unknown'  # Can't decode without proper library
                                }
                                qr_objects.append(qr_info)
                                
        except Exception as e:
            print(f"Contour-based QR detection error: {e}")
        
        return qr_objects
    
    def update_target_objects(self):
        """Update enabled targets based on checkboxes"""
        self.enabled_targets = set()
        for obj_type, var in self.target_objects.items():
            if var.get():
                self.enabled_targets.add(obj_type)
        
        # Ensure at least one target is enabled
        if not self.enabled_targets:
            self.target_objects['faces'].set(True)
            self.enabled_targets.add('faces')
    
    def select_all_targets(self):
        """Select all target object types"""
        for var in self.target_objects.values():
            var.set(True)
        self.update_target_objects()
    
    def clear_all_targets(self):
        """Clear all target object types"""
        for var in self.target_objects.values():
            var.set(False)
        # Ensure at least faces are enabled
        self.target_objects['faces'].set(True)
        self.update_target_objects()
    
    def toggle_target_detection(self):
        """Toggle target detection mode"""
        self.target_detection_mode = not self.target_detection_mode
        if self.target_detection_mode:
            self.target_detect_btn.configure(text="Stop Detection", bg='#f44336')
            self.target_validation_frames = 0
            print("Target detection mode activated")
        else:
            self.target_detect_btn.configure(text="Detect Targets", bg='#FF9800')
            print("Target detection mode deactivated")
    
    def validate_targets(self, current_objects):
        """Validate targets by checking if they remain stable for multiple frames"""
        if not self.target_detection_mode:
            return
        
        self.target_validation_frames += 1
        
        # Only validate after threshold frames
        if self.target_validation_frames >= self.target_validation_threshold:
            # Check for QR codes (beakers with QR codes)
            qr_targets = [obj for obj in current_objects if obj['type'] == 'qr_code']
            
            # Check for cups (beakers without QR codes)
            cup_targets = [obj for obj in current_objects if obj['type'] == 'cup']
            
            # Check for argucos (specialized chemistry objects)
            arguco_targets = [obj for obj in current_objects if obj['type'] == 'arguco']
            
            # Check for arucos (Aruco markers)
            aruco_targets = [obj for obj in current_objects if obj['type'] == 'aruco']
            
            # Combine all potential targets
            potential_targets = qr_targets + cup_targets + arguco_targets + aruco_targets
            
            # Validate targets by checking if they're stable
            for target in potential_targets:
                if self.is_target_stable(target):
                    if not self.is_target_already_registered(target):
                        self.register_target(target)
        
        # Reset validation if no objects detected
        if not current_objects:
            self.target_validation_frames = 0
    
    def is_target_stable(self, target):
        """Check if a target is stable (position hasn't changed much)"""
        # For now, consider all detected objects as stable
        # In a real implementation, you'd track position over time
        return True
    
    def is_target_already_registered(self, target):
        """Check if a target is already registered"""
        for registered_target in self.targets:
            # Check if centers are close (within 50 pixels)
            center1 = target['center']
            center2 = registered_target['center']
            distance = math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
            if distance < 50:
                return True
        return False
    
    def register_target(self, target):
        """Register a new target"""
        target_id = len(self.targets) + 1
        registered_target = {
            'id': target_id,
            'type': target['type'],
            'center': target['center'],
            'rect': target['rect'],
            'size': target['size'],
            'confidence': target['confidence'],
            'timestamp': time.time(),
            'data': target.get('data', 'Unknown')
        }
        self.targets.append(registered_target)
        print(f"Target {target_id} registered: {target['type']} at {target['center']}")
    
    def update_selected_target(self):
        """Update the selected target index"""
        try:
            self.selected_target_index = int(self.target_var.get())
        except ValueError:
            self.selected_target_index = 0
    
    def move_to_selected_target(self):
        """Move robot to the selected target"""
        if not self.targets:
            print("No targets available")
            return
        
        if self.selected_target_index >= len(self.targets):
            print(f"Target {self.selected_target_index} not available")
            return
        
        target = self.targets[self.selected_target_index]
        print(f"Moving to Target {target['id']}: {target['type']} at {target['center']}")
        
        # Update robot target position
        self.update_target(target['center'], 0)
        self.target_movement_mode = True
    
    def clear_all_targets_list(self):
        """Clear all registered targets"""
        self.targets.clear()
        self.target_validation_frames = 0
        print("All targets cleared")
    
    def define_arguco(self):
        """Start arguco definition mode"""
        name = self.arguco_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name for the arguco")
            return
        
        if name in self.arguco_definitions:
            messagebox.showerror("Error", f"Arguco '{name}' already exists")
            return
        
        self.arguco_definition_mode = True
        self.arguco_definition_frames = 0
        self.define_arguco_btn.configure(text="Capturing...", bg='#f44336')
        self.arguco_name_entry.configure(state='disabled')
        print(f"Starting arguco definition for '{name}' - Click on the arguco in the camera feed")
    
    def clear_arguco_definitions(self):
        """Clear all arguco definitions"""
        self.arguco_definitions.clear()
        self.arguco_definition_mode = False
        self.current_arguco_roi = None
        self.define_arguco_btn.configure(text="Define Arguco", bg='#9C27B0')
        self.arguco_name_entry.configure(state='normal')
        self.arguco_name_var.set("")
        print("All arguco definitions cleared")
    
    def open_aruco_builder(self):
        """Open the Aruco Builder window"""
        try:
            # Check if window is already open
            if self.aruco_builder_window is not None:
                try:
                    self.aruco_builder_window.deiconify()  # Bring to front
                    self.aruco_builder_window.lift()  # Raise window
                    return
                except:
                    pass  # Window was closed, create new one
            
            # Import and create Aruco Builder
            from aruco_generator import ArucoGenerator
            
            # Create new window
            self.aruco_builder_window = tk.Toplevel(self.root)
            self.aruco_builder_window.title("ADAI Aruco Builder")
            self.aruco_builder_window.geometry("1200x800")
            self.aruco_builder_window.configure(bg='#1e1e1e')
            
            # Create Aruco Generator instance
            aruco_app = ArucoGenerator()
            
            # Handle window closing
            def on_aruco_builder_closing():
                self.aruco_builder_window.destroy()
                self.aruco_builder_window = None
            
            self.aruco_builder_window.protocol("WM_DELETE_WINDOW", on_aruco_builder_closing)
            
            # Start the Aruco Builder
            aruco_app.run()
            
        except ImportError:
            messagebox.showerror("Error", "Aruco Builder not available. Make sure aruco_generator.py is in the same directory.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Aruco Builder: {e}")
            print(f"Error opening Aruco Builder: {e}")
    
    def capture_arguco_definition(self, frame):
        """Capture arguco definition from current frame"""
        if not self.arguco_definition_mode:
            return
        
        self.arguco_definition_frames += 1
        
        # Wait for threshold frames to ensure stable capture
        if self.arguco_definition_frames >= self.arguco_definition_threshold:
            name = self.arguco_name_var.get().strip()
            
            # Get the ROI from the current frame (center area)
            height, width = frame.shape[:2]
            center_x, center_y = width // 2, height // 2
            roi_size = 100  # Size of ROI to capture
            
            x1 = max(0, center_x - roi_size // 2)
            y1 = max(0, center_y - roi_size // 2)
            x2 = min(width, center_x + roi_size // 2)
            y2 = min(height, center_y + roi_size // 2)
            
            roi = frame[y1:y2, x1:x2]
            
            if roi.size > 0:
                # Convert ROI to HSV and calculate color statistics
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                
                # Calculate color ranges
                h_mean, s_mean, v_mean = cv2.mean(hsv_roi)[:3]
                h_std, s_std, v_std = np.std(hsv_roi, axis=(0, 1))
                
                # Define color range based on statistics
                h_tolerance = min(30, h_std * 2)
                s_tolerance = min(50, s_std * 2)
                v_tolerance = min(50, v_std * 2)
                
                lower_hsv = np.array([
                    max(0, h_mean - h_tolerance),
                    max(0, s_mean - s_tolerance),
                    max(0, v_mean - v_tolerance)
                ])
                
                upper_hsv = np.array([
                    min(180, h_mean + h_tolerance),
                    min(255, s_mean + s_tolerance),
                    min(255, v_mean + v_tolerance)
                ])
                
                # Store arguco definition
                self.arguco_definitions[name] = {
                    'lower_hsv': lower_hsv,
                    'upper_hsv': upper_hsv,
                    'roi': roi,
                    'center': (center_x, center_y),
                    'timestamp': time.time()
                }
                
                print(f"Arguco '{name}' defined successfully")
                print(f"Color range: H({lower_hsv[0]:.1f}-{upper_hsv[0]:.1f}), "
                      f"S({lower_hsv[1]:.1f}-{upper_hsv[1]:.1f}), "
                      f"V({lower_hsv[2]:.1f}-{upper_hsv[2]:.1f})")
                
                # Reset definition mode
                self.arguco_definition_mode = False
                self.define_arguco_btn.configure(text="Define Arguco", bg='#9C27B0')
                self.arguco_name_entry.configure(state='normal')
                self.arguco_name_var.set("")
                
                messagebox.showinfo("Success", f"Arguco '{name}' defined successfully!")
            else:
                print("Failed to capture ROI for arguco definition")
    
    def detect_custom_argucos(self, frame):
        """Detect argucos based on custom definitions"""
        custom_arguco_objects = []
        
        if not self.arguco_definitions:
            return custom_arguco_objects
        
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            for name, definition in self.arguco_definitions.items():
                # Create mask using custom color range
                mask = cv2.inRange(hsv, definition['lower_hsv'], definition['upper_hsv'])
                
                # Apply morphological operations
                kernel = np.ones((5, 5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 500:  # Minimum area threshold
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / float(h)
                        
                        # Check if it looks like an arguco
                        if 0.3 < aspect_ratio < 3.0:
                            arguco_info = {
                                'type': 'arguco',
                                'subtype': f'custom_{name}',
                                'name': name,
                                'center': (x + w // 2, y + h // 2),
                                'rect': (x, y, w, h),
                                'size': (w, h),
                                'confidence': 0.9,
                                'timestamp': time.time(),
                                'definition': definition
                            }
                            custom_arguco_objects.append(arguco_info)
                            
        except Exception as e:
            print(f"Custom arguco detection error: {e}")
        
        return custom_arguco_objects
    
    def detect_arucos(self, frame):
        """Detect Aruco markers in the frame"""
        aruco_objects = []
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Try different dictionaries
            for dict_name, dict_id in self.aruco_dicts.items():
                try:
                    # Use the correct API for different OpenCV versions
                    try:
                        # New API (OpenCV 4.7+)
                        aruco_dict = cv2.aruco.getPredefinedDictionary(dict_id)
                        parameters = cv2.aruco.DetectorParameters()
                    except AttributeError:
                        # Old API (OpenCV 4.6 and earlier)
                        aruco_dict = cv2.aruco.Dictionary_get(dict_id)
                        parameters = cv2.aruco.DetectorParameters_create()
                    
                    # Create detector
                    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
                    
                    # Detect markers
                    corners, ids, rejected = detector.detectMarkers(gray)
                    
                    if ids is not None:
                        for i, marker_id in enumerate(ids):
                            corner = corners[i][0]
                            
                            # Calculate center
                            center_x = int(np.mean(corner[:, 0]))
                            center_y = int(np.mean(corner[:, 1]))
                            
                            # Calculate bounding box
                            x_coords = corner[:, 0]
                            y_coords = corner[:, 1]
                            x, y = int(min(x_coords)), int(min(y_coords))
                            w, h = int(max(x_coords) - x), int(max(y_coords) - y)
                            
                            aruco_info = {
                                'type': 'aruco',
                                'id': int(marker_id),
                                'dict_type': dict_name,
                                'center': (center_x, center_y),
                                'rect': (x, y, w, h),
                                'size': (w, h),
                                'corners': corner.tolist(),
                                'confidence': 0.95,
                                'timestamp': time.time()
                            }
                            aruco_objects.append(aruco_info)
                            
                except Exception as e:
                    print(f"Error detecting with {dict_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Aruco detection error: {e}")
        
        return aruco_objects
    
    def update_target(self, target_center, distance):
        """Update robot arm target position"""
        center_x, center_y = 320, 240
        dx = target_center[0] - center_x
        dy = target_center[1] - center_y
        distance_from_center = math.sqrt(dx*dx + dy*dy)
        
        if distance_from_center > self.max_reach:
            scale = self.max_reach / distance_from_center
            target_x = center_x + dx * scale
            target_y = center_y + dy * scale
        else:
            target_x, target_y = target_center
        
        self.target_position = (int(target_x), int(target_y))
        self.is_moving = True
        
        # Update robot position
        self.robot_position = self.target_position
    
    def draw_robot_arm(self, frame):
        """Draw robot arm on frame"""
        arm_color = (0, 255, 0)  # Green
        
        # Draw arm base (circle)
        cv2.circle(frame, self.robot_position, self.arm_size // 2, arm_color, 3)
        
        # Draw arm fingers (lines)
        finger_length = self.arm_size // 3
        finger_angles = [0, 45, -45, 90, -90]
        
        for angle in finger_angles:
            angle_rad = math.radians(angle)
            end_x = int(self.robot_position[0] + finger_length * math.cos(angle_rad))
            end_y = int(self.robot_position[1] + finger_length * math.sin(angle_rad))
            
            cv2.line(frame, self.robot_position, (end_x, end_y), arm_color, 2)
        
        # Draw target if moving
        if self.is_moving:
            cv2.circle(frame, self.target_position, 10, (0, 0, 255), 2)
            cv2.line(frame, self.robot_position, self.target_position, (0, 0, 255), 2)
    
    def draw_objects(self, frame):
        """Draw detected objects on frame"""
        for obj in self.detected_objects:
            center = obj['center']
            x, y, w, h = obj['rect']
            
            # Define colors for different object types
            color_map = {
                'face': (0, 255, 0),      # Green
                'circle': (255, 0, 0),     # Blue
                'qr_code': (0, 0, 255),    # Red
                'cup': (255, 255, 0),      # Cyan
                'arguco': (255, 0, 255),   # Magenta
                'aruco': (0, 255, 255)     # Yellow
            }
            
            color = color_map.get(obj['type'], (255, 255, 255))
            
            # Special color handling for argucos based on subtype
            if obj['type'] == 'arguco' and 'subtype' in obj:
                if 'blue' in obj['subtype']:
                    color = (255, 0, 0)  # Blue in BGR
                elif 'green' in obj['subtype']:
                    color = (0, 255, 0)  # Green in BGR
                elif 'red' in obj['subtype']:
                    color = (0, 0, 255)  # Red in BGR
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Calculate and draw distance
            width_pixels = obj['size'][0]
            distance = self.calculate_distance(width_pixels)
            distance_text = f"{distance:.2f}m"
            cv2.putText(frame, distance_text, 
                       (center[0] + 10, center[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw object label
            if obj['type'] == 'aruco':
                # Draw Aruco ID
                cv2.putText(frame, f"ARUCO ID:{obj['id']}", 
                           (center[0] - 30, center[1] + 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            else:
                label = obj['type'].replace('_', ' ').upper()
                cv2.putText(frame, label, 
                           (center[0] - 20, center[1] + 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw additional info for QR codes
            if obj['type'] == 'qr_code' and 'data' in obj:
                qr_text = obj['data'][:10] + "..." if len(obj['data']) > 10 else obj['data']
                cv2.putText(frame, qr_text, 
                           (center[0] - 20, center[1] + 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    def draw_targets(self, frame):
        """Draw registered targets on frame"""
        for target in self.targets:
            center = target['center']
            x, y, w, h = target['rect']
            
            # Draw target with different color and style
            target_color = (0, 255, 255)  # Cyan for targets
            cv2.rectangle(frame, (x, y), (x + w, y + h), target_color, 3)
            
            # Draw target ID
            target_text = f"Target {target['id']}"
            cv2.putText(frame, target_text, 
                       (center[0] - 30, center[1] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, target_color, 2)
            
            # Draw target type
            type_text = target['type'].replace('_', ' ').title()
            cv2.putText(frame, type_text, 
                       (center[0] - 30, center[1] + 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, target_color, 1)
            
            # Draw QR data if available
            if target['type'] == 'qr_code' and 'data' in target:
                qr_data = target['data'][:15] + "..." if len(target['data']) > 15 else target['data']
                cv2.putText(frame, qr_data, 
                           (center[0] - 30, center[1] + 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, target_color, 1)
            
            # Draw arguco subtype if available
            if target['type'] == 'arguco' and 'subtype' in target:
                arguco_subtype = target['subtype'].replace('_', ' ').title()
                cv2.putText(frame, arguco_subtype, 
                           (center[0] - 30, center[1] + 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, target_color, 1)
            
            # Draw aruco ID if available
            if target['type'] == 'aruco' and 'id' in target:
                aruco_id = f"ID: {target['id']}"
                cv2.putText(frame, aruco_id, 
                           (center[0] - 30, center[1] + 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, target_color, 1)
            
            # Highlight selected target
            if target['id'] == self.selected_target_index + 1:
                cv2.circle(frame, center, 25, (255, 255, 0), 3)  # Yellow circle around selected
    
    def draw_arguco_definition_ui(self, frame):
        """Draw UI elements for arguco definition mode"""
        if not self.arguco_definition_mode:
            return
        
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Draw crosshair at center
        crosshair_size = 50
        cv2.line(frame, (center_x - crosshair_size, center_y), 
                (center_x + crosshair_size, center_y), (0, 255, 255), 2)
        cv2.line(frame, (center_x, center_y - crosshair_size), 
                (center_x, center_y + crosshair_size), (0, 255, 255), 2)
        
        # Draw ROI rectangle
        roi_size = 100
        x1 = max(0, center_x - roi_size // 2)
        y1 = max(0, center_y - roi_size // 2)
        x2 = min(width, center_x + roi_size // 2)
        y2 = min(height, center_y + roi_size // 2)
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        
        # Draw instruction text
        instruction_text = f"Position arguco '{self.arguco_name_var.get()}' in the center"
        cv2.putText(frame, instruction_text, (10, height - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Draw progress
        progress = self.arguco_definition_frames / self.arguco_definition_threshold
        progress_text = f"Capturing... {progress*100:.0f}%"
        cv2.putText(frame, progress_text, (10, height - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    def draw_performance_info(self, frame):
        """Draw performance information on frame"""
        # Update FPS
        self.fps_counter += 1
        if time.time() - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter / (time.time() - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = time.time()
        
        # Draw info
        cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Objects: {len(self.detected_objects)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Robot arm status
        status = "MOVING" if self.is_moving else "IDLE"
        cv2.putText(frame, f"Robot Arm: {status}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def update_video_display_simple(self, frame):
        """Update video display without PIL - simplified version"""
        try:
            # Convert frame to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame to fit display
            height, width = frame_rgb.shape[:2]
            max_width = 500
            max_height = 350
            
            if width > max_width or height > max_height:
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
            
            # Convert to PhotoImage using tkinter's built-in method
            # This is a simplified approach that works without PIL
            frame_pil = tk.PhotoImage(data=cv2.imencode('.ppm', frame_rgb)[1].tobytes())
            
            # Update label
            self.video_label.configure(image=frame_pil, text="")
            self.video_label.image = frame_pil  # Keep a reference
            
        except Exception as e:
            print(f"Error updating video display: {e}")
            # Fallback to text display
            self.video_label.configure(text=f"Camera Active - FPS: {self.current_fps:.1f}")
    
    def update_object_list(self):
        """Update the object detection list"""
        try:
            self.object_listbox.delete(0, tk.END)
            
            for obj in self.detected_objects:
                timestamp = datetime.datetime.fromtimestamp(obj['timestamp']).strftime('%H:%M:%S')
                distance = self.calculate_distance(obj['size'][0])
                obj_type = obj['type'].replace('_', ' ').title()
                
                # Create detailed list item
                list_item = f"[{timestamp}] {obj_type}"
                list_item += f" - Dist: {distance:.2f}m"
                list_item += f" - Conf: {obj['confidence']:.2f}"
                
                # Add QR code data if available
                if obj['type'] == 'qr_code' and 'data' in obj:
                    qr_data = obj['data'][:15] + "..." if len(obj['data']) > 15 else obj['data']
                    list_item += f" - Data: {qr_data}"
                
                # Add arguco subtype if available
                if obj['type'] == 'arguco' and 'subtype' in obj:
                    arguco_subtype = obj['subtype'].replace('_', ' ').title()
                    list_item += f" - {arguco_subtype}"
                
                # Add Aruco ID info
                if obj['type'] == 'aruco' and 'id' in obj:
                    list_item += f" - ID:{obj['id']}"
                
                self.object_listbox.insert(tk.END, list_item)
                
        except Exception as e:
            print(f"Error updating object list: {e}")
    
    def clear_object_list(self):
        """Clear the object detection list"""
        self.object_listbox.delete(0, tk.END)
        self.detected_objects.clear()
        self.object_history.clear()
    
    def export_object_data(self):
        """Export object detection data to JSON"""
        try:
            data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'objects': list(self.object_history),
                'statistics': {
                    'total_objects': len(self.object_history),
                    'unique_objects': len(set(obj['type'] for obj in self.object_history)),
                    'detection_rate': len(self.detected_objects) / max(1, len(self.object_history))
                }
            }
            
            filename = f"robot_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def update_statistics(self):
        """Update the statistics panel"""
        try:
            self.stats_text.delete(1.0, tk.END)
            
            # Past actions
            past_actions = list(self.action_history)[-10:]  # Last 10 actions
            self.stats_text.insert(tk.END, "=== PAST ACTIONS ===\n", "title")
            for action in past_actions:
                self.stats_text.insert(tk.END, f"• {action}\n")
            
            self.stats_text.insert(tk.END, "\n=== CURRENT STATUS ===\n", "title")
            self.stats_text.insert(tk.END, f"• Objects detected: {len(self.detected_objects)}\n")
            self.stats_text.insert(tk.END, f"• Enabled targets: {', '.join(self.enabled_targets)}\n")
            self.stats_text.insert(tk.END, f"• Registered targets: {len(self.targets)}\n")
            self.stats_text.insert(tk.END, f"• Target detection: {'Active' if self.target_detection_mode else 'Inactive'}\n")
            self.stats_text.insert(tk.END, f"• Arguco definitions: {len(self.arguco_definitions)}\n")
            self.stats_text.insert(tk.END, f"• Arguco definition mode: {'Active' if self.arguco_definition_mode else 'Inactive'}\n")
            self.stats_text.insert(tk.END, f"• Robot moving: {'Yes' if self.is_moving else 'No'}\n")
            self.stats_text.insert(tk.END, f"• Arm simulation: {'Enabled' if self.arm_simulation_enabled.get() else 'Disabled'}\n")
            self.stats_text.insert(tk.END, f"• FPS: {self.current_fps:.1f}\n")
            
            self.stats_text.insert(tk.END, "\n=== FUTURE ACTIONS ===\n", "title")
            if self.detected_objects:
                closest = min(self.detected_objects, key=lambda x: self.calculate_distance(x['size'][0]))
                self.stats_text.insert(tk.END, f"• Target: {closest['type']} at {self.calculate_distance(closest['size'][0]):.2f}m\n")
            else:
                self.stats_text.insert(tk.END, "• No targets detected\n")
                
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def update_position_info(self):
        """Update the position information"""
        try:
            position_text = f"X: {self.robot_position[0]}, Y: {self.robot_position[1]}"
            
            # Add target information if available
            if self.targets and self.selected_target_index < len(self.targets):
                target = self.targets[self.selected_target_index]
                position_text += f"\nTarget {target['id']}: {target['type']}"
                if target['type'] == 'qr_code' and 'data' in target:
                    position_text += f" ({target['data'][:10]}...)"
            
            self.position_label.configure(text=position_text)
        except Exception as e:
            print(f"Error updating position: {e}")
    
    def start_status_updates(self):
        """Start periodic status updates"""
        def update_loop():
            while True:
                try:
                    self.update_statistics()
                    self.update_position_info()
                    time.sleep(1)  # Update every second
                except Exception as e:
                    print(f"Error in status update loop: {e}")
                    time.sleep(1)
        
        status_thread = threading.Thread(target=update_loop, daemon=True)
        status_thread.start()
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        self.stop_camera()
        self.root.quit()

def main():
    """Main function"""
    print("Starting ADAI Robot GUI Application (No PIL Version)...")
    
    try:
        app = RobotGUINoPIL()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main() 