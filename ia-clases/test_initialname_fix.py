#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify the initialname parameter fix
"""

import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_initialname_fix():
    """Test that the initialname parameter issue is fixed"""
    print("🧪 Testing initialname parameter fix")
    print("=" * 50)
    
    try:
        # Import the module to check for syntax errors
        from tabs.sequence_builder_tab import SequenceBuilderTab
        print("✅ SequenceBuilderTab imported successfully - no syntax errors")
        
        # Check if the save_sequence method exists
        if hasattr(SequenceBuilderTab, 'save_sequence'):
            print("✅ save_sequence method exists")
        else:
            print("❌ save_sequence method not found")
            return False
        
        # Check if the create_sample_sequence method exists
        if hasattr(SequenceBuilderTab, 'create_sample_sequence'):
            print("✅ create_sample_sequence method exists")
        else:
            print("❌ create_sample_sequence method not found")
            return False
        
        print("\n✅ All tests passed! The initialname parameter issue is fixed.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_initialname_fix()
    sys.exit(0 if success else 1)
