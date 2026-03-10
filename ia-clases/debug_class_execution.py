#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test class execution and identify issues
"""

import sys
import os
import subprocess
import time
import traceback

def test_class_execution_direct(class_name):
    """Test direct execution of a class"""
    print(f"Testing direct execution of: {class_name}")
    print("=" * 50)
    
    try:
        # Find the class in its folder
        class_name_no_ext = class_name.replace('.py', '')
        class_path = os.path.join("clases", class_name_no_ext, class_name)
        if not os.path.exists(class_path):
            print(f"❌ Class file not found: {class_path}")
            return False
        
        print(f"✅ Class file found: {class_path}")
        
        # Test direct execution
        result = subprocess.run([
            sys.executable, 
            class_path
        ], 
        capture_output=True,  # Capture output to see errors
        text=True,
        timeout=30,  # 30 seconds timeout
        cwd=os.getcwd())
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            print(f"✅ {class_name} executed successfully")
            return True
        else:
            print(f"❌ {class_name} failed with code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {class_name} timed out")
        return True
    except Exception as e:
        print(f"❌ Error executing {class_name}: {e}")
        traceback.print_exc()
        return False

def test_class_execution_via_manager(class_name):
    """Test class execution via Class Manager"""
    print(f"\nTesting Class Manager execution of: {class_name}")
    print("=" * 50)
    
    try:
        # Import class manager
        sys.path.insert(0, ".")
        from class_manager import get_class_manager
        
        class_manager = get_class_manager()
        
        # Set up callbacks
        def on_executed(class_info, output):
            print(f"✅ Class executed: {class_info['title']}")
            print(f"Output: {output}")
        
        def on_error(error_msg):
            print(f"❌ Class error: {error_msg}")
        
        class_manager.on_class_executed = on_executed
        class_manager.on_class_error = on_error
        
        # Test execution
        print(f"🚀 Executing {class_name} via Class Manager...")
        success = class_manager.execute_class(class_name)
        
        if success:
            print(f"✅ {class_name} started successfully via Class Manager")
            
            # Wait a bit for execution
            time.sleep(5)
            
            # Check if still running
            if class_manager.is_class_running():
                print(f"✅ {class_name} is still running")
                
                # Test stop functionality
                print(f"⏹️ Stopping {class_name}...")
                stop_success = class_manager.stop_class_execution()
                
                if stop_success:
                    print(f"✅ {class_name} stopped successfully")
                else:
                    print(f"⚠️ {class_name} stop failed")
            else:
                print(f"⚠️ {class_name} finished quickly")
            
            return True
        else:
            print(f"❌ {class_name} failed to start via Class Manager")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {class_name} via Class Manager: {e}")
        traceback.print_exc()
        return False

def test_simple_class():
    """Test with a simple class that should work"""
    print("\nCreating and testing a simple class...")
    print("=" * 50)
    
    simple_class_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Test Class
"""

import time
import sys

def main():
    print("Simple test class starting...")
    print("This is a test message")
    time.sleep(2)
    print("Simple test class completed successfully")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
'''
    
    # Save simple class
    simple_class_path = "clases/test_simple_debug.py"
    with open(simple_class_path, 'w', encoding='utf-8') as f:
        f.write(simple_class_content)
    
    print(f"✅ Simple class created: {simple_class_path}")
    
    # Test execution
    result = test_class_execution_direct("test_simple_debug.py")
    
    # Clean up
    if os.path.exists(simple_class_path):
        os.remove(simple_class_path)
    
    return result

def main():
    """Main debug function"""
    print("Class Execution Debug")
    print("=" * 60)
    
    # Test simple class first
    simple_ok = test_simple_class()
    
    # Test existing classes
    classes_to_test = [
        "ejemplo_clase_simple.py",
        "test_simple_class.py",
        "test_nueva_clase.py"
    ]
    
    results = {}
    
    for class_path in classes_to_test:
        print(f"\n{'='*60}")
        print(f"TESTING: {class_path}")
        print(f"{'='*60}")
        
        # Test direct execution
        direct_ok = test_class_execution_direct(class_path)
        
        # Test class manager execution
        manager_ok = test_class_execution_via_manager(class_path)
        
        results[class_path] = {
            'direct': direct_ok,
            'manager': manager_ok
        }
    
    # Summary
    print(f"\n{'='*60}")
    print("DEBUG SUMMARY")
    print(f"{'='*60}")
    
    print(f"Simple class test: {'✅ PASSED' if simple_ok else '❌ FAILED'}")
    
    for class_path, result in results.items():
        status = "✅ PASSED" if result['direct'] and result['manager'] else "❌ FAILED"
        print(f"{class_path}: {status}")
        if not result['direct']:
            print(f"  - Direct execution failed")
        if not result['manager']:
            print(f"  - Manager execution failed")
    
    print(f"\n{'='*60}")
    if simple_ok:
        print("✅ Simple class works - basic execution is functional")
    else:
        print("❌ Simple class failed - there's a fundamental issue")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()
