#!/usr/bin/env python3
"""
Install QR Code Detection Dependencies
=====================================

This script installs the necessary dependencies for QR code detection
in the ADAI robot system.
"""

import subprocess
import sys
import os

def install_package(package_name):
    """Install a Python package using pip"""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package_name}: {e}")
        return False

def test_import(module_name):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {module_name} is available")
        return True
    except ImportError:
        print(f"✗ {module_name} is not available")
        return False

def main():
    """Main installation function"""
    print("Installing QR Code Detection Dependencies")
    print("=" * 50)
    
    # List of packages to install
    packages = [
        "pyzbar",
        "opencv-python",
        "numpy"
    ]
    
    # Install packages
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\nInstallation Summary:")
    print(f"Successfully installed: {success_count}/{len(packages)} packages")
    
    # Test imports
    print(f"\nTesting imports...")
    test_modules = ["pyzbar", "cv2", "numpy"]
    
    import_success = 0
    for module in test_modules:
        if test_import(module):
            import_success += 1
    
    print(f"\nImport Test Summary:")
    print(f"Successful imports: {import_success}/{len(test_modules)} modules")
    
    if import_success == len(test_modules):
        print("\n🎉 All QR code detection dependencies are ready!")
        print("You can now use QR code detection in the robot GUI.")
    else:
        print("\n⚠️  Some dependencies may not be working properly.")
        print("Try running the installation again or check your Python environment.")
    
    # Additional instructions for Windows
    if os.name == 'nt':  # Windows
        print("\n📝 Note for Windows users:")
        print("If pyzbar doesn't work, you may need to install zbar:")
        print("1. Download zbar from: https://github.com/NaturalHistoryMuseum/pyzbar")
        print("2. Or try: pip install pyzbar[windows]")
        print("3. Alternative: pip install pyzbar --only-binary=pyzbar")

if __name__ == "__main__":
    main()
