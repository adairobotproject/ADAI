#!/usr/bin/env python3
"""
Arguco Paint Demo
================

A Paint-like interface for manually creating arguco definitions that:
1. Allows users to draw argucos using a canvas
2. Captures color and shape characteristics
3. Saves the definition for camera detection
4. Provides tools for drawing, erasing, and color selection

This creates a visual way to define argucos for the robot system.
"""

import cv2
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import datetime

class ArgucoPaintDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ADAI Arguco Paint - Manual Definition")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Canvas parameters
        self.canvas_width = 400
        self.canvas_height = 300
        self.canvas = None
        self.drawing = False
        self.last_x = None
        self.last_y = None
        
        # Drawing parameters
        self.brush_size = 5
        self.current_color = "#FF0000"  # Red
        self.draw_mode = "draw"  # "draw" or "erase"
        
        # Arguco definition system
        self.arguco_definitions = {}
        self.current_arguco_name = ""
        
        # Camera parameters
        self.camera_index = tk.IntVar(value=0)
        self.is_running = False
        self.cap = None
        self.detected_argucos = []
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # UI components
        self.video_label = None
        self.definition_listbox = None
        self.detection_listbox = None
        
        self.setup_ui()
        self.setup_camera()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_container, text="ADAI Arguco Paint - Manual Definition", 
                              font=('Arial', 20, 'bold'), 
                              bg='#1e1e1e', fg='#ffffff')
        title_label.pack(pady=(0, 10))
        
        # Top section (Canvas + Controls)
        top_frame = tk.Frame(main_container, bg='#1e1e1e')
        top_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel (Canvas)
        self.setup_canvas_panel(top_frame)
        
        # Right panel (Controls)
        self.setup_controls_panel(top_frame)
        
        # Bottom section (Camera + Lists)
        bottom_frame = tk.Frame(main_container, bg='#1e1e1e')
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Camera and lists panel
        self.setup_camera_lists_panel(bottom_frame)
        
    def setup_canvas_panel(self, parent):
        """Setup the canvas panel on the left"""
        canvas_frame = tk.LabelFrame(parent, text="Arguco Drawing Canvas", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        canvas_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Canvas controls
        controls_frame = tk.Frame(canvas_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Clear canvas button
        tk.Button(controls_frame, text="Clear Canvas", 
                 command=self.clear_canvas,
                 bg='#f44336', fg='white', 
                 font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        
        # Save canvas button
        tk.Button(controls_frame, text="Save as Image", 
                 command=self.save_canvas_image,
                 bg='#4CAF50', fg='white', 
                 font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        
        # Canvas
        canvas_container = tk.Frame(canvas_frame, bg='#2d2d2d')
        canvas_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_container, 
                               width=self.canvas_width, 
                               height=self.canvas_height,
                               bg='white', 
                               relief='sunken', 
                               bd=2)
        self.canvas.pack(expand=True)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        
    def setup_controls_panel(self, parent):
        """Setup the controls panel on the right"""
        controls_frame = tk.LabelFrame(parent, text="Drawing Controls", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        controls_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Drawing tools
        tools_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        tools_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(tools_frame, text="Drawing Tools:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Draw mode
        mode_frame = tk.Frame(tools_frame, bg='#2d2d2d')
        mode_frame.pack(fill="x", pady=5)
        
        self.draw_mode_var = tk.StringVar(value="draw")
        tk.Radiobutton(mode_frame, text="Draw", variable=self.draw_mode_var, 
                      value="draw", bg='#2d2d2d', fg='#ffffff',
                      selectcolor='#3d3d3d').pack(side="left", padx=5)
        tk.Radiobutton(mode_frame, text="Erase", variable=self.draw_mode_var, 
                      value="erase", bg='#2d2d2d', fg='#ffffff',
                      selectcolor='#3d3d3d').pack(side="left", padx=5)
        
        # Brush size
        size_frame = tk.Frame(tools_frame, bg='#2d2d2d')
        size_frame.pack(fill="x", pady=5)
        
        tk.Label(size_frame, text="Brush Size:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10)).pack(side="left")
        
        self.brush_size_var = tk.IntVar(value=5)
        size_scale = tk.Scale(size_frame, from_=1, to=20, orient="horizontal",
                             variable=self.brush_size_var, bg='#2d2d2d', fg='#ffffff',
                             highlightbackground='#2d2d2d')
        size_scale.pack(side="left", padx=5, fill="x", expand=True)
        
        # Color selection
        color_frame = tk.Frame(tools_frame, bg='#2d2d2d')
        color_frame.pack(fill="x", pady=5)
        
        tk.Label(color_frame, text="Color:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10)).pack(side="left")
        
        self.color_button = tk.Button(color_frame, text="Choose Color", 
                                     command=self.choose_color,
                                     bg=self.current_color, fg='white', 
                                     font=('Arial', 10))
        self.color_button.pack(side="left", padx=5)
        
        # Predefined colors
        colors_frame = tk.Frame(tools_frame, bg='#2d2d2d')
        colors_frame.pack(fill="x", pady=5)
        
        tk.Label(colors_frame, text="Quick Colors:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10)).pack(anchor="w")
        
        quick_colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']
        for color in quick_colors:
            btn = tk.Button(colors_frame, text="", width=3, height=1,
                           bg=color, command=lambda c=color: self.set_color(c))
            btn.pack(side="left", padx=2)
        
        # Arguco definition
        definition_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        definition_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(definition_frame, text="Define Arguco:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        # Name entry
        name_frame = tk.Frame(definition_frame, bg='#2d2d2d')
        name_frame.pack(fill="x", pady=5)
        
        tk.Label(name_frame, text="Name:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10)).pack(side="left")
        
        self.arguco_name_var = tk.StringVar(value="")
        self.arguco_name_entry = tk.Entry(name_frame, textvariable=self.arguco_name_var,
                                        bg='#3d3d3d', fg='#ffffff',
                                        font=('Arial', 10))
        self.arguco_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Define button
        self.define_btn = tk.Button(definition_frame, text="Define Arguco", 
                                   command=self.define_arguco_from_canvas,
                                   bg='#9C27B0', fg='white', 
                                   font=('Arial', 12, 'bold'))
        self.define_btn.pack(fill="x", pady=5)
        
        # Instructions
        instructions_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        instructions_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(instructions_frame, text="Instructions:", 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12, 'bold')).pack(anchor="w", pady=(0, 5))
        
        instructions_text = """
1. Draw your arguco on the canvas
2. Choose colors and brush size
3. Enter a name for the arguco
4. Click "Define Arguco"
5. The system will learn to detect it
        """
        
        tk.Label(instructions_frame, text=instructions_text, 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10), justify="left").pack(anchor="w")
        
    def setup_camera_lists_panel(self, parent):
        """Setup the camera and lists panel at the bottom"""
        # Camera panel
        camera_frame = tk.LabelFrame(parent, text="Camera Detection", 
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
        
        # Definitions list
        definitions_frame = tk.LabelFrame(lists_frame, text="Defined Argucos", 
                                        font=('Arial', 12, 'bold'),
                                        bg='#2d2d2d', fg='#ffffff')
        definitions_frame.pack(fill="both", expand=True, padx=(0, 0), pady=(0, 5))
        
        self.definition_listbox = tk.Listbox(definitions_frame, 
                                            bg='#3d3d3d', fg='#ffffff',
                                            font=('Consolas', 10),
                                            height=4)
        self.definition_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Detection list
        detection_frame = tk.LabelFrame(lists_frame, text="Detected Argucos", 
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
    
    def start_draw(self, event):
        """Start drawing on canvas"""
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
    
    def draw(self, event):
        """Draw on canvas"""
        if self.drawing and self.last_x and self.last_y:
            # Get current brush size
            brush_size = self.brush_size_var.get()
            
            # Get current color
            color = self.current_color
            
            # Get draw mode
            mode = self.draw_mode_var.get()
            
            if mode == "draw":
                # Draw line
                self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                      fill=color, width=brush_size, capstyle=tk.ROUND,
                                      smooth=True)
            else:  # erase mode
                # Erase by drawing with white
                self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                      fill='white', width=brush_size, capstyle=tk.ROUND,
                                      smooth=True)
            
            self.last_x = event.x
            self.last_y = event.y
    
    def stop_draw(self, event):
        """Stop drawing on canvas"""
        self.drawing = False
        self.last_x = None
        self.last_y = None
    
    def clear_canvas(self):
        """Clear the canvas"""
        self.canvas.delete("all")
    
    def choose_color(self):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(title="Choose Color")[1]
        if color:
            self.set_color(color)
    
    def set_color(self, color):
        """Set the current drawing color"""
        self.current_color = color
        self.color_button.configure(bg=color)
    
    def save_canvas_image(self):
        """Save canvas as image"""
        try:
            # Get canvas content as PostScript
            ps = self.canvas.postscript(colormode='color')
            
            # Convert to image using PIL
            from PIL import Image, ImageDraw
            
            # Create a new image with white background
            img = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Get all canvas items and draw them
            items = self.canvas.find_all()
            for item in items:
                coords = self.canvas.coords(item)
                if len(coords) >= 4:  # Line item
                    color = self.canvas.itemcget(item, 'fill')
                    width = int(self.canvas.itemcget(item, 'width'))
                    draw.line(coords, fill=color, width=width)
            
            # Save image
            filename = f"arguco_drawing_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(filename)
            messagebox.showinfo("Success", f"Canvas saved as {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save canvas: {e}")
    
    def define_arguco_from_canvas(self):
        """Define arguco from canvas drawing"""
        name = self.arguco_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a name for the arguco")
            return
        
        if name in self.arguco_definitions:
            messagebox.showerror("Error", f"Arguco '{name}' already exists")
            return
        
        try:
            # Get canvas content as image
            from PIL import Image, ImageDraw
            
            # Create a new image with white background
            img = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Get all canvas items and draw them
            items = self.canvas.find_all()
            if not items:
                messagebox.showerror("Error", "Please draw something on the canvas first")
                return
            
            for item in items:
                coords = self.canvas.coords(item)
                if len(coords) >= 4:  # Line item
                    color = self.canvas.itemcget(item, 'fill')
                    width = int(self.canvas.itemcget(item, 'width'))
                    draw.line(coords, fill=color, width=width)
            
            # Convert PIL image to OpenCV format
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # Convert to HSV and analyze colors
            hsv_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            
            # Find non-white pixels (drawn content)
            white_mask = cv2.inRange(hsv_img, np.array([0, 0, 200]), np.array([180, 30, 255]))
            non_white_mask = cv2.bitwise_not(white_mask)
            
            if cv2.countNonZero(non_white_mask) == 0:
                messagebox.showerror("Error", "No drawing content found")
                return
            
            # Calculate color statistics for non-white pixels
            non_white_pixels = hsv_img[non_white_mask > 0]
            
            if len(non_white_pixels) == 0:
                messagebox.showerror("Error", "No valid color content found")
                return
            
            # Calculate color ranges
            h_mean, s_mean, v_mean = np.mean(non_white_pixels, axis=0)
            h_std, s_std, v_std = np.std(non_white_pixels, axis=0)
            
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
                'lower_hsv': lower_hsv.tolist(),
                'upper_hsv': upper_hsv.tolist(),
                'canvas_image': img_cv.tolist(),
                'timestamp': time.time()
            }
            
            print(f"Arguco '{name}' defined from canvas successfully")
            print(f"Color range: H({lower_hsv[0]:.1f}-{upper_hsv[0]:.1f}), "
                  f"S({lower_hsv[1]:.1f}-{upper_hsv[1]:.1f}), "
                  f"V({lower_hsv[2]:.1f}-{upper_hsv[2]:.1f})")
            
            # Clear name entry
            self.arguco_name_var.set("")
            
            messagebox.showinfo("Success", f"Arguco '{name}' defined successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to define arguco: {e}")
    
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
            self.update_lists()
            
            # Small delay
            time.sleep(0.03)  # ~30 FPS
    
    def process_frame(self, frame):
        """Process a single frame"""
        # Detect argucos
        self.detected_argucos = self.detect_argucos(frame)
        
        # Draw everything
        self.draw_detected_argucos(frame)
        self.draw_performance_info(frame)
        
        return frame
    
    def detect_argucos(self, frame):
        """Detect argucos based on custom definitions"""
        detected_argucos = []
        
        if not self.arguco_definitions:
            return detected_argucos
        
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            for name, definition in self.arguco_definitions.items():
                # Create mask using custom color range
                lower_hsv = np.array(definition['lower_hsv'])
                upper_hsv = np.array(definition['upper_hsv'])
                mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
                
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
                                'name': name,
                                'center': (x + w // 2, y + h // 2),
                                'rect': (x, y, w, h),
                                'size': (w, h),
                                'confidence': 0.9,
                                'timestamp': time.time()
                            }
                            detected_argucos.append(arguco_info)
                            
        except Exception as e:
            print(f"Arguco detection error: {e}")
        
        return detected_argucos
    
    def draw_detected_argucos(self, frame):
        """Draw detected argucos on frame"""
        for arguco in self.detected_argucos:
            center = arguco['center']
            x, y, w, h = arguco['rect']
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw arguco name
            cv2.putText(frame, arguco['name'], 
                       (center[0] - 30, center[1] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw confidence
            confidence_text = f"{arguco['confidence']:.2f}"
            cv2.putText(frame, confidence_text, 
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
        cv2.putText(frame, f"Definitions: {len(self.arguco_definitions)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Detected: {len(self.detected_argucos)}", (10, 90), 
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
            
            # Convert to PhotoImage using tkinter's built-in method
            frame_pil = tk.PhotoImage(data=cv2.imencode('.ppm', frame_rgb)[1].tobytes())
            
            # Update label
            self.video_label.configure(image=frame_pil, text="")
            self.video_label.image = frame_pil  # Keep a reference
            
        except Exception as e:
            print(f"Error updating video display: {e}")
            self.video_label.configure(text=f"Camera Active - FPS: {self.current_fps:.1f}")
    
    def update_lists(self):
        """Update the definition and detection lists"""
        try:
            # Update definitions list
            self.definition_listbox.delete(0, tk.END)
            for name, definition in self.arguco_definitions.items():
                timestamp = datetime.datetime.fromtimestamp(definition['timestamp']).strftime('%H:%M:%S')
                list_item = f"[{timestamp}] {name}"
                self.definition_listbox.insert(tk.END, list_item)
            
            # Update detection list
            self.detection_listbox.delete(0, tk.END)
            for arguco in self.detected_argucos:
                timestamp = datetime.datetime.fromtimestamp(arguco['timestamp']).strftime('%H:%M:%S')
                list_item = f"[{timestamp}] {arguco['name']} - Conf: {arguco['confidence']:.2f}"
                self.detection_listbox.insert(tk.END, list_item)
                
        except Exception as e:
            print(f"Error updating lists: {e}")
    
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
    print("Starting ADAI Arguco Paint Demo...")
    
    try:
        app = ArgucoPaintDemo()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
