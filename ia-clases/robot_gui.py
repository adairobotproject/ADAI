#!/usr/bin/env python3
"""
Robot GUI Application
====================

A comprehensive GUI application for the ADAI robot system with:
- Camera feed with arm simulation toggle
- Object detection list
- Statistics panel (past, current, future actions)
- Position information
- Connection status
- Robot arm inverse kinematics control
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
from collections import deque
from typing import Optional
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Import modular tabs
from tabs import (MainTab, ESP32Tab, SequenceBuilderTab, SettingsTab,
                  SimulatorTab, ClassBuilderTab, ClassControllerTab,
                  MobileAppTab, StudentsManagerTab, ClassesManagerTab)

# Import class manager
try:
    from class_manager import get_class_manager
    CLASS_MANAGER_AVAILABLE = True
except ImportError:
    CLASS_MANAGER_AVAILABLE = False
    print("⚠️ Class manager no disponible")

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

try:
    from mrl_connector import MRLConnector, MRLConfig
except Exception:
    MRLConnector = None  # type: ignore
    MRLConfig = None  # type: ignore

try:
    from esp32_connector import ESP32Connector, ESP32Config
    from esp32_config import get_esp32_config, update_esp32_config
except Exception:
    ESP32Connector = None  # type: ignore
    ESP32Config = None  # type: ignore
    get_esp32_config = None  # type: ignore
    update_esp32_config = None  # type: ignore

# =======================
# IP DETECTION FUNCTIONS
# =======================

def get_local_ip():
    """Get the local IP address of this computer"""
    try:
        # Try to connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            # Fallback: get hostname and resolve it
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except Exception:
            return "127.0.0.1"

def get_all_network_interfaces():
    """Get all available network interfaces and their IPs"""
    interfaces = []
    try:
        # Get all network interfaces
        for interface_name in socket.if_nameindex():
            try:
                # Get IP for this interface
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
        # Fallback to basic method
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
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            
            # Log request and update stats
            client_ip = self.client_address[0]
            
            # Log the request only if it's not /api/connection or if connection logging is enabled
            if path != '/api/connection' or self.robot_gui.log_connection_calls:
                self.robot_gui.log_mobile_message(f"GET {path} - {client_ip}")
            
            self.robot_gui.increment_api_stat('total_requests')
            
            # Add device to connected list if new
            device_info = f"{client_ip} - {datetime.datetime.now().strftime('%H:%M:%S')}"
            self.robot_gui.add_connected_device(device_info)
            
            # Add CORS headers
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
            else:
                self.send_error(404, "Endpoint not found")
                self.robot_gui.increment_api_stat('failed_requests')
                return
            
            self.wfile.write(json.dumps(response).encode())
            self.robot_gui.increment_api_stat('successful_requests')
            
        except Exception as e:
            print(f"Error in GET request: {e}")
            self.robot_gui.log_mobile_message(f"ERROR GET {path}: {e}")
            self.robot_gui.increment_api_stat('failed_requests')
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            path = urllib.parse.urlparse(self.path).path
            
            # Log request and update stats
            client_ip = self.client_address[0]
            self.robot_gui.log_mobile_message(f"POST {path} - {client_ip}")
            self.robot_gui.increment_api_stat('total_requests')
            
            # Add device to connected list if new
            device_info = f"{client_ip} - {datetime.datetime.now().strftime('%H:%M:%S')}"
            self.robot_gui.add_connected_device(device_info)
            
            # Add CORS headers
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
            elif path == '/api/teacher/request':
                response = self.handle_teacher_request(data)
            elif path == '/api/teacher/pause':
                response = self.handle_class_pause(data)
            else:
                self.send_error(404, "Endpoint not found")
                self.robot_gui.increment_api_stat('failed_requests')
                return
            
            self.wfile.write(json.dumps(response).encode())
            
            # Update stats based on response
            if response.get('success', False):
                self.robot_gui.increment_api_stat('successful_requests')
            else:
                self.robot_gui.increment_api_stat('failed_requests')
            
        except Exception as e:
            print(f"Error in POST request: {e}")
            self.robot_gui.log_mobile_message(f"ERROR POST {path}: {e}")
            self.robot_gui.increment_api_stat('failed_requests')
            self.send_error(500, str(e))
    
    def get_robot_status(self):
        """Get current robot status"""
        return {
            "status": "active" if hasattr(self.robot_gui, 'camera_running') and self.robot_gui.camera_running else "idle",
            "battery": 87,  # Simulated
            "temperature": 42.5,  # Simulated
            "connection": "connected" if hasattr(self.robot_gui, 'esp32') and self.robot_gui.esp32 and self.robot_gui.esp32.connected else "disconnected",
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def get_robot_position(self):
        """Get current robot position"""
        # Get position from ESP32 or simulator
        position = {
            "head": {"x": 0, "y": 0, "z": 0},
            "leftArm": {"shoulder": 0, "elbow": 0, "wrist": 0},
            "rightArm": {"shoulder": 0, "elbow": 0, "wrist": 0},
            "torso": {"rotation": 0, "tilt": 0},
            "leftHand": {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 0},
            "rightHand": {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 0}
        }
        
        # Update with actual positions if available
        if hasattr(self.robot_gui, 'inmoov_head_angles'):
            position["head"]["x"] = self.robot_gui.inmoov_head_angles.get('yaw', 0)
            position["head"]["y"] = self.robot_gui.inmoov_head_angles.get('pitch', 0)
        
        if hasattr(self.robot_gui, 'inmoov_left_arm'):
            position["leftArm"]["shoulder"] = self.robot_gui.inmoov_left_arm.get('yaw', 0)
            position["leftArm"]["elbow"] = self.robot_gui.inmoov_left_arm.get('elbow', 0)
        
        if hasattr(self.robot_gui, 'inmoov_right_arm'):
            position["rightArm"]["shoulder"] = self.robot_gui.inmoov_right_arm.get('yaw', 0)
            position["rightArm"]["elbow"] = self.robot_gui.inmoov_right_arm.get('elbow', 0)
        
        return position
    
    def get_available_classes(self):
        """Get available robot classes"""
        return {
            "classes": [
                {
                    "id": 1,
                    "title": "Introducción a la Robótica",
                    "duration": "45 min",
                    "level": "Básico",
                    "subject": "Tecnología",
                    "description": "Conceptos fundamentales de robótica y automatización",
                    "schedule": "Lunes 9:00 AM",
                    "status": "scheduled",
                    "robotActions": [
                        "Demostración de movimientos básicos",
                        "Explicación de sensores",
                        "Interacción con estudiantes"
                    ],
                    "movements": [
                        {"action": "speak", "text": "Buenos días estudiantes. Hoy aprenderemos sobre robótica."},
                        {"action": "move", "part": "head", "x": 15, "y": 0, "z": 0, "duration": 2},
                        {"action": "move", "part": "rightArm", "shoulder": 45, "elbow": 90, "duration": 3},
                        {"action": "speak", "text": "Este es un ejemplo de movimiento programado."},
                        {"action": "preset", "name": "saludo"}
                    ]
                },
                {
                    "id": 2,
                    "title": "Programación de Movimientos",
                    "duration": "60 min",
                    "level": "Intermedio",
                    "subject": "Programación",
                    "description": "Aprende a programar movimientos complejos del robot",
                    "schedule": "Martes 10:30 AM",
                    "status": "scheduled",
                    "robotActions": [
                        "Ejecución de secuencias programadas",
                        "Demostración de algoritmos",
                        "Práctica con estudiantes"
                    ],
                    "movements": [
                        {"action": "speak", "text": "Vamos a explorar la programación de movimientos."},
                        {"action": "move", "part": "leftArm", "shoulder": -30, "elbow": 60, "duration": 2},
                        {"action": "move", "part": "rightArm", "shoulder": 30, "elbow": 60, "duration": 2},
                        {"action": "speak", "text": "Los movimientos pueden ser sincronizados y programados."},
                        {"action": "preset", "name": "aplauso"}
                    ]
                },
                {
                    "id": 3,
                    "title": "Inteligencia Artificial Básica",
                    "duration": "90 min",
                    "level": "Avanzado",
                    "subject": "IA",
                    "description": "Introducción a conceptos de IA y machine learning",
                    "schedule": "Miércoles 2:00 PM",
                    "status": "scheduled",
                    "robotActions": [
                        "Demostración de reconocimiento de voz",
                        "Interacción conversacional",
                        "Ejemplos de aprendizaje"
                    ],
                    "movements": [
                        {"action": "speak", "text": "La inteligencia artificial me permite interactuar con ustedes."},
                        {"action": "move", "part": "head", "x": -20, "y": 10, "z": 0, "duration": 1},
                        {"action": "move", "part": "head", "x": 20, "y": 10, "z": 0, "duration": 1},
                        {"action": "speak", "text": "Puedo reconocer voces y responder preguntas."},
                        {"action": "preset", "name": "pensativo"}
                    ]
                }
            ]
        }
    
    def get_connection_status(self):
        """Get connection status"""
        return {
            "mainServer": "connected",
            "robotServer": "connected" if hasattr(self.robot_gui, 'esp32') and self.robot_gui.esp32 and self.robot_gui.esp32.connected else "disconnected",
            "database": "connected",
            "camera": "connected" if hasattr(self.robot_gui, 'camera_running') and self.robot_gui.camera_running else "disconnected"
        }
    
    def get_movement_presets(self):
        """Get available movement presets"""
        return {
            "presets": [
                {"id": "saludo", "name": "Saludo", "icon": "👋", "description": "Movimiento de saludo"},
                {"id": "aplauso", "name": "Aplauso", "icon": "👏", "description": "Aplaudir"},
                {"id": "punto", "name": "Señalar", "icon": "👆", "description": "Señalar con el dedo"},
                {"id": "ok", "name": "OK", "icon": "👍", "description": "Gesto de aprobación"},
                {"id": "paz", "name": "Paz", "icon": "✌️", "description": "Signo de paz"},
                {"id": "pensativo", "name": "Pensativo", "icon": "🤔", "description": "Postura pensativa"}
            ]
        }
    
    def handle_robot_movement(self, data):
        """Handle robot movement commands"""
        try:
            part = data.get('part')
            if part == 'head':
                x = data.get('x', 0)
                y = data.get('y', 0) 
                z = data.get('z', 0)
                # Update simulator
                if hasattr(self.robot_gui, 'inmoov_head_angles'):
                    self.robot_gui.inmoov_head_angles['yaw'] = float(x) * math.pi / 180
                    self.robot_gui.inmoov_head_angles['pitch'] = float(y) * math.pi / 180
                    self.robot_gui.draw_inmoov_sim(None)
                
                # Send to ESP32 if connected
                if hasattr(self.robot_gui, 'esp32') and self.robot_gui.esp32 and self.robot_gui.esp32.connected:
                    self.robot_gui.esp32.send_command(f"HEAD:{x},{y},{z}")
                
            elif part in ['leftArm', 'rightArm']:
                shoulder = data.get('shoulder', 0)
                elbow = data.get('elbow', 0)
                wrist = data.get('wrist', 0)
                
                # Update simulator
                arm_key = 'inmoov_left_arm' if part == 'leftArm' else 'inmoov_right_arm'
                if hasattr(self.robot_gui, arm_key):
                    arm = getattr(self.robot_gui, arm_key)
                    arm['yaw'] = float(shoulder) * math.pi / 180
                    arm['elbow'] = float(elbow) * math.pi / 180
                    self.robot_gui.draw_inmoov_sim(None)
                
                # Send to ESP32 if connected
                if hasattr(self.robot_gui, 'esp32') and self.robot_gui.esp32 and self.robot_gui.esp32.connected:
                    prefix = "LEFT_ARM" if part == 'leftArm' else "RIGHT_ARM"
                    self.robot_gui.esp32.send_command(f"{prefix}:{shoulder},{elbow},{wrist}")
            
            return {"success": True, "message": "Movement executed successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_robot_speech(self, data):
        """Handle robot speech commands"""
        try:
            text = data.get('text', '')
            if text:
                # Use TTS if available (from prueba.py functionality)
                if hasattr(self.robot_gui, 'tts_engine'):
                    self.robot_gui.tts_engine.say(text)
                    self.robot_gui.tts_engine.runAndWait()
                else:
                    print(f"Robot says: {text}")
            
            return {"success": True, "message": "Speech executed successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_start_class(self, data):
        """Handle start class command"""
        try:
            class_id = data.get('classId')
            classes = self.get_available_classes()['classes']
            selected_class = next((c for c in classes if c['id'] == class_id), None)
            
            if not selected_class:
                return {"success": False, "error": "Class not found"}
            
            # Execute class movements
            if 'movements' in selected_class:
                threading.Thread(target=self.execute_class_movements, 
                               args=(selected_class['movements'],), 
                               daemon=True).start()
            
            return {"success": True, "message": f"Class '{selected_class['title']}' started"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_stop_class(self, data):
        """Handle stop class command"""
        try:
            # Stop any ongoing class execution
            return {"success": True, "message": "Class stopped successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_execute_preset(self, data):
        """Handle execute preset command"""
        try:
            preset_name = data.get('preset')
            
            # Execute preset based on name
            if preset_name == "saludo":
                threading.Thread(target=self.execute_saludo_preset, daemon=True).start()
            elif preset_name == "aplauso":
                threading.Thread(target=self.execute_aplauso_preset, daemon=True).start()
            elif preset_name == "punto":
                threading.Thread(target=self.execute_punto_preset, daemon=True).start()
            elif preset_name == "ok":
                threading.Thread(target=self.execute_ok_preset, daemon=True).start()
            elif preset_name == "paz":
                threading.Thread(target=self.execute_paz_preset, daemon=True).start()
            elif preset_name == "pensativo":
                threading.Thread(target=self.execute_pensativo_preset, daemon=True).start()
            
            return {"success": True, "message": f"Preset '{preset_name}' executed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_emergency_stop(self):
        """Handle emergency stop command"""
        try:
            # Stop all movements and return to safe position
            if hasattr(self.robot_gui, 'center_inmoov_pose'):
                self.robot_gui.center_inmoov_pose()
            
            # Send emergency stop to ESP32
            if hasattr(self.robot_gui, 'esp32') and self.robot_gui.esp32 and self.robot_gui.esp32.connected:
                self.robot_gui.esp32.send_command("EMERGENCY_STOP")
            
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
    
    def execute_class_movements(self, movements):
        """Execute a sequence of class movements"""
        for movement in movements:
            try:
                action = movement.get('action')
                
                if action == 'speak':
                    self.handle_robot_speech({'text': movement.get('text', '')})
                elif action == 'move':
                    move_data = {k: v for k, v in movement.items() if k != 'action'}
                    self.handle_robot_movement(move_data)
                elif action == 'preset':
                    self.handle_execute_preset({'preset': movement.get('name', '')})
                
                # Wait for duration if specified
                duration = movement.get('duration', 1)
                time.sleep(duration)
                
            except Exception as e:
                print(f"Error executing movement: {e}")
    
    def execute_saludo_preset(self):
        """Execute saludo preset"""
        # Raise right arm and wave
        self.handle_robot_movement({
            'part': 'rightArm',
            'shoulder': 45,
            'elbow': 90,
            'wrist': 0
        })
        time.sleep(1)
        # Wave motion
        for i in range(3):
            self.handle_robot_movement({'part': 'rightArm', 'wrist': 30})
            time.sleep(0.5)
            self.handle_robot_movement({'part': 'rightArm', 'wrist': -30})
            time.sleep(0.5)
        # Return to rest
        self.handle_robot_movement({'part': 'rightArm', 'shoulder': 0, 'elbow': 0, 'wrist': 0})
    
    def execute_aplauso_preset(self):
        """Execute aplauso preset"""
        # Clapping motion
        for i in range(5):
            self.handle_robot_movement({
                'part': 'leftArm',
                'shoulder': 45,
                'elbow': 90
            })
            self.handle_robot_movement({
                'part': 'rightArm', 
                'shoulder': -45,
                'elbow': 90
            })
            time.sleep(0.3)
    
    def execute_punto_preset(self):
        """Execute pointing preset"""
        self.handle_robot_movement({
            'part': 'rightArm',
            'shoulder': 30,
            'elbow': 45,
            'wrist': 0
        })
        time.sleep(2)
        self.handle_robot_movement({'part': 'rightArm', 'shoulder': 0, 'elbow': 0, 'wrist': 0})
    
    def execute_ok_preset(self):
        """Execute OK gesture preset"""
        self.handle_robot_movement({
            'part': 'rightArm',
            'shoulder': 30,
            'elbow': 60,
            'wrist': 0
        })
        time.sleep(2)
        self.handle_robot_movement({'part': 'rightArm', 'shoulder': 0, 'elbow': 0, 'wrist': 0})
    
    def execute_paz_preset(self):
        """Execute peace sign preset"""
        self.handle_robot_movement({
            'part': 'rightArm',
            'shoulder': 45,
            'elbow': 90,
            'wrist': 0
        })
        time.sleep(2)
        self.handle_robot_movement({'part': 'rightArm', 'shoulder': 0, 'elbow': 0, 'wrist': 0})
    
    def execute_pensativo_preset(self):
        """Execute thoughtful pose preset"""
        self.handle_robot_movement({
            'part': 'rightArm',
            'shoulder': 60,
            'elbow': 120,
            'wrist': 0
        })
        self.handle_robot_movement({
            'part': 'head',
            'x': 0,
            'y': -15,
            'z': 0
        })
        time.sleep(3)
        # Return to neutral
        self.handle_robot_movement({'part': 'rightArm', 'shoulder': 0, 'elbow': 0, 'wrist': 0})
        self.handle_robot_movement({'part': 'head', 'x': 0, 'y': 0, 'z': 0})

class MobileAPIServer(HTTPServer):
    """HTTP Server for mobile app communication"""
    
    def __init__(self, robot_gui, host='localhost', port=8080):
        self.robot_gui = robot_gui
        super().__init__((host, port), MobileAPIHandler)
        print(f"Mobile API Server started on {host}:{port}")

class RobotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ADAI Robot System - Control Panel")
        self.root.geometry("1400x700")  # Reduced height from 900 to 700
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

        # InMoov simulator state (3D torso-up: head + both arms)
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
        # joints
        self.inmoov_head_angles = {'yaw': 0.0, 'pitch': 0.0}
        self.inmoov_left_arm = {'yaw': -0.4, 'pitch': 0.3, 'elbow': 0.8}
        self.inmoov_right_arm = {'yaw': 0.4, 'pitch': 0.3, 'elbow': 0.8}
        # camera view controls (yaw/pitch in degrees, distance in world units)
        self.inmoov_cam_yaw_deg = tk.DoubleVar(value=0.0)
        self.inmoov_cam_pitch_deg = tk.DoubleVar(value=0.0)
        self.inmoov_cam_dist = tk.DoubleVar(value=400.0)
        self.inmoov_cam_x = tk.DoubleVar(value=0.0)
        self.inmoov_cam_y = tk.DoubleVar(value=0.0)
        self.inmoov_cam_z = tk.DoubleVar(value=0.0)
        # mouse drag state for simulator camera
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

        # ESP32 integration
        self.esp32_enabled = tk.BooleanVar(value=False)
        self.esp32_host = tk.StringVar(value="192.168.1.100")
        self.esp32_port = tk.IntVar(value=80)
        self.esp32_status_label: Optional[tk.Label] = None
        self.esp32: Optional[ESP32Connector] = None
        
        # Quick ESP32 control for Robot Control tab
        self.quick_esp32: Optional[ESP32Connector] = None
        self.esp32_simulator_sync = tk.BooleanVar(value=False)
        
        # Sequence Builder system
        self.sequence_builder_enabled = tk.BooleanVar(value=False)
        self.sequence_recording = False
        self.sequence_playing = False
        self.recorded_positions = []  # List of recorded robot positions
        self.current_sequence = []    # Current sequence being built
        self.sequence_playback_index = 0
        self.sequence_playback_speed = tk.DoubleVar(value=1.0)  # Speed multiplier
        self.sequence_loop = tk.BooleanVar(value=False)  # Loop sequence
        self.sequence_name = tk.StringVar(value="New Sequence")
        self.saved_sequences = {}  # Dictionary of saved sequences
        
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
        
        # Robot arms state tracking for simulator
        self.robot_arms_state = {
            'left_arm': {
                'brazo_izq': 10,    # BI - Brazo Izquierdo
                'frente_izq': 80,   # FI - Frente Izquierdo  
                'high_izq': 80      # HI - High Izquierdo
            },
            'right_arm': {
                'brazo_der': 40,    # BD - Brazo Derecho
                'frente_der': 90,   # FD - Frente Derecho
                'high_der': 80,     # HD - High Derecho
                'pollo_der': 45     # PD - Pollo Derecho
            },
            'timestamp': time.time()
        }
        
        # Arms simulator variables
        self.arms_canvas = None
        self.arms_canvas_size = (800, 600)
        self.arms_update_interval = 50  # ms
        self.arms_history = deque(maxlen=100)  # Store movement history
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
        
        # Mobile App Tab variables
        self.connected_devices = []
        self.mobile_server_running = False
        self.mobile_start_time = None
        self.log_connection_calls = True  # Flag to control /api/connection logging
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
        
        # UI components
        self.video_label = None
        self.object_listbox = None
        self.stats_text = None
        self.position_label = None
        self.connection_labels = {}
        
        self.setup_ui()
        self.setup_camera()
        self.start_status_updates()
        
    def setup_robot_arm_chain(self):
        """Setup the robot arm kinematic chain using ikpy"""
        if not IKPY_AVAILABLE:
            return
            
        try:
            # Create the robot arm chain based on MovimientosBrazo_Robot.py
            pi = math.pi
            
            # Define the links using DH parameters
            link1 = ikpy.link.DHLink("link1", 0, 40, pi/2, pi/2)
            link1.bounds = (0, 0.0000001)
            
            link2 = ikpy.link.DHLink("link2", -80, 0, pi/2, pi/2)
            link3 = ikpy.link.DHLink("link3", 280, 0, pi/2, 0)
            link4 = ikpy.link.DHLink("link4", 0, 280, 0, pi/2)
            
            # Create the chain
            self.arm_chain = Chain(name="arm", links=[
                ikpy.link.OriginLink(),
                link1,
                link2,
                link3,
                link4,
            ])
            
            # Initialize joint angles
            self.arm_current_angles = [0, 0, 0, 0, 0]
            
            print("Robot arm kinematic chain initialized successfully")
            
        except Exception as e:
            print(f"Error setting up robot arm chain: {e}")
            self.arm_chain = None

    def calculate_arm_ik(self):
        """Calculate inverse kinematics for the robot arm"""
        if not IKPY_AVAILABLE or self.arm_chain is None:
            messagebox.showerror("Error", "Robot arm IK not available")
            return
            
        try:
            # Get target position from UI
            x = self.arm_x_var.get()
            y = self.arm_y_var.get()
            z = self.arm_z_var.get()
            
            target_position = [x, y, z]
            self.arm_target_position = target_position
            
            # Calculate inverse kinematics
            angles = self.arm_chain.inverse_kinematics(target_position)
            
            # Convert to degrees and update current angles
            self.arm_current_angles = [math.degrees(angle) for angle in angles]
            
            # Update UI labels
            self.update_arm_angles_display()
            
            # Add to action history
            action = f"Calculated IK for position ({x:.1f}, {y:.1f}, {z:.1f})"
            self.action_history.append(action)
            
            print(f"IK calculated: {target_position} -> {self.arm_current_angles}")
            
        except Exception as e:
            error_msg = f"Error calculating IK: {e}"
            print(error_msg)
            messagebox.showerror("IK Error", error_msg)

    def move_arm_to_target(self):
        """Move the robot arm to the calculated target position"""
        if not IKPY_AVAILABLE or self.arm_chain is None:
            messagebox.showerror("Error", "Robot arm IK not available")
            return
            
        try:
            # First calculate IK if not already done
            if all(angle == 0 for angle in self.arm_current_angles):
                self.calculate_arm_ik()
            
            # Convert angles back to radians
            angles_rad = [math.radians(angle) for angle in self.arm_current_angles]
            
            # Here you would send the angles to the actual robot
            # For now, we'll just simulate the movement
            print(f"Moving arm to angles: {self.arm_current_angles}")
            
            # Add to action history
            action = f"Moved arm to target position {self.arm_target_position}"
            self.action_history.append(action)
            
            # Update robot position in simulation
            self.update_robot_arm_simulation()
            
            messagebox.showinfo("Success", "Arm movement command sent!")
            
        except Exception as e:
            error_msg = f"Error moving arm: {e}"
            print(error_msg)
            messagebox.showerror("Movement Error", error_msg)

    def show_arm_3d_plot(self):
        """Show 3D plot of the robot arm"""
        if not IKPY_AVAILABLE or self.arm_chain is None:
            messagebox.showerror("Error", "Robot arm IK not available")
            return
            
        try:
            # Calculate IK if needed
            if all(angle == 0 for angle in self.arm_current_angles):
                self.calculate_arm_ik()
            
            # Convert angles to radians
            angles_rad = [math.radians(angle) for angle in self.arm_current_angles]
            
            # Create 3D plot
            fig = matplotlib.pyplot.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # Plot the arm
            self.arm_chain.plot(angles_rad, ax)
            
            # Add target point
            ax.scatter([self.arm_target_position[0]], 
                      [self.arm_target_position[1]], 
                      [self.arm_target_position[2]], 
                      color='red', s=100, label='Target')
            
            # Set labels and title
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('Robot Arm 3D Visualization')
            ax.legend()
            
            # Show the plot
            matplotlib.pyplot.show()
            
        except Exception as e:
            error_msg = f"Error creating 3D plot: {e}"
            print(error_msg)
            messagebox.showerror("Plot Error", error_msg)

    def update_arm_angles_display(self):
        """Update the joint angles display in the UI"""
        if not hasattr(self, 'arm_angles_labels'):
            return
            
        for i, (label, angle) in enumerate(zip(self.arm_angles_labels, self.arm_current_angles)):
            label.configure(text=f"{angle:.1f}°")

    def update_robot_arm_simulation(self):
        """Update the robot arm simulation based on IK calculations"""
        if not self.arm_ik_enabled.get():
            return
            
        # Update the robot position based on the calculated end effector position
        # This is a simplified mapping - in a real implementation you'd use forward kinematics
        try:
            if self.arm_chain is not None:
                angles_rad = [math.radians(angle) for angle in self.arm_current_angles]
                end_effector_pos = self.arm_chain.forward_kinematics(angles_rad)[:3, 3]
                
                # Map 3D position to 2D camera coordinates (simplified)
                # In a real implementation, you'd have proper camera calibration
                camera_x = int(320 + end_effector_pos[0] * 0.5)  # Scale factor
                camera_y = int(240 - end_effector_pos[1] * 0.5)  # Invert Y and scale
                
                # Clamp to camera bounds
                camera_x = max(0, min(640, camera_x))
                camera_y = max(0, min(480, camera_y))
                
                self.robot_position = (camera_x, camera_y)
                
        except Exception as e:
            print(f"Error updating robot arm simulation: {e}")

    def map_camera_to_arm_coordinates(self, camera_point):
        """Map camera coordinates to robot arm coordinates"""
        # This is a simplified mapping - in a real implementation you'd use proper calibration
        camera_x, camera_y = camera_point
        
        # Map from camera coordinates (640x480) to robot workspace
        # Assuming robot workspace is roughly -500 to 500 in X and Z, 0 to 1000 in Y
        arm_x = (camera_x - 320) * 2.0  # Scale and center
        arm_y = 500 - (camera_y - 240) * 2.0  # Invert Y and scale
        arm_z = -300  # Fixed Z for now
        
        return [arm_x, arm_y, arm_z]

    def move_arm_to_detected_object(self, object_index):
        """Move the robot arm to a specific detected object"""
        if not IKPY_AVAILABLE or self.arm_chain is None:
            messagebox.showerror("Error", "Robot arm IK not available")
            return
            
        if not self.detected_objects or object_index >= len(self.detected_objects):
            messagebox.showerror("Error", "Object not found")
            return
            
        try:
            # Get the selected object
            obj = self.detected_objects[object_index]
            
            # Map camera coordinates to arm coordinates
            arm_coords = self.map_camera_to_arm_coordinates(obj['center'])
            
            # Update UI variables
            self.arm_x_var.set(arm_coords[0])
            self.arm_y_var.set(arm_coords[1])
            self.arm_z_var.set(arm_coords[2])
            
            # Calculate IK and move
            self.calculate_arm_ik()
            self.move_arm_to_target()
            
            # Add to action history
            action = f"Moved arm to {obj['type']} at {obj['center']}"
            self.action_history.append(action)
            
        except Exception as e:
            error_msg = f"Error moving arm to object: {e}"
            print(error_msg)
            messagebox.showerror("Movement Error", error_msg)

    def export_arm_data(self):
        """Export robot arm data to JSON"""
        if not IKPY_AVAILABLE or self.arm_chain is None:
            messagebox.showerror("Error", "Robot arm IK not available")
            return
            
        try:
            data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'arm_configuration': {
                    'chain_name': self.arm_chain.name,
                    'target_position': self.arm_target_position,
                    'current_angles': self.arm_current_angles,
                    'joint_names': self.arm_joint_names
                },
                'detected_objects': [
                    {
                        'type': obj['type'],
                        'center': obj['center'],
                        'arm_coordinates': self.map_camera_to_arm_coordinates(obj['center'])
                    }
                    for obj in self.detected_objects
                ]
            }
            
            filename = f"robot_arm_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            messagebox.showinfo("Export Successful", f"Arm data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export arm data: {e}")
        
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame with both vertical and horizontal scrollbars"""
        # Main container
        container = tk.Frame(parent, bg='#1e1e1e')
        container.pack(fill="both", expand=True)
        
        # Create canvas and scrollbars
        canvas = tk.Canvas(container, bg='#1e1e1e', highlightthickness=0)
        v_scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        
        # Create the scrollable frame
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel events
        def on_mousewheel(event):
            if event.state == 0:  # No modifier key
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif event.state == 1:  # Shift key
                canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
            widget.bind("<Shift-Button-4>", lambda e: canvas.xview_scroll(-1, "units"))
            widget.bind("<Shift-Button-5>", lambda e: canvas.xview_scroll(1, "units"))
        
        # Bind to canvas and scrollable frame
        bind_mousewheel(canvas)
        bind_mousewheel(scrollable_frame)
        
        # Update canvas scroll region when window size changes
        def configure_canvas(event):
            # Update the scrollable frame width to match canvas width if needed
            canvas_width = event.width
            if scrollable_frame.winfo_reqwidth() < canvas_width:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas)
        
        # Return the scrollable frame and canvas for further configuration
        return scrollable_frame, canvas, container

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
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure notebook style
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2d2d2d', foreground='#ffffff', 
                       padding=[10, 5], font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#4CAF50'), ('active', '#3d3d3d')])
        
        # Initialize class manager
        self.class_manager = None
        if CLASS_MANAGER_AVAILABLE:
            try:
                self.class_manager = get_class_manager()
                print("✅ Class manager initialized")
            except Exception as e:
                print(f"⚠️ Error initializing class manager: {e}")
        else:
            print("⚠️ Class manager not available")

        # Create tabs using modular system
        self.setup_modular_tabs()  # All tabs are now modular
    
    def setup_modular_tabs(self):
        """Setup all tabs using modular system"""
        try:
            # Create and setup all modular tabs
            self.main_tab = MainTab(self, self.notebook)
            self.main_tab.create_tab()
            
            self.esp32_tab = ESP32Tab(self, self.notebook)
            self.esp32_tab.create_tab()
            
            self.sequence_builder_tab = SequenceBuilderTab(self, self.notebook)
            self.sequence_builder_tab.create_tab()
            
            self.settings_tab = SettingsTab(self, self.notebook)
            self.settings_tab.create_tab()
            
            self.simulator_tab = SimulatorTab(self, self.notebook)
            self.simulator_tab.create_tab()
            
            self.class_builder_tab = ClassBuilderTab(self, self.notebook)
            self.class_builder_tab.create_tab()
            
            self.class_controller_tab = ClassControllerTab(self, self.notebook)
            self.class_controller_tab.create_tab()
            
            self.mobile_app_tab = MobileAppTab(self, self.notebook)
            self.mobile_app_tab.create_tab()
            
            self.students_manager_tab = StudentsManagerTab(self, self.notebook)
            self.students_manager_tab.create_tab()

            # Classes Manager Tab
            try:
                self.classes_manager_tab = ClassesManagerTab(self, self.notebook)
                self.classes_manager_tab.create_tab()
                print("✅ Classes Manager tab created")
            except Exception as e:
                print(f"⚠️ Error creating Classes Manager tab: {e}")

            print("✅ All modular tabs created successfully")
            
        except Exception as e:
            print(f"❌ Error creating modular tabs: {e}")
            # Fallback to legacy methods if modular fails
            self.setup_main_tab()
            self.setup_esp32_tab()
            self.setup_sequence_builder_tab()
            self.setup_settings_tab()
            self.setup_simulator_tab()
            self.setup_class_builder_tab()
            self.setup_class_controller_tab()
            self.setup_mobile_app_tab()
            self.setup_students_manager_tab()
            self.setup_classes_manager_tab()
    
    def setup_main_tab(self):
        """Setup the main robot control tab (legacy fallback)"""
        main_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(main_tab, text="🤖 Robot Control")
        tk.Label(main_tab, text="Main tab fallback - please restart application", 
                bg='#1e1e1e', fg='#ff0000', font=('Arial', 14)).pack(pady=50)
    
    def setup_esp32_tab(self):
        """Setup the ESP32 controller tab (legacy fallback)"""
        esp32_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(esp32_tab, text="🔌 ESP32 Controller")
        tk.Label(esp32_tab, text="ESP32 tab fallback - please restart application", 
                bg='#1e1e1e', fg='#ff0000', font=('Arial', 14)).pack(pady=50)
    
    def setup_sequence_builder_tab(self):
        """Setup the sequence builder tab (legacy fallback)"""
        sequence_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(sequence_tab, text="🎬 Sequence Builder")
        tk.Label(sequence_tab, text="Sequence Builder fallback - please restart application", 
                bg='#1e1e1e', fg='#ff0000', font=('Arial', 14)).pack(pady=50)
    
    def setup_settings_tab(self):
        """Setup the settings and configuration tab (legacy fallback)"""
        settings_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(settings_tab, text="⚙️ Settings")
        tk.Label(settings_tab, text="Settings tab fallback - please restart application", 
                bg='#1e1e1e', fg='#ff0000', font=('Arial', 14)).pack(pady=50)
    
    def setup_simulator_tab(self):
        """Setup the robot arms simulator tab (legacy fallback)"""
        simulator_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(simulator_tab, text="🦾 Simulador")
        tk.Label(simulator_tab, text="Simulator tab fallback - please restart application", 
                bg='#1e1e1e', fg='#ff0000', font=('Arial', 14)).pack(pady=50)
    
    def setup_class_builder_tab(self):
        """Setup the simplified class builder tab (legacy fallback)"""
        class_builder_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(class_builder_tab, text="🏗️ Class Builder")
        tk.Label(class_builder_tab, text="Class Builder fallback - please restart application", 
                bg='#1e1e1e', fg='#ff0000', font=('Arial', 14)).pack(pady=50)

    def setup_step_1_basic_info(self, parent):
        """Step 1: Basic class information"""
        step1_frame = tk.LabelFrame(parent, text="📝 Paso 1: Información Básica de la Clase", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step1_frame.pack(fill="x", pady=(0, 15))
        
        form_frame = tk.Frame(step1_frame, bg='#2d2d2d')
        form_frame.pack(fill="x", padx=20, pady=15)
        
        # Two column layout
        left_col = tk.Frame(form_frame, bg='#2d2d2d')
        left_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        right_col = tk.Frame(form_frame, bg='#2d2d2d')
        right_col.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Class title
        tk.Label(left_col, text="Título de la Clase:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        self.class_title_var = tk.StringVar(value="Mi Clase de Robótica")
        tk.Entry(left_col, textvariable=self.class_title_var, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10), width=35).pack(fill="x", pady=(5, 15))
        
        # Subject
        tk.Label(right_col, text="Materia/Tema:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        self.class_subject_var = tk.StringVar(value="Robots Médicos")
        
        # Subject dropdown
        subject_options = [
            "Robots Médicos",
            "Exoesqueletos de Rehabilitación", 
            "Desafíos IoMT",
            "Robótica Industrial",
            "Inteligencia Artificial",
            "Otra materia"
        ]
        subject_combo = ttk.Combobox(right_col, textvariable=self.class_subject_var, 
                                   values=subject_options, state="readonly", width=33)
        subject_combo.pack(fill="x", pady=(5, 15))
        
        # Description
        tk.Label(left_col, text="Descripción:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        self.class_description_var = tk.StringVar(value="Una clase sobre la aplicación de robots en medicina")
        description_entry = tk.Text(left_col, bg='#3d3d3d', fg='#ffffff',
                                   font=('Arial', 10), height=3, wrap=tk.WORD)
        description_entry.pack(fill="x", pady=(5, 0))
        description_entry.insert("1.0", self.class_description_var.get())
        
        # Bind text widget to StringVar
        def on_description_change(*args):
            self.class_description_var.set(description_entry.get("1.0", tk.END).strip())
        description_entry.bind('<KeyRelease>', on_description_change)
        
        # Duration and level
        tk.Label(right_col, text="Duración estimada:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        self.class_duration_var = tk.StringVar(value="45 minutos")
        duration_combo = ttk.Combobox(right_col, textvariable=self.class_duration_var, 
                                    values=["30 minutos", "45 minutos", "60 minutos", "90 minutos"], 
                                    state="readonly", width=33)
        duration_combo.pack(fill="x", pady=(5, 15))

    def setup_step_2_diagnostic_test(self, parent):
        """Step 2: Diagnostic test configuration"""
        step2_frame = tk.LabelFrame(parent, text="📱 Paso 2: Prueba Diagnóstica (QR Code)", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step2_frame.pack(fill="x", pady=(0, 15))
        
        content_frame = tk.Frame(step2_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Instructions
        info_label = tk.Label(content_frame, 
                            text="La prueba diagnóstica se muestra al inicio de la clase para evaluar conocimientos previos",
                            bg='#2d2d2d', fg='#888888', font=('Arial', 10))
        info_label.pack(anchor="w", pady=(0, 10))
        
        # QR selection frame
        qr_frame = tk.Frame(content_frame, bg='#2d2d2d')
        qr_frame.pack(fill="x")
        
        # QR path
        tk.Label(qr_frame, text="Imagen QR de Prueba Diagnóstica:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        qr_input_frame = tk.Frame(qr_frame, bg='#2d2d2d')
        qr_input_frame.pack(fill="x", pady=(5, 15))
        
        self.diagnostic_qr_path = tk.StringVar()
        tk.Entry(qr_input_frame, textvariable=self.diagnostic_qr_path, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 9), state="readonly").pack(side="left", fill="x", expand=True)
        
        tk.Button(qr_input_frame, text="📁 Seleccionar QR", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=lambda: self.select_qr_file(self.diagnostic_qr_path, "Seleccionar QR de Prueba Diagnóstica")).pack(side="right", padx=(10, 0))
        
        # Pre-existing QR options
        tk.Label(qr_frame, text="O selecciona una prueba diagnóstica existente:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(anchor="w", pady=(10, 5))
        
        existing_qrs = tk.Frame(qr_frame, bg='#2d2d2d')
        existing_qrs.pack(fill="x")
        
        self.diagnostic_preset_var = tk.StringVar()
        preset_options = [
            ("Robots Médicos", "diagnostic"),
            ("Exoesqueletos", "diagnostic_Exoesqueletos"),
            ("IoMT", "diagnostic_IoMT"),
            ("Personalizada", "custom")
        ]
        
        for i, (text, value) in enumerate(preset_options):
            tk.Radiobutton(existing_qrs, text=text, variable=self.diagnostic_preset_var, value=value,
                          bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                          font=('Arial', 10), command=self.on_diagnostic_preset_change).pack(side="left", padx=(0, 20))

    def setup_step_3_class_content(self, parent):
        """Step 3: Main class content (PDF)"""
        step3_frame = tk.LabelFrame(parent, text="📚 Paso 3: Contenido Principal de la Clase (PDF)", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step3_frame.pack(fill="x", pady=(0, 15))
        
        content_frame = tk.Frame(step3_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Instructions
        info_label = tk.Label(content_frame, 
                            text="El PDF contiene las diapositivas que ADAI explicará durante la clase con preguntas aleatorias",
                            bg='#2d2d2d', fg='#888888', font=('Arial', 10))
        info_label.pack(anchor="w", pady=(0, 10))
        
        # PDF selection
        pdf_frame = tk.Frame(content_frame, bg='#2d2d2d')
        pdf_frame.pack(fill="x")
        
        tk.Label(pdf_frame, text="Archivo PDF de la Presentación:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        pdf_input_frame = tk.Frame(pdf_frame, bg='#2d2d2d')
        pdf_input_frame.pack(fill="x", pady=(5, 15))
        
        self.class_pdf_path = tk.StringVar()
        tk.Entry(pdf_input_frame, textvariable=self.class_pdf_path, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 9), state="readonly").pack(side="left", fill="x", expand=True)
        
        tk.Button(pdf_input_frame, text="📁 Seleccionar PDF", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=lambda: self.select_pdf_file_for_class()).pack(side="right", padx=(10, 0))
        
        # PDF analysis button
        tk.Button(pdf_input_frame, text="📊 Analizar PDF", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=self.analyze_class_pdf).pack(side="right", padx=(10, 0))
        
        # Pre-existing PDF options
        tk.Label(pdf_frame, text="O selecciona un contenido existente:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(anchor="w", pady=(15, 5))
        
        existing_pdfs = tk.Frame(pdf_frame, bg='#2d2d2d')
        existing_pdfs.pack(fill="x")
        
        self.pdf_preset_var = tk.StringVar()
        pdf_preset_options = [
            ("Robots Médicos", "RobotsMedicos.pdf"),
            ("Exoesqueletos", "ExoesqueletosDeRehabilitacion.pdf"),
            ("IoMT", "DesafiosDeIoMT.pdf"),
            ("Personalizado", "custom")
        ]
        
        for i, (text, value) in enumerate(pdf_preset_options):
            tk.Radiobutton(existing_pdfs, text=text, variable=self.pdf_preset_var, value=value,
                          bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                          font=('Arial', 10), command=self.on_pdf_preset_change).pack(side="left", padx=(0, 20))

    def setup_step_4_final_exam(self, parent):
        """Step 4: Final exam configuration"""
        step4_frame = tk.LabelFrame(parent, text="🎓 Paso 4: Examen Final (QR Code)", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step4_frame.pack(fill="x", pady=(0, 15))
        
        content_frame = tk.Frame(step4_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Instructions
        info_label = tk.Label(content_frame, 
                            text="El examen final se muestra al terminar la clase para evaluar el aprendizaje",
                            bg='#2d2d2d', fg='#888888', font=('Arial', 10))
        info_label.pack(anchor="w", pady=(0, 10))
        
        # QR selection frame
        qr_frame = tk.Frame(content_frame, bg='#2d2d2d')
        qr_frame.pack(fill="x")
        
        # QR path
        tk.Label(qr_frame, text="Imagen QR de Examen Final:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        qr_input_frame = tk.Frame(qr_frame, bg='#2d2d2d')
        qr_input_frame.pack(fill="x", pady=(5, 15))
        
        self.final_exam_qr_path = tk.StringVar()
        tk.Entry(qr_input_frame, textvariable=self.final_exam_qr_path, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 9), state="readonly").pack(side="left", fill="x", expand=True)
        
        tk.Button(qr_input_frame, text="📁 Seleccionar QR", bg='#9C27B0', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=lambda: self.select_qr_file(self.final_exam_qr_path, "Seleccionar QR de Examen Final")).pack(side="right", padx=(10, 0))
        
        # Pre-existing QR options
        tk.Label(qr_frame, text="O selecciona un examen existente:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(anchor="w", pady=(10, 5))
        
        existing_exams = tk.Frame(qr_frame, bg='#2d2d2d')
        existing_exams.pack(fill="x")
        
        self.exam_preset_var = tk.StringVar()
        exam_preset_options = [
            ("Robots Médicos I", "final_examI"),
            ("Robots Médicos II", "final_examII"),
            ("Exoesqueletos I", "final_examExoI"),
            ("IoMT", "final_examIoMT"),
            ("Personalizado", "custom")
        ]
        
        for i, (text, value) in enumerate(exam_preset_options):
            tk.Radiobutton(existing_exams, text=text, variable=self.exam_preset_var, value=value,
                          bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                          font=('Arial', 10), command=self.on_exam_preset_change).pack(side="left", padx=(0, 15))

    def setup_step_5_class_generation(self, parent):
        """Step 5: Class generation and execution"""
        step5_frame = tk.LabelFrame(parent, text="🚀 Paso 5: Generación y Ejecución de la Clase", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step5_frame.pack(fill="both", expand=True)
        
        content_frame = tk.Frame(step5_frame, bg='#2d2d2d')
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Left side - Controls
        left_side = tk.Frame(content_frame, bg='#2d2d2d')
        left_side.pack(side="left", fill="y", padx=(0, 15))
        
        # Generation controls
        controls_frame = tk.LabelFrame(left_side, text="Controles de Generación", 
                                     font=('Arial', 11, 'bold'),
                                     bg='#3d3d3d', fg='#ffffff')
        controls_frame.pack(fill="x", pady=(0, 15))
        
        controls_content = tk.Frame(controls_frame, bg='#3d3d3d')
        controls_content.pack(fill="x", padx=15, pady=15)
        
        tk.Button(controls_content, text="🔨 Generar Clase Completa", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.generate_complete_class).pack(fill="x", pady=(0, 10))
        
        tk.Button(controls_content, text="👁️ Vista Previa", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 11, 'bold'), command=self.preview_generated_class).pack(fill="x", pady=(0, 10))
        
        tk.Button(controls_content, text="💾 Guardar Clase", bg='#9C27B0', fg='#ffffff',
                 font=('Arial', 11, 'bold'), command=self.save_generated_class).pack(fill="x", pady=(0, 10))
        
        tk.Button(controls_content, text="▶️ Ejecutar Clase", bg='#FF5722', fg='#ffffff',
                 font=('Arial', 11, 'bold'), command=self.execute_complete_class).pack(fill="x", pady=(0, 5))
        
        # Status frame
        status_frame = tk.LabelFrame(left_side, text="Estado", 
                                   font=('Arial', 11, 'bold'),
                                   bg='#3d3d3d', fg='#ffffff')
        status_frame.pack(fill="x")
        
        status_content = tk.Frame(status_frame, bg='#3d3d3d')
        status_content.pack(fill="x", padx=15, pady=15)
        
        self.class_status_label = tk.Label(status_content, text="✅ Listo para generar clase", 
                                         bg='#3d3d3d', fg='#4CAF50', font=('Arial', 10))
        self.class_status_label.pack(anchor="w")
        
        # Right side - Preview
        right_side = tk.Frame(content_frame, bg='#2d2d2d')
        right_side.pack(side="right", fill="both", expand=True)
        
        # Code preview
        preview_frame = tk.LabelFrame(right_side, text="Vista Previa del Código Generado", 
                                    font=('Arial', 11, 'bold'),
                                    bg='#3d3d3d', fg='#ffffff')
        preview_frame.pack(fill="both", expand=True)
        
        preview_content = tk.Frame(preview_frame, bg='#3d3d3d')
        preview_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Text area with scrollbar
        text_frame = tk.Frame(preview_content, bg='#3d3d3d')
        text_frame.pack(fill="both", expand=True)
        
        self.class_code_preview = tk.Text(text_frame, bg='#1e1e1e', fg='#ffffff',
                                        font=('Consolas', 9), wrap=tk.WORD)
        self.class_code_preview.pack(side="left", fill="both", expand=True)
        
        preview_scrollbar = tk.Scrollbar(text_frame, orient="vertical")
        preview_scrollbar.pack(side="right", fill="y")
        self.class_code_preview.config(yscrollcommand=preview_scrollbar.set)
        preview_scrollbar.config(command=self.class_code_preview.yview)
        
        # Initialize with welcome message
        welcome_msg = """# 🎓 Bienvenido al Creador de Clases ADAI

# Completa los pasos 1-4 y luego haz clic en "Generar Clase Completa"
# para crear automáticamente una clase basada en el flujo de main.py

# El código generado incluirá:
# - Configuración inicial
# - Prueba diagnóstica con QR
# - Explicación de diapositivas con preguntas aleatorias  
# - Examen final con QR
# - Integración completa con ADAI

class ClasePersonalizada:
    def __init__(self):
        print("🤖 Inicializando ADAI...")
        
    def run(self):
        print("🚀 ¡Clase lista para ejecutar!")"""
        
        self.class_code_preview.insert("1.0", welcome_msg)

    # =====================================
    # SIMPLIFIED CLASS BUILDER METHODS  
    # =====================================
    
    def select_qr_file(self, path_var, title):
        """Select QR code image file"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title=title,
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                path_var.set(file_path)
                self.update_class_status(f"✅ QR seleccionado: {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error seleccionando QR: {e}")

    def select_pdf_file_for_class(self):
        """Select PDF file for class content"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="Seleccionar PDF de la Clase",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.class_pdf_path.set(file_path)
                self.update_class_status(f"✅ PDF seleccionado: {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error seleccionando PDF: {e}")

    def on_diagnostic_preset_change(self):
        """Handle diagnostic preset selection"""
        try:
            preset = self.diagnostic_preset_var.get()
            if preset != "custom":
                # Map preset to actual file paths from main.py
                qr_paths = {
                    'diagnostic': os.path.join(os.path.dirname(os.path.abspath(__file__)), "RobotsMedicosExamen", "pruebadiagnosticaRobotsMedicos.jpeg"),
                    'diagnostic_Exoesqueletos': os.path.join(os.path.dirname(os.path.abspath(__file__)), "ExoesqueletosExamen", "pruebadiagnosticaExoesqueletos.jpeg"),
                    'diagnostic_IoMT': os.path.join(os.path.dirname(os.path.abspath(__file__)), "DesafiosIoMTExamen", "pruebadiagnosticaDesafiosIoMT.jpeg")
                }
                
                if preset in qr_paths and os.path.exists(qr_paths[preset]):
                    self.diagnostic_qr_path.set(qr_paths[preset])
                    self.update_class_status(f"✅ Prueba diagnóstica: {preset}")
                else:
                    self.update_class_status(f"⚠️ Archivo no encontrado: {preset}")
            else:
                self.diagnostic_qr_path.set("")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error configurando prueba diagnóstica: {e}")

    def on_pdf_preset_change(self):
        """Handle PDF preset selection"""
        try:
            preset = self.pdf_preset_var.get()
            if preset != "custom":
                pdf_paths = {
                    'RobotsMedicos.pdf': os.path.join(os.path.dirname(os.path.abspath(__file__)), "RobotsMedicos.pdf"),
                    'ExoesqueletosDeRehabilitacion.pdf': os.path.join(os.path.dirname(os.path.abspath(__file__)), "ExoesqueletosDeRehabilitacion.pdf"),
                    'DesafiosDeIoMT.pdf': os.path.join(os.path.dirname(os.path.abspath(__file__)), "DesafiosDeIoMT.pdf")
                }
                
                if preset in pdf_paths and os.path.exists(pdf_paths[preset]):
                    self.class_pdf_path.set(pdf_paths[preset])
                    self.update_class_status(f"✅ PDF de clase: {preset}")
                else:
                    self.update_class_status(f"⚠️ Archivo PDF no encontrado: {preset}")
            else:
                self.class_pdf_path.set("")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error configurando PDF: {e}")

    def on_exam_preset_change(self):
        """Handle exam preset selection"""
        try:
            preset = self.exam_preset_var.get()
            if preset != "custom":
                # Map preset to actual file paths from main.py
                exam_paths = {
                    'final_examI': os.path.join(os.path.dirname(os.path.abspath(__file__)), "RobotsMedicosExamen", "RobotsMedicosExamenI.jpeg"),
                    'final_examII': os.path.join(os.path.dirname(os.path.abspath(__file__)), "RobotsMedicosExamen", "RobotsMedicosExamenII.jpeg"),
                    'final_examExoI': os.path.join(os.path.dirname(os.path.abspath(__file__)), "ExoesqueletosExamen", "ExoesqueletosExamenI.jpeg"),
                    'final_examIoMT': os.path.join(os.path.dirname(os.path.abspath(__file__)), "DesafiosIoMTExamen", "DesafiosIoMTExamenI.png")
                }
                
                if preset in exam_paths and os.path.exists(exam_paths[preset]):
                    self.final_exam_qr_path.set(exam_paths[preset])
                    self.update_class_status(f"✅ Examen final: {preset}")
                else:
                    self.update_class_status(f"⚠️ Archivo de examen no encontrado: {preset}")
            else:
                self.final_exam_qr_path.set("")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error configurando examen: {e}")

    def analyze_class_pdf(self):
        """Analyze the selected PDF for the class"""
        try:
            pdf_path = self.class_pdf_path.get()
            if not pdf_path:
                messagebox.showwarning("Sin PDF", "Por favor selecciona un archivo PDF primero")
                return
            
            # Simple PDF analysis
            self.update_class_status("📊 Analizando PDF...")
            
            import fitz
            with fitz.open(pdf_path) as doc:
                total_pages = len(doc)
                text_sample = ""
                
                # Extract text from first few pages
                for page_num in range(min(3, total_pages)):
                    page = doc[page_num]
                    text_sample += page.get_text()[:200] + "...\n"
                
                analysis_msg = f"""📄 Análisis del PDF:
• Total de páginas: {total_pages}
• Archivo: {os.path.basename(pdf_path)}
• Contenido detectado: {len(text_sample)} caracteres

Muestra del contenido:
{text_sample[:300]}..."""
                
                messagebox.showinfo("Análisis PDF", analysis_msg)
                self.update_class_status(f"✅ PDF analizado: {total_pages} páginas")
                
        except Exception as e:
            self.update_class_status(f"❌ Error analizando PDF: {e}")
            messagebox.showerror("Error", f"Error analizando PDF: {e}")

    def generate_complete_class(self):
        """Generate complete class code based on main.py structure"""
        try:
            self.update_class_status("🔨 Generando clase completa...")
            
            # Validate inputs
            if not self.class_title_var.get().strip():
                messagebox.showwarning("Información faltante", "Por favor ingresa el título de la clase")
                return
                
            # Generate class code based on main.py
            class_code = self._generate_main_py_based_class()
            
            # Update preview
            self.class_code_preview.delete("1.0", tk.END)
            self.class_code_preview.insert("1.0", class_code)
            
            self.generated_class_code = class_code
            self.update_class_status("✅ Clase generada exitosamente")
            
            messagebox.showinfo("Éxito", "¡Clase generada exitosamente! Puedes ver el código en la vista previa.")
            
        except Exception as e:
            self.update_class_status(f"❌ Error generando clase: {e}")
            messagebox.showerror("Error", f"Error generando clase: {e}")

    def _generate_main_py_based_class(self):
        """Generate class code based on main.py structure"""
        try:
            # Get user inputs
            class_title = self.class_title_var.get().strip()
            class_subject = self.class_subject_var.get()
            class_description = self.class_description_var.get().strip()
            duration = self.class_duration_var.get()
            
            diagnostic_qr = self.diagnostic_qr_path.get()
            class_pdf = self.class_pdf_path.get()
            final_exam_qr = self.final_exam_qr_path.get()
            
            # Clean class name for filename
            clean_class_name = "".join(c for c in class_title if c.isalnum() or c in " _-").replace(" ", "_")
            
            # Generate the complete class code
            class_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{class_title}
Materia: {class_subject}
Duración: {duration}

{class_description}

Generado automáticamente por ADAI Class Builder
Basado en la estructura de main.py
"""

import os
import sys
import cv2
import fitz
import time
import multiprocessing
from multiprocessing import Process, Value, Event
import pyttsx3
import speech_recognition as sr
import numpy as np

# Get absolute path for the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

class {clean_class_name}:
    def __init__(self):
        """Inicializar la clase {class_title}"""
        print(f"🤖 Inicializando {class_title}")
        
        # Configuración de archivos
        self.diagnostic_qr = r"{diagnostic_qr}"
        self.class_pdf = r"{class_pdf}"
        self.final_exam_qr = r"{final_exam_qr}"
        
        # Variables de control
        self.hand_raised_counter = multiprocessing.Value('i', 0)
        self.current_slide_num = multiprocessing.Value('i', 1)
        self.exit_flag = multiprocessing.Value('i', 0)
        self.current_hand_raiser = multiprocessing.Value('i', -1)
        
        # Inicializar TTS
        self.engine = self.initialize_tts()
        
    def initialize_tts(self):
        """Inicializar motor de text-to-speech"""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Buscar voz en español
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            return engine
            
        except Exception as e:
            print(f"❌ Error inicializando TTS: {{e}}")
            return None
    
    def speak_with_animation(self, text):
        """Hablar con animación facial"""
        try:
            if self.engine:
                print(f"🤖 ADAI: {{text}}")
                
                # Crear cara animada simple
                img = np.ones((400, 600, 3), dtype=np.uint8) * 50
                
                # Dibujar cara básica
                cv2.circle(img, (300, 200), 150, (100, 100, 100), 3)  # Cara
                cv2.circle(img, (250, 170), 20, (255, 255, 255), -1)   # Ojo izquierdo
                cv2.circle(img, (350, 170), 20, (255, 255, 255), -1)   # Ojo derecho
                cv2.ellipse(img, (300, 250), (50, 30), 0, 0, 180, (255, 255, 255), 3)  # Boca
                
                # Agregar texto
                cv2.putText(img, "ADAI hablando...", (200, 350), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                cv2.imshow("ADAI Robot Face", img)
                cv2.waitKey(100)
                
                # Hablar
                self.engine.say(text)
                self.engine.runAndWait()
                
        except Exception as e:
            print(f"❌ Error en speech: {{e}}")
    
    def show_qr_code(self, qr_path, display_time=30, title="Código QR"):
        """Mostrar código QR en pantalla"""
        try:
            if not qr_path or not os.path.exists(qr_path):
                print(f"⚠️ QR no encontrado: {{qr_path}}")
                return False
                
            print(f"📱 Mostrando {{title}}: {{qr_path}}")
            
            # Cargar y mostrar QR
            qr_img = cv2.imread(qr_path)
            if qr_img is None:
                return False
                
            # Redimensionar para visualización
            height, width = qr_img.shape[:2]
            max_size = 600
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            qr_resized = cv2.resize(qr_img, (new_width, new_height))
            
            cv2.namedWindow(title, cv2.WINDOW_NORMAL)
            cv2.imshow(title, qr_resized)
            
            # Mostrar por tiempo determinado
            for i in range(display_time):
                if cv2.waitKey(1000) & 0xFF == 27:  # ESC to exit
                    break
                    
            cv2.destroyWindow(title)
            return True
            
        except Exception as e:
            print(f"❌ Error mostrando QR: {{e}}")
            return False
    
    def explain_slides(self):
        """Explicar las diapositivas del PDF"""
        try:
            if not self.class_pdf or not os.path.exists(self.class_pdf):
                print(f"⚠️ PDF no encontrado: {{self.class_pdf}}")
                return False
                
            print("📚 Iniciando explicación de diapositivas...")
            
            # Crear ventana para presentación
            cv2.namedWindow("Presentacion", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Presentacion", 800, 600)
            
            with fitz.open(self.class_pdf) as doc:
                total_slides = len(doc)
                
                for slide_num in range(total_slides):
                    if self.exit_flag.value != 0:
                        break
                        
                    page = doc[slide_num]
                    
                    # Convertir página a imagen
                    mat = page.get_pixmap()
                    img_data = mat.tobytes("ppm")
                    img_array = np.frombuffer(img_data, dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                    if img is not None:
                        # Mostrar diapositiva
                        cv2.imshow("Presentacion", img)
                        
                        # Extraer texto de la diapositiva
                        slide_text = page.get_text()
                        
                        # Narrar contenido (simplificado)
                        if slide_text.strip():
                            # Tomar las primeras líneas como resumen
                            lines = slide_text.split('\\n')
                            summary = ' '.join(lines[:3])[:200]
                            self.speak_with_animation(f"En esta diapositiva vemos: {{summary}}")
                        else:
                            self.speak_with_animation(f"Diapositiva {{slide_num + 1}} de {{total_slides}}")
                        
                        # Esperar antes de continuar
                        if cv2.waitKey(3000) & 0xFF == 27:  # ESC to exit
                            break
                
            cv2.destroyWindow("Presentacion")
            return True
            
        except Exception as e:
            print(f"❌ Error explicando diapositivas: {{e}}")
            return False
    
    def run_diagnostic_test(self):
        """Ejecutar prueba diagnóstica"""
        print("\\n" + "="*50)
        print("📱 FASE 1: EVALUACIÓN DIAGNÓSTICA")
        print("="*50)
        
        self.speak_with_animation("Comenzaremos con una evaluación diagnóstica para conocer sus conocimientos previos.")
        
        if self.diagnostic_qr:
            success = self.show_qr_code(self.diagnostic_qr, 30, "Prueba Diagnóstica")
            if success:
                self.speak_with_animation("Por favor, escaneen el código QR y completen la evaluación diagnóstica.")
            else:
                self.speak_with_animation("Continuaremos sin la evaluación diagnóstica.")
        else:
            print("⚠️ No hay prueba diagnóstica configurada")
            self.speak_with_animation("Comenzaremos directamente con la clase.")
    
    def run_class_content(self):
        """Ejecutar contenido principal de la clase"""
        print("\\n" + "="*50)
        print("🤖 FASE 2: CONTENIDO DE LA CLASE")
        print("="*50)
        
        self.speak_with_animation(f"Ahora comenzaremos con la clase: {class_title}")
        
        # Explicar diapositivas
        if self.class_pdf:
            success = self.explain_slides()
            if not success:
                self.speak_with_animation("Hubo un problema con la presentación, pero continuaremos.")
        else:
            self.speak_with_animation("Desarrollaremos la clase de forma interactiva.")
    
    def run_final_exam(self):
        """Ejecutar examen final"""
        print("\\n" + "="*50)
        print("🎓 FASE 3: EXAMEN FINAL")
        print("="*50)
        
        self.speak_with_animation("Excelente trabajo. Ahora es momento del examen final.")
        
        if self.final_exam_qr:
            self.speak_with_animation("Por favor, escaneen el código QR para acceder al examen final.")
            success = self.show_qr_code(self.final_exam_qr, 40, "Examen Final")
            if success:
                self.speak_with_animation("Tómense el tiempo necesario para completar el examen.")
            else:
                self.speak_with_animation("El examen se realizará de forma alternativa.")
        else:
            self.speak_with_animation("Realizaremos una evaluación oral rápida.")
    
    def run(self):
        """Ejecutar la clase completa"""
        try:
            print(f"🚀 Iniciando {class_title}")
            
            # Crear ventana para la cara animada
            cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("ADAI Robot Face", 600, 400)
            
            # Saludo inicial
            self.speak_with_animation(f"Hola, soy ADAI. Bienvenidos a la clase de {class_subject}.")
            self.speak_with_animation("{class_description}")
            
            # Fase 1: Prueba diagnóstica
            self.run_diagnostic_test()
            
            # Fase 2: Contenido de la clase
            self.run_class_content()
            
            # Fase 3: Examen final
            self.run_final_exam()
            
            # Despedida
            self.speak_with_animation("¡Excelente trabajo! Hemos completado la clase. ¡Hasta la próxima!")
            
            # Cleanup
            cv2.destroyAllWindows()
            
            print("✅ Clase completada exitosamente")
            
        except Exception as e:
            print(f"❌ Error ejecutando clase: {{e}}")
            cv2.destroyAllWindows()

def main():
    """Función principal"""
    try:
        # Crear instancia de la clase
        clase = {clean_class_name}()
        
        # Ejecutar la clase
        clase.run()
        
    except KeyboardInterrupt:
        print("\\n🛑 Clase interrumpida por el usuario")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"❌ Error en main: {{e}}")
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
'''
            
            return class_code
            
        except Exception as e:
            raise Exception(f"Error generando código: {e}")

    def preview_generated_class(self):
        """Preview the generated class"""
        if not self.generated_class_code:
            messagebox.showinfo("Sin código", "Primero genera la clase usando 'Generar Clase Completa'")
            return
            
        # The code is already shown in the preview text widget
        messagebox.showinfo("Vista Previa", "El código generado se muestra en el panel de la derecha. Puedes revisarlo y luego guardarlo o ejecutarlo.")

    def save_generated_class(self):
        """Save the generated class to a file"""
        try:
            if not self.generated_class_code:
                messagebox.showwarning("Sin código", "Primero genera la clase usando 'Generar Clase Completa'")
                return
                
            from tkinter import filedialog
            
            # Suggest filename based on class title
            class_title = self.class_title_var.get().strip()
            clean_name = "".join(c for c in class_title if c.isalnum() or c in " _-").replace(" ", "_")
            suggested_name = f"{clean_name}_clase.py"
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar Clase",
                defaultextension=".py",
                initialfile=suggested_name,
                filetypes=[
                    ("Python files", "*.py"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.generated_class_code)
                    
                self.update_class_status(f"✅ Clase guardada: {os.path.basename(file_path)}")
                messagebox.showinfo("Éxito", f"Clase guardada exitosamente en:\\n{file_path}")
                
        except Exception as e:
            self.update_class_status(f"❌ Error guardando: {e}")
            messagebox.showerror("Error", f"Error guardando clase: {e}")

    def execute_complete_class(self):
        """Execute the generated class"""
        try:
            if not self.generated_class_code:
                messagebox.showwarning("Sin código", "Primero genera la clase usando 'Generar Clase Completa'")
                return
                
            if self.class_execution_active:
                messagebox.showinfo("Clase en ejecución", "Ya hay una clase ejecutándose")
                return
                
            # Confirm execution
            if not messagebox.askyesno("Confirmar Ejecución", 
                                     "¿Estás seguro de que quieres ejecutar la clase completa?\\n\\n"
                                     "Esto iniciará ADAI y comenzará la secuencia completa de la clase."):
                return
                
            self.class_execution_active = True
            self.update_class_status("🚀 Ejecutando clase...")
            
            # Execute in separate thread
            import threading
            
            def execute_thread():
                try:
                    # Create a temporary namespace for execution
                    exec_globals = {}
                    exec_locals = {}
                    
                    # Execute the generated code
                    exec(self.generated_class_code, exec_globals, exec_locals)
                    
                    # Find and run the main function
                    if 'main' in exec_locals:
                        exec_locals['main']()
                    else:
                        # Find the class and instantiate it
                        for name, obj in exec_locals.items():
                            if isinstance(obj, type) and hasattr(obj, 'run'):
                                instance = obj()
                                instance.run()
                                break
                                
                    self.root.after(0, lambda: self.update_class_status("✅ Clase ejecutada exitosamente"))
                    
                except Exception as e:
                    error_msg = f"❌ Error ejecutando clase: {e}"
                    self.root.after(0, lambda: self.update_class_status(error_msg))
                    self.root.after(0, lambda: messagebox.showerror("Error de Ejecución", str(e)))
                finally:
                    self.class_execution_active = False
                    
            execution_thread = threading.Thread(target=execute_thread, daemon=True)
            execution_thread.start()
            
        except Exception as e:
            self.class_execution_active = False
            self.update_class_status(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error ejecutando clase: {e}")

    def update_class_status(self, message):
        """Update the class status label"""
        try:
            if hasattr(self, 'class_status_label'):
                self.class_status_label.config(text=message)
                
                # Color coding
                if "✅" in message:
                    self.class_status_label.config(fg='#4CAF50')
                elif "❌" in message:
                    self.class_status_label.config(fg='#f44336')
                elif "⚠️" in message:
                    self.class_status_label.config(fg='#FF9800')
                elif "🚀" in message or "🔨" in message:
                    self.class_status_label.config(fg='#2196F3')
                else:
                    self.class_status_label.config(fg='#ffffff')
                    
        except Exception as e:
            print(f"Error updating status: {e}")
    
    # =====================================
    # LEGACY CLASS BUILDER METHODS (PRESERVED - TODO: REMOVE AFTER FULL MIGRATION)
    # =====================================
    
    def setup_mobile_app_tab_legacy(self):
        """Legacy method - preserved for reference"""
        pass
        
    # Old method definition removed - see line 2629 for actual method
    
    # Duplicate method definition removed - actual method starts at line ~2632
        
        # Class name
        tk.Label(basic_frame, text="Nombre de la Clase:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        self.class_name_var = tk.StringVar()
        tk.Entry(basic_frame, textvariable=self.class_name_var, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10), width=30).pack(fill="x", pady=(5, 10))
        
        # Class description
        tk.Label(basic_frame, text="Descripción:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        self.class_description_var = tk.StringVar()
        tk.Entry(basic_frame, textvariable=self.class_description_var, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10), width=30).pack(fill="x", pady=(5, 10))
        
        # PDF Upload Section
        pdf_frame = tk.LabelFrame(basic_frame, text="📄 Carga de PDF para Análisis Automático", 
                                font=('Arial', 11, 'bold'),
                                bg='#3d3d3d', fg='#ffffff')
        pdf_frame.pack(fill="x", pady=(10, 15))
        
        # PDF file selection
        pdf_controls = tk.Frame(pdf_frame, bg='#3d3d3d')
        pdf_controls.pack(fill="x", padx=10, pady=10)
        
        self.pdf_path_var = tk.StringVar()
        pdf_entry = tk.Entry(pdf_controls, textvariable=self.pdf_path_var, bg='#4d4d4d', fg='#ffffff',
                            font=('Arial', 9), state="readonly")
        pdf_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Button(pdf_controls, text="📁 Seleccionar PDF", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=self.select_pdf_file).pack(side="right")
        
        # PDF analysis controls
        analysis_controls = tk.Frame(pdf_frame, bg='#3d3d3d')
        analysis_controls.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(analysis_controls, text="🤖 Generar Clase Automática", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.generate_class_from_pdf).pack(side="left", padx=5)
        tk.Button(analysis_controls, text="📊 Analizar PDF", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.analyze_pdf_content).pack(side="left", padx=5)
        
        # PDF analysis status
        self.pdf_status_label = tk.Label(pdf_frame, text="Ningún PDF cargado", 
                                        bg='#3d3d3d', fg='#888888', font=('Arial', 9))
        self.pdf_status_label.pack(padx=10, pady=(0, 10))
        
        # Class template selection
        tk.Label(basic_frame, text="Plantilla Base:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        self.class_template_var = tk.StringVar(value="basic_class")
        template_combo = ttk.Combobox(basic_frame, textvariable=self.class_template_var,
                                     values=["basic_class", "presentation_class", "thesis_defense", 
                                            "camera_processor", "speech_handler", "face_recognition", 
                                            "pdf_processor", "auto_generated", "custom"], 
                                     state="readonly", width=28)
        template_combo.pack(fill="x", pady=(5, 10))
        
        # Methods section
        methods_frame = tk.LabelFrame(left_panel, text="Métodos de la Clase", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#3d3d3d', fg='#ffffff')
        methods_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Methods listbox with scrollbar
        methods_list_frame = tk.Frame(methods_frame, bg='#3d3d3d')
        methods_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.methods_listbox = tk.Listbox(methods_list_frame, bg='#4d4d4d', fg='#ffffff',
                                        font=('Arial', 10), selectbackground='#4CAF50')
        methods_scrollbar = tk.Scrollbar(methods_list_frame, orient="vertical")
        self.methods_listbox.config(yscrollcommand=methods_scrollbar.set)
        methods_scrollbar.config(command=self.methods_listbox.yview)
        
        self.methods_listbox.pack(side="left", fill="both", expand=True)
        methods_scrollbar.pack(side="right", fill="y")
        
        # Method controls
        method_controls = tk.Frame(methods_frame, bg='#3d3d3d')
        method_controls.pack(fill="x", padx=5, pady=5)
        
        tk.Button(method_controls, text="Agregar Método", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.add_method_dialog).pack(side="left", padx=5)
        tk.Button(method_controls, text="Editar", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.edit_method_dialog).pack(side="left", padx=5)
        tk.Button(method_controls, text="Eliminar", bg='#f44336', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.remove_method).pack(side="left", padx=5)
        
        # Right panel - Code preview and generation
        right_panel = tk.LabelFrame(main_content, text="Vista Previa del Código", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Code preview text widget with scrollbar
        code_frame = tk.Frame(right_panel, bg='#2d2d2d')
        code_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.code_preview = tk.Text(code_frame, bg='#1e1e1e', fg='#ffffff',
                                  font=('Courier New', 10), wrap="none",
                                  insertbackground='#ffffff')
        code_v_scrollbar = tk.Scrollbar(code_frame, orient="vertical")
        code_h_scrollbar = tk.Scrollbar(code_frame, orient="horizontal")
        
        self.code_preview.config(yscrollcommand=code_v_scrollbar.set, 
                               xscrollcommand=code_h_scrollbar.set)
        code_v_scrollbar.config(command=self.code_preview.yview)
        code_h_scrollbar.config(command=self.code_preview.xview)
        
        self.code_preview.grid(row=0, column=0, sticky="nsew")
        code_v_scrollbar.grid(row=0, column=1, sticky="ns")
        code_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        code_frame.grid_rowconfigure(0, weight=1)
        code_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        control_frame = tk.Frame(right_panel, bg='#2d2d2d')
        control_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(control_frame, text="Generar Código", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.generate_class_code).pack(side="left", padx=5)
        tk.Button(control_frame, text="Guardar Clase", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.save_class_file).pack(side="left", padx=5)
        tk.Button(control_frame, text="Cargar Plantilla", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.load_template).pack(side="left", padx=5)
        tk.Button(control_frame, text="Limpiar", bg='#f44336', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.clear_class_builder).pack(side="left", padx=5)
        
        # Class execution section
        execution_frame = tk.LabelFrame(right_panel, text="🚀 Ejecución de Clase", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#3d3d3d', fg='#ffffff')
        execution_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Execution controls
        exec_controls = tk.Frame(execution_frame, bg='#3d3d3d')
        exec_controls.pack(fill="x", padx=10, pady=10)
        
        tk.Button(exec_controls, text="▶️ Ejecutar Clase", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.execute_generated_class).pack(side="left", padx=5)
        tk.Button(exec_controls, text="⏹️ Detener Ejecución", bg='#f44336', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.stop_class_execution).pack(side="left", padx=5)
        tk.Button(exec_controls, text="📋 Probar Código", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.test_class_code).pack(side="left", padx=5)
        
        # Execution status
        self.execution_status_label = tk.Label(execution_frame, text="Clase no ejecutándose", 
                                             bg='#3d3d3d', fg='#888888', font=('Arial', 10))
        self.execution_status_label.pack(padx=10, pady=(0, 10))
        
        # Initialize class builder variables
        self.current_methods = []
        self.pdf_content = None
        self.pdf_analysis = None
        self.class_execution_thread = None
        self.class_execution_active = False
        self.generated_class_instance = None
        self.update_code_preview()
    
    def setup_mobile_app_tab(self):
        """Setup the mobile app connection and management tab (legacy fallback)"""
        mobile_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(mobile_tab, text="📱 Mobile App")
        tk.Label(mobile_tab, text="Mobile App fallback - please restart application", 
                bg='#1e1e1e', fg='#ff0000', font=('Arial', 14)).pack(pady=50)


        
        # Left panel - Server Configuration and Status
        left_panel = tk.LabelFrame(main_content, text="Configuración del Servidor API", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Server Status Section
        status_frame = tk.Frame(left_panel, bg='#2d2d2d')
        status_frame.pack(fill="x", padx=10, pady=10)
        
        # Server status indicator
        tk.Label(status_frame, text="Estado del Servidor:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        self.server_status_frame = tk.Frame(status_frame, bg='#2d2d2d')
        self.server_status_frame.pack(fill="x", pady=(5, 10))
        
        self.server_status_indicator = tk.Label(self.server_status_frame, text="●", 
                                              font=('Arial', 16), bg='#2d2d2d')
        self.server_status_indicator.pack(side="left")
        
        self.server_status_label = tk.Label(self.server_status_frame, text="Desconectado", 
                                          font=('Arial', 12), bg='#2d2d2d', fg='#ffffff')
        self.server_status_label.pack(side="left", padx=(5, 0))
        
        # Server configuration
        config_frame = tk.Frame(left_panel, bg='#2d2d2d')
        config_frame.pack(fill="x", padx=10, pady=10)
        
        # Port configuration
        tk.Label(config_frame, text="Puerto del Servidor:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        port_frame = tk.Frame(config_frame, bg='#2d2d2d')
        port_frame.pack(fill="x", pady=(5, 10))
        
        self.mobile_port_var = tk.IntVar(value=self.api_port)
        port_entry = tk.Entry(port_frame, textvariable=self.mobile_port_var, 
                             bg='#3d3d3d', fg='#ffffff', font=('Arial', 10), width=10)
        port_entry.pack(side="left")
        
        tk.Button(port_frame, text="Aplicar", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.update_mobile_port).pack(side="left", padx=(10, 0))
        
        # Server URL display
        tk.Label(config_frame, text="URL del Servidor:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        # Get local IP for display
        local_ip = get_local_ip()
        self.server_url_label = tk.Label(config_frame, text=f"http://{local_ip}:{self.api_port}/api", 
                                        bg='#3d3d3d', fg='#4CAF50', font=('Courier New', 10),
                                        relief="sunken", anchor="w")
        self.server_url_label.pack(fill="x", pady=(5, 10))
        
        # Network Information Section
        network_frame = tk.LabelFrame(config_frame, text="Información de Red", 
                                    font=('Arial', 11, 'bold'),
                                    bg='#3d3d3d', fg='#ffffff')
        network_frame.pack(fill="x", pady=(10, 10))
        
        # IP Address display
        ip_frame = tk.Frame(network_frame, bg='#3d3d3d')
        ip_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(ip_frame, text="IP Local:", bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(side="left")
        
        self.ip_display_label = tk.Label(ip_frame, text=local_ip, bg='#4d4d4d', fg='#00ff00',
                                       font=('Courier New', 10, 'bold'), relief="sunken")
        self.ip_display_label.pack(side="left", padx=(10, 0))
        
        # Copy IP button
        tk.Button(ip_frame, text="📋 Copiar IP", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=lambda: self.copy_to_clipboard(local_ip)).pack(side="right")
        
        # Refresh IP button
        tk.Button(ip_frame, text="🔄 Actualizar", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=self.refresh_network_info).pack(side="right", padx=(0, 5))
        
        # Network interfaces info
        interfaces = get_all_network_interfaces()
        if len(interfaces) > 1:
            interfaces_frame = tk.Frame(network_frame, bg='#3d3d3d')
            interfaces_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(interfaces_frame, text="Interfaces de Red:", bg='#3d3d3d', fg='#ffffff',
                    font=('Arial', 10, 'bold')).pack(anchor="w")
            
            for interface in interfaces:
                if interface['ip'] != local_ip:  # Don't show the main IP again
                    interface_frame = tk.Frame(interfaces_frame, bg='#3d3d3d')
                    interface_frame.pack(fill="x", pady=2)
                    
                    tk.Label(interface_frame, text=f"{interface['name']}:", bg='#3d3d3d', fg='#cccccc',
                            font=('Arial', 9)).pack(side="left")
                    
                    tk.Label(interface_frame, text=interface['ip'], bg='#4d4d4d', fg='#ffff00',
                           font=('Courier New', 9), relief="sunken").pack(side="left", padx=(5, 0))
                    
                    tk.Button(interface_frame, text="📋", bg='#2196F3', fg='#ffffff',
                             font=('Arial', 8), 
                             command=lambda ip=interface['ip']: self.copy_to_clipboard(ip)).pack(side="right")
        
        # Server controls
        controls_frame = tk.Frame(left_panel, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(controls_frame, text="🟢 Iniciar Servidor", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.start_mobile_server).pack(side="left", padx=5)
        tk.Button(controls_frame, text="🔴 Detener Servidor", bg='#f44336', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.stop_mobile_server).pack(side="left", padx=5)
        tk.Button(controls_frame, text="🔄 Reiniciar", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.restart_mobile_server).pack(side="left", padx=5)
        
        # Connection Log Section
        log_frame = tk.LabelFrame(left_panel, text="Registro de Conexiones", 
                                font=('Arial', 12, 'bold'),
                                bg='#3d3d3d', fg='#ffffff')
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Log control buttons
        log_controls = tk.Frame(log_frame, bg='#3d3d3d')
        log_controls.pack(fill="x", padx=5, pady=5)
        
        # Toggle connection logging button
        self.connection_log_button = tk.Button(log_controls, text="🔇 Pausar logs /connection", 
                                             bg='#FF5722', fg='#ffffff',
                                             font=('Arial', 10, 'bold'), 
                                             command=self.toggle_connection_logging)
        self.connection_log_button.pack(side="left", padx=(0, 10))
        
        # Clear log button
        tk.Button(log_controls, text="🗑️ Limpiar Log", bg='#607D8B', fg='#ffffff',
                 font=('Arial', 10, 'bold'), 
                 command=self.clear_connection_log).pack(side="left")
        
        # Log text widget with scrollbar
        log_content_frame = tk.Frame(log_frame, bg='#3d3d3d')
        log_content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.mobile_log_text = tk.Text(log_content_frame, bg='#1e1e1e', fg='#ffffff',
                                     font=('Courier New', 9), wrap="word", height=8)
        log_scrollbar = tk.Scrollbar(log_content_frame, orient="vertical")
        self.mobile_log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.mobile_log_text.yview)
        
        self.mobile_log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # Right panel - Connected Devices and API Statistics
        right_panel = tk.LabelFrame(main_content, text="Dispositivos Conectados y Estadísticas", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Connected devices section
        devices_frame = tk.LabelFrame(right_panel, text="Dispositivos Móviles Conectados", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#3d3d3d', fg='#ffffff')
        devices_frame.pack(fill="x", padx=10, pady=10)
        
        # Devices list
        devices_content = tk.Frame(devices_frame, bg='#3d3d3d')
        devices_content.pack(fill="x", padx=5, pady=5)
        
        self.devices_listbox = tk.Listbox(devices_content, bg='#4d4d4d', fg='#ffffff',
                                        font=('Arial', 10), selectbackground='#4CAF50', height=6)
        devices_list_scrollbar = tk.Scrollbar(devices_content, orient="vertical")
        self.devices_listbox.config(yscrollcommand=devices_list_scrollbar.set)
        devices_list_scrollbar.config(command=self.devices_listbox.yview)
        
        self.devices_listbox.pack(side="left", fill="both", expand=True)
        devices_list_scrollbar.pack(side="right", fill="y")
        
        # API Statistics section
        stats_frame = tk.LabelFrame(right_panel, text="Estadísticas de la API", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#3d3d3d', fg='#ffffff')
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Statistics content
        stats_content = tk.Frame(stats_frame, bg='#3d3d3d')
        stats_content.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialize statistics variables
        self.api_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'active_connections': 0,
            'uptime': 0
        }
        
        # Statistics labels
        self.stats_labels = {}
        stats_data = [
            ('Total Requests', 'total_requests'),
            ('Successful', 'successful_requests'),
            ('Failed', 'failed_requests'),
            ('Active Connections', 'active_connections'),
            ('Uptime (min)', 'uptime')
        ]
        
        for i, (label_text, key) in enumerate(stats_data):
            row_frame = tk.Frame(stats_content, bg='#3d3d3d')
            row_frame.pack(fill="x", pady=2)
            
            tk.Label(row_frame, text=f"{label_text}:", bg='#3d3d3d', fg='#ffffff',
                    font=('Arial', 10, 'bold')).pack(side="left")
            
            value_label = tk.Label(row_frame, text="0", bg='#3d3d3d', fg='#4CAF50',
                                 font=('Arial', 10, 'bold'))
            value_label.pack(side="right")
            
            self.stats_labels[key] = value_label
        
        # API Endpoints status
        endpoints_frame = tk.LabelFrame(right_panel, text="Estado de Endpoints", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#3d3d3d', fg='#ffffff')
        endpoints_frame.pack(fill="x", padx=10, pady=10)
        
        endpoints_content = tk.Frame(endpoints_frame, bg='#3d3d3d')
        endpoints_content.pack(fill="x", padx=5, pady=5)
        
        # Endpoints list
        self.endpoints_listbox = tk.Listbox(endpoints_content, bg='#4d4d4d', fg='#ffffff',
                                          font=('Courier New', 9), selectbackground='#4CAF50', height=8)
        endpoints_scrollbar = tk.Scrollbar(endpoints_content, orient="vertical")
        self.endpoints_listbox.config(yscrollcommand=endpoints_scrollbar.set)
        endpoints_scrollbar.config(command=self.endpoints_listbox.yview)
        
        self.endpoints_listbox.pack(side="left", fill="both", expand=True)
        endpoints_scrollbar.pack(side="right", fill="y")
        
        # Update initial status
        self.update_mobile_status()
        self.update_endpoints_list()
        
        # Start periodic updates
        self.update_mobile_stats()
        
    def setup_esp32_connection_panel(self, parent):
        """Setup ESP32 connection settings panel"""
        conn_frame = tk.LabelFrame(parent, text="Connection Settings", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        conn_frame.pack(fill="x", pady=(0, 10))
        
        # Connection settings
        settings_frame = tk.Frame(conn_frame, bg='#2d2d2d')
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # Host and Port
        host_frame = tk.Frame(settings_frame, bg='#2d2d2d')
        host_frame.pack(fill="x", pady=5)
        tk.Label(host_frame, text="Host:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12)).pack(side="left")
        tk.Entry(host_frame, textvariable=self.esp32_host, width=20, 
                bg='#3d3d3d', fg='#ffffff', font=('Arial', 12)).pack(side="left", padx=10)
        
        port_frame = tk.Frame(settings_frame, bg='#2d2d2d')
        port_frame.pack(fill="x", pady=5)
        tk.Label(port_frame, text="Port:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12)).pack(side="left")
        tk.Entry(port_frame, textvariable=self.esp32_port, width=10, 
                bg='#3d3d3d', fg='#ffffff', font=('Arial', 12)).pack(side="left", padx=10)
        
        # Connection controls
        controls_frame = tk.Frame(settings_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", pady=10)
        
        tk.Button(controls_frame, text="Connect", bg='#4CAF50', fg='white', 
                 font=('Arial', 12, 'bold'), command=self.esp32_connect).pack(side="left", padx=(0, 10))
        tk.Button(controls_frame, text="Disconnect", bg='#f44336', fg='white', 
                 font=('Arial', 12, 'bold'), command=self.esp32_disconnect).pack(side="left", padx=10)
        tk.Checkbutton(controls_frame, text="Enable Control", variable=self.esp32_enabled, 
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', 12)).pack(side="right")
        
        # Status display
        self.esp32_status_label = tk.Label(settings_frame, text="ESP32: Disconnected", 
                                          bg='#2d2d2d', fg='#ff8888', 
                                          font=('Consolas', 12, 'bold'))
        self.esp32_status_label.pack(anchor="w", pady=(10, 0))
    
    def setup_esp32_status_panel(self, parent):
        """Setup ESP32 status monitoring panel"""
        status_frame = tk.LabelFrame(parent, text="System Status", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        status_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Status text area
        status_text_frame = tk.Frame(status_frame, bg='#2d2d2d')
        status_text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.esp32_status_text = tk.Text(status_text_frame, 
                                        bg='#3d3d3d', fg='#ffffff',
                                        font=('Consolas', 10),
                                        wrap="word", height=10,
                                        insertbackground='#ffffff',
                                        selectbackground='#4a4a4a',
                                        selectforeground='#ffffff')
        self.esp32_status_text.pack(side="left", fill="both", expand=True)
        
        # Scrollbar for status text
        status_scrollbar = tk.Scrollbar(status_text_frame, orient="vertical")
        status_scrollbar.pack(side="right", fill="y")
        
        self.esp32_status_text.config(yscrollcommand=status_scrollbar.set)
        status_scrollbar.config(command=self.esp32_status_text.yview)
        
        # Configure text tags for status
        self.esp32_status_text.tag_configure("success", foreground="#00ff00")
        self.esp32_status_text.tag_configure("error", foreground="#ff4444")
        self.esp32_status_text.tag_configure("warning", foreground="#ffaa00")
        self.esp32_status_text.tag_configure("info", foreground="#00aaff")
        
    def setup_esp32_control_panels(self, parent):
        """Setup ESP32 control panels with scrollbar"""
        # Create canvas and scrollbar for control panels
        control_canvas = tk.Canvas(parent, bg='#1e1e1e', highlightthickness=0)
        control_scrollbar = tk.Scrollbar(parent, orient="vertical", command=control_canvas.yview)
        control_frame = tk.Frame(control_canvas, bg='#1e1e1e')
        
        # Configure canvas
        control_canvas.configure(yscrollcommand=control_scrollbar.set)
        control_canvas.pack(side="left", fill="both", expand=True)
        control_scrollbar.pack(side="right", fill="y")
        
        # Create window in canvas
        control_canvas.create_window((0, 0), window=control_frame, anchor="nw")
        
        # System controls
        system_frame = tk.LabelFrame(control_frame, text="System Controls", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        system_frame.pack(fill="x", pady=(0, 10))
        
        system_buttons = tk.Frame(system_frame, bg='#2d2d2d')
        system_buttons.pack(fill="x", padx=10, pady=10)
        
        tk.Button(system_buttons, text="Rest Position", bg='#2196F3', fg='white', 
                 command=self.esp32_rest_position, font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(system_buttons, text="Reset", bg='#f44336', fg='white', 
                 command=self.esp32_reset, font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(system_buttons, text="Check Status", bg='#FF9800', fg='white', 
                 command=self.esp32_check, font=('Arial', 10)).pack(side="left", padx=5)
        
        # Arms controls
        arms_frame = tk.LabelFrame(control_frame, text="Arms Control", 
                                 font=('Arial', 12, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        arms_frame.pack(fill="x", pady=(0, 10))
        
        arms_buttons = tk.Frame(arms_frame, bg='#2d2d2d')
        arms_buttons.pack(fill="x", padx=10, pady=10)
        
        tk.Button(arms_buttons, text="Rest", bg='#2196F3', fg='white', 
                 command=self.esp32_arms_rest, font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(arms_buttons, text="Salute", bg='#4CAF50', fg='white', 
                 command=self.esp32_arms_salute, font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(arms_buttons, text="Hug", bg='#9C27B0', fg='white', 
                 command=self.esp32_arms_hug, font=('Arial', 10)).pack(side="left", padx=5)
        
        # Neck controls
        neck_frame = tk.LabelFrame(control_frame, text="Neck Control", 
                                 font=('Arial', 12, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        neck_frame.pack(fill="x", pady=(0, 10))
        
        neck_buttons = tk.Frame(neck_frame, bg='#2d2d2d')
        neck_buttons.pack(fill="x", padx=10, pady=10)
        
        tk.Button(neck_buttons, text="Center", bg='#2196F3', fg='white', 
                 command=self.esp32_neck_center, font=('Arial', 12)).pack(side="left", padx=5)
        tk.Button(neck_buttons, text="Yes", bg='#4CAF50', fg='white', 
                 command=self.esp32_neck_yes, font=('Arial', 12)).pack(side="left", padx=5)
        tk.Button(neck_buttons, text="No", bg='#f44336', fg='white', 
                 command=self.esp32_neck_no, font=('Arial', 12)).pack(side="left", padx=5)
        tk.Button(neck_buttons, text="Random", bg='#FF9800', fg='white', 
                 command=self.esp32_neck_random, font=('Arial', 12)).pack(side="left", padx=5)
        
        # Hands controls
        hands_frame = tk.LabelFrame(control_frame, text="Hands Control", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        hands_frame.pack(fill="x", pady=(0, 10))
        
        hands_buttons1 = tk.Frame(hands_frame, bg='#2d2d2d')
        hands_buttons1.pack(fill="x", padx=10, pady=5)
        
        tk.Button(hands_buttons1, text="Open", bg='#4CAF50', fg='white', 
                 command=lambda: self.esp32_hand_gesture('ambas', 'abrir'), font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(hands_buttons1, text="Close", bg='#f44336', fg='white', 
                 command=lambda: self.esp32_hand_gesture('ambas', 'cerrar'), font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(hands_buttons1, text="Peace", bg='#2196F3', fg='white', 
                 command=lambda: self.esp32_hand_gesture('ambas', 'paz'), font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(hands_buttons1, text="Rock", bg='#9C27B0', fg='white', 
                 command=lambda: self.esp32_hand_gesture('ambas', 'rock'), font=('Arial', 10)).pack(side="left", padx=5)
        
        hands_buttons2 = tk.Frame(hands_frame, bg='#2d2d2d')
        hands_buttons2.pack(fill="x", padx=10, pady=5)
        
        tk.Button(hands_buttons2, text="OK", bg='#FF9800', fg='white', 
                 command=lambda: self.esp32_hand_gesture('ambas', 'ok'), font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(hands_buttons2, text="Point", bg='#607D8B', fg='white', 
                 command=lambda: self.esp32_hand_gesture('ambas', 'senalar'), font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(hands_buttons2, text="Right", bg='#E91E63', fg='white', 
                 command=lambda: self.esp32_hand_gesture('derecha', 'abrir'), font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(hands_buttons2, text="Left", bg='#795548', fg='white', 
                 command=lambda: self.esp32_hand_gesture('izquierda', 'abrir'), font=('Arial', 10)).pack(side="left", padx=5)
        
        # Wrists controls
        wrists_frame = tk.LabelFrame(control_frame, text="Wrists Control", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        wrists_frame.pack(fill="x", pady=(0, 10))
        
        wrists_buttons = tk.Frame(wrists_frame, bg='#2d2d2d')
        wrists_buttons.pack(fill="x", padx=10, pady=10)
        
        tk.Button(wrists_buttons, text="Center", bg='#2196F3', fg='white', 
                 command=self.esp32_wrists_center, font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(wrists_buttons, text="Random", bg='#FF9800', fg='white', 
                 command=self.esp32_wrists_random, font=('Arial', 10)).pack(side="left", padx=5)
        
        # Configure canvas scrolling
        def configure_control_scroll(event):
            control_canvas.configure(scrollregion=control_canvas.bbox("all"))
        
        control_frame.bind("<Configure>", configure_control_scroll)
        
        # Bind mouse wheel to canvas
        def on_control_mousewheel(event):
            control_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        control_canvas.bind("<MouseWheel>", on_control_mousewheel)
    
    def setup_sequence_recording_panel(self, parent):
        """Setup sequence recording panel"""
        recording_frame = tk.LabelFrame(parent, text="🎬 Sequence Recording", 
                                      font=('Arial', 14, 'bold'),
                                      bg='#2d2d2d', fg='#ffffff')
        recording_frame.pack(fill="x", pady=(0, 10))
        
        content_frame = tk.Frame(recording_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=10, pady=10)
        
        # Sequence name
        name_frame = tk.Frame(content_frame, bg='#2d2d2d')
        name_frame.pack(fill="x", pady=5)
        tk.Label(name_frame, text="Sequence Name:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12)).pack(side="left")
        tk.Entry(name_frame, textvariable=self.sequence_name, width=20, 
                bg='#3d3d3d', fg='#ffffff', font=('Arial', 12)).pack(side="left", padx=10)
        
        # Recording controls
        controls_frame = tk.Frame(content_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", pady=10)
        
        self.record_button = tk.Button(controls_frame, text="🔴 Start Recording", 
                                     bg='#f44336', fg='white', 
                                     font=('Arial', 12, 'bold'), 
                                     command=self.start_sequence_recording)
        self.record_button.pack(side="left", padx=(0, 10))
        
        self.stop_record_button = tk.Button(controls_frame, text="⏹️ Stop Recording", 
                                          bg='#666666', fg='white', 
                                          font=('Arial', 12, 'bold'), 
                                          command=self.stop_sequence_recording,
                                          state="disabled")
        self.stop_record_button.pack(side="left", padx=10)
        
        # Quick position recording
        quick_frame = tk.Frame(content_frame, bg='#2d2d2d')
        quick_frame.pack(fill="x", pady=10)
        
        tk.Label(quick_frame, text="Quick Record:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        quick_buttons = tk.Frame(quick_frame, bg='#2d2d2d')
        quick_buttons.pack(fill="x")
        
        tk.Button(quick_buttons, text="📸 Capture Position", bg='#2196F3', fg='white', 
                 command=self.capture_current_position, font=('Arial', 10)).pack(side="left", padx=(0, 10))
        tk.Button(quick_buttons, text="🔄 Capture Simulator", bg='#4CAF50', fg='white', 
                 command=self.capture_simulator_position, font=('Arial', 10)).pack(side="left", padx=10)
             
        # Hand gesture capture buttons
        hand_gestures_frame = tk.Frame(content_frame, bg='#2d2d2d')
        hand_gestures_frame.pack(fill="x", pady=10)
        
        tk.Label(hand_gestures_frame, text="Hand Gestures:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        hand_buttons = tk.Frame(hand_gestures_frame, bg='#2d2d2d')
        hand_buttons.pack(fill="x")
        
        tk.Button(hand_buttons, text="✌️ Peace", bg='#9C27B0', fg='white', 
                 command=lambda: self.capture_hand_gesture('paz'), font=('Arial', 9)).pack(side="left", padx=(0, 5))
        tk.Button(hand_buttons, text="🤘 Rock", bg='#FF5722', fg='white', 
                 command=lambda: self.capture_hand_gesture('rock'), font=('Arial', 9)).pack(side="left", padx=5)
        tk.Button(hand_buttons, text="👌 OK", bg='#4CAF50', fg='white', 
                 command=lambda: self.capture_hand_gesture('ok'), font=('Arial', 9)).pack(side="left", padx=5)
        tk.Button(hand_buttons, text="👆 Point", bg='#2196F3', fg='white', 
                 command=lambda: self.capture_hand_gesture('senalar'), font=('Arial', 9)).pack(side="left", padx=5)
        tk.Button(hand_buttons, text="✋ Open", bg='#FF9800', fg='white', 
                 command=lambda: self.capture_hand_gesture('abrir'), font=('Arial', 9)).pack(side="left", padx=5)
        tk.Button(hand_buttons, text="✊ Close", bg='#795548', fg='white', 
                 command=lambda: self.capture_hand_gesture('cerrar'), font=('Arial', 9)).pack(side="left", padx=5)
        
        # ESP32 Connection status
        self.esp32_connection_status = tk.Label(content_frame, text="ESP32: Not Connected", 
                                              bg='#2d2d2d', fg='#ff0000', 
                                              font=('Consolas', 12, 'bold'))
        self.esp32_connection_status.pack(anchor="w", pady=(10, 0))
             
        # Recording status
        self.recording_status_label = tk.Label(content_frame, text="Status: Ready to record", 
                                             bg='#2d2d2d', fg='#00ff00', 
                                             font=('Consolas', 12, 'bold'))
        self.recording_status_label.pack(anchor="w", pady=(5, 0))
        
        # Recorded positions counter
        self.positions_counter_label = tk.Label(content_frame, text="Positions: 0", 
                                              bg='#2d2d2d', fg='#ffffff', 
                                              font=('Consolas', 12))
        self.positions_counter_label.pack(anchor="w", pady=(5, 0))
    
    def setup_sequence_playback_panel(self, parent):
        """Setup sequence playback panel"""
        playback_frame = tk.LabelFrame(parent, text="▶️ Sequence Playback", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        playback_frame.pack(fill="x", pady=(0, 10))
        
        content_frame = tk.Frame(playback_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=10, pady=10)
        
        # Playback controls
        controls_frame = tk.Frame(content_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", pady=5)
        
        self.play_button = tk.Button(controls_frame, text="▶️ Play Sequence", 
                                   bg='#4CAF50', fg='white', 
                                   font=('Arial', 12, 'bold'), 
                                   command=self.play_sequence)
        self.play_button.pack(side="left", padx=(0, 10))
        
        self.pause_button = tk.Button(controls_frame, text="⏸️ Pause", 
                                    bg='#FF9800', fg='white', 
                                    font=('Arial', 12, 'bold'), 
                                    command=self.pause_sequence,
                                    state="disabled")
        self.pause_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = tk.Button(controls_frame, text="⏹️ Stop", 
                                   bg='#f44336', fg='white', 
                                   font=('Arial', 12, 'bold'), 
                                   command=self.stop_sequence,
                                   state="disabled")
        self.stop_button.pack(side="left", padx=10)
        
        # Playback settings
        settings_frame = tk.Frame(content_frame, bg='#2d2d2d')
        settings_frame.pack(fill="x", pady=10)
        
        # Speed control
        speed_frame = tk.Frame(settings_frame, bg='#2d2d2d')
        speed_frame.pack(fill="x", pady=5)
        tk.Label(speed_frame, text="Speed:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12)).pack(side="left")
        speed_scale = tk.Scale(speed_frame, from_=0.1, to=3.0, resolution=0.1,
                              variable=self.sequence_playback_speed,
                              orient="horizontal", bg='#2d2d2d', fg='#ffffff',
                              highlightthickness=0, length=150)
        speed_scale.pack(side="left", padx=10)
        tk.Label(speed_frame, textvariable=self.sequence_playback_speed, 
                bg='#2d2d2d', fg='#ffffff', font=('Arial', 12)).pack(side="left")
        
        # Loop option
        tk.Checkbutton(settings_frame, text="🔁 Loop Sequence", 
                      variable=self.sequence_loop,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', 12)).pack(anchor="w", pady=5)
        
        # Playback status
        self.playback_status_label = tk.Label(content_frame, text="Status: Ready to play", 
                                            bg='#2d2d2d', fg='#00ff00', 
                                            font=('Consolas', 12, 'bold'))
        self.playback_status_label.pack(anchor="w", pady=(10, 0))
        
        # Progress bar
        self.progress_bar = tk.Scale(content_frame, from_=0, to=100, 
                                    orient="horizontal", bg='#2d2d2d', fg='#ffffff',
                                    highlightthickness=0, state="disabled")
        self.progress_bar.pack(fill="x", pady=(10, 0))
    
    def setup_sequence_management_panel(self, parent):
        """Setup sequence management panel"""
        management_frame = tk.LabelFrame(parent, text="📁 Sequence Management", 
                                       font=('Arial', 14, 'bold'),
                                       bg='#2d2d2d', fg='#ffffff')
        management_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        content_frame = tk.Frame(management_frame, bg='#2d2d2d')
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sequence list
        list_frame = tk.Frame(content_frame, bg='#2d2d2d')
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        tk.Label(list_frame, text="Saved Sequences:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Create listbox with scrollbar
        listbox_frame = tk.Frame(list_frame, bg='#2d2d2d')
        listbox_frame.pack(fill="both", expand=True)
        
        self.sequence_listbox = tk.Listbox(listbox_frame, bg='#3d3d3d', fg='#ffffff',
                                          font=('Consolas', 10), height=8)
        sequence_scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", 
                                        command=self.sequence_listbox.yview)
        self.sequence_listbox.configure(yscrollcommand=sequence_scrollbar.set)
        
        self.sequence_listbox.pack(side="left", fill="both", expand=True)
        sequence_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.sequence_listbox.bind('<<ListboxSelect>>', self.on_sequence_select)
        
        # Management buttons
        buttons_frame = tk.Frame(content_frame, bg='#2d2d2d')
        buttons_frame.pack(fill="x", pady=5)
        
        tk.Button(buttons_frame, text="💾 Save Sequence", bg='#2196F3', fg='white', 
                 command=self.save_sequence, font=('Arial', 10)).pack(side="left", padx=(0, 5))
        tk.Button(buttons_frame, text="📂 Load Sequence", bg='#4CAF50', fg='white', 
                 command=self.load_sequence, font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="🗑️ Delete Sequence", bg='#f44336', fg='white', 
                 command=self.delete_sequence, font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="🔄 Clear Current", bg='#FF9800', fg='white', 
                 command=self.clear_current_sequence, font=('Arial', 10)).pack(side="left", padx=5)
    
    def setup_sequence_details_panel(self, parent):
        """Setup sequence details panel"""
        details_frame = tk.LabelFrame(parent, text="📋 Sequence Details", 
                                    font=('Arial', 14, 'bold'),
                                    bg='#2d2d2d', fg='#ffffff')
        details_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        content_frame = tk.Frame(details_frame, bg='#2d2d2d')
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Current sequence info
        info_frame = tk.Frame(content_frame, bg='#2d2d2d')
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.sequence_info_label = tk.Label(info_frame, text="Current Sequence: None", 
                                          bg='#2d2d2d', fg='#ffffff', 
                                          font=('Arial', 12, 'bold'))
        self.sequence_info_label.pack(anchor="w")
        
        # Position list
        positions_frame = tk.Frame(content_frame, bg='#2d2d2d')
        positions_frame.pack(fill="both", expand=True)
        
        tk.Label(positions_frame, text="Positions:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Create text widget for position details
        self.positions_text = tk.Text(positions_frame, bg='#3d3d3d', fg='#ffffff',
                                     font=('Consolas', 9), height=12, wrap="word")
        positions_scrollbar = tk.Scrollbar(positions_frame, orient="vertical", 
                                         command=self.positions_text.yview)
        self.positions_text.configure(yscrollcommand=positions_scrollbar.set)
        
        self.positions_text.pack(side="left", fill="both", expand=True)
        positions_scrollbar.pack(side="right", fill="y")
        
        # Position editing buttons
        edit_frame = tk.Frame(content_frame, bg='#2d2d2d')
        edit_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(edit_frame, text="✏️ Edit Position", bg='#2196F3', fg='white', 
                 command=self.edit_position, font=('Arial', 10)).pack(side="left", padx=(0, 5))
        tk.Button(edit_frame, text="🗑️ Remove Position", bg='#f44336', fg='white', 
                 command=self.remove_position, font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(edit_frame, text="⬆️ Move Up", bg='#FF9800', fg='white', 
                 command=self.move_position_up, font=('Arial', 10)).pack(side="left", padx=5)
        tk.Button(edit_frame, text="⬇️ Move Down", bg='#9C27B0', fg='white', 
                 command=self.move_position_down, font=('Arial', 10)).pack(side="left", padx=5)
    
    def setup_camera_settings_panel(self, parent):
        """Setup camera settings panel"""
        camera_frame = tk.LabelFrame(parent, text="Camera Settings", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        camera_frame.pack(fill="x", pady=(0, 10))
        
        settings_frame = tk.Frame(camera_frame, bg='#2d2d2d')
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # Camera index
        index_frame = tk.Frame(settings_frame, bg='#2d2d2d')
        index_frame.pack(fill="x", pady=5)
        tk.Label(index_frame, text="Camera Index:", bg='#2d2d2d', fg='#ffffff').pack(side="left")
        tk.Entry(index_frame, textvariable=self.camera_index, width=5, 
                bg='#3d3d3d', fg='#ffffff').pack(side="left", padx=10)
        
        # Arm simulation toggle
        tk.Checkbutton(settings_frame, text="Enable Arm Simulation", 
                      variable=self.arm_simulation_enabled,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d').pack(anchor="w", pady=5)
    
    def setup_detection_settings_panel(self, parent):
        """Setup detection settings panel"""
        detection_frame = tk.LabelFrame(parent, text="Detection Settings", 
                                      font=('Arial', 14, 'bold'),
                                      bg='#2d2d2d', fg='#ffffff')
        detection_frame.pack(fill="x", pady=(0, 10))
        
        settings_frame = tk.Frame(detection_frame, bg='#2d2d2d')
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # Target objects
        tk.Label(settings_frame, text="Target Objects:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        for obj_type, var in self.target_objects.items():
            tk.Checkbutton(settings_frame, text=obj_type.replace('_', ' ').title(), 
                          variable=var,
                          bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                          command=self.update_target_objects).pack(anchor="w", pady=2)
    
    def setup_system_settings_panel(self, parent):
        """Setup system settings panel"""
        system_frame = tk.LabelFrame(parent, text="System Settings", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        system_frame.pack(fill="x", pady=(0, 10))
        
        settings_frame = tk.Frame(system_frame, bg='#2d2d2d')
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # InMoov simulator
        tk.Checkbutton(settings_frame, text="Enable InMoov Simulator", 
                      variable=self.inmoov_sim_enabled,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d').pack(anchor="w", pady=5)
        
        tk.Checkbutton(settings_frame, text="Track Closest Target", 
                      variable=self.inmoov_track_target,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d').pack(anchor="w", pady=5)
        
        # Arm IK
        if IKPY_AVAILABLE:
            tk.Checkbutton(settings_frame, text="Enable Arm Inverse Kinematics", 
                          variable=self.arm_ik_enabled,
                          bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d').pack(anchor="w", pady=5)
    
    def setup_esp32_quick_control_panel(self, parent):
        """Setup ESP32 quick control panel for Robot Control tab"""
        esp32_frame = tk.LabelFrame(parent, text="🔌 ESP32 Quick Control", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        esp32_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Connection section
        conn_frame = tk.Frame(esp32_frame, bg='#2d2d2d')
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        # IP and Port inputs
        ip_frame = tk.Frame(conn_frame, bg='#2d2d2d')
        ip_frame.pack(fill="x", pady=2)
        tk.Label(ip_frame, text="IP:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10)).pack(side="left")
        self.quick_esp32_ip = tk.StringVar(value="192.168.1.100")
        tk.Entry(ip_frame, textvariable=self.quick_esp32_ip, width=15, 
                bg='#3d3d3d', fg='#ffffff', font=('Arial', 10)).pack(side="left", padx=5)
        
        port_frame = tk.Frame(conn_frame, bg='#2d2d2d')
        port_frame.pack(fill="x", pady=2)
        tk.Label(port_frame, text="Port:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10)).pack(side="left")
        self.quick_esp32_port = tk.IntVar(value=80)
        tk.Entry(port_frame, textvariable=self.quick_esp32_port, width=8, 
                bg='#3d3d3d', fg='#ffffff', font=('Arial', 10)).pack(side="left", padx=5)
        
        # Connection buttons
        conn_buttons = tk.Frame(conn_frame, bg='#2d2d2d')
        conn_buttons.pack(fill="x", pady=5)
        
        tk.Button(conn_buttons, text="Connect", bg='#4CAF50', fg='white', 
                 command=self.quick_esp32_connect, font=('Arial', 10, 'bold')).pack(side="left", padx=(0, 5))
        tk.Button(conn_buttons, text="Disconnect", bg='#f44336', fg='white', 
                 command=self.quick_esp32_disconnect, font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        
        # Status indicator
        self.quick_esp32_status = tk.Label(conn_frame, text="Disconnected", 
                                          bg='#2d2d2d', fg='#ff8888', 
                                          font=('Consolas', 9, 'bold'))
        self.quick_esp32_status.pack(anchor="w", pady=(5, 0))
        
        # Simulator sync checkbox
        sync_frame = tk.Frame(conn_frame, bg='#2d2d2d')
        sync_frame.pack(fill="x", pady=5)
        tk.Checkbutton(sync_frame, text="Sync Simulator to ESP32", 
                      variable=self.esp32_simulator_sync,
                      bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d',
                      font=('Arial', 9)).pack(side="left")
        
        # Quick control buttons
        control_frame = tk.Frame(esp32_frame, bg='#2d2d2d')
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # System controls
        system_buttons = tk.Frame(control_frame, bg='#2d2d2d')
        system_buttons.pack(fill="x", pady=2)
        tk.Label(system_buttons, text="System:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 9, 'bold')).pack(side="left")
        tk.Button(system_buttons, text="Rest", bg='#2196F3', fg='white', 
                 command=self.quick_esp32_rest, font=('Arial', 8)).pack(side="left", padx=2)
        tk.Button(system_buttons, text="Reset", bg='#f44336', fg='white', 
                 command=self.quick_esp32_reset, font=('Arial', 8)).pack(side="left", padx=2)
        
        # Arms controls
        arms_buttons = tk.Frame(control_frame, bg='#2d2d2d')
        arms_buttons.pack(fill="x", pady=2)
        tk.Label(arms_buttons, text="Arms:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 9, 'bold')).pack(side="left")
        tk.Button(arms_buttons, text="Rest", bg='#2196F3', fg='white', 
                 command=self.quick_esp32_arms_rest, font=('Arial', 8)).pack(side="left", padx=2)
        tk.Button(arms_buttons, text="Salute", bg='#4CAF50', fg='white', 
                 command=self.quick_esp32_arms_salute, font=('Arial', 8)).pack(side="left", padx=2)
        tk.Button(arms_buttons, text="Hug", bg='#9C27B0', fg='white', 
                 command=self.quick_esp32_arms_hug, font=('Arial', 8)).pack(side="left", padx=2)
        
        # Neck controls
        neck_buttons = tk.Frame(control_frame, bg='#2d2d2d')
        neck_buttons.pack(fill="x", pady=2)
        tk.Label(neck_buttons, text="Neck:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 9, 'bold')).pack(side="left")
        tk.Button(neck_buttons, text="Center", bg='#2196F3', fg='white', 
                 command=self.quick_esp32_neck_center, font=('Arial', 8)).pack(side="left", padx=2)
        tk.Button(neck_buttons, text="Yes", bg='#4CAF50', fg='white', 
                 command=self.quick_esp32_neck_yes, font=('Arial', 8)).pack(side="left", padx=2)
        tk.Button(neck_buttons, text="No", bg='#f44336', fg='white', 
                 command=self.quick_esp32_neck_no, font=('Arial', 8)).pack(side="left", padx=2)
        
        # Hands controls
        hands_buttons = tk.Frame(control_frame, bg='#2d2d2d')
        hands_buttons.pack(fill="x", pady=2)
        tk.Label(hands_buttons, text="Hands:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 9, 'bold')).pack(side="left")
        tk.Button(hands_buttons, text="Open", bg='#4CAF50', fg='white', 
                 command=lambda: self.quick_esp32_hand_gesture('ambas', 'abrir'), font=('Arial', 8)).pack(side="left", padx=2)
        tk.Button(hands_buttons, text="Close", bg='#f44336', fg='white', 
                 command=lambda: self.quick_esp32_hand_gesture('ambas', 'cerrar'), font=('Arial', 8)).pack(side="left", padx=2)
        tk.Button(hands_buttons, text="Peace", bg='#2196F3', fg='white', 
                 command=lambda: self.quick_esp32_hand_gesture('ambas', 'paz'), font=('Arial', 8)).pack(side="left", padx=2)
        
        # Manual sync button
        sync_button_frame = tk.Frame(control_frame, bg='#2d2d2d')
        sync_button_frame.pack(fill="x", pady=5)
        tk.Button(sync_button_frame, text="Send Simulator to ESP32", 
                 command=self.send_simulator_to_esp32,
                 bg='#FF9800', fg='white', 
                 font=('Arial', 9, 'bold')).pack(fill="x")
        
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
                 bg='#2d2d2d', fg='#ffffff', highlightthickness=0)
        tk.Scale(view_frame, from_=-60, to=60, orient='horizontal', resolution=1,
                 variable=self.inmoov_cam_pitch_deg, command=lambda _=None: self.update_inmoov_sim(),
                 bg='#2d2d2d', fg='#ffffff', highlightthickness=0).grid(row=1, column=1, sticky='ew')
        # Place yaw scale
        view_frame.grid_columnconfigure(1, weight=1)
        view_frame.grid_columnconfigure(3, weight=1)
        tk.Scale(view_frame, from_=-120, to=120, orient='horizontal', resolution=1,
                 variable=self.inmoov_cam_yaw_deg, command=lambda _=None: self.update_inmoov_sim(),
                 bg='#2d2d2d', fg='#ffffff', highlightthickness=0).grid(row=0, column=1, sticky='ew')
        tk.Label(view_frame, text="Pitch", bg='#2d2d2d', fg='#ffffff').grid(row=1, column=0, sticky='w')
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
        tk.Button(view_frame, text="Reset View", bg='#616161', fg='white',
                  command=self.reset_inmoov_view).grid(row=0, column=3, rowspan=6, padx=10)

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
        
        # Left side - Object list with improved scrollbar
        list_frame = tk.Frame(object_split_frame, bg='#2d2d2d')
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Add title for object list with counter
        title_frame = tk.Frame(list_frame, bg='#2d2d2d')
        title_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(title_frame, text="Detected Objects", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(side="left")
        
        # Object counter label
        self.object_counter_label = tk.Label(title_frame, text="(0 items)", 
                                            bg='#2d2d2d', fg='#00aaff', 
                                            font=('Arial', 10))
        self.object_counter_label.pack(side="right")
        
        # Listbox with scrollbar - improved configuration
        listbox_frame = tk.Frame(list_frame, bg='#2d2d2d')
        listbox_frame.pack(fill="both", expand=True)
        
        # Create vertical scrollbar first
        v_scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", 
                                  bg='#2d2d2d', troughcolor='#1e1e1e',
                                  activebackground='#4a4a4a')
        v_scrollbar.pack(side="right", fill="y")
        
        # Create horizontal scrollbar
        h_scrollbar = tk.Scrollbar(listbox_frame, orient="horizontal",
                                  bg='#2d2d2d', troughcolor='#1e1e1e',
                                  activebackground='#4a4a4a')
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Create listbox with proper scrollbar connections
        self.object_listbox = tk.Listbox(listbox_frame, 
                                        bg='#3d3d3d', fg='#ffffff',
                                        font=('Consolas', 9),  # Slightly smaller font
                                        selectmode='single',
                                        height=15,  # Fixed height to ensure scrollbar appears
                                        yscrollcommand=v_scrollbar.set,
                                        xscrollcommand=h_scrollbar.set)
        self.object_listbox.pack(side="left", fill="both", expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.object_listbox.yview)
        h_scrollbar.config(command=self.object_listbox.xview)
        
        # Add mouse wheel support for listbox
        def on_listbox_mousewheel(event):
            self.object_listbox.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.object_listbox.bind("<MouseWheel>", on_listbox_mousewheel)
        
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

        # Robot Arm Control section with Scrollbar
        if IKPY_AVAILABLE:
            arm_control_container = tk.Frame(target_frame, bg='#2d2d2d')
            arm_control_container.pack(fill="both", expand=True, pady=(10, 0))
            
            # Create canvas and scrollbar for arm controls
            arm_canvas = tk.Canvas(arm_control_container, bg='#2d2d2d', highlightthickness=0, height=200)  # Reduced from 300 to 200
            arm_scrollbar = tk.Scrollbar(arm_control_container, orient="vertical", command=arm_canvas.yview)
            arm_control_frame = tk.Frame(arm_canvas, bg='#2d2d2d')
            
            # Configure canvas
            arm_canvas.configure(yscrollcommand=arm_scrollbar.set)
            arm_canvas.pack(side="left", fill="both", expand=True)
            arm_scrollbar.pack(side="right", fill="y")
            
            # Create window in canvas
            arm_canvas.create_window((0, 0), window=arm_control_frame, anchor="nw")
            
            tk.Label(arm_control_frame, text="Robot Arm Control:", 
                    bg='#2d2d2d', fg='#ffffff', 
                    font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
            
            # Enable arm IK checkbox
            tk.Checkbutton(arm_control_frame, text="Enable Inverse Kinematics", 
                          variable=self.arm_ik_enabled,
                          bg='#2d2d2d', fg='#ffffff', 
                          selectcolor='#3d3d3d',
                          font=('Arial', 9)).pack(anchor="w", pady=2)
            
            # Target position controls
            pos_frame = tk.Frame(arm_control_frame, bg='#2d2d2d')
            pos_frame.pack(fill="x", pady=5)
            
            tk.Label(pos_frame, text="Target Position (X, Y, Z):", 
                    bg='#2d2d2d', fg='#ffffff', 
                    font=('Arial', 9)).pack(anchor="w")
            
            # X coordinate
            x_frame = tk.Frame(pos_frame, bg='#2d2d2d')
            x_frame.pack(fill="x", pady=2)
            tk.Label(x_frame, text="X:", bg='#2d2d2d', fg='#ffffff').pack(side="left")
            self.arm_x_var = tk.DoubleVar(value=0)
            tk.Entry(x_frame, textvariable=self.arm_x_var, width=8, 
                    bg='#3d3d3d', fg='#ffffff').pack(side="left", padx=5)
            
            # Y coordinate
            y_frame = tk.Frame(pos_frame, bg='#2d2d2d')
            y_frame.pack(fill="x", pady=2)
            tk.Label(y_frame, text="Y:", bg='#2d2d2d', fg='#ffffff').pack(side="left")
            self.arm_y_var = tk.DoubleVar(value=450)
            tk.Entry(y_frame, textvariable=self.arm_y_var, width=8, 
                    bg='#3d3d3d', fg='#ffffff').pack(side="left", padx=5)
            
            # Z coordinate
            z_frame = tk.Frame(pos_frame, bg='#2d2d2d')
            z_frame.pack(fill="x", pady=2)
            tk.Label(z_frame, text="Z:", bg='#2d2d2d', fg='#ffffff').pack(side="left")
            self.arm_z_var = tk.DoubleVar(value=-290)
            tk.Entry(z_frame, textvariable=self.arm_z_var, width=8, 
                    bg='#3d3d3d', fg='#ffffff').pack(side="left", padx=5)
            
                                # Control buttons
            arm_buttons_frame = tk.Frame(arm_control_frame, bg='#2d2d2d')
            arm_buttons_frame.pack(fill="x", pady=5)
            
            tk.Button(arm_buttons_frame, text="Calculate IK", 
                     command=self.calculate_arm_ik,
                     bg='#2196F3', fg='white', 
                     font=('Arial', 9)).pack(side="left", padx=(0, 5))
            
            tk.Button(arm_buttons_frame, text="Move to Target", 
                     command=self.move_arm_to_target,
                     bg='#4CAF50', fg='white', 
                     font=('Arial', 9)).pack(side="left", padx=5)
            
            tk.Button(arm_buttons_frame, text="Show 3D Plot", 
                     command=self.show_arm_3d_plot,
                     bg='#FF9800', fg='white', 
                     font=('Arial', 9)).pack(side="left", padx=5)
            
            tk.Button(arm_buttons_frame, text="Export Data", 
                     command=self.export_arm_data,
                     bg='#9C27B0', fg='white', 
                     font=('Arial', 9)).pack(side="left", padx=5)
            
            # Additional arm control buttons
            arm_buttons_frame2 = tk.Frame(arm_control_frame, bg='#2d2d2d')
            arm_buttons_frame2.pack(fill="x", pady=2)
            
            tk.Button(arm_buttons_frame2, text="Reset Position", 
                     command=lambda: self.arm_x_var.set(0) or self.arm_y_var.set(450) or self.arm_z_var.set(-290),
                     bg='#607D8B', fg='white', 
                     font=('Arial', 8)).pack(side="left", padx=2)
            
            tk.Button(arm_buttons_frame2, text="Home Position", 
                     command=lambda: self.arm_x_var.set(0) or self.arm_y_var.set(0) or self.arm_z_var.set(0),
                     bg='#795548', fg='white', 
                     font=('Arial', 8)).pack(side="left", padx=2)
            
            tk.Button(arm_buttons_frame2, text="Test Position", 
                     command=lambda: self.arm_x_var.set(100) or self.arm_y_var.set(300) or self.arm_z_var.set(-200),
                     bg='#E91E63', fg='white', 
                     font=('Arial', 8)).pack(side="left", padx=2)
            
            tk.Button(arm_buttons_frame2, text="Clear Angles", 
                     command=lambda: [label.configure(text="0.0°") for label in self.arm_angles_labels],
                     bg='#FF5722', fg='white', 
                     font=('Arial', 8)).pack(side="left", padx=2)
            
            # Joint angles display
            angles_frame = tk.Frame(arm_control_frame, bg='#2d2d2d')
            angles_frame.pack(fill="x", pady=5)
            
            tk.Label(angles_frame, text="Joint Angles (degrees):", 
                    bg='#2d2d2d', fg='#ffffff', 
                    font=('Arial', 9, 'bold')).pack(anchor="w")
            
            self.arm_angles_labels = []
            for i, name in enumerate(self.arm_joint_names):
                angle_frame = tk.Frame(angles_frame, bg='#2d2d2d')
                angle_frame.pack(fill="x", pady=1)
                tk.Label(angle_frame, text=f"{name}:", 
                        bg='#2d2d2d', fg='#ffffff', 
                        font=('Arial', 8)).pack(side="left")
                angle_label = tk.Label(angle_frame, text="0.0°", 
                                     bg='#2d2d2d', fg='#00ff00', 
                                     font=('Consolas', 8))
                angle_label.pack(side="right")
                self.arm_angles_labels.append(angle_label)
            
            # Configure canvas scrolling
            def configure_arm_scroll(event):
                arm_canvas.configure(scrollregion=arm_canvas.bbox("all"))
            
            arm_control_frame.bind("<Configure>", configure_arm_scroll)
            
            # Bind mouse wheel to canvas
            def on_arm_mousewheel(event):
                arm_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            arm_canvas.bind("<MouseWheel>", on_arm_mousewheel)
        else:
            # Show warning if ikpy is not available
            arm_warning_frame = tk.Frame(target_frame, bg='#2d2d2d')
            arm_warning_frame.pack(fill="x", pady=(10, 0))
            
            tk.Label(arm_warning_frame, text="Robot Arm Control:", 
                    bg='#2d2d2d', fg='#ffffff', 
                    font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))
            
            tk.Label(arm_warning_frame, text="⚠️ ikpy not available", 
                    bg='#2d2d2d', fg='#ffaa00', 
                    font=('Arial', 9)).pack(anchor="w")
            
            tk.Label(arm_warning_frame, text="Install: pip install ikpy", 
                    bg='#2d2d2d', fg='#888888', 
                    font=('Arial', 8)).pack(anchor="w")

        # MRL (InMoov2) controls with Scrollbar
        mrl_container = tk.Frame(target_frame, bg='#2d2d2d')
        mrl_container.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create canvas and scrollbar for MRL controls
        mrl_canvas = tk.Canvas(mrl_container, bg='#2d2d2d', highlightthickness=0, height=100)  # Reduced from 150 to 100
        mrl_scrollbar = tk.Scrollbar(mrl_container, orient="vertical", command=mrl_canvas.yview)
        mrl_frame = tk.Frame(mrl_canvas, bg='#2d2d2d')
        
        # Configure canvas
        mrl_canvas.configure(yscrollcommand=mrl_scrollbar.set)
        mrl_canvas.pack(side="left", fill="both", expand=True)
        mrl_scrollbar.pack(side="right", fill="y")
        
        # Create window in canvas
        mrl_canvas.create_window((0, 0), window=mrl_frame, anchor="nw")
        
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
        
        # Additional MRL controls
        mrl_controls2 = tk.Frame(mrl_frame, bg='#2d2d2d'); mrl_controls2.pack(fill='x', pady=2)
        tk.Button(mrl_controls2, text="Test Connection", bg='#FF9800', fg='white', command=lambda: print("MRL Test")).pack(side='left', padx=2)
        tk.Button(mrl_controls2, text="Get Status", bg='#9C27B0', fg='white', command=lambda: print("MRL Status")).pack(side='left', padx=2)
        tk.Button(mrl_controls2, text="Reset Pose", bg='#607D8B', fg='white', command=lambda: print("MRL Reset")).pack(side='left', padx=2)
        tk.Button(mrl_controls2, text="Save Config", bg='#795548', fg='white', command=lambda: print("MRL Save")).pack(side='left', padx=2)
        self.mrl_status_label = tk.Label(mrl_frame, text="MRL: Disconnected", bg='#2d2d2d', fg='#ff8888', font=('Consolas', 9))
        self.mrl_status_label.pack(anchor='w', pady=(2, 0))
        
        # Configure canvas scrolling
        def configure_mrl_scroll(event):
            mrl_canvas.configure(scrollregion=mrl_canvas.bbox("all"))
        
        mrl_frame.bind("<Configure>", configure_mrl_scroll)
        
        # Bind mouse wheel to canvas
        def on_mrl_mousewheel(event):
            mrl_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        mrl_canvas.bind("<MouseWheel>", on_mrl_mousewheel)

        # ESP32 Robot Controller
        esp32_frame = tk.Frame(target_frame, bg='#2d2d2d')
        esp32_frame.pack(fill='x', pady=(10, 0))
        tk.Label(esp32_frame, text="ESP32 Robot Controller", bg='#2d2d2d', fg='#ffffff', font=('Arial', 10, 'bold')).pack(anchor='w')
        
        # ESP32 connection settings
        esp32_host_row = tk.Frame(esp32_frame, bg='#2d2d2d'); esp32_host_row.pack(fill='x', pady=2)
        tk.Label(esp32_host_row, text="Host:", bg='#2d2d2d', fg='#ffffff').pack(side='left')
        tk.Entry(esp32_host_row, textvariable=self.esp32_host, width=12, bg='#3d3d3d', fg='#ffffff').pack(side='left', padx=5)
        tk.Label(esp32_host_row, text="Port:", bg='#2d2d2d', fg='#ffffff').pack(side='left')
        tk.Entry(esp32_host_row, textvariable=self.esp32_port, width=6, bg='#3d3d3d', fg='#ffffff').pack(side='left', padx=5)
        
        # ESP32 connection controls
        esp32_controls_row = tk.Frame(esp32_frame, bg='#2d2d2d'); esp32_controls_row.pack(fill='x', pady=2)
        tk.Button(esp32_controls_row, text="Connect", bg='#4CAF50', fg='white', command=self.esp32_connect).pack(side='left')
        tk.Button(esp32_controls_row, text="Disconnect", bg='#f44336', fg='white', command=self.esp32_disconnect).pack(side='left', padx=5)
        tk.Checkbutton(esp32_controls_row, text="Enable Control", variable=self.esp32_enabled, bg='#2d2d2d', fg='#ffffff', selectcolor='#3d3d3d').pack(side='left', padx=10)
        
        # ESP32 status
        self.esp32_status_label = tk.Label(esp32_frame, text="ESP32: Disconnected", bg='#2d2d2d', fg='#ff8888', font=('Consolas', 9))
        self.esp32_status_label.pack(anchor='w', pady=(2, 0))
        
        # ESP32 Robot Control Panel with Scrollbar
        esp32_control_container = tk.Frame(esp32_frame, bg='#2d2d2d')
        esp32_control_container.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create canvas and scrollbar for ESP32 controls
        esp32_canvas = tk.Canvas(esp32_control_container, bg='#2d2d2d', highlightthickness=0, height=150)  # Reduced from 200 to 150
        esp32_scrollbar = tk.Scrollbar(esp32_control_container, orient="vertical", command=esp32_canvas.yview)
        esp32_control_frame = tk.Frame(esp32_canvas, bg='#2d2d2d')
        
        # Configure canvas
        esp32_canvas.configure(yscrollcommand=esp32_scrollbar.set)
        esp32_canvas.pack(side="left", fill="both", expand=True)
        esp32_scrollbar.pack(side="right", fill="y")
        
        # Create window in canvas
        esp32_canvas.create_window((0, 0), window=esp32_control_frame, anchor="nw")
        
        # System controls
        system_frame = tk.Frame(esp32_control_frame, bg='#2d2d2d')
        system_frame.pack(fill='x', pady=2)
        tk.Label(system_frame, text="System:", bg='#2d2d2d', fg='#ffffff', font=('Arial', 9, 'bold')).pack(anchor='w')
        system_buttons = tk.Frame(system_frame, bg='#2d2d2d'); system_buttons.pack(fill='x', pady=2)
        tk.Button(system_buttons, text="Rest Position", bg='#2196F3', fg='white', command=self.esp32_rest_position, font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(system_buttons, text="Reset", bg='#f44336', fg='white', command=self.esp32_reset, font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(system_buttons, text="Check", bg='#FF9800', fg='white', command=self.esp32_check, font=('Arial', 8)).pack(side='left', padx=2)
        
        # Arms controls
        arms_frame = tk.Frame(esp32_control_frame, bg='#2d2d2d')
        arms_frame.pack(fill='x', pady=2)
        tk.Label(arms_frame, text="Arms:", bg='#2d2d2d', fg='#ffffff', font=('Arial', 9, 'bold')).pack(anchor='w')
        arms_buttons = tk.Frame(arms_frame, bg='#2d2d2d'); arms_buttons.pack(fill='x', pady=2)
        tk.Button(arms_buttons, text="Rest", bg='#2196F3', fg='white', command=self.esp32_arms_rest, font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(arms_buttons, text="Salute", bg='#4CAF50', fg='white', command=self.esp32_arms_salute, font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(arms_buttons, text="Hug", bg='#9C27B0', fg='white', command=self.esp32_arms_hug, font=('Arial', 8)).pack(side='left', padx=2)
        
        # Neck controls
        neck_frame = tk.Frame(esp32_control_frame, bg='#2d2d2d')
        neck_frame.pack(fill='x', pady=2)
        tk.Label(neck_frame, text="Neck:", bg='#2d2d2d', fg='#ffffff', font=('Arial', 9, 'bold')).pack(anchor='w')
        neck_buttons = tk.Frame(neck_frame, bg='#2d2d2d'); neck_buttons.pack(fill='x', pady=2)
        tk.Button(neck_buttons, text="Center", bg='#2196F3', fg='white', command=self.esp32_neck_center, font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(neck_buttons, text="Yes", bg='#4CAF50', fg='white', command=self.esp32_neck_yes, font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(neck_buttons, text="No", bg='#f44336', fg='white', command=self.esp32_neck_no, font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(neck_buttons, text="Random", bg='#FF9800', fg='white', command=self.esp32_neck_random, font=('Arial', 8)).pack(side='left', padx=2)
        
        # Hands controls
        hands_frame = tk.Frame(esp32_control_frame, bg='#2d2d2d')
        hands_frame.pack(fill='x', pady=2)
        tk.Label(hands_frame, text="Hands:", bg='#2d2d2d', fg='#ffffff', font=('Arial', 9, 'bold')).pack(anchor='w')
        hands_buttons = tk.Frame(hands_frame, bg='#2d2d2d'); hands_buttons.pack(fill='x', pady=2)
        tk.Button(hands_buttons, text="Open", bg='#4CAF50', fg='white', command=lambda: self.esp32_hand_gesture('ambas', 'abrir'), font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(hands_buttons, text="Close", bg='#f44336', fg='white', command=lambda: self.esp32_hand_gesture('ambas', 'cerrar'), font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(hands_buttons, text="Peace", bg='#2196F3', fg='white', command=lambda: self.esp32_hand_gesture('ambas', 'paz'), font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(hands_buttons, text="Rock", bg='#9C27B0', fg='white', command=lambda: self.esp32_hand_gesture('ambas', 'rock'), font=('Arial', 8)).pack(side='left', padx=2)
        
        # Additional hand gestures
        hands_buttons2 = tk.Frame(hands_frame, bg='#2d2d2d'); hands_buttons2.pack(fill='x', pady=2)
        tk.Button(hands_buttons2, text="OK", bg='#FF9800', fg='white', command=lambda: self.esp32_hand_gesture('ambas', 'ok'), font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(hands_buttons2, text="Point", bg='#607D8B', fg='white', command=lambda: self.esp32_hand_gesture('ambas', 'senalar'), font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(hands_buttons2, text="Right", bg='#E91E63', fg='white', command=lambda: self.esp32_hand_gesture('derecha', 'abrir'), font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(hands_buttons2, text="Left", bg='#795548', fg='white', command=lambda: self.esp32_hand_gesture('izquierda', 'abrir'), font=('Arial', 8)).pack(side='left', padx=2)
        
        # Wrists controls
        wrists_frame = tk.Frame(esp32_control_frame, bg='#2d2d2d')
        wrists_frame.pack(fill='x', pady=2)
        tk.Label(wrists_frame, text="Wrists:", bg='#2d2d2d', fg='#ffffff', font=('Arial', 9, 'bold')).pack(anchor='w')
        wrists_buttons = tk.Frame(wrists_frame, bg='#2d2d2d'); wrists_buttons.pack(fill='x', pady=2)
        tk.Button(wrists_buttons, text="Center", bg='#2196F3', fg='white', command=self.esp32_wrists_center, font=('Arial', 8)).pack(side='left', padx=2)
        tk.Button(wrists_buttons, text="Random", bg='#FF9800', fg='white', command=self.esp32_wrists_random, font=('Arial', 8)).pack(side='left', padx=2)
        
        # Configure canvas scrolling
        def configure_esp32_scroll(event):
            esp32_canvas.configure(scrollregion=esp32_canvas.bbox("all"))
        
        esp32_control_frame.bind("<Configure>", configure_esp32_scroll)
        
        # Bind mouse wheel to canvas
        def on_mousewheel(event):
            esp32_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        esp32_canvas.bind("<MouseWheel>", on_mousewheel)
        
        # Target movement controls with Scrollbar
        target_movement_container = tk.Frame(target_frame, bg='#2d2d2d')
        target_movement_container.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create canvas and scrollbar for target movement controls
        target_canvas = tk.Canvas(target_movement_container, bg='#2d2d2d', highlightthickness=0, height=80)  # Reduced from 120 to 80
        target_scrollbar = tk.Scrollbar(target_movement_container, orient="vertical", command=target_canvas.yview)
        target_movement_frame = tk.Frame(target_canvas, bg='#2d2d2d')
        
        # Configure canvas
        target_canvas.configure(yscrollcommand=target_scrollbar.set)
        target_canvas.pack(side="left", fill="both", expand=True)
        target_scrollbar.pack(side="right", fill="y")
        
        # Create window in canvas
        target_canvas.create_window((0, 0), window=target_movement_frame, anchor="nw")
        
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
        
        # Additional target controls
        target_controls2 = tk.Frame(target_movement_frame, bg='#2d2d2d')
        target_controls2.pack(fill="x", pady=2)
        
        tk.Button(target_controls2, text="Track Target", 
                 command=lambda: print("Track Target"),
                 bg='#FF9800', fg='white', 
                 font=('Arial', 8)).pack(side="left", padx=2)
        
        tk.Button(target_controls2, text="Save Target", 
                 command=lambda: print("Save Target"),
                 bg='#9C27B0', fg='white', 
                 font=('Arial', 8)).pack(side="left", padx=2)
        
        tk.Button(target_controls2, text="Load Target", 
                 command=lambda: print("Load Target"),
                 bg='#607D8B', fg='white', 
                 font=('Arial', 8)).pack(side="left", padx=2)
        
        tk.Button(target_controls2, text="Auto Track", 
                 command=lambda: print("Auto Track"),
                 bg='#795548', fg='white', 
                 font=('Arial', 8)).pack(side="left", padx=2)
        
        # Configure canvas scrolling
        def configure_target_scroll(event):
            target_canvas.configure(scrollregion=target_canvas.bbox("all"))
        
        target_movement_frame.bind("<Configure>", configure_target_scroll)
        
        # Bind mouse wheel to canvas
        def on_target_mousewheel(event):
            target_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        target_canvas.bind("<MouseWheel>", on_target_mousewheel)
        
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
        
        # ESP32 Quick Control Panel
        self.setup_esp32_quick_control_panel(object_frame)
        
    def setup_statistics_panel(self, parent):
        """Setup the statistics panel"""
        stats_frame = tk.LabelFrame(parent, text="Robot Statistics", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        stats_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Statistics text area with improved scrolling
        text_frame = tk.Frame(stats_frame, bg='#2d2d2d')
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create text widget with scrollbar
        self.stats_text = tk.Text(text_frame, 
                                 bg='#3d3d3d', fg='#ffffff',
                                 font=('Consolas', 9),
                                 wrap="word", height=8,  # Reduced from 12 to 8 lines
                                 insertbackground='#ffffff',
                                 selectbackground='#4a4a4a',
                                 selectforeground='#ffffff')
        self.stats_text.pack(side="left", fill="both", expand=True)
        
        # Vertical scrollbar
        stats_scrollbar = tk.Scrollbar(text_frame, orient="vertical", 
                                      bg='#2d2d2d', troughcolor='#1e1e1e',
                                      activebackground='#4a4a4a')
        stats_scrollbar.pack(side="right", fill="y")
        
        # Horizontal scrollbar for long lines
        stats_h_scrollbar = tk.Scrollbar(text_frame, orient="horizontal",
                                        bg='#2d2d2d', troughcolor='#1e1e1e',
                                        activebackground='#4a4a4a')
        stats_h_scrollbar.pack(side="bottom", fill="x")
        
        # Configure scrollbars
        self.stats_text.config(yscrollcommand=stats_scrollbar.set,
                              xscrollcommand=stats_h_scrollbar.set)
        stats_scrollbar.config(command=self.stats_text.yview)
        stats_h_scrollbar.config(command=self.stats_text.xview)
        
        # Configure text tags for better formatting
        self.stats_text.tag_configure("title", foreground="#00ff00", font=('Consolas', 10, 'bold'))
        self.stats_text.tag_configure("success", foreground="#00ff00")
        self.stats_text.tag_configure("error", foreground="#ff4444")
        self.stats_text.tag_configure("warning", foreground="#ffaa00")
        self.stats_text.tag_configure("info", foreground="#00aaff")
        
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
            
            # Update video display
            self.update_video_display(processed_frame)
            
            # Update object list
            self.update_object_list()

            # Update InMoov simulator (draw on canvas)
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

                # Choose arm based on target x
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

            # If MRL sync enabled, send pose periodically (throttled by time)
            if self.mrl_enabled.get():
                now = time.time()
                if not hasattr(self, '_mrl_last_sent') or now - getattr(self, '_mrl_last_sent') > 0.2:
                    self._mrl_last_sent = now
                    self.mrl_send_pose(silent=True)
            
            # If ESP32 quick control is connected and sync is enabled, send simulator movements
            if self.quick_esp32 and self.quick_esp32.connected and self.esp32_simulator_sync.get():
                now = time.time()
                if not hasattr(self, '_esp32_last_sent') or now - getattr(self, '_esp32_last_sent') > 0.5:
                    self._esp32_last_sent = now
                    self.send_simulator_to_esp32(silent=True)
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
        """Reset camera view controls"""
        self.inmoov_cam_yaw_deg.set(0.0)
        self.inmoov_cam_pitch_deg.set(0.0)
        self.inmoov_cam_dist.set(400.0)
        self.inmoov_cam_x.set(0.0)
        self.inmoov_cam_y.set(0.0)
        self.inmoov_cam_z.set(0.0)
        self.update_inmoov_sim()

    def _map_camera_point_to_sim_3d(self, point):
        """Map a camera (x,y) point to a coarse 3D target in front of the torso"""
        cam_w, cam_h = 640.0, 480.0
        cx, cy = point
        # normalize around center (320,240)
        dx = (cx - cam_w/2.0) / (cam_w/2.0)
        dy = ((cam_h/2.0) - cy) / (cam_h/2.0)
        # scale to world units relative to shoulders
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

        # Convenience
        torso = self.inmoov_torso
        center = torso['center']
        w, h, d = torso['width'], torso['height'], torso['depth']

        # Torso box corners (8 points)
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
        # Edges to draw
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        pts2d = [self._project(p) for p in corners]
        for a,b in edges:
            self._line2d(c, pts2d[a], pts2d[b], '#444444', 2)

        # Neck and head
        neck = np.array([center[0], center[1]+hh-10.0, center[2]])
        head_center = neck + np.array([0.0, 30.0, 0.0])
        # Draw head as small circle after projecting a few points around
        head_p = self._project(head_center)
        c.create_oval(head_p[0]-10, head_p[1]-10, head_p[0]+10, head_p[1]+10, outline='#FFFFFF')

        # Nose direction from head yaw/pitch
        yaw, pitch = self.inmoov_head_angles['yaw'], self.inmoov_head_angles['pitch']
        nose_dir = self._dir_from_yaw_pitch(yaw, pitch)
        nose_tip = head_center + 30.0 * nose_dir
        self._line3d(c, head_center, nose_tip, '#FF9800', 2)

        # Shoulders
        ls, rs = self._get_shoulder_positions()
        # Left arm (upper + fore)
        l_sh, l_el, l_wr = self._arm_fk(ls, self.inmoov_left_arm['yaw'], self.inmoov_left_arm['pitch'], self.inmoov_left_arm['elbow'])
        self._line3d(c, l_sh, l_el, '#4CAF50', 6)
        self._line3d(c, l_el, l_wr, '#8BC34A', 6)
        # Right arm
        r_sh, r_el, r_wr = self._arm_fk(rs, self.inmoov_right_arm['yaw'], self.inmoov_right_arm['pitch'], self.inmoov_right_arm['elbow'])
        self._line3d(c, r_sh, r_el, '#4CAF50', 6)
        self._line3d(c, r_el, r_wr, '#8BC34A', 6)

        # Target indicator
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
        """Solve 3D IK: compute shoulder yaw, shoulder pitch, elbow flex for 2-link arm"""
        # Vector from shoulder to target
        v = target - shoulder_pos
        dx, dy, dz = float(v[0]), float(v[1]), float(v[2])
        # yaw around Y so that plane contains target
        yaw = math.atan2(dx, dz)
        # rotate vector into yaw frame (so x' = 0)
        cz = math.cos(-yaw)
        sz = math.sin(-yaw)
        # Rotate around Y: [x', y', z']
        xp = cz*dx + sz*dz
        yp = dy
        zp = -sz*dx + cz*dz
        # xp should be ~0; use yp, zp for planar IK where -Y is down
        r2 = yp*yp + zp*zp
        r = math.sqrt(max(1e-6, r2))
        # clamp reach
        r_clamped = max(1.0, min(r, L1 + L2 - 1.0))
        # elbow by law of cosines
        cos_elbow = (r_clamped*r_clamped - L1*L1 - L2*L2) / (2.0*L1*L2)
        cos_elbow = max(-1.0, min(1.0, cos_elbow))
        elbow = math.acos(cos_elbow)
        # shoulder pitch
        angle_to_p = math.atan2(zp, -yp)  # measured from -Y toward +Z
        beta = math.atan2(L2*math.sin(elbow), L1 + L2*math.cos(elbow))
        pitch = angle_to_p - beta
        return yaw, pitch, elbow

    def _arm_fk(self, shoulder_pos, yaw, pitch, elbow):
        """Forward kinematics for a 2-link arm given yaw/pitch/elbow"""
        L1, L2 = self.inmoov_upper_len, self.inmoov_fore_len
        # local directions in yaw frame
        uy = -math.cos(pitch)
        uz = math.sin(pitch)
        upper_local = np.array([0.0, uy, uz])
        fore_local = np.array([0.0, -math.cos(pitch+elbow), math.sin(pitch+elbow)])
        # rotate by yaw around Y
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
        # yaw around Y, then pitch around X (down is -Y)
        # Base forward along +Z
        forward = np.array([0.0, 0.0, 1.0])
        # Apply yaw
        Ry = np.array([[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]])
        v = Ry @ forward
        # Apply pitch around X
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
        # clamp to reasonable ranges
        self.inmoov_head_angles['yaw'] = max(-1.2, min(1.2, yaw))
        self.inmoov_head_angles['pitch'] = max(-0.9, min(0.9, pitch))

    def _project(self, p3):
        """Project 3D world point to canvas with camera yaw/pitch/zoom"""
        # Camera parameters
        yaw = math.radians(self.inmoov_cam_yaw_deg.get())
        pitch = math.radians(self.inmoov_cam_pitch_deg.get())
        cam_dist = float(self.inmoov_cam_dist.get())
        cam_pos = np.array([
            float(self.inmoov_cam_x.get()),
            float(self.inmoov_cam_y.get()),
            -cam_dist + float(self.inmoov_cam_z.get())
        ], dtype=float)

        # Build rotation matrices for inverse (world to camera)
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

        # Map our joint space to MRL degrees (approx mapping)
        # Head: pitch ~ neck (0 center), yaw ~ rothead
        head_pitch_rad = self.inmoov_head_angles['pitch']
        head_yaw_rad = self.inmoov_head_angles['yaw']
        neck_deg = max(0.0, min(180.0, 90.0 - head_pitch_rad * 180.0 / math.pi))
        rothead_deg = max(0.0, min(180.0, 90.0 + head_yaw_rad * 180.0 / math.pi))

        # Right arm
        r = self.inmoov_right_arm
        r_shoulder = max(0.0, min(180.0, 90.0 + r['pitch'] * 180.0 / math.pi))
        r_rotate = max(0.0, min(180.0, 90.0 + r['yaw'] * 180.0 / math.pi))
        r_bicep = 90.0
        r_elbow = max(0.0, min(180.0, 60.0 + r['elbow'] * 180.0 / math.pi))
        r_omoplate = 90.0

        # Left arm
        l = self.inmoov_left_arm
        l_shoulder = max(0.0, min(180.0, 90.0 + l['pitch'] * 180.0 / math.pi))
        l_rotate = max(0.0, min(180.0, 90.0 + l['yaw'] * 180.0 / math.pi))
        l_bicep = 90.0
        l_elbow = max(0.0, min(180.0, 60.0 + l['elbow'] * 180.0 / math.pi))
        l_omoplate = 90.0

        # Send
        ok1, msg1 = self.mrl.move_head(neck_deg, rothead_deg)
        ok2, msg2 = self.mrl.move_right_arm(r_shoulder, r_rotate, r_bicep, r_elbow, r_omoplate)
        ok3, msg3 = self.mrl.move_left_arm(l_shoulder, l_rotate, l_bicep, l_elbow, l_omoplate)

        if not all([ok1, ok2, ok3]):
            # Show script fallbacks if REST failed
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
        # Mouse wheel (Windows)
        self.inmoov_canvas.bind('<MouseWheel>', self._inmoov_on_mouse_wheel)
        # Middle mouse for pan
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
        sensitivity = 0.3  # deg per pixel
        new_yaw = self._inmoov_start_yaw + dx * sensitivity
        new_pitch = self._inmoov_start_pitch - dy * sensitivity
        # clamp
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
        factor = 0.8  # world units per pixel
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
            # If IK is enabled, calculate arm coordinates
            if self.arm_ik_enabled.get() and IKPY_AVAILABLE and self.arm_chain is not None:
                try:
                    # Map camera coordinates to arm coordinates
                    arm_coords = self.map_camera_to_arm_coordinates(closest_object['center'])
                    
                    # Update UI variables
                    self.arm_x_var.set(arm_coords[0])
                    self.arm_y_var.set(arm_coords[1])
                    self.arm_z_var.set(arm_coords[2])
                    
                    # Calculate IK automatically
                    self.calculate_arm_ik()
                    
                    # Update simulation
                    self.update_robot_arm_simulation()
                    
                except Exception as e:
                    print(f"Error in IK-based arm update: {e}")
            
            # Update traditional target system
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
        
        # If IK is enabled, also move the robot arm
        if self.arm_ik_enabled.get() and IKPY_AVAILABLE and self.arm_chain is not None:
            try:
                # Map target coordinates to arm coordinates
                arm_coords = self.map_camera_to_arm_coordinates(target['center'])
                
                # Update UI variables
                self.arm_x_var.set(arm_coords[0])
                self.arm_y_var.set(arm_coords[1])
                self.arm_z_var.set(arm_coords[2])
                
                # Calculate IK and move
                self.calculate_arm_ik()
                self.move_arm_to_target()
                
                print(f"Arm IK calculated for target {target['id']}")
                
            except Exception as e:
                print(f"Error in IK-based target movement: {e}")
        
        # Update robot target position (traditional method)
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
                cv2.putText(frame, obj['type'].upper(), 
                           (center[0] - 20, center[1] + 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
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
    
    def update_video_display(self, frame):
        """Update video display in GUI"""
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
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=pil_image)
            
            # Update label
            self.video_label.configure(image=photo, text="")
            self.video_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Error updating video display: {e}")
    
    def update_object_list(self):
        """Update the object detection list"""
        try:
            self.object_listbox.delete(0, tk.END)
            
            for obj in self.detected_objects:
                timestamp = datetime.datetime.fromtimestamp(obj['timestamp']).strftime('%H:%M:%S')
                distance = self.calculate_distance(obj['size'][0])
                
                # Create list item with object info
                list_item = f"[{timestamp}] {obj['type'].upper()} - Dist: {distance:.2f}m - Conf: {obj['confidence']:.2f}"
                
                # Add subtype info for argucos
                if obj['type'] == 'arguco' and 'subtype' in obj:
                    list_item += f" - {obj['subtype'].replace('_', ' ').title()}"
                
                # Add QR data info
                if obj['type'] == 'qr_code' and 'data' in obj:
                    qr_data = obj['data'][:15] + "..." if len(obj['data']) > 15 else obj['data']
                    list_item += f" - {qr_data}"
                
                # Add Aruco ID info
                if obj['type'] == 'aruco' and 'id' in obj:
                    list_item += f" - ID:{obj['id']}"
                
                self.object_listbox.insert(tk.END, list_item)
            
            # Update object counter
            if hasattr(self, 'object_counter_label'):
                count = len(self.detected_objects)
                if count == 1:
                    self.object_counter_label.configure(text=f"({count} item)")
                else:
                    self.object_counter_label.configure(text=f"({count} items)")
                
        except Exception as e:
            print(f"Error updating object list: {e}")
    
    def clear_object_list(self):
        """Clear the object detection list"""
        self.object_listbox.delete(0, tk.END)
        self.detected_objects.clear()
        self.object_history.clear()
        
        # Update object counter
        if hasattr(self, 'object_counter_label'):
            self.object_counter_label.configure(text="(0 items)")
    
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
            
            # Camera and detection status
            self.stats_text.insert(tk.END, f"• Objects detected: {len(self.detected_objects)}\n", "info")
            self.stats_text.insert(tk.END, f"• Enabled targets: {', '.join(self.enabled_targets)}\n", "info")
            self.stats_text.insert(tk.END, f"• Registered targets: {len(self.targets)}\n", "info")
            
            # Target detection status
            if self.target_detection_mode:
                self.stats_text.insert(tk.END, f"• Target detection: Active\n", "success")
            else:
                self.stats_text.insert(tk.END, f"• Target detection: Inactive\n", "warning")
            
            self.stats_text.insert(tk.END, f"• Arguco definitions: {len(self.arguco_definitions)}\n", "info")
            
            if self.arguco_definition_mode:
                self.stats_text.insert(tk.END, f"• Arguco definition mode: Active\n", "success")
            else:
                self.stats_text.insert(tk.END, f"• Arguco definition mode: Inactive\n", "warning")
            
            # Robot movement status
            if self.is_moving:
                self.stats_text.insert(tk.END, f"• Robot moving: Yes\n", "warning")
            else:
                self.stats_text.insert(tk.END, f"• Robot moving: No\n", "info")
            
            if self.arm_simulation_enabled.get():
                self.stats_text.insert(tk.END, f"• Arm simulation: Enabled\n", "success")
            else:
                self.stats_text.insert(tk.END, f"• Arm simulation: Disabled\n", "warning")
            
            # ESP32 connection status
            if ESP32Connector is not None:
                if self.esp32 and self.esp32.connected:
                    self.stats_text.insert(tk.END, f"• ESP32 (Settings): Connected\n", "success")
                    if self.esp32_enabled.get():
                        self.stats_text.insert(tk.END, f"• ESP32 Control: Enabled\n", "success")
                    else:
                        self.stats_text.insert(tk.END, f"• ESP32 Control: Disabled\n", "warning")
                    
                    status = self.esp32.get_connection_status()
                    if status['error_count'] > 0:
                        self.stats_text.insert(tk.END, f"• ESP32 Errors: {status['error_count']}\n", "error")
                    else:
                        self.stats_text.insert(tk.END, f"• ESP32 Errors: {status['error_count']}\n", "success")
                else:
                    self.stats_text.insert(tk.END, f"• ESP32 (Settings): Disconnected\n", "error")
                    self.stats_text.insert(tk.END, f"• ESP32 Control: Disabled\n", "warning")
                
                # Quick ESP32 status
                if self.quick_esp32 and self.quick_esp32.connected:
                    self.stats_text.insert(tk.END, f"• ESP32 (Quick): Connected\n", "success")
                    if self.esp32_simulator_sync.get():
                        self.stats_text.insert(tk.END, f"• ESP32 Simulator Sync: Active\n", "success")
                    else:
                        self.stats_text.insert(tk.END, f"• ESP32 Simulator Sync: Inactive\n", "warning")
                else:
                    self.stats_text.insert(tk.END, f"• ESP32 (Quick): Disconnected\n", "error")
            else:
                self.stats_text.insert(tk.END, f"• ESP32: Not available\n", "error")
            
            # Robot arm IK information
            if IKPY_AVAILABLE:
                if self.arm_ik_enabled.get():
                    self.stats_text.insert(tk.END, f"• Arm IK: Enabled\n", "success")
                    if self.arm_chain is not None:
                        self.stats_text.insert(tk.END, f"• Arm target: ({self.arm_target_position[0]:.1f}, {self.arm_target_position[1]:.1f}, {self.arm_target_position[2]:.1f})\n", "info")
                        if self.arm_current_angles:
                            self.stats_text.insert(tk.END, f"• Arm angles: {[f'{a:.1f}°' for a in self.arm_current_angles]}\n", "info")
                else:
                    self.stats_text.insert(tk.END, f"• Arm IK: Disabled\n", "warning")
            else:
                self.stats_text.insert(tk.END, f"• Arm IK: Not available (ikpy missing)\n", "error")
            
            # Performance
            self.stats_text.insert(tk.END, f"• FPS: {self.current_fps:.1f}\n", "info")
            
            self.stats_text.insert(tk.END, "\n=== FUTURE ACTIONS ===\n", "title")
            if self.detected_objects:
                closest = min(self.detected_objects, key=lambda x: self.calculate_distance(x['size'][0]))
                self.stats_text.insert(tk.END, f"• Target: {closest['type']} at {self.calculate_distance(closest['size'][0]):.2f}m\n", "info")
            else:
                self.stats_text.insert(tk.END, "• No targets detected\n", "warning")
            
            # Auto-scroll to bottom
            self.stats_text.see(tk.END)
            
            # Update Sequence Builder ESP32 status
            self.update_esp32_connection_status()
                
        except Exception as e:
            print(f"Error updating statistics: {e}")
            self.stats_text.insert(tk.END, f"Error updating statistics: {e}\n", "error")
    
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
    
    # ===== ARMS SIMULATOR METHODS =====
    
    def setup_3d_arms_plot(self, parent):
        """Setup 3D matplotlib plot for arms visualization"""
        try:
            # Create matplotlib figure with dark theme
            self.arms_fig = Figure(figsize=(10, 8), facecolor='#1e1e1e')
            self.arms_ax = self.arms_fig.add_subplot(111, projection='3d', facecolor='#1e1e1e')
            
            # Configure 3D plot appearance
            self.arms_ax.set_facecolor('#1e1e1e')
            self.arms_fig.patch.set_facecolor('#1e1e1e')
            
            # Set axis labels and colors
            self.arms_ax.set_xlabel('X (mm)', color='white')
            self.arms_ax.set_ylabel('Y (mm)', color='white')
            self.arms_ax.set_zlabel('Z (mm)', color='white')
            
            # Set axis colors
            self.arms_ax.xaxis.label.set_color('white')
            self.arms_ax.yaxis.label.set_color('white')
            self.arms_ax.zaxis.label.set_color('white')
            self.arms_ax.tick_params(axis='x', colors='white')
            self.arms_ax.tick_params(axis='y', colors='white')
            self.arms_ax.tick_params(axis='z', colors='white')
            
            # Set initial view and limits
            self.arms_ax.set_xlim([-300, 300])
            self.arms_ax.set_ylim([-300, 300])
            self.arms_ax.set_zlim([0, 400])
            
            # Set initial viewing angle
            self.arms_ax.view_init(elev=20, azim=45)
            
            # Create tkinter canvas widget
            self.arms_canvas_widget = FigureCanvasTkAgg(self.arms_fig, parent)
            self.arms_canvas_widget.draw()
            self.arms_canvas_widget.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
            # Initial plot
            self.update_3d_arms_display()
            
        except Exception as e:
            print(f"Error setting up 3D arms plot: {e}")
            # Fallback to 2D canvas
            self.arms_canvas = tk.Canvas(parent, bg='#1e1e1e', 
                                       width=self.arms_canvas_size[0], 
                                       height=self.arms_canvas_size[1])
            self.arms_canvas.pack(padx=10, pady=10)
            self.arms_3d_enabled = False
    
    def toggle_arms_tracking(self):
        """Toggle arms tracking on/off"""
        if self.arms_tracking_enabled.get():
            self.start_arms_tracking()
        else:
            self.stop_arms_tracking()
    
    def start_arms_tracking(self):
        """Start tracking robot arms movements"""
        if hasattr(self, '_arms_tracking_timer'):
            self.root.after_cancel(self._arms_tracking_timer)
        self.schedule_arms_update()
    
    def stop_arms_tracking(self):
        """Stop tracking robot arms movements"""
        if hasattr(self, '_arms_tracking_timer'):
            self.root.after_cancel(self._arms_tracking_timer)
            delattr(self, '_arms_tracking_timer')
    
    def schedule_arms_update(self):
        """Schedule the next arms update"""
        if self.arms_tracking_enabled.get():
            self.update_arms_from_esp32()
            self._arms_tracking_timer = self.root.after(self.arms_update_interval, self.schedule_arms_update)
    
    def update_arms_from_esp32(self):
        """Update arms state from ESP32 if connected"""
        try:
            if hasattr(self, 'esp32_connector') and self.esp32_connector and self.esp32_connector.is_connected:
                # Get current positions from ESP32
                response = self.esp32_connector.get('/posiciones')
                if response and response.status_code == 200:
                    data = response.json()
                    self.update_arms_state_from_data(data)
            else:
                # Simulate data for testing (remove this in production)
                self.simulate_arms_movement()
        except Exception as e:
            print(f"Error updating arms from ESP32: {e}")
    
    def update_arms_state_from_data(self, data):
        """Update arms state from ESP32 position data"""
        try:
            if 'brazos' in data:
                brazos_data = data['brazos']
                
                # Update left arm (indices 0, 1, 2)
                if len(brazos_data) >= 3:
                    self.robot_arms_state['left_arm']['brazo_izq'] = brazos_data[0]['posicion']
                    self.robot_arms_state['left_arm']['frente_izq'] = brazos_data[1]['posicion']
                    self.robot_arms_state['left_arm']['high_izq'] = brazos_data[2]['posicion']
                
                # Update right arm (indices 3, 4, 5, 6)
                if len(brazos_data) >= 7:
                    self.robot_arms_state['right_arm']['brazo_der'] = brazos_data[3]['posicion']
                    self.robot_arms_state['right_arm']['frente_der'] = brazos_data[4]['posicion']
                    self.robot_arms_state['right_arm']['high_der'] = brazos_data[5]['posicion']
                    self.robot_arms_state['right_arm']['pollo_der'] = brazos_data[6]['posicion']
                
                # Update timestamp
                self.robot_arms_state['timestamp'] = time.time()
                
                # Add to history
                self.arms_history.append(dict(self.robot_arms_state))
                
                # Update display
                self.update_arms_display()
                
        except Exception as e:
            print(f"Error updating arms state from data: {e}")
    
    def simulate_arms_movement(self):
        """Simulate arms movement for testing (remove in production)"""
        import random
        
        # Slightly modify current positions for testing
        for arm in ['left_arm', 'right_arm']:
            for servo in self.robot_arms_state[arm]:
                if servo != 'timestamp':
                    current = self.robot_arms_state[arm][servo]
                    # Add small random movement
                    delta = random.uniform(-2, 2)
                    new_value = max(0, min(180, current + delta))
                    self.robot_arms_state[arm][servo] = new_value
        
        self.robot_arms_state['timestamp'] = time.time()
        self.arms_history.append(dict(self.robot_arms_state))
        self.update_arms_display()
    
    def update_arms_display(self):
        """Update the arms display canvas"""
        if self.arms_3d_enabled and self.arms_ax is not None:
            self.update_3d_arms_display()
        elif self.arms_canvas:
            self.update_2d_arms_display()
        
        # Always update status labels
        self.update_arms_status_labels()
    
    def update_3d_arms_display(self):
        """Update the 3D arms visualization"""
        if not self.arms_ax:
            return
            
        try:
            # Clear previous plot
            self.arms_ax.clear()
            
            # Configure 3D plot appearance again (since clear removes styling)
            self.arms_ax.set_facecolor('#1e1e1e')
            self.arms_ax.set_xlabel('X (mm)', color='white')
            self.arms_ax.set_ylabel('Y (mm)', color='white')
            self.arms_ax.set_zlabel('Z (mm)', color='white')
            self.arms_ax.xaxis.label.set_color('white')
            self.arms_ax.yaxis.label.set_color('white')
            self.arms_ax.zaxis.label.set_color('white')
            self.arms_ax.tick_params(axis='x', colors='white')
            self.arms_ax.tick_params(axis='y', colors='white')
            self.arms_ax.tick_params(axis='z', colors='white')
            
            # Set limits
            self.arms_ax.set_xlim([-300, 300])
            self.arms_ax.set_ylim([-300, 300])
            self.arms_ax.set_zlim([0, 400])
            
            # Draw robot base/torso
            self.draw_3d_robot_base()
            
            # Draw left arm
            self.draw_3d_arm('left', self.robot_arms_state['left_arm'])
            
            # Draw right arm
            self.draw_3d_arm('right', self.robot_arms_state['right_arm'])
            
            # Draw trajectory if enabled
            if self.arms_show_trajectory.get():
                self.draw_3d_arms_trajectory()
            
            # Refresh canvas
            self.arms_canvas_widget.draw()
            
        except Exception as e:
            print(f"Error updating 3D arms display: {e}")
    
    def update_2d_arms_display(self):
        """Update the 2D arms display (fallback)"""
        try:
            # Clear canvas
            self.arms_canvas.delete("all")
            
            # Draw robot base
            self.draw_robot_base()
            
            # Draw left arm
            self.draw_arm('left', self.robot_arms_state['left_arm'])
            
            # Draw right arm  
            self.draw_arm('right', self.robot_arms_state['right_arm'])
            
            # Draw trajectory if enabled
            if self.arms_show_trajectory.get():
                self.draw_arms_trajectory()
            
        except Exception as e:
            print(f"Error updating 2D arms display: {e}")
    
    def draw_3d_robot_base(self):
        """Draw the 3D robot base/torso"""
        try:
            # Torso dimensions (in mm)
            torso_width = 150
            torso_depth = 100
            torso_height = 200
            
            # Torso center position
            torso_x = 0
            torso_y = 0
            torso_z = torso_height / 2
            
            # Create torso vertices (simplified box)
            x_offset = torso_width / 2
            y_offset = torso_depth / 2
            z_offset = torso_height / 2
            
            # Draw torso outline
            torso_x_coords = [torso_x - x_offset, torso_x + x_offset, torso_x + x_offset, torso_x - x_offset, torso_x - x_offset]
            torso_y_coords = [torso_y - y_offset, torso_y - y_offset, torso_y + y_offset, torso_y + y_offset, torso_y - y_offset]
            torso_z_coords = [torso_z - z_offset] * 5
            
            self.arms_ax.plot(torso_x_coords, torso_y_coords, torso_z_coords, 'w-', linewidth=3, alpha=0.8)
            
            # Draw top of torso
            torso_z_coords_top = [torso_z + z_offset] * 5
            self.arms_ax.plot(torso_x_coords, torso_y_coords, torso_z_coords_top, 'w-', linewidth=3, alpha=0.8)
            
            # Draw vertical edges
            for i in range(4):
                self.arms_ax.plot([torso_x_coords[i], torso_x_coords[i]], 
                                [torso_y_coords[i], torso_y_coords[i]], 
                                [torso_z - z_offset, torso_z + z_offset], 'w-', linewidth=2, alpha=0.6)
            
            # Draw shoulders
            shoulder_radius = 20
            shoulder_height = torso_z + z_offset - 30  # Near top of torso
            
            left_shoulder_x = torso_x - x_offset
            right_shoulder_x = torso_x + x_offset
            shoulder_y = torso_y
            
            # Draw shoulder spheres (simplified as circles)
            theta = np.linspace(0, 2*np.pi, 20)
            
            # Left shoulder
            left_shoulder_x_circle = left_shoulder_x + shoulder_radius * np.cos(theta)
            left_shoulder_y_circle = shoulder_y + shoulder_radius * np.sin(theta)
            left_shoulder_z_circle = [shoulder_height] * len(theta)
            self.arms_ax.plot(left_shoulder_x_circle, left_shoulder_y_circle, left_shoulder_z_circle, 
                            'g-', linewidth=2, alpha=0.8)
            
            # Right shoulder
            right_shoulder_x_circle = right_shoulder_x + shoulder_radius * np.cos(theta)
            right_shoulder_y_circle = shoulder_y + shoulder_radius * np.sin(theta)
            right_shoulder_z_circle = [shoulder_height] * len(theta)
            self.arms_ax.plot(right_shoulder_x_circle, right_shoulder_y_circle, right_shoulder_z_circle, 
                            'b-', linewidth=2, alpha=0.8)
            
        except Exception as e:
            print(f"Error drawing 3D robot base: {e}")
    
    def draw_3d_arm(self, side, arm_data):
        """Draw a 3D arm with corrected kinematics"""
        try:
            # Arm link lengths (in mm)
            upper_arm_length = 150  # Hombro a codo
            forearm_length = 120    # Codo a muñeca
            hand_length = 60        # Muñeca a punta
            
            # Shoulder position
            shoulder_height = 170  # Height from ground
            if side == 'left':
                shoulder_x = -75  # Left side
                color = 'green'
                # Left arm angles - convertir de grados a radianes
                brazo_angle = math.radians(arm_data['brazo_izq'])    # Shoulder rotation
                frente_angle = math.radians(arm_data['frente_izq'])  # Elbow bend
                high_angle = math.radians(arm_data['high_izq'])      # Wrist rotation
            else:
                shoulder_x = 75   # Right side
                color = 'blue'
                # Right arm angles - CORREGIDAS: invertir algunas para orientación correcta
                brazo_angle = math.radians(180 - arm_data['brazo_der'])   # Invertir para orientación correcta
                frente_angle = math.radians(-arm_data['frente_der'])      # Invertir flexión
                high_angle = math.radians(-arm_data['high_der'])          # Invertir rotación muñeca
            
            shoulder_y = 0
            shoulder_z = shoulder_height
            
            # Calculate 3D positions using forward kinematics
            # Upper arm: desde hombro hasta codo
            elbow_x = shoulder_x + upper_arm_length * math.cos(brazo_angle) * math.cos(0)  # Proyección en XY
            elbow_y = shoulder_y + upper_arm_length * math.sin(brazo_angle)
            elbow_z = shoulder_z - upper_arm_length * math.sin(0)  # Componente vertical
            
            # Forearm: desde codo hasta muñeca
            total_angle_xy = brazo_angle + frente_angle
            wrist_x = elbow_x + forearm_length * math.cos(total_angle_xy)
            wrist_y = elbow_y + forearm_length * math.sin(total_angle_xy)
            wrist_z = elbow_z - forearm_length * math.sin(frente_angle * 0.3)  # Pequeña componente vertical
            
            # Hand: desde muñeca hasta punta
            hand_total_angle = total_angle_xy + high_angle
            hand_x = wrist_x + hand_length * math.cos(hand_total_angle)
            hand_y = wrist_y + hand_length * math.sin(hand_total_angle)
            hand_z = wrist_z - hand_length * math.sin(high_angle * 0.2)  # Componente vertical menor
            
            # Draw arm segments
            # Upper arm (hombro a codo)
            self.arms_ax.plot([shoulder_x, elbow_x], [shoulder_y, elbow_y], [shoulder_z, elbow_z], 
                            color=color, linewidth=8, alpha=0.8, solid_capstyle='round')
            
            # Forearm (codo a muñeca)
            self.arms_ax.plot([elbow_x, wrist_x], [elbow_y, wrist_y], [elbow_z, wrist_z], 
                            color=color, linewidth=6, alpha=0.8, solid_capstyle='round')
            
            # Hand (muñeca a punta)
            self.arms_ax.plot([wrist_x, hand_x], [wrist_y, hand_y], [wrist_z, hand_z], 
                            color=color, linewidth=4, alpha=0.8, solid_capstyle='round')
            
            # Draw joints as spheres
            joint_size = 15
            
            # Shoulder joint
            self.arms_ax.scatter([shoulder_x], [shoulder_y], [shoulder_z], 
                               color='orange', s=joint_size**2, alpha=0.9)
            
            # Elbow joint
            self.arms_ax.scatter([elbow_x], [elbow_y], [elbow_z], 
                               color='orange', s=joint_size**2, alpha=0.9)
            
            # Wrist joint
            self.arms_ax.scatter([wrist_x], [wrist_y], [wrist_z], 
                               color='orange', s=joint_size**2, alpha=0.9)
            
            # End effector
            self.arms_ax.scatter([hand_x], [hand_y], [hand_z], 
                               color='red', s=joint_size**2, alpha=1.0)
            
            # Store end effector position for trajectory
            return (hand_x, hand_y, hand_z)
            
        except Exception as e:
            print(f"Error drawing 3D arm ({side}): {e}")
            return (0, 0, 0)
    
    def draw_3d_arms_trajectory(self):
        """Draw 3D trajectory history"""
        if len(self.arms_history) < 2:
            return
            
        try:
            # Extract trajectory points
            left_trajectory = []
            right_trajectory = []
            
            for state in self.arms_history:
                # Calculate end effector positions for this state
                left_pos = self.calculate_3d_end_effector_position('left', state['left_arm'])
                right_pos = self.calculate_3d_end_effector_position('right', state['right_arm'])
                
                left_trajectory.append(left_pos)
                right_trajectory.append(right_pos)
            
            # Draw trajectories
            if left_trajectory:
                left_x, left_y, left_z = zip(*left_trajectory)
                self.arms_ax.plot(left_x, left_y, left_z, 'g--', linewidth=2, alpha=0.6, label='Left Arm Trail')
            
            if right_trajectory:
                right_x, right_y, right_z = zip(*right_trajectory)
                self.arms_ax.plot(right_x, right_y, right_z, 'b--', linewidth=2, alpha=0.6, label='Right Arm Trail')
                
        except Exception as e:
            print(f"Error drawing 3D trajectory: {e}")
    
    def calculate_3d_end_effector_position(self, side, arm_data):
        """Calculate 3D end effector position"""
        try:
            # Same kinematics as draw_3d_arm but just return end position
            upper_arm_length = 150
            forearm_length = 120
            hand_length = 60
            
            shoulder_height = 170
            if side == 'left':
                shoulder_x = -75
                brazo_angle = math.radians(arm_data['brazo_izq'])
                frente_angle = math.radians(arm_data['frente_izq'])
                high_angle = math.radians(arm_data['high_izq'])
            else:
                shoulder_x = 75
                brazo_angle = math.radians(180 - arm_data['brazo_der'])
                frente_angle = math.radians(-arm_data['frente_der'])
                high_angle = math.radians(-arm_data['high_der'])
            
            shoulder_y = 0
            shoulder_z = shoulder_height
            
            # Calculate end effector position
            elbow_x = shoulder_x + upper_arm_length * math.cos(brazo_angle)
            elbow_y = shoulder_y + upper_arm_length * math.sin(brazo_angle)
            elbow_z = shoulder_z
            
            total_angle_xy = brazo_angle + frente_angle
            wrist_x = elbow_x + forearm_length * math.cos(total_angle_xy)
            wrist_y = elbow_y + forearm_length * math.sin(total_angle_xy)
            wrist_z = elbow_z - forearm_length * math.sin(frente_angle * 0.3)
            
            hand_total_angle = total_angle_xy + high_angle
            hand_x = wrist_x + hand_length * math.cos(hand_total_angle)
            hand_y = wrist_y + hand_length * math.sin(hand_total_angle)
            hand_z = wrist_z - hand_length * math.sin(high_angle * 0.2)
            
            return (hand_x, hand_y, hand_z)
            
        except Exception as e:
            print(f"Error calculating 3D end effector position: {e}")
            return (0, 0, 0)
    
    def draw_robot_base(self):
        """Draw the robot base/torso"""
        canvas_w = self.arms_canvas_size[0]
        canvas_h = self.arms_canvas_size[1]
        
        # Robot torso center
        center_x = canvas_w // 2
        center_y = canvas_h // 2
        
        # Draw torso
        torso_w = 120
        torso_h = 80
        self.arms_canvas.create_rectangle(
            center_x - torso_w//2, center_y - torso_h//2,
            center_x + torso_w//2, center_y + torso_h//2,
            fill='#4CAF50', outline='#ffffff', width=2
        )
        
        # Draw shoulders
        shoulder_radius = 15
        left_shoulder_x = center_x - torso_w//2
        right_shoulder_x = center_x + torso_w//2
        shoulder_y = center_y - torso_h//4
        
        self.arms_canvas.create_oval(
            left_shoulder_x - shoulder_radius, shoulder_y - shoulder_radius,
            left_shoulder_x + shoulder_radius, shoulder_y + shoulder_radius,
            fill='#2196F3', outline='#ffffff', width=2
        )
        
        self.arms_canvas.create_oval(
            right_shoulder_x - shoulder_radius, shoulder_y - shoulder_radius,
            right_shoulder_x + shoulder_radius, shoulder_y + shoulder_radius,
            fill='#2196F3', outline='#ffffff', width=2
        )
    
    def draw_arm(self, side, arm_data):
        """Draw an individual arm"""
        canvas_w = self.arms_canvas_size[0]
        canvas_h = self.arms_canvas_size[1]
        
        center_x = canvas_w // 2
        center_y = canvas_h // 2
        
        # Arm parameters
        upper_arm_length = 80
        forearm_length = 70
        hand_length = 30
        
        # Get shoulder position
        torso_w = 120
        shoulder_y = center_y - 20
        
        if side == 'left':
            shoulder_x = center_x - torso_w//2
            color = '#4CAF50'
            # Left arm angles
            brazo = math.radians(arm_data['brazo_izq'])
            frente = math.radians(arm_data['frente_izq'])
            high = math.radians(arm_data['high_izq'])
        else:
            shoulder_x = center_x + torso_w//2
            color = '#2196F3'
            # Right arm angles
            brazo = math.radians(arm_data['brazo_der'])
            frente = math.radians(arm_data['frente_der'])
            high = math.radians(arm_data['high_der'])
        
        # Calculate arm segments
        # Upper arm (shoulder to elbow)
        elbow_x = shoulder_x + upper_arm_length * math.cos(brazo)
        elbow_y = shoulder_y + upper_arm_length * math.sin(brazo)
        
        # Forearm (elbow to wrist)
        wrist_x = elbow_x + forearm_length * math.cos(brazo + frente)
        wrist_y = elbow_y + forearm_length * math.sin(brazo + frente)
        
        # Hand (wrist to end)
        hand_x = wrist_x + hand_length * math.cos(brazo + frente + high)
        hand_y = wrist_y + hand_length * math.sin(brazo + frente + high)
        
        # Draw upper arm
        self.arms_canvas.create_line(
            shoulder_x, shoulder_y, elbow_x, elbow_y,
            fill=color, width=8, capstyle=tk.ROUND
        )
        
        # Draw forearm
        self.arms_canvas.create_line(
            elbow_x, elbow_y, wrist_x, wrist_y,
            fill=color, width=6, capstyle=tk.ROUND
        )
        
        # Draw hand
        self.arms_canvas.create_line(
            wrist_x, wrist_y, hand_x, hand_y,
            fill=color, width=4, capstyle=tk.ROUND
        )
        
        # Draw joints
        joint_radius = 6
        self.arms_canvas.create_oval(
            elbow_x - joint_radius, elbow_y - joint_radius,
            elbow_x + joint_radius, elbow_y + joint_radius,
            fill='#FF9800', outline='#ffffff', width=2
        )
        
        self.arms_canvas.create_oval(
            wrist_x - joint_radius, wrist_y - joint_radius,
            wrist_x + joint_radius, wrist_y + joint_radius,
            fill='#FF9800', outline='#ffffff', width=2
        )
        
        # Draw end effector
        self.arms_canvas.create_oval(
            hand_x - 4, hand_y - 4,
            hand_x + 4, hand_y + 4,
            fill='#F44336', outline='#ffffff', width=2
        )
    
    def draw_arms_trajectory(self):
        """Draw the trajectory history of arm movements"""
        if len(self.arms_history) < 2:
            return
            
        # Draw trajectory for end effectors
        for i in range(1, len(self.arms_history)):
            prev_state = self.arms_history[i-1]
            curr_state = self.arms_history[i]
            
            # Calculate end effector positions for both states
            prev_left_end = self.calculate_end_effector_position('left', prev_state['left_arm'])
            curr_left_end = self.calculate_end_effector_position('left', curr_state['left_arm'])
            
            prev_right_end = self.calculate_end_effector_position('right', prev_state['right_arm'])
            curr_right_end = self.calculate_end_effector_position('right', curr_state['right_arm'])
            
            # Draw trajectory lines
            alpha = max(0.1, i / len(self.arms_history))  # Fade effect
            
            # Left arm trajectory
            self.arms_canvas.create_line(
                prev_left_end[0], prev_left_end[1],
                curr_left_end[0], curr_left_end[1],
                fill='#4CAF50', width=2, stipple='gray50'
            )
            
            # Right arm trajectory
            self.arms_canvas.create_line(
                prev_right_end[0], prev_right_end[1],
                curr_right_end[0], curr_right_end[1],
                fill='#2196F3', width=2, stipple='gray50'
            )
    
    def calculate_end_effector_position(self, side, arm_data):
        """Calculate end effector position for an arm"""
        canvas_w = self.arms_canvas_size[0]
        canvas_h = self.arms_canvas_size[1]
        
        center_x = canvas_w // 2
        center_y = canvas_h // 2
        
        # Arm parameters
        upper_arm_length = 80
        forearm_length = 70
        hand_length = 30
        
        # Get shoulder position
        torso_w = 120
        shoulder_y = center_y - 20
        
        if side == 'left':
            shoulder_x = center_x - torso_w//2
            brazo = math.radians(arm_data['brazo_izq'])
            frente = math.radians(arm_data['frente_izq'])
            high = math.radians(arm_data['high_izq'])
        else:
            shoulder_x = center_x + torso_w//2
            brazo = math.radians(arm_data['brazo_der'])
            frente = math.radians(arm_data['frente_der'])
            high = math.radians(arm_data['high_der'])
        
        # Calculate end effector position
        elbow_x = shoulder_x + upper_arm_length * math.cos(brazo)
        elbow_y = shoulder_y + upper_arm_length * math.sin(brazo)
        
        wrist_x = elbow_x + forearm_length * math.cos(brazo + frente)
        wrist_y = elbow_y + forearm_length * math.sin(brazo + frente)
        
        hand_x = wrist_x + hand_length * math.cos(brazo + frente + high)
        hand_y = wrist_y + hand_length * math.sin(brazo + frente + high)
        
        return (hand_x, hand_y)
    
    def update_arms_status_labels(self):
        """Update the status labels with current servo positions"""
        try:
            # Update left arm labels
            for servo in self.left_arm_labels:
                value = self.robot_arms_state['left_arm'][servo]
                self.left_arm_labels[servo].config(text=f"{servo}: {value:.1f}°")
            
            # Update right arm labels
            for servo in self.right_arm_labels:
                value = self.robot_arms_state['right_arm'][servo]
                self.right_arm_labels[servo].config(text=f"{servo}: {value:.1f}°")
                
        except Exception as e:
            print(f"Error updating arms status labels: {e}")
    
    def clear_arms_history(self):
        """Clear the arms movement history"""
        self.arms_history.clear()
        self.update_arms_display()
    
    def set_arms_rest_position(self):
        """Set arms to rest position"""
        self.robot_arms_state['left_arm'] = {
            'brazo_izq': 10,
            'frente_izq': 80,
            'high_izq': 80
        }
        self.robot_arms_state['right_arm'] = {
            'brazo_der': 40,
            'frente_der': 90,
            'high_der': 80,
            'pollo_der': 45
        }
        self.robot_arms_state['timestamp'] = time.time()
        
        # Send to robot if connected
        if hasattr(self, 'esp32_connector') and self.esp32_connector and self.esp32_connector.is_connected:
            try:
                self.esp32_connector.get('/system/descanso')
            except Exception as e:
                print(f"Error sending rest position to robot: {e}")
        
        self.update_arms_display()
    
    def center_arms_view(self):
        """Center the arms view (reset zoom/pan for 3D view)"""
        if self.arms_3d_enabled and self.arms_ax is not None:
            # Reset 3D view
            self.arms_ax.set_xlim([-300, 300])
            self.arms_ax.set_ylim([-300, 300])
            self.arms_ax.set_zlim([0, 400])
            self.arms_ax.view_init(elev=20, azim=45)
            
            if self.arms_canvas_widget:
                self.arms_canvas_widget.draw()
        else:
            # Refresh 2D display
            self.update_arms_display()
    
    # ===== ESP32 CONNECTION METHODS =====
    
    def esp32_connect(self):
        """Connect to ESP32 robot controller"""
        if ESP32Connector is None:
            messagebox.showerror("ESP32", "ESP32 connector not available. Make sure esp32_connector.py is present.")
            return
        
        try:
            config = ESP32Config(
                host=self.esp32_host.get().strip(),
                port=int(self.esp32_port.get())
            )
            self.esp32 = ESP32Connector(config)
            
            success, message = self.esp32.connect()
            if success:
                self.esp32.start_status_monitoring()
                if self.esp32_status_label:
                    self.esp32_status_label.configure(text=f"ESP32: Connected to {config.host}:{config.port}", fg='#88ff88')
                
                # Update status text
                if hasattr(self, 'esp32_status_text'):
                    self.esp32_status_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Connected to {config.host}:{config.port}\n", "success")
                    self.esp32_status_text.see(tk.END)
                
                # Save configuration
                if update_esp32_config is not None:
                    update_esp32_config('host', config.host)
                    update_esp32_config('port', config.port)
                    update_esp32_config('enable_control', self.esp32_enabled.get())
                
                # Update Sequence Builder status
                self.update_esp32_connection_status()
                
                messagebox.showinfo("ESP32", f"Connected successfully: {message}")
            else:
                if self.esp32_status_label:
                    self.esp32_status_label.configure(text=f"ESP32: {message}", fg='#ff8888')
                
                # Update status text
                if hasattr(self, 'esp32_status_text'):
                    self.esp32_status_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Connection failed: {message}\n", "error")
                    self.esp32_status_text.see(tk.END)
                
                messagebox.showerror("ESP32", f"Connection failed: {message}")
                
        except Exception as e:
            error_msg = f"Error connecting to ESP32: {e}"
            if self.esp32_status_label:
                self.esp32_status_label.configure(text=f"ESP32: {error_msg}", fg='#ff8888')
            
            # Update status text
            if hasattr(self, 'esp32_status_text'):
                self.esp32_status_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {error_msg}\n", "error")
                self.esp32_status_text.see(tk.END)
            
            messagebox.showerror("ESP32", error_msg)
    
    def esp32_disconnect(self):
        """Disconnect from ESP32 robot controller"""
        if self.esp32:
            self.esp32.disconnect()
            self.esp32 = None
            if self.esp32_status_label:
                self.esp32_status_label.configure(text="ESP32: Disconnected", fg='#ff8888')
            
            # Update status text
            if hasattr(self, 'esp32_status_text'):
                self.esp32_status_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Disconnected from ESP32\n", "warning")
                self.esp32_status_text.see(tk.END)
            
            messagebox.showinfo("ESP32", "Disconnected from ESP32")
    
    def esp32_rest_position(self):
        """Move robot to rest position"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.system_rest_position()
        if success:
            self.action_history.append("ESP32: Robot moved to rest position")
            messagebox.showinfo("ESP32", "Robot moved to rest position")
        else:
            messagebox.showerror("ESP32", f"Failed to move to rest position: {message}")
    
    def esp32_reset(self):
        """Reset robot"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.system_reset()
        if success:
            self.action_history.append("ESP32: Robot reset")
            messagebox.showinfo("ESP32", "Robot reset successfully")
        else:
            messagebox.showerror("ESP32", f"Failed to reset robot: {message}")
    
    def esp32_check(self):
        """Check ESP32 system status"""
        if not self.esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.esp32.system_check()
        if success:
            messagebox.showinfo("ESP32", f"System check: {message}")
        else:
            messagebox.showerror("ESP32", f"System check failed: {message}")
    
    def esp32_arms_rest(self):
        """Move arms to rest position"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.arms_rest_position()
        if success:
            self.action_history.append("ESP32: Arms moved to rest position")
        else:
            messagebox.showerror("ESP32", f"Failed to move arms: {message}")
    
    def esp32_arms_salute(self):
        """Perform salute gesture"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.arms_salute()
        if success:
            self.action_history.append("ESP32: Salute gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform salute: {message}")
    
    def esp32_arms_hug(self):
        """Perform hug gesture"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.arms_hug()
        if success:
            self.action_history.append("ESP32: Hug gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform hug: {message}")
    
    def esp32_neck_center(self):
        """Center neck position"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.neck_center()
        if success:
            self.action_history.append("ESP32: Neck centered")
        else:
            messagebox.showerror("ESP32", f"Failed to center neck: {message}")
    
    def esp32_neck_yes(self):
        """Perform 'yes' gesture with neck"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.neck_yes()
        if success:
            self.action_history.append("ESP32: Neck 'yes' gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform 'yes' gesture: {message}")
    
    def esp32_neck_no(self):
        """Perform 'no' gesture with neck"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.neck_no()
        if success:
            self.action_history.append("ESP32: Neck 'no' gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform 'no' gesture: {message}")
    
    def esp32_neck_random(self):
        """Move neck to random position"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.neck_random()
        if success:
            self.action_history.append("ESP32: Neck moved to random position")
        else:
            messagebox.showerror("ESP32", f"Failed to move neck randomly: {message}")
    
    def esp32_hand_gesture(self, hand: str, gesture: str):
        """Perform hand gesture"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.hand_gesture(hand, gesture)
        if success:
            self.action_history.append(f"ESP32: {hand} hand {gesture} gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform {gesture} gesture: {message}")
    
    def esp32_wrists_center(self):
        """Center both wrists"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.wrists_center()
        if success:
            self.action_history.append("ESP32: Wrists centered")
        else:
            messagebox.showerror("ESP32", f"Failed to center wrists: {message}")
    
    def esp32_wrists_random(self):
        """Move wrists to random positions"""
        if not self.esp32 or not self.esp32_enabled.get():
            messagebox.showwarning("ESP32", "ESP32 not connected or control not enabled")
            return
        
        success, message = self.esp32.wrists_random()
        if success:
            self.action_history.append("ESP32: Wrists moved to random positions")
        else:
            messagebox.showerror("ESP32", f"Failed to move wrists randomly: {message}")
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start Mobile API Server
        self.start_api_server()
        
        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Set minimum window size
        self.root.minsize(1200, 600)  # Reduced minimum height from 800 to 600
        
        self.root.mainloop()
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        # Only handle main window resize, not child widgets
        if event.widget == self.root:
            # Update canvas scroll regions if needed
            try:
                # This will be called when the window is resized
                # The canvas scroll regions are automatically updated by the bind events
                pass
            except Exception as e:
                print(f"Error handling window resize: {e}")
    
    def start_api_server(self):
        """Start the mobile API server"""
        try:
            if self.api_server is None:
                self.api_server = MobileAPIServer(self, host='0.0.0.0', port=self.api_port)
                self.api_server_thread = threading.Thread(target=self.api_server.serve_forever, daemon=True)
                self.api_server_thread.start()
                print(f"Mobile API Server started on 0.0.0.0:{self.api_port} (accessible from all network interfaces)")
                self.action_history.append(f"Mobile API Server started on port {self.api_port} (all interfaces)")
                
                # Update mobile app status
                self.mobile_server_running = True
                self.mobile_start_time = time.time()
                if hasattr(self, 'mobile_log_text'):
                    self.log_mobile_message(f"Servidor iniciado en puerto {self.api_port}")
        except Exception as e:
            print(f"Error starting API server: {e}")
            if hasattr(self, 'mobile_log_text'):
                self.log_mobile_message(f"Error iniciando servidor: {e}")
    
    def stop_api_server(self):
        """Stop the mobile API server"""
        try:
            if self.api_server:
                self.api_server.shutdown()
                self.api_server = None
                print("Mobile API Server stopped")
                self.action_history.append("Mobile API Server stopped")
                
                # Update mobile app status
                self.mobile_server_running = False
                self.mobile_start_time = None
                if hasattr(self, 'mobile_log_text'):
                    self.log_mobile_message("Servidor detenido")
        except Exception as e:
            print(f"Error stopping API server: {e}")
            if hasattr(self, 'mobile_log_text'):
                self.log_mobile_message(f"Error deteniendo servidor: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        # Stop API server
        self.stop_api_server()
        
        self.stop_camera()
        
        # Disconnect ESP32
        if self.esp32:
            self.esp32_disconnect()
        
        # Disconnect quick ESP32
        if self.quick_esp32:
            self.quick_esp32_disconnect()
        
        self.root.quit()
    
    # ===== QUICK ESP32 CONTROL METHODS =====
    
    def quick_esp32_connect(self):
        """Connect to ESP32 for quick control"""
        if ESP32Connector is None:
            messagebox.showerror("ESP32", "ESP32 connector not available. Make sure esp32_connector.py is present.")
            return
        
        try:
            config = ESP32Config(
                host=self.quick_esp32_ip.get().strip(),
                port=int(self.quick_esp32_port.get())
            )
            self.quick_esp32 = ESP32Connector(config)
            
            success, message = self.quick_esp32.connect()
            if success:
                self.quick_esp32.start_status_monitoring()
                self.quick_esp32_status.configure(text=f"Connected to {config.host}:{config.port}", fg='#88ff88')
                
                # Add to action history
                self.action_history.append(f"Quick ESP32: Connected to {config.host}:{config.port}")
                
                # Update Sequence Builder status
                self.update_esp32_connection_status()
                
                messagebox.showinfo("ESP32", f"Connected successfully: {message}")
            else:
                self.quick_esp32_status.configure(text=f"Connection failed: {message}", fg='#ff8888')
                messagebox.showerror("ESP32", f"Connection failed: {message}")
                
        except Exception as e:
            error_msg = f"Error connecting to ESP32: {e}"
            self.quick_esp32_status.configure(text=error_msg, fg='#ff8888')
            messagebox.showerror("ESP32", error_msg)
    
    def quick_esp32_disconnect(self):
        """Disconnect from ESP32 quick control"""
        if self.quick_esp32:
            self.quick_esp32.disconnect()
            self.quick_esp32 = None
            self.quick_esp32_status.configure(text="Disconnected", fg='#ff8888')
            self.action_history.append("Quick ESP32: Disconnected")
            
            # Update Sequence Builder status
            self.update_esp32_connection_status()
            
            messagebox.showinfo("ESP32", "Disconnected from ESP32")
    
    def quick_esp32_rest(self):
        """Move robot to rest position via quick ESP32"""
        if not self.quick_esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.quick_esp32.system_rest_position()
        if success:
            self.action_history.append("Quick ESP32: Robot moved to rest position")
            messagebox.showinfo("ESP32", "Robot moved to rest position")
        else:
            messagebox.showerror("ESP32", f"Failed to move to rest position: {message}")
    
    def quick_esp32_reset(self):
        """Reset robot via quick ESP32"""
        if not self.quick_esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.quick_esp32.system_reset()
        if success:
            self.action_history.append("Quick ESP32: Robot reset")
            messagebox.showinfo("ESP32", "Robot reset successfully")
        else:
            messagebox.showerror("ESP32", f"Failed to reset robot: {message}")
    
    def quick_esp32_arms_rest(self):
        """Move arms to rest position via quick ESP32"""
        if not self.quick_esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.quick_esp32.arms_rest_position()
        if success:
            self.action_history.append("Quick ESP32: Arms moved to rest position")
        else:
            messagebox.showerror("ESP32", f"Failed to move arms: {message}")
    
    def quick_esp32_arms_salute(self):
        """Perform salute gesture via quick ESP32"""
        if not self.quick_esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.quick_esp32.arms_salute()
        if success:
            self.action_history.append("Quick ESP32: Salute gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform salute: {message}")
    
    def quick_esp32_arms_hug(self):
        """Perform hug gesture via quick ESP32"""
        if not self.quick_esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.quick_esp32.arms_hug()
        if success:
            self.action_history.append("Quick ESP32: Hug gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform hug: {message}")
    
    def quick_esp32_neck_center(self):
        """Center neck position via quick ESP32"""
        if not self.quick_esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.quick_esp32.neck_center()
        if success:
            self.action_history.append("Quick ESP32: Neck centered")
        else:
            messagebox.showerror("ESP32", f"Failed to center neck: {message}")
    
    def quick_esp32_neck_yes(self):
        """Perform 'yes' gesture with neck via quick ESP32"""
        if not self.quick_esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.quick_esp32.neck_yes()
        if success:
            self.action_history.append("Quick ESP32: Neck 'yes' gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform 'yes' gesture: {message}")
    
    def quick_esp32_neck_no(self):
        """Perform 'no' gesture with neck via quick ESP32"""
        if not self.quick_esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.quick_esp32.neck_no()
        if success:
            self.action_history.append("Quick ESP32: Neck 'no' gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform 'no' gesture: {message}")
    
    def quick_esp32_hand_gesture(self, hand: str, gesture: str):
        """Perform hand gesture via quick ESP32"""
        if not self.quick_esp32:
            messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        success, message = self.quick_esp32.hand_gesture(hand, gesture)
        if success:
            self.action_history.append(f"Quick ESP32: {hand} hand {gesture} gesture performed")
        else:
            messagebox.showerror("ESP32", f"Failed to perform {gesture} gesture: {message}")
    
    def send_simulator_to_esp32(self, silent: bool = False):
        """Send simulator movements to ESP32"""
        if not self.quick_esp32 or not self.quick_esp32.connected:
            if not silent:
                messagebox.showwarning("ESP32", "ESP32 not connected")
            return
        
        try:
            # Get current simulator angles from InMoov simulator
            if hasattr(self, 'inmoov_head_angles') and hasattr(self, 'inmoov_left_arm') and hasattr(self, 'inmoov_right_arm'):
                # Use InMoov simulator angles
                head_yaw = self.inmoov_head_angles.get('yaw', 0.0)
                head_pitch = self.inmoov_head_angles.get('pitch', 0.0)
                left_arm_yaw = self.inmoov_left_arm.get('yaw', 0.0)
                left_arm_pitch = self.inmoov_left_arm.get('pitch', 0.5)
                right_arm_yaw = self.inmoov_right_arm.get('yaw', 0.0)
                right_arm_pitch = self.inmoov_right_arm.get('pitch', 0.5)
            else:
                # Fallback to default values
                head_yaw = getattr(self, 'head_yaw', 0.0)
                head_pitch = getattr(self, 'head_pitch', 0.0)
                left_arm_yaw = getattr(self, 'left_arm_yaw', 0.0)
                left_arm_pitch = getattr(self, 'left_arm_pitch', 0.5)
                right_arm_yaw = getattr(self, 'right_arm_yaw', 0.0)
                right_arm_pitch = getattr(self, 'right_arm_pitch', 0.5)
            
            # Convert simulator angles to ESP32 servo positions
            # Neck mapping (simulator radians to ESP32 degrees)
            neck_lateral = int(140 + (head_yaw * 20 / 1.2))  # Center at 140, range ±20
            neck_inferior = int(95 + (head_pitch * 35 / 0.9))  # Center at 95, range ±35
            
            # Clamp to safe ranges
            neck_lateral = max(120, min(160, neck_lateral))
            neck_inferior = max(60, min(130, neck_inferior))
            
            # Arms mapping (simulator radians to ESP32 degrees)
            left_brazo = int(20 + (left_arm_yaw * 10 / 0.4))  # Center at 20, range ±10
            left_frente = int(90 + (left_arm_pitch - 0.5) * 30 / 0.3)  # Center at 90, range ±30
            
            right_brazo = int(42 + (right_arm_yaw * 12 / 0.4))  # Center at 42, range ±12
            right_frente = int(90 + (right_arm_pitch - 0.5) * 20 / 0.3)  # Center at 90, range ±20
            
            # Clamp to safe ranges
            left_brazo = max(10, min(30, left_brazo))
            left_frente = max(60, min(120, left_frente))
            right_brazo = max(30, min(55, right_brazo))
            right_frente = max(70, min(110, right_frente))
            
            # Send neck command to ESP32 using HTTP POST
            neck_data = {
                'lateral': neck_lateral,
                'inferior': neck_inferior,
                'superior': 105
            }
            success_neck = self.quick_esp32.send_http_post('/cuello/mover', neck_data)
            
            # Send arms command to ESP32 using HTTP POST
            arms_data = {
                'bi': left_brazo,
                'fi': left_frente,
                'bd': right_brazo,
                'fd': right_frente
            }
            success_arms = self.quick_esp32.send_http_post('/brazos/mover', arms_data)
            
            if not silent:
                if success_neck and success_arms:
                    self.action_history.append(f"✅ Simulator sync: Neck({neck_lateral},{neck_inferior}) Arms({left_brazo},{left_frente},{right_brazo},{right_frente})")
                else:
                    error_msg = f"❌ Sync failed: Neck={success_neck}, Arms={success_arms}"
                    self.action_history.append(error_msg)
                    if not silent:
                        messagebox.showerror("ESP32 Sync", error_msg)
                        
        except Exception as e:
            if not silent:
                messagebox.showerror("ESP32 Sync", f"Error sending simulator to ESP32: {str(e)}")
            self.action_history.append(f"❌ ESP32 sync error: {str(e)}")
    
    # ===== SEQUENCE BUILDER METHODS =====
    
    def start_sequence_recording(self):
        """Start recording a new sequence"""
        # Check if any ESP32 connection is available
        esp32_connected = (self.esp32 and self.esp32.connected) or (self.quick_esp32 and self.quick_esp32.connected)
        
        if not esp32_connected:
            messagebox.showwarning("Sequence Builder", "ESP32 must be connected to record sequences")
            return
        
        self.sequence_recording = True
        self.recorded_positions = []
        self.current_sequence = []
        
        # Update UI
        self.record_button.configure(text="⏹️ Stop Recording", bg='#666666', state="disabled")
        self.stop_record_button.configure(text="⏹️ Stop Recording", bg='#f44336', state="normal")
        self.recording_status_label.configure(text="Status: Recording...", fg='#ff0000')
        
        # Start recording timer
        self.recording_timer = self.root.after(100, self.record_position_timer)
        
        self.action_history.append("Sequence Builder: Started recording")
    
    def stop_sequence_recording(self):
        """Stop recording sequence"""
        self.sequence_recording = False
        
        # Stop recording timer
        if hasattr(self, 'recording_timer'):
            self.root.after_cancel(self.recording_timer)
        
        # Update UI
        self.record_button.configure(text="🔴 Start Recording", bg='#f44336', state="normal")
        self.stop_record_button.configure(text="⏹️ Stop Recording", bg='#666666', state="disabled")
        self.recording_status_label.configure(text="Status: Recording stopped", fg='#ffaa00')
        
        # Update positions counter
        self.positions_counter_label.configure(text=f"Positions: {len(self.recorded_positions)}")
        
        # Update sequence details
        self.update_sequence_details()
        
        self.action_history.append(f"Sequence Builder: Stopped recording - {len(self.recorded_positions)} positions captured")
    
    def record_position_timer(self):
        """Timer function to record positions during recording"""
        if self.sequence_recording:
            self.capture_current_position(silent=True)
            self.recording_timer = self.root.after(500, self.record_position_timer)  # Record every 500ms
    
    def get_active_esp32_connection(self):
        """Get the active ESP32 connection (prefer quick_esp32, fallback to esp32)"""
        if self.quick_esp32 and self.quick_esp32.connected:
            return self.quick_esp32
        elif self.esp32 and self.esp32.connected:
            return self.esp32
        return None
    
    def capture_current_position(self, silent: bool = False):
        """Capture current robot position from ESP32"""
        esp32_conn = self.get_active_esp32_connection()
        if not esp32_conn:
            if not silent:
                messagebox.showwarning("Sequence Builder", "ESP32 not connected")
            return
        
        try:
            # Get current positions from ESP32
            success, positions = esp32_conn.get_positions()
            if success:
                position_data = {
                    'timestamp': time.time(),
                    'arms': positions.get('brazos', []),
                    'neck': positions.get('cuello', []),
                    'hands': positions.get('manos', []),
                    'wrists': positions.get('munecas', [])
                }
                
                # If hands/wrists data is not available from ESP32, try to get it separately
                if not position_data['hands']:
                    try:
                        # Try to get hands data from ESP32
                        success_hands, hands_data = esp32_conn._make_request('/manos/posiciones', method="GET")
                        if success_hands and hands_data:
                            position_data['hands'] = hands_data
                    except:
                        pass
                
                if not position_data['wrists']:
                    try:
                        # Try to get wrists data from ESP32
                        success_wrists, wrists_data = esp32_conn._make_request('/munecas/posiciones', method="GET")
                        if success_wrists and wrists_data:
                            position_data['wrists'] = wrists_data
                    except:
                        pass
                
                self.recorded_positions.append(position_data)
                self.current_sequence.append(position_data)
                
                if not silent:
                    self.positions_counter_label.configure(text=f"Positions: {len(self.recorded_positions)}")
                    self.update_sequence_details()
                    self.action_history.append(f"Sequence Builder: Captured position {len(self.recorded_positions)}")
            else:
                if not silent:
                    messagebox.showerror("Sequence Builder", f"Failed to get positions: {positions}")
                    
        except Exception as e:
            if not silent:
                messagebox.showerror("Sequence Builder", f"Error capturing position: {str(e)}")
    
    def capture_hand_gesture(self, gesture: str):
        """Capture a specific hand gesture and add to sequence"""
        esp32_conn = self.get_active_esp32_connection()
        if not esp32_conn:
            messagebox.showwarning("Sequence Builder", "ESP32 not connected")
            return
        
        try:
            # Send gesture command to ESP32
            gesture_data = {
                'mano': 'ambas',  # Apply to both hands
                'gesto': gesture
            }
            success = esp32_conn.send_http_post('/manos/gesto', gesture_data)
            
            if success:
                # Create position data with the gesture
                position_data = {
                    'timestamp': time.time(),
                    'arms': [],  # Keep current arm positions
                    'neck': [],  # Keep current neck positions
                    'hands': [
                        # Gesture-specific hand positions
                        {'mano': 'derecha', 'gesto': gesture},
                        {'mano': 'izquierda', 'gesto': gesture}
                    ],
                    'wrists': [
                        {'mano': 'derecha', 'angulo': 80},
                        {'mano': 'izquierda', 'angulo': 80}
                    ]
                }
                
                self.recorded_positions.append(position_data)
                self.current_sequence.append(position_data)
                
                self.positions_counter_label.configure(text=f"Positions: {len(self.recorded_positions)}")
                self.update_sequence_details()
                self.action_history.append(f"Sequence Builder: Captured {gesture} gesture")
                
                messagebox.showinfo("Sequence Builder", f"Captured {gesture} gesture successfully!")
            else:
                messagebox.showerror("Sequence Builder", f"Failed to send {gesture} gesture to ESP32")
                
        except Exception as e:
            messagebox.showerror("Sequence Builder", f"Error capturing gesture: {str(e)}")
    
    def capture_simulator_position(self):
        """Capture current simulator position and convert to ESP32 format"""
        esp32_conn = self.get_active_esp32_connection()
        if not esp32_conn:
            messagebox.showwarning("Sequence Builder", "ESP32 not connected")
            return
        
        try:
            # Get simulator angles
            head_yaw = getattr(self, 'inmoov_head_angles', {}).get('yaw', 0.0)
            head_pitch = getattr(self, 'inmoov_head_angles', {}).get('pitch', 0.0)
            left_arm_yaw = getattr(self, 'inmoov_left_arm', {}).get('yaw', 0.0)
            left_arm_pitch = getattr(self, 'inmoov_left_arm', {}).get('pitch', 0.5)
            right_arm_yaw = getattr(self, 'inmoov_right_arm', {}).get('yaw', 0.0)
            right_arm_pitch = getattr(self, 'inmoov_right_arm', {}).get('pitch', 0.5)
            
            # Convert to ESP32 servo positions (same logic as send_simulator_to_esp32)
            neck_lateral = int(140 + (head_yaw * 20 / 1.2))
            neck_inferior = int(95 + (head_pitch * 35 / 0.9))
            neck_lateral = max(120, min(160, neck_lateral))
            neck_inferior = max(60, min(130, neck_inferior))
            
            left_brazo = int(20 + (left_arm_yaw * 10 / 0.4))
            left_frente = int(90 + (left_arm_pitch - 0.5) * 30 / 0.3)
            left_brazo = max(10, min(30, left_brazo))
            left_frente = max(60, min(120, left_frente))
            
            right_brazo = int(42 + (right_arm_yaw * 12 / 0.4))
            right_frente = int(90 + (right_arm_pitch - 0.5) * 20 / 0.3)
            right_brazo = max(30, min(55, right_brazo))
            right_frente = max(70, min(110, right_frente))
            
            # Create position data
            position_data = {
                'timestamp': time.time(),
                'arms': [
                    {'nombre': 'Brazo Izq', 'posicion': left_brazo, 'min': 10, 'max': 30},
                    {'nombre': 'Frente Izq', 'posicion': left_frente, 'min': 60, 'max': 120},
                    {'nombre': 'Brazo Der', 'posicion': right_brazo, 'min': 30, 'max': 55},
                    {'nombre': 'Frente Der', 'posicion': right_frente, 'min': 70, 'max': 110}
                ],
                'neck': [
                    {'nombre': 'Lateral', 'posicion': neck_lateral, 'min': 120, 'max': 160},
                    {'nombre': 'Inferior', 'posicion': neck_inferior, 'min': 60, 'max': 130},
                    {'nombre': 'Superior', 'posicion': 105, 'min': 109, 'max': 110}
                ],
                'hands': [
                    # Default hand positions (open hands)
                    {'mano': 'derecha', 'dedo': 'pulgar', 'angulo': 90},
                    {'mano': 'derecha', 'dedo': 'indice', 'angulo': 90},
                    {'mano': 'derecha', 'dedo': 'medio', 'angulo': 90},
                    {'mano': 'derecha', 'dedo': 'anular', 'angulo': 90},
                    {'mano': 'derecha', 'dedo': 'menique', 'angulo': 90},
                    {'mano': 'izquierda', 'dedo': 'pulgar', 'angulo': 90},
                    {'mano': 'izquierda', 'dedo': 'indice', 'angulo': 90},
                    {'mano': 'izquierda', 'dedo': 'medio', 'angulo': 90},
                    {'mano': 'izquierda', 'dedo': 'anular', 'angulo': 90},
                    {'mano': 'izquierda', 'dedo': 'menique', 'angulo': 90}
                ],
                'wrists': [
                    {'mano': 'derecha', 'angulo': 80},
                    {'mano': 'izquierda', 'angulo': 80}
                ]
            }
            
            self.recorded_positions.append(position_data)
            self.current_sequence.append(position_data)
            
            self.positions_counter_label.configure(text=f"Positions: {len(self.recorded_positions)}")
            self.update_sequence_details()
            self.action_history.append(f"Sequence Builder: Captured simulator position {len(self.recorded_positions)}")
            
        except Exception as e:
            messagebox.showerror("Sequence Builder", f"Error capturing simulator position: {str(e)}")
    
    def play_sequence(self):
        """Play the current sequence"""
        if not self.current_sequence:
            messagebox.showwarning("Sequence Builder", "No sequence to play")
            return
        
        esp32_conn = self.get_active_esp32_connection()
        if not esp32_conn:
            messagebox.showwarning("Sequence Builder", "ESP32 not connected")
            return
        
        self.sequence_playing = True
        self.sequence_playback_index = 0
        
        # Update UI
        self.play_button.configure(state="disabled")
        self.pause_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        self.playback_status_label.configure(text="Status: Playing sequence...", fg='#00ff00')
        
        # Start playback
        self.play_next_position()
        
        self.action_history.append("Sequence Builder: Started playing sequence")
    
    def pause_sequence(self):
        """Pause sequence playback"""
        self.sequence_playing = False
        
        # Update UI
        self.play_button.configure(state="normal")
        self.pause_button.configure(state="disabled")
        self.playback_status_label.configure(text="Status: Paused", fg='#ffaa00')
        
        self.action_history.append("Sequence Builder: Paused sequence")
    
    def stop_sequence(self):
        """Stop sequence playback"""
        self.sequence_playing = False
        self.sequence_playback_index = 0
        
        # Update UI
        self.play_button.configure(state="normal")
        self.pause_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        self.playback_status_label.configure(text="Status: Stopped", fg='#ff0000')
        self.progress_bar.set(0)
        
        self.action_history.append("Sequence Builder: Stopped sequence")
    
    def play_next_position(self):
        """Play the next position in the sequence"""
        if not self.sequence_playing or self.sequence_playback_index >= len(self.current_sequence):
            if self.sequence_loop.get() and self.sequence_playing:
                # Loop sequence
                self.sequence_playback_index = 0
            else:
                # End sequence
                self.stop_sequence()
                return
        
        position_data = self.current_sequence[self.sequence_playback_index]
        
        try:
            esp32_conn = self.get_active_esp32_connection()
            if not esp32_conn:
                messagebox.showerror("Sequence Builder", "ESP32 connection lost")
                self.stop_sequence()
                return
            
            # Send position to ESP32
            if 'arms' in position_data and position_data['arms']:
                arms_data = {
                    'bi': position_data['arms'][0]['posicion'],
                    'fi': position_data['arms'][1]['posicion'],
                    'bd': position_data['arms'][2]['posicion'],
                    'fd': position_data['arms'][3]['posicion']
                }
                esp32_conn.send_http_post('/brazos/mover', arms_data)
            
            if 'neck' in position_data and position_data['neck']:
                neck_data = {
                    'lateral': position_data['neck'][0]['posicion'],
                    'inferior': position_data['neck'][1]['posicion'],
                    'superior': position_data['neck'][2]['posicion']
                }
                esp32_conn.send_http_post('/cuello/mover', neck_data)
            
            # Send hands positions
            if 'hands' in position_data and position_data['hands']:
                for hand_data in position_data['hands']:
                    if 'mano' in hand_data and 'dedo' in hand_data and 'angulo' in hand_data:
                        # Individual finger movement
                        hands_data = {
                            'mano': hand_data['mano'],
                            'dedo': hand_data['dedo'],
                            'angulo': hand_data['angulo']
                        }
                        esp32_conn.send_http_post('/manos/dedo', hands_data)
                    elif 'mano' in hand_data and 'gesto' in hand_data:
                        # Hand gesture
                        gesture_data = {
                            'mano': hand_data['mano'],
                            'gesto': hand_data['gesto']
                        }
                        esp32_conn.send_http_post('/manos/gesto', gesture_data)
            
            # Send wrists positions
            if 'wrists' in position_data and position_data['wrists']:
                for wrist_data in position_data['wrists']:
                    if 'mano' in wrist_data and 'angulo' in wrist_data:
                        wrists_data = {
                            'mano': wrist_data['mano'],
                            'angulo': wrist_data['angulo']
                        }
                        esp32_conn.send_http_post('/munecas/mover', wrists_data)
            
            # Update progress
            progress = int((self.sequence_playback_index + 1) / len(self.current_sequence) * 100)
            self.progress_bar.set(progress)
            
            self.sequence_playback_index += 1
            
            # Schedule next position
            delay = int(1000 / self.sequence_playback_speed.get())  # Convert to milliseconds
            self.root.after(delay, self.play_next_position)
            
        except Exception as e:
            messagebox.showerror("Sequence Builder", f"Error playing position: {str(e)}")
            self.stop_sequence()
    
    def save_sequence(self):
        """Save current sequence to file"""
        if not self.current_sequence:
            messagebox.showwarning("Sequence Builder", "No sequence to save")
            return
        
        try:
            sequence_data = {
                'name': self.sequence_name.get(),
                'timestamp': time.time(),
                'positions': self.current_sequence
            }
            
            filename = f"sequence_{self.sequence_name.get().replace(' ', '_')}_{int(time.time())}.json"
            filepath = os.path.join(os.getcwd(), 'sequences', filename)
            
            # Create sequences directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(sequence_data, f, indent=2)
            
            # Add to saved sequences
            self.saved_sequences[sequence_data['name']] = filepath
            self.update_sequence_list()
            
            messagebox.showinfo("Sequence Builder", f"Sequence saved as {filename}")
            self.action_history.append(f"Sequence Builder: Saved sequence '{self.sequence_name.get()}'")
            
        except Exception as e:
            messagebox.showerror("Sequence Builder", f"Error saving sequence: {str(e)}")
    
    def load_sequence(self):
        """Load sequence from file"""
        try:
            from tkinter import filedialog
            filepath = filedialog.askopenfilename(
                title="Load Sequence",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=os.path.join(os.getcwd(), 'sequences')
            )
            
            if filepath:
                with open(filepath, 'r') as f:
                    sequence_data = json.load(f)
                
                self.sequence_name.set(sequence_data['name'])
                self.current_sequence = sequence_data['positions']
                
                self.update_sequence_details()
                self.positions_counter_label.configure(text=f"Positions: {len(self.current_sequence)}")
                
                messagebox.showinfo("Sequence Builder", f"Loaded sequence '{sequence_data['name']}' with {len(self.current_sequence)} positions")
                self.action_history.append(f"Sequence Builder: Loaded sequence '{sequence_data['name']}'")
                
        except Exception as e:
            messagebox.showerror("Sequence Builder", f"Error loading sequence: {str(e)}")
    
    def delete_sequence(self):
        """Delete selected sequence"""
        selection = self.sequence_listbox.curselection()
        if not selection:
            messagebox.showwarning("Sequence Builder", "No sequence selected")
            return
        
        sequence_name = self.sequence_listbox.get(selection[0])
        
        if messagebox.askyesno("Sequence Builder", f"Delete sequence '{sequence_name}'?"):
            try:
                if sequence_name in self.saved_sequences:
                    filepath = self.saved_sequences[sequence_name]
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    del self.saved_sequences[sequence_name]
                
                self.update_sequence_list()
                messagebox.showinfo("Sequence Builder", f"Deleted sequence '{sequence_name}'")
                self.action_history.append(f"Sequence Builder: Deleted sequence '{sequence_name}'")
                
            except Exception as e:
                messagebox.showerror("Sequence Builder", f"Error deleting sequence: {str(e)}")
    
    def clear_current_sequence(self):
        """Clear current sequence"""
        if messagebox.askyesno("Sequence Builder", "Clear current sequence?"):
            self.current_sequence = []
            self.recorded_positions = []
            self.sequence_name.set("New Sequence")
            
            self.update_sequence_details()
            self.positions_counter_label.configure(text="Positions: 0")
            
            self.action_history.append("Sequence Builder: Cleared current sequence")
    
    def on_sequence_select(self, event):
        """Handle sequence listbox selection"""
        selection = self.sequence_listbox.curselection()
        if selection:
            sequence_name = self.sequence_listbox.get(selection[0])
            if sequence_name in self.saved_sequences:
                try:
                    with open(self.saved_sequences[sequence_name], 'r') as f:
                        sequence_data = json.load(f)
                    
                    self.sequence_name.set(sequence_data['name'])
                    self.current_sequence = sequence_data['positions']
                    
                    self.update_sequence_details()
                    self.positions_counter_label.configure(text=f"Positions: {len(self.current_sequence)}")
                    
                except Exception as e:
                    messagebox.showerror("Sequence Builder", f"Error loading sequence: {str(e)}")
    
    def update_sequence_details(self):
        """Update sequence details display"""
        if self.current_sequence:
            self.sequence_info_label.configure(text=f"Current Sequence: {self.sequence_name.get()} ({len(self.current_sequence)} positions)")
            
            # Update positions text
            self.positions_text.delete(1.0, tk.END)
            for i, position in enumerate(self.current_sequence):
                self.positions_text.insert(tk.END, f"Position {i+1}:\n")
                
                if 'arms' in position and position['arms']:
                    self.positions_text.insert(tk.END, "  Arms:\n")
                    for arm in position['arms']:
                        self.positions_text.insert(tk.END, f"    {arm['nombre']}: {arm['posicion']}°\n")
                
                if 'neck' in position and position['neck']:
                    self.positions_text.insert(tk.END, "  Neck:\n")
                    for neck in position['neck']:
                        self.positions_text.insert(tk.END, f"    {neck['nombre']}: {neck['posicion']}°\n")
                
                if 'hands' in position and position['hands']:
                    self.positions_text.insert(tk.END, "  Hands:\n")
                    for hand in position['hands']:
                        if 'mano' in hand and 'dedo' in hand and 'angulo' in hand:
                            self.positions_text.insert(tk.END, f"    {hand['mano']} {hand['dedo']}: {hand['angulo']}°\n")
                        elif 'mano' in hand and 'gesto' in hand:
                            self.positions_text.insert(tk.END, f"    {hand['mano']} gesture: {hand['gesto']}\n")
                
                if 'wrists' in position and position['wrists']:
                    self.positions_text.insert(tk.END, "  Wrists:\n")
                    for wrist in position['wrists']:
                        if 'mano' in wrist and 'angulo' in wrist:
                            self.positions_text.insert(tk.END, f"    {wrist['mano']}: {wrist['angulo']}°\n")
                
                self.positions_text.insert(tk.END, "\n")
        else:
            self.sequence_info_label.configure(text="Current Sequence: None")
            self.positions_text.delete(1.0, tk.END)
    
    def update_sequence_list(self):
        """Update sequence listbox"""
        self.sequence_listbox.delete(0, tk.END)
        for sequence_name in sorted(self.saved_sequences.keys()):
            self.sequence_listbox.insert(tk.END, sequence_name)
    
    def update_esp32_connection_status(self):
        """Update ESP32 connection status in Sequence Builder panel"""
        if hasattr(self, 'esp32_connection_status'):
            esp32_conn = self.get_active_esp32_connection()
            if esp32_conn:
                self.esp32_connection_status.config(text="ESP32: Connected", fg='#00ff00')
            else:
                self.esp32_connection_status.config(text="ESP32: Not Connected", fg='#ff0000')
    
    def edit_position(self):
        """Edit selected position"""
        # TODO: Implement position editing dialog
        messagebox.showinfo("Sequence Builder", "Position editing feature coming soon!")
    
    def remove_position(self):
        """Remove selected position from sequence"""
        # TODO: Implement position removal
        messagebox.showinfo("Sequence Builder", "Position removal feature coming soon!")
    
    def move_position_up(self):
        """Move selected position up in sequence"""
        # TODO: Implement position reordering
        messagebox.showinfo("Sequence Builder", "Position reordering feature coming soon!")
    
    def move_position_down(self):
        """Move selected position down in sequence"""
        # TODO: Implement position reordering
        messagebox.showinfo("Sequence Builder", "Position reordering feature coming soon!")
    
    def center_inmoov_pose(self):
        """Center/default pose for the simulator and send to ESP32 if connected"""
        try:
            self.inmoov_head_angles = {'yaw': 0.0, 'pitch': 0.0}
            self.inmoov_left_arm = {'yaw': -0.4, 'pitch': 0.2, 'elbow': 0.8}
            self.inmoov_right_arm = {'yaw': 0.4, 'pitch': 0.2, 'elbow': 0.8}
            self.draw_inmoov_sim(None)
            
            # If ESP32 is connected, send center pose
            if self.quick_esp32 and self.quick_esp32.connected:
                self.quick_esp32_neck_center()
                self.quick_esp32_arms_rest()
                
        except Exception as e:
            print(f"Center pose error: {e}")
    
    # =====================================
    # CLASS BUILDER METHODS
    # =====================================
    
    def add_method_dialog(self):
        """Open dialog to add a new method to the class"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Método")
        dialog.configure(bg='#2d2d2d')
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        
        # Method name
        tk.Label(dialog, text="Nombre del Método:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w", padx=10, pady=(10, 5))
        method_name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=method_name_var, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10), width=40).pack(fill="x", padx=10, pady=(0, 10))
        
        # Method parameters
        tk.Label(dialog, text="Parámetros (separados por coma):", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w", padx=10, pady=(10, 5))
        method_params_var = tk.StringVar()
        tk.Entry(dialog, textvariable=method_params_var, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10), width=40).pack(fill="x", padx=10, pady=(0, 10))
        
        # Method body
        tk.Label(dialog, text="Cuerpo del Método:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w", padx=10, pady=(10, 5))
        
        text_frame = tk.Frame(dialog, bg='#2d2d2d')
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        method_body_text = tk.Text(text_frame, bg='#1e1e1e', fg='#ffffff',
                                 font=('Courier New', 10), wrap="none",
                                 insertbackground='#ffffff')
        v_scrollbar = tk.Scrollbar(text_frame, orient="vertical")
        h_scrollbar = tk.Scrollbar(text_frame, orient="horizontal")
        
        method_body_text.config(yscrollcommand=v_scrollbar.set, 
                              xscrollcommand=h_scrollbar.set)
        v_scrollbar.config(command=method_body_text.yview)
        h_scrollbar.config(command=method_body_text.xview)
        
        method_body_text.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Default method body
        method_body_text.insert("1.0", "        pass")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#2d2d2d')
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def add_method():
            name = method_name_var.get().strip()
            params = method_params_var.get().strip()
            body = method_body_text.get("1.0", "end-1c")
            
            if not name:
                messagebox.showerror("Error", "El nombre del método es requerido")
                return
            
            # Create method object
            method = {
                'name': name,
                'params': params,
                'body': body
            }
            
            self.current_methods.append(method)
            self.update_methods_list()
            self.update_code_preview()
            dialog.destroy()
        
        tk.Button(button_frame, text="Agregar", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=add_method).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancelar", bg='#f44336', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=dialog.destroy).pack(side="left", padx=5)
    
    def edit_method_dialog(self):
        """Edit selected method"""
        selection = self.methods_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un método para editar")
            return
        
        method_index = selection[0]
        method = self.current_methods[method_index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Editar Método")
        dialog.configure(bg='#2d2d2d')
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        
        # Method name
        tk.Label(dialog, text="Nombre del Método:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w", padx=10, pady=(10, 5))
        method_name_var = tk.StringVar(value=method['name'])
        tk.Entry(dialog, textvariable=method_name_var, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10), width=40).pack(fill="x", padx=10, pady=(0, 10))
        
        # Method parameters
        tk.Label(dialog, text="Parámetros (separados por coma):", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w", padx=10, pady=(10, 5))
        method_params_var = tk.StringVar(value=method['params'])
        tk.Entry(dialog, textvariable=method_params_var, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10), width=40).pack(fill="x", padx=10, pady=(0, 10))
        
        # Method body
        tk.Label(dialog, text="Cuerpo del Método:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w", padx=10, pady=(10, 5))
        
        text_frame = tk.Frame(dialog, bg='#2d2d2d')
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        method_body_text = tk.Text(text_frame, bg='#1e1e1e', fg='#ffffff',
                                 font=('Courier New', 10), wrap="none",
                                 insertbackground='#ffffff')
        v_scrollbar = tk.Scrollbar(text_frame, orient="vertical")
        h_scrollbar = tk.Scrollbar(text_frame, orient="horizontal")
        
        method_body_text.config(yscrollcommand=v_scrollbar.set, 
                              xscrollcommand=h_scrollbar.set)
        v_scrollbar.config(command=method_body_text.yview)
        h_scrollbar.config(command=method_body_text.xview)
        
        method_body_text.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Load current method body
        method_body_text.insert("1.0", method['body'])
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#2d2d2d')
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def save_changes():
            name = method_name_var.get().strip()
            params = method_params_var.get().strip()
            body = method_body_text.get("1.0", "end-1c")
            
            if not name:
                messagebox.showerror("Error", "El nombre del método es requerido")
                return
            
            # Update method
            self.current_methods[method_index] = {
                'name': name,
                'params': params,
                'body': body
            }
            
            self.update_methods_list()
            self.update_code_preview()
            dialog.destroy()
        
        tk.Button(button_frame, text="Guardar", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=save_changes).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancelar", bg='#f44336', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=dialog.destroy).pack(side="left", padx=5)
    
    def remove_method(self):
        """Remove selected method"""
        selection = self.methods_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un método para eliminar")
            return
        
        method_index = selection[0]
        method_name = self.current_methods[method_index]['name']
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el método '{method_name}'?"):
            del self.current_methods[method_index]
            self.update_methods_list()
            self.update_code_preview()
    
    def update_methods_list(self):
        """Update the methods listbox"""
        self.methods_listbox.delete(0, tk.END)
        for method in self.current_methods:
            display_text = f"{method['name']}({method['params']})"
            self.methods_listbox.insert(tk.END, display_text)
    
    def get_class_template(self, template_type):
        """Get class template based on type"""
        templates = {
            "basic_class": {
                "imports": ["import time", "import os"],
                "methods": [
                    {
                        "name": "__init__",
                        "params": "self",
                        "body": "        \"\"\"Initialize the class\"\"\"\n        pass"
                    }
                ]
            },
            "camera_processor": {
                "imports": ["import cv2", "import numpy as np", "import time"],
                "methods": [
                    {
                        "name": "__init__",
                        "params": "self",
                        "body": "        \"\"\"Initialize camera processor\"\"\"\n        self.cap = None\n        self.frame_count = 0"
                    },
                    {
                        "name": "start_camera",
                        "params": "self",
                        "body": "        \"\"\"Start camera capture\"\"\"\n        try:\n            self.cap = cv2.VideoCapture(0)\n            if not self.cap.isOpened():\n                print(\"Error: Could not open camera\")\n                return False\n            return True\n        except Exception as e:\n            print(f\"Error starting camera: {e}\")\n            return False"
                    },
                    {
                        "name": "process_frame",
                        "params": "self, frame",
                        "body": "        \"\"\"Process camera frame\"\"\"\n        if frame is None:\n            return None\n        \n        self.frame_count += 1\n        # Add your frame processing here\n        return frame"
                    },
                    {
                        "name": "stop_camera",
                        "params": "self",
                        "body": "        \"\"\"Stop camera capture\"\"\"\n        if self.cap:\n            self.cap.release()\n        cv2.destroyAllWindows()"
                    }
                ]
            },
            "speech_handler": {
                "imports": ["import pyttsx3", "import speech_recognition as sr", "import time"],
                "methods": [
                    {
                        "name": "__init__",
                        "params": "self",
                        "body": "        \"\"\"Initialize speech handler\"\"\"\n        self.engine = None\n        self.recognizer = sr.Recognizer()\n        self.initialize_tts()"
                    },
                    {
                        "name": "initialize_tts",
                        "params": "self",
                        "body": "        \"\"\"Initialize text-to-speech engine\"\"\"\n        try:\n            self.engine = pyttsx3.init()\n            self.engine.setProperty('rate', 180)\n            return True\n        except Exception as e:\n            print(f\"Error initializing TTS: {e}\")\n            return False"
                    },
                    {
                        "name": "speak",
                        "params": "self, text",
                        "body": "        \"\"\"Speak the given text\"\"\"\n        if self.engine:\n            print(f\"Speaking: {text}\")\n            self.engine.say(text)\n            self.engine.runAndWait()"
                    },
                    {
                        "name": "listen",
                        "params": "self, timeout=5",
                        "body": "        \"\"\"Listen for speech input\"\"\"\n        try:\n            with sr.Microphone() as source:\n                print(\"Listening...\")\n                self.recognizer.adjust_for_ambient_noise(source)\n                audio = self.recognizer.listen(source, timeout=timeout)\n            \n            text = self.recognizer.recognize_google(audio, language=\"es-ES\")\n            print(f\"Recognized: {text}\")\n            return text.lower()\n        except Exception as e:\n            print(f\"Error in speech recognition: {e}\")\n            return \"\""
                    }
                ]
            },
            "face_recognition": {
                "imports": ["import cv2", "import face_recognition", "import numpy as np", "import os"],
                "methods": [
                    {
                        "name": "__init__",
                        "params": "self",
                        "body": "        \"\"\"Initialize face recognition system\"\"\"\n        self.known_faces = {}\n        self.known_encodings = []\n        self.known_names = []"
                    },
                    {
                        "name": "load_known_faces",
                        "params": "self, faces_directory",
                        "body": "        \"\"\"Load known faces from directory\"\"\"\n        for filename in os.listdir(faces_directory):\n            if filename.endswith('.jpg') or filename.endswith('.png'):\n                name = os.path.splitext(filename)[0]\n                image_path = os.path.join(faces_directory, filename)\n                \n                image = face_recognition.load_image_file(image_path)\n                encodings = face_recognition.face_encodings(image)\n                \n                if encodings:\n                    self.known_encodings.append(encodings[0])\n                    self.known_names.append(name)\n                    print(f\"Loaded face: {name}\")"
                    },
                    {
                        "name": "recognize_faces",
                        "params": "self, frame",
                        "body": "        \"\"\"Recognize faces in frame\"\"\"\n        face_locations = face_recognition.face_locations(frame)\n        face_encodings = face_recognition.face_encodings(frame, face_locations)\n        \n        face_names = []\n        for face_encoding in face_encodings:\n            matches = face_recognition.compare_faces(self.known_encodings, face_encoding)\n            name = \"Unknown\"\n            \n            if True in matches:\n                first_match_index = matches.index(True)\n                name = self.known_names[first_match_index]\n            \n            face_names.append(name)\n        \n        return face_locations, face_names"
                    }
                ]
            },
            "pdf_processor": {
                "imports": ["import fitz", "import os", "import time"],
                "methods": [
                    {
                        "name": "__init__",
                        "params": "self",
                        "body": "        \"\"\"Initialize PDF processor\"\"\"\n        self.current_doc = None\n        self.current_page = 0"
                    },
                    {
                        "name": "load_pdf",
                        "params": "self, pdf_path",
                        "body": "        \"\"\"Load PDF document\"\"\"\n        try:\n            self.current_doc = fitz.open(pdf_path)\n            self.current_page = 0\n            print(f\"PDF loaded: {len(self.current_doc)} pages\")\n            return True\n        except Exception as e:\n            print(f\"Error loading PDF: {e}\")\n            return False"
                    },
                    {
                        "name": "extract_text",
                        "params": "self, page_num=None",
                        "body": "        \"\"\"Extract text from PDF page\"\"\"\n        if not self.current_doc:\n            return \"\"\n        \n        if page_num is None:\n            page_num = self.current_page\n        \n        if 0 <= page_num < len(self.current_doc):\n            page = self.current_doc[page_num]\n            return page.get_text()\n        return \"\""
                    },
                    {
                        "name": "get_page_image",
                        "params": "self, page_num=None",
                        "body": "        \"\"\"Get page as image\"\"\"\n        if not self.current_doc:\n            return None\n        \n        if page_num is None:\n            page_num = self.current_page\n        \n        if 0 <= page_num < len(self.current_doc):\n            page = self.current_doc[page_num]\n            pix = page.get_pixmap()\n            img_data = pix.tobytes(\"ppm\")\n            return img_data\n        return None"
                    }
                ]
            }
        }
        
        return templates.get(template_type, templates["basic_class"])
    
    def generate_class_code(self):
        """Generate the complete class code"""
        class_name = self.class_name_var.get().strip()
        class_description = self.class_description_var.get().strip()
        template_type = self.class_template_var.get()
        
        if not class_name:
            messagebox.showerror("Error", "El nombre de la clase es requerido")
            return
        
        # Get template
        template = self.get_class_template(template_type)
        
        # Build imports
        imports = template.get("imports", [])
        imports_text = "\n".join(imports) + "\n\n" if imports else ""
        
        # Build class header
        class_header = f"class {class_name}:\n"
        if class_description:
            class_header += f"    \"\"\"{class_description}\"\"\"\n\n"
        
        # Build methods
        methods_text = ""
        
        # Add template methods if none exist
        if not self.current_methods and template_type != "custom":
            self.current_methods = template.get("methods", [])
            self.update_methods_list()
        
        for method in self.current_methods:
            method_signature = f"    def {method['name']}({method['params']}):\n"
            method_body = method['body']
            
            # Ensure proper indentation
            if not method_body.startswith("        "):
                method_body = "\n".join("        " + line if line.strip() else line 
                                      for line in method_body.split('\n'))
            
            methods_text += method_signature + method_body + "\n\n"
        
        # Combine all parts
        full_code = imports_text + class_header + methods_text
        
        # Update code preview
        self.code_preview.delete("1.0", tk.END)
        self.code_preview.insert("1.0", full_code)
    
    def update_code_preview(self):
        """Update the code preview"""
        self.generate_class_code()
    
    def save_class_file(self):
        """Save the generated class to a file"""
        class_name = self.class_name_var.get().strip()
        if not class_name:
            messagebox.showerror("Error", "El nombre de la clase es requerido")
            return
        
        # Get the code from preview
        code = self.code_preview.get("1.0", "end-1c")
        
        if not code.strip():
            messagebox.showerror("Error", "No hay código para guardar")
            return
        
        # Ask for file location
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialfile=f"{class_name.lower()}.py",
            title="Guardar Clase Python"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                messagebox.showinfo("Éxito", f"Clase guardada en: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando archivo: {e}")
    
    def load_template(self):
        """Load a predefined template"""
        template_type = self.class_template_var.get()
        
        if template_type == "custom":
            messagebox.showinfo("Información", "Plantilla personalizada seleccionada. Configure manualmente.")
            return
        
        # Load template
        template = self.get_class_template(template_type)
        
        # Clear current methods and load template methods
        self.current_methods = template.get("methods", []).copy()
        self.update_methods_list()
        self.update_code_preview()
        
        messagebox.showinfo("Éxito", f"Plantilla '{template_type}' cargada")
    
    def clear_class_builder(self):
        """Clear all class builder data"""
        if messagebox.askyesno("Confirmar", "¿Limpiar todo el constructor de clases?"):
            self.class_name_var.set("")
            self.class_description_var.set("")
            self.class_template_var.set("basic_class")
            self.current_methods = []
            self.update_methods_list()
            self.update_code_preview()
    
    # =====================================
    # MOBILE APP TAB METHODS
    # =====================================
    
    def update_mobile_port(self):
        """Update the mobile API server port"""
        try:
            new_port = self.mobile_port_var.get()
            if new_port != self.api_port:
                old_port = self.api_port
                self.api_port = new_port
                
                # Restart server with new port
                if self.api_server:
                    self.stop_api_server()
                    self.start_api_server()
                
                # Update URL display with real IP
                local_ip = get_local_ip()
                self.server_url_label.config(text=f"http://{local_ip}:{self.api_port}/api")
                
                # Log the change
                self.log_mobile_message(f"Puerto cambiado de {old_port} a {new_port}")
                
                messagebox.showinfo("Puerto Actualizado", 
                                  f"Puerto del servidor actualizado a {new_port}")
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando puerto: {e}")
    
    def start_mobile_server(self):
        """Start the mobile API server manually"""
        try:
            if not self.api_server:
                self.start_api_server()
                self.mobile_server_running = True
                self.mobile_start_time = time.time()
                self.update_mobile_status()
                self.log_mobile_message("Servidor iniciado manualmente")
            else:
                messagebox.showinfo("Servidor", "El servidor ya está ejecutándose")
        except Exception as e:
            self.log_mobile_message(f"Error iniciando servidor: {e}")
            messagebox.showerror("Error", f"Error iniciando servidor: {e}")
    
    def stop_mobile_server(self):
        """Stop the mobile API server manually"""
        try:
            if self.api_server:
                self.stop_api_server()
                self.mobile_server_running = False
                self.mobile_start_time = None
                self.update_mobile_status()
                self.log_mobile_message("Servidor detenido manualmente")
            else:
                messagebox.showinfo("Servidor", "El servidor ya está detenido")
        except Exception as e:
            self.log_mobile_message(f"Error deteniendo servidor: {e}")
            messagebox.showerror("Error", f"Error deteniendo servidor: {e}")
    
    def restart_mobile_server(self):
        """Restart the mobile API server"""
        try:
            self.log_mobile_message("Reiniciando servidor...")
            if self.api_server:
                self.stop_api_server()
            time.sleep(1)  # Brief pause
            self.start_api_server()
            self.mobile_server_running = True
            self.mobile_start_time = time.time()
            self.update_mobile_status()
            self.log_mobile_message("Servidor reiniciado exitosamente")
        except Exception as e:
            self.log_mobile_message(f"Error reiniciando servidor: {e}")
            messagebox.showerror("Error", f"Error reiniciando servidor: {e}")
    
    def update_mobile_status(self):
        """Update mobile server status indicators"""
        try:
            if hasattr(self, 'server_status_indicator') and hasattr(self, 'server_status_label'):
                if self.api_server and self.mobile_server_running:
                    self.server_status_indicator.config(text="●", fg='#4CAF50')
                    self.server_status_label.config(text="Ejecutándose", fg='#4CAF50')
                else:
                    self.server_status_indicator.config(text="●", fg='#f44336')
                    self.server_status_label.config(text="Detenido", fg='#f44336')
        except Exception as e:
            print(f"Error updating mobile status: {e}")
    
    def log_mobile_message(self, message):
        """Add a message to the mobile app log"""
        try:
            if hasattr(self, 'mobile_log_text'):
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] {message}\n"
                
                # Insert at the end
                self.mobile_log_text.insert(tk.END, log_entry)
                
                # Auto-scroll to bottom
                self.mobile_log_text.see(tk.END)
        except Exception as e:
            print(f"Error logging mobile message: {e}")
    
    def toggle_connection_logging(self):
        """Toggle logging of /api/connection calls"""
        try:
            self.log_connection_calls = not self.log_connection_calls
            
            if self.log_connection_calls:
                self.connection_log_button.config(
                    text="🔇 Pausar logs /connection",
                    bg='#FF5722'
                )
                self.log_mobile_message("✅ Logging de /api/connection ACTIVADO")
            else:
                self.connection_log_button.config(
                    text="🔊 Reanudar logs /connection",
                    bg='#4CAF50'
                )
                self.log_mobile_message("🔇 Logging de /api/connection PAUSADO")
                
        except Exception as e:
            print(f"Error toggling connection logging: {e}")
    
    def clear_connection_log(self):
        """Clear the connection log"""
        try:
            if hasattr(self, 'mobile_log_text'):
                self.mobile_log_text.delete(1.0, tk.END)
                self.log_mobile_message("🗑️ Log limpiado")
        except Exception as e:
            print(f"Error clearing connection log: {e}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.log_mobile_message(f"IP copiada al portapapeles: {text}")
            messagebox.showinfo("Copiado", f"IP copiada: {text}")
        except Exception as e:
            self.log_mobile_message(f"Error copiando IP: {e}")
            messagebox.showerror("Error", f"Error copiando IP: {e}")
    
    def refresh_network_info(self):
        """Refresh network information and update displays"""
        try:
            # Get updated IP
            local_ip = get_local_ip()
            
            # Update IP display
            if hasattr(self, 'ip_display_label'):
                self.ip_display_label.config(text=local_ip)
            
            # Update server URL
            if hasattr(self, 'server_url_label'):
                self.server_url_label.config(text=f"http://{local_ip}:{self.api_port}/api")
            
            # Log the refresh
            self.log_mobile_message(f"Información de red actualizada - IP: {local_ip}")
            
            messagebox.showinfo("Red Actualizada", f"IP actualizada: {local_ip}")
        except Exception as e:
            self.log_mobile_message(f"Error actualizando red: {e}")
            messagebox.showerror("Error", f"Error actualizando red: {e}")
    
    def log_mobile_message(self, message):
        """Add a message to the mobile app log"""
        try:
            if hasattr(self, 'mobile_log_text'):
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] {message}\n"
                
                # Insert at the end
                self.mobile_log_text.insert(tk.END, log_entry)
                
                # Auto-scroll to bottom
                self.mobile_log_text.see(tk.END)
                
                # Limit log size (keep last 1000 lines)
                lines = self.mobile_log_text.get("1.0", tk.END).split('\n')
                if len(lines) > 1000:
                    self.mobile_log_text.delete("1.0", f"{len(lines)-1000}.0")
        except Exception as e:
            print(f"Error logging mobile message: {e}")
    
    def update_endpoints_list(self):
        """Update the endpoints list display"""
        try:
            if hasattr(self, 'endpoints_listbox'):
                self.endpoints_listbox.delete(0, tk.END)
                
                endpoints = [
                    "GET  /api/status           - Robot status",
                    "GET  /api/position         - Robot position", 
                    "GET  /api/classes          - Available classes",
                    "GET  /api/connection       - Connection status",
                    "GET  /api/presets          - Movement presets",
                    "POST /api/robot/move       - Move robot parts",
                    "POST /api/robot/speak      - Robot speech",
                    "POST /api/class/start      - Start class",
                    "POST /api/class/stop       - Stop class",
                    "POST /api/preset/execute   - Execute preset",
                    "POST /api/robot/emergency  - Emergency stop"
                ]
                
                for endpoint in endpoints:
                    self.endpoints_listbox.insert(tk.END, endpoint)
        except Exception as e:
            print(f"Error updating endpoints list: {e}")
    
    def update_mobile_stats(self):
        """Update mobile API statistics"""
        try:
            if hasattr(self, 'stats_labels'):
                # Update uptime
                if self.mobile_start_time:
                    uptime_seconds = time.time() - self.mobile_start_time
                    uptime_minutes = int(uptime_seconds / 60)
                    self.api_stats['uptime'] = uptime_minutes
                
                # Update active connections (simulated)
                self.api_stats['active_connections'] = len(self.connected_devices)
                
                # Update labels
                for key, value in self.api_stats.items():
                    if key in self.stats_labels:
                        self.stats_labels[key].config(text=str(value))
            
            # Update devices list
            if hasattr(self, 'devices_listbox'):
                self.devices_listbox.delete(0, tk.END)
                if self.connected_devices:
                    for device in self.connected_devices:
                        self.devices_listbox.insert(tk.END, device)
                else:
                    self.devices_listbox.insert(tk.END, "No hay dispositivos conectados")
            
            # Update mobile status
            self.update_mobile_status()
            
            # Schedule next update
            if hasattr(self, 'root'):
                self.root.after(5000, self.update_mobile_stats)  # Update every 5 seconds
                
        except Exception as e:
            print(f"Error updating mobile stats: {e}")
    
    def increment_api_stat(self, stat_name):
        """Increment an API statistic counter"""
        try:
            if stat_name in self.api_stats:
                self.api_stats[stat_name] += 1
        except Exception as e:
            print(f"Error incrementing API stat: {e}")
    
    def add_connected_device(self, device_info):
        """Add a connected device to the list"""
        try:
            if device_info not in self.connected_devices:
                self.connected_devices.append(device_info)
                self.log_mobile_message(f"Dispositivo conectado: {device_info}")
        except Exception as e:
            print(f"Error adding connected device: {e}")
    
    def remove_connected_device(self, device_info):
        """Remove a connected device from the list"""
        try:
            if device_info in self.connected_devices:
                self.connected_devices.remove(device_info)
                self.log_mobile_message(f"Dispositivo desconectado: {device_info}")
        except Exception as e:
            print(f"Error removing connected device: {e}")
    
    # =====================================================
    #   ENHANCED CLASS BUILDER METHODS - PDF PROCESSING
    # =====================================================
    
    def select_pdf_file(self):
        """Select a PDF file for class generation"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="Seleccionar PDF para análisis",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialdir=os.path.dirname(os.path.abspath(__file__))
            )
            
            if file_path:
                self.pdf_path_var.set(file_path)
                self.pdf_status_label.config(text=f"PDF cargado: {os.path.basename(file_path)}", fg='#4CAF50')
                print(f"📄 PDF seleccionado: {file_path}")
            else:
                self.pdf_status_label.config(text="Selección cancelada", fg='#ff9800')
                
        except Exception as e:
            print(f"❌ Error selecting PDF: {e}")
            messagebox.showerror("Error", f"Error al seleccionar PDF: {e}")
            self.pdf_status_label.config(text="Error al seleccionar PDF", fg='#f44336')
    
    def analyze_pdf_content(self):
        """Analyze PDF content to extract structure and information"""
        try:
            pdf_path = self.pdf_path_var.get()
            if not pdf_path or not os.path.exists(pdf_path):
                messagebox.showwarning("Advertencia", "Por favor selecciona un PDF válido primero")
                return
            
            self.pdf_status_label.config(text="🔄 Analizando PDF...", fg='#ff9800')
            self.root.update()
            
            # Import PyMuPDF for PDF processing
            import fitz
            
            with fitz.open(pdf_path) as doc:
                total_pages = len(doc)
                text_content = ""
                
                # Extract text from all pages
                for page_num in range(total_pages):
                    page = doc[page_num]
                    text_content += page.get_text()
                
                self.pdf_content = text_content
                
                # Basic analysis
                self.pdf_analysis = {
                    'total_pages': total_pages,
                    'total_chars': len(text_content),
                    'total_words': len(text_content.split()),
                    'filename': os.path.basename(pdf_path),
                    'structure': self._analyze_pdf_structure(text_content)
                }
                
                analysis_summary = (f"Análisis completado: {total_pages} páginas, "
                                  f"{self.pdf_analysis['total_words']} palabras")
                self.pdf_status_label.config(text=analysis_summary, fg='#4CAF50')
                
                print(f"📊 PDF analizado: {self.pdf_analysis}")
                messagebox.showinfo("Análisis Completado", 
                                  f"PDF analizado exitosamente:\n\n"
                                  f"• Páginas: {total_pages}\n"
                                  f"• Palabras: {self.pdf_analysis['total_words']}\n"
                                  f"• Caracteres: {self.pdf_analysis['total_chars']}")
                
        except ImportError:
            messagebox.showerror("Error", "PyMuPDF no está instalado. Instala con: pip install PyMuPDF")
        except Exception as e:
            print(f"❌ Error analyzing PDF: {e}")
            messagebox.showerror("Error", f"Error al analizar PDF: {e}")
            self.pdf_status_label.config(text="Error en análisis", fg='#f44336')
    
    def _analyze_pdf_structure(self, text_content):
        """Analyze PDF structure to identify sections and content types"""
        try:
            lines = text_content.split('\n')
            structure = {
                'sections': [],
                'keywords': [],
                'content_type': 'unknown'
            }
            
            # Identify potential sections
            for i, line in enumerate(lines):
                line = line.strip()
                if len(line) > 0:
                    # Look for section headers (short lines, potentially in caps)
                    if (len(line) < 100 and 
                        (line.isupper() or 
                         any(word in line.lower() for word in ['introducción', 'metodología', 'resultados', 'conclusión', 'abstract', 'resumen', 'capítulo', 'chapter']))):
                        structure['sections'].append({'title': line, 'line': i})
            
            # Identify content type
            content_lower = text_content.lower()
            if any(word in content_lower for word in ['tesis', 'thesis', 'proyecto', 'investigación']):
                structure['content_type'] = 'thesis'
            elif any(word in content_lower for word in ['presentación', 'diapositiva', 'slide']):
                structure['content_type'] = 'presentation'
            elif any(word in content_lower for word in ['manual', 'guía', 'tutorial']):
                structure['content_type'] = 'manual'
            
            # Extract keywords
            common_words = ['y', 'de', 'la', 'el', 'en', 'a', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'que', 'esta', 'este', 'como', 'pero', 'sus', 'tan', 'sin', 'más', 'muy', 'ya', 'también', 'hasta', 'sobre', 'todo', 'así', 'cuando', 'donde', 'puede', 'ser', 'hace', 'han', 'vez', 'cada', 'antes', 'después', 'durante']
            words = text_content.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3 and word not in common_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            structure['keywords'] = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return structure
            
        except Exception as e:
            print(f"❌ Error analyzing PDF structure: {e}")
            return {'sections': [], 'keywords': [], 'content_type': 'unknown'}
    
    def generate_class_from_pdf(self):
        """Generate a complete class automatically from PDF content"""
        try:
            if not self.pdf_content or not self.pdf_analysis:
                messagebox.showwarning("Advertencia", "Por favor analiza el PDF primero")
                return
            
            self.pdf_status_label.config(text="🤖 Generando clase automática...", fg='#ff9800')
            self.root.update()
            
            # Generate class based on PDF content type and structure
            content_type = self.pdf_analysis['structure']['content_type']
            
            if content_type == 'thesis':
                generated_class = self._generate_thesis_defense_class()
            elif content_type == 'presentation':
                generated_class = self._generate_presentation_class()
            else:
                generated_class = self._generate_generic_presentation_class()
            
            # Update class builder with generated content
            self.class_name_var.set(generated_class['name'])
            self.class_description_var.set(generated_class['description'])
            self.class_template_var.set("auto_generated")
            
            # Clear and add generated methods
            self.current_methods = generated_class['methods']
            self.update_methods_list()
            
            # Generate and display code
            self.generate_class_code()
            
            self.pdf_status_label.config(text="✅ Clase generada automáticamente", fg='#4CAF50')
            messagebox.showinfo("Clase Generada", 
                              f"Clase '{generated_class['name']}' generada exitosamente!\n\n"
                              f"• Métodos generados: {len(generated_class['methods'])}\n"
                              f"• Tipo: {content_type.title()}\n"
                              f"• Listo para ejecutar")
            
        except Exception as e:
            print(f"❌ Error generating class from PDF: {e}")
            messagebox.showerror("Error", f"Error al generar clase: {e}")
            self.pdf_status_label.config(text="Error generando clase", fg='#f44336')
    
    def _generate_thesis_defense_class(self):
        """Generate a thesis defense class based on ADAI functionality"""
        filename = self.pdf_analysis['filename'].replace('.pdf', '')
        
        return {
            'name': f"ThesisDefense_{filename}",
            'description': f"Defensa automatizada de tesis basada en {filename}",
            'methods': [
                {
                    'name': '__init__',
                    'params': 'self',
                    'description': 'Initialize thesis defense system',
                    'code': '''        """Initialize thesis defense system"""
        import pyttsx3
        import speech_recognition as sr
        import cv2
        import fitz
        import openai
        import os
        import time
        import multiprocessing
        from multiprocessing import Process, Value
        
        self.engine = self._initialize_tts()
        self.pdf_path = r\"""" + self.pdf_path_var.get() + """\"
        self.pdf_content = \"""" + self.pdf_content[:500].replace('"', '\\"') + """...\"
        self.tribunal_members = []
        self.presentation_active = False
        
        print("🎓 Thesis Defense System Initialized")'''
                },
                {
                    'name': '_initialize_tts',
                    'params': 'self',
                    'description': 'Initialize text-to-speech engine',
                    'code': '''        """Initialize text-to-speech engine"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0')
            engine.setProperty('rate', 180)
            return engine
        except Exception as e:
            print(f"❌ Error initializing TTS: {e}")
            return None'''
                },
                {
                    'name': 'speak',
                    'params': 'self, text',
                    'description': 'Make the system speak',
                    'code': '''        """Make the system speak"""
        try:
            if self.engine:
                print(f"🎓 ADAI: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            print(f"❌ Error in speech: {e}")'''
                },
                {
                    'name': 'start_presentation',
                    'params': 'self',
                    'description': 'Start the thesis presentation',
                    'code': '''        """Start the thesis presentation"""
        try:
            self.presentation_active = True
            self.speak("Buenos días honorables miembros de la terna evaluadora.")
            self.speak("Procedo a presentar mi proyecto de tesis.")
            
            # Process PDF pages
            import fitz
            with fitz.open(self.pdf_path) as doc:
                for page_num in range(min(5, len(doc))):  # Present first 5 pages
                    if not self.presentation_active:
                        break
                    
                    page = doc[page_num]
                    page_text = page.get_text()
                    
                    if page_text.strip():
                        summary = page_text[:200] + "..." if len(page_text) > 200 else page_text
                        self.speak(f"Diapositiva {page_num + 1}. {summary}")
                    
                    time.sleep(2)  # Pause between slides
            
            self.speak("He concluido la presentación. Estoy disponible para preguntas.")
            
        except Exception as e:
            print(f"❌ Error in presentation: {e}")
            self.speak("Disculpe, experimento dificultades técnicas.")'''
                },
                {
                    'name': 'stop_presentation',
                    'params': 'self',
                    'description': 'Stop the presentation',
                    'code': '''        """Stop the presentation"""
        self.presentation_active = False
        self.speak("Deteniendo presentación. Muchas gracias.")
        print("🛑 Presentation stopped")'''
                },
                {
                    'name': 'answer_question',
                    'params': 'self, question',
                    'description': 'Answer a question about the thesis',
                    'code': '''        """Answer a question about the thesis"""
        try:
            # Simple keyword-based responses
            question_lower = question.lower()
            
            if any(word in question_lower for word in ['metodología', 'método', 'como']):
                response = "La metodología utilizada se basa en un enfoque sistemático que integra análisis teórico y validación práctica."
            elif any(word in question_lower for word in ['resultado', 'conclusión']):
                response = "Los resultados obtenidos demuestran la viabilidad del proyecto y cumplen con los objetivos planteados."
            elif any(word in question_lower for word in ['futuro', 'mejora']):
                response = "Las líneas futuras incluyen optimización del sistema y extensión a nuevos casos de uso."
            else:
                response = "Es una excelente pregunta. Basándome en el desarrollo del proyecto, puedo indicar que se siguieron las mejores prácticas de ingeniería."
            
            self.speak(response)
            return response
            
        except Exception as e:
            print(f"❌ Error answering question: {e}")
            self.speak("Disculpe, no pude procesar la pregunta.")
            return "Error procesando pregunta"'''
                },
                {
                    'name': 'run_defense',
                    'params': 'self',
                    'description': 'Run complete thesis defense',
                    'code': '''        """Run complete thesis defense"""
        try:
            print("🎓 Starting Thesis Defense")
            self.speak("Iniciando defensa de tesis automatizada.")
            
            # Start presentation
            self.start_presentation()
            
            # Q&A session simulation
            self.speak("Ahora procedo con la sesión de preguntas y respuestas.")
            
            # Simulate some common questions
            common_questions = [
                "¿Cuál fue la metodología utilizada?",
                "¿Cuáles son los principales resultados?",
                "¿Qué trabajos futuros propone?"
            ]
            
            for question in common_questions:
                if self.presentation_active:
                    self.speak(f"Pregunta simulada: {question}")
                    time.sleep(1)
                    self.answer_question(question)
                    time.sleep(2)
            
            self.speak("Con esto concluyo la defensa de mi tesis. Muchas gracias por su atención.")
            
        except Exception as e:
            print(f"❌ Error in thesis defense: {e}")'''
                }
            ]
        }
    
    def _generate_presentation_class(self):
        """Generate a presentation class"""
        filename = self.pdf_analysis['filename'].replace('.pdf', '')
        
        return {
            'name': f"Presentation_{filename}",
            'description': f"Presentación automatizada basada en {filename}",
            'methods': [
                {
                    'name': '__init__',
                    'params': 'self',
                    'description': 'Initialize presentation system',
                    'code': '''        """Initialize presentation system"""
        import pyttsx3
        import fitz
        import time
        
        self.engine = self._initialize_tts()
        self.pdf_path = r\"""" + self.pdf_path_var.get() + """\"
        self.current_slide = 0
        self.presentation_active = False
        
        print("📊 Presentation System Initialized")'''
                },
                {
                    'name': '_initialize_tts',
                    'params': 'self',
                    'description': 'Initialize speech engine',
                    'code': '''        """Initialize speech engine"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            return engine
        except Exception as e:
            print(f"Error initializing TTS: {e}")
            return None'''
                },
                {
                    'name': 'start_presentation',
                    'params': 'self',
                    'description': 'Start the presentation',
                    'code': '''        """Start the presentation"""
        try:
            self.presentation_active = True
            if self.engine:
                self.engine.say("Iniciando presentación.")
                self.engine.runAndWait()
            
            import fitz
            with fitz.open(self.pdf_path) as doc:
                total_slides = len(doc)
                
                for slide_num in range(total_slides):
                    if not self.presentation_active:
                        break
                    
                    self.current_slide = slide_num
                    page = doc[slide_num]
                    text = page.get_text()
                    
                    if text.strip():
                        summary = text[:150] + "..." if len(text) > 150 else text
                        speech_text = f"Diapositiva {slide_num + 1}. {summary}"
                        
                        if self.engine:
                            self.engine.say(speech_text)
                            self.engine.runAndWait()
                    
                    time.sleep(1.5)
                
                if self.engine:
                    self.engine.say("Presentación completada.")
                    self.engine.runAndWait()
            
        except Exception as e:
            print(f"Error in presentation: {e}")'''
                },
                {
                    'name': 'stop_presentation',
                    'params': 'self',
                    'description': 'Stop the presentation',
                    'code': '''        """Stop the presentation"""
        self.presentation_active = False
        if self.engine:
            self.engine.say("Presentación detenida.")
            self.engine.runAndWait()
        print("Presentation stopped")'''
                }
            ]
        }
    
    def _generate_generic_presentation_class(self):
        """Generate a generic presentation class"""
        filename = self.pdf_analysis['filename'].replace('.pdf', '')
        
        return {
            'name': f"GenericPresentation_{filename}",
            'description': f"Presentación genérica basada en {filename}",
            'methods': [
                {
                    'name': '__init__',
                    'params': 'self',
                    'description': 'Initialize generic presentation',
                    'code': '''        """Initialize generic presentation"""
        print("🎯 Generic Presentation System Ready")
        self.pdf_path = r\"""" + self.pdf_path_var.get() + """\"
        self.active = False'''
                },
                {
                    'name': 'run',
                    'params': 'self',
                    'description': 'Run the presentation',
                    'code': '''        """Run the presentation"""
        try:
            self.active = True
            print("▶️ Starting presentation...")
            
            import fitz
            with fitz.open(self.pdf_path) as doc:
                print(f"📊 Processing {len(doc)} slides")
                
                for i, page in enumerate(doc):
                    if not self.active:
                        break
                    
                    text = page.get_text()
                    print(f"Slide {i+1}: {text[:100]}..." if len(text) > 100 else f"Slide {i+1}: {text}")
                    
                    time.sleep(1)
            
            print("✅ Presentation completed")
            
        except Exception as e:
            print(f"❌ Error in presentation: {e}")'''
                },
                {
                    'name': 'stop',
                    'params': 'self',
                    'description': 'Stop the presentation',
                    'code': '''        """Stop the presentation"""
        self.active = False
        print("⏹️ Presentation stopped")'''
                }
            ]
        }
    
    def execute_generated_class(self):
        """Execute the generated class"""
        try:
            if not self.code_preview.get(1.0, tk.END).strip():
                messagebox.showwarning("Advertencia", "Por favor genera el código de la clase primero")
                return
            
            if self.class_execution_active:
                messagebox.showwarning("Advertencia", "Ya hay una clase ejecutándose")
                return
            
            self.execution_status_label.config(text="🚀 Ejecutando clase...", fg='#4CAF50')
            self.class_execution_active = True
            
            # Execute in separate thread to avoid blocking UI
            self.class_execution_thread = threading.Thread(target=self._execute_class_thread, daemon=True)
            self.class_execution_thread.start()
            
        except Exception as e:
            print(f"❌ Error executing class: {e}")
            messagebox.showerror("Error", f"Error al ejecutar clase: {e}")
            self.execution_status_label.config(text="Error en ejecución", fg='#f44336')
            self.class_execution_active = False
    
    def _execute_class_thread(self):
        """Execute class in separate thread"""
        try:
            # Get the generated code
            code = self.code_preview.get(1.0, tk.END)
            
            # Create a namespace for execution
            namespace = {}
            
            # Execute the class definition
            exec(code, namespace)
            
            # Find the class in the namespace
            class_name = self.class_name_var.get()
            if class_name in namespace:
                # Create instance of the class
                self.generated_class_instance = namespace[class_name]()
                
                # Update status on main thread
                self.root.after(0, lambda: self.execution_status_label.config(
                    text="✅ Clase ejecutándose", fg='#4CAF50'))
                
                # Check if class has a 'run' method and execute it
                if hasattr(self.generated_class_instance, 'run'):
                    self.generated_class_instance.run()
                elif hasattr(self.generated_class_instance, 'run_defense'):
                    self.generated_class_instance.run_defense()
                elif hasattr(self.generated_class_instance, 'start_presentation'):
                    self.generated_class_instance.start_presentation()
                else:
                    print("🎯 Clase instanciada exitosamente")
                
            else:
                self.root.after(0, lambda: self.execution_status_label.config(
                    text="Error: clase no encontrada", fg='#f44336'))
            
        except Exception as e:
            print(f"❌ Error in class execution thread: {e}")
            self.root.after(0, lambda: self.execution_status_label.config(
                text=f"Error: {str(e)[:30]}...", fg='#f44336'))
        finally:
            self.class_execution_active = False
    
    def stop_class_execution(self):
        """Stop class execution"""
        try:
            self.class_execution_active = False
            
            if self.generated_class_instance:
                # Try to stop the instance if it has stop methods
                if hasattr(self.generated_class_instance, 'stop'):
                    self.generated_class_instance.stop()
                elif hasattr(self.generated_class_instance, 'stop_presentation'):
                    self.generated_class_instance.stop_presentation()
                
                self.generated_class_instance = None
            
            self.execution_status_label.config(text="⏹️ Ejecución detenida", fg='#888888')
            print("🛑 Class execution stopped")
            
        except Exception as e:
            print(f"❌ Error stopping class execution: {e}")
    
    def test_class_code(self):
        """Test the generated class code for syntax errors"""
        try:
            code = self.code_preview.get(1.0, tk.END).strip()
            
            if not code:
                messagebox.showwarning("Advertencia", "No hay código para probar")
                return
            
            # Try to compile the code
            compile(code, '<string>', 'exec')
            
            messagebox.showinfo("Prueba Exitosa", "✅ El código no tiene errores de sintaxis")
            self.execution_status_label.config(text="✅ Código validado", fg='#4CAF50')
            
        except SyntaxError as e:
            error_msg = f"Error de sintaxis en línea {e.lineno}: {e.msg}"
            messagebox.showerror("Error de Sintaxis", error_msg)
            self.execution_status_label.config(text="❌ Error de sintaxis", fg='#f44336')
        except Exception as e:
            error_msg = f"Error en el código: {e}"
            messagebox.showerror("Error", error_msg)
            self.execution_status_label.config(text="❌ Error en código", fg='#f44336')

    def setup_class_controller_tab(self):
        """Setup the class and sequence controller tab"""
        controller_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(controller_tab, text="🎮 Controller")
        
        # Create scrollable frame for controller content
        main_frame, canvas, container = self.create_scrollable_frame(controller_tab)
        
        # Title for controller tab
        controller_title = tk.Label(main_frame, text="Class & Sequence Controller", 
                                   font=('Arial', 18, 'bold'), 
                                   bg='#1e1e1e', fg='#ffffff')
        controller_title.pack(pady=(10, 20))
        
        # Left panel - Available Classes
        left_panel = tk.LabelFrame(main_frame, text="📚 Clases Disponibles", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Class list and controls
        class_frame = tk.Frame(left_panel, bg='#2d2d2d')
        class_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Available classes listbox
        tk.Label(class_frame, text="Clases Generadas:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        class_list_frame = tk.Frame(class_frame, bg='#2d2d2d')
        class_list_frame.pack(fill="both", expand=True, pady=(5, 10))
        
        self.available_classes_listbox = tk.Listbox(class_list_frame, 
                                                   bg='#3d3d3d', fg='#ffffff',
                                                   font=('Arial', 10),
                                                   selectmode=tk.SINGLE)
        self.available_classes_listbox.pack(side="left", fill="both", expand=True)
        
        class_scrollbar = tk.Scrollbar(class_list_frame, orient="vertical")
        class_scrollbar.pack(side="right", fill="y")
        self.available_classes_listbox.config(yscrollcommand=class_scrollbar.set)
        class_scrollbar.config(command=self.available_classes_listbox.yview)
        
        # Class control buttons
        class_buttons_frame = tk.Frame(class_frame, bg='#2d2d2d')
        class_buttons_frame.pack(fill="x", pady=10)
        
        tk.Button(class_buttons_frame, text="🔄 Actualizar Lista", 
                 command=self.refresh_available_classes,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left", padx=(0, 5))
        
        tk.Button(class_buttons_frame, text="📋 Ver Detalles", 
                 command=self.show_class_details,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left", padx=5)
        
        tk.Button(class_buttons_frame, text="🗑️ Eliminar Clase", 
                 command=self.delete_selected_class,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="right")
        
        # Middle panel - Sequences
        middle_panel = tk.LabelFrame(main_frame, text="🎬 Secuencias Disponibles", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        middle_panel.pack(side="left", fill="both", expand=True, padx=10)
        
        # Sequence list and controls
        sequence_frame = tk.Frame(middle_panel, bg='#2d2d2d')
        sequence_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Available sequences listbox
        tk.Label(sequence_frame, text="Secuencias Guardadas:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        sequence_list_frame = tk.Frame(sequence_frame, bg='#2d2d2d')
        sequence_list_frame.pack(fill="both", expand=True, pady=(5, 10))
        
        self.available_sequences_listbox = tk.Listbox(sequence_list_frame, 
                                                     bg='#3d3d3d', fg='#ffffff',
                                                     font=('Arial', 10),
                                                     selectmode=tk.SINGLE)
        self.available_sequences_listbox.pack(side="left", fill="both", expand=True)
        
        sequence_scrollbar = tk.Scrollbar(sequence_list_frame, orient="vertical")
        sequence_scrollbar.pack(side="right", fill="y")
        self.available_sequences_listbox.config(yscrollcommand=sequence_scrollbar.set)
        sequence_scrollbar.config(command=self.available_sequences_listbox.yview)
        
        # Sequence control buttons
        sequence_buttons_frame = tk.Frame(sequence_frame, bg='#2d2d2d')
        sequence_buttons_frame.pack(fill="x", pady=10)
        
        tk.Button(sequence_buttons_frame, text="🔄 Actualizar Lista", 
                 command=self.refresh_available_sequences,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left", padx=(0, 5))
        
        tk.Button(sequence_buttons_frame, text="📋 Ver Detalles", 
                 command=self.show_sequence_details,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left", padx=5)
        
        tk.Button(sequence_buttons_frame, text="🗑️ Eliminar Secuencia", 
                 command=self.delete_selected_sequence,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="right")
        
        # Right panel - Execution Control
        right_panel = tk.LabelFrame(main_frame, text="🎮 Control de Ejecución", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Execution controls
        exec_frame = tk.Frame(right_panel, bg='#2d2d2d')
        exec_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Current execution status
        tk.Label(exec_frame, text="Estado de Ejecución:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        self.controller_status_label = tk.Label(exec_frame, text="⏸️ Inactivo", 
                                              bg='#2d2d2d', fg='#FFC107',
                                              font=('Arial', 12, 'bold'))
        self.controller_status_label.pack(anchor="w", pady=(5, 15))
        
        # Execution type selection
        tk.Label(exec_frame, text="Tipo de Ejecución:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        self.execution_type_var = tk.StringVar(value="class")
        type_frame = tk.Frame(exec_frame, bg='#2d2d2d')
        type_frame.pack(fill="x", pady=(5, 10))
        
        tk.Radiobutton(type_frame, text="Ejecutar Clase", variable=self.execution_type_var, 
                      value="class", bg='#2d2d2d', fg='#ffffff', 
                      selectcolor='#4CAF50', font=('Arial', 10)).pack(anchor="w")
        tk.Radiobutton(type_frame, text="Ejecutar Secuencia", variable=self.execution_type_var, 
                      value="sequence", bg='#2d2d2d', fg='#ffffff',
                      selectcolor='#4CAF50', font=('Arial', 10)).pack(anchor="w")
        
        # Main execution buttons
        exec_buttons_frame = tk.Frame(exec_frame, bg='#2d2d2d')
        exec_buttons_frame.pack(fill="x", pady=20)
        
        self.start_execution_button = tk.Button(exec_buttons_frame, text="▶️ INICIAR", 
                                              command=self.start_execution,
                                              bg='#4CAF50', fg='white', 
                                              font=('Arial', 14, 'bold'),
                                              relief='flat', padx=20, pady=10)
        self.start_execution_button.pack(fill="x", pady=(0, 10))
        
        self.pause_execution_button = tk.Button(exec_buttons_frame, text="⏸️ PAUSAR", 
                                              command=self.pause_execution,
                                              bg='#FF9800', fg='white', 
                                              font=('Arial', 14, 'bold'),
                                              relief='flat', padx=20, pady=10,
                                              state='disabled')
        self.pause_execution_button.pack(fill="x", pady=(0, 10))
        
        self.stop_execution_button = tk.Button(exec_buttons_frame, text="⏹️ DETENER", 
                                             command=self.stop_execution,
                                             bg='#f44336', fg='white', 
                                             font=('Arial', 14, 'bold'),
                                             relief='flat', padx=20, pady=10,
                                             state='disabled')
        self.stop_execution_button.pack(fill="x", pady=(0, 10))
        
        # Execution progress
        tk.Label(exec_frame, text="Progreso de Ejecución:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(20, 5))
        
        self.execution_progress = tk.Text(exec_frame, bg='#1e1e1e', fg='#ffffff',
                                        font=('Consolas', 9), height=8,
                                        wrap=tk.WORD)
        self.execution_progress.pack(fill="both", expand=True, pady=(0, 10))
        
        # Progress scrollbar
        progress_scrollbar = tk.Scrollbar(exec_frame, orient="vertical")
        progress_scrollbar.pack(side="right", fill="y")
        self.execution_progress.config(yscrollcommand=progress_scrollbar.set)
        progress_scrollbar.config(command=self.execution_progress.yview)
        
        # Initialize controller state
        self.controller_execution_active = False
        self.controller_execution_paused = False
        self.controller_execution_thread = None
        self.current_execution_item = None
        
        # Load initial data
        self.refresh_available_classes()
        self.refresh_available_sequences()

    def refresh_available_classes(self):
        """Refresh the list of available classes"""
        try:
            self.available_classes_listbox.delete(0, tk.END)
            
            # Look for generated class files in current directory
            import glob
            class_files = glob.glob("*.py")
            
            # Filter for likely generated classes
            for file in class_files:
                if any(keyword in file.lower() for keyword in ['thesis', 'defense', 'presentation', 'class_']):
                    self.available_classes_listbox.insert(tk.END, file)
            
            # Also check for classes in the generated_classes attribute if it exists
            if hasattr(self, 'generated_classes') and self.generated_classes:
                for class_name in self.generated_classes:
                    if class_name not in [self.available_classes_listbox.get(i) for i in range(self.available_classes_listbox.size())]:
                        self.available_classes_listbox.insert(tk.END, class_name)
            
            self.log_controller_message(f"Clases disponibles actualizadas: {self.available_classes_listbox.size()} encontradas")
            
        except Exception as e:
            self.log_controller_message(f"Error actualizando clases: {e}")

    def refresh_available_sequences(self):
        """Refresh the list of available sequences"""
        try:
            self.available_sequences_listbox.delete(0, tk.END)
            
            # Look for sequence files
            import glob
            import os
            
            sequences_dir = "sequences"
            if os.path.exists(sequences_dir):
                sequence_files = glob.glob(os.path.join(sequences_dir, "sequence_*.json"))
                for file in sequence_files:
                    filename = os.path.basename(file)
                    self.available_sequences_listbox.insert(tk.END, filename)
            
            self.log_controller_message(f"Secuencias disponibles actualizadas: {self.available_sequences_listbox.size()} encontradas")
            
        except Exception as e:
            self.log_controller_message(f"Error actualizando secuencias: {e}")

    def show_class_details(self):
        """Show details of the selected class"""
        try:
            selection = self.available_classes_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selección", "Selecciona una clase para ver detalles")
                return
            
            class_name = self.available_classes_listbox.get(selection[0])
            
            # Read class file content
            try:
                with open(class_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create details window
                details_window = tk.Toplevel(self.root)
                details_window.title(f"Detalles de {class_name}")
                details_window.geometry("800x600")
                details_window.configure(bg='#1e1e1e')
                
                # Content display
                text_widget = tk.Text(details_window, bg='#2d2d2d', fg='#ffffff',
                                    font=('Consolas', 10), wrap=tk.WORD)
                text_widget.pack(fill="both", expand=True, padx=10, pady=10)
                
                text_widget.insert(tk.END, content)
                text_widget.config(state='disabled')
                
                # Scrollbar
                scrollbar = tk.Scrollbar(details_window, orient="vertical")
                scrollbar.pack(side="right", fill="y")
                text_widget.config(yscrollcommand=scrollbar.set)
                scrollbar.config(command=text_widget.yview)
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
                
        except Exception as e:
            self.log_controller_message(f"Error mostrando detalles de clase: {e}")

    def show_sequence_details(self):
        """Show details of the selected sequence"""
        try:
            selection = self.available_sequences_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selección", "Selecciona una secuencia para ver detalles")
                return
            
            sequence_name = self.available_sequences_listbox.get(selection[0])
            sequence_path = os.path.join("sequences", sequence_name)
            
            # Read sequence file content
            try:
                import json
                with open(sequence_path, 'r', encoding='utf-8') as f:
                    sequence_data = json.load(f)
                
                # Create details window
                details_window = tk.Toplevel(self.root)
                details_window.title(f"Detalles de {sequence_name}")
                details_window.geometry("800x600")
                details_window.configure(bg='#1e1e1e')
                
                # Content display
                text_widget = tk.Text(details_window, bg='#2d2d2d', fg='#ffffff',
                                    font=('Consolas', 10), wrap=tk.WORD)
                text_widget.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Format sequence data nicely
                formatted_content = json.dumps(sequence_data, indent=2, ensure_ascii=False)
                text_widget.insert(tk.END, formatted_content)
                text_widget.config(state='disabled')
                
                # Scrollbar
                scrollbar = tk.Scrollbar(details_window, orient="vertical")
                scrollbar.pack(side="right", fill="y")
                text_widget.config(yscrollcommand=scrollbar.set)
                scrollbar.config(command=text_widget.yview)
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo de secuencia: {e}")
                
        except Exception as e:
            self.log_controller_message(f"Error mostrando detalles de secuencia: {e}")

    def delete_selected_class(self):
        """Delete the selected class file"""
        try:
            selection = self.available_classes_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selección", "Selecciona una clase para eliminar")
                return
            
            class_name = self.available_classes_listbox.get(selection[0])
            
            # Confirm deletion
            if messagebox.askyesno("Confirmar", f"¿Eliminar la clase '{class_name}'?"):
                try:
                    import os
                    if os.path.exists(class_name):
                        os.remove(class_name)
                        self.refresh_available_classes()
                        self.log_controller_message(f"Clase eliminada: {class_name}")
                        messagebox.showinfo("Éxito", f"Clase '{class_name}' eliminada")
                    else:
                        messagebox.showerror("Error", f"Archivo no encontrado: {class_name}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")
                    
        except Exception as e:
            self.log_controller_message(f"Error eliminando clase: {e}")

    def delete_selected_sequence(self):
        """Delete the selected sequence file"""
        try:
            selection = self.available_sequences_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selección", "Selecciona una secuencia para eliminar")
                return
            
            sequence_name = self.available_sequences_listbox.get(selection[0])
            sequence_path = os.path.join("sequences", sequence_name)
            
            # Confirm deletion
            if messagebox.askyesno("Confirmar", f"¿Eliminar la secuencia '{sequence_name}'?"):
                try:
                    import os
                    if os.path.exists(sequence_path):
                        os.remove(sequence_path)
                        self.refresh_available_sequences()
                        self.log_controller_message(f"Secuencia eliminada: {sequence_name}")
                        messagebox.showinfo("Éxito", f"Secuencia '{sequence_name}' eliminada")
                    else:
                        messagebox.showerror("Error", f"Archivo no encontrado: {sequence_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")
                    
        except Exception as e:
            self.log_controller_message(f"Error eliminando secuencia: {e}")

    def start_execution(self):
        """Start execution of selected class or sequence"""
        try:
            execution_type = self.execution_type_var.get()
            
            if execution_type == "class":
                selection = self.available_classes_listbox.curselection()
                if not selection:
                    messagebox.showwarning("Selección", "Selecciona una clase para ejecutar")
                    return
                self.current_execution_item = self.available_classes_listbox.get(selection[0])
            else:  # sequence
                selection = self.available_sequences_listbox.curselection()
                if not selection:
                    messagebox.showwarning("Selección", "Selecciona una secuencia para ejecutar")
                    return
                self.current_execution_item = self.available_sequences_listbox.get(selection[0])
            
            # Start execution in separate thread
            self.controller_execution_active = True
            self.controller_execution_paused = False
            
            # Update UI
            self.start_execution_button.config(state='disabled')
            self.pause_execution_button.config(state='normal')
            self.stop_execution_button.config(state='normal')
            self.controller_status_label.config(text="▶️ Ejecutando", fg='#4CAF50')
            
            # Start execution thread
            self.controller_execution_thread = threading.Thread(
                target=self._execute_controller_item,
                args=(execution_type, self.current_execution_item),
                daemon=True
            )
            self.controller_execution_thread.start()
            
            self.log_controller_message(f"Iniciando ejecución de {execution_type}: {self.current_execution_item}")
            
        except Exception as e:
            self.log_controller_message(f"Error iniciando ejecución: {e}")

    def pause_execution(self):
        """Pause/resume execution"""
        try:
            if self.controller_execution_paused:
                # Resume
                self.controller_execution_paused = False
                self.pause_execution_button.config(text="⏸️ PAUSAR")
                self.controller_status_label.config(text="▶️ Ejecutando", fg='#4CAF50')
                self.log_controller_message("Ejecución reanudada")
            else:
                # Pause
                self.controller_execution_paused = True
                self.pause_execution_button.config(text="▶️ REANUDAR")
                self.controller_status_label.config(text="⏸️ Pausado", fg='#FF9800')
                self.log_controller_message("Ejecución pausada")
                
        except Exception as e:
            self.log_controller_message(f"Error pausando/reanudando ejecución: {e}")

    def stop_execution(self):
        """Stop execution"""
        try:
            self.controller_execution_active = False
            self.controller_execution_paused = False
            
            # Update UI
            self.start_execution_button.config(state='normal')
            self.pause_execution_button.config(state='disabled', text="⏸️ PAUSAR")
            self.stop_execution_button.config(state='disabled')
            self.controller_status_label.config(text="⏹️ Detenido", fg='#f44336')
            
            self.log_controller_message("Ejecución detenida")
            
            # Wait for thread to finish (with timeout)
            if self.controller_execution_thread and self.controller_execution_thread.is_alive():
                self.controller_execution_thread.join(timeout=2)
            
            # Reset status after brief delay
            self.root.after(2000, lambda: self.controller_status_label.config(text="⏸️ Inactivo", fg='#FFC107'))
            
        except Exception as e:
            self.log_controller_message(f"Error deteniendo ejecución: {e}")

    def _execute_controller_item(self, execution_type, item_name):
        """Execute a class or sequence in a separate thread"""
        try:
            if execution_type == "class":
                self._execute_class_controller(item_name)
            else:  # sequence
                self._execute_sequence_controller(item_name)
                
        except Exception as e:
            self.log_controller_message(f"Error en ejecución: {e}")
        finally:
            # Reset UI state
            self.root.after(0, self._reset_execution_ui)

    def _execute_class_controller(self, class_file):
        """Execute a Python class file"""
        try:
            self.log_controller_message(f"Cargando clase: {class_file}")
            
            # Read and execute the class file
            with open(class_file, 'r', encoding='utf-8') as f:
                class_code = f.read()
            
            # Create execution environment
            exec_globals = {}
            exec_locals = {}
            
            # Execute the class definition
            exec(class_code, exec_globals, exec_locals)
            
            # Find the main class in the executed code
            class_instance = None
            for name, obj in exec_locals.items():
                if isinstance(obj, type) and hasattr(obj, '__init__'):
                    try:
                        # Try to instantiate the class
                        class_instance = obj()
                        break
                    except:
                        continue
            
            if class_instance is None:
                self.log_controller_message("❌ No se encontró una clase ejecutable")
                return
            
            self.log_controller_message(f"✅ Clase cargada: {class_instance.__class__.__name__}")
            
            # Look for execution methods
            execution_methods = []
            for method_name in dir(class_instance):
                if (method_name.startswith('execute') or 
                    method_name.startswith('run') or 
                    method_name.startswith('start') or
                    method_name == 'main'):
                    if callable(getattr(class_instance, method_name)):
                        execution_methods.append(method_name)
            
            if not execution_methods:
                self.log_controller_message("❌ No se encontraron métodos de ejecución")
                return
            
            # Execute the first available method
            method_name = execution_methods[0]
            method = getattr(class_instance, method_name)
            
            self.log_controller_message(f"🚀 Ejecutando método: {method_name}")
            
            # Execute with pause checking
            step = 0
            total_steps = 10  # Estimate for progress
            
            for step in range(total_steps):
                if not self.controller_execution_active:
                    self.log_controller_message("⏹️ Ejecución cancelada")
                    return
                
                # Wait if paused
                while self.controller_execution_paused and self.controller_execution_active:
                    time.sleep(0.1)
                
                if not self.controller_execution_active:
                    return
                
                # Simulate execution progress
                progress = (step + 1) / total_steps * 100
                self.log_controller_message(f"Progreso: {progress:.1f}% - Paso {step + 1}/{total_steps}")
                
                # Add some delay to simulate real execution
                time.sleep(1)
            
            # Execute the actual method
            method()
            
            self.log_controller_message("✅ Ejecución de clase completada")
            
        except Exception as e:
            self.log_controller_message(f"❌ Error ejecutando clase: {e}")

    def _execute_sequence_controller(self, sequence_file):
        """Execute a sequence file"""
        try:
            sequence_path = os.path.join("sequences", sequence_file)
            self.log_controller_message(f"Cargando secuencia: {sequence_file}")
            
            # Load sequence data
            import json
            with open(sequence_path, 'r', encoding='utf-8') as f:
                sequence_data = json.load(f)
            
            positions = sequence_data.get('positions', [])
            if not positions:
                self.log_controller_message("❌ Secuencia vacía")
                return
            
            self.log_controller_message(f"✅ Secuencia cargada: {len(positions)} posiciones")
            
            # Execute sequence positions
            for i, position in enumerate(positions):
                if not self.controller_execution_active:
                    self.log_controller_message("⏹️ Ejecución de secuencia cancelada")
                    return
                
                # Wait if paused
                while self.controller_execution_paused and self.controller_execution_active:
                    time.sleep(0.1)
                
                if not self.controller_execution_active:
                    return
                
                # Log position execution
                progress = (i + 1) / len(positions) * 100
                self.log_controller_message(f"Ejecutando posición {i + 1}/{len(positions)} ({progress:.1f}%)")
                
                # Send position to ESP32 if connected
                if hasattr(self, 'esp32_connector') and self.esp32_connector and self.esp32_connector.is_connected:
                    try:
                        # Extract position data
                        esp32_data = position.get('esp32_data', {})
                        if esp32_data:
                            self.esp32_connector.send_position_data(esp32_data)
                            self.log_controller_message(f"✅ Posición enviada al ESP32")
                    except Exception as e:
                        self.log_controller_message(f"⚠️ Error enviando posición al ESP32: {e}")
                
                # Wait for position duration
                duration = position.get('duration', 2.0)
                time.sleep(duration)
            
            self.log_controller_message("✅ Ejecución de secuencia completada")
            
        except Exception as e:
            self.log_controller_message(f"❌ Error ejecutando secuencia: {e}")

    def _reset_execution_ui(self):
        """Reset execution UI to initial state"""
        try:
            self.controller_execution_active = False
            self.controller_execution_paused = False
            
            self.start_execution_button.config(state='normal')
            self.pause_execution_button.config(state='disabled', text="⏸️ PAUSAR")
            self.stop_execution_button.config(state='disabled')
            self.controller_status_label.config(text="⏸️ Inactivo", fg='#FFC107')
            
        except Exception as e:
            print(f"Error resetting execution UI: {e}")

    def log_controller_message(self, message):
        """Log a message to the controller execution progress"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            
            # Insert at end and auto-scroll
            self.execution_progress.insert(tk.END, formatted_message)
            self.execution_progress.see(tk.END)
            
            # Limit text length to prevent memory issues
            lines = self.execution_progress.get("1.0", tk.END).split('\n')
            if len(lines) > 100:  # Keep last 100 lines
                self.execution_progress.delete("1.0", f"{len(lines) - 100}.0")
            
        except Exception as e:
            print(f"Error logging controller message: {e}")

    def setup_students_manager_tab(self):
        """Setup the students management tab"""
        students_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(students_tab, text="👥 Students")
        
        # Create scrollable frame for students manager content
        main_frame, canvas, container = self.create_scrollable_frame(students_tab)
        
        # Title for students tab
        students_title = tk.Label(main_frame, text="Student Management System", 
                                font=('Arial', 18, 'bold'), 
                                bg='#1e1e1e', fg='#ffffff')
        students_title.pack(pady=(10, 20))
        
        # Left panel - Registered Students
        left_panel = tk.LabelFrame(main_frame, text="📋 Registered Students", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Students list and controls
        students_frame = tk.Frame(left_panel, bg='#2d2d2d')
        students_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Current students info
        tk.Label(students_frame, text="Current Class Students:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        # Students listbox
        students_list_frame = tk.Frame(students_frame, bg='#2d2d2d')
        students_list_frame.pack(fill="both", expand=True, pady=(5, 10))
        
        self.students_listbox = tk.Listbox(students_list_frame, 
                                         bg='#3d3d3d', fg='#ffffff',
                                         font=('Arial', 10),
                                         selectmode=tk.SINGLE)
        self.students_listbox.pack(side="left", fill="both", expand=True)
        
        students_scrollbar = tk.Scrollbar(students_list_frame, orient="vertical")
        students_scrollbar.pack(side="right", fill="y")
        self.students_listbox.config(yscrollcommand=students_scrollbar.set)
        students_scrollbar.config(command=self.students_listbox.yview)
        
        # Student control buttons
        students_buttons_frame = tk.Frame(students_frame, bg='#2d2d2d')
        students_buttons_frame.pack(fill="x", pady=10)
        
        tk.Button(students_buttons_frame, text="🔄 Refresh List", 
                 command=self.refresh_students_list,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left", padx=(0, 5))
        
        tk.Button(students_buttons_frame, text="👁️ View Face", 
                 command=self.view_student_face,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left", padx=5)
        
        tk.Button(students_buttons_frame, text="✏️ Edit Student", 
                 command=self.edit_student,
                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left", padx=5)
        
        tk.Button(students_buttons_frame, text="🗑️ Remove Student", 
                 command=self.remove_student,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="right")
        
        # Statistics section
        stats_frame = tk.Frame(students_frame, bg='#2d2d2d')
        stats_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(stats_frame, text="Statistics:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        self.students_stats_label = tk.Label(stats_frame, text="Total Students: 0", 
                                           bg='#2d2d2d', fg='#4CAF50',
                                           font=('Arial', 10))
        self.students_stats_label.pack(anchor="w", pady=(5, 0))
        
        # Right panel - Add New Student
        right_panel = tk.LabelFrame(main_frame, text="➕ Add New Student", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Add student form
        add_frame = tk.Frame(right_panel, bg='#2d2d2d')
        add_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Manual entry section
        manual_section = tk.LabelFrame(add_frame, text="📝 Manual Entry", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#3d3d3d', fg='#ffffff')
        manual_section.pack(fill="x", pady=(0, 15))
        
        manual_form = tk.Frame(manual_section, bg='#3d3d3d')
        manual_form.pack(fill="x", padx=10, pady=10)
        
        # Student name
        tk.Label(manual_form, text="Student Name:", bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        self.new_student_name_var = tk.StringVar()
        tk.Entry(manual_form, textvariable=self.new_student_name_var, bg='#4d4d4d', fg='#ffffff',
                font=('Arial', 10), width=25).pack(fill="x", pady=(5, 10))
        
        # Student ID (optional)
        tk.Label(manual_form, text="Student ID (optional):", bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        self.new_student_id_var = tk.StringVar()
        tk.Entry(manual_form, textvariable=self.new_student_id_var, bg='#4d4d4d', fg='#ffffff',
                font=('Arial', 10), width=25).pack(fill="x", pady=(5, 10))
        
        # Add manually button
        tk.Button(manual_form, text="➕ Add Student Manually", 
                 command=self.add_student_manually,
                 bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'),
                 relief='flat', padx=15, pady=8).pack(fill="x", pady=(5, 0))
        
        # Camera capture section
        camera_section = tk.LabelFrame(add_frame, text="📸 Camera Capture", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#3d3d3d', fg='#ffffff')
        camera_section.pack(fill="x", pady=(0, 15))
        
        camera_form = tk.Frame(camera_section, bg='#3d3d3d')
        camera_form.pack(fill="x", padx=10, pady=10)
        
        # Camera capture instructions
        tk.Label(camera_form, text="Capture face from camera:", bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10)).pack(anchor="w")
        
        camera_buttons = tk.Frame(camera_form, bg='#3d3d3d')
        camera_buttons.pack(fill="x", pady=(5, 0))
        
        tk.Button(camera_buttons, text="📸 Capture Face", 
                 command=self.capture_student_face,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left", padx=(0, 5))
        
        tk.Button(camera_buttons, text="🎥 Live Preview", 
                 command=self.start_camera_preview,
                 bg='#9C27B0', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left")
        
        # Import section
        import_section = tk.LabelFrame(add_frame, text="📁 Import Students", 
                                     font=('Arial', 12, 'bold'),
                                     bg='#3d3d3d', fg='#ffffff')
        import_section.pack(fill="x", pady=(0, 15))
        
        import_form = tk.Frame(import_section, bg='#3d3d3d')
        import_form.pack(fill="x", padx=10, pady=10)
        
        # Import buttons
        import_buttons = tk.Frame(import_form, bg='#3d3d3d')
        import_buttons.pack(fill="x")
        
        tk.Button(import_buttons, text="📄 Import from CSV", 
                 command=self.import_students_csv,
                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left", padx=(0, 5))
        
        tk.Button(import_buttons, text="📁 Import Face Images", 
                 command=self.import_face_images,
                 bg='#795548', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(side="left")
        
        # Class management section
        class_section = tk.LabelFrame(add_frame, text="🎓 Class Management", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#3d3d3d', fg='#ffffff')
        class_section.pack(fill="both", expand=True)
        
        class_form = tk.Frame(class_section, bg='#3d3d3d')
        class_form.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Class actions
        tk.Label(class_form, text="Class Actions:", bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        class_buttons = tk.Frame(class_form, bg='#3d3d3d')
        class_buttons.pack(fill="x", pady=(5, 10))
        
        tk.Button(class_buttons, text="🔍 Auto-Identify Students", 
                 command=self.auto_identify_students,
                 bg='#E91E63', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(fill="x", pady=(0, 5))
        
        tk.Button(class_buttons, text="💾 Export Student List", 
                 command=self.export_students_list,
                 bg='#607D8B', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(fill="x", pady=(0, 5))
        
        tk.Button(class_buttons, text="🗑️ Clear All Students", 
                 command=self.clear_all_students,
                 bg='#B71C1C', fg='white', font=('Arial', 10, 'bold'),
                 relief='flat', padx=10, pady=5).pack(fill="x")
        
        # Activity log
        tk.Label(class_form, text="Activity Log:", bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w", pady=(15, 5))
        
        self.students_log = tk.Text(class_form, bg='#1e1e1e', fg='#ffffff',
                                  font=('Consolas', 8), height=6,
                                  wrap=tk.WORD)
        self.students_log.pack(fill="both", expand=True)
        
        # Initialize variables
        self.current_students = []
        self.students_faces = {}
        self.camera_preview_active = False
        self.faces_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faces")
        
        # Import required modules for this tab
        import time
        from tkinter import messagebox, simpledialog
        
        # Create faces directory if it doesn't exist
        if not os.path.exists(self.faces_dir):
            os.makedirs(self.faces_dir)
            self.log_students_message("Created faces directory")
        
        # Load initial data
        self.refresh_students_list()

    def log_students_message(self, message):
        """Log a message to the students activity log"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            
            # Insert at end and auto-scroll
            self.students_log.insert(tk.END, formatted_message)
            self.students_log.see(tk.END)
            
            # Limit text length to prevent memory issues
            lines = self.students_log.get("1.0", tk.END).split('\n')
            if len(lines) > 50:  # Keep last 50 lines
                self.students_log.delete("1.0", f"{len(lines) - 50}.0")
            
        except Exception as e:
            print(f"Error logging students message: {e}")

    def refresh_students_list(self):
        """Refresh the list of registered students"""
        try:
            self.students_listbox.delete(0, tk.END)
            self.current_students = []
            self.students_faces = {}
            
            # Load known faces from files
            if os.path.exists(self.faces_dir):
                face_files = [f for f in os.listdir(self.faces_dir) if f.endswith('.jpg')]
                
                for face_file in face_files:
                    student_name = face_file.replace('.jpg', '')
                    self.current_students.append(student_name)
                    
                    # Load face encoding
                    face_path = os.path.join(self.faces_dir, face_file)
                    try:
                        import face_recognition
                        image = face_recognition.load_image_file(face_path)
                        encodings = face_recognition.face_encodings(image)
                        if encodings:
                            self.students_faces[student_name] = encodings[0]
                    except Exception as e:
                        self.log_students_message(f"Warning: Could not load face encoding for {student_name}: {e}")
                    
                    # Add to listbox with status
                    status = "✅" if student_name in self.students_faces else "⚠️"
                    self.students_listbox.insert(tk.END, f"{status} {student_name}")
            
            # Update statistics
            total_students = len(self.current_students)
            faces_loaded = len(self.students_faces)
            self.students_stats_label.config(text=f"Total Students: {total_students} | Faces Loaded: {faces_loaded}")
            
            self.log_students_message(f"Refreshed student list: {total_students} students, {faces_loaded} faces loaded")
            
        except Exception as e:
            self.log_students_message(f"Error refreshing student list: {e}")

    def add_student_manually(self):
        """Add a student manually without face recognition"""
        try:
            name = self.new_student_name_var.get().strip()
            student_id = self.new_student_id_var.get().strip()
            
            if not name:
                messagebox.showwarning("Invalid Input", "Please enter a student name")
                return
            
            # Clean the name
            clean_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
            if not clean_name:
                messagebox.showwarning("Invalid Input", "Please enter a valid student name")
                return
            
            # Check if student already exists
            if clean_name in self.current_students:
                messagebox.showwarning("Duplicate Student", f"Student '{clean_name}' already exists")
                return
            
            # Add to current students list
            self.current_students.append(clean_name)
            
            # Create a placeholder face file (empty/default)
            try:
                # Create a simple placeholder image
                import numpy as np
                placeholder_img = np.ones((150, 150, 3), dtype=np.uint8) * 200  # Light gray
                
                # Add text to placeholder
                import cv2
                cv2.putText(placeholder_img, clean_name[:10], (10, 75), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
                cv2.putText(placeholder_img, "No Face", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
                
                face_path = os.path.join(self.faces_dir, f"{clean_name}.jpg")
                cv2.imwrite(face_path, placeholder_img)
                
            except Exception as e:
                self.log_students_message(f"Warning: Could not create placeholder image for {clean_name}: {e}")
            
            # Clear form
            self.new_student_name_var.set("")
            self.new_student_id_var.set("")
            
            # Refresh list
            self.refresh_students_list()
            
            self.log_students_message(f"Added student manually: {clean_name}")
            messagebox.showinfo("Success", f"Student '{clean_name}' added successfully!")
            
        except Exception as e:
            self.log_students_message(f"Error adding student manually: {e}")
            messagebox.showerror("Error", f"Failed to add student: {e}")

    def view_student_face(self):
        """View the face image of the selected student"""
        try:
            selection = self.students_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a student to view their face")
                return
            
            selected_text = self.students_listbox.get(selection[0])
            student_name = selected_text.split(" ", 1)[1]  # Remove status emoji
            
            face_path = os.path.join(self.faces_dir, f"{student_name}.jpg")
            
            if not os.path.exists(face_path):
                messagebox.showerror("File Not Found", f"Face image not found for {student_name}")
                return
            
            # Display face image
            import cv2
            face_img = cv2.imread(face_path)
            if face_img is not None:
                # Resize for display
                height, width = face_img.shape[:2]
                max_size = 400
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                
                resized_img = cv2.resize(face_img, (new_width, new_height))
                
                # Show in window
                cv2.imshow(f"Face: {student_name}", resized_img)
                cv2.waitKey(0)
                cv2.destroyWindow(f"Face: {student_name}")
            else:
                messagebox.showerror("Error", f"Could not load face image for {student_name}")
            
            self.log_students_message(f"Viewed face for student: {student_name}")
            
        except Exception as e:
            self.log_students_message(f"Error viewing student face: {e}")
            messagebox.showerror("Error", f"Failed to view face: {e}")

    def edit_student(self):
        """Edit the selected student's information"""
        try:
            selection = self.students_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a student to edit")
                return
            
            selected_text = self.students_listbox.get(selection[0])
            current_name = selected_text.split(" ", 1)[1]  # Remove status emoji
            
            # Create edit dialog
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Edit Student: {current_name}")
            edit_window.geometry("400x300")
            edit_window.configure(bg='#1e1e1e')
            edit_window.transient(self.root)
            edit_window.grab_set()
            
            # Center the window
            edit_window.update_idletasks()
            x = (edit_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (edit_window.winfo_screenheight() // 2) - (300 // 2)
            edit_window.geometry(f"400x300+{x}+{y}")
            
            # Edit form
            main_frame = tk.Frame(edit_window, bg='#1e1e1e')
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Label(main_frame, text="Edit Student Information", 
                    font=('Arial', 14, 'bold'), bg='#1e1e1e', fg='#ffffff').pack(pady=(0, 20))
            
            # Current name
            tk.Label(main_frame, text="Current Name:", bg='#1e1e1e', fg='#ffffff',
                    font=('Arial', 10, 'bold')).pack(anchor="w")
            tk.Label(main_frame, text=current_name, bg='#1e1e1e', fg='#4CAF50',
                    font=('Arial', 10)).pack(anchor="w", pady=(0, 10))
            
            # New name
            tk.Label(main_frame, text="New Name:", bg='#1e1e1e', fg='#ffffff',
                    font=('Arial', 10, 'bold')).pack(anchor="w")
            new_name_var = tk.StringVar(value=current_name)
            tk.Entry(main_frame, textvariable=new_name_var, bg='#3d3d3d', fg='#ffffff',
                    font=('Arial', 10), width=30).pack(fill="x", pady=(5, 15))
            
            # Buttons
            buttons_frame = tk.Frame(main_frame, bg='#1e1e1e')
            buttons_frame.pack(fill="x", pady=(20, 0))
            
            def save_changes():
                try:
                    new_name = new_name_var.get().strip()
                    if not new_name:
                        messagebox.showwarning("Invalid Input", "Please enter a valid name")
                        return
                    
                    clean_new_name = "".join(c for c in new_name if c.isalnum() or c in " _-").strip()
                    if not clean_new_name:
                        messagebox.showwarning("Invalid Input", "Please enter a valid name")
                        return
                    
                    if clean_new_name == current_name:
                        edit_window.destroy()
                        return
                    
                    if clean_new_name in self.current_students:
                        messagebox.showwarning("Duplicate Name", f"Student '{clean_new_name}' already exists")
                        return
                    
                    # Rename face file
                    old_face_path = os.path.join(self.faces_dir, f"{current_name}.jpg")
                    new_face_path = os.path.join(self.faces_dir, f"{clean_new_name}.jpg")
                    
                    if os.path.exists(old_face_path):
                        os.rename(old_face_path, new_face_path)
                    
                    # Update internal data
                    if current_name in self.current_students:
                        index = self.current_students.index(current_name)
                        self.current_students[index] = clean_new_name
                    
                    if current_name in self.students_faces:
                        self.students_faces[clean_new_name] = self.students_faces.pop(current_name)
                    
                    # Refresh list
                    self.refresh_students_list()
                    
                    self.log_students_message(f"Renamed student: {current_name} → {clean_new_name}")
                    messagebox.showinfo("Success", f"Student renamed to '{clean_new_name}'")
                    edit_window.destroy()
                    
                except Exception as e:
                    self.log_students_message(f"Error saving student changes: {e}")
                    messagebox.showerror("Error", f"Failed to save changes: {e}")
            
            tk.Button(buttons_frame, text="💾 Save Changes", command=save_changes,
                     bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                     relief='flat', padx=15, pady=8).pack(side="left", padx=(0, 10))
            
            tk.Button(buttons_frame, text="❌ Cancel", command=edit_window.destroy,
                     bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                     relief='flat', padx=15, pady=8).pack(side="right")
            
        except Exception as e:
            self.log_students_message(f"Error editing student: {e}")
            messagebox.showerror("Error", f"Failed to edit student: {e}")

    def remove_student(self):
        """Remove the selected student"""
        try:
            selection = self.students_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a student to remove")
                return
            
            selected_text = self.students_listbox.get(selection[0])
            student_name = selected_text.split(" ", 1)[1]  # Remove status emoji
            
            # Confirm removal
            if messagebox.askyesno("Confirm Removal", 
                                 f"Are you sure you want to remove '{student_name}' from the class?\n\n"
                                 f"This will delete their face data permanently."):
                
                # Remove face file
                face_path = os.path.join(self.faces_dir, f"{student_name}.jpg")
                if os.path.exists(face_path):
                    os.remove(face_path)
                
                # Remove from internal data
                if student_name in self.current_students:
                    self.current_students.remove(student_name)
                
                if student_name in self.students_faces:
                    del self.students_faces[student_name]
                
                # Refresh list
                self.refresh_students_list()
                
                self.log_students_message(f"Removed student: {student_name}")
                messagebox.showinfo("Success", f"Student '{student_name}' removed successfully")
                
        except Exception as e:
            self.log_students_message(f"Error removing student: {e}")
            messagebox.showerror("Error", f"Failed to remove student: {e}")

    def capture_student_face(self):
        """Capture a student's face from camera"""
        try:
            # Get student name first
            name = self.new_student_name_var.get().strip()
            if not name:
                messagebox.showwarning("Missing Name", "Please enter a student name before capturing face")
                return
            
            clean_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
            if not clean_name:
                messagebox.showwarning("Invalid Name", "Please enter a valid student name")
                return
            
            if clean_name in self.current_students:
                if not messagebox.askyesno("Student Exists", 
                                         f"Student '{clean_name}' already exists. Replace their face?"):
                    return
            
            # Capture from camera
            self.log_students_message(f"Starting face capture for {clean_name}")
            
            import cv2
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                messagebox.showerror("Camera Error", "Could not open camera")
                return
            
            cv2.namedWindow("Face Capture - Press SPACE to capture, ESC to cancel", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Face Capture - Press SPACE to capture, ESC to cancel", 640, 480)
            
            face_captured = False
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Draw instructions
                cv2.putText(frame, f"Capturing face for: {clean_name}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Press SPACE to capture, ESC to cancel", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Try to detect faces and draw rectangles
                try:
                    import face_recognition
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_frame)
                    
                    for (top, right, bottom, left) in face_locations:
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(frame, "Face detected", (left, top-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                except Exception:
                    pass  # Continue without face detection if it fails
                
                cv2.imshow("Face Capture - Press SPACE to capture, ESC to cancel", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 32:  # SPACE key
                    # Capture face
                    face_path = os.path.join(self.faces_dir, f"{clean_name}.jpg")
                    cv2.imwrite(face_path, frame)
                    
                    # Try to generate face encoding
                    try:
                        import face_recognition
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        face_encodings = face_recognition.face_encodings(rgb_frame)
                        if face_encodings:
                            self.students_faces[clean_name] = face_encodings[0]
                            self.log_students_message(f"Face encoding generated for {clean_name}")
                        else:
                            self.log_students_message(f"Warning: No face encoding generated for {clean_name}")
                    except Exception as e:
                        self.log_students_message(f"Warning: Could not generate face encoding: {e}")
                    
                    face_captured = True
                    break
                    
                elif key == 27:  # ESC key
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if face_captured:
                # Add to students list if not already there
                if clean_name not in self.current_students:
                    self.current_students.append(clean_name)
                
                # Clear form
                self.new_student_name_var.set("")
                self.new_student_id_var.set("")
                
                # Refresh list
                self.refresh_students_list()
                
                self.log_students_message(f"Face captured successfully for {clean_name}")
                messagebox.showinfo("Success", f"Face captured for '{clean_name}'!")
            else:
                self.log_students_message(f"Face capture cancelled for {clean_name}")
            
        except Exception as e:
            self.log_students_message(f"Error capturing face: {e}")
            messagebox.showerror("Error", f"Failed to capture face: {e}")

    def start_camera_preview(self):
        """Start camera preview for positioning"""
        try:
            if self.camera_preview_active:
                messagebox.showinfo("Camera Active", "Camera preview is already running")
                return
            
            import cv2
            
            def preview_thread():
                self.camera_preview_active = True
                cap = cv2.VideoCapture(0)
                
                if not cap.isOpened():
                    self.log_students_message("Error: Could not open camera for preview")
                    self.camera_preview_active = False
                    return
                
                cv2.namedWindow("Camera Preview - Press ESC to close", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Camera Preview - Press ESC to close", 640, 480)
                
                while self.camera_preview_active:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame = cv2.flip(frame, 1)  # Mirror effect
                    
                    # Draw grid for positioning
                    h, w = frame.shape[:2]
                    cv2.line(frame, (w//3, 0), (w//3, h), (255, 255, 255), 1)
                    cv2.line(frame, (2*w//3, 0), (2*w//3, h), (255, 255, 255), 1)
                    cv2.line(frame, (0, h//3), (w, h//3), (255, 255, 255), 1)
                    cv2.line(frame, (0, 2*h//3), (w, 2*h//3), (255, 255, 255), 1)
                    
                    cv2.putText(frame, "Position face in center area", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "Press ESC to close preview", (10, h-20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow("Camera Preview - Press ESC to close", frame)
                    
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                        break
                
                cap.release()
                cv2.destroyAllWindows()
                self.camera_preview_active = False
                self.log_students_message("Camera preview closed")
            
            # Start preview in separate thread
            import threading
            preview_thread = threading.Thread(target=preview_thread, daemon=True)
            preview_thread.start()
            
            self.log_students_message("Camera preview started")
            
        except Exception as e:
            self.log_students_message(f"Error starting camera preview: {e}")
            messagebox.showerror("Error", f"Failed to start camera preview: {e}")

    def import_students_csv(self):
        """Import students from CSV file"""
        try:
            from tkinter import filedialog
            
            csv_file = filedialog.askopenfilename(
                title="Select CSV file with student names",
                filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if not csv_file:
                return
            
            imported_count = 0
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                import csv
                reader = csv.reader(f)
                
                for row_num, row in enumerate(reader, 1):
                    if not row or not row[0].strip():
                        continue
                    
                    name = row[0].strip()
                    clean_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
                    
                    if not clean_name or clean_name in self.current_students:
                        continue
                    
                    # Add student without face
                    self.current_students.append(clean_name)
                    
                    # Create placeholder image
                    try:
                        import numpy as np
                        import cv2
                        placeholder_img = np.ones((150, 150, 3), dtype=np.uint8) * 200
                        cv2.putText(placeholder_img, clean_name[:10], (10, 75), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
                        cv2.putText(placeholder_img, "Imported", (10, 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
                        
                        face_path = os.path.join(self.faces_dir, f"{clean_name}.jpg")
                        cv2.imwrite(face_path, placeholder_img)
                        imported_count += 1
                        
                    except Exception as e:
                        self.log_students_message(f"Warning: Could not create placeholder for {clean_name}: {e}")
            
            self.refresh_students_list()
            self.log_students_message(f"Imported {imported_count} students from CSV")
            messagebox.showinfo("Import Complete", f"Successfully imported {imported_count} students")
            
        except Exception as e:
            self.log_students_message(f"Error importing CSV: {e}")
            messagebox.showerror("Error", f"Failed to import CSV: {e}")

    def import_face_images(self):
        """Import face images from a directory"""
        try:
            from tkinter import filedialog
            
            image_dir = filedialog.askdirectory(title="Select directory containing face images")
            if not image_dir:
                return
            
            imported_count = 0
            supported_formats = ['.jpg', '.jpeg', '.png', '.bmp']
            
            for filename in os.listdir(image_dir):
                if any(filename.lower().endswith(fmt) for fmt in supported_formats):
                    # Extract name from filename (without extension)
                    name = os.path.splitext(filename)[0]
                    clean_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
                    
                    if not clean_name:
                        continue
                    
                    source_path = os.path.join(image_dir, filename)
                    dest_path = os.path.join(self.faces_dir, f"{clean_name}.jpg")
                    
                    try:
                        # Copy and convert image
                        import cv2
                        img = cv2.imread(source_path)
                        if img is not None:
                            cv2.imwrite(dest_path, img)
                            
                            # Add to students list if not already there
                            if clean_name not in self.current_students:
                                self.current_students.append(clean_name)
                            
                            # Try to generate face encoding
                            try:
                                import face_recognition
                                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                encodings = face_recognition.face_encodings(rgb_img)
                                if encodings:
                                    self.students_faces[clean_name] = encodings[0]
                            except Exception:
                                pass  # Continue without encoding if it fails
                            
                            imported_count += 1
                            
                    except Exception as e:
                        self.log_students_message(f"Warning: Could not import {filename}: {e}")
            
            self.refresh_students_list()
            self.log_students_message(f"Imported {imported_count} face images")
            messagebox.showinfo("Import Complete", f"Successfully imported {imported_count} face images")
            
        except Exception as e:
            self.log_students_message(f"Error importing face images: {e}")
            messagebox.showerror("Error", f"Failed to import face images: {e}")

    def auto_identify_students(self):
        """Auto-identify students using camera (similar to main.py)"""
        try:
            self.log_students_message("Starting auto-identification process...")
            
            import cv2
            import face_recognition
            
            # Start camera capture
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Camera Error", "Could not open camera for identification")
                return
            
            cv2.namedWindow("Auto Identification - Press SPACE to capture, ESC to finish", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Auto Identification - Press SPACE to capture, ESC to finish", 800, 600)
            
            identified_students = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                
                # Detect faces
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                
                # Draw rectangles around faces
                for i, (top, right, bottom, left) in enumerate(face_locations):
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"Person {i+1}", (left, top-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Instructions
                cv2.putText(frame, f"Detected {len(face_locations)} faces", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame, "Press SPACE to identify, ESC to finish", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Identified: {len(identified_students)}", (10, frame.shape[0]-20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                cv2.imshow("Auto Identification - Press SPACE to capture, ESC to finish", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 32:  # SPACE
                    # Identify faces
                    if face_locations:
                        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                        
                        for i, encoding in enumerate(face_encodings):
                            # Check against known faces
                            name_found = False
                            for known_name, known_encoding in self.students_faces.items():
                                matches = face_recognition.compare_faces([known_encoding], encoding, tolerance=0.6)
                                if matches[0]:
                                    if known_name not in identified_students:
                                        identified_students.append(known_name)
                                        self.log_students_message(f"Identified: {known_name}")
                                    name_found = True
                                    break
                            
                            if not name_found:
                                # Ask for name
                                name = tk.simpledialog.askstring("Unknown Face", 
                                                                f"Enter name for person {i+1}:")
                                if name:
                                    clean_name = "".join(c for c in name if c.isalnum() or c in " _-").strip()
                                    if clean_name and clean_name not in identified_students:
                                        # Save face
                                        top, right, bottom, left = face_locations[i]
                                        face_img = frame[top:bottom, left:right]
                                        face_path = os.path.join(self.faces_dir, f"{clean_name}.jpg")
                                        cv2.imwrite(face_path, face_img)
                                        
                                        # Add to lists
                                        if clean_name not in self.current_students:
                                            self.current_students.append(clean_name)
                                        self.students_faces[clean_name] = encoding
                                        identified_students.append(clean_name)
                                        
                                        self.log_students_message(f"Added new student: {clean_name}")
                
                elif key == 27:  # ESC
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            self.refresh_students_list()
            self.log_students_message(f"Auto-identification complete. Identified {len(identified_students)} students")
            messagebox.showinfo("Identification Complete", 
                               f"Successfully identified {len(identified_students)} students:\n" + 
                               "\n".join(identified_students))
            
        except Exception as e:
            self.log_students_message(f"Error in auto-identification: {e}")
            messagebox.showerror("Error", f"Failed to auto-identify students: {e}")

    def export_students_list(self):
        """Export the current students list to CSV"""
        try:
            from tkinter import filedialog
            
            if not self.current_students:
                messagebox.showwarning("No Students", "No students to export")
                return
            
            csv_file = filedialog.asksaveasfilename(
                title="Save student list as CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not csv_file:
                return
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                import csv
                writer = csv.writer(f)
                
                # Header
                writer.writerow(["Student Name", "Has Face Data", "Face File"])
                
                # Data
                for student in self.current_students:
                    has_face = "Yes" if student in self.students_faces else "No"
                    face_file = f"{student}.jpg"
                    writer.writerow([student, has_face, face_file])
            
            self.log_students_message(f"Exported {len(self.current_students)} students to {csv_file}")
            messagebox.showinfo("Export Complete", f"Student list exported to {csv_file}")
            
        except Exception as e:
            self.log_students_message(f"Error exporting students: {e}")
            messagebox.showerror("Error", f"Failed to export students: {e}")

    def clear_all_students(self):
        """Clear all students from the system"""
        try:
            if not self.current_students:
                messagebox.showinfo("No Students", "No students to clear")
                return
            
            if messagebox.askyesno("Confirm Clear All", 
                                 f"Are you sure you want to remove ALL {len(self.current_students)} students?\n\n"
                                 f"This will delete all face data permanently and cannot be undone."):
                
                # Remove all face files
                if os.path.exists(self.faces_dir):
                    for filename in os.listdir(self.faces_dir):
                        if filename.endswith('.jpg'):
                            file_path = os.path.join(self.faces_dir, filename)
                            try:
                                os.remove(file_path)
                            except Exception as e:
                                self.log_students_message(f"Warning: Could not delete {filename}: {e}")
                
                # Clear internal data
                count = len(self.current_students)
                self.current_students.clear()
                self.students_faces.clear()
                
                # Refresh display
                self.refresh_students_list()
                
                self.log_students_message(f"Cleared all {count} students from system")
                messagebox.showinfo("Clear Complete", f"All {count} students have been removed")
                
        except Exception as e:
            self.log_students_message(f"Error clearing students: {e}")
            messagebox.showerror("Error", f"Failed to clear students: {e}")

    def setup_classes_manager_tab(self):
        """Setup the classes manager tab (legacy fallback)"""
        classes_tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(classes_tab, text="📚 Classes Manager")
        tk.Label(classes_tab, text="Classes Manager tab fallback - please restart application",
                bg='#1e1e1e', fg='#ff0000', font=('Arial', 14)).pack(pady=50)

def main():
    """Main function"""
    print("Starting ADAI Robot GUI Application...")
    
    try:
        app = RobotGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main() 