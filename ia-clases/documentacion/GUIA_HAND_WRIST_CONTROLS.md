# Hand and Wrist Controls Guide for SequenceBuilderTab

## Overview

The SequenceBuilderTab now includes comprehensive hand and wrist controls that allow you to control individual fingers and wrist movements for both hands. These controls are integrated with the ESP32 robot and can be used for recording sequences.

## Features

### ✋ Hand Controls
- **Individual Finger Control**: Control each finger (thumb, index, middle, ring, pinky) independently
- **Wrist Control**: Control wrist rotation for both hands
- **Real-time ESP32 Integration**: Direct control of the robot's hands
- **Sequence Recording**: All hand movements can be recorded and played back

### 🎬 Sequence Integration
- **Recording**: Hand movements are automatically recorded when creating sequences
- **Playback**: Hand movements are executed during sequence playback
- **JSON Export**: Hand movements are saved in the sequence JSON format

## UI Layout

### Hands Control Section
The hands control section is located below the "Arms Control" section and includes:

#### Left Hand Controls
- **Thumb**: 0-180 degrees
- **Index**: 0-180 degrees  
- **Middle**: 0-180 degrees
- **Ring**: 0-180 degrees
- **Pinky**: 0-180 degrees
- **Wrist**: 0-160 degrees

#### Right Hand Controls
- **Thumb**: 0-180 degrees
- **Index**: 0-180 degrees
- **Middle**: 0-180 degrees
- **Ring**: 0-180 degrees
- **Pinky**: 0-180 degrees
- **Wrist**: 0-160 degrees

### Quick Action Buttons
- **✋ Open Hands**: Opens both hands
- **✊ Close Hands**: Closes both hands
- **✌️ Peace**: Makes peace sign with both hands

## Usage Instructions

### 1. Connecting to ESP32
Before using hand controls, you must connect to the ESP32:
1. Click "🔗 Connect" in the ESP32 Connection panel
2. Wait for the status to show "🟢 Connected"
3. Test the connection with "🧪 Test" button

### 2. Controlling Individual Fingers
1. **Adjust Sliders**: Use the sliders for each finger to set the desired angle
2. **Real-time Control**: Changes are sent immediately to the ESP32
3. **Recording**: If recording is active, movements are added to the sequence

### 3. Controlling Wrists
1. **Wrist Rotation**: Use the wrist sliders to rotate the wrists
2. **Range**: 0-160 degrees for natural wrist movement
3. **Independent Control**: Each wrist can be controlled independently

### 4. Recording Hand Movements
1. **Start Recording**: Click "🔴 Start Recording"
2. **Move Controls**: Adjust finger and wrist positions
3. **Capture Position**: Click "📍 Capture Position" to save current state
4. **Stop Recording**: Click "⏹️ Stop Recording" when done

### 5. Playing Sequences with Hand Movements
1. **Load Sequence**: Load a saved sequence with hand movements
2. **Play**: Click "▶️ Play" to execute the sequence
3. **Monitor**: Watch the robot execute hand movements along with arm movements

## Technical Details

### ESP32 Communication
- **Finger Commands**: Sent as individual servo commands
- **Wrist Commands**: Sent as wrist rotation commands
- **Gesture Commands**: Sent as predefined gesture commands

### Sequence Format
Hand movements are stored in the sequence JSON as:

```json
{
  "command": "MANO",
  "parameters": {
    "M": "left",           // "left", "right", or "ambas"
    "DEDO": "pulgar",      // finger name (for finger control)
    "TIPO": "muñeca",      // "muñeca" (for wrist control)
    "GESTO": "ABRIR",      // gesture name (for gestures)
    "ANG": 90              // angle value
  },
  "description": "Left thumb movement",
  "timestamp": 1234567890.123
}
```

### Finger Mapping
The UI uses English finger names that are mapped to ESP32 Spanish names:

| English | ESP32 Spanish |
|---------|---------------|
| thumb   | pulgar        |
| index   | indice        |
| middle  | medio         |
| ring    | anular        |
| pinky   | menique       |

### Supported Gestures
- **ABRIR**: Open hands
- **CERRAR**: Close hands
- **PAZ**: Peace sign
- **SALUDO**: Wave gesture
- **ABRAZO**: Hug gesture
- **OK**: OK sign
- **SEÑALAR**: Point gesture

## Safety Considerations

### Angle Limits
- **Fingers**: 0-180 degrees (safe range for servo motors)
- **Wrists**: 0-160 degrees (prevents over-rotation)
- **Default Positions**: All fingers start at 90 degrees (neutral)

### Movement Safety
- **Gradual Changes**: Sliders provide smooth, gradual movement
- **Real-time Feedback**: Immediate response prevents sudden movements
- **Error Handling**: Invalid angles are automatically clamped to safe ranges

## Troubleshooting

### Common Issues

