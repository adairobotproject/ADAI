#!/usr/bin/env python3
"""
QR Code Detection Debug Script
==============================

This script provides comprehensive debugging capabilities for QR code detection
with optional filtering by orange sheets. It includes camera diagnostics,
real-time QR code detection, and parameter adjustment tools.

Features:
- Camera diagnostics and performance testing
- QR code detection with OpenCV and pyzbar
- Optional filtering by orange sheet detection
- Real-time parameter adjustment
- Performance metrics and FPS monitoring
- Comprehensive error handling and logging

Author: AI Assistant
Date: 2024
"""

import cv2
import numpy as np
import time
import os
import sys
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
import logging

# Try to import pyzbar for QR code detection
try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    print("Warning: pyzbar not available. Install with: pip install pyzbar")
    print("QR code detection will be limited to OpenCV's QR code detector.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qr_detection_debug.log'),
        logging.StreamHandler()
    ]
)

class QRCodeDetectionDebugger:
    """
    Comprehensive QR code detection debugger with camera diagnostics
    and real-time parameter adjustment capabilities.
    """
    
    def __init__(self):
        """Initialize the QR code detection debugger."""
        self.camera = None
        self.is_running = False
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.avg_fps = 0.0
        self.processing_times = []
        
        # QR code detection parameters
        self.qr_detection_params = {
            'use_pyzbar': True,  # Use pyzbar if available
            'use_opencv_qr': True,  # Use OpenCV QR detector as backup
            'min_confidence': 0.5,  # Minimum confidence for OpenCV QR detector
            'scale_factor': 1.0,  # Scale factor for image processing
        }
        
        # Orange sheet detection parameters (for filtering)
        self.orange_detection_params = {
            'lower_hsv': np.array([5, 50, 50]),    # Lower HSV for orange
            'upper_hsv': np.array([25, 255, 255]),  # Upper HSV for orange
            'min_area': 1000,                       # Minimum area for orange sheet
            'blur_kernel': 5,                       # Blur kernel size
            'morph_kernel': 3,                      # Morphological kernel size
        }
        
        # Detection results storage
        self.detection_results = {
            'qr_codes': [],
            'orange_sheets': [],
            'filtered_qr_codes': []
        }
        
        # Performance tracking
        self.performance_metrics = {
            'total_frames': 0,
            'detection_frames': 0,
            'avg_processing_time': 0.0,
            'max_processing_time': 0.0,
            'min_processing_time': float('inf')
        }
        
        # Create debug directory
        self.debug_dir = 'debug_results'
        os.makedirs(self.debug_dir, exist_ok=True)
        
        logging.info("QR Code Detection Debugger initialized")
    
    def print_camera_info(self, camera_index: int = 0) -> bool:
        """
        Print detailed camera information and test different backends.
        
        Args:
            camera_index: Index of the camera to test
            
        Returns:
            bool: True if camera is accessible, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"CAMERA DIAGNOSTICS - Camera {camera_index}")
        print(f"{'='*60}")
        
        # Test different camera backends
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_ANY, "Auto-detect")
        ]
        
        camera_working = False
        
        for backend, backend_name in backends:
            print(f"\n--- Testing {backend_name} Backend ---")
            
            try:
                cap = cv2.VideoCapture(camera_index, backend)
                
                if not cap.isOpened():
                    print(f"❌ Failed to open camera with {backend_name}")
                    continue
                
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                backend_id = cap.get(cv2.CAP_PROP_BACKEND)
                
                print(f"✅ Camera opened successfully with {backend_name}")
                print(f"   Resolution: {width}x{height}")
                print(f"   FPS: {fps}")
                print(f"   Backend ID: {backend_id}")
                
                # Test frame capture
                ret, frame = cap.read()
                if ret:
                    print(f"✅ Frame capture successful: {frame.shape}")
                    camera_working = True
                else:
                    print("❌ Frame capture failed")
                
                cap.release()
                
            except Exception as e:
                print(f"❌ Error with {backend_name}: {str(e)}")
        
        if camera_working:
            print(f"\n✅ Camera {camera_index} is working")
        else:
            print(f"\n❌ Camera {camera_index} is not accessible")
        
        return camera_working
    
    def test_qr_detection_libraries(self) -> Dict[str, bool]:
        """
        Test QR code detection libraries and their availability.
        
        Returns:
            Dict containing library availability status
        """
        print(f"\n{'='*60}")
        print("QR CODE DETECTION LIBRARY TEST")
        print(f"{'='*60}")
        
        library_status = {
            'pyzbar': PYZBAR_AVAILABLE,
            'opencv_qr': True,  # OpenCV QR detector is built-in
        }
        
        # Test pyzbar
        if PYZBAR_AVAILABLE:
            print("✅ pyzbar library is available")
            try:
                # Test with a simple QR code image
                test_image = np.zeros((100, 100, 3), dtype=np.uint8)
                qr_codes = pyzbar.decode(test_image)
                print("✅ pyzbar decode function works")
            except Exception as e:
                print(f"❌ pyzbar decode error: {str(e)}")
                library_status['pyzbar'] = False
        else:
            print("❌ pyzbar library not available")
            print("   Install with: pip install pyzbar")
        
        # Test OpenCV QR detector
        try:
            qr_detector = cv2.QRCodeDetector()
            print("✅ OpenCV QR detector is available")
        except Exception as e:
            print(f"❌ OpenCV QR detector error: {str(e)}")
            library_status['opencv_qr'] = False
        
        return library_status
    
    def detect_orange_sheets(self, frame: np.ndarray) -> List[np.ndarray]:
        """
        Detect orange sheets in the frame using HSV color detection.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of contours representing orange sheets
        """
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for orange color
        mask = cv2.inRange(hsv, 
                          self.orange_detection_params['lower_hsv'],
                          self.orange_detection_params['upper_hsv'])
        
        # Apply blur to reduce noise
        blur_kernel = self.orange_detection_params['blur_kernel']
        if blur_kernel > 1:
            mask = cv2.GaussianBlur(mask, (blur_kernel, blur_kernel), 0)
        
        # Apply morphological operations
        morph_kernel = np.ones((self.orange_detection_params['morph_kernel'], 
                               self.orange_detection_params['morph_kernel']), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, morph_kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morph_kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area
        orange_sheets = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.orange_detection_params['min_area']:
                orange_sheets.append(contour)
        
        return orange_sheets
    
    def detect_qr_codes_pyzbar(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect QR codes using pyzbar library.
        
        Args:
            frame: Input frame
            
        Returns:
            List of dictionaries containing QR code information
        """
        if not PYZBAR_AVAILABLE:
            return []
        
        qr_codes = []
        try:
            # Convert to grayscale for pyzbar
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect QR codes
            decoded_objects = pyzbar.decode(gray)
            
            for obj in decoded_objects:
                qr_info = {
                    'data': obj.data.decode('utf-8'),
                    'type': obj.type,
                    'rect': obj.rect,
                    'polygon': obj.polygon,
                    'quality': getattr(obj, 'quality', 0),
                    'detector': 'pyzbar'
                }
                qr_codes.append(qr_info)
                
        except Exception as e:
            logging.error(f"pyzbar detection error: {str(e)}")
        
        return qr_codes
    
    def detect_qr_codes_opencv(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect QR codes using OpenCV's QR detector.
        
        Args:
            frame: Input frame
            
        Returns:
            List of dictionaries containing QR code information
        """
        qr_codes = []
        try:
            qr_detector = cv2.QRCodeDetector()
            
            # Detect QR code
            retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(frame)
            
            if retval:
                for i, (info, point) in enumerate(zip(decoded_info, points)):
                    if info:  # Only add if QR code was successfully decoded
                        qr_info = {
                            'data': info,
                            'type': 'QR_CODE',
                            'points': point.astype(int),
                            'quality': 1.0,  # OpenCV doesn't provide quality score
                            'detector': 'opencv'
                        }
                        qr_codes.append(qr_info)
                        
        except Exception as e:
            logging.error(f"OpenCV QR detection error: {str(e)}")
        
        return qr_codes
    
    def filter_qr_codes_by_orange_sheets(self, qr_codes: List[Dict], 
                                       orange_sheets: List[np.ndarray]) -> List[Dict]:
        """
        Filter QR codes to only include those within orange sheets.
        
        Args:
            qr_codes: List of detected QR codes
            orange_sheets: List of orange sheet contours
            
        Returns:
            List of QR codes that are within orange sheets
        """
        if not orange_sheets:
            return []
        
        filtered_qr_codes = []
        
        for qr_code in qr_codes:
            # Get QR code center point
            if 'rect' in qr_code:  # pyzbar format
                center = (qr_code['rect'].left + qr_code['rect'].width // 2,
                         qr_code['rect'].top + qr_code['rect'].height // 2)
            elif 'points' in qr_code:  # OpenCV format
                points = qr_code['points']
                center = (int(np.mean(points[:, 0])), int(np.mean(points[:, 1])))
            else:
                continue
            
            # Check if center is within any orange sheet
            for sheet_contour in orange_sheets:
                if cv2.pointPolygonTest(sheet_contour, center, False) >= 0:
                    qr_code['sheet_contour'] = sheet_contour
                    filtered_qr_codes.append(qr_code)
                    break
        
        return filtered_qr_codes
    
    def detect_qr_codes(self, frame: np.ndarray, 
                       filter_by_orange: bool = False) -> Dict[str, Any]:
        """
        Detect QR codes in the frame with optional orange sheet filtering.
        
        Args:
            frame: Input frame
            filter_by_orange: Whether to filter QR codes by orange sheets
            
        Returns:
            Dictionary containing detection results
        """
        start_time = time.time()
        
        # Detect orange sheets if filtering is enabled
        orange_sheets = []
        if filter_by_orange:
            orange_sheets = self.detect_orange_sheets(frame)
        
        # Detect QR codes using available methods
        qr_codes = []
        
        # Use pyzbar if available and enabled
        if self.qr_detection_params['use_pyzbar'] and PYZBAR_AVAILABLE:
            pyzbar_qr_codes = self.detect_qr_codes_pyzbar(frame)
            qr_codes.extend(pyzbar_qr_codes)
        
        # Use OpenCV QR detector if enabled
        if self.qr_detection_params['use_opencv_qr']:
            opencv_qr_codes = self.detect_qr_codes_opencv(frame)
            qr_codes.extend(opencv_qr_codes)
        
        # Filter QR codes by orange sheets if requested
        filtered_qr_codes = []
        if filter_by_orange and orange_sheets:
            filtered_qr_codes = self.filter_qr_codes_by_orange_sheets(qr_codes, orange_sheets)
        else:
            filtered_qr_codes = qr_codes
        
        processing_time = time.time() - start_time
        self.processing_times.append(processing_time)
        
        # Update performance metrics
        self.performance_metrics['total_frames'] += 1
        if qr_codes or orange_sheets:
            self.performance_metrics['detection_frames'] += 1
        
        return {
            'qr_codes': qr_codes,
            'orange_sheets': orange_sheets,
            'filtered_qr_codes': filtered_qr_codes,
            'processing_time': processing_time
        }
    
    def draw_detection_results(self, frame: np.ndarray, 
                             detection_results: Dict[str, Any]) -> np.ndarray:
        """
        Draw detection results on the frame.
        
        Args:
            frame: Input frame
            detection_results: Detection results dictionary
            
        Returns:
            Frame with detection results drawn
        """
        # Draw orange sheets
        for sheet_contour in detection_results['orange_sheets']:
            cv2.drawContours(frame, [sheet_contour], -1, (0, 165, 255), 2)
            cv2.putText(frame, 'Orange Sheet', 
                       (sheet_contour[0][0][0], sheet_contour[0][0][1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
        
        # Draw QR codes
        for qr_code in detection_results['filtered_qr_codes']:
            if 'rect' in qr_code:  # pyzbar format
                rect = qr_code['rect']
                cv2.rectangle(frame, (rect.left, rect.top), 
                             (rect.left + rect.width, rect.top + rect.height),
                             (0, 255, 0), 2)
                cv2.putText(frame, f"QR: {qr_code['data'][:20]}...", 
                           (rect.left, rect.top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
            elif 'points' in qr_code:  # OpenCV format
                points = qr_code['points']
                cv2.polylines(frame, [points], True, (0, 255, 0), 2)
                
                # Calculate center for text
                center_x = int(np.mean(points[:, 0]))
                center_y = int(np.mean(points[:, 1]))
                
                cv2.putText(frame, f"QR: {qr_code['data'][:20]}...", 
                           (center_x, center_y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw performance info
        self.draw_performance_info(frame)
        
        return frame
    
    def draw_performance_info(self, frame: np.ndarray):
        """Draw performance information on the frame."""
        # Calculate FPS
        self.fps_counter += 1
        if time.time() - self.fps_start_time >= 1.0:
            self.avg_fps = self.fps_counter / (time.time() - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = time.time()
        
        # Calculate average processing time
        if self.processing_times:
            avg_time = np.mean(self.processing_times[-30:])  # Last 30 frames
            self.performance_metrics['avg_processing_time'] = avg_time
        
        # Draw info on frame
        info_lines = [
            f"FPS: {self.avg_fps:.1f}",
            f"Avg Processing: {self.performance_metrics['avg_processing_time']*1000:.1f}ms",
            f"Total Frames: {self.performance_metrics['total_frames']}",
            f"Detection Frames: {self.performance_metrics['detection_frames']}"
        ]
        
        y_offset = 30
        for line in info_lines:
            cv2.putText(frame, line, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, line, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            y_offset += 25
    
    def create_parameter_window(self):
        """Create parameter adjustment window with trackbars."""
        cv2.namedWindow('QR Detection Parameters', cv2.WINDOW_NORMAL)
        
        # QR detection parameters
        cv2.createTrackbar('Use pyzbar', 'QR Detection Parameters', 
                          int(self.qr_detection_params['use_pyzbar']), 1, 
                          lambda x: setattr(self.qr_detection_params, 'use_pyzbar', bool(x)))
        
        cv2.createTrackbar('Use OpenCV QR', 'QR Detection Parameters', 
                          int(self.qr_detection_params['use_opencv_qr']), 1, 
                          lambda x: setattr(self.qr_detection_params, 'use_opencv_qr', bool(x)))
        
        # Orange detection parameters
        cv2.createTrackbar('Orange Min Area', 'QR Detection Parameters', 
                          self.orange_detection_params['min_area'], 1000, 
                          lambda x: setattr(self.orange_detection_params, 'min_area', x))
        
        cv2.createTrackbar('Orange Blur Kernel', 'QR Detection Parameters', 
                          self.orange_detection_params['blur_kernel'], 10, 
                          lambda x: setattr(self.orange_detection_params, 'blur_kernel', max(1, x)))
    
    def test_qr_detection(self, camera_index: int = 0, 
                         filter_by_orange: bool = False):
        """
        Test QR code detection with real-time parameter adjustment.
        
        Args:
            camera_index: Camera index to use
            filter_by_orange: Whether to filter QR codes by orange sheets
        """
        print(f"\n{'='*60}")
        print("QR CODE DETECTION TEST")
        print(f"{'='*60}")
        print("Controls:")
        print("- Press 'q' to quit")
        print("- Press 'o' to toggle orange sheet filtering")
        print("- Press 'p' to toggle parameter window")
        print("- Press 's' to save current frame")
        print("- Press 'r' to reset performance metrics")
        print(f"{'='*60}")
        
        # Initialize camera
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            print(f"❌ Failed to open camera {camera_index}")
            return
        
        # Create parameter window
        self.create_parameter_window()
        
        self.is_running = True
        show_parameters = True
        
        try:
            while self.is_running:
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                # Detect QR codes
                detection_results = self.detect_qr_codes(frame, filter_by_orange)
                
                # Draw results
                frame = self.draw_detection_results(frame, detection_results)
                
                # Show frame
                cv2.imshow('QR Code Detection', frame)
                
                # Show parameter window if enabled
                if show_parameters:
                    cv2.imshow('QR Detection Parameters', np.zeros((200, 400, 3), dtype=np.uint8))
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('o'):
                    filter_by_orange = not filter_by_orange
                    print(f"Orange sheet filtering: {'ON' if filter_by_orange else 'OFF'}")
                elif key == ord('p'):
                    show_parameters = not show_parameters
                    if not show_parameters:
                        cv2.destroyWindow('QR Detection Parameters')
                elif key == ord('s'):
                    self.save_debug_frame(frame, detection_results)
                elif key == ord('r'):
                    self.reset_performance_metrics()
                    print("Performance metrics reset")
                
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            self.cleanup()
    
    def save_debug_frame(self, frame: np.ndarray, detection_results: Dict[str, Any]):
        """Save current frame with detection results for debugging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qr_debug_frame_{timestamp}.jpg"
        filepath = os.path.join(self.debug_dir, filename)
        
        # Save frame
        cv2.imwrite(filepath, frame)
        
        # Save detection results
        results_file = f"qr_debug_results_{timestamp}.txt"
        results_path = os.path.join(self.debug_dir, results_file)
        
        with open(results_path, 'w') as f:
            f.write(f"QR Code Detection Results - {timestamp}\n")
            f.write("="*50 + "\n")
            f.write(f"Total QR codes detected: {len(detection_results['qr_codes'])}\n")
            f.write(f"Filtered QR codes: {len(detection_results['filtered_qr_codes'])}\n")
            f.write(f"Orange sheets detected: {len(detection_results['orange_sheets'])}\n")
            f.write(f"Processing time: {detection_results['processing_time']*1000:.2f}ms\n\n")
            
            for i, qr_code in enumerate(detection_results['filtered_qr_codes']):
                f.write(f"QR Code {i+1}:\n")
                f.write(f"  Data: {qr_code['data']}\n")
                f.write(f"  Type: {qr_code['type']}\n")
                f.write(f"  Detector: {qr_code['detector']}\n")
                f.write(f"  Quality: {qr_code.get('quality', 'N/A')}\n\n")
        
        print(f"Debug frame saved: {filepath}")
        print(f"Results saved: {results_path}")
    
    def reset_performance_metrics(self):
        """Reset performance metrics."""
        self.performance_metrics = {
            'total_frames': 0,
            'detection_frames': 0,
            'avg_processing_time': 0.0,
            'max_processing_time': 0.0,
            'min_processing_time': float('inf')
        }
        self.processing_times = []
        self.fps_counter = 0
        self.fps_start_time = time.time()
    
    def cleanup(self):
        """Clean up resources."""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        self.is_running = False
        logging.info("QR Code Detection Debugger cleaned up")
    
    def print_summary(self):
        """Print detection summary and statistics."""
        print(f"\n{'='*60}")
        print("QR CODE DETECTION SUMMARY")
        print(f"{'='*60}")
        
        print(f"Total frames processed: {self.performance_metrics['total_frames']}")
        print(f"Frames with detections: {self.performance_metrics['detection_frames']}")
        print(f"Average processing time: {self.performance_metrics['avg_processing_time']*1000:.2f}ms")
        print(f"Average FPS: {self.avg_fps:.1f}")
        
        if self.processing_times:
            print(f"Min processing time: {min(self.processing_times)*1000:.2f}ms")
            print(f"Max processing time: {max(self.processing_times)*1000:.2f}ms")
        
        print(f"\nDebug files saved in: {self.debug_dir}")
        print(f"Log file: qr_detection_debug.log")


def main():
    """Main function to run QR code detection debugger."""
    print("QR Code Detection Debugger")
    print("="*50)
    
    # Initialize debugger
    debugger = QRCodeDetectionDebugger()
    
    try:
        while True:
            print("\nSelect an option:")
            print("1. Camera Diagnostics")
            print("2. QR Detection Library Test")
            print("3. QR Code Detection Test (All QR codes)")
            print("4. QR Code Detection Test (Orange sheet filtered)")
            print("5. Quick QR Detection Test")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                camera_index = int(input("Enter camera index (default 0): ") or "0")
                debugger.print_camera_info(camera_index)
                
            elif choice == '2':
                library_status = debugger.test_qr_detection_libraries()
                print("\nLibrary Status Summary:")
                for library, status in library_status.items():
                    print(f"  {library}: {'✅ Available' if status else '❌ Not Available'}")
                
            elif choice == '3':
                camera_index = int(input("Enter camera index (default 0): ") or "0")
                debugger.test_qr_detection(camera_index, filter_by_orange=False)
                
            elif choice == '4':
                camera_index = int(input("Enter camera index (default 0): ") or "0")
                debugger.test_qr_detection(camera_index, filter_by_orange=True)
                
            elif choice == '5':
                camera_index = int(input("Enter camera index (default 0): ") or "0")
                print("\nQuick QR Detection Test")
                print("Press 'q' to quit, 'o' to toggle orange filtering")
                debugger.test_qr_detection(camera_index, filter_by_orange=False)
                
            elif choice == '6':
                print("Exiting...")
                break
                
            else:
                print("Invalid choice. Please enter 1-6.")
                
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        debugger.print_summary()
        debugger.cleanup()


if __name__ == "__main__":
    main() 