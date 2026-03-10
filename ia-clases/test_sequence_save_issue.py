#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to diagnose sequence saving issues in SequenceBuilderTab
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sequence_saving_issue():
    """Test the sequence saving functionality"""
    print("🧪 Testing Sequence Saving Issue")
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
        
        # Check initial state
        print(f"\n📊 Initial State:")
        print(f"   ESP32 connected: {sequence_builder.esp32_connected}")
        print(f"   Debug mode: {sequence_builder.debug_mode}")
        print(f"   Is recording: {sequence_builder.is_recording}")
        print(f"   Recorded actions: {len(sequence_builder.recorded_actions)}")
        print(f"   Current movement: {sequence_builder.current_movement}")
        
        # Test 1: Try to save without recording (should fail)
        print(f"\n🧪 Test 1: Try to save without recording")
        try:
            sequence_builder.save_sequence()
            print("❌ Test 1 FAILED: Should not be able to save without recording")
        except Exception as e:
            print(f"✅ Test 1 PASSED: Correctly prevented saving without recording")
        
        # Test 2: Enable debug mode
        print(f"\n🧪 Test 2: Enable debug mode")
        sequence_builder.toggle_debug_mode()
        print(f"   ESP32 connected after debug: {sequence_builder.esp32_connected}")
        print(f"   Debug mode after debug: {sequence_builder.debug_mode}")
        
        # Test 3: Start recording
        print(f"\n🧪 Test 3: Start recording")
        sequence_builder.toggle_recording()
        print(f"   Is recording after start: {sequence_builder.is_recording}")
        print(f"   Current movement after start: {sequence_builder.current_movement}")
        
        # Test 4: Add some actions manually
        print(f"\n🧪 Test 4: Add actions manually")
        if sequence_builder.current_movement:
            # Add a test action
            test_action = {
                "command": "BRAZOS",
                "parameters": {
                    "BI": 10, "BD": 40, "FI": 80, "FD": 90, 
                    "HI": 80, "HD": 80, "PD": 45
                },
                "duration": 1000,
                "description": "Test Home Position",
                "timestamp": 1234567890.0
            }
            sequence_builder.current_movement["actions"].append(test_action)
            print(f"   Added test action to current movement")
            print(f"   Current movement actions: {len(sequence_builder.current_movement['actions'])}")
        
        # Test 5: Stop recording
        print(f"\n🧪 Test 5: Stop recording")
        sequence_builder.toggle_recording()
        print(f"   Is recording after stop: {sequence_builder.is_recording}")
        print(f"   Recorded actions after stop: {len(sequence_builder.recorded_actions)}")
        print(f"   Current movement after stop: {sequence_builder.current_movement}")
        
        # Test 6: Try to save again
        print(f"\n🧪 Test 6: Try to save with recorded actions")
        try:
            # Mock the filedialog to avoid actual file dialog
            original_asksaveasfilename = sequence_builder.parent_gui.root.tk.call
            def mock_asksaveasfilename(*args, **kwargs):
                return "test_sequence.json"
            
            # Temporarily replace the filedialog
            import tkinter.filedialog
            original_filedialog = tkinter.filedialog.asksaveasfilename
            tkinter.filedialog.asksaveasfilename = mock_asksaveasfilename
            
            sequence_builder.save_sequence()
            print("✅ Test 6 PASSED: Successfully called save_sequence")
            
            # Restore original filedialog
            tkinter.filedialog.asksaveasfilename = original_filedialog
            
        except Exception as e:
            print(f"❌ Test 6 FAILED: Error saving sequence: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 7: Check if recorded_actions is properly populated
        print(f"\n🧪 Test 7: Check recorded_actions content")
        print(f"   Recorded actions count: {len(sequence_builder.recorded_actions)}")
        if sequence_builder.recorded_actions:
            print(f"   First movement: {sequence_builder.recorded_actions[0]}")
            print(f"   First movement actions: {len(sequence_builder.recorded_actions[0]['actions'])}")
        else:
            print("   ❌ No recorded actions found!")
        
        # Clean up
        parent_gui.root.destroy()
        
        print("\n✅ All sequence saving tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing sequence saving: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_sequence_creation():
    """Test creating a sequence manually"""
    print("\n🧪 Testing Manual Sequence Creation")
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
        
        # Enable debug mode
        sequence_builder.toggle_debug_mode()
        
        # Manually create a sequence
        print("📝 Creating manual sequence...")
        
        # Create a test movement
        test_movement = {
            "id": 1,
            "name": "Test_Movement_1",
            "actions": [
                {
                    "command": "BRAZOS",
                    "parameters": {
                        "BI": 10, "BD": 40, "FI": 80, "FD": 90, 
                        "HI": 80, "HD": 80, "PD": 45
                    },
                    "duration": 1000,
                    "description": "Home Position",
                    "timestamp": 1234567890.0
                },
                {
                    "command": "MANO",
                    "parameters": {
                        "M": "derecha",
                        "GESTO": "SALUDO"
                    },
                    "duration": 1000,
                    "description": "Wave Gesture",
                    "timestamp": 1234567891.0
                }
            ]
        }
        
        # Add to recorded actions
        sequence_builder.recorded_actions.append(test_movement)
        
        print(f"✅ Manual sequence created with {len(sequence_builder.recorded_actions)} movements")
        print(f"   First movement has {len(sequence_builder.recorded_actions[0]['actions'])} actions")
        
        # Test saving
        print("💾 Testing save with manual sequence...")
        try:
            # Mock the filedialog
            import tkinter.filedialog
            original_filedialog = tkinter.filedialog.asksaveasfilename
            tkinter.filedialog.asksaveasfilename = lambda *args, **kwargs: "manual_test_sequence.json"
            
            sequence_builder.save_sequence()
            print("✅ Manual sequence save test PASSED")
            
            # Restore original filedialog
            tkinter.filedialog.asksaveasfilename = original_filedialog
            
        except Exception as e:
            print(f"❌ Manual sequence save test FAILED: {e}")
            import traceback
            traceback.print_exc()
        
        # Clean up
        parent_gui.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing manual sequence creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all sequence saving tests"""
    print("🚀 Starting Sequence Saving Issue Tests")
    print("=" * 60)
    
    tests = [
        ("Sequence Saving Issue", test_sequence_saving_issue),
        ("Manual Sequence Creation", test_manual_sequence_creation),
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
        print("🎉 All sequence saving tests passed!")
    else:
        print("⚠️ Some sequence saving tests failed. Check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
