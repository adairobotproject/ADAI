#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the Demo System in ClassBuilderTab
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_demo_system_functionality():
    """Test the demo system functionality"""
    print("🧪 Testing Demo System in ClassBuilderTab")
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
        
        # Create the ClassBuilderTab
        from tabs.class_builder_tab import ClassBuilderTab
        class_builder = ClassBuilderTab(parent_gui, notebook)
        
        print("✅ ClassBuilderTab created successfully")
        
        # Test 1: Check if demo variables exist
        print("\n🔍 Test 1: Checking demo variables existence...")
        if hasattr(class_builder, 'demo_enabled'):
            print("✅ demo_enabled variable exists")
        else:
            print("❌ demo_enabled variable not found")
            return False
        
        if hasattr(class_builder, 'demo_pdf_path'):
            print("✅ demo_pdf_path variable exists")
        else:
            print("❌ demo_pdf_path variable not found")
            return False
        
        if hasattr(class_builder, 'demo_sequences'):
            print("✅ demo_sequences variable exists")
        else:
            print("❌ demo_sequences variable not found")
            return False
        
        # Test 2: Check initial demo state
        print("\n🔍 Test 2: Checking initial demo state...")
        print(f"   Demo enabled: {class_builder.demo_enabled.get()}")
        print(f"   Demo PDF path: {class_builder.demo_pdf_path.get()}")
        print(f"   Demo sequences count: {len(class_builder.demo_sequences)}")
        
        # Test 3: Test demo enable/disable
        print("\n🔍 Test 3: Testing demo enable/disable...")
        class_builder.demo_enabled.set(True)
        print(f"   Demo enabled set to: {class_builder.demo_enabled.get()}")
        
        # Test 4: Test demo PDF selection (mock)
        print("\n🔍 Test 4: Testing demo PDF selection...")
        mock_pdf_path = "test_demo.pdf"
        class_builder.demo_pdf_path.set(mock_pdf_path)
        print(f"   Demo PDF path set to: {class_builder.demo_pdf_path.get()}")
        
        # Test 5: Test demo sequence management
        print("\n🔍 Test 5: Testing demo sequence management...")
        
        # Add a mock demo sequence
        mock_sequence = {
            "page": 1,
            "sequence_file": "test_sequence.json",
            "sequence_name": "test_sequence.json",
            "description": "Test demo sequence",
            "enabled": True
        }
        
        class_builder.demo_sequences.append(mock_sequence)
        print(f"   Added mock demo sequence")
        print(f"   Demo sequences count: {len(class_builder.demo_sequences)}")
        
        # Test 6: Test demo sequence code generation
        print("\n🔍 Test 6: Testing demo sequence code generation...")
        try:
            demo_code = class_builder._generate_demo_sequences_code()
            print("✅ Demo sequence code generation works")
            print(f"   Generated code: {demo_code}")
        except Exception as e:
            print(f"❌ Demo sequence code generation failed: {e}")
            return False
        
        # Test 7: Test class generation with demo
        print("\n🔍 Test 7: Testing class generation with demo...")
        try:
            # Set required fields
            class_builder.class_title_var.set("Test Class with Demo")
            class_builder.class_subject_var.set("Robots Médicos")
            
            # Generate class code
            class_code = class_builder._generate_class_code()
            print("✅ Class generation with demo works")
            print(f"   Generated code length: {len(class_code)} characters")
            
            # Check if demo code is included
            if "DEMO_SEQUENCES" in class_code:
                print("✅ Demo sequences configuration included in generated code")
            else:
                print("❌ Demo sequences configuration not found in generated code")
                return False
                
        except Exception as e:
            print(f"❌ Class generation with demo failed: {e}")
            return False
        
        # Clean up
        parent_gui.root.destroy()
        
        print("\n✅ All demo system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing demo system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_demo_workflow():
    """Test the complete demo workflow"""
    print("\n🧪 Testing Complete Demo Workflow")
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
        
        # Create the ClassBuilderTab
        from tabs.class_builder_tab import ClassBuilderTab
        class_builder = ClassBuilderTab(parent_gui, notebook)
        
        print("✅ ClassBuilderTab created successfully")
        
        # Complete demo workflow
        print("📝 Testing complete demo workflow...")
        
        # Step 1: Enable demo
        class_builder.demo_enabled.set(True)
        print("   ✅ Demo enabled")
        
        # Step 2: Set demo PDF path
        class_builder.demo_pdf_path.set("demo_presentation.pdf")
        print("   ✅ Demo PDF path set")
        
        # Step 3: Add multiple demo sequences
        demo_sequences = [
            {
                "page": 1,
                "sequence_file": "demo_intro.json",
                "sequence_name": "demo_intro.json",
                "description": "Demo de introducción",
                "enabled": True
            },
            {
                "page": 3,
                "sequence_file": "demo_main.json",
                "sequence_name": "demo_main.json",
                "description": "Demo principal",
                "enabled": True
            },
            {
                "page": 5,
                "sequence_file": "demo_conclusion.json",
                "sequence_name": "demo_conclusion.json",
                "description": "Demo de conclusión",
                "enabled": True
            }
        ]
        
        for seq in demo_sequences:
            class_builder.demo_sequences.append(seq)
            print(f"   ✅ Added demo sequence for page {seq['page']}")
        
        # Step 4: Generate class code
        class_builder.class_title_var.set("Clase con Sistema de Demos")
        class_builder.class_subject_var.set("Robots Médicos")
        
        class_code = class_builder._generate_class_code()
        print("   ✅ Class code generated")
        
        # Step 5: Verify demo integration
        if "DEMO_SEQUENCES" in class_code and "demo_intro.json" in class_code:
            print("   ✅ Demo sequences properly integrated in class code")
        else:
            print("   ❌ Demo sequences not properly integrated")
            return False
        
        # Clean up
        parent_gui.root.destroy()
        
        print("\n✅ Complete demo workflow test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing demo workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all demo system tests"""
    print("🚀 Starting Demo System Tests")
    print("=" * 60)
    
    tests = [
        ("Demo System Functionality", test_demo_system_functionality),
        ("Complete Demo Workflow", test_demo_workflow),
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
        print("🎉 All demo system tests passed!")
        print("\n📋 Summary of new features:")
        print("✅ Demo system variables properly initialized")
        print("✅ Demo enable/disable functionality works")
        print("✅ Demo PDF path management works")
        print("✅ Demo sequence management works")
        print("✅ Demo sequence code generation works")
        print("✅ Class generation includes demo configuration")
        print("✅ Complete demo workflow works")
    else:
        print("⚠️ Some demo system tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

