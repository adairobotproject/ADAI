#!/usr/bin/env python3
"""
Install Dependencies Script
==========================

This script helps install all required dependencies for the camera debug scripts.
It checks for existing installations and provides guidance for missing packages.

Author: AI Assistant
Date: 2024
"""

import subprocess
import sys
import os
import importlib

def check_package(package_name):
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name, pip_name=None):
    """Install a package using pip."""
    if pip_name is None:
        pip_name = package_name
    
    print(f"Installing {pip_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        print(f"✅ {pip_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {pip_name}: {e}")
        return False

def main():
    """Main function to check and install dependencies."""
    print("Camera Debug Scripts - Dependency Installer")
    print("="*50)
    
    # List of required packages
    required_packages = [
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
        ("face-recognition", "face_recognition"),
        ("mediapipe", "mediapipe"),
        ("pyzbar", "pyzbar"),
    ]
    
    # List of optional packages
    optional_packages = [
        ("dlib", "dlib"),
        ("cmake", "cmake"),
    ]
    
    print("\nChecking required packages...")
    print("-" * 30)
    
    missing_required = []
    for pip_name, import_name in required_packages:
        if check_package(import_name):
            print(f"✅ {pip_name} is already installed")
        else:
            print(f"❌ {pip_name} is missing")
            missing_required.append((pip_name, import_name))
    
    print("\nChecking optional packages...")
    print("-" * 30)
    
    missing_optional = []
    for pip_name, import_name in optional_packages:
        if check_package(import_name):
            print(f"✅ {pip_name} is already installed")
        else:
            print(f"⚠️  {pip_name} is missing (optional)")
            missing_optional.append((pip_name, import_name))
    
    # Install missing required packages
    if missing_required:
        print(f"\nInstalling {len(missing_required)} missing required packages...")
        print("-" * 50)
        
        for pip_name, import_name in missing_required:
            if not install_package(pip_name, pip_name):
                print(f"⚠️  Manual installation may be required for {pip_name}")
    
    # Install missing optional packages
    if missing_optional:
        print(f"\nInstalling {len(missing_optional)} missing optional packages...")
        print("-" * 50)
        
        for pip_name, import_name in missing_optional:
            install_package(pip_name, pip_name)
    
    # Final check
    print("\nFinal verification...")
    print("-" * 30)
    
    all_installed = True
    for pip_name, import_name in required_packages:
        if check_package(import_name):
            print(f"✅ {pip_name} is working")
        else:
            print(f"❌ {pip_name} is still missing")
            all_installed = False
    
    if all_installed:
        print("\n🎉 All required packages are installed!")
        print("You can now run the camera debug scripts.")
    else:
        print("\n⚠️  Some packages are still missing.")
        print("Please try manual installation:")
        print("\nFor Windows:")
        print("pip install opencv-python numpy face-recognition mediapipe pyzbar")
        print("\nFor face_recognition on Windows, you may need:")
        print("pip install cmake")
        print("pip install dlib")
        print("pip install face-recognition")
    
    print("\nTroubleshooting tips:")
    print("1. Make sure you're using the correct Python environment")
    print("2. Try running: python -m pip install --upgrade pip")
    print("3. For dlib issues on Windows, try: pip install dlib-binary")
    print("4. For OpenCV issues, try: pip install opencv-python-headless")

if __name__ == "__main__":
    main() 