#!/usr/bin/env python3
"""
Fix Installation Issues Script
==============================

This script helps resolve common installation issues and provides
alternative installation methods for the camera debug scripts.

Author: AI Assistant
Date: 2024
"""

import subprocess
import sys
import os
import importlib

def run_command(command, description=""):
    """Run a command and return success status."""
    print(f"\n{description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            return True
        else:
            print(f"❌ Failed: {description}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_package(package_name):
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def main():
    """Main function to fix installation issues."""
    print("Fix Installation Issues")
    print("="*40)
    
    print("\n1. Upgrading pip to latest version...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    print("\n2. Clearing pip cache...")
    run_command(f"{sys.executable} -m pip cache purge", "Clearing pip cache")
    
    print("\n3. Installing packages with --no-cache-dir...")
    
    packages = [
        "opencv-python",
        "numpy", 
        "mediapipe",
        "pyzbar"
    ]
    
    for package in packages:
        if not check_package(package.replace("-", "_")):
            run_command(
                f"{sys.executable} -m pip install --no-cache-dir {package}",
                f"Installing {package}"
            )
    
    print("\n4. Trying alternative OpenCV packages...")
    if not check_package("cv2"):
        alternatives = [
            "opencv-python-headless",
            "opencv-contrib-python",
            "opencv-python==4.8.1.78"
        ]
        
        for alt in alternatives:
            if run_command(
                f"{sys.executable} -m pip install --no-cache-dir {alt}",
                f"Trying {alt}"
            ):
                break
    
    print("\n5. Installing face_recognition dependencies...")
    if not check_package("face_recognition"):
        # Install cmake first
        run_command(
            f"{sys.executable} -m pip install --no-cache-dir cmake",
            "Installing cmake"
        )
        
        # Try different dlib versions
        dlib_alternatives = [
            "dlib",
            "dlib-binary",
            "dlib==19.24.0"
        ]
        
        for dlib_ver in dlib_alternatives:
            if run_command(
                f"{sys.executable} -m pip install --no-cache-dir {dlib_ver}",
                f"Installing {dlib_ver}"
            ):
                break
        
        # Install face_recognition
        run_command(
            f"{sys.executable} -m pip install --no-cache-dir face-recognition",
            "Installing face_recognition"
        )
    
    print("\n6. Final verification...")
    print("-" * 30)
    
    required_packages = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("mediapipe", "MediaPipe"),
        ("pyzbar", "pyzbar"),
        ("face_recognition", "face_recognition"),
    ]
    
    all_working = True
    for module_name, display_name in required_packages:
        if check_package(module_name):
            print(f"✅ {display_name} - OK")
        else:
            print(f"❌ {display_name} - FAILED")
            all_working = False
    
    if all_working:
        print("\n🎉 All packages are working!")
        print("You can now run the camera debug scripts.")
    else:
        print("\n⚠️  Some packages are still missing.")
        print("\nManual installation commands:")
        print("pip install --no-cache-dir opencv-python numpy mediapipe pyzbar")
        print("pip install --no-cache-dir cmake dlib face-recognition")
        
        print("\nAlternative solutions:")
        print("1. Try using conda instead of pip:")
        print("   conda install opencv numpy")
        print("   conda install -c conda-forge face_recognition")
        
        print("\n2. Try installing from wheels:")
        print("   Download wheels from: https://www.lfd.uci.edu/~gohlke/pythonlibs/")
        
        print("\n3. Try using a virtual environment:")
        print("   python -m venv venv")
        print("   venv\\Scripts\\activate  # Windows")
        print("   pip install --upgrade pip")
        print("   pip install opencv-python")

if __name__ == "__main__":
    main() 