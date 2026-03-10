#!/usr/bin/env python3
"""
Quick Aruco Generator
====================

A simple script to quickly generate Aruco markers for the robot system.
Generates markers with different dictionaries and saves them as images.
"""

import cv2
import numpy as np
import os
import argparse

def generate_aruco_marker(marker_id, dict_type, size=200, margin=2):
    """Generate a single Aruco marker"""
    try:
        # Get the Aruco dictionary using correct API
        try:
            # New API (OpenCV 4.7+)
            aruco_dict = cv2.aruco.getPredefinedDictionary(dict_type)
        except AttributeError:
            # Old API (OpenCV 4.6 and earlier)
            aruco_dict = cv2.aruco.Dictionary_get(dict_type)
        
        # Generate the marker
        marker_img = cv2.aruco.drawMarker(aruco_dict, marker_id, size)
        
        # Add margin
        if margin > 0:
            marker_img = cv2.copyMakeBorder(marker_img, margin, margin, margin, margin,
                                          cv2.BORDER_CONSTANT, value=255)
        
        return marker_img
        
    except Exception as e:
        print(f"Error generating Aruco marker: {e}")
        return None

def generate_batch_markers(dict_type, start_id=0, end_id=9, size=200, margin=2, output_dir="aruco_markers"):
    """Generate a batch of Aruco markers"""
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Get dictionary name for filename
    dict_names = {
        cv2.aruco.DICT_4X4_50: "DICT_4X4_50",
        cv2.aruco.DICT_4X4_100: "DICT_4X4_100",
        cv2.aruco.DICT_5X5_50: "DICT_5X5_50",
        cv2.aruco.DICT_5X5_100: "DICT_5X5_100",
        cv2.aruco.DICT_6X6_50: "DICT_6X6_50",
        cv2.aruco.DICT_6X6_100: "DICT_6X6_100"
    }
    
    dict_name = dict_names.get(dict_type, "UNKNOWN")
    
    generated_count = 0
    for marker_id in range(start_id, end_id + 1):
        marker_img = generate_aruco_marker(marker_id, dict_type, size, margin)
        
        if marker_img is not None:
            # Save marker
            filename = f"aruco_{dict_name}_id{marker_id:03d}.png"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, marker_img)
            print(f"Generated: {filename}")
            generated_count += 1
    
    print(f"\nGenerated {generated_count} Aruco markers in {output_dir}/")
    return generated_count

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate Aruco markers")
    parser.add_argument("--dict", type=str, default="DICT_4X4_50", 
                       choices=["DICT_4X4_50", "DICT_4X4_100", "DICT_5X5_50", "DICT_5X5_100", "DICT_6X6_50", "DICT_6X6_100"],
                       help="Aruco dictionary type")
    parser.add_argument("--start", type=int, default=0, help="Starting marker ID")
    parser.add_argument("--end", type=int, default=9, help="Ending marker ID")
    parser.add_argument("--size", type=int, default=200, help="Marker size in pixels")
    parser.add_argument("--margin", type=int, default=2, help="Margin around marker")
    parser.add_argument("--output", type=str, default="aruco_markers", help="Output directory")
    
    args = parser.parse_args()
    
    # Convert dictionary name to OpenCV constant
    dict_map = {
        "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
        "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
        "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
        "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
        "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
        "DICT_6X6_100": cv2.aruco.DICT_6X6_100
    }
    
    dict_type = dict_map[args.dict]
    
    print(f"Generating Aruco markers...")
    print(f"Dictionary: {args.dict}")
    print(f"Range: {args.start} to {args.end}")
    print(f"Size: {args.size}px")
    print(f"Margin: {args.margin}px")
    print(f"Output: {args.output}/")
    print("-" * 50)
    
    # Generate markers
    count = generate_batch_markers(dict_type, args.start, args.end, args.size, args.margin, args.output)
    
    print(f"\nSuccessfully generated {count} Aruco markers!")
    print(f"Markers saved in: {os.path.abspath(args.output)}/")

if __name__ == "__main__":
    main()
