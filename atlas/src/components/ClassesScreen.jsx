import { useEffect } from '@lynx-js/react'
import { useClassesState, useClassesLoader, useClassControl } from '../services/useClassesState'
import { ClassProgressBar } from './ClassProgressBar.jsx'

export function ClassesScreen() {
  // Use the new persistent state management
  const { 
    selectedClass, 
    isPlaying, 
    isConnected, 
    classes, 
    classProgress,
    totalClasses,
    runningClasses,
    availableClasses,
    completedClasses,
    hasSelectedClass,
    isClassActive,
    setSelectedClass,
    setClassProgress
  } = useClassesState()
  
  const { loading, error, loadClassesFromAPI } = useClassesLoader()
  const { handleStartClass, handleStopClass } = useClassControl()

  // Load classes from robot API
  useEffect(() => {
    'background only'
    // Load classes on component mount
    loadClassesFromAPI()
  }, []) // Solo ejecutar una vez al montar el componente

  // Set up auto-refresh interval separately
  useEffect(() => {
    let interval = null
    
    // Only refresh automatically if:
    // 1. We're connected to the robot
    // 2. We have classes loaded
    // 3. No class is currently active (to avoid interrupting)
    if (isConnected && totalClasses > 0 && !isClassActive) {
      // Refresh classes every 2 minutes (increased to reduce frequency)
      interval = setInterval(() => {
        // Only refresh if not currently loading and no class is active
        if (!loading && !isClassActive) {
          console.log('Auto-refreshing classes...')
          loadClassesFromAPI()
        }
      }, 120000) // 2 minutes
    }
    
    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [isConnected, totalClasses, loading, isClassActive, loadClassesFromAPI])

  // handleStartClass and handleStopClass are now provided by useClassControl hook

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'green'
      case 'available': return 'blue'
      case 'completed': return 'gray'
      default: return 'gray'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running': return '▶️'
      case 'available': return '📅'
      case 'completed': return '✅'
      default: return '⏸️'
    }
  }

  const ClassCard = ({ classItem }) => (
    <view className={`class-card ${classItem.status || 'available'}`}>
      <view className="class-header">
        <view className="class-status">
          <view className={`status-dot ${getStatusColor(classItem.status || 'available')}`} />
          <text className="class-title">{classItem.title}</text>
        </view>
        <view className="class-meta">
          <text className="class-duration">{classItem.duration || 'N/A'}</text>
          <text className="class-subject">{classItem.subject || 'N/A'}</text>
        </view>
      </view>
      
      <view className="class-content">
        <text className="class-description">{classItem.description || 'Sin descripción disponible'}</text>
        <text className="class-subject">Materia: {classItem.subject || 'N/A'}</text>
        <text className="class-path">Archivo: {classItem.name}</text>
      </view>
      
      <view className="class-actions">
        {classItem.status === 'running' ? (
          <view className="action-button stop" bindtap={handleStopClass}>
            <text className="action-text">⏹️ Detener</text>
          </view>
        ) : (
          <view className="action-button start" bindtap={() => handleStartClass(classItem.name)}>
            <text className="action-text">▶️ Iniciar</text>
          </view>
        )}
        <view className="action-button details" bindtap={() => setSelectedClass(classItem.name)}>
          <text className="action-text">📋 Detalles</text>
        </view>
      </view>
    </view>
  )

  const ClassDetails = ({ classItem }) => (
    <view className="class-details">
      <view className="details-header">
        <text className="details-title">{classItem.title}</text>
        <view className="details-meta">
          <text className="meta-item">⏱️ {classItem.duration || 'N/A'}</text>
          <text className="meta-item">📚 {classItem.subject || 'N/A'}</text>
          <text className="meta-item">📁 {classItem.name}</text>
        </view>
      </view>
      
      <view className="details-content">
        <text className="details-description">{classItem.description || 'Sin descripción disponible'}</text>
        
        <view className="class-info">
          <text className="info-title">Información de la Clase:</text>
          <text className="info-item">• Título: {classItem.title}</text>
          <text className="info-item">• Materia: {classItem.subject || 'N/A'}</text>
          <text className="info-item">• Duración: {classItem.duration || 'N/A'}</text>
          <text className="info-item">• Archivo: {classItem.name}</text>
          <text className="info-item">• Creado: {classItem.created_date || 'N/A'}</text>
        </view>
      </view>
      
      <view className="details-actions">
        <view className="action-button primary" bindtap={() => handleStartClass(classItem.name)}>
          <text className="action-text">🎓 Iniciar Clase</text>
        </view>
        <view className="action-button secondary" bindtap={() => setSelectedClass(null)}>
          <text className="action-text">← Volver</text>
        </view>
      </view>
    </view>
  )

  if (loading) {
    return (
      <view className="screen">
        <view className="loading-container">
          <text className="loading-text">Cargando clases...</text>
        </view>
      </view>
    )
  }

  if (error) {
    return (
      <view className="screen">
        <view className="error-container">
          <text className="error-text">Error: {error}</text>
          <view className="retry-button" bindtap={() => window.location.reload()}>
            <text className="retry-text">🔄 Reintentar</text>
          </view>
        </view>
      </view>
    )
  }

  return (
    <view className="screen">
      <view className="classes-content">
        <view className="classes-header">
          <view className="header-text">
            <text className="classes-title">Clases Disponibles</text>
            <text className="classes-subtitle">Clases Generadas del Robot Inmoov</text>
          </view>
          <view className="header-actions">
            <view className={`refresh-button ${loading ? 'loading' : ''}`} bindtap={loadClassesFromAPI}>
              <text className="refresh-text">{loading ? '⏳ Cargando...' : '🔄 Actualizar'}</text>
            </view>
          </view>
        </view>

        {!isConnected && (
          <view className="connection-warning">
            <view className="warning-icon">⚠️</view>
            <view className="warning-content">
              <text className="warning-title">Sin Conexión</text>
              <text className="warning-subtitle">No se puede conectar con el robot</text>
            </view>
          </view>
        )}

        {isClassActive && (
          <view className="active-class-banner">
            <view className="banner-icon">🎓</view>
            <view className="banner-content">
              <text className="banner-title">Clase en Progreso</text>
              <text className="banner-subtitle">El robot está ejecutando: {selectedClass}</text>
            </view>
            <view className="banner-action" bindtap={handleStopClass}>
              <text className="banner-button">⏹️ Detener</text>
            </view>
          </view>
        )}

        {/* Progress Bar Component */}
        <ClassProgressBar 
          className={selectedClass}
          isActive={isClassActive}
          onProgressUpdate={setClassProgress}
        />

        {hasSelectedClass ? (
          <ClassDetails classItem={classes.find(c => c.name === selectedClass)} />
        ) : (
          <view className="classes-grid">
            {totalClasses === 0 ? (
              <view className="no-classes">
                <text className="no-classes-text">No hay clases disponibles</text>
                <text className="no-classes-subtitle">Las clases aparecerán aquí cuando sean generadas</text>
              </view>
            ) : (
              classes.map(classItem => (
                <ClassCard key={classItem.name} classItem={classItem} />
              ))
            )}
          </view>
        )}

        <view className="classes-stats">
          <view className="stat-item">
            <text className="stat-number">{totalClasses}</text>
            <text className="stat-label">Clases Totales</text>
          </view>
          <view className="stat-item">
            <text className="stat-number">{runningClasses}</text>
            <text className="stat-label">En Progreso</text>
          </view>
          <view className="stat-item">
            <text className="stat-number">{completedClasses}</text>
            <text className="stat-label">Completadas</text>
          </view>
        </view>
      </view>
    </view>
  )
} 