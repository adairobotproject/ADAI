import { useState, useEffect } from '@lynx-js/react'
import robotAPI from '../services/RobotAPI'

export function TeacherControlScreen() {
  const [isConnected, setIsConnected] = useState(false)
  const [isClassActive, setIsClassActive] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [isPaused, setIsPaused] = useState(false)

  // Check connection status periodically
  useEffect(() => {
    const checkConnection = async () => {
      const result = await robotAPI.getConnectionStatus()
      if (result && result.success !== undefined) {
        setIsConnected(result.success)
      } else {
        // Fallback: check connection status
        const status = robotAPI.getConnectionStatus()
        setIsConnected(status?.isConnected || false)
      }
    }

    checkConnection()
    const interval = setInterval(checkConnection, 5000) // Check every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const showMessage = (text, duration = 3000) => {
    setMessage(text)
    setTimeout(() => setMessage(''), duration)
  }

  const handleTeacherRequest = async () => {
    if (!isConnected) {
      showMessage('❌ No hay conexión con el robot')
      return
    }

    setLoading(true)
    try {
      // Send request to robot to pause class and listen for teacher request
      const result = await robotAPI.handleTeacherRequest()
      
      if (result.success) {
        showMessage('✅ Solicitud enviada al robot')
      } else {
        showMessage(`❌ Error: ${result.error || 'No se pudo enviar la solicitud'}`)
      }
    } catch (error) {
      console.error('Error handling teacher request:', error)
      showMessage('❌ Error de comunicación con el robot')
    } finally {
      setLoading(false)
    }
  }

  const handleRequestExamples = async () => {
    if (!isConnected) {
      showMessage('❌ No hay conexión con el robot')
      return
    }

    setLoading(true)
    try {
      const result = await robotAPI.handleTeacherRequest('examples')
      
      if (result.success) {
        showMessage('✅ Solicitud de ejemplos enviada')
      } else {
        showMessage(`❌ Error: ${result.error || 'No se pudo enviar la solicitud'}`)
      }
    } catch (error) {
      console.error('Error requesting examples:', error)
      showMessage('❌ Error de comunicación con el robot')
    } finally {
      setLoading(false)
    }
  }

  const handleRepeatQuestion = async () => {
    if (!isConnected) {
      showMessage('❌ No hay conexión con el robot')
      return
    }

    setLoading(true)
    try {
      const result = await robotAPI.handleTeacherRequest('repeat_question')
      
      if (result.success) {
        showMessage('✅ Solicitud de repetir pregunta enviada')
      } else {
        showMessage(`❌ Error: ${result.error || 'No se pudo enviar la solicitud'}`)
      }
    } catch (error) {
      console.error('Error repeating question:', error)
      showMessage('❌ Error de comunicación con el robot')
    } finally {
      setLoading(false)
    }
  }

  const handlePauseResume = async () => {
    if (!isConnected) {
      showMessage('❌ No hay conexión con el robot')
      return
    }

    setLoading(true)
    try {
      const newPauseState = !isPaused
      const result = await robotAPI.pauseClass(newPauseState)
      
      if (result.success) {
        setIsPaused(newPauseState)
        showMessage(newPauseState ? '⏸️ Clase pausada' : '▶️ Clase reanudada')
      } else {
        showMessage(`❌ Error: ${result.error || 'No se pudo cambiar el estado de la clase'}`)
      }
    } catch (error) {
      console.error('Error pausing/resuming class:', error)
      showMessage('❌ Error de comunicación con el robot')
    } finally {
      setLoading(false)
    }
  }

  return (
    <view className="screen">
      <view className="teacher-control-content">
        <view className="teacher-control-header">
          <text className="teacher-control-title">🎓 Control de Profesora</text>
          <text className="teacher-control-subtitle">Gestiona la clase en tiempo real</text>
        </view>

        {/* Connection Status */}
        <view className="connection-status">
          <view className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            <text className="status-icon">{isConnected ? '🟢' : '🔴'}</text>
            <text className="status-text">
              {isConnected ? 'Conectado' : 'Desconectado'}
            </text>
          </view>
        </view>

        {/* Main Control Buttons */}
        <view className="control-buttons">
          {/* Primary Request Button */}
          <view 
            className={`teacher-button primary ${loading ? 'loading' : ''}`}
            bindtap={handleTeacherRequest}
          >
            <text className="button-icon">🎤</text>
            <text className="button-text">
              {loading ? '⏳ Enviando...' : 'Solicitar al Robot'}
            </text>
            <text className="button-subtitle">
              Pausar clase y escuchar solicitud
            </text>
          </view>

          {/* Secondary Request Buttons */}
          <view className="secondary-buttons">
            <view 
              className={`teacher-button secondary ${loading ? 'loading' : ''}`}
              bindtap={handleRequestExamples}
            >
              <text className="button-icon">💡</text>
              <text className="button-text">Más Ejemplos</text>
            </view>

            <view 
              className={`teacher-button secondary ${loading ? 'loading' : ''}`}
              bindtap={handleRepeatQuestion}
            >
              <text className="button-icon">🔁</text>
              <text className="button-text">Repetir Pregunta</text>
            </view>
          </view>

          {/* Pause/Resume Button */}
          <view 
            className={`teacher-button ${isPaused ? 'resume' : 'pause'} ${loading ? 'loading' : ''}`}
            bindtap={handlePauseResume}
          >
            <text className="button-icon">{isPaused ? '▶️' : '⏸️'}</text>
            <text className="button-text">
              {loading ? '⏳ Enviando...' : isPaused ? 'Reanudar Clase' : 'Pausar Clase'}
            </text>
            <text className="button-subtitle">
              {isPaused ? 'Reanudar la explicación' : 'Pausar y esperar instrucciones'}
            </text>
          </view>
        </view>

        {/* Information Card */}
        <view className="info-card">
          <text className="info-title">ℹ️ Información</text>
          <text className="info-text">
            • Presiona "Pausar Clase" para detener la clase y que el robot espere tus instrucciones
          </text>
          <text className="info-text">
            • Usa "Solicitar al Robot" para pausar la clase y hacer una petición personalizada
          </text>
          <text className="info-text">
            • Usa "Más Ejemplos" para solicitar ejemplos adicionales del tema
          </text>
          <text className="info-text">
            • Usa "Repetir Pregunta" para que el robot vuelva a hacer una pregunta al estudiante
          </text>
        </view>

        {/* Message Display */}
        {message && (
          <view className="message-display">
            <text className="message-text">{message}</text>
          </view>
        )}
      </view>
    </view>
  )
}

