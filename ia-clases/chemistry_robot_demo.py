#!/usr/bin/env python3
"""
Chemistry Robot Demo
===================

Demonstration script for the ADAI chemistry robot that:
1. Detects beakers with QR codes (containing substance information)
2. Registers them as targets
3. Moves to each target systematically
4. Simulates picking up beakers for chemistry experiments

This is designed for a robot that assists in chemistry classes by
identifying and handling different chemical substances.
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

class ChemistryRobotDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ADAI Chemistry Robot - Beaker Detection Demo")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Robot parameters
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
        
        # Chemistry-specific parameters
        self.beakers = []  # List of detected beakers
        self.current_beaker_index = 0
        self.auto_mode = False
        self.pickup_simulation = False
        
        # Detection parameters
        self.face_cascade = None
        self.detected_objects = []
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # UI components
        self.video_label = None
        self.beaker_listbox = None
        self.status_label = None
        
        self.setup_ui()
        self.setup_camera()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_container, text="ADAI Chemistry Robot - Beaker Detection", 
                              font=('Arial', 20, 'bold'), 
                              bg='#1e1e1e', fg='#ffffff')
        title_label.pack(pady=(0, 10))
        
        # Top section (Camera + Beaker List)
        top_frame = tk.Frame(main_container, bg='#1e1e1e')
        top_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel (Camera)
        self.setup_camera_panel(top_frame)
        
        # Right panel (Beaker Detection)
        self.setup_beaker_panel(top_frame)
        
        # Bottom section (Controls + Status)
        bottom_frame = tk.Frame(main_container, bg='#1e1e1e')
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Controls panel
        self.setup_controls_panel(bottom_frame)
        
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
        
        # Video display
        video_frame = tk.Frame(camera_frame, bg='#2d2d2d')
        video_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.video_label = tk.Label(video_frame, text="Click 'Start Camera' to begin",
                                   bg='#2d2d2d', fg='#ffffff', font=('Arial', 12))
        self.video_label.pack(expand=True)
        
    def setup_beaker_panel(self, parent):
        """Setup the beaker detection panel on the right"""
        beaker_frame = tk.LabelFrame(parent, text="Detected Beakers", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        beaker_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Beaker list
        list_frame = tk.Frame(beaker_frame, bg='#2d2d2d')
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(list_frame, bg='#2d2d2d')
        listbox_frame.pack(fill="both", expand=True)
        
        self.beaker_listbox = tk.Listbox(listbox_frame, 
                                        bg='#3d3d3d', fg='#ffffff',
                                        font=('Consolas', 10),
                                        selectmode='single')
        self.beaker_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        self.beaker_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.beaker_listbox.yview)
        
        # Beaker controls
        controls_frame = tk.Frame(beaker_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(controls_frame, text="Clear List", 
                 command=self.clear_beaker_list,
                 bg='#f44336', fg='white', 
                 font=('Arial', 10)).pack(side="left")
        
        tk.Button(controls_frame, text="Export Data", 
                 command=self.export_beaker_data,
                 bg='#2196F3', fg='white', 
                 font=('Arial', 10)).pack(side="right")
        
    def setup_controls_panel(self, parent):
        """Setup the controls panel"""
        controls_frame = tk.LabelFrame(parent, text="Robot Controls", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Control buttons
        buttons_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # Auto mode toggle
        self.auto_mode_var = tk.BooleanVar(value=False)
        auto_toggle = tk.Checkbutton(buttons_frame, text="Auto Mode", 
                                    variable=self.auto_mode_var,
                                    bg='#2d2d2d', fg='#ffffff', 
                                    selectcolor='#3d3d3d',
                                    font=('Arial', 12, 'bold'))
        auto_toggle.pack(side="left", padx=10)
        
        # Pickup simulation toggle
        self.pickup_var = tk.BooleanVar(value=False)
        pickup_toggle = tk.Checkbutton(buttons_frame, text="Pickup Simulation", 
                                      variable=self.pickup_var,
                                      bg='#2d2d2d', fg='#ffffff', 
                                      selectcolor='#3d3d3d',
                                      font=('Arial', 12, 'bold'))
        pickup_toggle.pack(side="left", padx=10)
        
        # Manual control buttons
        tk.Button(buttons_frame, text="Next Beaker", 
                 command=self.next_beaker,
                 bg='#FF9800', fg='white', 
                 font=('Arial', 12, 'bold')).pack(side="left", padx=10)
        
        tk.Button(buttons_frame, text="Pickup Current", 
                 command=self.pickup_current_beaker,
                 bg='#4CAF50', fg='white', 
                 font=('Arial', 12, 'bold')).pack(side="left", padx=10)
        
        # Status label
        self.status_label = tk.Label(buttons_frame, text="Status: Ready", 
                                   bg='#2d2d2d', fg='#00ff00',
                                   font=('Arial', 12, 'bold'))
        self.status_label.pack(side="right", padx=10)
        
    def setup_camera(self):
        """Initialize camera and detection"""
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.face_cascade.empty():
                messagebox.showerror("Error", "Failed to load face cascade classifier")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize detection: {e}")
    
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
            self.start_stop_btn.configure(text="Stop Camera", bg='#f44336')
            
            # Start video thread
            self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.video_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {e}")
    
    def stop_camera(self):
        """Stop camera capture"""
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_stop_btn.configure(text="Start Camera", bg='#4CAF50')
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
            
            # Update beaker list
            self.update_beaker_list()
            
            # Auto mode processing
            if self.auto_mode_var.get():
                self.process_auto_mode()
            
            # Small delay
            time.sleep(0.03)  # ~30 FPS
    
    def process_frame(self, frame):
        """Process a single frame"""
        # Detect beakers (QR codes and cups)
        self.detected_objects = self.detect_beakers(frame)
        
        # Update beakers list
        self.update_beakers_from_objects()
        
        # Draw everything
        self.draw_robot_arm(frame)
        self.draw_beakers(frame)
        self.draw_performance_info(frame)
        
        return frame
    
    def detect_beakers(self, frame):
        """Detect beakers (QR codes and cups) and argucos in the frame"""
        objects = []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect QR codes (beakers with substance info)
            qr_objects = self.detect_qr_codes(frame)
            objects.extend(qr_objects)
            
            # Detect cups (beakers without QR codes)
            cup_objects = self.detect_cups(frame)
            objects.extend(cup_objects)
            
            # Detect argucos (specialized chemistry objects)
            arguco_objects = self.detect_argucos(frame)
            objects.extend(arguco_objects)
                
        except Exception as e:
            print(f"Beaker detection error: {e}")
        
        return objects
    
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
                
        except Exception as e:
            print(f"QR code detection error: {e}")
        
        return qr_objects
    
    def detect_cups(self, frame):
        """Detect cups/beakers in the frame"""
        cup_objects = []
        try:
            # Convert to HSV for color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for common beaker colors (white, transparent, etc.)
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
                    
                    # Check if it looks like a beaker (reasonable aspect ratio)
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
    
    def update_beakers_from_objects(self):
        """Update beakers list from detected objects"""
        self.beakers = []
        for obj in self.detected_objects:
            beaker_info = {
                'id': len(self.beakers) + 1,
                'type': obj['type'],
                'center': obj['center'],
                'rect': obj['rect'],
                'size': obj['size'],
                'confidence': obj['confidence'],
                'timestamp': obj['timestamp'],
                'data': obj.get('data', 'Unknown substance')
            }
            self.beakers.append(beaker_info)
    
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
    
    def draw_beakers(self, frame):
        """Draw detected beakers on frame"""
        for beaker in self.beakers:
            center = beaker['center']
            x, y, w, h = beaker['rect']
            
            # Define colors for different beaker types
            color_map = {
                'qr_code': (0, 255, 255),  # Cyan for QR beakers
                'cup': (255, 255, 0),      # Yellow for regular beakers
                'arguco': (255, 0, 255)    # Magenta for argucos
            }
            
            color = color_map.get(beaker['type'], (255, 255, 255))
            
            # Special color handling for argucos based on subtype
            if beaker['type'] == 'arguco' and 'subtype' in beaker:
                if 'blue' in beaker['subtype']:
                    color = (255, 0, 0)  # Blue in BGR
                elif 'green' in beaker['subtype']:
                    color = (0, 255, 0)  # Green in BGR
                elif 'red' in beaker['subtype']:
                    color = (0, 0, 255)  # Red in BGR
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw beaker ID
            beaker_text = f"Beaker {beaker['id']}"
            cv2.putText(frame, beaker_text, 
                       (center[0] - 30, center[1] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Draw substance info
            if beaker['type'] == 'qr_code':
                substance_text = beaker['data'][:15] + "..." if len(beaker['data']) > 15 else beaker['data']
                cv2.putText(frame, substance_text, 
                           (center[0] - 30, center[1] + 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            elif beaker['type'] == 'arguco' and 'subtype' in beaker:
                arguco_subtype = beaker['subtype'].replace('_', ' ').title()
                cv2.putText(frame, arguco_subtype, 
                           (center[0] - 30, center[1] + 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            else:
                cv2.putText(frame, "Unknown substance", 
                           (center[0] - 30, center[1] + 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # Highlight current beaker
            if beaker['id'] == self.current_beaker_index + 1:
                cv2.circle(frame, center, 25, (255, 255, 0), 3)  # Yellow circle around current
    
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
        cv2.putText(frame, f"Beakers: {len(self.beakers)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Robot status
        status = "MOVING" if self.is_moving else "IDLE"
        cv2.putText(frame, f"Robot: {status}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Auto mode status
        auto_status = "AUTO" if self.auto_mode_var.get() else "MANUAL"
        cv2.putText(frame, f"Mode: {auto_status}", (10, 120), 
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
            from PIL import Image, ImageTk
            pil_image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=pil_image)
            
            # Update label
            self.video_label.configure(image=photo, text="")
            self.video_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Error updating video display: {e}")
    
    def update_beaker_list(self):
        """Update the beaker detection list"""
        try:
            self.beaker_listbox.delete(0, tk.END)
            
            for beaker in self.beakers:
                timestamp = datetime.datetime.fromtimestamp(beaker['timestamp']).strftime('%H:%M:%S')
                list_item = f"[{timestamp}] Beaker {beaker['id']}: {beaker['type']}"
                
                if beaker['type'] == 'qr_code':
                    substance = beaker['data'][:20] + "..." if len(beaker['data']) > 20 else beaker['data']
                    list_item += f" - {substance}"
                elif beaker['type'] == 'arguco' and 'subtype' in beaker:
                    arguco_subtype = beaker['subtype'].replace('_', ' ').title()
                    list_item += f" - {arguco_subtype}"
                else:
                    list_item += " - Unknown substance"
                
                self.beaker_listbox.insert(tk.END, list_item)
                
        except Exception as e:
            print(f"Error updating beaker list: {e}")
    
    def clear_beaker_list(self):
        """Clear the beaker detection list"""
        self.beaker_listbox.delete(0, tk.END)
        self.beakers.clear()
    
    def export_beaker_data(self):
        """Export beaker detection data to JSON"""
        try:
            data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'beakers': self.beakers,
                'statistics': {
                    'total_beakers': len(self.beakers),
                    'qr_beakers': len([b for b in self.beakers if b['type'] == 'qr_code']),
                    'regular_beakers': len([b for b in self.beakers if b['type'] == 'cup']),
                    'argucos': len([b for b in self.beakers if b['type'] == 'arguco'])
                }
            }
            
            filename = f"chemistry_robot_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def next_beaker(self):
        """Move to next beaker"""
        if not self.beakers:
            self.status_label.configure(text="Status: No beakers detected", fg='#ff4444')
            return
        
        self.current_beaker_index = (self.current_beaker_index + 1) % len(self.beakers)
        beaker = self.beakers[self.current_beaker_index]
        
        # Move robot to beaker
        self.move_to_beaker(beaker)
        
        self.status_label.configure(text=f"Status: Moving to Beaker {beaker['id']}", fg='#00ff00')
    
    def pickup_current_beaker(self):
        """Pickup the current beaker"""
        if not self.beakers or self.current_beaker_index >= len(self.beakers):
            self.status_label.configure(text="Status: No beaker selected", fg='#ff4444')
            return
        
        beaker = self.beakers[self.current_beaker_index]
        
        if self.pickup_var.get():
            # Simulate pickup
            self.simulate_pickup(beaker)
        
        self.status_label.configure(text=f"Status: Picked up Beaker {beaker['id']}", fg='#00ff00')
    
    def move_to_beaker(self, beaker):
        """Move robot to a specific beaker"""
        self.target_position = beaker['center']
        self.is_moving = True
        
        # Update robot position (simulated movement)
        self.robot_position = self.target_position
        self.is_moving = False
    
    def simulate_pickup(self, beaker):
        """Simulate picking up a beaker"""
        print(f"Simulating pickup of Beaker {beaker['id']}: {beaker['data']}")
        # In a real implementation, this would control the robot arm
        time.sleep(0.5)  # Simulate pickup time
    
    def process_auto_mode(self):
        """Process auto mode - automatically move through beakers"""
        if not self.beakers:
            return
        
        # Auto mode logic: move to each beaker and pickup
        if not self.is_moving:
            beaker = self.beakers[self.current_beaker_index]
            self.move_to_beaker(beaker)
            
            # Simulate pickup
            if self.pickup_var.get():
                self.simulate_pickup(beaker)
            
            # Move to next beaker
            self.current_beaker_index = (self.current_beaker_index + 1) % len(self.beakers)
    
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
    print("Starting ADAI Chemistry Robot Demo...")
    
    try:
        app = ChemistryRobotDemo()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
