#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script for the ESP32Tab class fix
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("🔧 Verifying ESP32Tab class fix...\n")

    try:
        # Test 1: Import the module
        print("1. Testing import...")
        from tabs.esp32_tab import ESP32Tab, MockBooleanVar
        print("✅ Import successful")

        # Test 2: Test MockBooleanVar
        print("\n2. Testing MockBooleanVar...")
        mock_var = MockBooleanVar(True)
        assert mock_var.get() == True
        mock_var.set(False)
        assert mock_var.get() == False
        print("✅ MockBooleanVar works correctly")

        # Test 3: Test class instantiation without tkinter
        print("\n3. Testing class instantiation...")
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

        esp32_tab = ESP32Tab(mock_parent, mock_notebook)
        print("✅ ESP32Tab instance created successfully")

        # Test 4: Check attributes
        print("\n4. Checking attributes...")
        print(f"   Tab name: {esp32_tab.tab_name}")
        print(f"   ESP32 real mode: {esp32_tab.esp32_real_mode.get()}")
        print(f"   Connected: {esp32_tab.esp32_connected}")

        # Test 5: Test _create_boolean_var method
        print("\n5. Testing _create_boolean_var method...")
        test_var = esp32_tab._create_boolean_var(True)
        assert test_var.get() == True
        print("✅ _create_boolean_var works correctly")

        print("\n🎉 All tests passed! The ESP32Tab class should now work correctly.")
        print("\n📝 Summary of fixes:")
        print("   - Added safe BooleanVar creation with fallback to MockBooleanVar")
        print("   - Class can now be instantiated even without tkinter context")
        print("   - All tkinter variables are created safely")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
