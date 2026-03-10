#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for SequenceBuilderTab Debug Mode
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_debug_mode_functionality():
    """Test the debug mode functionality"""
    print("🧪 Testing SequenceBuilderTab Debug Mode")
    print("=" * 60)
    
    try:
        # Create a mock parent GUI
        class MockParentGUI:
            def __init__(self):
                self.root = tk.Tk()
                self.root.withdraw()  # Hide the window
        
        # Create a mock notebook
        parent_gui = MockParentGUI()
        notebook = ttk.Notebook(parent_gui.root)
        
        # Create the SequenceBuilderTab
        from tabs.sequence_builder_tab import SequenceBuilderTab
        sequence_builder = SequenceBuilderTab(parent_gui, notebook)
        
        print("✅ SequenceBuilderTab created successfully")
        
        # Test debug mode state
        print(f"   Initial debug mode: {sequence_builder.debug_mode}")
        print(f"   Initial ESP32 connected: {sequence_builder.esp32_connected}")
        
        # Test enabling debug mode
        print("\n🔧 Testing debug mode activation...")
        sequence_builder.toggle_debug_mode()
        
        print(f"   Debug mode after toggle: {sequence_builder.debug_mode}")
        print(f"   ESP32 connected after toggle: {sequence_builder.esp32_connected}")
        
        # Test ESP32 commands in debug mode
        print("\n🐛 Testing ESP32 commands in debug mode...")
        
        # Test arm movement
        sequence_builder.on_arm_change('left_brazo', 45)
        
        # Test finger movement
        sequence_builder.on_finger_change('left', 'thumb', 90)
        
        # Test wrist movement
        sequence_builder.on_wrist_change('right', 80)
        
        # Test gestures
        sequence_builder.hand_gesture('left', 'ABRIR')
        sequence_builder.wave_gesture()
        sequence_builder.hug_gesture()
        
        # Test other commands
        sequence_builder.home_position()
        sequence_builder.look_around()
        
        # Test speech (need to set up speech text variable)
        sequence_builder.speech_text_var = tk.StringVar(value="Hello World")
        sequence_builder.speak_text()
        
        # Test connection test in debug mode
        print("\n🧪 Testing connection test in debug mode...")
        sequence_builder.test_esp32_connection()
        
        # Test disabling debug mode
        print("\n🔧 Testing debug mode deactivation...")
        sequence_builder.toggle_debug_mode()
        
        print(f"   Debug mode after second toggle: {sequence_builder.debug_mode}")
        print(f"   ESP32 connected after second toggle: {sequence_builder.esp32_connected}")
        
        # Clean up
        parent_gui.root.destroy()
        
        print("\n✅ All debug mode tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing debug mode: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_debug_mode_ui():
    """Test the debug mode UI elements"""
    print("\n🧪 Testing Debug Mode UI Elements")
    print("=" * 60)
    
    try:
        # Create a mock parent GUI
        class MockParentGUI:
            def __init__(self):
                self.root = tk.Tk()
                self.root.withdraw()  # Hide the window
        
        # Create a mock notebook
        parent_gui = MockParentGUI()
        notebook = ttk.Notebook(parent_gui.root)
        
        # Create the SequenceBuilderTab
        from tabs.sequence_builder_tab import SequenceBuilderTab
        sequence_builder = SequenceBuilderTab(parent_gui, notebook)
        
        # Check if debug button exists
        if hasattr(sequence_builder, 'debug_btn'):
            print("✅ Debug button exists")
            print(f"   Button text: {sequence_builder.debug_btn.cget('text')}")
            print(f"   Button background: {sequence_builder.debug_btn.cget('bg')}")
        else:
            print("❌ Debug button not found")
            return False
        
        # Check if status label exists
        if hasattr(sequence_builder, 'esp32_status_label'):
            print("✅ ESP32 status label exists")
            print(f"   Status text: {sequence_builder.esp32_status_label.cget('text')}")
        else:
            print("❌ ESP32 status label not found")
            return False
        
        # Clean up
        parent_gui.root.destroy()
        
        print("✅ Debug mode UI tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing debug mode UI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all debug mode tests"""
    print("🚀 Starting SequenceBuilderTab Debug Mode Tests")
    print("=" * 60)
    
    tests = [
        ("Debug Mode Functionality", test_debug_mode_functionality),
        ("Debug Mode UI", test_debug_mode_ui),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All debug mode tests passed! Debug functionality is working correctly.")
    else:
        print("⚠️ Some debug mode tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
