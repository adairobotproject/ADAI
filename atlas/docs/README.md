# 🤖 Robot Atlas - Mobile Control App

A ReactLynx mobile application for controlling the InMoov robot through a web-based API. This app allows you to control robot movements, execute pre-programmed classes, and monitor robot status from any mobile device.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Development Server
```bash
npm run dev
```

### 3. Configure Server Connection
1. Open the app in LynxExplorer
2. **EASIEST**: Tap the **🚀** (rocket) icon for Quick Setup
3. **OR** Tap the **🔧** (wrench) icon for detailed configuration
4. **OR** Tap the **⚡** (lightning) icon for advanced testing
5. Enter your computer's IP address (e.g., `10.136.166.163`)
6. The app will save configuration and test connection automatically

### 4. Start the Robot Server
```bash
cd ../ia-clases
python robot_gui.py
```

## 📱 App Features

### 🎮 Robot Control
- **Head Movement**: Control X, Y, Z rotation
- **Arm Control**: Shoulder, elbow, wrist movements
- **Hand Gestures**: Individual finger control
- **Movement Presets**: Pre-programmed gestures (salute, applause, etc.)
- **Emergency Stop**: Immediate halt of all movements

### 🎓 Educational Classes
- **Pre-programmed Sequences**: Educational robot demonstrations
- **Movement + Speech**: Synchronized robot actions and explanations
- **Class Management**: Start, stop, and monitor class progress
- **Multiple Classes**: Different educational content available

### 🔧 Server Configuration
- **Custom IP Setup**: Connect to robot server from any network device
- **Port Configuration**: Flexible port settings
- **Connection Testing**: Real-time connection verification
- **Persistent Settings**: Configuration saved between sessions

### 📊 Connection Monitoring
- **Real-time Status**: Live connection indicators
- **Server Configuration**: Current IP and port display
- **Connection Logs**: Detailed connection history
- **Quick Access**: Direct links to configuration

## 🔧 Configuration

### Network Setup
The app supports connecting to the robot server from any device on the same network:

- **Same Computer**: Use `localhost` as the host
- **Local Network**: Use your computer's IP address (e.g., `10.136.166.163`)
- **Custom Ports**: Configure any port that matches the robot server

### Finding Your IP Address

**Windows:**
```bash
ipconfig
```

**Mac/Linux:**
```bash
ifconfig
# or
ip addr
```

Look for your local IP address (usually starts with `192.168.x.x`)

## 📋 Navigation

- **⌂ Home**: App overview and quick actions
- **☰ Dashboard**: System status and statistics
- **● Control**: Manual robot control interface
- **★ Classes**: Educational robot classes
- **⚙ Connections**: Connection status and monitoring
- **🔧 Config**: Detailed server configuration
- **🚀 Quick Setup**: Easy one-step configuration
- **⚡ ConfigTest**: Advanced testing and debugging
- **🧪 Test**: General functionality testing
- **📱 Simple**: Minimal test interface

## 🛠️ Development

### Project Structure
```
src/
├── components/          # React components
│   ├── ControlScreen.jsx      # Robot control interface
│   ├── ClassesScreen.jsx      # Educational classes
│   ├── ServerConfigScreen.jsx # Server configuration
│   └── ...
├── services/           # API services
│   └── RobotAPI.js     # Robot communication service
└── App.jsx             # Main application
```

### Key Components

**RobotAPI.js**: Handles all communication with the robot server
- Configuration management
- HTTP request handling
- Connection testing
- Error handling

**ServerConfigScreen.jsx**: Server configuration interface
- IP/hostname input
- Port configuration
- Connection testing
- Settings persistence

## 📚 Documentation

- **[IP Configuration Guide](./IP_CONFIGURATION_GUIDE.md)**: Detailed setup instructions
- **[Mobile Robot Integration](./MOBILE_ROBOT_INTEGRATION.md)**: Integration with robot_gui.py
- **[Mobile Tab Guide](./MOBILE_TAB_GUIDE.md)**: Robot GUI mobile tab documentation

## 🔗 Integration

This app integrates with the `robot_gui.py` Python application:

- **HTTP API**: RESTful API for robot control
- **Real-time Communication**: Live status updates
- **CORS Support**: Cross-origin request handling
- **Error Handling**: Robust error management

## 🚨 Troubleshooting

### Common Issues

**Connection Failed:**
1. Verify both devices are on the same WiFi network
2. Check that `robot_gui.py` is running
3. Ensure the IP address and port are correct
4. Check firewall settings

**App Not Responding:**
1. Restart the LynxExplorer app
2. Clear app cache if available
3. Verify network connectivity
4. Check server logs in `robot_gui.py`

### Getting Help

1. Check the **🔧 Configuration** screen for connection status
2. Review the **⚙ Connections** tab for detailed information
3. Consult the troubleshooting guides in the documentation
4. Check the `robot_gui.py` console for server-side errors

## 🎯 Future Features

- [ ] WebSocket support for real-time updates
- [ ] Voice control integration
- [ ] Custom movement recording
- [ ] Advanced gesture recognition
- [ ] Multi-robot support
- [ ] Offline mode with cached commands

---

**🎉 Ready to control your robot from anywhere on your network!**
