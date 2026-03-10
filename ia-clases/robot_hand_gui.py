#!/usr/bin/env python3
"""
Robot Hand GUI Application
==========================

A modern GUI application for robot hand simulation with face detection
using CustomTkinter for a professional interface.
"""

import cv2
import numpy as np
import time
import math
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RobotHandGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Robot Hand Simulation - Face Detection")
        self.root.geometry("1200x800")
        
        # Robot hand parameters
        self.hand_size = ctk.IntVar(value=80)
        self.movement_speed = ctk.DoubleVar(value=0.1)
        self.max_reach = ctk.IntVar(value=200)
        self.max_distance = ctk.DoubleVar(value=2.0)
        
        # Camera parameters
        self.camera_index = ctk.IntVar(value=0)
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
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Robot Hand Simulation", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=10)
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (controls)
        left_panel = ctk.CTkFrame(content_frame, width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel (video)
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.setup_controls(left_panel)
        self.setup_video_display(right_panel)
        
    def setup_controls(self, parent):
        """Setup control panel"""
        # Camera controls
        camera_frame = ctk.CTkFrame(parent)
        camera_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(camera_frame, text="Camera Controls", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Camera index
        camera_index_frame = ctk.CTkFrame(camera_frame)
        camera_index_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(camera_index_frame, text="Camera Index:").pack(side="left")
        camera_index_entry = ctk.CTkEntry(camera_index_frame, textvariable=self.camera_index, width=50)
        camera_index_entry.pack(side="right", padx=5)
        
        # Start/Stop button
        self.start_stop_btn = ctk.CTkButton(camera_frame, text="Start Camera", 
                                           command=self.toggle_camera)
        self.start_stop_btn.pack(pady=10)
        
        # Robot hand controls
        hand_frame = ctk.CTkFrame(parent)
        hand_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(hand_frame, text="Robot Hand Controls", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Hand size
        hand_size_frame = ctk.CTkFrame(hand_frame)
        hand_size_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(hand_size_frame, text="Hand Size:").pack(side="left")
        hand_size_slider = ctk.CTkSlider(hand_size_frame, from_=20, to=150, 
                                        variable=self.hand_size, number_of_steps=130)
        hand_size_slider.pack(side="right", fill="x", expand=True, padx=5)
        
        # Movement speed
        speed_frame = ctk.CTkFrame(hand_frame)
        speed_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(speed_frame, text="Speed:").pack(side="left")
        speed_slider = ctk.CTkSlider(speed_frame, from_=0.01, to=0.5, 
                                    variable=self.movement_speed, number_of_steps=49)
        speed_slider.pack(side="right", fill="x", expand=True, padx=5)
        
        # Max reach
        reach_frame = ctk.CTkFrame(hand_frame)
        reach_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(reach_frame, text="Max Reach:").pack(side="left")
        reach_slider = ctk.CTkSlider(reach_frame, from_=50, to=400, 
                                    variable=self.max_reach, number_of_steps=350)
        reach_slider.pack(side="right", fill="x", expand=True, padx=5)
        
        # Max distance
        distance_frame = ctk.CTkFrame(hand_frame)
        distance_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(distance_frame, text="Max Distance:").pack(side="left")
        distance_slider = ctk.CTkSlider(distance_frame, from_=0.5, to=5.0, 
                                       variable=self.max_distance, number_of_steps=45)
        distance_slider.pack(side="right", fill="x", expand=True, padx=5)
        
        # Reset button
        reset_btn = ctk.CTkButton(hand_frame, text="Reset Hand Position", 
                                 command=self.reset_hand_position)
        reset_btn.pack(pady=10)
        
        # Status frame
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(status_frame, text="Status", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Status labels
        self.camera_status_label = ctk.CTkLabel(status_frame, text="Camera: Stopped")
        self.camera_status_label.pack(pady=2)
        
        self.fps_label = ctk.CTkLabel(status_frame, text="FPS: 0")
        self.fps_label.pack(pady=2)
        
        self.faces_label = ctk.CTkLabel(status_frame, text="Faces: 0")
        self.faces_label.pack(pady=2)
        
        self.hand_status_label = ctk.CTkLabel(status_frame, text="Hand: IDLE")
        self.hand_status_label.pack(pady=2)
        
    def setup_video_display(self, parent):
        """Setup video display panel"""
        # Video frame
        self.video_frame = ctk.CTkFrame(parent)
        self.video_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Video label
        self.video_label = ctk.CTkLabel(self.video_frame, text="Click 'Start Camera' to begin")
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
            self.start_stop_btn.configure(text="Stop Camera")
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
        
        self.start_stop_btn.configure(text="Start Camera")
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
            
            # Convert to PhotoImage
            frame_pil = tk.PhotoImage(data=cv2.imencode('.ppm', frame_rgb)[1].tobytes())
            
            # Update label
            self.video_label.configure(image=frame_pil, text="")
            self.video_label.image = frame_pil  # Keep a reference
            
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
    print("Starting Robot Hand GUI Application...")
    
    try:
        app = RobotHandGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main() 