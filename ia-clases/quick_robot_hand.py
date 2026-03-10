#!/usr/bin/env python3
"""
Quick Robot Hand Simulation
===========================

A simplified script for quick robot hand simulation testing with distance analysis.
The robot hand only moves towards detected faces.
"""

import cv2
import numpy as np
import time
import math

class QuickRobotHand:
    def __init__(self):
        self.hand_size = 80
        self.hand_color = (0, 255, 0)  # Green
        self.hand_position = (320, 240)  # Center
        self.target_position = (320, 240)
        self.is_moving = False
        self.movement_speed = 0.1
        self.max_reach = 200  # pixels
        self.max_distance = 2.0  # meters
        self.pixels_per_meter = 1000.0
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
    
    def calculate_distance(self, object_width_pixels: float, 
                         known_width_meters: float = 0.1) -> float:
        if object_width_pixels <= 0:
            return float('inf')
        distance = (known_width_meters * self.pixels_per_meter) / object_width_pixels
        return min(distance, self.max_distance)
    
    def update_target(self, target_center, distance):
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
    
    def update_hand_position(self):
        if not self.is_moving:
            return
        
        dx = self.target_position[0] - self.hand_position[0]
        dy = self.target_position[1] - self.hand_position[1]
        total_distance = math.sqrt(dx*dx + dy*dy)
        
        if total_distance <= 0:
            self.is_moving = False
            return
        
        movement_distance = self.movement_speed * 100
        progress = min(movement_distance / total_distance, 1.0)
        new_x = self.hand_position[0] + dx * progress
        new_y = self.hand_position[1] + dy * progress
        
        self.hand_position = (int(new_x), int(new_y))
        
        if progress >= 1.0:
            self.is_moving = False
    
    def draw_robot_hand(self, frame):
        # Draw hand base (circle)
        cv2.circle(frame, self.hand_position, self.hand_size // 2,
                  self.hand_color, 3)
        
        # Draw hand fingers (lines)
        finger_length = self.hand_size // 3
        finger_angles = [0, 45, -45, 90, -90]
        
        for angle in finger_angles:
            angle_rad = math.radians(angle)
            end_x = int(self.hand_position[0] + finger_length * math.cos(angle_rad))
            end_y = int(self.hand_position[1] + finger_length * math.sin(angle_rad))
            
            cv2.line(frame, self.hand_position, (end_x, end_y),
                    self.hand_color, 2)
        
        # Draw target if moving
        if self.is_moving:
            cv2.circle(frame, self.target_position, 10, (0, 0, 255), 2)
            cv2.line(frame, self.hand_position, self.target_position,
                    (0, 0, 255), 2)
    
    def detect_objects(self, frame):
        objects = []
        
        # Detect faces only
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected_faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in detected_faces:
                obj_info = {
                    'type': 'face',
                    'center': (x + w // 2, y + h // 2),
                    'rect': (x, y, w, h),
                    'size': (w, h)
                }
                objects.append(obj_info)
        except Exception as e:
            print(f"Face detection error: {e}")
        
        return objects
    
    def draw_objects_and_distances(self, frame, objects):
        for obj in objects:
            center = obj['center']
            obj_type = obj['type']
            
            # Draw bounding box for faces
            if 'rect' in obj:
                x, y, w, h = obj['rect']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Calculate and draw distance
            if 'size' in obj:
                width_pixels = obj['size'][0]
                distance = self.calculate_distance(width_pixels)
                distance_text = f"{distance:.2f}m"
                cv2.putText(frame, distance_text, 
                           (center[0] + 10, center[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw object type
            cv2.putText(frame, obj_type.upper(), 
                       (center[0] - 20, center[1] + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Update robot hand target (only for faces)
            if obj_type == 'face' and 'size' in obj:
                width_pixels = obj['size'][0]
                distance = self.calculate_distance(width_pixels)
                if distance < self.max_distance:
                    self.update_target(center, distance)
    
    def quick_robot_hand_test(self, camera_index=0, duration=30):
        print(f"Quick Robot Hand Simulation Test")
        print(f"Camera: {camera_index}")
        print(f"Duration: {duration} seconds")
        print("Press 'q' to quit, 'r' to reset hand position")
        print("Robot hand will only move towards detected faces")
        
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_index}")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                # Detect objects (faces only)
                objects = self.detect_objects(frame)
                
                # Draw objects and distances
                self.draw_objects_and_distances(frame, objects)
                
                # Update robot hand position
                self.update_hand_position()
                
                # Draw robot hand
                self.draw_robot_hand(frame)
                
                # Draw performance information
                self.fps_counter += 1
                if time.time() - self.fps_start_time >= 1.0:
                    fps = self.fps_counter / (time.time() - self.fps_start_time)
                    self.fps_counter = 0
                    self.fps_start_time = time.time()
                else:
                    fps = 0
                
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Faces: {len(objects)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Robot hand status
                status = "MOVING" if self.is_moving else "IDLE"
                cv2.putText(frame, f"Robot Hand: {status}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show frame
                cv2.imshow('Quick Robot Hand Simulation - Face Detection Only', frame)
                
                # Check duration
                if time.time() - start_time > duration:
                    break
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.hand_position = (320, 240)
                    self.is_moving = False
                    print("Reset hand position")
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()

def main():
    print("Quick Robot Hand Simulation - Face Detection Only")
    print("="*50)
    
    robot_hand = QuickRobotHand()
    
    while True:
        print("\nSelect an option:")
        print("1. Quick Robot Hand Simulation (Faces Only)")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == '1':
            camera_index = int(input("Enter camera index (default 0): ") or "0")
            duration = int(input("Enter test duration in seconds (default 30): ") or "30")
            robot_hand.quick_robot_hand_test(camera_index, duration)
            
        elif choice == '2':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please enter 1-2.")

if __name__ == "__main__":
    main() 