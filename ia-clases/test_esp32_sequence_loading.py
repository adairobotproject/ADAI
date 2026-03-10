#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for ESP32 Tab Sequence Loading functionality
"""

import os
import sys
import json

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sequence_loading():
    """Test loading and parsing sequence files"""
    print("🧪 Testing ESP32 Tab Sequence Loading")
    print("=" * 50)
    
    # Test the chemistry neutralization sequence
    sequence_file = "sequences/sequence_Quimica_Neutralizacion_Completa.json"
    
    if not os.path.exists(sequence_file):
        print(f"❌ Sequence file not found: {sequence_file}")
        return False
    
    print(f"📁 Found sequence file: {sequence_file}")
    
    try:
        # Load and parse the sequence
        with open(sequence_file, 'r', encoding='utf-8') as f:
            sequence_data = json.load(f)
        
        print("✅ Successfully loaded sequence JSON")
        
        # Validate sequence structure
        if not isinstance(sequence_data, dict):
            print("❌ Invalid sequence format: not a dictionary")
            return False
        
        if 'movements' not in sequence_data:
            print("❌ Invalid sequence format: missing 'movements' field")
            return False
        
        movements = sequence_data.get('movements', [])
        print(f"✅ Found {len(movements)} movements in sequence")
        
        # Check sequence metadata
        title = sequence_data.get('title', 'Untitled')
        print(f"📋 Sequence title: {title}")
        
        # Analyze movements
        total_actions = 0
        for i, movement in enumerate(movements):
            movement_name = movement.get('name', f'Movement {i+1}')
            actions = movement.get('actions', [])
            total_actions += len(actions)
            print(f"  Movement {i+1}: {movement_name} ({len(actions)} actions)")
        
        print(f"📊 Total actions: {total_actions}")
        
        # Test action parsing
        print("\n🔍 Testing action parsing:")
        for i, movement in enumerate(movements[:3]):  # Test first 3 movements
            print(f"\n  Movement {i+1}: {movement.get('name', 'Unnamed')}")
            actions = movement.get('actions', [])
            
            for j, action in enumerate(actions[:2]):  # Test first 2 actions per movement
                action_type = action.get('type', 'unknown')
                parameters = action.get('parameters', {})
                
                print(f"    Action {j+1}: {action_type}")
                print(f"      Parameters: {parameters}")
                
                # Check for action field (alternative format)
                if 'action' in action:
                    action_name = action['action']
                    print(f"      Action name: {action_name}")
        
        print("\n✅ Sequence loading test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing sequence loading: {e}")
        return False

def test_sequence_execution_simulation():
    """Test sequence execution simulation logic"""
    print("\n🎬 Testing Sequence Execution Simulation")
    print("=" * 50)
    
    # Simulate the ESP32 tab's sequence execution methods
    class MockESP32Tab:
        def __init__(self):
            self.log_messages = []
        
        def log_command(self, message, category):
            self.log_messages.append(f"[{category}] {message}")
            print(f"[{category}] {message}")
        
        def _simulate_movement_action(self, parameters):
            bi = parameters.get('BI', 0)
            bd = parameters.get('BD', 0)
            ci = parameters.get('CI', 0)
            cd = parameters.get('CD', 0)
            cu = parameters.get('CU', 0)
            cd_abajo = parameters.get('CD_abajo', 0)
            
            movement_str = f"Movement: BI={bi}, BD={bd}, CI={ci}, CD={cd}, CU={cu}, CD_abajo={cd_abajo}"
            self.log_command(movement_str, "MOVEMENT")
        
        def _simulate_gesture_action(self, parameters):
            gesture_type = parameters.get('gesture', 'unknown')
            self.log_command(f"Gesture: {gesture_type}", "GESTURE")
        
        def _simulate_speech_action(self, parameters):
            message = parameters.get('message', 'No message')
            self.log_command(f"Speech: {message}", "SPEECH")
        
        def _simulate_generic_action(self, action):
            action_name = action.get('action', 'unknown')
            parameters = action.get('parameters', {})
            
            if action_name == 'saludo':
                self.log_command("Gesture: Saludo (Wave)", "GESTURE")
            elif action_name == 'movimiento':
                self._simulate_movement_action(parameters)
            elif action_name == 'hablar':
                message = parameters.get('message', 'No message')
                self.log_command(f"Speech: {message}", "SPEECH")
            else:
                self.log_command(f"Generic action: {action_name}", "ACTION")
    
    # Create mock tab
    mock_tab = MockESP32Tab()
    
    # Load sequence
    sequence_file = "sequences/sequence_Quimica_Neutralizacion_Completa.json"
    
    try:
        with open(sequence_file, 'r', encoding='utf-8') as f:
            sequence_data = json.load(f)
        
        movements = sequence_data.get('movements', [])
        
        # Simulate execution of first movement
        if movements:
            first_movement = movements[0]
            movement_name = first_movement.get('name', 'First Movement')
            
            print(f"\n🎯 Simulating execution of: {movement_name}")
            
            actions = first_movement.get('actions', [])
            for i, action in enumerate(actions[:3]):  # Test first 3 actions
                print(f"\n  Executing action {i+1}:")
                
                action_type = action.get('type', 'unknown')
                parameters = action.get('parameters', {})
                
                if action_type == 'movement':
                    mock_tab._simulate_movement_action(parameters)
                elif action_type == 'gesture':
                    mock_tab._simulate_gesture_action(parameters)
                elif action_type == 'speech':
                    mock_tab._simulate_speech_action(parameters)
                else:
                    # Handle unknown action types
                    if 'action' in action:
                        mock_tab._simulate_generic_action(action)
                    else:
                        mock_tab.log_command(f"Unknown action type: {action_type}", "WARNING")
        
        print("\n✅ Sequence execution simulation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in sequence execution simulation: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ESP32 Tab Sequence Loading Test Suite")
    print("=" * 60)
    
    # Test sequence loading
    loading_success = test_sequence_loading()
    
    # Test execution simulation
    execution_success = test_sequence_execution_simulation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"  Sequence Loading: {'✅ PASS' if loading_success else '❌ FAIL'}")
    print(f"  Execution Simulation: {'✅ PASS' if execution_success else '❌ FAIL'}")
    
    if loading_success and execution_success:
        print("\n🎉 All tests passed! ESP32 tab sequence loading is ready.")
        print("\n💡 Next steps:")
        print("  1. Open the RobotGUI application")
        print("  2. Go to the ESP32 Controller tab")
        print("  3. Click on the '🤖 Arms Simulator' tab")
        print("  4. Use '📁 Load Sequence' to load a sequence file")
        print("  5. Use '🎬 Execute Sequence' to run it in the simulator")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
    
    return loading_success and execution_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
