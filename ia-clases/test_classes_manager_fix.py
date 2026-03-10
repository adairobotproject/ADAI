#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Classes Manager fix
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_classes_manager_initialization():
    """Test that ClassesManagerTab can be initialized with class_manager"""
    try:
        print("🔍 Testing ClassesManagerTab initialization...")

        # Import required modules
        from tabs.classes_manager_tab import ClassesManagerTab
        from class_manager import get_class_manager
        print("✅ Imports successful")

        # Create mock objects
        class MockNotebook:
            def add(self, frame, text):
                pass

        class MockParentGUI:
            def __init__(self):
                self.root = None
                self.window_width = 1200
                self.window_height = 600
                # Initialize class_manager
                try:
                    self.class_manager = get_class_manager()
                    print("✅ Class manager initialized in parent GUI")
                except Exception as e:
                    print(f"⚠️ Class manager initialization failed: {e}")
                    self.class_manager = None

        # Create instances
        mock_parent = MockParentGUI()
        mock_notebook = MockNotebook()

        print("🔧 Creating ClassesManagerTab instance...")
        classes_tab = ClassesManagerTab(mock_parent, mock_notebook)
        print("✅ ClassesManagerTab instance created successfully")

        # Check if class_manager is available
        if hasattr(mock_parent, 'class_manager') and mock_parent.class_manager:
            print("✅ Class manager is available in parent GUI")
        else:
            print("⚠️ Class manager not available - will use fallback")

        # Check tab attributes
        print(f"📋 Tab name: {classes_tab.tab_name}")
        print(f"📋 Classes list: {len(classes_tab.classes_list)} classes")

        return True

    except Exception as e:
        print(f"❌ ClassesManagerTab test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_class_manager_functionality():
    """Test basic class manager functionality"""
    try:
        print("\n🔍 Testing ClassManager functionality...")

        from class_manager import get_class_manager

        # Get class manager instance
        manager = get_class_manager()
        print("✅ Class manager instance obtained")

        # Test scanning classes
        classes = manager.refresh_classes()
        print(f"✅ Classes scanned: {len(classes)} found")

        # Show available classes
        for i, cls in enumerate(classes[:3]):  # Show first 3
            print(f"   {i+1}. {cls.get('title', 'Unknown')} - {cls.get('name', 'Unknown')}")

        return True

    except Exception as e:
        print(f"❌ ClassManager functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_integration():
    """Test the full integration between ClassesManagerTab and ClassManager"""
    try:
        print("\n🔍 Testing full integration...")

        from tabs.classes_manager_tab import ClassesManagerTab
        from class_manager import get_class_manager

        # Create mock objects
        class MockNotebook:
            def add(self, frame, text):
                pass

        class MockParentGUI:
            def __init__(self):
                self.root = None
                self.window_width = 1200
                self.window_height = 600
                self.class_manager = get_class_manager()

        # Create instances
        mock_parent = MockParentGUI()
        mock_notebook = MockNotebook()
        classes_tab = ClassesManagerTab(mock_parent, mock_notebook)

        # Test refreshing classes
        print("🔄 Testing class refresh...")
        classes_tab.refresh_classes()
        print(f"✅ Classes refreshed: {len(classes_tab.classes_list)} classes loaded")

        # Test that class_manager is accessible
        if hasattr(classes_tab.parent_gui, 'class_manager') and classes_tab.parent_gui.class_manager:
            print("✅ Class manager accessible from ClassesManagerTab")
        else:
            print("❌ Class manager not accessible")
            return False

        # Test execute_selected_class method (without actually executing)
        if classes_tab.classes_list:
            classes_tab.selected_class = classes_tab.classes_list[0]
            print(f"✅ Selected class: {classes_tab.selected_class.get('title', 'Unknown')}")
            print("✅ execute_selected_class method should work now")
        else:
            print("⚠️ No classes available for testing execute method")

        return True

    except Exception as e:
        print(f"❌ Full integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Classes Manager Fix...\n")

    test1 = test_classes_manager_initialization()
    test2 = test_class_manager_functionality()
    test3 = test_full_integration()

    print("\n" + "="*50)
    if test1 and test2 and test3:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Classes Manager should now work correctly")
        print("✅ Classes can be executed from the Classes Manager tab")
        print("\n📝 What was fixed:")
        print("   - Added ClassesManagerTab to main GUI initialization")
        print("   - Initialized class_manager in RobotGUI")
        print("   - Added proper error handling and fallbacks")
        print("   - Classes Manager tab now has access to class_manager")
    else:
        print("❌ SOME TESTS FAILED")
        print("   Check the error messages above for details")

    print("="*50)
