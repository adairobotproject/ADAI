#!/usr/bin/env python3
"""
Quick Cup Detection Script
==========================

A simplified script for quick cup/glass detection testing.
This script provides basic cup detection capabilities for rapid testing.

Features:
- Quick cup detection with multiple methods
- Real-time visualization
- Basic performance metrics
- Simple interface

Author: AI Assistant
Date: 2024
"""

import cv2
import numpy as np
import time
import math

class QuickCupDetector:
    """Quick cup detector with basic functionality."""
    
    def __init__(self):
        # Basic parameters
        self.min_area = 1000
        self.max_area = 50000
        self.min_circularity = 0.6
        self.min_rectangularity = 0.7
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
    
    def detect_cups(self, frame):
        """Detect cups using contour analysis."""
        cups = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by area
                if area < self.min_area or area > self.max_area:
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Filter by aspect ratio (cups are usually taller than wide)
                if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                    continue
                
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                circularity = 4 * math.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                
                # Calculate rectangularity
                rect_area = w * h
                rectangularity = area / rect_area if rect_area > 0 else 0
                
                # Check if it looks like a cup
                if (circularity > self.min_circularity or 
                    rectangularity > self.min_rectangularity):
                    
                    cup_info = {
                        'center': (x + w // 2, y + h // 2),
                        'bbox': (x, y, w, h),
                        'area': area,
                        'circularity': circularity,
                        'rectangularity': rectangularity
                    }
                    cups.append(cup_info)
                    
        except Exception as e:
            print(f"Cup detection error: {e}")
        
        return cups
    
    def detect_cups_by_color(self, frame):
        """Detect cups using color analysis."""
        cups = []
        
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create mask for cup colors (various colors)
            lower = np.array([0, 50, 50])
            upper = np.array([180, 255, 255])
            
            mask = cv2.inRange(hsv, lower, upper)
            
            # Apply morphological operations
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if area < self.min_area:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                    continue
                
                cup_info = {
                    'center': (x + w // 2, y + h // 2),
                    'bbox': (x, y, w, h),
                    'area': area,
                    'method': 'color'
                }
                cups.append(cup_info)
                
        except Exception as e:
            print(f"Color detection error: {e}")
        
        return cups
    
    def draw_cups(self, frame, cups):
        """Draw detected cups on frame."""
        for cup in cups:
            center = cup['center']
            
            # Draw bounding box
            if 'bbox' in cup:
                x, y, w, h = cup['bbox']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(frame, center, 5, (255, 0, 0), -1)
            
            # Draw cup label
            method = cup.get('method', 'contour')
            cv2.putText(frame, f"Vaso ({method})", 
                       (center[0] - 30, center[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw area info
            if 'area' in cup:
                area_text = f"Area: {cup['area']:.0f}"
                cv2.putText(frame, area_text, 
                           (center[0] - 30, center[1] + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def quick_cup_detection_test(self, camera_index=0, duration=30):
        """Quick cup detection test."""
        print(f"Quick Cup Detection Test")
        print(f"Camera: {camera_index}")
        print(f"Duration: {duration} seconds")
        print("Press 'q' to quit")
        
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_index}")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                start_process = time.time()
                
                # Detect cups using both methods
                contour_cups = self.detect_cups(frame)
                color_cups = self.detect_cups_by_color(frame)
                
                # Combine detections (simple merge)
                all_cups = contour_cups + color_cups
                
                # Remove duplicates (simple approach)
                unique_cups = []
                for cup in all_cups:
                    is_duplicate = False
                    for existing_cup in unique_cups:
                        distance = math.sqrt(
                            (cup['center'][0] - existing_cup['center'][0])**2 +
                            (cup['center'][1] - existing_cup['center'][1])**2
                        )
                        if distance < 50:  # 50 pixels threshold
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        unique_cups.append(cup)
                
                # Draw detections
                frame = self.draw_cups(frame, unique_cups)
                
                processing_time = time.time() - start_process
                
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
                cv2.putText(frame, f"Vasos: {len(unique_cups)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Tiempo: {processing_time*1000:.1f}ms", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show frame
                cv2.imshow('Detección de Vasos', frame)
                
                # Check duration
                if time.time() - start_time > duration:
                    break
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()

def main():
    """Main function."""
    print("Quick Cup Detection")
    print("="*25)
    
    detector = QuickCupDetector()
    
    while True:
        print("\nSelect an option:")
        print("1. Quick Cup Detection Test")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == '1':
            camera_index = int(input("Enter camera index (default 0): ") or "0")
            duration = int(input("Enter test duration in seconds (default 30): ") or "30")
            detector.quick_cup_detection_test(camera_index, duration)
            
        elif choice == '2':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please enter 1-2.")

if __name__ == "__main__":
    main() 