#!/usr/bin/env python3
"""
Robot Hand GUI Application (Simple Version)
==========================================

A simple GUI application for robot hand simulation with face detection
using standard Tkinter for a professional interface.
"""

import cv2
import numpy as np
import time
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class RobotHandGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robot Hand Simulation - Face Detection")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Robot hand parameters
        self.hand_size = tk.IntVar(value=80)
        self.movement_speed = tk.DoubleVar(value=0.1)
        self.max_reach = tk.IntVar(value=200)
        self.max_distance = tk.DoubleVar(value=2.0)
        
        # Camera parameters
        self.camera_index = tk.IntVar(value=0)
        self.is_running = False
        self.cap = None
        
        # Robot hand state
        self.hand_position = (320, 240)
        self.target_position = (320, 240)
        self.is_moving = False
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Face detection
        self.face_cascade = None
        self.detected_faces = []
        
        self.setup_ui()
        self.setup_camera()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Robot Hand Simulation", 
                              font=('Arial', 24, 'bold'), 
                              bg='#2b2b2b', fg='white')
        title_label.pack(pady=10)
        
        # Content frame
        content_frame = tk.Frame(main_frame, bg='#2b2b2b')
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (controls)
        left_panel = tk.Frame(content_frame, bg='#3b3b3b', width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel (video)
        right_panel = tk.Frame(content_frame, bg='#3b3b3b')
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.setup_controls(left_panel)
        self.setup_video_display(right_panel)
        
    def setup_controls(self, parent):
        """Setup control panel"""
        # Camera controls
        camera_frame = tk.LabelFrame(parent, text="Camera Controls", 
                                   font=('Arial', 16, 'bold'),
                                   bg='#3b3b3b', fg='white')
        camera_frame.pack(fill="x", padx=10, pady=10)
        
        # Camera index
        camera_index_frame = tk.Frame(camera_frame, bg='#3b3b3b')
        camera_index_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(camera_index_frame, text="Camera Index:", 
                bg='#3b3b3b', fg='white').pack(side="left")
        camera_index_entry = tk.Entry(camera_index_frame, textvariable=self.camera_index, 
                                    width=10, bg='#4b4b4b', fg='white')
        camera_index_entry.pack(side="right", padx=5)
        
        # Start/Stop button
        self.start_stop_btn = tk.Button(camera_frame, text="Start Camera", 
                                       command=self.toggle_camera,
                                       bg='#4CAF50', fg='white', 
                                       font=('Arial', 12, 'bold'))
        self.start_stop_btn.pack(pady=10)
        
        # Robot hand controls
        hand_frame = tk.LabelFrame(parent, text="Robot Hand Controls", 
                                 font=('Arial', 16, 'bold'),
                                 bg='#3b3b3b', fg='white')
        hand_frame.pack(fill="x", padx=10, pady=10)
        
        # Hand size
        hand_size_frame = tk.Frame(hand_frame, bg='#3b3b3b')
        hand_size_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(hand_size_frame, text="Hand Size:", 
                bg='#3b3b3b', fg='white').pack(side="left")
        hand_size_scale = tk.Scale(hand_size_frame, from_=20, to=150, 
                                 variable=self.hand_size, orient="horizontal",
                                 bg='#3b3b3b', fg='white', highlightbackground='#3b3b3b')
        hand_size_scale.pack(side="right", fill="x", expand=True, padx=5)
        
        # Movement speed
        speed_frame = tk.Frame(hand_frame, bg='#3b3b3b')
        speed_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(speed_frame, text="Speed:", 
                bg='#3b3b3b', fg='white').pack(side="left")
        speed_scale = tk.Scale(speed_frame, from_=0.01, to=0.5, 
                             variable=self.movement_speed, orient="horizontal",
                             bg='#3b3b3b', fg='white', highlightbackground='#3b3b3b')
        speed_scale.pack(side="right", fill="x", expand=True, padx=5)
        
        # Max reach
        reach_frame = tk.Frame(hand_frame, bg='#3b3b3b')
        reach_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(reach_frame, text="Max Reach:", 
                bg='#3b3b3b', fg='white').pack(side="left")
        reach_scale = tk.Scale(reach_frame, from_=50, to=400, 
                             variable=self.max_reach, orient="horizontal",
                             bg='#3b3b3b', fg='white', highlightbackground='#3b3b3b')
        reach_scale.pack(side="right", fill="x", expand=True, padx=5)
        
        # Max distance
        distance_frame = tk.Frame(hand_frame, bg='#3b3b3b')
        distance_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(distance_frame, text="Max Distance:", 
                bg='#3b3b3b', fg='white').pack(side="left")
        distance_scale = tk.Scale(distance_frame, from_=0.5, to=5.0, 
                                variable=self.max_distance, orient="horizontal",
                                bg='#3b3b3b', fg='white', highlightbackground='#3b3b3b')
        distance_scale.pack(side="right", fill="x", expand=True, padx=5)
        
        # Reset button
        reset_btn = tk.Button(hand_frame, text="Reset Hand Position", 
                            command=self.reset_hand_position,
                            bg='#FF9800', fg='white', 
                            font=('Arial', 12, 'bold'))
        reset_btn.pack(pady=10)
        
        # Status frame
        status_frame = tk.LabelFrame(parent, text="Status", 
                                   font=('Arial', 16, 'bold'),
                                   bg='#3b3b3b', fg='white')
        status_frame.pack(fill="x", padx=10, pady=10)
        
        # Status labels
        self.camera_status_label = tk.Label(status_frame, text="Camera: Stopped",
                                          bg='#3b3b3b', fg='white')
        self.camera_status_label.pack(pady=2)
        
        self.fps_label = tk.Label(status_frame, text="FPS: 0",
                                 bg='#3b3b3b', fg='white')
        self.fps_label.pack(pady=2)
        
        self.faces_label = tk.Label(status_frame, text="Faces: 0",
                                   bg='#3b3b3b', fg='white')
        self.faces_label.pack(pady=2)
        
        self.hand_status_label = tk.Label(status_frame, text="Hand: IDLE",
                                         bg='#3b3b3b', fg='white')
        self.hand_status_label.pack(pady=2)
        
    def setup_video_display(self, parent):
        """Setup video display panel"""
        # Video frame
        self.video_frame = tk.Frame(parent, bg='#3b3b3b')
        self.video_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Video label
        self.video_label = tk.Label(self.video_frame, text="Click 'Start Camera' to begin",
                                   bg='#3b3b3b', fg='white', font=('Arial', 14))
        self.video_label.pack(expand=True)
        
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
            self.start_stop_btn.configure(text="Stop Camera", bg='#f44336')
            self.camera_status_label.configure(text="Camera: Running")
            
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
        self.camera_status_label.configure(text="Camera: Stopped")
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
            
            # Update status
            self.update_status()
            
            # Small delay
            time.sleep(0.03)  # ~30 FPS
    
    def process_frame(self, frame):
        """Process a single frame"""
        # Detect faces
        self.detected_faces = self.detect_faces(frame)
        
        # Update robot hand
        self.update_robot_hand(frame)
        
        # Draw everything
        self.draw_robot_hand(frame)
        self.draw_faces(frame)
        self.draw_performance_info(frame)
        
        return frame
    
    def detect_faces(self, frame):
        """Detect faces in the frame"""
        faces = []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected_faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in detected_faces:
                face_info = {
                    'center': (x + w // 2, y + h // 2),
                    'rect': (x, y, w, h),
                    'size': (w, h)
                }
                faces.append(face_info)
        except Exception as e:
            print(f"Face detection error: {e}")
        
        return faces
    
    def update_robot_hand(self, frame):
        """Update robot hand position based on detected faces"""
        if not self.detected_faces:
            return
        
        # Find closest face
        closest_face = None
        min_distance = float('inf')
        
        for face in self.detected_faces:
            center = face['center']
            width_pixels = face['size'][0]
            distance = self.calculate_distance(width_pixels)
            
            if distance < min_distance and distance < self.max_distance.get():
                min_distance = distance
                closest_face = face
        
        if closest_face:
            self.update_target(closest_face['center'], min_distance)
    
    def calculate_distance(self, object_width_pixels: float, 
                         known_width_meters: float = 0.1) -> float:
        """Calculate distance to object based on its size"""
        if object_width_pixels <= 0:
            return float('inf')
        distance = (known_width_meters * 1000.0) / object_width_pixels
        return min(distance, self.max_distance.get())
    
    def update_target(self, target_center, distance):
        """Update robot hand target position"""
        center_x, center_y = 320, 240
        dx = target_center[0] - center_x
        dy = target_center[1] - center_y
        distance_from_center = math.sqrt(dx*dx + dy*dy)
        
        max_reach = self.max_reach.get()
        if distance_from_center > max_reach:
            scale = max_reach / distance_from_center
            target_x = center_x + dx * scale
            target_y = center_y + dy * scale
        else:
            target_x, target_y = target_center
        
        self.target_position = (int(target_x), int(target_y))
        self.is_moving = True
    
    def update_hand_position(self):
        """Update robot hand position towards target"""
        if not self.is_moving:
            return
        
        dx = self.target_position[0] - self.hand_position[0]
        dy = self.target_position[1] - self.hand_position[1]
        total_distance = math.sqrt(dx*dx + dy*dy)
        
        if total_distance <= 0:
            self.is_moving = False
            return
        
        movement_distance = self.movement_speed.get() * 100
        progress = min(movement_distance / total_distance, 1.0)
        new_x = self.hand_position[0] + dx * progress
        new_y = self.hand_position[1] + dy * progress
        
        self.hand_position = (int(new_x), int(new_y))
        
        if progress >= 1.0:
            self.is_moving = False
    
    def draw_robot_hand(self, frame):
        """Draw robot hand on frame"""
        hand_size = self.hand_size.get()
        hand_color = (0, 255, 0)  # Green
        
        # Draw hand base (circle)
        cv2.circle(frame, self.hand_position, hand_size // 2, hand_color, 3)
        
        # Draw hand fingers (lines)
        finger_length = hand_size // 3
        finger_angles = [0, 45, -45, 90, -90]
        
        for angle in finger_angles:
            angle_rad = math.radians(angle)
            end_x = int(self.hand_position[0] + finger_length * math.cos(angle_rad))
            end_y = int(self.hand_position[1] + finger_length * math.sin(angle_rad))
            
            cv2.line(frame, self.hand_position, (end_x, end_y), hand_color, 2)
        
        # Draw target if moving
        if self.is_moving:
            cv2.circle(frame, self.target_position, 10, (0, 0, 255), 2)
            cv2.line(frame, self.hand_position, self.target_position, (0, 0, 255), 2)
    
    def draw_faces(self, frame):
        """Draw detected faces on frame"""
        for face in self.detected_faces:
            center = face['center']
            x, y, w, h = face['rect']
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Calculate and draw distance
            width_pixels = face['size'][0]
            distance = self.calculate_distance(width_pixels)
            distance_text = f"{distance:.2f}m"
            cv2.putText(frame, distance_text, 
                       (center[0] + 10, center[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw face label
            cv2.putText(frame, "FACE", 
                       (center[0] - 20, center[1] + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
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
        cv2.putText(frame, f"Faces: {len(self.detected_faces)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Robot hand status
        status = "MOVING" if self.is_moving else "IDLE"
        cv2.putText(frame, f"Robot Hand: {status}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def update_video_display(self, frame):
        """Update video display in GUI"""
        try:
            # Convert frame to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame to fit display
            height, width = frame_rgb.shape[:2]
            max_width = 600
            max_height = 400
            
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
    
    def update_status(self):
        """Update status labels"""
        try:
            self.fps_label.configure(text=f"FPS: {self.current_fps:.1f}")
            self.faces_label.configure(text=f"Faces: {len(self.detected_faces)}")
            
            status = "MOVING" if self.is_moving else "IDLE"
            self.hand_status_label.configure(text=f"Hand: {status}")
            
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def reset_hand_position(self):
        """Reset robot hand to center position"""
        self.hand_position = (320, 240)
        self.is_moving = False
    
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
    print("Starting Robot Hand GUI Application (Simple Version)...")
    
    try:
        app = RobotHandGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main() 