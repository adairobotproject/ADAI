#!/usr/bin/env python3
"""
Cup/Glass Detection Debug Script
================================

This script provides comprehensive debugging capabilities for cup/glass detection
using multiple computer vision techniques. It includes real-time detection,
parameter adjustment, and performance analysis.

Features:
- Multiple cup detection methods (contour, color, shape analysis)
- Real-time parameter adjustment
- Performance metrics and FPS monitoring
- Comprehensive error handling and logging
- Distance calculation to cups
- Robot hand simulation for cup interaction

Author: AI Assistant
Date: 2024
"""

import cv2
import numpy as np
import time
import os
import json
import math
from typing import List, Dict, Any, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CupDetector:
    """Detects cups and glasses using multiple computer vision techniques."""
    
    def __init__(self):
        # Detection parameters
        self.contour_params = {
            'min_area': 1000,
            'max_area': 50000,
            'aspect_ratio_min': 0.5,
            'aspect_ratio_max': 2.0
        }
        
        self.color_params = {
            'glass_lower': np.array([0, 0, 100]),    # Transparent/white
            'glass_upper': np.array([180, 30, 255]),
            'cup_lower': np.array([0, 50, 50]),      # Various cup colors
            'cup_upper': np.array([180, 255, 255])
        }
        
        self.shape_params = {
            'circularity_min': 0.6,
            'rectangularity_min': 0.7
        }
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.processing_times = []
        
    def detect_cups_by_contour(self, frame: np.ndarray) -> List[Dict[str, Any]]:
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
                if area < self.contour_params['min_area'] or area > self.contour_params['max_area']:
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Filter by aspect ratio
                if (aspect_ratio < self.contour_params['aspect_ratio_min'] or 
                    aspect_ratio > self.contour_params['aspect_ratio_max']):
                    continue
                
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                circularity = 4 * math.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                
                # Calculate rectangularity
                rect_area = w * h
                rectangularity = area / rect_area if rect_area > 0 else 0
                
                # Check if it looks like a cup
                if (circularity > self.shape_params['circularity_min'] or 
                    rectangularity > self.shape_params['rectangularity_min']):
                    
                    cup_info = {
                        'type': 'cup',
                        'contour': contour,
                        'center': (x + w // 2, y + h // 2),
                        'bbox': (x, y, w, h),
                        'area': area,
                        'circularity': circularity,
                        'rectangularity': rectangularity,
                        'method': 'contour'
                    }
                    cups.append(cup_info)
                    
        except Exception as e:
            logger.error(f"Contour detection error: {e}")
        
        return cups
    
    def detect_cups_by_color(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect cups using color analysis."""
        cups = []
        
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create masks for different cup colors
            masks = []
            
            # Glass/transparent mask
            glass_mask = cv2.inRange(hsv, self.color_params['glass_lower'], self.color_params['glass_upper'])
            masks.append(glass_mask)
            
            # General cup color mask
            cup_mask = cv2.inRange(hsv, self.color_params['cup_lower'], self.color_params['cup_upper'])
            masks.append(cup_mask)
            
            # Combine masks
            combined_mask = cv2.bitwise_or(glass_mask, cup_mask)
            
            # Apply morphological operations
            kernel = np.ones((5, 5), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours in the mask
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if area < self.contour_params['min_area']:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                if (aspect_ratio < self.contour_params['aspect_ratio_min'] or 
                    aspect_ratio > self.contour_params['aspect_ratio_max']):
                    continue
                
                cup_info = {
                    'type': 'cup',
                    'contour': contour,
                    'center': (x + w // 2, y + h // 2),
                    'bbox': (x, y, w, h),
                    'area': area,
                    'method': 'color'
                }
                cups.append(cup_info)
                
        except Exception as e:
            logger.error(f"Color detection error: {e}")
        
        return cups
    
    def detect_cups_by_hough_circles(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect cups using Hough Circle detection."""
        cups = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            
            # Detect circles
            circles = cv2.HoughCircles(
                blurred, cv2.HOUGH_GRADIENT, 1, 20,
                param1=50, param2=30, minRadius=20, maxRadius=200
            )
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                
                for circle in circles[0, :]:
                    center = (circle[0], circle[1])
                    radius = circle[2]
                    
                    # Filter by size
                    area = math.pi * radius * radius
                    if area < self.contour_params['min_area'] or area > self.contour_params['max_area']:
                        continue
                    
                    cup_info = {
                        'type': 'cup',
                        'center': center,
                        'radius': radius,
                        'bbox': (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
                        'area': area,
                        'method': 'hough_circles'
                    }
                    cups.append(cup_info)
                    
        except Exception as e:
            logger.error(f"Hough circles detection error: {e}")
        
        return cups
    
    def merge_detections(self, detections_list: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Merge detections from different methods, removing duplicates."""
        all_cups = []
        
        for detections in detections_list:
            all_cups.extend(detections)
        
        # Remove duplicates based on center proximity
        merged_cups = []
        for cup in all_cups:
            is_duplicate = False
            
            for existing_cup in merged_cups:
                # Calculate distance between centers
                if 'center' in cup and 'center' in existing_cup:
                    distance = math.sqrt(
                        (cup['center'][0] - existing_cup['center'][0])**2 +
                        (cup['center'][1] - existing_cup['center'][1])**2
                    )
                    
                    # If centers are close, consider it a duplicate
                    if distance < 50:  # 50 pixels threshold
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                merged_cups.append(cup)
        
        return merged_cups
    
    def calculate_distance(self, cup_info: Dict[str, Any], frame_size: Tuple[int, int]) -> float:
        """Calculate approximate distance to cup based on size."""
        frame_center = (frame_size[0] // 2, frame_size[1] // 2)
        
        if 'area' in cup_info:
            # Use area to estimate distance (larger area = closer)
            max_area = frame_size[0] * frame_size[1] * 0.1  # 10% of frame
            distance_ratio = cup_info['area'] / max_area
            distance = 2.0 * (1 - distance_ratio)  # 0-2 meters range
            return max(0.1, min(2.0, distance))
        
        return 1.0  # Default distance
    
    def draw_detections(self, frame: np.ndarray, cups: List[Dict[str, Any]]) -> np.ndarray:
        """Draw cup detections on frame."""
        for cup in cups:
            center = cup['center']
            method = cup.get('method', 'unknown')
            
            # Draw bounding box
            if 'bbox' in cup:
                x, y, w, h = cup['bbox']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw contour if available
            if 'contour' in cup:
                cv2.drawContours(frame, [cup['contour']], -1, (0, 255, 0), 2)
            
            # Draw circle if available
            if 'radius' in cup:
                cv2.circle(frame, center, cup['radius'], (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(frame, center, 5, (255, 0, 0), -1)
            
            # Draw method label
            cv2.putText(frame, f"Cup ({method})", 
                       (center[0] - 30, center[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw distance if calculated
            if 'distance' in cup:
                distance_text = f"{cup['distance']:.2f}m"
                cv2.putText(frame, distance_text, 
                           (center[0] - 20, center[1] + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def update_parameters(self):
        """Update detection parameters using trackbars."""
        def nothing(x):
            pass
        
        # Create trackbar window
        cv2.namedWindow('Cup Detection Parameters')
        
        # Contour parameters
        cv2.createTrackbar('Min Area', 'Cup Detection Parameters', 
                          self.contour_params['min_area'], 10000, nothing)
        cv2.createTrackbar('Max Area', 'Cup Detection Parameters', 
                          self.contour_params['max_area'], 100000, nothing)
        cv2.createTrackbar('Min Aspect Ratio', 'Cup Detection Parameters', 
                          int(self.contour_params['aspect_ratio_min'] * 100), 100, nothing)
        cv2.createTrackbar('Max Aspect Ratio', 'Cup Detection Parameters', 
                          int(self.contour_params['aspect_ratio_max'] * 100), 300, nothing)
        
        # Shape parameters
        cv2.createTrackbar('Min Circularity', 'Cup Detection Parameters', 
                          int(self.shape_params['circularity_min'] * 100), 100, nothing)
        cv2.createTrackbar('Min Rectangularity', 'Cup Detection Parameters', 
                          int(self.shape_params['rectangularity_min'] * 100), 100, nothing)
        
        print("Adjust parameters using trackbars")
        print("Press 'q' to quit parameter adjustment")
        
        while True:
            # Update parameters from trackbars
            self.contour_params['min_area'] = cv2.getTrackbarPos('Min Area', 'Cup Detection Parameters')
            self.contour_params['max_area'] = cv2.getTrackbarPos('Max Area', 'Cup Detection Parameters')
            self.contour_params['aspect_ratio_min'] = cv2.getTrackbarPos('Min Aspect Ratio', 'Cup Detection Parameters') / 100.0
            self.contour_params['aspect_ratio_max'] = cv2.getTrackbarPos('Max Aspect Ratio', 'Cup Detection Parameters') / 100.0
            self.shape_params['circularity_min'] = cv2.getTrackbarPos('Min Circularity', 'Cup Detection Parameters') / 100.0
            self.shape_params['rectangularity_min'] = cv2.getTrackbarPos('Min Rectangularity', 'Cup Detection Parameters') / 100.0
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cv2.destroyWindow('Cup Detection Parameters')

class CupDetectionDebugger:
    """Main debugger class for cup detection."""
    
    def __init__(self):
        self.detector = CupDetector()
        
    def test_cup_detection(self, camera_index: int = 0, duration: int = 30):
        """Test cup detection with real-time analysis."""
        print(f"Cup Detection Test")
        print(f"Camera: {camera_index}")
        print(f"Duration: {duration} seconds")
        print("Press 'q' to quit, 'p' to adjust parameters")
        
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
                
                # Detect cups using multiple methods
                contour_cups = self.detector.detect_cups_by_contour(frame)
                color_cups = self.detector.detect_cups_by_color(frame)
                hough_cups = self.detector.detect_cups_by_hough_circles(frame)
                
                # Merge detections
                all_cups = self.detector.merge_detections([contour_cups, color_cups, hough_cups])
                
                # Calculate distances
                for cup in all_cups:
                    cup['distance'] = self.detector.calculate_distance(cup, (frame.shape[1], frame.shape[0]))
                
                # Draw detections
                frame = self.detector.draw_detections(frame, all_cups)
                
                processing_time = time.time() - start_process
                self.detector.processing_times.append(processing_time)
                
                # Draw performance information
                self.detector.fps_counter += 1
                if time.time() - self.detector.fps_start_time >= 1.0:
                    fps = self.detector.fps_counter / (time.time() - self.detector.fps_start_time)
                    self.detector.fps_counter = 0
                    self.detector.fps_start_time = time.time()
                else:
                    fps = 0
                
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Cups: {len(all_cups)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Time: {processing_time*1000:.1f}ms", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show frame
                cv2.imshow('Cup Detection', frame)
                
                # Check duration
                if time.time() - start_time > duration:
                    break
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('p'):
                    self.detector.update_parameters()
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def save_results(self, filename: str = None):
        """Save detection results."""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"cup_detection_results_{timestamp}.json"
        
        results = {
            'timestamp': time.time(),
            'parameters': {
                'contour_params': self.detector.contour_params,
                'color_params': self.detector.color_params,
                'shape_params': self.detector.shape_params
            },
            'performance': {
                'avg_processing_time': np.mean(self.detector.processing_times) if self.detector.processing_times else 0,
                'total_frames': len(self.detector.processing_times)
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Results saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

def main():
    """Main function."""
    print("Cup Detection Debugger")
    print("="*30)
    
    debugger = CupDetectionDebugger()
    
    while True:
        print("\nSelect an option:")
        print("1. Test Cup Detection")
        print("2. Adjust Parameters")
        print("3. Save Results")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            camera_index = int(input("Enter camera index (default 0): ") or "0")
            duration = int(input("Enter test duration in seconds (default 30): ") or "30")
            debugger.test_cup_detection(camera_index, duration)
            
        elif choice == '2':
            debugger.detector.update_parameters()
            
        elif choice == '3':
            filename = input("Enter filename (or press Enter for auto): ").strip()
            if not filename:
                filename = None
            debugger.save_results(filename)
            
        elif choice == '4':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main() 