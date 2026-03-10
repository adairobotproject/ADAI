#!/usr/bin/env python3
"""
Aruco Marker Generator
=====================

A comprehensive Aruco marker generator for the ADAI robot system that:
1. Generates Aruco markers with different dictionaries
2. Saves markers as images
3. Manages marker collections
4. Provides detection capabilities
5. Integrates with the robot GUI

Arucos are square markers with binary patterns used for:
- Robot localization
- Object identification
- Pose estimation
- Augmented reality applications
"""

import cv2
import numpy as np
import os
import json
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import time

class ArucoGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ADAI Aruco Marker Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Aruco parameters
        self.aruco_dict_type = tk.StringVar(value="DICT_4X4_50")
        self.marker_id = tk.IntVar(value=0)
        self.marker_size = tk.IntVar(value=200)
        self.marker_margin = tk.IntVar(value=2)
        
        # Available Aruco dictionaries
        self.aruco_dicts = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
            "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
            "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
            "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
            "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
            "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
            "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
            "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
            "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
            "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
            "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000
        }
        
        # Generated markers
        self.generated_markers = {}
        self.markers_folder = "aruco_markers"
        
        # Camera parameters for detection
        self.camera_index = tk.IntVar(value=0)
        self.is_running = False
        self.cap = None
        self.detected_arucos = []
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # UI components
        self.preview_label = None
        self.marker_listbox = None
        self.detection_listbox = None
        
        # Create markers folder
        self.create_markers_folder()
        
        self.setup_ui()
        self.setup_camera()
        
    def create_markers_folder(self):
        """Create folder for storing generated markers"""
        if not os.path.exists(self.markers_folder):
            os.makedirs(self.markers_folder)
            print(f"Created markers folder: {self.markers_folder}")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_container, text="ADAI Aruco Marker Generator", 
                              font=('Arial', 20, 'bold'), 
                              bg='#1e1e1e', fg='#ffffff')
        title_label.pack(pady=(0, 10))
        
        # Top section (Generator + Preview)
        top_frame = tk.Frame(main_container, bg='#1e1e1e')
        top_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel (Generator Controls)
        self.setup_generator_panel(top_frame)
        
        # Right panel (Preview)
        self.setup_preview_panel(top_frame)
        
        # Bottom section (Camera + Lists)
        bottom_frame = tk.Frame(main_container, bg='#1e1e1e')
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Camera and lists panel
        self.setup_camera_lists_panel(bottom_frame)
        
    def setup_generator_panel(self, parent):
        """Setup the generator controls panel on the left"""
        generator_frame = tk.LabelFrame(parent, text="Aruco Generator Controls", 
                                      font=('Arial', 14, 'bold'),
                                      bg='#2d2d2d', fg='#ffffff')
        generator_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Dictionary selection
        dict_frame = tk.Frame(generator_frame, bg='#2d2d2d')
        dict_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(dict_frame, text="Aruco Dictionary:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        dict_combo = ttk.Combobox(dict_frame, textvariable=self.aruco_dict_type,
                                 values=list(self.aruco_dicts.keys()),
                                 state="readonly", font=('Arial', 10))
        dict_combo.pack(fill="x", pady=2)
        dict_combo.bind('<<ComboboxSelected>>', self.update_preview)
        
        # Marker ID
        id_frame = tk.Frame(generator_frame, bg='#2d2d2d')
        id_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(id_frame, text="Marker ID:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        id_scale = tk.Scale(id_frame, from_=0, to=49, orient="horizontal",
                           variable=self.marker_id, bg='#2d2d2d', fg='#ffffff',
                           highlightbackground='#2d2d2d',
                           command=lambda x: self.update_preview())
        id_scale.pack(fill="x", pady=2)
        
        # Marker size
        size_frame = tk.Frame(generator_frame, bg='#2d2d2d')
        size_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(size_frame, text="Marker Size (pixels):", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        size_scale = tk.Scale(size_frame, from_=100, to=500, orient="horizontal",
                             variable=self.marker_size, bg='#2d2d2d', fg='#ffffff',
                             highlightbackground='#2d2d2d',
                             command=lambda x: self.update_preview())
        size_scale.pack(fill="x", pady=2)
        
        # Marker margin
        margin_frame = tk.Frame(generator_frame, bg='#2d2d2d')
        margin_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(margin_frame, text="Marker Margin:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        margin_scale = tk.Scale(margin_frame, from_=0, to=10, orient="horizontal",
                               variable=self.marker_margin, bg='#2d2d2d', fg='#ffffff',
                               highlightbackground='#2d2d2d',
                               command=lambda x: self.update_preview())
        margin_scale.pack(fill="x", pady=2)
        
        # Generation controls
        controls_frame = tk.Frame(generator_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Generate single marker
        tk.Button(controls_frame, text="Generate Marker", 
                 command=self.generate_single_marker,
                 bg='#4CAF50', fg='white', 
                 font=('Arial', 12, 'bold')).pack(fill="x", pady=2)
        
        # Generate batch
        tk.Button(controls_frame, text="Generate Batch (0-9)", 
                 command=self.generate_batch_markers,
                 bg='#2196F3', fg='white', 
                 font=('Arial', 12, 'bold')).pack(fill="x", pady=2)
        
        # Clear all
        tk.Button(controls_frame, text="Clear All Markers", 
                 command=self.clear_all_markers,
                 bg='#f44336', fg='white', 
                 font=('Arial', 12, 'bold')).pack(fill="x", pady=2)
        
        # Export/Import
        export_frame = tk.Frame(generator_frame, bg='#2d2d2d')
        export_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(export_frame, text="Export Markers", 
                 command=self.export_markers,
                 bg='#FF9800', fg='white', 
                 font=('Arial', 10, 'bold')).pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        tk.Button(export_frame, text="Import Markers", 
                 command=self.import_markers,
                 bg='#9C27B0', fg='white', 
                 font=('Arial', 10, 'bold')).pack(side="right", fill="x", expand=True, padx=(2, 0))
        
    def setup_preview_panel(self, parent):
        """Setup the preview panel on the right"""
        preview_frame = tk.LabelFrame(parent, text="Marker Preview", 
                                    font=('Arial', 14, 'bold'),
                                    bg='#2d2d2d', fg='#ffffff')
        preview_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Preview controls
        preview_controls = tk.Frame(preview_frame, bg='#2d2d2d')
        preview_controls.pack(fill="x", padx=10, pady=5)
        
        tk.Button(preview_controls, text="Save Preview", 
                 command=self.save_preview_marker,
                 bg='#4CAF50', fg='white', 
                 font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        
        # Preview display
        preview_container = tk.Frame(preview_frame, bg='#2d2d2d')
        preview_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.preview_label = tk.Label(preview_container, text="Generate a marker to see preview",
                                     bg='#2d2d2d', fg='#ffffff', font=('Arial', 12))
        self.preview_label.pack(expand=True)
        
    def setup_camera_lists_panel(self, parent):
        """Setup the camera and lists panel at the bottom"""
        # Camera panel
        camera_frame = tk.LabelFrame(parent, text="Aruco Detection", 
                                   font=('Arial', 12, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        camera_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Camera controls
        cam_controls_frame = tk.Frame(camera_frame, bg='#2d2d2d')
        cam_controls_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(cam_controls_frame, text="Camera:", 
                bg='#2d2d2d', fg='#ffffff').pack(side="left")
        camera_entry = tk.Entry(cam_controls_frame, textvariable=self.camera_index, 
                              width=5, bg='#3d3d3d', fg='#ffffff')
        camera_entry.pack(side="left", padx=5)
        
        self.start_stop_btn = tk.Button(cam_controls_frame, text="Start Camera", 
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
        
        # Lists panel
        lists_frame = tk.Frame(parent, bg='#1e1e1e')
        lists_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Generated markers list
        markers_frame = tk.LabelFrame(lists_frame, text="Generated Markers", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#2d2d2d', fg='#ffffff')
        markers_frame.pack(fill="both", expand=True, padx=(0, 0), pady=(0, 5))
        
        self.marker_listbox = tk.Listbox(markers_frame, 
                                        bg='#3d3d3d', fg='#ffffff',
                                        font=('Consolas', 10),
                                        height=4)
        self.marker_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Detection list
        detection_frame = tk.LabelFrame(lists_frame, text="Detected Arucos", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#2d2d2d', fg='#ffffff')
        detection_frame.pack(fill="both", expand=True, padx=(0, 0), pady=(5, 0))
        
        self.detection_listbox = tk.Listbox(detection_frame, 
                                           bg='#3d3d3d', fg='#ffffff',
                                           font=('Consolas', 10),
                                           height=4)
        self.detection_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
    def setup_camera(self):
        """Initialize camera"""
        pass  # Camera setup is handled in start_camera
    
    def generate_aruco_marker(self, marker_id, dict_type, size, margin):
        """Generate a single Aruco marker"""
        try:
            # Get the Aruco dictionary using correct API
            try:
                # New API (OpenCV 4.7+)
                aruco_dict = cv2.aruco.getPredefinedDictionary(self.aruco_dicts[dict_type])
            except AttributeError:
                # Old API (OpenCV 4.6 and earlier)
                aruco_dict = cv2.aruco.Dictionary_get(self.aruco_dicts[dict_type])
            
            # Generate the marker
            marker_img = cv2.aruco.drawMarker(aruco_dict, marker_id, size)
            
            # Add margin
            if margin > 0:
                marker_img = cv2.copyMakeBorder(marker_img, margin, margin, margin, margin,
                                              cv2.BORDER_CONSTANT, value=255)
            
            return marker_img
            
        except Exception as e:
            print(f"Error generating Aruco marker: {e}")
            return None
    
    def update_preview(self, event=None):
        """Update the preview with current settings"""
        try:
            marker_img = self.generate_aruco_marker(
                self.marker_id.get(),
                self.aruco_dict_type.get(),
                self.marker_size.get(),
                self.marker_margin.get()
            )
            
            if marker_img is not None:
                # Convert to PIL Image for display
                marker_pil = Image.fromarray(marker_img)
                
                # Resize for preview (max 300x300)
                max_size = 300
                if marker_pil.width > max_size or marker_pil.height > max_size:
                    marker_pil.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(marker_pil)
                
                # Update label
                self.preview_label.configure(image=photo, text="")
                self.preview_label.image = photo  # Keep a reference
                
        except Exception as e:
            print(f"Error updating preview: {e}")
    
    def generate_single_marker(self):
        """Generate and save a single marker"""
        try:
            marker_id = self.marker_id.get()
            dict_type = self.aruco_dict_type.get()
            size = self.marker_size.get()
            margin = self.marker_margin.get()
            
            marker_img = self.generate_aruco_marker(marker_id, dict_type, size, margin)
            
            if marker_img is not None:
                # Save marker
                filename = f"aruco_{dict_type}_id{marker_id:03d}.png"
                filepath = os.path.join(self.markers_folder, filename)
                cv2.imwrite(filepath, marker_img)
                
                # Store in memory
                self.generated_markers[marker_id] = {
                    'dict_type': dict_type,
                    'size': size,
                    'margin': margin,
                    'filepath': filepath,
                    'timestamp': time.time()
                }
                
                print(f"Generated Aruco marker: {filename}")
                messagebox.showinfo("Success", f"Aruco marker saved as {filename}")
                
                # Update marker list
                self.update_marker_list()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate marker: {e}")
    
    def generate_batch_markers(self):
        """Generate a batch of markers (0-9)"""
        try:
            dict_type = self.aruco_dict_type.get()
            size = self.marker_size.get()
            margin = self.marker_margin.get()
            
            generated_count = 0
            for marker_id in range(10):  # Generate markers 0-9
                marker_img = self.generate_aruco_marker(marker_id, dict_type, size, margin)
                
                if marker_img is not None:
                    # Save marker
                    filename = f"aruco_{dict_type}_id{marker_id:03d}.png"
                    filepath = os.path.join(self.markers_folder, filename)
                    cv2.imwrite(filepath, marker_img)
                    
                    # Store in memory
                    self.generated_markers[marker_id] = {
                        'dict_type': dict_type,
                        'size': size,
                        'margin': margin,
                        'filepath': filepath,
                        'timestamp': time.time()
                    }
                    generated_count += 1
            
            print(f"Generated {generated_count} Aruco markers")
            messagebox.showinfo("Success", f"Generated {generated_count} Aruco markers")
            
            # Update marker list
            self.update_marker_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate batch markers: {e}")
    
    def save_preview_marker(self):
        """Save the currently previewed marker"""
        try:
            marker_id = self.marker_id.get()
            dict_type = self.aruco_dict_type.get()
            size = self.marker_size.get()
            margin = self.marker_margin.get()
            
            marker_img = self.generate_aruco_marker(marker_id, dict_type, size, margin)
            
            if marker_img is not None:
                # Ask for filename
                filename = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                    initialname=f"aruco_{dict_type}_id{marker_id:03d}.png"
                )
                
                if filename:
                    cv2.imwrite(filename, marker_img)
                    print(f"Saved Aruco marker: {filename}")
                    messagebox.showinfo("Success", f"Aruco marker saved as {filename}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save marker: {e}")
    
    def clear_all_markers(self):
        """Clear all generated markers"""
        try:
            # Clear files
            for marker_info in self.generated_markers.values():
                if os.path.exists(marker_info['filepath']):
                    os.remove(marker_info['filepath'])
            
            # Clear memory
            self.generated_markers.clear()
            
            print("All Aruco markers cleared")
            messagebox.showinfo("Success", "All Aruco markers cleared")
            
            # Update marker list
            self.update_marker_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear markers: {e}")
    
    def export_markers(self):
        """Export marker information to JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialname=f"aruco_markers_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if filename:
                data = {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'markers': self.generated_markers
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                print(f"Exported markers to {filename}")
                messagebox.showinfo("Success", f"Markers exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export markers: {e}")
    
    def import_markers(self):
        """Import marker information from JSON"""
        try:
            filename = filedialog.askopenfilename(
                title="Select markers file",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                if 'markers' in data:
                    self.generated_markers.update(data['markers'])
                    print(f"Imported {len(data['markers'])} markers")
                    messagebox.showinfo("Success", f"Imported {len(data['markers'])} markers")
                    
                    # Update marker list
                    self.update_marker_list()
                else:
                    messagebox.showerror("Error", "Invalid file format")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import markers: {e}")
    
    def update_marker_list(self):
        """Update the marker list display"""
        try:
            self.marker_listbox.delete(0, tk.END)
            
            for marker_id, marker_info in self.generated_markers.items():
                timestamp = datetime.datetime.fromtimestamp(marker_info['timestamp']).strftime('%H:%M:%S')
                list_item = f"[{timestamp}] ID:{marker_id} - {marker_info['dict_type']}"
                self.marker_listbox.insert(tk.END, list_item)
                
        except Exception as e:
            print(f"Error updating marker list: {e}")
    
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
            
            # Update lists
            self.update_detection_list()
            
            # Small delay
            time.sleep(0.03)  # ~30 FPS
    
    def process_frame(self, frame):
        """Process a single frame for Aruco detection"""
        # Detect Arucos
        self.detected_arucos = self.detect_arucos(frame)
        
        # Draw everything
        self.draw_detected_arucos(frame)
        self.draw_performance_info(frame)
        
        return frame
    
    def detect_arucos(self, frame):
        """Detect Aruco markers in frame"""
        detected_arucos = []
        
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
                                'id': int(marker_id),
                                'dict_type': dict_name,
                                'center': (center_x, center_y),
                                'rect': (x, y, w, h),
                                'corners': corner.tolist(),
                                'confidence': 0.95,
                                'timestamp': time.time()
                            }
                            detected_arucos.append(aruco_info)
                            
                except Exception as e:
                    print(f"Error detecting with {dict_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Aruco detection error: {e}")
        
        return detected_arucos
    
    def draw_detected_arucos(self, frame):
        """Draw detected Arucos on frame"""
        for aruco in self.detected_arucos:
            center = aruco['center']
            x, y, w, h = aruco['rect']
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw Aruco ID
            cv2.putText(frame, f"ID:{aruco['id']}", 
                       (center[0] - 30, center[1] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw dictionary type
            dict_short = aruco['dict_type'].replace('DICT_', '')[:8]
            cv2.putText(frame, dict_short, 
                       (center[0] - 30, center[1] + 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
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
        cv2.putText(frame, f"Markers: {len(self.generated_markers)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Detected: {len(self.detected_arucos)}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def update_video_display(self, frame):
        """Update video display in GUI"""
        try:
            # Convert frame to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame to fit display
            height, width = frame_rgb.shape[:2]
            max_width = 400
            max_height = 250
            
            if width > max_width or height > max_height:
                scale = min(max_width / width, max_height / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
            
            # Convert to PIL Image
            frame_pil = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(frame_pil)
            
            # Update label
            self.video_label.configure(image=photo, text="")
            self.video_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Error updating video display: {e}")
            self.video_label.configure(text=f"Camera Active - FPS: {self.current_fps:.1f}")
    
    def update_detection_list(self):
        """Update the detection list display"""
        try:
            self.detection_listbox.delete(0, tk.END)
            
            for aruco in self.detected_arucos:
                timestamp = datetime.datetime.fromtimestamp(aruco['timestamp']).strftime('%H:%M:%S')
                list_item = f"[{timestamp}] ID:{aruco['id']} - {aruco['dict_type']}"
                self.detection_listbox.insert(tk.END, list_item)
                
        except Exception as e:
            print(f"Error updating detection list: {e}")
    
    def get_generated_markers(self):
        """Get all generated markers for external use"""
        return self.generated_markers.copy()
    
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
    print("Starting ADAI Aruco Generator...")
    
    try:
        app = ArucoGenerator()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
