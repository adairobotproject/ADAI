#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the new movement buttons in SequenceBuilderTab
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_movement_buttons():
    """Test the new movement buttons functionality"""
    print("🧪 Testing Movement Buttons Functionality")
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
        
        # Test 1: Check if movement buttons exist
        print("\n🔍 Test 1: Checking movement buttons existence...")
        if hasattr(sequence_builder, 'save_movement_btn'):
            print("✅ Save Movement button exists")
        else:
            print("❌ Save Movement button not found")
            return False
        
        if hasattr(sequence_builder, 'delete_last_movement_btn'):
            print("✅ Delete Last Movement button exists")
        else:
            print("❌ Delete Last Movement button not found")
            return False
        
        # Test 2: Check initial button states
        print("\n🔍 Test 2: Checking initial button states...")
        save_state = sequence_builder.save_movement_btn.cget('state')
        delete_state = sequence_builder.delete_last_movement_btn.cget('state')
        
        print(f"   Save Movement button state: {save_state}")
        print(f"   Delete Last Movement button state: {delete_state}")
        
        # Both should be disabled initially
        if save_state == "disabled" and delete_state == "disabled":
            print("✅ Initial button states are correct")
        else:
            print("❌ Initial button states are incorrect")
            return False
        
        # Test 3: Enable debug mode and start recording
        print("\n🔍 Test 3: Enabling debug mode and starting recording...")
        sequence_builder.toggle_debug_mode()
        sequence_builder.toggle_recording()
        
        print(f"   ESP32 connected: {sequence_builder.esp32_connected}")
        print(f"   Is recording: {sequence_builder.is_recording}")
        print(f"   Current movement: {sequence_builder.current_movement}")
        
        # Test 4: Add some actions and check button states
        print("\n🔍 Test 4: Adding actions and checking button states...")
        
        # Add a test action manually
        if sequence_builder.current_movement:
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
        
        # Update movement buttons
        sequence_builder.update_movement_buttons()
        
        # Check button states after adding action
        save_state = sequence_builder.save_movement_btn.cget('state')
        delete_state = sequence_builder.delete_last_movement_btn.cget('state')
        
        print(f"   Save Movement button state after action: {save_state}")
        print(f"   Delete Last Movement button state after action: {delete_state}")
        
        # Save button should be enabled, delete still disabled
        if save_state == "normal" and delete_state == "disabled":
            print("✅ Button states are correct after adding action")
        else:
            print("❌ Button states are incorrect after adding action")
            return False
        
        # Test 5: Save movement
        print("\n🔍 Test 5: Testing save movement functionality...")
        try:
            # This should work now
            sequence_builder.save_current_movement()
            print("✅ Save movement functionality works")
            print(f"   Recorded movements: {len(sequence_builder.recorded_actions)}")
        except Exception as e:
            print(f"❌ Save movement failed: {e}")
            return False
        
        # Test 6: Check button states after saving movement
        print("\n🔍 Test 6: Checking button states after saving movement...")
        sequence_builder.update_movement_buttons()
        
        save_state = sequence_builder.save_movement_btn.cget('state')
        delete_state = sequence_builder.delete_last_movement_btn.cget('state')
        
        print(f"   Save Movement button state after saving: {save_state}")
        print(f"   Delete Last Movement button state after saving: {delete_state}")
        
        # Save button should be disabled (no actions), delete should be enabled
        if save_state == "disabled" and delete_state == "normal":
            print("✅ Button states are correct after saving movement")
        else:
            print("❌ Button states are incorrect after saving movement")
            return False
        
        # Test 7: Test delete last movement
        print("\n🔍 Test 7: Testing delete last movement functionality...")
        try:
            # This should work now
            sequence_builder.delete_last_movement()
            print("✅ Delete last movement functionality works")
            print(f"   Remaining movements: {len(sequence_builder.recorded_actions)}")
        except Exception as e:
            print(f"❌ Delete last movement failed: {e}")
            return False
        
        # Test 8: Check final button states
        print("\n🔍 Test 8: Checking final button states...")
        sequence_builder.update_movement_buttons()
        
        save_state = sequence_builder.save_movement_btn.cget('state')
        delete_state = sequence_builder.delete_last_movement_btn.cget('state')
        
        print(f"   Final Save Movement button state: {save_state}")
        print(f"   Final Delete Last Movement button state: {delete_state}")
        
        # Both should be disabled again
        if save_state == "disabled" and delete_state == "disabled":
            print("✅ Final button states are correct")
        else:
            print("❌ Final button states are incorrect")
            return False
        
        # Clean up
        parent_gui.root.destroy()
        
        print("\n✅ All movement button tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing movement buttons: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_movement_workflow():
    """Test the complete movement workflow"""
    print("\n🧪 Testing Complete Movement Workflow")
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
        
        # Enable debug mode and start recording
        sequence_builder.toggle_debug_mode()
        sequence_builder.toggle_recording()
        
        print("📝 Testing complete movement workflow...")
        
        # Workflow: Create multiple movements
        movements_to_create = 3
        
        for i in range(movements_to_create):
            print(f"\n   Creating movement {i+1}...")
            
            # Add some actions to current movement
            for j in range(2):  # 2 actions per movement
                test_action = {
                    "command": "BRAZOS",
                    "parameters": {
                        "BI": 10 + i, "BD": 40 + i, "FI": 80 + i, "FD": 90 + i, 
                        "HI": 80 + i, "HD": 80 + i, "PD": 45 + i
                    },
                    "duration": 1000,
                    "description": f"Test Position {i+1}-{j+1}",
                    "timestamp": 1234567890.0 + i + j
                }
                sequence_builder.current_movement["actions"].append(test_action)
            
            print(f"   Added {len(sequence_builder.current_movement['actions'])} actions to movement {i+1}")
            
            # Save the movement
            sequence_builder.save_current_movement()
            print(f"   Movement {i+1} saved successfully")
        
        print(f"\n✅ Created {len(sequence_builder.recorded_actions)} movements")
        
        # Test saving the complete sequence
        print("\n💾 Testing sequence save...")
        try:
            # Mock filedialog
            import tkinter.filedialog
            original_filedialog = tkinter.filedialog.asksaveasfilename
            tkinter.filedialog.asksaveasfilename = lambda *args, **kwargs: "test_workflow_sequence.json"
            
            sequence_builder.save_sequence()
            print("✅ Sequence save works correctly")
            
            # Restore original filedialog
            tkinter.filedialog.asksaveasfilename = original_filedialog
            
        except Exception as e:
            print(f"❌ Sequence save failed: {e}")
            return False
        
        # Clean up
        parent_gui.root.destroy()
        
        print("\n✅ Complete movement workflow test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing movement workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all movement button tests"""
    print("🚀 Starting Movement Button Tests")
    print("=" * 60)
    
    tests = [
        ("Movement Buttons Functionality", test_movement_buttons),
        ("Complete Movement Workflow", test_movement_workflow),
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
        print("🎉 All movement button tests passed!")
        print("\n📋 Summary of new features:")
        print("✅ Save Movement button works correctly")
        print("✅ Delete Last Movement button works correctly")
        print("✅ Button states update automatically")
        print("✅ Complete movement workflow works")
        print("✅ Sequence saving works with new system")
    else:
        print("⚠️ Some movement button tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
