import { useState, useEffect } from '@lynx-js/react'
import robotAPI from '../services/RobotAPI'

export function ClassProgressBar({ className, isActive, onProgressUpdate }) {
  const [progress, setProgress] = useState(null)
  const [loading, setLoading] = useState(false)

  // Update progress when class changes or becomes active
  useEffect(() => {
    if (!isActive || !className) {
      setProgress(null)
      return
    }

    const fetchProgress = async () => {
      // Prevent multiple simultaneous requests
      if (loading) {
        console.log('Progress already loading, skipping...')
        return
      }
      
      try {
        setLoading(true)
        const result = await robotAPI.getClassProgress()
        
        if (result.success && result.data) {
          setProgress(result.data)
          if (onProgressUpdate) {
            onProgressUpdate(result.data)
          }
        } else {
          setProgress(null)
        }
      } catch (error) {
        console.error('Error fetching class progress:', error)
        setProgress(null)
      } finally {
        setLoading(false)
      }
    }

    // Fetch initial progress
    fetchProgress()

    // Set up interval to update progress every 10 seconds (reduced frequency)
    const interval = setInterval(fetchProgress, 10000)

    return () => clearInterval(interval)
  }, [className, isActive, onProgressUpdate])

  // Don't render if not active
  if (!isActive || !progress) {
    return null
  }

  const getPhaseEmoji = (phase) => {
    const emojiMap = {
      'not_started': '⏳',
      'initialization': '🚀',
      'presentation': '📖',
      'explanation': '💡',
      'demonstration': '🎯',
      'interaction': '🤝',
      'practice': '✍️',
      'evaluation': '📝',
      'summary': '📋',
      'completion': '✅',
      'error': '❌',
      'paused': '⏸️'
    }
    return emojiMap[phase] || '📊'
  }

  const getProgressColor = (percentage) => {
    if (percentage < 30) return '#ff6b6b' // Red
    if (percentage < 70) return '#feca57' // Orange
    return '#48dbfb' // Blue
  }

  const formatTime = (timeString) => {
    if (!timeString || timeString === '0s') return '0:00'
    
    // Convert "1m 30s" to "1:30" format
    const minutes = timeString.match(/(\d+)m/)
    const seconds = timeString.match(/(\d+)s/)
    
    const mins = minutes ? parseInt(minutes[1]) : 0
    const secs = seconds ? parseInt(seconds[1]) : 0
    
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <view className="class-progress-container">
      <view className="progress-header">
        <view className="progress-title">
          <text className="progress-icon">{getPhaseEmoji(progress.phase)}</text>
          <text className="progress-text">Progreso de la Clase</text>
        </view>
        <view className="progress-status">
          <text className="status-text">{progress.current_phase || 'Iniciando...'}</text>
        </view>
      </view>

      <view className="progress-bar-container">
        <view className="progress-bar-background">
          <view 
            className="progress-bar-fill"
            style={{
              width: `${progress.progress_percentage || 0}%`,
              backgroundColor: getProgressColor(progress.progress_percentage || 0)
            }}
          />
        </view>
        <text className="progress-percentage">{progress.progress_percentage || 0}%</text>
      </view>

      <view className="progress-details">
        <view className="detail-item">
          <text className="detail-label">⏱️ Tiempo Transcurrido:</text>
          <text className="detail-value">{formatTime(progress.elapsed_time)}</text>
        </view>
        
        {progress.remaining_time && progress.remaining_time !== '0s' && (
          <view className="detail-item">
            <text className="detail-label">⏳ Tiempo Restante:</text>
            <text className="detail-value">{formatTime(progress.remaining_time)}</text>
          </view>
        )}
        
        <view className="detail-item">
          <text className="detail-label">📊 Estado:</text>
          <text className="detail-value">{progress.status || 'Ejecutando'}</text>
        </view>
      </view>

      {loading && (
        <view className="progress-loading">
          <text className="loading-text">Actualizando progreso...</text>
        </view>
      )}
    </view>
  )
}
