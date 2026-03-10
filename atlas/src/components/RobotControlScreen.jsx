import { useState, useEffect } from '@lynx-js/react'
import robotAPI from '../services/RobotAPI'
import { useConfig } from '../services/useConfig'

export function RobotControlScreen() {
  const [message, setMessage] = useState('')
  const [isExecuting, setIsExecuting] = useState(false)
  const [robotStatus, setRobotStatus] = useState({})
  const [lastMovement, setLastMovement] = useState('')
  
  const { isConnected, baseURL } = useConfig()

  useEffect(() => {
    loadRobotStatus()
  }, [])

  const loadRobotStatus = async () => {
    try {
      const result = await robotAPI.getRobotStatus()
      if (result.success) {
        setRobotStatus(result.data)
      }
    } catch (error) {
      console.error('Error loading robot status:', error)
    }
  }

  const executeMovement = async (movementType, movementData) => {
    if (!isConnected) {
      setMessage('❌ No conectado al robot')
      return
    }

    setIsExecuting(true)
    setMessage('🔄 Ejecutando movimiento...')
    
    try {
      let result
      
      if (movementType === 'preset') {
        result = await robotAPI.executePreset(movementData.preset)
      } else if (movementType === 'movement') {
        result = await robotAPI.moveRobot(movementData)
      } else if (movementType === 'speak') {
        result = await robotAPI.speakText(movementData.text)
      }
      
      if (result && result.success) {
        setMessage(`✅ ${movementData.name || 'Movimiento'} ejecutado`)
        setLastMovement(movementData.name || 'Movimiento personalizado')
        await loadRobotStatus()
      } else {
        setMessage(`❌ Error: ${result?.message || 'Falló el movimiento'}`)
      }
    } catch (error) {
      setMessage(`❌ Error: ${error.message}`)
    } finally {
      setIsExecuting(false)
    }
  }

  const executeEmergencyStop = async () => {
    try {
      const result = await robotAPI.emergencyStop()
      if (result.success) {
        setMessage('🛑 Parada de emergencia activada')
      }
    } catch (error) {
      setMessage(`❌ Error en parada de emergencia: ${error.message}`)
    }
  }

  // Predefined movements similar to ESP32 controls
  const systemMovements = [
    {
      id: 'rest_position',
      name: 'Posición de Descanso',
      icon: '😴',
      type: 'movement',
      data: {
        action: 'rest_position',
        name: 'Posición de Descanso'
      },
      color: '#2196F3'
    },
    {
      id: 'safe_position',
      name: 'Posición Segura',
      icon: '🛡️',
      type: 'movement',
      data: {
        action: 'safe_position',
        name: 'Posición Segura'
      },
      color: '#4CAF50'
    }
  ]

  const armMovements = [
    {
      id: 'arms_rest',
      name: 'Brazos Descanso',
      icon: '🤲',
      type: 'movement',
      data: {
        action: 'arms_rest',
        part: 'arms',
        name: 'Brazos Descanso'
      },
      color: '#2196F3'
    },
    {
      id: 'arms_salute',
      name: 'Brazos Saludo',
      icon: '👋',
      type: 'preset',
      data: {
        preset: 'saludo',
        name: 'Saludo'
      },
      color: '#4CAF50'
    },
    {
      id: 'arms_hug',
      name: 'Abrazo',
      icon: '🤗',
      type: 'movement',
      data: {
        action: 'arms_hug',
        part: 'arms',
        name: 'Abrazo'
      },
      color: '#9C27B0'
    },
    {
      id: 'applause',
      name: 'Aplauso',
      icon: '👏',
      type: 'preset',
      data: {
        preset: 'aplauso',
        name: 'Aplauso'
      },
      color: '#FF9800'
    }
  ]

  const neckMovements = [
    {
      id: 'neck_center',
      name: 'Cuello Centro',
      icon: '⬆️',
      type: 'movement',
      data: {
        action: 'neck_center',
        part: 'neck',
        name: 'Cuello Centro'
      },
      color: '#2196F3'
    },
    {
      id: 'neck_yes',
      name: 'Asentir (Sí)',
      icon: '✅',
      type: 'movement',
      data: {
        action: 'neck_yes',
        part: 'neck',
        name: 'Asentir'
      },
      color: '#4CAF50'
    },
    {
      id: 'neck_no',
      name: 'Negar (No)',
      icon: '❌',
      type: 'movement',
      data: {
        action: 'neck_no',
        part: 'neck',
        name: 'Negar'
      },
      color: '#f44336'
    },
    {
      id: 'neck_random',
      name: 'Movimiento Aleatorio',
      icon: '🎲',
      type: 'movement',
      data: {
        action: 'neck_random',
        part: 'neck',
        name: 'Cuello Aleatorio'
      },
      color: '#FF9800'
    }
  ]

  const gesturePresets = [
    {
      id: 'pointing',
      name: 'Señalar',
      icon: '👉',
      type: 'preset',
      data: {
        preset: 'punto',
        name: 'Señalar'
      },
      color: '#607D8B'
    },
    {
      id: 'ok_gesture',
      name: 'Gesto OK',
      icon: '👌',
      type: 'preset',
      data: {
        preset: 'ok',
        name: 'OK'
      },
      color: '#4CAF50'
    },
    {
      id: 'peace',
      name: 'Paz',
      icon: '✌️',
      type: 'preset',
      data: {
        preset: 'paz',
        name: 'Paz'
      },
      color: '#9C27B0'
    },
    {
      id: 'thinking',
      name: 'Pensativo',
      icon: '🤔',
      type: 'preset',
      data: {
        preset: 'pensativo',
        name: 'Pensativo'
      },
      color: '#795548'
    }
  ]

  const renderMovementSection = (title, movements, columns = 2) => (
    <view style={{ marginBottom: '20px' }}>
      <text style={{ 
        fontSize: '18px', 
        color: '#ffffff', 
        fontWeight: 'bold',
        marginBottom: '10px'
      }}>
        {title}
      </text>
      
      <view style={{
        display: 'grid',
        gridTemplateColumns: columns === 3 ? 'repeat(3, 1fr)' : 'repeat(2, 1fr)',
        gap: '10px'
      }}>
        {movements.map(movement => (
          <view 
            key={movement.id}
            style={{ 
              padding: '15px',
              backgroundColor: isExecuting ? '#666666' : movement.color,
              borderRadius: '12px',
              cursor: isExecuting ? 'not-allowed' : 'pointer',
              textAlign: 'center',
              transition: 'all 0.3s ease',
              opacity: isExecuting ? 0.6 : 1
            }}
            bindtap={() => !isExecuting && executeMovement(movement.type, movement.data)}
          >
            <text style={{ 
              fontSize: '24px', 
              marginBottom: '8px'
            }}>
              {movement.icon}
            </text>
            <text style={{ 
              color: 'white', 
              fontSize: '14px', 
              fontWeight: 'bold',
              lineHeight: '1.2'
            }}>
              {movement.name}
            </text>
          </view>
        ))}
      </view>
    </view>
  )

  return (
    <view className="screen">
      <view style={{ padding: '20px', textAlign: 'center' }}>
        <text style={{ fontSize: '24px', color: 'white', fontWeight: 'bold' }}>
          🤖 Control del Robot
        </text>
        
        {/* Connection Status */}
        <view style={{ 
          marginTop: '15px',
          marginBottom: '20px',
          padding: '10px',
          backgroundColor: isConnected ? 'rgba(76, 175, 80, 0.2)' : 'rgba(244, 67, 54, 0.2)',
          borderRadius: '8px'
        }}>
          <text style={{ 
            color: isConnected ? '#4CAF50' : '#f44336',
            fontSize: '14px',
            fontWeight: 'bold'
          }}>
            {isConnected ? '🟢 Conectado' : '🔴 Desconectado'}
          </text>
          {baseURL && (
            <text style={{ 
              color: '#888888',
              fontSize: '12px',
              display: 'block',
              marginTop: '5px'
            }}>
              {baseURL}
            </text>
          )}
        </view>

        {/* Robot Status */}
        {lastMovement && (
          <view style={{ 
            marginBottom: '20px',
            padding: '10px',
            backgroundColor: 'rgba(33, 150, 243, 0.2)',
            borderRadius: '8px'
          }}>
            <text style={{ 
              color: '#2196F3',
              fontSize: '14px',
              fontWeight: 'bold'
            }}>
              Último movimiento: {lastMovement}
            </text>
          </view>
        )}

        {/* Emergency Stop */}
        <view style={{ marginBottom: '25px' }}>
          <view 
            style={{ 
              padding: '15px',
              backgroundColor: '#f44336',
              borderRadius: '12px',
              cursor: 'pointer'
            }}
            bindtap={executeEmergencyStop}
          >
            <text style={{ 
              color: 'white', 
              fontSize: '18px', 
              fontWeight: 'bold'
            }}>
              🛑 PARADA DE EMERGENCIA
            </text>
          </view>
        </view>

        {/* System Controls */}
        {renderMovementSection('🔧 Controles del Sistema', systemMovements)}

        {/* Arm Controls */}
        {renderMovementSection('💪 Control de Brazos', armMovements)}

        {/* Neck Controls */}
        {renderMovementSection('🗣️ Control del Cuello', neckMovements)}

        {/* Gesture Presets */}
        {renderMovementSection('✋ Gestos Predefinidos', gesturePresets)}

        {/* Status Message */}
        {message && (
          <view style={{ 
            marginTop: '20px',
            padding: '15px',
            backgroundColor: message.includes('❌') ? 'rgba(244, 67, 54, 0.2)' : 
                            message.includes('✅') ? 'rgba(76, 175, 80, 0.2)' :
                            'rgba(255, 152, 0, 0.2)',
            borderRadius: '8px'
          }}>
            <text style={{ 
              color: message.includes('❌') ? '#f44336' : 
                     message.includes('✅') ? '#4CAF50' : '#FF9800',
              fontSize: '14px',
              fontWeight: 'bold'
            }}>
              {message}
            </text>
          </view>
        )}

        {/* Execution Status */}
        {isExecuting && (
          <view style={{ 
            marginTop: '10px',
            padding: '10px',
            backgroundColor: 'rgba(255, 152, 0, 0.2)',
            borderRadius: '8px'
          }}>
            <text style={{ 
              color: '#FF9800',
              fontSize: '14px',
              fontWeight: 'bold'
            }}>
              ⏳ Ejecutando movimiento...
            </text>
          </view>
        )}
      </view>
    </view>
  )
}
