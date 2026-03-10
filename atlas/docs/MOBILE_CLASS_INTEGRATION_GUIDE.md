# Mobile Class Integration Guide

## Overview

This guide documents the integration between the ReactLynx mobile application and the Python robot GUI class management system. The mobile app can now discover, view, and execute classes that are generated and managed by the Python application.

## Architecture

```
┌─────────────────┐    HTTP API    ┌──────────────────┐
│   Mobile App    │ ◄────────────► │  Python Robot    │
│  (ReactLynx)    │                │     GUI          │
│                 │                │                  │
│ • ClassesScreen │                │ • ClassManager   │
│ • RobotAPI      │                │ • MobileAPI      │
│ • ConfigManager │                │ • ClassBuilder   │
└─────────────────┘                └──────────────────┘
```

## API Endpoints

### 1. Get Available Classes
- **Endpoint**: `GET /api/classes`
- **Description**: Retrieves all available classes with their metadata
- **Response**:
```json
{
  "success": true,
  "classes": [
    {
      "name": "ejemplo_clase.py",
      "title": "Ejemplo de Clase",
      "subject": "Tecnología",
      "description": "Una clase de ejemplo",
      "duration": "45 min",
      "created_date": "2024-01-15",
      "status": "available"
    }
  ]
}
```

### 2. Execute Class
- **Endpoint**: `POST /api/class/execute`
- **Description**: Executes a specific class by name
- **Request Body**:
```json
{
  "class_name": "ejemplo_clase.py"
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Class executed successfully",
  "class_name": "ejemplo_clase.py"
}
```

## Mobile App Components

### 1. ClassesScreen.jsx
The main component for displaying and managing classes.

**Key Features**:
- **Dynamic Loading**: Automatically loads classes from the Python server
- **Real-time Updates**: Refreshes class list every 30 seconds
- **Connection Status**: Shows connection status with visual indicators
- **Class Execution**: Allows users to start/stop classes remotely
- **Error Handling**: Graceful error handling with retry functionality

**State Management**:
```javascript
const [classes, setClasses] = useState([])
const [isPlaying, setIsPlaying] = useState(false)
const [isConnected, setIsConnected] = useState(false)
const [loading, setLoading] = useState(true)
const [error, setError] = useState(null)
```

### 2. RobotAPI.js
Enhanced API service for communicating with the Python robot GUI.

**New Methods**:
- `getAvailableClasses()`: Fetches classes from `/api/classes`
- `startClass(className)`: Executes class via `/api/class/execute`
- `getClassDetails(className)`: Gets specific class details

**Configuration**:
- Automatically updates base URL when configuration changes
- Handles connection status updates
- Provides detailed error reporting

## User Interface Features

### 1. Class Cards
Each class is displayed in a card format showing:
- **Title**: Class name
- **Subject**: Academic subject
- **Duration**: Estimated class duration
- **Status**: Available, running, or completed
- **File Path**: Python file name
- **Actions**: Start/Stop and Details buttons

### 2. Connection Status
- **Connected**: Green indicator, full functionality
- **Disconnected**: Warning banner with retry option
- **Loading**: Spinner while fetching data
- **Error**: Error message with retry button

### 3. Active Class Banner
When a class is running:
- Shows current executing class name
- Provides stop button
- Green background with progress indicator

### 4. Class Details View
Detailed view showing:
- Complete class information
- File metadata
- Creation date
- Execution controls

## Integration Flow

### 1. App Startup
1. Mobile app initializes with stored configuration
2. Tests connection to Python server
3. Loads available classes automatically
4. Updates connection status

### 2. Class Discovery
1. App requests classes from `/api/classes`
2. Python server queries ClassManager
3. Returns formatted class list with metadata
4. Mobile app displays classes in grid

### 3. Class Execution
1. User taps "Iniciar" on a class card
2. Mobile app sends POST to `/api/class/execute`
3. Python server executes class in background
4. Returns success/error response
5. Mobile app updates UI accordingly

### 4. Real-time Updates
1. App refreshes class list every 30 seconds
2. Checks for new classes or status changes
3. Updates UI without user interaction
4. Maintains current selection state

## Error Handling

### 1. Connection Errors
- **Network Issues**: Shows connection warning
- **Server Down**: Displays error with retry option
- **Timeout**: Automatic retry with exponential backoff

### 2. Class Execution Errors
- **Class Not Found**: Shows error message
- **Execution Failed**: Displays error details
- **Permission Issues**: Shows appropriate warning

### 3. Data Loading Errors
- **Invalid Response**: Graceful fallback to empty state
- **Parse Errors**: Error message with retry
- **Missing Data**: Uses default values where possible

## Configuration

### 1. Server Configuration
The mobile app uses the existing configuration system:
- **Host**: Python server IP address
- **Port**: Server port (default: 8000)
- **Auto-discovery**: Automatic configuration updates

### 2. API Configuration
- **Base URL**: Constructed from host and port
- **Timeout**: 5 seconds for GET, 10 seconds for POST
- **Headers**: JSON content type for all requests

## Testing

### 1. Manual Testing
1. Start Python server: `python robot_gui_conmodulos.py`
2. Open mobile app in browser
3. Navigate to Classes screen
4. Verify classes load correctly
5. Test class execution

### 2. Automated Testing
Run the test script:
```bash
cd ia-clases
python test_mobile_integration.py
```

### 3. Test Scenarios
- **No Classes**: Empty state display
- **Single Class**: Basic functionality
- **Multiple Classes**: List management
- **Connection Loss**: Error handling
- **Class Execution**: Start/stop functionality

## Troubleshooting

### 1. Classes Not Loading
- Check Python server is running
- Verify API endpoints are accessible
- Check network connectivity
- Review server logs for errors

### 2. Class Execution Fails
- Verify class file exists in `clases/` directory
- Check class file syntax
- Review execution logs
- Ensure proper permissions

### 3. Connection Issues
- Verify server configuration
- Check firewall settings
- Test with curl or Postman
- Review mobile app logs

## Future Enhancements

### 1. Planned Features
- **Real-time Status**: WebSocket for live updates
- **Class Scheduling**: Schedule classes for later execution
- **Progress Tracking**: Show class execution progress
- **Notifications**: Push notifications for class events

### 2. Performance Improvements
- **Caching**: Cache class metadata locally
- **Pagination**: Handle large numbers of classes
- **Optimistic Updates**: Immediate UI feedback
- **Background Sync**: Sync when app is in background

### 3. User Experience
- **Search/Filter**: Find classes quickly
- **Favorites**: Mark frequently used classes
- **History**: Track executed classes
- **Analytics**: Usage statistics

## Security Considerations

### 1. API Security
- **Input Validation**: Validate all API inputs
- **Rate Limiting**: Prevent abuse
- **Authentication**: Consider adding auth if needed
- **CORS**: Proper CORS configuration

### 2. Data Protection
- **Local Storage**: Secure configuration storage
- **Network Security**: Use HTTPS in production
- **Error Handling**: Don't expose sensitive data

## Conclusion

The mobile integration provides a seamless way for users to interact with the robot class management system. The implementation follows ReactLynx best practices and provides a robust, user-friendly interface for class discovery and execution.

The system is designed to be extensible, allowing for future enhancements while maintaining backward compatibility with existing functionality.
