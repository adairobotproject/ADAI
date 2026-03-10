import { useState, useCallback, useEffect } from '@lynx-js/react'
import robotAPI from '../services/RobotAPI'

export function ControlScreen() {
  const [activeTab, setActiveTab] = useState('status')
  const [robotStatus, setRobotStatus] = useState('idle') // idle, active, error
  const [currentPosition, setCurrentPosition] = useState({
    head: { x: 0, y: 0, z: 0 },
    leftArm: { shoulder: 0, elbow: 0, wrist: 0 },
    rightArm: { shoulder: 0, elbow: 0, wrist: 0 },
    torso: { rotation: 0, tilt: 0 },
    leftHand: { thumb: 0, index: 0, middle: 0, ring: 0, pinky: 0 },
    rightHand: { thumb: 0, index: 0, middle: 0, ring: 0, pinky: 0 }
  })

  const [batteryLevel, setBatteryLevel] = useState(87)
  const [temperature, setTemperature] = useState(42.5)
  const [connectionStatus, setConnectionStatus] = useState('connected')
  const [isConnected, setIsConnected] = useState(false)

  // Connect to robot and fetch initial data
  useEffect(() => {
    'background only'
    const connectToRobot = async () => {
      try {
        const connected = await robotAPI.testConnection()
        setIsConnected(connected)
        
        if (connected) {
          // Fetch initial robot status
          const statusResult = await robotAPI.getRobotStatus()
          if (statusResult.success) {
            const status = statusResult.data
            setRobotStatus(status.status)
            setBatteryLevel(status.battery)
            setTemperature(status.temperature)
            setConnectionStatus(status.connection)
          }
          
          // Fetch initial position
          const positionResult = await robotAPI.getRobotPosition()
          if (positionResult.success) {
            setCurrentPosition(positionResult.data)
          }
        }
      } catch (error) {
        console.error('Failed to connect to robot:', error)
        setIsConnected(false)
      }
    }
    
    connectToRobot()
    
    // Set up periodic status updates (reduced frequency to prevent excessive requests)
    const statusInterval = setInterval(connectToRobot, 15000) // Update every 15 seconds
    
    return () => clearInterval(statusInterval)
  }, [])

  const handleMovement = useCallback(async (part, axis, value) => {
    'background only'
    if (!isConnected) {
      console.log('Robot not connected')
      return
    }
    
    try {
      let moveResult
      
      if (part === 'head') {
        const newPosition = { ...currentPosition.head, [axis]: value }
        moveResult = await robotAPI.moveHead(newPosition.x, newPosition.y, newPosition.z)
      } else if (part === 'leftArm' || part === 'rightArm') {
        const newPosition = { ...currentPosition[part], [axis]: value }
        moveResult = await robotAPI.moveArm(part, newPosition.shoulder, newPosition.elbow, newPosition.wrist)
      }
      
      if (moveResult && moveResult.success) {
        setCurrentPosition(prev => ({
          ...prev,
          [part]: {
            ...prev[part],
            [axis]: value
          }
        }))
        console.log(`Successfully moved ${part} ${axis} to ${value}`)
      } else {
        console.error('Failed to move robot:', moveResult?.error)
      }
    } catch (error) {
      console.error('Error moving robot:', error)
    }
  }, [isConnected, currentPosition])

  const handleHandGesture = useCallback(async (hand, finger, value) => {
    'background only'
    if (!isConnected) {
      console.log('Robot not connected')
      return
    }
    
    try {
      const newFingers = { ...currentPosition[hand], [finger]: value }
      const moveResult = await robotAPI.moveHand(hand, newFingers)
      
      if (moveResult.success) {
        setCurrentPosition(prev => ({
          ...prev,
          [hand]: {
            ...prev[hand],
            [finger]: value
          }
        }))
        console.log(`Successfully moved ${hand} ${finger} to ${value}`)
      } else {
        console.error('Failed to move hand:', moveResult.error)
      }
    } catch (error) {
      console.error('Error moving hand:', error)
    }
  }, [isConnected, currentPosition])

  const toggleRobotStatus = useCallback(() => {
    'background only'
    setRobotStatus(prev => prev === 'idle' ? 'active' : 'idle')
  }, [])

  const executePreset = useCallback(async (preset) => {
    'background only'
    if (!isConnected) {
      console.log('Robot not connected')
      return
    }
    
    try {
      console.log(`Executing preset: ${preset}`)
      const result = await robotAPI.executePreset(preset)
      
      if (result.success) {
        console.log(`Preset "${preset}" executed successfully`)
      } else {
        console.error('Failed to execute preset:', result.error)
      }
    } catch (error) {
      console.error('Error executing preset:', error)
    }
  }, [isConnected])

  const ArrowControl = ({ label, value, min, max, onChange, unit = "°" }) => {
    const increment = () => {
      if (value < max) onChange(value + 1)
    }
    
    const decrement = () => {
      if (value > min) onChange(value - 1)
    }

    return (
      <view className="arrow-control">
        <view className="control-header">
          <text className="control-label">{label}</text>
          <text className="control-value">{value}{unit}</text>
        </view>
        <view className="arrow-buttons">
          <view className="arrow-button" bindtap={decrement}>
            <text className="arrow-text">▼</text>
          </view>
          <view className="arrow-button" bindtap={increment}>
            <text className="arrow-text">▲</text>
          </view>
        </view>
      </view>
    )
  }

  const StatusIndicator = ({ label, value, status, icon }) => (
    <view className={`status-indicator status-${status}`}>
      <view className="status-icon">{icon}</view>
      <view className="status-content">
        <text className="status-label">{label}</text>
        <text className="status-value">{value}</text>
      </view>
    </view>
  )

  const PresetButton = ({ name, icon, action }) => (
    <view className="preset-button" bindtap={() => executePreset(name)}>
      <view className="preset-icon">{icon}</view>
      <text className="preset-name">{name}</text>
    </view>
  )

  const TabButton = ({ id, label, icon, isActive }) => (
    <view 
      className={`tab-button ${isActive ? 'active' : ''}`}
      bindtap={() => setActiveTab(id)}
    >
      <view className="tab-icon">{icon}</view>
      <text className="tab-label">{label}</text>
    </view>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'status':
        return (
          <view className="tab-content">
            <view className="status-bar">
              <StatusIndicator 
                label="Estado"
                value={robotStatus === 'idle' ? 'Inactivo' : robotStatus === 'active' ? 'Activo' : 'Error'}
                status={robotStatus}
                icon={robotStatus === 'idle' ? '🤖' : robotStatus === 'active' ? '⚡' : '⚠️'}
              />
              <StatusIndicator 
                label="Batería"
                value={`${batteryLevel}%`}
                status={batteryLevel > 20 ? 'good' : 'warning'}
                icon="🔋"
              />
              <StatusIndicator 
                label="Temperatura"
                value={`${temperature}°C`}
                status={temperature < 50 ? 'good' : 'warning'}
                icon="🌡️"
              />
              <StatusIndicator 
                label="Conexión"
                value={isConnected ? 'Conectado' : 'Desconectado'}
                status={isConnected ? 'good' : 'error'}
                icon="📡"
              />
              <StatusIndicator 
                label="API Robot"
                value={isConnected ? 'Online' : 'Offline'}
                status={isConnected ? 'good' : 'error'}
                icon="🤖"
              />
            </view>

            <view className="control-section">
              <text className="section-title">Control Principal</text>
              <view className="control-buttons">
                <view className={`control-button ${robotStatus === 'active' ? 'active' : ''}`} bindtap={toggleRobotStatus}>
                  <view className="button-icon">{robotStatus === 'active' ? '⏸️' : '▶️'}</view>
                  <text className="button-text">{robotStatus === 'active' ? 'Pausar' : 'Activar'}</text>
                </view>
                <view className="control-button emergency" bindtap={async () => {
                  if (isConnected) {
                    try {
                      const result = await robotAPI.emergencyStop()
                      if (result.success) {
                        console.log('Emergency stop activated!')
                      } else {
                        console.error('Emergency stop failed:', result.error)
                      }
                    } catch (error) {
                      console.error('Emergency stop error:', error)
                    }
                  } else {
                    console.log('Robot not connected - cannot execute emergency stop')
                  }
                }}>
                  <view className="button-icon">🛑</view>
                  <text className="button-text">EMERGENCIA</text>
                </view>
              </view>
            </view>

            <view className="control-section">
              <text className="section-title">Posición Actual</text>
              <view className="position-display">
                <text className="position-text">
                  Cabeza: X:{currentPosition.head.x}° Y:{currentPosition.head.y}° Z:{currentPosition.head.z}°
                </text>
                <text className="position-text">
                  Brazo Izq: H:{currentPosition.leftArm.shoulder}° C:{currentPosition.leftArm.elbow}° M:{currentPosition.leftArm.wrist}°
                </text>
                <text className="position-text">
                  Brazo Der: H:{currentPosition.rightArm.shoulder}° C:{currentPosition.rightArm.elbow}° M:{currentPosition.rightArm.wrist}°
                </text>
              </view>
            </view>
          </view>
        )

      case 'head':
        return (
          <view className="tab-content">
            <text className="section-title">Control de Cabeza</text>
            <view className="control-grid">
              <ArrowControl 
                label="Rotación X"
                value={currentPosition.head.x}
                min={-45}
                max={45}
                onChange={(value) => handleMovement('head', 'x', value)}
              />
              <ArrowControl 
                label="Rotación Y"
                value={currentPosition.head.y}
                min={-30}
                max={30}
                onChange={(value) => handleMovement('head', 'y', value)}
              />
              <ArrowControl 
                label="Rotación Z"
                value={currentPosition.head.z}
                min={-90}
                max={90}
                onChange={(value) => handleMovement('head', 'z', value)}
              />
            </view>
          </view>
        )

      case 'arms':
        return (
          <view className="tab-content">
            <text className="section-title">Control de Brazos</text>
            <view className="arms-container">
              <view className="arm-control">
                <text className="arm-title">Brazo Izquierdo</text>
                <ArrowControl 
                  label="Hombro"
                  value={currentPosition.leftArm.shoulder}
                  min={-90}
                  max={90}
                  onChange={(value) => handleMovement('leftArm', 'shoulder', value)}
                />
                <ArrowControl 
                  label="Codo"
                  value={currentPosition.leftArm.elbow}
                  min={0}
                  max={120}
                  onChange={(value) => handleMovement('leftArm', 'elbow', value)}
                />
                <ArrowControl 
                  label="Muñeca"
                  value={currentPosition.leftArm.wrist}
                  min={-45}
                  max={45}
                  onChange={(value) => handleMovement('leftArm', 'wrist', value)}
                />
              </view>
              
              <view className="arm-control">
                <text className="arm-title">Brazo Derecho</text>
                <ArrowControl 
                  label="Hombro"
                  value={currentPosition.rightArm.shoulder}
                  min={-90}
                  max={90}
                  onChange={(value) => handleMovement('rightArm', 'shoulder', value)}
                />
                <ArrowControl 
                  label="Codo"
                  value={currentPosition.rightArm.elbow}
                  min={0}
                  max={120}
                  onChange={(value) => handleMovement('rightArm', 'elbow', value)}
                />
                <ArrowControl 
                  label="Muñeca"
                  value={currentPosition.rightArm.wrist}
                  min={-45}
                  max={45}
                  onChange={(value) => handleMovement('rightArm', 'wrist', value)}
                />
              </view>
            </view>
          </view>
        )

      case 'hands':
        return (
          <view className="tab-content">
            <text className="section-title">Control de Manos</text>
            <view className="hands-container">
              <view className="hand-control">
                <text className="hand-title">Mano Izquierda</text>
                <view className="fingers-grid">
                  {Object.entries(currentPosition.leftHand).map(([finger, value]) => (
                    <ArrowControl 
                      key={finger}
                      label={finger.charAt(0).toUpperCase() + finger.slice(1)}
                      value={value}
                      min={0}
                      max={90}
                      onChange={(newValue) => handleHandGesture('leftHand', finger, newValue)}
                    />
                  ))}
                </view>
              </view>
              
              <view className="hand-control">
                <text className="hand-title">Mano Derecha</text>
                <view className="fingers-grid">
                  {Object.entries(currentPosition.rightHand).map(([finger, value]) => (
                    <ArrowControl 
                      key={finger}
                      label={finger.charAt(0).toUpperCase() + finger.slice(1)}
                      value={value}
                      min={0}
                      max={90}
                      onChange={(newValue) => handleHandGesture('rightHand', finger, newValue)}
                    />
                  ))}
                </view>
              </view>
            </view>
          </view>
        )

      case 'presets':
        return (
          <view className="tab-content">
            <text className="section-title">Presets de Movimiento</text>
            <view className="presets-grid">
              <PresetButton name="Saludo" icon="👋" />
              <PresetButton name="Ola" icon="👋" />
              <PresetButton name="Aplauso" icon="👏" />
              <PresetButton name="Punto" icon="👆" />
              <PresetButton name="OK" icon="👍" />
              <PresetButton name="Paz" icon="✌️" />
            </view>
          </view>
        )

      default:
        return null
    }
  }

  return (
    <view className="screen">
      <view className="control-content">
        <text className="control-title">Control Inmoov</text>
        <text className="control-subtitle">Panel de Control del Robot</text>

        {/* Tab Navigation */}
        <view className="tab-navigation">
          <TabButton id="status" label="Estado" icon="📊" isActive={activeTab === 'status'} />
          <TabButton id="head" label="Cabeza" icon="👤" isActive={activeTab === 'head'} />
          <TabButton id="arms" label="Brazos" icon="💪" isActive={activeTab === 'arms'} />
          <TabButton id="hands" label="Manos" icon="✋" isActive={activeTab === 'hands'} />
          <TabButton id="presets" label="Presets" icon="🎯" isActive={activeTab === 'presets'} />
        </view>

        {/* Tab Content */}
        {renderTabContent()}
      </view>
    </view>
  )
} 