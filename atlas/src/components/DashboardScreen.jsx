import { useState, useEffect } from '@lynx-js/react'

export function DashboardScreen() {
  const [stats, setStats] = useState({
    totalSessions: 0,
    averageSessionTime: 0,
    successRate: 0,
    activeUsers: 0,
    totalDistance: 0,
    energyConsumption: 0
  })

  useEffect(() => {
    // Simular carga de datos
    const mockData = {
      totalSessions: 1247,
      averageSessionTime: 23.5,
      successRate: 94.2,
      activeUsers: 156,
      totalDistance: 2847.3,
      energyConsumption: 67.8
    }
    
    // Simular animación de carga
    setTimeout(() => {
      setStats(mockData)
    }, 500)
  }, [])

  const StatCard = ({ title, value, unit, icon, color }) => (
    <view className={`stat-card stat-card-${color}`}>
      <view className="stat-header">
        <view className="stat-icon">{icon}</view>
        <text className="stat-title">{title}</text>
      </view>
      <view className="stat-content">
        <text className="stat-value">{value}</text>
        <text className="stat-unit">{unit}</text>
      </view>
    </view>
  )

  const ProgressCard = ({ title, percentage, color }) => (
    <view className={`progress-card progress-card-${color}`}>
      <view className="progress-header">
        <text className="progress-title">{title}</text>
        <text className="progress-percentage">{percentage}%</text>
      </view>
      <view className="progress-bar">
        <view 
          className="progress-fill" 
          style={{ width: `${percentage}%` }}
        />
      </view>
    </view>
  )

  return (
    <view className="screen">
      <view className="dashboard-content">
        <text className="dashboard-title">Dashboard Imoov</text>
        <text className="dashboard-subtitle">Estadísticas del Robot</text>
        
        <view className="stats-grid">
          <StatCard 
            title="Sesiones Totales"
            value={stats.totalSessions}
            unit="sesiones"
            icon="📊"
            color="blue"
          />
          
          <StatCard 
            title="Tiempo Promedio"
            value={stats.averageSessionTime}
            unit="minutos"
            icon="⏱️"
            color="green"
          />
          
          <StatCard 
            title="Tasa de Éxito"
            value={stats.successRate}
            unit="%"
            icon="✅"
            color="purple"
          />
          
          <StatCard 
            title="Usuarios Activos"
            value={stats.activeUsers}
            unit="usuarios"
            icon="👥"
            color="orange"
          />
        </view>

        <view className="metrics-section">
          <text className="section-title">Métricas Detalladas</text>
          
          <view className="metrics-grid">
            <view className="metric-item">
              <text className="metric-label">Distancia Total</text>
              <text className="metric-value">{stats.totalDistance} km</text>
            </view>
            
            <view className="metric-item">
              <text className="metric-label">Consumo Energético</text>
              <text className="metric-value">{stats.energyConsumption} kWh</text>
            </view>
          </view>
        </view>

        <view className="progress-section">
          <text className="section-title">Progreso de Objetivos</text>
          
          <ProgressCard 
            title="Eficiencia Operacional"
            percentage={87}
            color="blue"
          />
          
          <ProgressCard 
            title="Satisfacción del Usuario"
            percentage={92}
            color="green"
          />
          
          <ProgressCard 
            title="Mantenimiento Preventivo"
            percentage={78}
            color="orange"
          />
        </view>

        <view className="recent-activity">
          <text className="section-title">Actividad Reciente</text>
          
          <view className="activity-list">
            <view className="activity-item">
              <view className="activity-icon">🤖</view>
              <view className="activity-content">
                <text className="activity-title">Sesión completada exitosamente</text>
                <text className="activity-time">Hace 5 minutos</text>
              </view>
            </view>
            
            <view className="activity-item">
              <view className="activity-icon">⚡</view>
              <view className="activity-content">
                <text className="activity-title">Actualización de firmware</text>
                <text className="activity-time">Hace 1 hora</text>
              </view>
            </view>
            
            <view className="activity-item">
              <view className="activity-icon">🔧</view>
              <view className="activity-content">
                <text className="activity-title">Mantenimiento programado</text>
                <text className="activity-time">Hace 3 horas</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  )
} 