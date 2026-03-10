#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to check if ESP32Tab class can be instantiated
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_class_instantiation():
    """Test if we can create an instance of ESP32Tab"""
    try:
        print("🔍 Testing ESP32Tab class instantiation...")

        # Initialize tkinter first
        import tkinter as tk
        print("🔧 Initializing tkinter...")

        # Create a root window (required for tkinter variables)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        print("✅ Tkinter root created")

        # Import required modules
        from tabs.esp32_tab import ESP32Tab
        print("✅ ESP32Tab import successful")

        # Create a mock parent GUI and notebook for testing
        class MockNotebook:
            def add(self, frame, text):
                pass

        class MockParentGUI:
            def __init__(self):
                self.root = root
                self.window_width = 1200
                self.window_height = 600

        # Try to create instance
        mock_parent = MockParentGUI()
        mock_notebook = MockNotebook()

        print("🔧 Creating ESP32Tab instance...")
        esp32_tab = ESP32Tab(mock_parent, mock_notebook)
        print("✅ ESP32Tab instance created successfully")

        # Check basic attributes
        print(f"📋 Tab name: {esp32_tab.tab_name}")
        print(f"📋 Config manager: {esp32_tab.config_manager}")
        print(f"📋 ESP32 client: {esp32_tab.esp32_client}")
        print(f"📋 Connected: {esp32_tab.esp32_connected}")

        # Clean up
        root.destroy()

        return True

    except Exception as e:
        print(f"❌ ESP32Tab instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_base_class():
    """Test if BaseTab can be instantiated"""
    try:
        print("\n🔍 Testing BaseTab class instantiation...")

        from tabs.base_tab import BaseTab

        class MockNotebook:
            def add(self, frame, text):
                pass

        class MockParentGUI:
            def __init__(self):
                self.root = None
                self.window_width = 1200
                self.window_height = 600

        mock_parent = MockParentGUI()
        mock_notebook = MockNotebook()

        base_tab = BaseTab(mock_parent, mock_notebook)
        print("✅ BaseTab instance created successfully")

        return True

    except Exception as e:
        print(f"❌ BaseTab instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting class instantiation test...\n")

    # Test base class first
    base_success = test_base_class()

    # Test ESP32Tab
    esp32_success = test_class_instantiation()

    if base_success and esp32_success:
        print("\n🎉 All tests passed! The class should work correctly.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
