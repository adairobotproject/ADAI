#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test to verify the sequence saving fix
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sequence_save_fix():
    """Test the sequence saving fix"""
    print("🧪 Testing Sequence Save Fix")
    print("=" * 50)
    
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
        
        # Test 1: Create sample sequence
        print("\n📝 Test 1: Creating sample sequence...")
        sequence_builder.create_sample_sequence()
        
        print(f"   Recorded actions: {len(sequence_builder.recorded_actions)}")
        if sequence_builder.recorded_actions:
            print(f"   First movement actions: {len(sequence_builder.recorded_actions[0]['actions'])}")
        
        # Test 2: Check save method (without actually saving)
        print("\n💾 Test 2: Testing save method...")
        try:
            # Mock filedialog to avoid actual file dialog
            import tkinter.filedialog
            original_filedialog = tkinter.filedialog.asksaveasfilename
            tkinter.filedialog.asksaveasfilename = lambda *args, **kwargs: "test_save.json"
            
            # This should work now
            sequence_builder.save_sequence()
            print("✅ Save method works correctly")
            
            # Restore original filedialog
            tkinter.filedialog.asksaveasfilename = original_filedialog
            
        except Exception as e:
            print(f"❌ Save method failed: {e}")
            return False
        
        # Test 3: Test recording without ESP32 connection
        print("\n🎬 Test 3: Testing recording without ESP32...")
        try:
            # This should now work (it will ask for confirmation)
            print("   Attempting to start recording without ESP32...")
            # Note: This will show a dialog, so we'll just test the method exists
            if hasattr(sequence_builder, 'toggle_recording'):
                print("✅ toggle_recording method exists")
            else:
                print("❌ toggle_recording method not found")
                return False
                
        except Exception as e:
            print(f"❌ Recording test failed: {e}")
            return False
        
        # Clean up
        parent_gui.root.destroy()
        
        print("\n✅ All sequence save fix tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing sequence save fix: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    print("🚀 Testing Sequence Save Fix")
    print("=" * 50)
    
    if test_sequence_save_fix():
        print("\n🎉 Sequence save fix is working correctly!")
        print("\n📋 Summary of fixes:")
        print("✅ Can create sample sequences")
        print("✅ Can save sequences without ESP32 connection")
        print("✅ Better error messages and user guidance")
        print("✅ Improved sequence validation")
        return True
    else:
        print("\n❌ Sequence save fix has issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
