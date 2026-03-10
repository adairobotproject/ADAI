#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for SequenceBuilderTab with Hand and Wrist Controls
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sequence_builder_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing SequenceBuilderTab imports...")
    
    try:
        from tabs.sequence_builder_tab import SequenceBuilderTab
        print("✅ SequenceBuilderTab imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SequenceBuilderTab: {e}")
        return False
    
    try:
        from services.esp32_services.esp32_client import ESP32Client
        print("✅ ESP32Client imported successfully")
    except ImportError as e:
        print(f"⚠️ ESP32Client not available: {e}")
    
    try:
        from services.esp32_services.esp32_config_binary import ESP32BinaryConfig
        print("✅ ESP32BinaryConfig imported successfully")
    except ImportError as e:
        print(f"⚠️ ESP32BinaryConfig not available: {e}")
    
    return True

def test_sequence_builder_creation():
    """Test creating the SequenceBuilderTab"""
    print("\n🧪 Testing SequenceBuilderTab creation...")
    
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
        
        # Check basic attributes
        print(f"   Tab name: {sequence_builder.tab_name}")
        print(f"   ESP32 available: {hasattr(sequence_builder, 'esp32_client')}")
        print(f"   Recording state: {sequence_builder.is_recording}")
        
        # Check sequence variables
        print(f"   Sequence name: {sequence_builder.sequence_name.get()}")
        print(f"   Sequence title: {sequence_builder.sequence_title.get()}")
        print(f"   Recorded actions: {len(sequence_builder.recorded_actions)}")
        
        # Clean up
        parent_gui.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create SequenceBuilderTab: {e}")
        return False

def test_hand_controls_variables():
    """Test that hand and wrist control variables are created"""
    print("\n🧪 Testing hand and wrist control variables...")
    
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
        
        # Test left hand variables
        left_hand_vars = [
            'left_thumb_var', 'left_index_var', 'left_middle_var',
            'left_ring_var', 'left_pinky_var', 'left_wrist_var'
        ]
        
        for var_name in left_hand_vars:
            if hasattr(sequence_builder, var_name):
                var = getattr(sequence_builder, var_name)
                print(f"✅ {var_name}: {var.get()}")
            else:
                print(f"❌ Missing {var_name}")
                return False
        
        # Test right hand variables
        right_hand_vars = [
            'right_thumb_var', 'right_index_var', 'right_middle_var',
            'right_ring_var', 'right_pinky_var', 'right_wrist_var'
        ]
        
        for var_name in right_hand_vars:
            if hasattr(sequence_builder, var_name):
                var = getattr(sequence_builder, var_name)
                print(f"✅ {var_name}: {var.get()}")
            else:
                print(f"❌ Missing {var_name}")
                return False
        
        # Clean up
        parent_gui.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test hand control variables: {e}")
        return False

def test_hand_control_methods():
    """Test that hand and wrist control methods exist"""
    print("\n🧪 Testing hand and wrist control methods...")
    
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
        
        # Test required methods
        required_methods = [
            'on_finger_change', 'on_wrist_change', 'hand_gesture'
        ]
        
        for method_name in required_methods:
            if hasattr(sequence_builder, method_name):
                method = getattr(sequence_builder, method_name)
                print(f"✅ {method_name}: {method.__name__}")
            else:
                print(f"❌ Missing method {method_name}")
                return False
        
        # Clean up
        parent_gui.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test hand control methods: {e}")
        return False

def test_sequence_recording_with_hands():
    """Test sequence recording with hand controls"""
    print("\n🧪 Testing sequence recording with hand controls...")
    
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
        
        # Simulate recording state
        sequence_builder.is_recording = True
        sequence_builder.current_movement = {
            "id": 1,
            "name": "Test_Movement",
            "actions": []
        }
        
        # Test adding finger action
        sequence_builder.add_action_to_sequence("MANO", {
            "M": "left",
            "DEDO": "pulgar",
            "ANG": 90
        }, "Left thumb test")
        
        # Test adding wrist action
        sequence_builder.add_action_to_sequence("MANO", {
            "M": "right",
            "TIPO": "muñeca",
            "ANG": 80
        }, "Right wrist test")
        
        # Test adding hand gesture
        sequence_builder.add_action_to_sequence("MANO", {
            "M": "ambas",
            "GESTO": "ABRIR"
        }, "Open hands gesture")
        
        # Check recorded actions
        if sequence_builder.current_movement and sequence_builder.current_movement["actions"]:
            print(f"✅ Recorded {len(sequence_builder.current_movement['actions'])} actions")
            for i, action in enumerate(sequence_builder.current_movement["actions"]):
                print(f"   Action {i+1}: {action['command']} - {action['description']}")
        else:
            print("❌ No actions recorded")
            return False
        
        # Clean up
        parent_gui.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test sequence recording: {e}")
        return False

def test_esp32_integration():
    """Test ESP32 integration with hand controls"""
    print("\n🧪 Testing ESP32 integration with hand controls...")
    
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
        
        # Check ESP32 integration
        print(f"   ESP32 client available: {sequence_builder.esp32_client is not None}")
        print(f"   ESP32 config available: {sequence_builder.esp32_config is not None}")
        print(f"   ESP32 connected: {sequence_builder.esp32_connected}")
        
        # Test finger mapping
        finger_map = {
            'thumb': 'pulgar',
            'index': 'indice', 
            'middle': 'medio',
            'ring': 'anular',
            'pinky': 'menique'
        }
        
        print("   Finger mapping:")
        for eng, esp in finger_map.items():
            print(f"     {eng} -> {esp}")
        
        # Clean up
        parent_gui.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test ESP32 integration: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting SequenceBuilderTab Hand Controls Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_sequence_builder_imports),
        ("Creation", test_sequence_builder_creation),
        ("Hand Control Variables", test_hand_controls_variables),
        ("Hand Control Methods", test_hand_control_methods),
        ("Sequence Recording", test_sequence_recording_with_hands),
        ("ESP32 Integration", test_esp32_integration),
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
        print("🎉 All tests passed! Hand and wrist controls are working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
