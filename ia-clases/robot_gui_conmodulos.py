#!/usr/bin/env python3
"""
Robot GUI Application - Modular Version
=======================================

A comprehensive GUI application for the ADAI robot system with modular tabs.
This is a clean implementation using the modular tab system.

All UI components are now organized in separate modules under the 'tabs' directory.
"""

import cv2
import numpy as np
import time
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import datetime
import os
import shutil
from collections import deque
from typing import Optional
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

from paths import is_frozen, get_bundle_dir, get_data_dir

# Import modular tabs - All UI components are now modular
from tabs import (MainTab, ESP32Tab, SequenceBuilderTab, SettingsTab, 
                  SimulatorTab, ClassBuilderTab, ClassControllerTab,
                  MobileAppTab, StudentsManagerTab, DemoSequenceTab)

# Import additional tabs
try:
    from tabs.classes_manager_tab import ClassesManagerTab
    CLASSES_MANAGER_AVAILABLE = True
except ImportError:
    CLASSES_MANAGER_AVAILABLE = False
    print("⚠️ Classes Manager Tab no disponible")

# Import class manager
try:
    from class_manager import get_class_manager
    CLASS_MANAGER_AVAILABLE = True
except ImportError:
    CLASS_MANAGER_AVAILABLE = False
    print("⚠️ Class Manager no disponible")

# Robot arm inverse kinematics imports
try:
    from ikpy.chain import Chain
    import ikpy.link
    from ikpy.link import OriginLink, URDFLink
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib
    matplotlib.use('TkAgg')
    IKPY_AVAILABLE = True
except ImportError:
    IKPY_AVAILABLE = False
    print("Warning: ikpy not available. Robot arm inverse kinematics will be disabled.")

# Optional imports with fallbacks
try:
    from mrl_connector import MRLConnector, MRLConfig
except Exception:
    MRLConnector = None
    MRLConfig = None

try:
    from esp32_connector import ESP32Connector, ESP32Config
    from esp32_config import get_esp32_config, update_esp32_config
except Exception:
    ESP32Connector = None
    ESP32Config = None
    get_esp32_config = None
    update_esp32_config = None

# =======================
# IP DETECTION FUNCTIONS
# =======================

