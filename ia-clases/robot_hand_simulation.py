#!/usr/bin/env python3
"""
Robot Hand Simulation with Distance Analysis
===========================================

This script provides comprehensive distance analysis and robot hand movement
simulation using computer vision. It can detect objects, calculate distances,
and simulate robot hand movement with visual feedback.

Features:
- Distance calculation using camera calibration
- Object detection and tracking
- Robot hand movement simulation with lines
- Real-time distance analysis
- Multiple detection modes (QR codes, objects, faces)
- Visual feedback with robot hand representation
- Performance metrics and logging

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
from dataclasses import dataclass
import logging

# Try to import pyzbar for QR code detection
try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    print("Warning: pyzbar not available. Install with: pip install pyzbar")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RobotHandConfig:
    """Configuration for robot hand simulation."""
    # Camera calibration parameters (pixels per meter at reference distance)
    pixels_per_meter: float = 1000.0  # Adjust based on your camera setup
    reference_distance: float = 1.0    # Reference distance in meters
    
    # Robot hand parameters
    hand_size: int = 100
    hand_color: Tuple[int, int, int] = (0, 255, 0)  # Green
    hand_thickness: int = 3
    
    # Movement parameters
    movement_speed: float = 0.1  # meters per second
    max_reach: float = 0.5       # maximum reach in meters
    
    # Detection parameters
    min_object_size: int = 50
    max_distance: float = 2.0    # maximum detection distance in meters

class DistanceAnalyzer:
    """Analyzes distances using computer vision techniques."""
    
    def __init__(self, config: RobotHandConfig):
        self.config = config
        self.calibration_data = {}
        self.load_calibration()
    
    def load_calibration(self):
        """Load camera calibration data if available."""
        try:
            if os.path.exists('camera_calibration.json'):
                with open('camera_calibration.json', 'r') as f:
                    self.calibration_data = json.load(f)
                logger.info("Camera calibration data loaded")
        except Exception as e:
            logger.warning(f"Could not load calibration data: {e}")
    
    def save_calibration(self):
        """Save camera calibration data."""
        try:
            with open('camera_calibration.json', 'w') as f:
                json.dump(self.calibration_data, f, indent=2)
            logger.info("Camera calibration data saved")
        except Exception as e:
            logger.error(f"Could not save calibration data: {e}")
    
    def calculate_distance_from_size(self, object_width_pixels: float, 
                                   known_width_meters: float = 0.1) -> float:
        """
        Calculate distance based on known object size.
        
        Args:
            object_width_pixels: Width of object in pixels
            known_width_meters: Known width of object in meters
            
        Returns:
            Distance in meters
        """
        if object_width_pixels <= 0:
            return float('inf')
        
        # Use calibration if available, otherwise use default
        pixels_per_meter = self.calibration_data.get('pixels_per_meter', 
                                                   self.config.pixels_per_meter)
        
        # Calculate distance using similar triangles
        distance = (known_width_meters * pixels_per_meter) / object_width_pixels
        return min(distance, self.config.max_distance)
    
    def calculate_distance_from_position(self, object_center: Tuple[int, int],
                                      image_center: Tuple[int, int],
                                      image_size: Tuple[int, int]) -> float:
        """
        Calculate approximate distance based on object position in image.
        
        Args:
            object_center: Center of object (x, y)
            image_center: Center of image (x, y)
            image_size: Size of image (width, height)
            
        Returns:
            Approximate distance in meters
        """
        # Calculate distance from center (closer to center = closer to camera)
        dx = object_center[0] - image_center[0]
        dy = object_center[1] - image_center[1]
        distance_from_center = math.sqrt(dx*dx + dy*dy)
        
        # Normalize by image size
        max_distance = math.sqrt(image_center[0]*image_center[0] + 
                               image_center[1]*image_center[1])
        normalized_distance = distance_from_center / max_distance
        
        # Convert to meters (approximate)
        distance_meters = normalized_distance * self.config.max_distance
        return min(distance_meters, self.config.max_distance)

class RobotHandSimulator:
    """Simulates robot hand movement and provides visual feedback."""
    
    def __init__(self, config: RobotHandConfig):
        self.config = config
        self.hand_position = (0, 0)  # Current hand position
        self.target_position = (0, 0)  # Target position
        self.is_moving = False
        self.movement_start_time = 0
        
    def update_target(self, target_center: Tuple[int, int], 
                     distance: float, frame_size: Tuple[int, int]):
        """Update target position for robot hand."""
        # Convert distance to movement constraints
        max_reach_pixels = self.config.max_reach * self.config.pixels_per_meter
        
        # Calculate target position considering distance
        target_x = target_center[0]
        target_y = target_center[1]
        
        # Constrain to robot's reach
        center_x, center_y = frame_size[0] // 2, frame_size[1] // 2
        dx = target_x - center_x
        dy = target_y - center_y
        distance_from_center = math.sqrt(dx*dx + dy*dy)
        
        if distance_from_center > max_reach_pixels:
            # Scale down to reach limit
            scale = max_reach_pixels / distance_from_center
            target_x = center_x + dx * scale
            target_y = center_y + dy * scale
        
        self.target_position = (int(target_x), int(target_y))
        self.is_moving = True
        self.movement_start_time = time.time()
    
    def update_hand_position(self, current_time: float):
        """Update hand position based on movement speed."""
        if not self.is_moving:
            return
        
        # Calculate movement progress
        elapsed_time = current_time - self.movement_start_time
        movement_distance = self.config.movement_speed * elapsed_time
        
        # Calculate current position
        dx = self.target_position[0] - self.hand_position[0]
        dy = self.target_position[1] - self.hand_position[1]
        total_distance = math.sqrt(dx*dx + dy*dy)
        
        if total_distance <= 0:
            self.is_moving = False
            return
        
        # Move towards target
        progress = min(movement_distance / total_distance, 1.0)
        new_x = self.hand_position[0] + dx * progress
        new_y = self.hand_position[1] + dy * progress
        
        self.hand_position = (int(new_x), int(new_y))
        
        # Check if reached target
        if progress >= 1.0:
            self.is_moving = False
    
    def draw_robot_hand(self, frame: np.ndarray):
        """Draw robot hand representation on frame."""
        if self.hand_position[0] <= 0 or self.hand_position[1] <= 0:
            return
        
        # Draw hand base (circle)
        cv2.circle(frame, self.hand_position, self.config.hand_size // 2,
                  self.config.hand_color, self.config.hand_thickness)
        
        # Draw hand fingers (lines)
        finger_length = self.config.hand_size // 3
        finger_angles = [0, 45, -45, 90, -90]  # Different finger directions
        
        for angle in finger_angles:
            angle_rad = math.radians(angle)
            end_x = int(self.hand_position[0] + finger_length * math.cos(angle_rad))
            end_y = int(self.hand_position[1] + finger_length * math.sin(angle_rad))
            
            cv2.line(frame, self.hand_position, (end_x, end_y),
                    self.config.hand_color, self.config.hand_thickness // 2)
        
        # Draw target if moving
        if self.is_moving:
            cv2.circle(frame, self.target_position, 10, (0, 0, 255), 2)
            cv2.line(frame, self.hand_position, self.target_position,
                    (0, 0, 255), 2)

class ObjectDetector:
    """Detects various types of objects for distance analysis."""
    
    def __init__(self):
        self.qr_detector = cv2.QRCodeDetector() if PYZBAR_AVAILABLE else None
    
    def detect_qr_codes(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect QR codes in frame."""
        qr_codes = []
        
        # Use pyzbar if available
        if PYZBAR_AVAILABLE:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                decoded_objects = pyzbar.decode(gray)
                
                for obj in decoded_objects:
                    qr_info = {
                        'type': 'qr_code',
                        'data': obj.data.decode('utf-8'),
                        'rect': obj.rect,
                        'center': (obj.rect.left + obj.rect.width // 2,
                                 obj.rect.top + obj.rect.height // 2),
                        'size': (obj.rect.width, obj.rect.height)
                    }
                    qr_codes.append(qr_info)
            except Exception as e:
                logger.error(f"pyzbar error: {e}")
        
        # Use OpenCV QR detector as backup
        try:
            retval, decoded_info, points, straight_qrcode = self.qr_detector.detectAndDecodeMulti(frame)
            
            if retval:
                for i, (info, point) in enumerate(zip(decoded_info, points)):
                    if info:
                        center = (int(np.mean(point[:, 0])), int(np.mean(point[:, 1])))
                        size = (int(np.max(point[:, 0]) - np.min(point[:, 0])),
                               int(np.max(point[:, 1]) - np.min(point[:, 1])))
                        
                        qr_info = {
                            'type': 'qr_code',
                            'data': info,
                            'points': point.astype(int),
                            'center': center,
                            'size': size
                        }
                        qr_codes.append(qr_info)
        except Exception as e:
            logger.error(f"OpenCV QR error: {e}")
        
        return qr_codes
    
    def detect_circles(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect circles in frame."""
        circles = []
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            
            # Detect circles
            detected_circles = cv2.HoughCircles(
                gray, cv2.HOUGH_GRADIENT, 1, 20,
                param1=50, param2=30, minRadius=20, maxRadius=100
            )
            
            if detected_circles is not None:
                detected_circles = np.uint16(np.around(detected_circles))
                
                for circle in detected_circles[0, :]:
                    center = (circle[0], circle[1])
                    radius = circle[2]
                    
                    circle_info = {
                        'type': 'circle',
                        'center': center,
                        'radius': radius,
                        'size': (radius * 2, radius * 2)
                    }
                    circles.append(circle_info)
        except Exception as e:
            logger.error(f"Circle detection error: {e}")
        
        return circles
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces in frame."""
        faces = []
        
        try:
            # Use OpenCV's Haar cascade for face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected_faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in detected_faces:
                center = (x + w // 2, y + h // 2)
                
                face_info = {
                    'type': 'face',
                    'center': center,
                    'rect': (x, y, w, h),
                    'size': (w, h)
                }
                faces.append(face_info)
        except Exception as e:
            logger.error(f"Face detection error: {e}")
        
        return faces

class RobotHandDebugger:
    """Main debugger class for robot hand simulation."""
    
    def __init__(self):
        self.config = RobotHandConfig()
        self.distance_analyzer = DistanceAnalyzer(self.config)
        self.robot_hand = RobotHandSimulator(self.config)
        self.object_detector = ObjectDetector()
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.processing_times = []
        
        # Detection results
        self.detected_objects = []
        self.distances = {}
        
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze frame for objects and distances."""
        start_time = time.time()
        
        # Detect objects
        qr_codes = self.object_detector.detect_qr_codes(frame)
        circles = self.object_detector.detect_circles(frame)
        faces = self.object_detector.detect_faces(frame)
        
        all_objects = qr_codes + circles + faces
        self.detected_objects = all_objects
        
        # Calculate distances
        distances = {}
        frame_center = (frame.shape[1] // 2, frame.shape[0] // 2)
        
        for obj in all_objects:
            # Calculate distance using size-based method
            if 'size' in obj:
                width_pixels = obj['size'][0]
                distance_from_size = self.distance_analyzer.calculate_distance_from_size(width_pixels)
                
                # Calculate distance using position-based method
                distance_from_position = self.distance_analyzer.calculate_distance_from_position(
                    obj['center'], frame_center, (frame.shape[1], frame.shape[0])
                )
                
                # Use average of both methods
                avg_distance = (distance_from_size + distance_from_position) / 2
                distances[obj['type'] + '_' + str(obj['center'])] = avg_distance
                
                # Update robot hand target
                if avg_distance < self.config.max_distance:
                    self.robot_hand.update_target(obj['center'], avg_distance, 
                                               (frame.shape[1], frame.shape[0]))
        
        self.distances = distances
        
        # Update robot hand position
        current_time = time.time()
        self.robot_hand.update_hand_position(current_time)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        self.processing_times.append(processing_time)
        
        return {
            'objects': all_objects,
            'distances': distances,
            'processing_time': processing_time
        }
    
    def draw_analysis(self, frame: np.ndarray, analysis: Dict[str, Any]):
        """Draw analysis results on frame."""
        # Draw robot hand
        self.robot_hand.draw_robot_hand(frame)
        
        # Draw detected objects and distances
        for obj in analysis['objects']:
            center = obj['center']
            obj_type = obj['type']
            
            # Draw bounding box
            if 'rect' in obj:
                x, y, w, h = obj['rect']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            elif 'radius' in obj:
                cv2.circle(frame, center, obj['radius'], (0, 255, 0), 2)
            elif 'points' in obj:
                cv2.polylines(frame, [obj['points']], True, (0, 255, 0), 2)
            
            # Draw distance information
            distance_key = obj_type + '_' + str(center)
            if distance_key in analysis['distances']:
                distance = analysis['distances'][distance_key]
                distance_text = f"{distance:.2f}m"
                cv2.putText(frame, distance_text, 
                           (center[0] + 10, center[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw object type
            cv2.putText(frame, obj_type.upper(), 
                       (center[0] - 20, center[1] + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw performance information
        self.fps_counter += 1
        if time.time() - self.fps_start_time >= 1.0:
            fps = self.fps_counter / (time.time() - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = time.time()
        else:
            fps = 0
        
        # Performance overlay
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Objects: {len(analysis['objects'])}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {analysis['processing_time']*1000:.1f}ms", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Robot hand status
        status = "MOVING" if self.robot_hand.is_moving else "IDLE"
        cv2.putText(frame, f"Robot Hand: {status}", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def test_robot_hand_simulation(self, camera_index: int = 0, duration: int = 30):
        """Test robot hand simulation with distance analysis."""
        print(f"Robot Hand Simulation Test")
        print(f"Camera: {camera_index}")
        print(f"Duration: {duration} seconds")
        print("Press 'q' to quit, 'r' to reset hand position")
        
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
                
                # Analyze frame
                analysis = self.analyze_frame(frame)
                
                # Draw analysis
                self.draw_analysis(frame, analysis)
                
                # Show frame
                cv2.imshow('Robot Hand Simulation', frame)
                
                # Check duration
                if time.time() - start_time > duration:
                    break
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Reset hand position to center
                    self.robot_hand.hand_position = (frame.shape[1] // 2, frame.shape[0] // 2)
                    self.robot_hand.is_moving = False
                    print("Reset hand position")
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def adjust_parameters(self):
        """Adjust robot hand parameters in real-time."""
        def nothing(x):
            pass
        
        # Create trackbar window
        cv2.namedWindow('Robot Hand Parameters')
        cv2.createTrackbar('Hand Size', 'Robot Hand Parameters', 
                          self.config.hand_size, 200, nothing)
        cv2.createTrackbar('Movement Speed', 'Robot Hand Parameters', 
                          int(self.config.movement_speed * 100), 50, nothing)
        cv2.createTrackbar('Max Reach', 'Robot Hand Parameters', 
                          int(self.config.max_reach * 100), 100, nothing)
        cv2.createTrackbar('Max Distance', 'Robot Hand Parameters', 
                          int(self.config.max_distance * 100), 200, nothing)
        
        print("Adjust parameters using trackbars")
        print("Press 'q' to quit parameter adjustment")
        
        while True:
            # Update parameters from trackbars
            self.config.hand_size = cv2.getTrackbarPos('Hand Size', 'Robot Hand Parameters')
            self.config.movement_speed = cv2.getTrackbarPos('Movement Speed', 'Robot Hand Parameters') / 100.0
            self.config.max_reach = cv2.getTrackbarPos('Max Reach', 'Robot Hand Parameters') / 100.0
            self.config.max_distance = cv2.getTrackbarPos('Max Distance', 'Robot Hand Parameters') / 100.0
            
            # Update robot hand config
            self.robot_hand.config = self.config
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cv2.destroyWindow('Robot Hand Parameters')
    
    def save_results(self, filename: str = None):
        """Save analysis results."""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"robot_hand_results_{timestamp}.json"
        
        results = {
            'timestamp': time.time(),
            'config': {
                'hand_size': self.config.hand_size,
                'movement_speed': self.config.movement_speed,
                'max_reach': self.config.max_reach,
                'max_distance': self.config.max_distance
            },
            'performance': {
                'avg_processing_time': np.mean(self.processing_times) if self.processing_times else 0,
                'total_frames': len(self.processing_times)
            },
            'detected_objects': len(self.detected_objects),
            'distances': self.distances
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Results saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

def main():
    """Main function."""
    print("Robot Hand Simulation with Distance Analysis")
    print("="*50)
    
    debugger = RobotHandDebugger()
    
    while True:
        print("\nSelect an option:")
        print("1. Test Robot Hand Simulation")
        print("2. Adjust Parameters")
        print("3. Save Results")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            camera_index = int(input("Enter camera index (default 0): ") or "0")
            duration = int(input("Enter test duration in seconds (default 30): ") or "30")
            debugger.test_robot_hand_simulation(camera_index, duration)
            
        elif choice == '2':
            debugger.adjust_parameters()
            
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