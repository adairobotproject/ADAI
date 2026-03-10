import { useState, useEffect } from '@lynx-js/react'
import { useConfig } from '../services/useConfig'
import robotAPI from '../services/RobotAPI'

export function ConfigDebugScreen() {
  const [debugInfo, setDebugInfo] = useState({})
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  
  const {
    config,
    serverConfig,
    connectionStatus,
    configStats,
    isConnected,
    baseURL
  } = useConfig()

  useEffect(() => {
    // Gather debug information
    const info = {
      timestamp: new Date().toISOString(),
      configManager: {
        fullConfig: config,
        serverConfig: serverConfig,
        connectionStatus: connectionStatus,
        configStats: configStats
      },
      robotAPI: {
        baseURL: robotAPI.getServerURL(),
        serverConfig: robotAPI.getServerConfig(),
        connectionStatus: robotAPI.getConnectionStatus(),
        configStats: robotAPI.getConfigStats()
      },
      localStorage: {},
      computed: {
        isConnected,
        baseURL
      }
    }

    // Get localStorage values
    try {
      if (typeof localStorage !== 'undefined') {
        info.localStorage = {
          robotAPI_host: localStorage.getItem('robotAPI_host'),
          robotAPI_port: localStorage.getItem('robotAPI_port'),
          connection_status: localStorage.getItem('connection_status'),
          last_connected: localStorage.getItem('last_connected'),
          config_version: localStorage.getItem('config_version'),
          user_preferences: localStorage.getItem('user_preferences')
        }
      }
    } catch (error) {
      info.localStorage.error = error.message
    }

    setDebugInfo(info)
    console.log('ConfigDebug: Debug info updated', info)
  }, [config, serverConfig, connectionStatus, configStats, isConnected, baseURL, refreshTrigger])

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  const handleTestAPI = async () => {
    try {
      console.log('ConfigDebug: Testing API with current config')
      const result = await robotAPI.pingServer()
      console.log('ConfigDebug: API test result:', result)
      setRefreshTrigger(prev => prev + 1)
    } catch (error) {
      console.error('ConfigDebug: API test error:', error)
    }
  }

  return (
    <view className="screen">
      <view style={{ padding: '20px', textAlign: 'center' }}>
        <text style={{ fontSize: '24px', color: 'white', fontWeight: 'bold' }}>
          🐛 Config Debug
        </text>
        
        <view style={{ marginTop: '20px' }}>
          <view 
            style={{ 
              padding: '15px',
              backgroundColor: '#3b82f6',
              borderRadius: '8px',
              marginBottom: '10px',
              cursor: 'pointer'
            }}
            bindtap={handleRefresh}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              🔄 Refresh Debug Info
            </text>
          </view>
          
          <view 
            style={{ 
              padding: '15px',
              backgroundColor: '#8b5cf6',
              borderRadius: '8px',
              marginBottom: '20px',
              cursor: 'pointer'
            }}
            bindtap={handleTestAPI}
          >
            <text style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
              🚀 Test API Call
            </text>
          </view>
        </view>

        {/* Current Configuration */}
        <view style={{ 
          marginBottom: '20px',
          padding: '15px',
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          borderRadius: '8px',
          textAlign: 'left'
        }}>
          <text style={{ fontSize: '14px', color: '#60a5fa', fontWeight: 'bold' }}>
            📊 Current Configuration:
          </text>
          <text style={{ fontSize: '12px', color: '#93c5fd', fontFamily: 'monospace' }}>
            Host: {serverConfig.host}{'\n'}
            Port: {serverConfig.port}{'\n'}
            Base URL: {baseURL}{'\n'}
            Status: {connectionStatus.status}{'\n'}
            Connected: {isConnected ? 'Yes' : 'No'}{'\n'}
            Last Connected: {connectionStatus.lastConnected || 'Never'}
          </text>
        </view>

        {/* RobotAPI Configuration */}
        <view style={{ 
          marginBottom: '20px',
          padding: '15px',
          backgroundColor: 'rgba(34, 197, 94, 0.2)',
          borderRadius: '8px',
          textAlign: 'left'
        }}>
          <text style={{ fontSize: '14px', color: '#22c55e', fontWeight: 'bold' }}>
            🤖 RobotAPI Configuration:
          </text>
          <text style={{ fontSize: '12px', color: '#86efac', fontFamily: 'monospace' }}>
            API Base URL: {debugInfo.robotAPI?.baseURL}{'\n'}
            API Host: {debugInfo.robotAPI?.serverConfig?.host}{'\n'}
            API Port: {debugInfo.robotAPI?.serverConfig?.port}{'\n'}
            API Status: {debugInfo.robotAPI?.connectionStatus?.status}
          </text>
        </view>

        {/* localStorage Values */}
        <view style={{ 
          marginBottom: '20px',
          padding: '15px',
          backgroundColor: 'rgba(251, 191, 36, 0.2)',
          borderRadius: '8px',
          textAlign: 'left'
        }}>
          <text style={{ fontSize: '14px', color: '#f59e0b', fontWeight: 'bold' }}>
            💾 localStorage Values:
          </text>
          <text style={{ fontSize: '12px', color: '#fbbf24', fontFamily: 'monospace' }}>
            robotAPI_host: {debugInfo.localStorage?.robotAPI_host || 'null'}{'\n'}
            robotAPI_port: {debugInfo.localStorage?.robotAPI_port || 'null'}{'\n'}
            connection_status: {debugInfo.localStorage?.connection_status || 'null'}{'\n'}
            last_connected: {debugInfo.localStorage?.last_connected || 'null'}{'\n'}
            config_version: {debugInfo.localStorage?.config_version || 'null'}
          </text>
        </view>

        {/* Configuration Stats */}
        <view style={{ 
          marginBottom: '20px',
          padding: '15px',
          backgroundColor: 'rgba(168, 85, 247, 0.2)',
          borderRadius: '8px',
          textAlign: 'left'
        }}>
          <text style={{ fontSize: '14px', color: '#a855f7', fontWeight: 'bold' }}>
            📈 Configuration Stats:
          </text>
          <text style={{ fontSize: '12px', color: '#c084fc', fontFamily: 'monospace' }}>
            Total Keys: {configStats.totalKeys}{'\n'}
            Saved Keys: {configStats.savedKeys}{'\n'}
            Config Version: {configStats.configVersion}{'\n'}
            Missing Keys: {configStats.missingKeys?.join(', ') || 'None'}
          </text>
        </view>

        {/* Debug Timestamp */}
        <view style={{ 
          padding: '10px',
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <text style={{ fontSize: '12px', color: '#888888' }}>
            Debug updated: {debugInfo.timestamp}
          </text>
        </view>
      </view>
    </view>
  )
}