#### Hand Controls Not Responding
1. **Check ESP32 Connection**: Ensure ESP32 is connected and status shows "🟢 Connected"
2. **Test Connection**: Use the "🧪 Test" button to verify communication
3. **Check ESP32 Services**: Verify that ESP32 services are available

#### Finger Movements Not Accurate
1. **Calibrate Servos**: Ensure robot servos are properly calibrated
2. **Check Angle Ranges**: Verify that angles are within safe limits (0-180)
3. **Test Individual Fingers**: Test each finger individually

#### Sequence Playback Issues
1. **Check Sequence Format**: Ensure sequence JSON is properly formatted
2. **Verify Commands**: Check that MANO commands are correctly structured
3. **Test Playback**: Try playing a simple sequence first

### Error Messages

#### "ESP32 services not available"
- **Solution**: Install or configure ESP32 services
- **Check**: Verify `services/esp32_services/` directory exists

#### "Failed to connect to ESP32"
- **Solution**: Check ESP32 IP address and network connection
- **Check**: Verify ESP32 is powered on and accessible

#### "Invalid finger angle"
- **Solution**: Ensure angle is between 0-180 degrees
- **Check**: Use the slider controls instead of manual input

## Examples

### Basic Hand Sequence
```json
{
  "name": "Basic_Hand_Sequence",
  "title": "Basic Hand Movement Demo",
  "movements": [
    {
      "id": 1,
      "name": "Open_Hands",
      "actions": [
        {
          "command": "MANO",
          "parameters": {
            "M": "ambas",
            "GESTO": "ABRIR"
          },
          "description": "Open both hands",
          "duration": 1000
        }
      ]
    },
    {
      "id": 2,
      "name": "Finger_Dance",
      "actions": [
        {
          "command": "MANO",
          "parameters": {
            "M": "left",
            "DEDO": "pulgar",
            "ANG": 180
          },
          "description": "Left thumb up",
          "duration": 500
        },
        {
          "command": "MANO",
          "parameters": {
            "M": "right",
            "DEDO": "indice",
            "ANG": 0
          },
          "description": "Right index down",
          "duration": 500
        }
      ]
    }
  ]
}
```

### Complex Hand Gesture Sequence
```json
{
  "name": "Complex_Hand_Gesture",
  "title": "Complex Hand Gesture Demo",
  "movements": [
    {
      "id": 1,
      "name": "Peace_Sign",
      "actions": [
        {
          "command": "MANO",
          "parameters": {
            "M": "ambas",
            "GESTO": "PAZ"
          },
          "description": "Peace sign with both hands",
          "duration": 2000
        }
      ]
    },
    {
      "id": 2,
      "name": "Wrist_Rotation",
      "actions": [
        {
          "command": "MANO",
          "parameters": {
            "M": "left",
            "TIPO": "muñeca",
            "ANG": 160
          },
          "description": "Left wrist full rotation",
          "duration": 1000
        },
        {
          "command": "MANO",
          "parameters": {
            "M": "right",
            "TIPO": "muñeca",
            "ANG": 0
          },
          "description": "Right wrist counter-rotation",
          "duration": 1000
        }
      ]
    }
  ]
}
```

## Integration with Classes

The hand and wrist controls can be integrated with the class system:

### Class Demo Sequences
- **Chemistry Demos**: Use hand gestures to point to different elements
- **Physics Demos**: Use finger movements to demonstrate concepts
- **Biology Demos**: Use hand gestures to show anatomical features

### Class Progress Integration
- **Hand Gestures**: Can be used to signal class progress
- **Finger Counting**: Use fingers to count or show numbers
- **Pointing**: Use index finger to point to important information

## Future Enhancements

### Planned Features
- **Hand Gesture Recognition**: AI-powered gesture recognition
- **Custom Gestures**: User-defined hand gestures
- **Hand Tracking**: Integration with computer vision for hand tracking
- **Haptic Feedback**: Force feedback for more precise control

### Advanced Controls
- **Finger Combinations**: Predefined finger combinations
- **Hand Postures**: Complete hand posture presets
- **Animation Sequences**: Smooth hand movement animations
- **Synchronization**: Synchronized hand and arm movements

## Support

For technical support or questions about hand and wrist controls:

1. **Check Documentation**: Review this guide and related documentation
2. **Run Tests**: Use `test_sequence_builder_hand_controls.py` to verify functionality
3. **Check Logs**: Review console output for error messages
4. **ESP32 Status**: Verify ESP32 connection and configuration

## Version History

- **v1.0**: Initial implementation with basic finger and wrist controls
- **v1.1**: Added gesture buttons and improved UI layout
- **v1.2**: Enhanced sequence recording and playback
- **v1.3**: Added comprehensive error handling and safety features

---

*This guide covers the complete hand and wrist control system for the SequenceBuilderTab. For additional information, refer to the main SequenceBuilderTab documentation.*
