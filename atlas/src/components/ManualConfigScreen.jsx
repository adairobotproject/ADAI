import { useState, useEffect } from '@lynx-js/react'
import robotAPI from '../services/RobotAPI'
import { useConfig } from '../services/useConfig'
import { useIPInput, useQuickIPUpdate, useIPConfig } from '../services/useIPConfig'

export function ManualConfigScreen() {
  // Estados para debug de botones
  const [examplePressed, setExamplePressed] = useState(false)
  const [refreshPressed, setRefreshPressed] = useState(false)
  const [savePressed, setSavePressed] = useState(false)
  const [testPressed, setTestPressed] = useState(false)
  const [resetPressed, setResetPressed] = useState(false)
  const [staticPressed, setStaticPressed] = useState(false)
  
  // Use the IP input hook for handling IP configuration
  const {
    inputIP,
    inputPort,
    message,
    currentIP,
    currentPort,
    handleIPChange,
    handlePortChange,
    updateConfiguration,
    setExampleValues,
    setStaticValues,
    clearMessage,
    setMessage: setIPMessage
  } = useIPInput()

  // Use IP config hook for direct updates
  const { updateIPConfig } = useIPConfig()

  // Use quick IP update methods
  const { setDevIP, setHomeIP, setLocalhostIP } = useQuickIPUpdate()
  
  // Use the configuration hook for reactive state management
  const {
    serverConfig,
    connectionStatus,
    configStats,
    isConnected,
    setServerConfig: updateServerConfig,
    forceRefresh,
    resetToDefaults
  } = useConfig()

  useEffect(() => {
    // Initialize with current configuration
    console.log('ManualConfig loaded:', { serverConfig, connectionStatus, configStats })
  }, [serverConfig.host, serverConfig.port, connectionStatus.status, configStats])

  const handleSave = () => {
    // Capturar valores directamente del DOM (solución al bug de ReactLynx)
    const hostInput = document.querySelector('input[placeholder="Ejemplo: 10.136.166.163"]')
    const portInput = document.querySelector('input[placeholder="Ejemplo: 8080"]')
    
    const domHost = hostInput ? hostInput.value : inputIP
    const domPort = portInput ? portInput.value : inputPort
    
    console.log('ManualConfig saving:', { domHost, domPort, inputIP, inputPort })
    
    // Usar valores del DOM si están disponibles, sino usar valores del estado
    const finalHost = domHost || inputIP
    const finalPort = domPort || inputPort
    
    if (!finalHost || !finalPort) {
      setIPMessage('❌ Error: IP y puerto son requeridos')
      return
    }

    const trimmedHost = finalHost.trim()
    const trimmedPort = finalPort.trim()
    
    if (!trimmedHost || !trimmedPort) {
      setIPMessage('❌ Error: IP y puerto no pueden estar vacíos')
      return
    }

    // Actualizar usando los valores capturados
    const success = updateIPConfig(trimmedHost, trimmedPort)
    if (success) {
      setIPMessage(`✅ Configuración guardada: ${trimmedHost}:${trimmedPort}`)
      console.log('ManualConfig saved successfully via IP store')
    } else {
      setIPMessage('❌ Error: No se pudo guardar la configuración')
    }
  }

  const handleTest = async () => {
    clearMessage()
    setIPMessage('🔄 Probando conexión...')
    
    try {
      const result = await robotAPI.pingServer()
      setIPMessage(result.success ? '✅ ¡Conectado!' : `❌ Error: ${result.message}`)
    } catch (error) {
      setIPMessage(`❌ Error: ${error.message}`)
    }
  }

  const handleRefresh = () => {
    // Force refresh configuration from storage
    forceRefresh()
    
    // Get the refreshed configuration immediately
    setTimeout(() => {
      setIPMessage(`🔄 Valores actualizados: ${serverConfig.host}:${serverConfig.port} - Estado: ${connectionStatus.status}`)
      console.log('🔍 DEBUG: handleRefresh - Valores actualizados:', { host: serverConfig.host, port: serverConfig.port })
    }, 100)
  }

  const handleReset = () => {
    // Use the configuration hook method for reset
    resetToDefaults()
    
    // Update message after reset
    setTimeout(() => {
      setIPMessage('🔄 Configuración reseteada a valores por defecto')
    }, 100)
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Nunca';
    try {
      return new Date(timestamp).toLocaleString('es-ES');
    } catch (error) {
      return 'Inválido';
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return '#00ff00';
      case 'connecting': return '#ffff00';
      case 'error': return '#ff0000';
      default: return '#888888';
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'connected': return '🟢 CONECTADO';
      case 'connecting': return '🟡 CONECTANDO';
      case 'error': return '🔴 ERROR';
      default: return '⚪ DESCONECTADO';
    }
  }

  const handleQuickUpdate = () => {
    // Capturar valores directamente del DOM (solución al bug de ReactLynx)
    const hostInput = document.querySelector('input[placeholder="Ejemplo: 10.136.166.163"]')
    const portInput = document.querySelector('input[placeholder="Ejemplo: 8080"]')
    
    const domHost = hostInput ? hostInput.value : inputIP
    const domPort = portInput ? portInput.value : inputPort
    
    console.log('🔍 DEBUG: Valores capturados del DOM:', { domHost, domPort })
    console.log('🔍 DEBUG: Valores del estado:', { inputIP, inputPort })
    
    // Usar valores del DOM si están disponibles, sino usar valores del estado
    const finalHost = domHost || inputIP
    const finalPort = domPort || inputPort
    
    if (!finalHost || !finalPort) {
      setIPMessage('❌ Error: IP y puerto son requeridos')
      return
    }

    const trimmedHost = finalHost.trim()
    const trimmedPort = finalPort.trim()
    
    if (!trimmedHost || !trimmedPort) {
      setIPMessage('❌ Error: IP y puerto no pueden estar vacíos')
      return
    }

    // Actualizar usando los valores capturados
    const success = updateIPConfig(trimmedHost, trimmedPort)
    if (success) {
      setIPMessage(`✅ IP actualizada inmediatamente: ${trimmedHost}:${trimmedPort}`)
    } else {
      setIPMessage('❌ Error: No se pudo actualizar la IP')
    }
  }

  return (
    <view className="screen">
      <view style={{ padding: '20px', textAlign: 'center' }}>
        <text style={{ fontSize: '24px', color: 'white', fontWeight: 'bold' }}>
          🛠️ Config Manual
        </text>
        
        {/* Connection Status */}
        <view style={{ 
          marginTop: '15px',
          padding: '10px',
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '8px',
          border: `2px solid ${getStatusColor(connectionStatus.status)}`
        }}>
          <text style={{ 
            fontSize: '18px', 
            color: getStatusColor(connectionStatus.status),
            fontWeight: 'bold'
          }}>
            {getStatusText(connectionStatus.status)}
          </text>
          
          {connectionStatus.lastConnected && (
            <text style={{ 
              fontSize: '12px', 
              color: '#cccccc',
              display: 'block',
              marginTop: '5px'
            }}>
              Última conexión: {formatTimestamp(connectionStatus.lastConnected)}
            </text>
          )}
        </view>

        {/* Configuration Info */}
        <view style={{ 
          marginTop: '15px',
          padding: '15px',
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          borderRadius: '8px',
          textAlign: 'left'
        }}>
          <text style={{ fontSize: '14px', color: '#60a5fa', fontWeight: 'bold' }}>
            📊 Configuración Actual:
          </text>
          <text style={{ fontSize: '12px', color: '#93c5fd', fontFamily: 'monospace' }}>
            Host: {inputIP}{'\n'}
            Port: {inputPort}{'\n'}
            URL: http://{inputIP}:{inputPort}/api{'\n'}
            Versión: {configStats.configVersion || '1.0.0'}
          </text>
        </view>

        {/* Live Preview Label */}
        <view style={{ 
          marginTop: '15px',
          padding: '15px',
          backgroundColor: 'rgba(168, 85, 247, 0.2)',
          borderRadius: '8px',
          textAlign: 'center',
          border: '2px solid #a855f7'
        }}>
          <text style={{ fontSize: '14px', color: '#a855f7', fontWeight: 'bold' }}>
            🔍 Vista Previa en Tiempo Real:
          </text>
          <text style={{ 
            fontSize: '16px', 
            color: inputIP && inputPort ? '#22c55e' : '#f59e0b', 
            fontWeight: 'bold',
            fontFamily: 'monospace',
            display: 'block',
            marginTop: '8px'
          }}>
            {inputIP && inputPort ? `http://${inputIP}:${inputPort}/api` : 'Completa IP y Puerto para ver la URL'}
          </text>
          {inputIP && inputPort && (
            <text style={{ 
              fontSize: '12px', 
              color: '#22c55e',
              display: 'block',
              marginTop: '5px'
            }}>
              ✅ URL válida - Lista para probar conexión
            </text>
          )}
        </view>

        {/* Configuration Inputs */}
        <view style={{ marginTop: '20px', textAlign: 'left' }}>
          <text style={{ fontSize: '16px', color: 'white', marginBottom: '10px', fontWeight: 'bold' }}>
            📍 IP del Servidor:
          </text>
          
          <input
            type="text"
            value={inputIP}
            placeholder="Ejemplo: 10.136.166.163"
            bindinput={(e) => {
              const newIP = e.detail?.value || e.target?.value || '';
              console.log('🔍 IP input changed:', newIP);
              handleIPChange(newIP);
              // Guardar automáticamente en localStorage después de un pequeño delay
              setTimeout(() => {
                if (newIP.trim()) {
                  const portInput = document.querySelector('input[placeholder="Ejemplo: 8080"]');
                  const currentPort = portInput ? (portInput.value || inputPort) : inputPort;
                  if (currentPort && currentPort.trim()) {
                    console.log('💾 Auto-guardando IP:', newIP.trim(), 'Puerto:', currentPort.trim());
                    const success = updateIPConfig(newIP.trim(), currentPort.trim());
                    if (success) {
                      setIPMessage(`✅ IP guardada automáticamente: ${newIP.trim()}:${currentPort.trim()}`);
                      setTimeout(() => setIPMessage(''), 2000);
                    }
                  }
                }
              }, 500);
            }}
            style={{
              width: '100%',
              padding: '15px',
              fontSize: '18px',
              borderRadius: '8px',
              border: '3px solid #3b82f6',
              backgroundColor: '#ffffff',
              color: '#000000',
              fontWeight: 'bold',
              textAlign: 'center',
              marginBottom: '10px'
            }}
          />

          <text style={{ fontSize: '16px', color: 'white', marginBottom: '10px', fontWeight: 'bold' }}>
            🔌 Puerto:
          </text>
          
          <input
            type="text"
            value={inputPort}
            placeholder="Ejemplo: 8080"
            bindinput={(e) => {
              const newPort = e.detail?.value || e.target?.value || '';
              console.log('🔍 Port input changed:', newPort);
              handlePortChange(newPort);
              // Guardar automáticamente en localStorage después de un pequeño delay
              setTimeout(() => {
                if (newPort.trim()) {
                  const hostInput = document.querySelector('input[placeholder="Ejemplo: 10.136.166.163"]');
                  const currentIP = hostInput ? (hostInput.value || inputIP) : inputIP;
                  if (currentIP && currentIP.trim()) {
                    console.log('💾 Auto-guardando Puerto:', newPort.trim(), 'IP:', currentIP.trim());
                    const success = updateIPConfig(currentIP.trim(), newPort.trim());
                    if (success) {
                      setIPMessage(`✅ Puerto guardado automáticamente: ${currentIP.trim()}:${newPort.trim()}`);
                      setTimeout(() => setIPMessage(''), 2000);
                    }
                  }
                }
              }, 500);
            }}
            style={{
              width: '100%',
              padding: '15px',
              fontSize: '18px',
              borderRadius: '8px',
              border: '3px solid #3b82f6',
              backgroundColor: '#ffffff',
              color: '#000000',
              fontWeight: 'bold',
              textAlign: 'center',
              marginBottom: '20px'
            }}
          />
        </view>

        {/* Action Buttons */}
        <view style={{ marginBottom: '15px' }}>

          <view 
            style={{ 
              padding: '15px',
              backgroundColor: examplePressed ? '#dc2626' : '#f59e0b',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              setExamplePressed(true)
              setExampleValues()
              console.log('🔍 DEBUG: Botón Ejemplo presionado')
              // Resetear el color después de 500ms
              setTimeout(() => setExamplePressed(false), 500)
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              📝 Poner Ejemplo (10.136.166.163:8080)
            </text>
          </view>

          <view 
            style={{ 
              padding: '15px',
              backgroundColor: staticPressed ? '#dc2626' : '#059669',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              setStaticPressed(true)
              setStaticValues()
              console.log('🔍 DEBUG: Botón Estático presionado - Host: 192.168.1.100, Port: 2233')
              // Resetear el color después de 500ms
              setTimeout(() => setStaticPressed(false), 500)
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              🔧 Establecer Valores Estáticos (192.168.1.100:2233)
            </text>
          </view>
          
          <view 
            style={{ 
              padding: '15px',
              backgroundColor: refreshPressed ? '#dc2626' : '#10b981',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              setRefreshPressed(true)
              handleRefresh()
              
              console.log('🔍 DEBUG: Botón Actualizar presionado')
              // Resetear el color después de 500ms
              setTimeout(() => setRefreshPressed(false), 500)
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              🔄 Actualizar Valores
            </text>
          </view>
          
          <view 
            style={{ 
              padding: '15px',
              backgroundColor: savePressed ? '#dc2626' : '#3b82f6',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              setSavePressed(true)
              handleSave()
              console.log('🔍 DEBUG: Botón Guardar presionado')
              // Resetear el color después de 500ms
              setTimeout(() => setSavePressed(false), 500)
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              💾 Guardar Configuración
            </text>
          </view>

          <view 
            style={{ 
              padding: '15px',
              backgroundColor: '#10b981',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              handleQuickUpdate()
              console.log('🔍 DEBUG: Actualización rápida de IP')
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              ⚡ Actualizar IP Inmediatamente
            </text>
          </view>

          <view 
            style={{ 
              padding: '15px',
              backgroundColor: '#6366f1',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              // Capturar valores actuales del DOM para mostrar al usuario
              const hostInput = document.querySelector('input[placeholder="Ejemplo: 10.136.166.163"]')
              const portInput = document.querySelector('input[placeholder="Ejemplo: 8080"]')
              
              const domHost = hostInput ? hostInput.value : 'No capturado'
              const domPort = portInput ? portInput.value : 'No capturado'
              
              setIPMessage(`📋 Valores actuales en inputs: IP="${domHost}", Puerto="${domPort}"`)
              console.log('🔍 DEBUG: Valores capturados del DOM:', { domHost, domPort })
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              📋 Ver Valores Actuales en Inputs
            </text>
          </view>

          <view 
            style={{ 
              padding: '15px',
              backgroundColor: '#8b5cf6',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              setDevIP()
              setIPMessage('🚀 IP de desarrollo establecida: 10.136.166.163:8080')
              console.log('🔍 DEBUG: IP de desarrollo establecida')
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              🚀 IP Desarrollo (10.136.166.163:8080)
            </text>
          </view>

          <view 
            style={{ 
              padding: '15px',
              backgroundColor: '#f59e0b',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              setHomeIP()
              setIPMessage('🏠 IP de casa establecida: 192.168.1.100:2233')
              console.log('🔍 DEBUG: IP de casa establecida')
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              🏠 IP Casa (192.168.1.100:2233)
            </text>
          </view>

          <view 
            style={{ 
              padding: '15px',
              backgroundColor: '#06b6d4',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              setLocalhostIP()
              setIPMessage('💻 IP localhost establecida: 127.0.0.1:8080')
              console.log('🔍 DEBUG: IP localhost establecida')
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              💻 IP Localhost (127.0.0.1:8080)
            </text>
          </view>
          
          <view 
            style={{ 
              padding: '15px',
              backgroundColor: testPressed ? '#dc2626' : '#8b5cf6',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              setTestPressed(true)
              handleTest()
              console.log('🔍 DEBUG: Botón Probar presionado')
              // Resetear el color después de 500ms
              setTimeout(() => setTestPressed(false), 500)
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              🚀 Probar Conexión
            </text>
          </view>

          <view 
            style={{ 
              padding: '15px',
              backgroundColor: resetPressed ? '#dc2626' : '#ef4444',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
            bindtap={() => {
              setResetPressed(true)
              handleReset()
              console.log('🔍 DEBUG: Botón Reset presionado')
              // Resetear el color después de 500ms
              setTimeout(() => setResetPressed(false), 500)
            }}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              🔄 Reset a Valores por Defecto
            </text>
          </view>
        </view>

        {/* Status Message */}
        {message && (
          <view style={{ 
            padding: '15px', 
            backgroundColor: 'rgba(0, 0, 0, 0.8)', 
            borderRadius: '8px',
            border: '1px solid #4b5563'
          }}>
            <text style={{ 
              color: message.includes('❌') ? '#ff4444' : message.includes('✅') ? '#00ff00' : '#60a5fa', 
              fontSize: '14px',
              fontWeight: 'bold'
            }}>
              {message}
            </text>
          </view>
        )}

        {/* Configuration Statistics */}
        <view style={{ 
          marginTop: '20px',
          padding: '15px',
          backgroundColor: 'rgba(34, 197, 94, 0.2)',
          borderRadius: '8px',
          textAlign: 'left'
        }}>
          <text style={{ fontSize: '14px', color: '#22c55e', fontWeight: 'bold' }}>
            📈 Estadísticas de Configuración:
          </text>
          <text style={{ fontSize: '12px', color: '#86efac' }}>
            Claves guardadas: {configStats.savedKeys}/{configStats.totalKeys}{'\n'}
            Versión: {configStats.configVersion}{'\n'}
            Estado: {connectionStatus.status}{'\n'}
            Última conexión: {formatTimestamp(connectionStatus.lastConnected)}
          </text>
        </view>

        {/* Instructions */}
        <view style={{ 
          marginTop: '20px',
          padding: '15px',
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          borderRadius: '8px',
          textAlign: 'left'
        }}>
          <text style={{ fontSize: '14px', color: '#60a5fa', fontWeight: 'bold' }}>
            🎯 Instrucciones:
          </text>
          <text style={{ fontSize: '12px', color: '#93c5fd' }}>
            1. Ejecuta robot_gui.py en tu computadora{'\n'}
            2. Encuentra tu IP con "ipconfig" (Windows) o "ifconfig" (Mac/Linux){'\n'}
            3. MÉTODO A - Botones rápidos:{'\n'}
               • Tap "📝 Poner Ejemplo" para autocompletar{'\n'}
               • Tap "🚀 IP Desarrollo" para IP de desarrollo{'\n'}
               • Tap "🏠 IP Casa" para IP de casa{'\n'}
            4. MÉTODO B - Escritura manual:{'\n'}
               • Escribe manualmente en los inputs{'\n'}
               • Tap "📋 Ver Valores Actuales" para verificar{'\n'}
               • Tap "⚡ Actualizar IP Inmediatamente" para aplicar{'\n'}
            5. Tap "🚀 Probar Conexión" para verificar{'\n'}
            6. Opcional: Tap "💾 Guardar Configuración" para persistir
          </text>
        </view>
      </view>
    </view>
  )
}