def get_local_ip():
    """Get the local IP address of this computer"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except Exception:
            return "127.0.0.1"

def get_all_network_interfaces():
    """Get all available network interfaces and their IPs"""
    interfaces = []
    try:
        for interface_name in socket.if_nameindex():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, interface_name[1].encode())
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                interfaces.append({
                    'name': interface_name[1],
                    'ip': ip
                })
            except Exception:
                continue
    except Exception:
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            interfaces.append({
                'name': 'Default',
                'ip': ip
            })
        except Exception:
            interfaces.append({
                'name': 'Localhost',
                'ip': '127.0.0.1'
            })
    
    return interfaces

# =======================
# MOBILE API SERVER
# =======================

class MobileAPIHandler(BaseHTTPRequestHandler):
    """HTTP Request handler for mobile app communication"""
    
    def __init__(self, request, client_address, server):
        self.robot_gui = server.robot_gui
        super().__init__(request, client_address, server)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = urllib.parse.urlparse(self.path).path
            client_ip = self.client_address[0]
            
            if path != '/api/connection' or self.robot_gui.log_connection_calls:
                self.robot_gui.log_mobile_message(f"GET {path} - {client_ip}")
            
            self.robot_gui.increment_api_stat('total_requests')
            
            device_info = f"{client_ip} - {datetime.datetime.now().strftime('%H:%M:%S')}"
            self.robot_gui.add_connected_device(device_info)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {}
            
            if path == '/api/status':
                response = self.get_robot_status()
            elif path == '/api/position':
                response = self.get_robot_position()
            elif path == '/api/classes':
                response = self.get_available_classes()
            elif path == '/api/connection':
                response = self.get_connection_status()
            elif path == '/api/presets':
                response = self.get_movement_presets()
            elif path == '/api/classes':
                response = self.get_available_classes()
            elif path == '/api/class/progress':
                response = self.get_class_progress()
            else:
                self.send_error(404, "Endpoint not found")
                self.robot_gui.increment_api_stat('failed_requests')
                return
            
            self.wfile.write(json.dumps(response).encode())
            self.robot_gui.increment_api_stat('successful_requests')
            
        except Exception as e:
            print(f"Error in GET request: {e}")
            self.robot_gui.increment_api_stat('failed_requests')
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            path = urllib.parse.urlparse(self.path).path
            client_ip = self.client_address[0]
            self.robot_gui.log_mobile_message(f"POST {path} - {client_ip}")
            self.robot_gui.increment_api_stat('total_requests')
            
            device_info = f"{client_ip} - {datetime.datetime.now().strftime('%H:%M:%S')}"
            self.robot_gui.add_connected_device(device_info)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {}
            
            if path == '/api/robot/move':
                response = self.handle_robot_movement(data)
            elif path == '/api/robot/speak':
                response = self.handle_robot_speech(data)
            elif path == '/api/class/start':
                response = self.handle_start_class(data)
            elif path == '/api/class/stop':
                response = self.handle_stop_class(data)
            elif path == '/api/preset/execute':
                response = self.handle_execute_preset(data)
            elif path == '/api/robot/emergency':
                response = self.handle_emergency_stop()
            elif path == '/api/class/execute':
                response = self.handle_execute_class(data)
            elif path == '/api/teacher/request':
                response = self.handle_teacher_request(data)
            elif path == '/api/teacher/pause':
                response = self.handle_class_pause(data)
            else:
                self.send_error(404, "Endpoint not found")
                self.robot_gui.increment_api_stat('failed_requests')
                return
            
            self.wfile.write(json.dumps(response).encode())
            
            if response.get('success', False):
                self.robot_gui.increment_api_stat('successful_requests')
            else:
                self.robot_gui.increment_api_stat('failed_requests')
            
        except Exception as e:
            print(f"Error in POST request: {e}")
            self.robot_gui.increment_api_stat('failed_requests')
            self.send_error(500, str(e))
    
    def get_robot_status(self):
        """Get current robot status"""
        return {
            "status": "active" if hasattr(self.robot_gui, 'camera_running') and self.robot_gui.camera_running else "idle",
            "battery": 87,
            "temperature": 42.5,
            "connection": "connected" if hasattr(self.robot_gui, 'esp32') and self.robot_gui.esp32 and self.robot_gui.esp32.connected else "disconnected",
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def get_robot_position(self):
        """Get current robot position"""
        position = {
            "head": {"x": 0, "y": 0, "z": 0},
            "leftArm": {"shoulder": 0, "elbow": 0, "wrist": 0},
            "rightArm": {"shoulder": 0, "elbow": 0, "wrist": 0},
            "torso": {"rotation": 0, "tilt": 0},
            "leftHand": {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 0},
            "rightHand": {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 0}
        }
        
        if hasattr(self.robot_gui, 'inmoov_head_angles'):
            position["head"]["x"] = self.robot_gui.inmoov_head_angles.get('yaw', 0)
            position["head"]["y"] = self.robot_gui.inmoov_head_angles.get('pitch', 0)
        
        return position
    
    def get_available_classes(self):
        """Get available robot classes"""
        try:
            if hasattr(self.robot_gui, 'get_available_classes_for_mobile'):
                return self.robot_gui.get_available_classes_for_mobile()
            else:
                # Fallback: return empty classes list
                return {"classes": []}
        except Exception as e:
            return {
                "classes": [],
                "error": str(e)
            }
    
    def get_class_progress(self):
        """Get current class progress"""
        try:
            if hasattr(self.robot_gui, 'class_manager') and self.robot_gui.class_manager:
                progress_info = self.robot_gui.class_manager.get_class_progress()
                return progress_info
            else:
                return {
                    "class_name": None,
                    "phase": "not_started",
                    "progress_percentage": 0,
                    "elapsed_time": "0s",
                    "remaining_time": "0s",
                    "current_phase": "No iniciada",
                    "phase_emoji": "⏳",
                    "is_active": False,
                    "status": "No hay clase activa"
                }
        except Exception as e:
            return {
                "error": str(e),
                "class_name": None,
                "is_active": False
            }
    
    def get_connection_status(self):
        """Get connection status"""
        return {
            "mainServer": "connected" if self.robot_gui.mobile_server_running else "disconnected",
            "robotServer": "connected" if hasattr(self.robot_gui, 'esp32') and self.robot_gui.esp32 and self.robot_gui.esp32.connected else "disconnected",
            "database": "connected",
            "camera": "connected" if hasattr(self.robot_gui, 'camera_running') and self.robot_gui.camera_running else "disconnected",
            "mobileAPI": "connected" if self.robot_gui.mobile_server_running else "disconnected"
        }
    
    def get_movement_presets(self):
        """Get available movement presets"""
        return {
            "presets": [
                {"id": "saludo", "name": "Saludo", "icon": "👋", "description": "Movimiento de saludo"},
                {"id": "aplauso", "name": "Aplauso", "icon": "👏", "description": "Aplaudir"}
            ]
        }
    
    def handle_robot_movement(self, data):
        """Handle robot movement commands"""
        try:
            # Implementation would be here
            return {"success": True, "message": "Movement executed successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_robot_speech(self, data):
        """Handle robot speech commands"""
        try:
            # Implementation would be here
            return {"success": True, "message": "Speech executed successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_start_class(self, data):
        """Handle start class command"""
        try:
            # Implementation would be here
            return {"success": True, "message": "Class started"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_stop_class(self, data):
        """Handle stop class command"""
        try:
            if hasattr(self.robot_gui, 'stop_class_from_mobile'):
                result = self.robot_gui.stop_class_from_mobile()
                return result
            else:
                return {"success": False, "error": "Class stop not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_execute_preset(self, data):
        """Handle execute preset command"""
        try:
            # Implementation would be here
            return {"success": True, "message": "Preset executed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_emergency_stop(self):
        """Handle emergency stop command"""
        try:
            # Implementation would be here
            return {"success": True, "message": "Emergency stop executed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_teacher_request(self, data):
        """Handle teacher request to pause class and listen for request"""
        try:
            request_type = data.get('request_type', 'general')
            
            # Log the teacher request
            print(f"📚 Teacher request received: {request_type}")
            self.robot_gui.log_mobile_message(f"Teacher request: {request_type}")
            
            # Write request to shared file for the class to read
            # The file should be in classes/main/ directory
            try:
                # Try to find the classes/main directory
                current_file = os.path.abspath(__file__)
                classes_main_dir = os.path.join(os.path.dirname(current_file), "clases", "main")
                teacher_request_file = os.path.join(classes_main_dir, "teacher_request.json")
                
                # Write the request to the file
                with open(teacher_request_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'active': True,
                        'request_type': request_type,
                        'timestamp': time.time()
                    }, f)
                
                print(f"✅ Teacher request written to: {teacher_request_file}")
            except Exception as e:
                print(f"⚠️ Could not write teacher request file: {e}")
            
            # Send speech request to robot using TTS
            if hasattr(self.robot_gui, 'tts_engine'):
                speech_text = "Si profesora, cual es su solicitud"
                self.robot_gui.tts_engine.say(speech_text)
                self.robot_gui.tts_engine.runAndWait()
            else:
                print("Robot says: Si profesora, cual es su solicitud")
            
            # If specific request types are needed, handle them
            if request_type == 'examples':
                # Additional handling for examples request could go here
                pass
            elif request_type == 'repeat_question':
                # Additional handling for repeat question could go here
                pass
            
            return {"success": True, "message": f"Teacher request '{request_type}' processed"}
            
        except Exception as e:
            print(f"Error handling teacher request: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_class_pause(self, data):
        """Handle class pause/resume request"""
        try:
            is_paused = data.get('is_paused', True)  # Default to pause if not specified
            
            # Log the pause state change
            action = "pausada" if is_paused else "reanudada"
            print(f"⏸️ Clase {action} por profesora")
            self.robot_gui.log_mobile_message(f"Class {action} by teacher")
            
            # Write pause state to shared file for the class to read
            try:
                # Try to find the classes/main directory
                current_file = os.path.abspath(__file__)
                classes_main_dir = os.path.join(os.path.dirname(current_file), "clases", "main")
                teacher_request_file = os.path.join(classes_main_dir, "teacher_request.json")
                
                # Read current file state if it exists
                file_data = {'active': False, 'request_type': '', 'is_paused': False}
                if os.path.exists(teacher_request_file):
                    with open(teacher_request_file, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                
                # Update pause state
                file_data['is_paused'] = is_paused
                
                # Write the updated state to the file
                with open(teacher_request_file, 'w', encoding='utf-8') as f:
                    json.dump(file_data, f)
                
                print(f"✅ Clase {action}. Estado guardado en: {teacher_request_file}")
            except Exception as e:
                print(f"⚠️ Could not write class pause state file: {e}")
            
            return {"success": True, "message": f"Clase {action}"}
            
        except Exception as e:
            print(f"Error handling class pause: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_execute_class(self, data):
        """Handle class execution command from mobile app"""
        try:
            class_name = data.get('class_name')
            if not class_name:
                return {"success": False, "error": "class_name is required"}
            
            if hasattr(self.robot_gui, 'execute_class_from_mobile'):
                result = self.robot_gui.execute_class_from_mobile(class_name)
                return result
            else:
                return {"success": False, "error": "Class execution not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

class MobileAPIServer(HTTPServer):
    """HTTP Server for mobile app communication"""
    
    def __init__(self, robot_gui, host='localhost', port=8080):
        self.robot_gui = robot_gui
        super().__init__((host, port), MobileAPIHandler)
        print(f"Mobile API Server started on {host}:{port}")

# =======================
# MAIN ROBOT GUI CLASS
# =======================

class RobotGUI:
    def __init__(self):
        """Initialize the Robot GUI with modular architecture"""
        self.root = tk.Tk()
        self.root.title("ADAI Robot System - Control Panel (Modular)")
        
        # Get screen dimensions for responsive design
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate responsive window size (80% of screen size, minimum 1200x600)
        window_width = max(1200, int(screen_width * 0.8))
        window_height = max(600, int(screen_height * 0.8))
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#1e1e1e')
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(1000, 500)
        
        # Store responsive dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.window_width = window_width
        self.window_height = window_height
        
        # Core robot parameters
        self.arm_simulation_enabled = tk.BooleanVar(value=False)
        self.camera_index = tk.IntVar(value=0)
        self.is_running = False
        self.cap = None
        self.camera_running = False
        
        # Robot state
        self.robot_position = (320, 240)
        self.target_position = (320, 240)
        self.is_moving = False
        self.arm_size = 80
        self.movement_speed = 0.1
        self.max_reach = 200
        self.max_distance = 2.0

        # InMoov simulator state
        self.inmoov_sim_enabled = tk.BooleanVar(value=True)
        self.inmoov_track_target = tk.BooleanVar(value=True)
        self.inmoov_canvas = None
        self.inmoov_canvas_size = (500, 350)
        
        # 3D model params
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
        
        # Joint angles
        self.inmoov_head_angles = {'yaw': 0.0, 'pitch': 0.0}
        self.inmoov_left_arm = {'yaw': -0.4, 'pitch': 0.3, 'elbow': 0.8}
        self.inmoov_right_arm = {'yaw': 0.4, 'pitch': 0.3, 'elbow': 0.8}
        
        # Camera view controls
        self.inmoov_cam_yaw_deg = tk.DoubleVar(value=0.0)
        self.inmoov_cam_pitch_deg = tk.DoubleVar(value=0.0)
        self.inmoov_cam_dist = tk.DoubleVar(value=400.0)
        self.inmoov_cam_x = tk.DoubleVar(value=0.0)
        self.inmoov_cam_y = tk.DoubleVar(value=0.0)
        self.inmoov_cam_z = tk.DoubleVar(value=0.0)
        
        # Mouse drag state for simulator camera
        self._inmoov_dragging = False
        self._inmoov_last_xy = None
        self._inmoov_start_yaw = 0.0
        self._inmoov_start_pitch = 0.0
        self._inmoov_panning = False
        self._inmoov_pan_last_xy = None
        self._inmoov_start_cam_x = 0.0
        self._inmoov_start_cam_y = 0.0
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Detection data
        self.face_cascade = None
        self.detected_objects = []
        self.object_history = deque(maxlen=100)
        
        # Target objects configuration
        self.enabled_targets = {'faces'}
        
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
        self.targets = []
        self.target_detection_mode = False
        self.target_validation_frames = 0
        self.target_validation_threshold = 10
        self.target_movement_mode = False
        self.selected_target_index = 0
        
        # Arguco definition system
        self.arguco_definitions = {}
        self.arguco_definition_mode = False
        self.current_arguco_roi = None
        self.arguco_definition_frames = 0
        self.arguco_definition_threshold = 5
        
        # MRL integration
        self.mrl_enabled = tk.BooleanVar(value=False)
        self.mrl_host = tk.StringVar(value="127.0.0.1")
        self.mrl_port = tk.IntVar(value=8888)
        self.mrl_service = tk.StringVar(value="i01")
        self.mrl_status_label: Optional[tk.Label] = None
        self.mrl: Optional[MRLConnector] = None

        # ESP32 integration
        self.esp32_enabled = tk.BooleanVar(value=False)
        self.esp32_host = tk.StringVar(value="192.168.1.100")
        self.esp32_port = tk.IntVar(value=80)
        self.esp32_status_label: Optional[tk.Label] = None
        self.esp32: Optional[ESP32Connector] = None
        
        # Quick ESP32 control
        self.quick_esp32: Optional[ESP32Connector] = None
        self.esp32_simulator_sync = tk.BooleanVar(value=False)
        
        # Sequence Builder system
        self.sequence_builder_enabled = tk.BooleanVar(value=False)
        self.sequence_recording = False
        self.sequence_playing = False
        self.recorded_positions = []
        self.current_sequence = []
        self.sequence_playback_index = 0
        self.sequence_playback_speed = tk.DoubleVar(value=1.0)
        self.sequence_loop = tk.BooleanVar(value=False)
        self.sequence_name = tk.StringVar(value="New Sequence")
        self.saved_sequences = {}
        
        # Load ESP32 configuration if available
        if get_esp32_config is not None:
            try:
                config = get_esp32_config()
                self.esp32_host.set(config.host)
                self.esp32_port.set(config.port)
                self.esp32_enabled.set(config.enable_control)
            except Exception as e:
                print(f"Error loading ESP32 config: {e}")

        # Robot arm inverse kinematics
        self.arm_ik_enabled = tk.BooleanVar(value=False)
        self.arm_chain = None
        self.arm_joints = []
        self.arm_target_position = [0, 0, 0]
        self.arm_current_angles = [0, 0, 0, 0, 0]
        self.arm_joint_names = ["Origen", "BP", "High", "Front", "Bicep"]
        self.arm_3d_plot_enabled = tk.BooleanVar(value=False)
        self.arm_3d_figure = None
        self.arm_3d_ax = None
        
        # Robot arms state tracking
        self.robot_arms_state = {
            'left_arm': {
                'brazo_izq': 10,
                'frente_izq': 80,
                'high_izq': 80
            },
            'right_arm': {
                'brazo_der': 40,
                'frente_der': 90,
                'high_der': 80,
                'pollo_der': 45
            },
            'timestamp': time.time()
        }
        
        # Arms simulator variables
        self.arms_canvas = None
        self.arms_canvas_size = (800, 600)
        self.arms_update_interval = 50
        self.arms_history = deque(maxlen=100)
        self.arms_tracking_enabled = tk.BooleanVar(value=True)
        self.arms_show_trajectory = tk.BooleanVar(value=True)
        self.arms_real_time_update = tk.BooleanVar(value=True)
        
        # 3D visualization variables
        self.arms_fig = None
        self.arms_ax = None
        self.arms_canvas_widget = None
        self.arms_3d_enabled = True
        
        # Initialize robot arm chain if ikpy is available
        if IKPY_AVAILABLE:
            self.setup_robot_arm_chain()

        # Statistics
        self.action_history = deque(maxlen=50)
        self.current_actions = []
        self.future_actions = []
        
        # Mobile API Server
        self.api_server = None
        self.api_server_thread = None
        self.api_port = 8080
        
        # Class Manager
        self.class_manager = None
        if CLASS_MANAGER_AVAILABLE:
            self.class_manager = get_class_manager()
            # Configurar callbacks para el sistema de hilos
            self.class_manager.on_class_started = self.on_class_started
            self.class_manager.on_class_executed = self.on_class_executed
            self.class_manager.on_class_error = self.on_class_error
            self.class_manager.on_class_stopped = self.on_class_stopped
            self.class_manager.on_class_progress = self.on_class_progress
        
        # Mobile App variables
        self.connected_devices = []
        self.mobile_server_running = False
        self.mobile_start_time = None
        self.log_connection_calls = True
        self.api_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'active_connections': 0,
            'uptime': 0
        }
        
        # Connection status
        self.camera_connected = False
        self.robot_connected = False
        self.network_connected = True
        
        # UI components references (will be set by modules)
        self.video_label = None
        self.object_listbox = None
        self.stats_text = None
        self.position_label = None
        self.connection_labels = {}
        
        # Initialize UI and camera
        self.setup_ui()
        self.setup_camera()
        self.start_status_updates()
        
    def setup_robot_arm_chain(self):
        """Setup the robot arm kinematic chain using ikpy"""
        if not IKPY_AVAILABLE:
            return
            
        try:
            pi = math.pi
            
            link1 = ikpy.link.DHLink("link1", 0, 40, pi/2, pi/2)
            link1.bounds = (0, 0.0000001)
            
            link2 = ikpy.link.DHLink("link2", -80, 0, pi/2, pi/2)
            link3 = ikpy.link.DHLink("link3", 280, 0, pi/2, 0)
            link4 = ikpy.link.DHLink("link4", 0, 280, 0, pi/2)
            
            self.arm_chain = Chain(name="arm", links=[
                ikpy.link.OriginLink(),
                link1,
                link2,
                link3,
                link4,
            ])
            
            self.arm_current_angles = [0, 0, 0, 0, 0]
            
            print("Robot arm kinematic chain initialized successfully")
            
        except Exception as e:
            print(f"Error setting up robot arm chain: {e}")
            self.arm_chain = None

    def create_scrollable_frame(self, parent):
        """Create a responsive scrollable frame with both vertical and horizontal scrollbars"""
        container = tk.Frame(parent, bg='#1e1e1e')
        container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(container, bg='#1e1e1e', highlightthickness=0)
        v_scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        def on_mousewheel(event):
            if event.state == 0:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif event.state == 1:
                canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
            widget.bind("<Shift-Button-4>", lambda e: canvas.xview_scroll(-1, "units"))
            widget.bind("<Shift-Button-5>", lambda e: canvas.xview_scroll(1, "units"))
        
        bind_mousewheel(canvas)
        bind_mousewheel(scrollable_frame)
        
        def configure_canvas(event):
            canvas_width = event.width
            if scrollable_frame.winfo_reqwidth() < canvas_width:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas)
        
        return scrollable_frame, canvas, container

    def setup_ui(self):
        """Setup the user interface using modular tabs with responsive design"""
        # Main container with responsive padding
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Responsive title with dynamic font size
        title_font_size = max(16, min(24, self.window_width // 60))
        title_label = tk.Label(main_container, text="ADAI Robot System - Control Panel (Modular)", 
                              font=('Arial', title_font_size, 'bold'), 
                              bg='#1e1e1e', fg='#ffffff')
        title_label.pack(pady=(0, 10))
        
        # Create notebook (tabs) with responsive configuration
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure responsive notebook style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        
        # Responsive tab font size
        tab_font_size = max(8, min(12, self.window_width // 120))
        style.configure('TNotebook.Tab', background='#2d2d2d', foreground='#ffffff', 
                       padding=[max(5, self.window_width // 140), max(3, self.window_height // 200)], 
                       font=('Arial', tab_font_size, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#4CAF50'), ('active', '#3d3d3d')])
        
        # Bind window resize event for responsive updates
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Create all modular tabs
        self.setup_modular_tabs()
    
    def setup_modular_tabs(self):
        """Setup all tabs using the modular system"""
        try:
            print("🚀 Creating modular tabs...")
            
            # Create and setup all modular tabs
            self.main_tab = MainTab(self, self.notebook)
            self.main_tab.create_tab()
            print("✅ Main tab created")
            
            self.esp32_tab = ESP32Tab(self, self.notebook)
            self.esp32_tab.create_tab()
            print("✅ ESP32 tab created")
            
            self.sequence_builder_tab = SequenceBuilderTab(self, self.notebook)
            self.sequence_builder_tab.create_tab()
            print("✅ Sequence Builder tab created")
            
            self.settings_tab = SettingsTab(self, self.notebook)
            self.settings_tab.create_tab()
            print("✅ Settings tab created")
            
            self.simulator_tab = SimulatorTab(self, self.notebook)
            self.simulator_tab.create_tab()
            print("✅ Simulator tab created")
            
            self.class_builder_tab = ClassBuilderTab(self, self.notebook)
            self.class_builder_tab.create_tab()
            print("✅ Class Builder tab created")
            
            self.class_controller_tab = ClassControllerTab(self, self.notebook)
            self.class_controller_tab.create_tab()
            print("✅ Class Controller tab created")
            
            self.mobile_app_tab = MobileAppTab(self, self.notebook)
            self.mobile_app_tab.create_tab()
            print("✅ Mobile App tab created")
            
            self.students_manager_tab = StudentsManagerTab(self, self.notebook)
            self.students_manager_tab.create_tab()
            print("✅ Students Manager tab created")
            
            self.demo_sequence_tab = DemoSequenceTab(self, self.notebook)
            self.demo_sequence_tab.create_tab()
            print("✅ Demo Sequence tab created")
            
            # Create Classes Manager tab if available
            if CLASSES_MANAGER_AVAILABLE:
                self.classes_manager_tab = ClassesManagerTab(self, self.notebook)
                self.classes_manager_tab.create_tab()
                print("✅ Classes Manager tab created")
            
            print("🎉 All modular tabs created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating modular tabs: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error creating tabs: {e}")

    def setup_camera(self):
        """Initialize camera and face detection"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index.get())
            if self.cap.isOpened():
                self.camera_running = True
                self.camera_connected = True
                print("✅ Camera initialized successfully")
            else:
                self.camera_connected = False
                print("❌ Failed to open camera")
                
            # Initialize face cascade
            try:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                print("✅ Face detection initialized")
            except Exception as e:
                print(f"❌ Error initializing face detection: {e}")
                
        except Exception as e:
            print(f"❌ Error setting up camera: {e}")
            self.camera_connected = False

    def start_status_updates(self):
        """Start periodic status updates"""
        def update_status():
            try:
                # Update FPS
                self.fps_counter += 1
                current_time = time.time()
                if current_time - self.fps_start_time >= 1.0:
                    self.current_fps = self.fps_counter
                    self.fps_counter = 0
                    self.fps_start_time = current_time
                
                # Update API stats if mobile server is running
                if hasattr(self, 'mobile_app_tab') and self.mobile_app_tab:
                    if hasattr(self.mobile_app_tab, 'update_mobile_stats'):
                        self.mobile_app_tab.update_mobile_stats()
                
                # Schedule next update
                self.root.after(1000, update_status)
                
            except Exception as e:
                print(f"Error in status update: {e}")
                
        # Start the update loop
        update_status()

    # ===============================
    # MOBILE API INTEGRATION METHODS
    # ===============================
    
    def log_mobile_message(self, message):
        """Log message to mobile tab if available"""
        try:
            if hasattr(self, 'mobile_app_tab') and self.mobile_app_tab:
                self.mobile_app_tab.log_mobile_message(message)
            else:
                print(f"[Mobile] {message}")
        except Exception as e:
            print(f"Error logging mobile message: {e}")
    
    def increment_api_stat(self, stat_name):
        """Increment API statistic"""
        try:
            if hasattr(self, 'mobile_app_tab') and self.mobile_app_tab:
                self.mobile_app_tab.increment_api_stat(stat_name)
        except Exception as e:
            print(f"Error incrementing API stat: {e}")
    
    def add_connected_device(self, device_info):
        """Add connected device to list"""
        try:
            if hasattr(self, 'mobile_app_tab') and self.mobile_app_tab:
                self.mobile_app_tab.add_connected_device(device_info)
        except Exception as e:
            print(f"Error adding connected device: {e}")

    def start_mobile_server(self):
        """Start the mobile API server"""
        try:
            if not self.mobile_server_running:
                local_ip = get_local_ip()
                self.api_server = MobileAPIServer(self, local_ip, self.api_port)
                self.api_server_thread = threading.Thread(target=self.api_server.serve_forever, daemon=True)
                self.api_server_thread.start()
                self.mobile_server_running = True
                self.mobile_start_time = time.time()
                print(f"✅ Mobile API server started on {local_ip}:{self.api_port}")
                # Update mobile status
                self.update_mobile_status()
        except Exception as e:
            print(f"❌ Error starting mobile server: {e}")
    
    def stop_mobile_server(self):
        """Stop the mobile API server"""
        try:
            if self.mobile_server_running and self.api_server:
                self.api_server.shutdown()
                self.mobile_server_running = False
                self.mobile_start_time = None
                print("✅ Mobile API server stopped")
                # Update mobile status
                self.update_mobile_status()
        except Exception as e:
            print(f"❌ Error stopping mobile server: {e}")
    
    def update_mobile_status(self):
        """Update mobile server status indicators"""
        try:
            # Update mobile tab status if it exists
            if hasattr(self, 'mobile_tab') and self.mobile_tab:
                if hasattr(self.mobile_tab, 'update_mobile_status'):
                    self.mobile_tab.update_mobile_status()
        except Exception as e:
            print(f"Error updating mobile status: {e}")

    # ===============================
    # PLACEHOLDER METHODS FOR TABS
    # ===============================
    
    # These methods are called by the modular tabs and can be implemented as needed
    
    def setup_camera_panel(self, parent):
        """Setup responsive camera panel with full functionality"""
        # Responsive font size
        font_size = max(10, min(14, self.window_width // 100))
        
        camera_frame = tk.LabelFrame(parent, text="📹 Camera", 
                                   font=('Arial', font_size, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        camera_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Camera controls frame
        controls_frame = tk.Frame(camera_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Camera controls
        tk.Button(controls_frame, text="🎥 Start Camera", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', max(9, min(12, self.window_width // 120)), 'bold'),
                 command=self.start_camera).pack(side="left", padx=(0, 5))
        
        tk.Button(controls_frame, text="⏹️ Stop Camera", bg='#f44336', fg='#ffffff',
                 font=('Arial', max(9, min(12, self.window_width // 120)), 'bold'),
                 command=self.stop_camera).pack(side="left", padx=(0, 5))
        
        # Arm simulation toggle
        self.arm_sim_var = tk.BooleanVar(value=False)
        tk.Checkbutton(controls_frame, text="🤖 Arm Simulation", variable=self.arm_sim_var,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', max(9, min(12, self.window_width // 120))),
                      command=self.toggle_arm_simulation).pack(side="left", padx=(0, 5))
        
        # Detection controls
        detection_frame = tk.Frame(camera_frame, bg='#2d2d2d')
        detection_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(detection_frame, text="Detection:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', max(9, min(12, self.window_width // 120)), 'bold')).pack(side="left")
        
        # Detection toggles
        self.face_detection_var = tk.BooleanVar(value=True)
        tk.Checkbutton(detection_frame, text="👤 Faces", variable=self.face_detection_var,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', max(8, min(11, self.window_width // 130)))).pack(side="left", padx=(0, 5))
        
        self.circle_detection_var = tk.BooleanVar(value=False)
        tk.Checkbutton(detection_frame, text="⭕ Circles", variable=self.circle_detection_var,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', max(8, min(11, self.window_width // 130)))).pack(side="left", padx=(0, 5))
        
        self.qr_detection_var = tk.BooleanVar(value=False)
        tk.Checkbutton(detection_frame, text="📱 QR Codes", variable=self.qr_detection_var,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', max(8, min(11, self.window_width // 130)))).pack(side="left", padx=(0, 5))
        
        # Camera display
        self.video_label = tk.Label(camera_frame, text="Camera feed will appear here", 
                                   bg='#3d3d3d', fg='#888888', 
                                   font=('Arial', max(12, min(16, self.window_width // 80))))
        self.video_label.pack(expand=True, padx=10, pady=10)
        
        # Status label
        self.camera_status_label = tk.Label(camera_frame, text="Camera: Disconnected", 
                                           bg='#2d2d2d', fg='#ff6b6b',
                                           font=('Arial', max(8, min(11, self.window_width // 130))))
        self.camera_status_label.pack(pady=(0, 5))
    
    def setup_inmoov_sim_panel(self, parent):
        """Setup responsive InMoov simulator panel with full functionality"""
        # Responsive font size
        font_size = max(10, min(14, self.window_width // 100))
        
        sim_frame = tk.LabelFrame(parent, text="🤖 InMoov Simulator", 
                                font=('Arial', font_size, 'bold'),
                                bg='#2d2d2d', fg='#ffffff')
        sim_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Simulator controls
        controls_frame = tk.Frame(sim_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Simulator toggles
        self.sim_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(controls_frame, text="🎮 Enable Simulator", variable=self.sim_enabled_var,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', max(9, min(12, self.window_width // 120))),
                      command=self.toggle_simulator).pack(side="left", padx=(0, 5))
        
        self.track_target_var = tk.BooleanVar(value=True)
        tk.Checkbutton(controls_frame, text="🎯 Track Target", variable=self.track_target_var,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', max(9, min(12, self.window_width // 120)))).pack(side="left", padx=(0, 5))
        
        # Simulator actions
        actions_frame = tk.Frame(sim_frame, bg='#2d2d2d')
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(actions_frame, text="🏠 Center Pose", bg='#2196F3', fg='#ffffff',
                 font=('Arial', max(8, min(11, self.window_width // 130)), 'bold'),
                 command=self.center_simulator_pose).pack(side="left", padx=(0, 5))
        
        tk.Button(actions_frame, text="🔄 Reset View", bg='#FF9800', fg='#ffffff',
                 font=('Arial', max(8, min(11, self.window_width // 130)), 'bold'),
                 command=self.reset_simulator_view).pack(side="left", padx=(0, 5))
        
        # Simulator canvas
        self.sim_canvas = tk.Canvas(sim_frame, bg='#1a1a1a', highlightthickness=0)
        self.sim_canvas.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Simulator status
        self.sim_status_label = tk.Label(sim_frame, text="Simulator: Ready", 
                                        bg='#2d2d2d', fg='#4CAF50',
                                        font=('Arial', max(8, min(11, self.window_width // 130))))
        self.sim_status_label.pack(pady=(0, 5))
    
    def setup_object_panel(self, parent):
        """Setup responsive object detection panel with full functionality"""
        # Responsive font size
        font_size = max(10, min(14, self.window_width // 100))
        
        object_frame = tk.LabelFrame(parent, text="🎯 Object Detection", 
                                   font=('Arial', font_size, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        object_frame.pack(side="right", fill="y", padx=(5, 0))
        
        # Object controls
        controls_frame = tk.Frame(object_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(controls_frame, text="🗑️ Clear List", bg='#f44336', fg='#ffffff',
                 font=('Arial', max(8, min(11, self.window_width // 130)), 'bold'),
                 command=self.clear_object_list).pack(side="left", padx=(0, 5))
        
        tk.Button(controls_frame, text="📊 Export", bg='#2196F3', fg='#ffffff',
                 font=('Arial', max(8, min(11, self.window_width // 130)), 'bold'),
                 command=self.export_objects).pack(side="left", padx=(0, 5))
        
        # Object list with scrollbar
        list_frame = tk.Frame(object_frame, bg='#2d2d2d')
        list_frame.pack(expand=True, fill="both", padx=10, pady=5)
        
        # Responsive object list dimensions
        list_height = max(8, min(15, self.window_height // 50))
        list_width = max(20, min(30, self.window_width // 50))
        
        # Object listbox with scrollbar
        self.object_listbox = tk.Listbox(list_frame, bg='#3d3d3d', fg='#ffffff',
                                       font=('Arial', max(9, min(12, self.window_width // 120))), 
                                       height=list_height, width=list_width,
                                       selectmode=tk.SINGLE)
        self.object_listbox.pack(side="left", fill="both", expand=True)
        
        # Scrollbar for object list
        object_scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.object_listbox.yview)
        object_scrollbar.pack(side="right", fill="y")
        self.object_listbox.configure(yscrollcommand=object_scrollbar.set)
        
        # Object details frame
        details_frame = tk.Frame(object_frame, bg='#2d2d2d')
        details_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(details_frame, text="Selected Object:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', max(9, min(12, self.window_width // 120)), 'bold')).pack(anchor="w")
        
        self.object_details_text = tk.Text(details_frame, bg='#3d3d3d', fg='#ffffff',
                                         font=('Arial', max(8, min(11, self.window_width // 130))),
                                         height=3, width=25, wrap=tk.WORD)
        self.object_details_text.pack(fill="x", pady=(5, 0))
        
        # Bind selection event
        self.object_listbox.bind('<<ListboxSelect>>', self.on_object_select)
    
    def setup_statistics_panel(self, parent):
        """Setup responsive statistics panel - called by MainTab"""
        # Responsive font size
        font_size = max(10, min(14, self.window_width // 100))
        
        stats_frame = tk.LabelFrame(parent, text="📊 Statistics", 
                                  font=('Arial', font_size, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        stats_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Responsive text dimensions
        text_height = max(3, min(6, self.window_height // 100))
        text_width = max(25, min(40, self.window_width // 40))
        
        # Placeholder statistics
        self.stats_text = tk.Text(stats_frame, bg='#3d3d3d', fg='#ffffff',
                                font=('Arial', max(9, min(12, self.window_width // 120))), 
                                height=text_height, width=text_width)
        self.stats_text.pack(expand=True, padx=10, pady=10)
    
    def setup_info_panel(self, parent):
        """Setup responsive info panel - called by MainTab"""
        # Responsive font size
        font_size = max(10, min(14, self.window_width // 100))
        
        info_frame = tk.LabelFrame(parent, text="ℹ️ Information", 
                                 font=('Arial', font_size, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        info_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Responsive placeholder info
        self.position_label = tk.Label(info_frame, text="Robot position: (0, 0)", 
                                     bg='#3d3d3d', fg='#ffffff', 
                                     font=('Arial', max(9, min(12, self.window_width // 120))))
        self.position_label.pack(expand=True, padx=10, pady=10)

    def on_window_resize(self, event):
        """Handle window resize events for responsive design"""
        try:
            # Only handle main window resize events
            if event.widget == self.root:
                # Update stored dimensions
                self.window_width = event.width
                self.window_height = event.height
                
                # Update responsive elements
                self.update_responsive_elements()
                
        except Exception as e:
            print(f"Error in window resize handler: {e}")
    
    def update_responsive_elements(self):
        """Update all responsive elements when window size changes"""
        try:
            # Update title font size
            title_font_size = max(16, min(24, self.window_width // 60))
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label) and "ADAI Robot System" in child.cget("text"):
                            child.configure(font=('Arial', title_font_size, 'bold'))
                            break
            
            # Update tab font sizes
            tab_font_size = max(8, min(12, self.window_width // 120))
            style = ttk.Style()
            style.configure('TNotebook.Tab', 
                          padding=[max(5, self.window_width // 140), max(3, self.window_height // 200)], 
                          font=('Arial', tab_font_size, 'bold'))
            
            # Notify modular tabs about resize
            self.notify_tabs_resize()
            
        except Exception as e:
            print(f"Error updating responsive elements: {e}")
    
    def notify_tabs_resize(self):
        """Notify all modular tabs about window resize"""
        try:
            # List of tab attributes to check
            tab_attributes = [
                'main_tab', 'esp32_tab', 'sequence_builder_tab', 'settings_tab',
                'simulator_tab', 'class_builder_tab', 'class_controller_tab',
                'mobile_app_tab', 'students_manager_tab'
            ]
            
            for attr in tab_attributes:
                if hasattr(self, attr):
                    tab = getattr(self, attr)
                    if hasattr(tab, 'on_resize'):
                        tab.on_resize(self.window_width, self.window_height)
                        
        except Exception as e:
            print(f"Error notifying tabs about resize: {e}")
    
    def on_class_started(self, class_info):
        """Callback cuando una clase inicia su ejecución"""
        try:
            print(f"🚀 Clase iniciada: {class_info.get('title', 'Unknown')}")
            # Notificar a la UI que una clase ha comenzado
            self.update_class_status("Ejecutando", class_info.get('title', 'Unknown'))
            # Notificar a la app móvil si está disponible
            if hasattr(self, 'mobile_app_tab') and self.mobile_app_tab:
                self.mobile_app_tab.log_mobile_message(f"Clase iniciada: {class_info.get('title', 'Unknown')}")
        except Exception as e:
            print(f"Error en callback de inicio de clase: {e}")
    
    def on_class_executed(self, class_info, output):
        """Callback cuando una clase se ejecuta exitosamente"""
        try:
            print(f"✅ Clase ejecutada: {class_info.get('title', 'Unknown')}")
            # Notificar a la UI que la clase ha terminado exitosamente
            self.update_class_status("Completada", class_info.get('title', 'Unknown'))
            # Notificar a la app móvil si está disponible
            if hasattr(self, 'mobile_app_tab') and self.mobile_app_tab:
                self.mobile_app_tab.log_mobile_message(f"Clase ejecutada: {class_info.get('title', 'Unknown')}")
            
            # Reiniciar botones en Classes Manager Tab
            if hasattr(self, 'classes_manager_tab') and self.classes_manager_tab:
                # Usar root.after para actualizar la UI de manera segura
                self.root.after(0, self.reset_class_buttons_after_completion)
        except Exception as e:
            print(f"Error en callback de clase ejecutada: {e}")
    
    def on_class_error(self, error_msg):
        """Callback cuando hay error ejecutando una clase"""
        try:
            print(f"❌ Error ejecutando clase: {error_msg}")
            # Notificar a la UI que ha ocurrido un error
            self.update_class_status("Error", "Error en ejecución")
            # Notificar a la app móvil si está disponible
            if hasattr(self, 'mobile_app_tab') and self.mobile_app_tab:
                self.mobile_app_tab.log_mobile_message(f"Error en clase: {error_msg}")
            
            # Reiniciar botones en Classes Manager Tab
            if hasattr(self, 'classes_manager_tab') and self.classes_manager_tab:
                # Usar root.after para actualizar la UI de manera segura
                self.root.after(0, self.reset_class_buttons_after_completion)
        except Exception as e:
            print(f"Error en callback de error de clase: {e}")
    
    def on_class_stopped(self, class_info, message):
        """Callback cuando una clase se detiene"""
        try:
            print(f"⏹️ Clase detenida: {class_info.get('title', 'Unknown')} - {message}")
            # Notificar a la UI que la clase ha sido detenida
            self.update_class_status("Detenida", class_info.get('title', 'Unknown'))
            # Notificar a la app móvil si está disponible
            if hasattr(self, 'mobile_app_tab') and self.mobile_app_tab:
                self.mobile_app_tab.log_mobile_message(f"Clase detenida: {class_info.get('title', 'Unknown')}")
            
            # Reiniciar botones en Classes Manager Tab
            if hasattr(self, 'classes_manager_tab') and self.classes_manager_tab:
                # Usar root.after para actualizar la UI de manera segura
                self.root.after(0, self.reset_class_buttons_after_completion)
        except Exception as e:
            print(f"Error en callback de detención de clase: {e}")
    
    def on_class_progress(self, progress_info):
        """Callback cuando hay actualización de progreso de una clase"""
        try:
            print(f"📊 Progreso: {progress_info.get('current_phase', 'Unknown')} - {progress_info.get('progress_percentage', 0)}%")
            # Aquí puedes agregar lógica para actualizar barras de progreso en la UI
        except Exception as e:
            print(f"Error en callback de progreso de clase: {e}")
    
    def update_class_status(self, status, class_title):
        """Actualizar el estado de la clase en la UI"""
        try:
            # Buscar y actualizar el widget de estado de clase si existe
            if hasattr(self, 'class_status_label'):
                self.class_status_label.config(
                    text=f"Clase: {status} - {class_title}",
                    fg='#4CAF50' if status == "Ejecutando" else '#FF9800' if status == "Completada" else '#f44336'
                )
        except Exception as e:
            print(f"Error actualizando estado de clase: {e}")
    
    def reset_class_buttons_after_completion(self):
        """Reiniciar botones después de que una clase se completa, detiene o tiene error"""
        try:
            print("🔄 Reiniciando botones de control de clases...")
            
            # Actualizar Classes Manager Tab
            if hasattr(self, 'classes_manager_tab') and self.classes_manager_tab:
                self.classes_manager_tab.is_class_running = False
                self.classes_manager_tab.current_class_name = None
                self.classes_manager_tab.update_control_buttons(False)
                self.classes_manager_tab.clear_progress_display()
                print("✅ Botones de Classes Manager Tab reiniciados")
            
            # Actualizar Class Controller Tab si existe
            if hasattr(self, 'class_controller_tab') and self.class_controller_tab:
                if hasattr(self.class_controller_tab, 'on_class_completed'):
                    self.class_controller_tab.on_class_completed()
                    print("✅ Botones de Class Controller Tab reiniciados")
            
        except Exception as e:
            print(f"Error reiniciando botones: {e}")
    
    def log_esp32_command_from_class(self, command, parameters=None, response=None):
        """Registrar comando ESP32 desde una clase en ejecución"""
        try:
            if hasattr(self, 'esp32_tab') and self.esp32_tab:
                # Registrar el comando en el log del ESP32 tab
                if hasattr(self.esp32_tab, 'log_esp32_command'):
                    self.esp32_tab.log_esp32_command(command, parameters, response)
                elif hasattr(self.esp32_tab, 'log_command'):
                    # Formatear el mensaje para el log
                    if parameters:
                        param_str = f" with params: {parameters}"
                    else:
                        param_str = ""
                    
                    command_msg = f"Class ESP32 Command: {command}{param_str}"
                    self.esp32_tab.log_command(command_msg, "CLASS")
                    
                    if response:
                        response_msg = f"Class ESP32 Response: {response}"
                        self.esp32_tab.log_command(response_msg, "RESPONSE")
                        
        except Exception as e:
            print(f"Error logging ESP32 command from class: {e}")
    
    def execute_class_from_mobile(self, class_name):
        """Ejecutar clase desde la app móvil"""
        try:
            if not self.class_manager:
                return {"success": False, "error": "Class Manager no disponible"}
            
            success = self.class_manager.execute_class(class_name)
            return {
                "success": success,
                "message": f"Clase {class_name} iniciada" if success else f"Error ejecutando {class_name}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop_class_from_mobile(self):
        """Detener clase desde la app móvil"""
        try:
            if not self.class_manager:
                return {"success": False, "error": "Class Manager no disponible"}
            
            success = self.class_manager.stop_class_execution()
            return {
                "success": success,
                "message": "Clase detenida exitosamente" if success else "Error deteniendo la clase"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_available_classes_for_mobile(self):
        """Obtener clases disponibles para la app móvil"""
        try:
            if not self.class_manager:
                return {"classes": []}
            
            classes = self.class_manager.get_available_classes()
            return {"classes": classes}
        except Exception as e:
            return {"classes": [], "error": str(e)}

    def run(self):
        """Start the GUI application"""
        try:
            print("🚀 Starting ADAI Robot GUI (Modular Version)...")
            
            # Start mobile API server automatically
            print("🌐 Starting mobile API server...")
            self.start_mobile_server()
            
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🛑 Application interrupted by user")
            self.cleanup()
        except Exception as e:
            print(f"❌ Error running application: {e}")
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources before closing"""
        try:
            print("🧹 Cleaning up resources...")
            
            # Stop mobile server
            if self.mobile_server_running:
                self.stop_mobile_server()
            
            # Stop camera
            self.stop_camera()
            
            # Release camera
            if self.cap and self.cap.isOpened():
                self.cap.release()
            
            # Close OpenCV windows
            cv2.destroyAllWindows()
            
            # Cleanup class manager threading resources
            if self.class_manager:
                print("🧹 Limpiando recursos de hilos de clases...")
                self.class_manager.force_cleanup()
            
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

    # ===============================
    # CAMERA AND DETECTION METHODS
    # ===============================
    
    def start_camera(self):
        """Start camera feed with detection"""
        try:
            if not self.camera_running:
                self.cap = cv2.VideoCapture(self.camera_index.get())
                if self.cap.isOpened():
                    self.camera_running = True
                    self.camera_connected = True
                    self.camera_status_label.config(text="Camera: Connected", fg='#4CAF50')
                    print("✅ Camera started successfully")
                    self.update_camera_feed()
                else:
                    self.camera_status_label.config(text="Camera: Failed to connect", fg='#f44336')
                    print("❌ Failed to open camera")
            else:
                print("Camera is already running")
        except Exception as e:
            print(f"❌ Error starting camera: {e}")
            self.camera_status_label.config(text=f"Camera: Error - {e}", fg='#f44336')
    
    def stop_camera(self):
        """Stop camera feed"""
        try:
            self.camera_running = False
            if self.cap and self.cap.isOpened():
                self.cap.release()
            self.camera_status_label.config(text="Camera: Disconnected", fg='#ff6b6b')
            self.video_label.config(text="Camera feed stopped")
            print("✅ Camera stopped")
        except Exception as e:
            print(f"❌ Error stopping camera: {e}")
    
    def update_camera_feed(self):
        """Update camera feed with detection"""
        if not self.camera_running or not self.cap or not self.cap.isOpened():
            return
        
        try:
            ret, frame = self.cap.read()
            if ret:
                # Process frame with detection
                processed_frame = self.process_frame(frame)
                
                # Convert to PIL Image for tkinter
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize for display
                display_width = 400
                display_height = 300
                pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update video label
                self.video_label.config(image=photo)
                self.video_label.image = photo  # Keep a reference
                
                # Update simulator if enabled
                if self.sim_enabled_var.get():
                    self.update_simulator()
                
            # Schedule next update
            if self.camera_running:
                self.root.after(30, self.update_camera_feed)  # ~30 FPS
                
        except Exception as e:
            print(f"Error updating camera feed: {e}")
            self.camera_status_label.config(text=f"Camera: Error - {e}", fg='#f44336')
    
    def process_frame(self, frame):
        """Process frame with object detection"""
        try:
            # Detect objects based on enabled detectors
            detected_objects = self.detect_objects(frame)
            
            # Update object list
            self.update_object_list(detected_objects)
            
            # Draw detections on frame
            self.draw_detections(frame, detected_objects)
            
            return frame
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame
    
    def detect_objects(self, frame):
        """Detect objects in frame"""
        objects = []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Face detection
            if self.face_detection_var.get() and self.face_cascade:
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                for (x, y, w, h) in faces:
                    objects.append({
                        'type': 'face',
                        'center': (x + w // 2, y + h // 2),
                        'rect': (x, y, w, h),
                        'confidence': 0.9,
                        'timestamp': time.time()
                    })
            
            # Circle detection
            if self.circle_detection_var.get():
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                         param1=50, param2=30, minRadius=10, maxRadius=100)
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for circle in circles[0, :]:
                        objects.append({
                            'type': 'circle',
                            'center': (circle[0], circle[1]),
                            'rect': (circle[0] - circle[2], circle[1] - circle[2], 
                                   circle[2] * 2, circle[2] * 2),
                            'confidence': 0.8,
                            'timestamp': time.time()
                        })
            
            # QR code detection (simplified)
            if self.qr_detection_var.get():
                # This would use a QR detector library
                pass
                
        except Exception as e:
            print(f"Error in object detection: {e}")
        
        return objects
    
    def draw_detections(self, frame, objects):
        """Draw detection boxes on frame"""
        try:
            for obj in objects:
                x, y, w, h = obj['rect']
                obj_type = obj['type']
                
                # Different colors for different object types
                if obj_type == 'face':
                    color = (0, 255, 0)  # Green
                    label = f"Face ({obj['confidence']:.1f})"
                elif obj_type == 'circle':
                    color = (255, 0, 0)  # Blue
                    label = f"Circle ({obj['confidence']:.1f})"
                else:
                    color = (0, 0, 255)  # Red
                    label = f"{obj_type} ({obj['confidence']:.1f})"
                
                # Draw rectangle
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Draw label
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, color, 2)
                
        except Exception as e:
            print(f"Error drawing detections: {e}")
    
    def update_object_list(self, objects):
        """Update the object list display"""
        try:
            # Clear current list
            self.object_listbox.delete(0, tk.END)
            
            # Add new objects
            for obj in objects:
                obj_type = obj['type']
                center = obj['center']
                confidence = obj['confidence']
                timestamp = obj['timestamp']
                
                # Format timestamp
                time_str = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
                
                # Create list item
                item_text = f"{obj_type.upper()} at ({center[0]}, {center[1]}) - {confidence:.1f} - {time_str}"
                self.object_listbox.insert(tk.END, item_text)
                
        except Exception as e:
            print(f"Error updating object list: {e}")
    
    def on_object_select(self, event):
        """Handle object selection in list"""
        try:
            selection = self.object_listbox.curselection()
            if selection:
                index = selection[0]
                # Get object details and display them
                self.object_details_text.delete(1.0, tk.END)
                self.object_details_text.insert(1.0, f"Selected object at index {index}")
        except Exception as e:
            print(f"Error handling object selection: {e}")
    
    def clear_object_list(self):
        """Clear the object list"""
        try:
            self.object_listbox.delete(0, tk.END)
            self.object_details_text.delete(1.0, tk.END)
        except Exception as e:
            print(f"Error clearing object list: {e}")
    
    def export_objects(self):
        """Export detected objects to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                # Get objects from listbox
                objects = []
                for i in range(self.object_listbox.size()):
                    item = self.object_listbox.get(i)
                    objects.append({"item": item, "index": i})
                
                # Save to file
                with open(filename, 'w') as f:
                    json.dump(objects, f, indent=2)
                
                print(f"✅ Objects exported to {filename}")
        except Exception as e:
            print(f"Error exporting objects: {e}")
    
    # ===============================
    # SIMULATOR METHODS
    # ===============================
    
    def toggle_simulator(self):
        """Toggle simulator on/off"""
        try:
            if self.sim_enabled_var.get():
                self.sim_status_label.config(text="Simulator: Active", fg='#4CAF50')
                print("✅ Simulator enabled")
            else:
                self.sim_status_label.config(text="Simulator: Disabled", fg='#ff6b6b')
                print("⏸️ Simulator disabled")
        except Exception as e:
            print(f"Error toggling simulator: {e}")
    
    def toggle_arm_simulation(self):
        """Toggle arm simulation"""
        try:
            if self.arm_sim_var.get():
                print("✅ Arm simulation enabled")
            else:
                print("⏸️ Arm simulation disabled")
        except Exception as e:
            print(f"Error toggling arm simulation: {e}")
    
    def center_simulator_pose(self):
        """Center the simulator pose"""
        try:
            # Reset simulator angles to center
            self.inmoov_head_angles = {'yaw': 0.0, 'pitch': 0.0}
            self.inmoov_left_arm = {'yaw': -0.4, 'pitch': 0.3, 'elbow': 0.8}
            self.inmoov_right_arm = {'yaw': 0.4, 'pitch': 0.3, 'elbow': 0.8}
            
            # Update simulator display
            self.update_simulator()
            print("✅ Simulator pose centered")
        except Exception as e:
            print(f"Error centering simulator pose: {e}")
    
    def reset_simulator_view(self):
        """Reset simulator camera view"""
        try:
            # Reset camera view controls
            self.inmoov_cam_yaw_deg.set(0.0)
            self.inmoov_cam_pitch_deg.set(0.0)
            self.inmoov_cam_dist.set(400.0)
            self.inmoov_cam_x.set(0.0)
            self.inmoov_cam_y.set(0.0)
            self.inmoov_cam_z.set(0.0)
            
            # Update simulator display
            self.update_simulator()
            print("✅ Simulator view reset")
        except Exception as e:
            print(f"Error resetting simulator view: {e}")
    
    def update_simulator(self):
        """Update simulator display"""
        try:
            if not self.sim_enabled_var.get() or not self.sim_canvas:
                return
            
            # Clear canvas
            self.sim_canvas.delete('all')
            
            # Draw simple 3D representation
            self.draw_simple_3d_robot()
            
        except Exception as e:
            print(f"Error updating simulator: {e}")
    
    def draw_simple_3d_robot(self):
        """Draw a simple 3D robot representation"""
        try:
            canvas = self.sim_canvas
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                return
            
            # Center point
            center_x = width // 2
            center_y = height // 2
            
            # Draw torso (rectangle)
            torso_width = 80
            torso_height = 120
            torso_x = center_x - torso_width // 2
            torso_y = center_y - torso_height // 2
            
            canvas.create_rectangle(torso_x, torso_y, 
                                  torso_x + torso_width, torso_y + torso_height,
                                  fill='#666666', outline='#ffffff', width=2)
            
            # Draw head (circle)
            head_radius = 30
            head_x = center_x
            head_y = torso_y - head_radius - 10
            
            canvas.create_oval(head_x - head_radius, head_y - head_radius,
                             head_x + head_radius, head_y + head_radius,
                             fill='#888888', outline='#ffffff', width=2)
            
            # Draw arms (lines)
            arm_length = 60
            left_arm_x = torso_x - 10
            right_arm_x = torso_x + torso_width + 10
            arm_y = torso_y + 30
            
            # Left arm
            canvas.create_line(left_arm_x, arm_y, 
                             left_arm_x - arm_length, arm_y - 20,
                             fill='#888888', width=3)
            
            # Right arm
            canvas.create_line(right_arm_x, arm_y,
                             right_arm_x + arm_length, arm_y - 20,
                             fill='#888888', width=3)
            
            # Add labels
            canvas.create_text(center_x, torso_y + torso_height + 20,
                             text="InMoov Robot", fill='#ffffff',
                             font=('Arial', 10, 'bold'))
            
        except Exception as e:
            print(f"Error drawing 3D robot: {e}")

def _bootstrap_frozen_data():
    """On first launch after install, copy bundled seed data to the writable data dir."""
    if not is_frozen():
        return

    bundle = get_bundle_dir()
    data = get_data_dir()

    seed_items = [
        ("clases", True),              # directory
        ("esp32_config.json", False),   # file
        ("students_data.json", False),  # file
    ]

    for name, is_dir in seed_items:
        src = os.path.join(bundle, name)
        dst = os.path.join(data, name)
        if not os.path.exists(src):
            continue
        if os.path.exists(dst):
            continue
        try:
            if is_dir:
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"  Seeded {name} -> {dst}")
        except Exception as e:
            print(f"  Warning: could not seed {name}: {e}")

    # Seed .env from env.example if .env doesn't exist yet
    env_src = os.path.join(bundle, "env.example")
    env_dst = os.path.join(data, ".env")
    if os.path.exists(env_src) and not os.path.exists(env_dst):
        try:
            shutil.copy2(env_src, env_dst)
            print(f"  Seeded .env from env.example -> {env_dst}")
        except Exception as e:
            print(f"  Warning: could not seed .env: {e}")


def main():
    """Main function to run the Robot GUI"""
    try:
        print("="*60)
        print("🤖 ADAI Robot System - Modular Version")
        print("="*60)

        # Bootstrap writable data directory on first installed launch
        _bootstrap_frozen_data()

        # Create and run the GUI
        app = RobotGUI()
        app.run()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("👋 ADAI Robot GUI shutting down...")

if __name__ == "__main__":
    main()
