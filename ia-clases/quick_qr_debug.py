#!/usr/bin/env python3
"""
Quick QR Code Detection Debug Script
===================================

A simplified script for quick QR code detection testing with optional
orange sheet filtering. This script provides basic QR code detection
capabilities for rapid testing and debugging.

Features:
- Quick QR code detection with pyzbar and OpenCV
- Optional orange sheet filtering
- Real-time visualization
- Basic performance metrics

Author: AI Assistant
Date: 2024
"""

import cv2
import numpy as np
import time
import os
from typing import List, Dict, Any

# Try to import pyzbar for QR code detection
try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    print("Warning: pyzbar not available. Install with: pip install pyzbar")
    print("QR code detection will be limited to OpenCV's QR code detector.")

def detect_orange_sheets(frame):
    """Detect orange sheets in the frame."""
    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Orange color range in HSV
    lower_orange = np.array([5, 50, 50])
    upper_orange = np.array([25, 255, 255])
    
    # Create mask
    mask = cv2.inRange(hsv, lower_orange, upper_orange)
    
    # Apply blur and morphological operations
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter by area
    orange_sheets = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:  # Minimum area threshold
            orange_sheets.append(contour)
    
    return orange_sheets

def detect_qr_codes_pyzbar(frame):
    """Detect QR codes using pyzbar."""
    if not PYZBAR_AVAILABLE:
        return []
    
    qr_codes = []
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect QR codes
        decoded_objects = pyzbar.decode(gray)
        
        for obj in decoded_objects:
            qr_info = {
                'data': obj.data.decode('utf-8'),
                'type': obj.type,
                'rect': obj.rect,
                'detector': 'pyzbar'
            }
            qr_codes.append(qr_info)
            
    except Exception as e:
        print(f"pyzbar error: {e}")
    
    return qr_codes

def detect_qr_codes_opencv(frame):
    """Detect QR codes using OpenCV."""
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
                        'detector': 'opencv'
                    }
                    qr_codes.append(qr_info)
                    
    except Exception as e:
        print(f"OpenCV QR error: {e}")
    
    return qr_codes

def filter_qr_codes_by_orange_sheets(qr_codes, orange_sheets):
    """Filter QR codes to only include those within orange sheets."""
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
                filtered_qr_codes.append(qr_code)
                break
    
    return filtered_qr_codes

def draw_detections(frame, orange_sheets, qr_codes):
    """Draw detection results on the frame."""
    # Draw orange sheets
    for sheet_contour in orange_sheets:
        cv2.drawContours(frame, [sheet_contour], -1, (0, 165, 255), 2)
        cv2.putText(frame, 'Orange Sheet', 
                   (sheet_contour[0][0][0], sheet_contour[0][0][1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
    
    # Draw QR codes
    for qr_code in qr_codes:
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
    
    return frame

def quick_qr_detection(camera_index=0, filter_by_orange=False):
    """Quick QR code detection test."""
    print(f"Quick QR Detection Test")
    print(f"Camera: {camera_index}")
    print(f"Orange filtering: {'ON' if filter_by_orange else 'OFF'}")
    print("Press 'q' to quit, 'o' to toggle orange filtering")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ Failed to open camera {camera_index}")
        return
    
    fps_counter = 0
    fps_start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            start_time = time.time()
            
            # Detect orange sheets if filtering is enabled
            orange_sheets = []
            if filter_by_orange:
                orange_sheets = detect_orange_sheets(frame)
            
            # Detect QR codes
            qr_codes = []
            
            # Use pyzbar if available
            if PYZBAR_AVAILABLE:
                pyzbar_qr_codes = detect_qr_codes_pyzbar(frame)
                qr_codes.extend(pyzbar_qr_codes)
            
            # Use OpenCV QR detector
            opencv_qr_codes = detect_qr_codes_opencv(frame)
            qr_codes.extend(opencv_qr_codes)
            
            # Filter QR codes if requested
            if filter_by_orange and orange_sheets:
                qr_codes = filter_qr_codes_by_orange_sheets(qr_codes, orange_sheets)
            
            processing_time = time.time() - start_time
            
            # Draw results
            frame = draw_detections(frame, orange_sheets, qr_codes)
            
            # Draw performance info
            fps_counter += 1
            if time.time() - fps_start_time >= 1.0:
                fps = fps_counter / (time.time() - fps_start_time)
                fps_counter = 0
                fps_start_time = time.time()
            else:
                fps = 0
            
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"QR Codes: {len(qr_codes)}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Orange Sheets: {len(orange_sheets)}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Time: {processing_time*1000:.1f}ms", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Quick QR Detection', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('o'):
                filter_by_orange = not filter_by_orange
                print(f"Orange filtering: {'ON' if filter_by_orange else 'OFF'}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def test_camera(camera_index=0):
    """Quick camera test."""
    print(f"Testing camera {camera_index}...")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ Failed to open camera {camera_index}")
        return False
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"✅ Camera {camera_index} is working")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    
    # Test frame capture
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame capture successful: {frame.shape}")
        cap.release()
        return True
    else:
        print("❌ Frame capture failed")
        cap.release()
        return False

def test_qr_libraries():
    """Test QR code detection libraries."""
    print("Testing QR code detection libraries...")
    
    # Test pyzbar
    if PYZBAR_AVAILABLE:
        print("✅ pyzbar library is available")
    else:
        print("❌ pyzbar library not available")
        print("   Install with: pip install pyzbar")
    
    # Test OpenCV QR detector
    try:
        qr_detector = cv2.QRCodeDetector()
        print("✅ OpenCV QR detector is available")
    except Exception as e:
        print(f"❌ OpenCV QR detector error: {e}")

def main():
    """Main function."""
    print("Quick QR Code Detection Debugger")
    print("="*40)
    
    while True:
        print("\nSelect an option:")
        print("1. Test Camera")
        print("2. Test QR Libraries")
        print("3. Quick QR Detection (All QR codes)")
        print("4. Quick QR Detection (Orange filtered)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            camera_index = int(input("Enter camera index (default 0): ") or "0")
            test_camera(camera_index)
            
        elif choice == '2':
            test_qr_libraries()
            
        elif choice == '3':
            camera_index = int(input("Enter camera index (default 0): ") or "0")
            quick_qr_detection(camera_index, filter_by_orange=False)
            
        elif choice == '4':
            camera_index = int(input("Enter camera index (default 0): ") or "0")
            quick_qr_detection(camera_index, filter_by_orange=True)
            
        elif choice == '5':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main() 