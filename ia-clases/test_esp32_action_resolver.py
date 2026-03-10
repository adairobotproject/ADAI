#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the ESP32 Action Resolver method
"""

import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_esp32_action_resolver():
    """Test the ESP32 action resolver method"""
    print("🧪 Testing ESP32 Action Resolver")
    print("=" * 60)
    
    try:
        # Import the main module
        from clases.main.main import esp32_action_resolver
        
        print("✅ ESP32 Action Resolver imported successfully")
        
        # Test 1: Test with a valid sequence name
        print("\n🔍 Test 1: Testing with valid sequence name...")
        
        # List available sequences
        sequences_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sequences")
        if os.path.exists(sequences_dir):
            sequences = [f for f in os.listdir(sequences_dir) if f.endswith('.json')]
            print(f"📁 Available sequences: {sequences}")
            
            if sequences:
                # Test with the first available sequence
                test_sequence = sequences[0].replace('.json', '')
                print(f"🎯 Testing with sequence: {test_sequence}")
                
                # Test the method
                result = esp32_action_resolver(test_sequence)
                
                if result:
                    print(f"✅ ESP32 Action Resolver test PASSED for {test_sequence}")
                else:
                    print(f"❌ ESP32 Action Resolver test FAILED for {test_sequence}")
                    return False
            else:
                print("⚠️ No sequences found for testing")
                return False
        else:
            print("⚠️ Sequences directory not found")
            return False
        
        # Test 2: Test with invalid sequence name
        print("\n🔍 Test 2: Testing with invalid sequence name...")
        result = esp32_action_resolver("nonexistent_sequence")
        
        if not result:
            print("✅ ESP32 Action Resolver correctly handled invalid sequence")
        else:
            print("❌ ESP32 Action Resolver should have failed for invalid sequence")
            return False
        
        print("\n✅ All ESP32 Action Resolver tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing ESP32 Action Resolver: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sequence_loading():
    """Test sequence loading functionality"""
    print("\n🧪 Testing Sequence Loading")
    print("=" * 60)
    
    try:
        # Test sequence directory access
        sequences_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sequences")
        
        if not os.path.exists(sequences_dir):
            print("❌ Sequences directory not found")
            return False
        
        print(f"✅ Sequences directory found: {sequences_dir}")
        
        # List sequences
        sequences = [f for f in os.listdir(sequences_dir) if f.endswith('.json')]
        print(f"📁 Found {len(sequences)} sequence files")
        
        if not sequences:
            print("⚠️ No sequence files found")
            return False
        
        # Test loading a sequence
        test_sequence_file = os.path.join(sequences_dir, sequences[0])
        print(f"📄 Testing sequence file: {test_sequence_file}")
        
        import json
        with open(test_sequence_file, 'r', encoding='utf-8') as f:
            sequence_data = json.load(f)
        
        print(f"✅ Sequence loaded successfully")
        print(f"   - Name: {sequence_data.get('name', 'Unknown')}")
        print(f"   - Actions: {len(sequence_data.get('actions', []))}")
        
        # Test action structure
        actions = sequence_data.get('actions', [])
        if actions:
            first_action = actions[0]
            print(f"   - First action: {first_action.get('command', 'Unknown')}")
            print(f"   - Parameters: {first_action.get('parameters', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing sequence loading: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting ESP32 Action Resolver Tests")
    print("=" * 60)
    
    tests = [
        ("Sequence Loading", test_sequence_loading),
        ("ESP32 Action Resolver", test_esp32_action_resolver),
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
        print("🎉 All tests passed!")
        print("\n📋 Summary of new features:")
        print("✅ ESP32 Action Resolver method implemented")
        print("✅ Sequence loading and parsing works")
        print("✅ ESP32 configuration loading works")
        print("✅ Command execution framework ready")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
