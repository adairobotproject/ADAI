#!/usr/bin/env python3
"""
Arguco Definition Demo
=====================

Demonstration script for the custom arguco definition system that:
1. Allows users to define custom argucos by name
2. Captures color characteristics from the camera
3. Detects the defined argucos in real-time
4. Shows the detection process with visual feedback

This is designed to show how the robot can learn to recognize
specific argucos for chemistry experiments.
"""

import cv2
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime

class ArgucoDefinitionDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ADAI Arguco Definition Demo")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Camera parameters
        self.camera_index = tk.IntVar(value=0)
        self.is_running = False
        self.cap = None
        
        # Arguco definition system
        self.arguco_definitions = {}
        self.arguco_definition_mode = False
        self.arguco_definition_frames = 0
        self.arguco_definition_threshold = 5
        self.current_arguco_name = ""
        
        # Detection results
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
        title_label = tk.Label(main_container, text="ADAI Arguco Definition Demo", 
                              font=('Arial', 20, 'bold'), 
                              bg='#1e1e1e', fg='#ffffff')
        title_label.pack(pady=(0, 10))
        
        # Top section (Camera + Controls)
        top_frame = tk.Frame(main_container, bg='#1e1e1e')
        top_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel (Camera)
        self.setup_camera_panel(top_frame)
        
        # Right panel (Controls)
        self.setup_controls_panel(top_frame)
        
        # Bottom section (Lists)
        bottom_frame = tk.Frame(main_container, bg='#1e1e1e')
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Lists panel
        self.setup_lists_panel(bottom_frame)
        
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
        
    def setup_controls_panel(self, parent):
        """Setup the controls panel on the right"""
        controls_frame = tk.LabelFrame(parent, text="Arguco Definition Controls", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        controls_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Definition controls
        definition_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        definition_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(definition_frame, text="Define New Arguco:", 
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
                                   command=self.start_arguco_definition,
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
1. Enter a name for your arguco
2. Click "Define Arguco"
3. Position the arguco in the center of the camera
4. Wait for the capture to complete
5. The system will learn to detect this arguco
        """
        
        tk.Label(instructions_frame, text=instructions_text, 
                bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 10), justify="left").pack(anchor="w")
        
        # Management controls
        management_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        management_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(management_frame, text="Clear All Definitions", 
                 command=self.clear_all_definitions,
                 bg='#f44336', fg='white', 
                 font=('Arial', 12, 'bold')).pack(fill="x", pady=2)
        
        tk.Button(management_frame, text="Export Definitions", 
                 command=self.export_definitions,
                 bg='#2196F3', fg='white', 
                 font=('Arial', 12, 'bold')).pack(fill="x", pady=2)
        
        tk.Button(management_frame, text="Import Definitions", 
                 command=self.import_definitions,
                 bg='#FF9800', fg='white', 
                 font=('Arial', 12, 'bold')).pack(fill="x", pady=2)
        
    def setup_lists_panel(self, parent):
        """Setup the lists panel at the bottom"""
        lists_frame = tk.Frame(parent, bg='#1e1e1e')
        lists_frame.pack(fill="x", padx=5, pady=5)
        
        # Definitions list
        definitions_frame = tk.LabelFrame(lists_frame, text="Defined Argucos", 
                                        font=('Arial', 12, 'bold'),
                                        bg='#2d2d2d', fg='#ffffff')
        definitions_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.definition_listbox = tk.Listbox(definitions_frame, 
                                            bg='#3d3d3d', fg='#ffffff',
                                            font=('Consolas', 10),
                                            height=6)
        self.definition_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Detection list
        detection_frame = tk.LabelFrame(lists_frame, text="Detected Argucos", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#2d2d2d', fg='#ffffff')
        detection_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.detection_listbox = tk.Listbox(detection_frame, 
                                           bg='#3d3d3d', fg='#ffffff',
                                           font=('Consolas', 10),
                                           height=6)
        self.detection_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
    def setup_camera(self):
        """Initialize camera"""
        pass  # Camera setup is handled in start_camera
    
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
        # Capture arguco definition if in definition mode
        self.capture_arguco_definition(frame)
        
        # Detect argucos
        self.detected_argucos = self.detect_argucos(frame)
        
        # Draw everything
        self.draw_arguco_definition_ui(frame)
        self.draw_detected_argucos(frame)
        self.draw_performance_info(frame)
        
        return frame
    
    def start_arguco_definition(self):
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
        self.current_arguco_name = name
        self.define_btn.configure(text="Capturing...", bg='#f44336')
        self.arguco_name_entry.configure(state='disabled')
        print(f"Starting arguco definition for '{name}'")
    
    def capture_arguco_definition(self, frame):
        """Capture arguco definition from current frame"""
        if not self.arguco_definition_mode:
            return
        
        self.arguco_definition_frames += 1
        
        # Wait for threshold frames to ensure stable capture
        if self.arguco_definition_frames >= self.arguco_definition_threshold:
            name = self.current_arguco_name
            
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
                    'lower_hsv': lower_hsv.tolist(),
                    'upper_hsv': upper_hsv.tolist(),
                    'center': (center_x, center_y),
                    'timestamp': time.time()
                }
                
                print(f"Arguco '{name}' defined successfully")
                print(f"Color range: H({lower_hsv[0]:.1f}-{upper_hsv[0]:.1f}), "
                      f"S({lower_hsv[1]:.1f}-{upper_hsv[1]:.1f}), "
                      f"V({lower_hsv[2]:.1f}-{upper_hsv[2]:.1f})")
                
                # Reset definition mode
                self.arguco_definition_mode = False
                self.define_btn.configure(text="Define Arguco", bg='#9C27B0')
                self.arguco_name_entry.configure(state='normal')
                self.arguco_name_var.set("")
                
                messagebox.showinfo("Success", f"Arguco '{name}' defined successfully!")
            else:
                print("Failed to capture ROI for arguco definition")
    
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
        instruction_text = f"Position arguco '{self.current_arguco_name}' in the center"
        cv2.putText(frame, instruction_text, (10, height - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Draw progress
        progress = self.arguco_definition_frames / self.arguco_definition_threshold
        progress_text = f"Capturing... {progress*100:.0f}%"
        cv2.putText(frame, progress_text, (10, height - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
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
            max_width = 500
            max_height = 350
            
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
    
    def clear_all_definitions(self):
        """Clear all arguco definitions"""
        self.arguco_definitions.clear()
        print("All arguco definitions cleared")
    
    def export_definitions(self):
        """Export arguco definitions to JSON"""
        try:
            data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'definitions': self.arguco_definitions
            }
            
            filename = f"arguco_definitions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            messagebox.showinfo("Export Successful", f"Definitions exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export definitions: {e}")
    
    def import_definitions(self):
        """Import arguco definitions from JSON"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select definitions file",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                if 'definitions' in data:
                    self.arguco_definitions.update(data['definitions'])
                    print(f"Imported {len(data['definitions'])} definitions")
                    messagebox.showinfo("Import Successful", f"Imported {len(data['definitions'])} definitions")
                else:
                    messagebox.showerror("Import Error", "Invalid file format")
                    
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import definitions: {e}")
    
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
    print("Starting ADAI Arguco Definition Demo...")
    
    try:
        app = ArgucoDefinitionDemo()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
