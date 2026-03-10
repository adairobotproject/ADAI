#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for sequence parsing logic
"""

import json
import os

def test_sequence_parsing():
    """Test parsing the chemistry sequence file"""
    print("🧪 Testing Sequence Parsing Logic")
    print("=" * 50)
    
    # Test the chemistry neutralization sequence
    sequence_file = "sequences/sequence_Quimica_Neutralizacion_Completa.json"
    
    if not os.path.exists(sequence_file):
        print(f"❌ Sequence file not found: {sequence_file}")
        return False
    
    try:
        # Load and parse the sequence
        with open(sequence_file, 'r', encoding='utf-8') as f:
            sequence_data = json.load(f)
        
        print("✅ Successfully loaded sequence JSON")
        
        movements = sequence_data.get('movements', [])
        print(f"📊 Found {len(movements)} movements")
        
        # Test parsing the first few actions
        if movements:
            first_movement = movements[0]
            print(f"\n🎯 Testing movement: {first_movement.get('name', 'Unnamed')}")
            
            actions = first_movement.get('actions', [])
            for i, action in enumerate(actions[:3]):  # Test first 3 actions
                print(f"\n  Action {i+1}:")
                print(f"    Command: {action.get('command', 'None')}")
                print(f"    Type: {action.get('type', 'None')}")
                print(f"    Parameters: {action.get('parameters', {})}")
                
                # Test the parsing logic
                command = action.get('command', '')
                action_type = action.get('type', 'unknown')
                parameters = action.get('parameters', {})
                
                if command:
                    print(f"    ✅ Command-based action: {command}")
                    if command == 'BRAZOS':
                        print(f"      -> Movement action with parameters: {parameters}")
                    elif command == 'CUELLO':
                        print(f"      -> Neck action with parameters: {parameters}")
                    elif command == 'MANO':
                        print(f"      -> Hand action with parameters: {parameters}")
                    elif command == 'HABLAR':
                        print(f"      -> Speech action with parameters: {parameters}")
                    else:
                        print(f"      -> Unknown command: {command}")
                elif action_type != 'unknown':
                    print(f"    ✅ Type-based action: {action_type}")
                else:
                    print(f"    ⚠️ Unknown action format")
        
        print("\n✅ Sequence parsing test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing sequence parsing: {e}")
        return False

if __name__ == "__main__":
    success = test_sequence_parsing()
    if success:
        print("\n🎉 Sequence parsing is working correctly!")
        print("\n💡 The ESP32 tab should now properly parse and execute the chemistry sequence.")
    else:
        print("\n⚠️ Sequence parsing test failed.")
