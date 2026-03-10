/**
 * React Hook for Configuration Management
 * Provides reactive access to configuration state
 */

import { useState, useEffect } from '@lynx-js/react'
import configManager from './ConfigManager.js'

/**
 * Custom hook for accessing and managing configuration
 * @returns {Object} Configuration state and methods
 */
export function useConfig() {
  const [config, setConfig] = useState(configManager.getConfiguration())
  const [serverConfig, setServerConfig] = useState(configManager.getServerConfig())
  const [connectionStatus, setConnectionStatus] = useState(configManager.getConnectionStatus())
  const [configStats, setConfigStats] = useState(configManager.getConfigStats())

  useEffect(() => {
    console.log('useConfig: Setting up configuration listeners')
    
    // Listen for configuration changes
    const unsubscribeConfigChange = configManager.addEventListener('configurationChanged', (data) => {
      console.log('useConfig: Configuration changed event received', data)
      setConfig(configManager.getConfiguration())
      setServerConfig(configManager.getServerConfig())
      setConnectionStatus(configManager.getConnectionStatus())
      setConfigStats(configManager.getConfigStats())
    })

    // Listen for configuration refresh
    const unsubscribeConfigRefresh = configManager.addEventListener('configurationRefreshed', (data) => {
      console.log('useConfig: Configuration refreshed event received', data)
      setConfig(configManager.getConfiguration())
      setServerConfig(configManager.getServerConfig())
      setConnectionStatus(configManager.getConnectionStatus())
      setConfigStats(configManager.getConfigStats())
    })

    // Cleanup listeners on unmount
    return () => {
      console.log('useConfig: Cleaning up configuration listeners')
      unsubscribeConfigChange()
      unsubscribeConfigRefresh()
    }
  }, [])

  // Configuration methods
  const methods = {
    /**
     * Update server configuration
     * @param {string} host - Server host/IP
     * @param {string} port - Server port
     * @returns {boolean} Success status
     */
    setServerConfig: (host, port) => {
      console.log('useConfig: Setting server config:', { host, port })
      const success = configManager.setServerConfig(host, port)
      if (success) {
        // Force immediate update of local state
        setConfig(configManager.getConfiguration())
        setServerConfig(configManager.getServerConfig())
        setConnectionStatus(configManager.getConnectionStatus())
        setConfigStats(configManager.getConfigStats())
      }
      return success
    },

    /**
     * Update connection status
     * @param {string} status - Connection status
     * @returns {boolean} Success status
     */
    updateConnectionStatus: (status) => {
      console.log('useConfig: Updating connection status:', status)
      const success = configManager.updateConnectionStatus(status)
      if (success) {
        setConnectionStatus(configManager.getConnectionStatus())
        setConfig(configManager.getConfiguration())
      }
      return success
    },

    /**
     * Update user preferences
     * @param {Object} preferences - User preferences
     * @returns {boolean} Success status
     */
    updateUserPreferences: (preferences) => {
      console.log('useConfig: Updating user preferences:', preferences)
      const success = configManager.updateUserPreferences(preferences)
      if (success) {
        setConfig(configManager.getConfiguration())
      }
      return success
    },

    /**
     * Reset configuration to defaults
     * @returns {boolean} Success status
     */
    resetToDefaults: () => {
      console.log('useConfig: Resetting to defaults')
      const success = configManager.resetToDefaults()
      if (success) {
        setConfig(configManager.getConfiguration())
        setServerConfig(configManager.getServerConfig())
        setConnectionStatus(configManager.getConnectionStatus())
        setConfigStats(configManager.getConfigStats())
      }
      return success
    },

    /**
     * Force refresh configuration from storage
     * @returns {boolean} Success status
     */
    forceRefresh: () => {
      console.log('useConfig: Force refreshing configuration')
      return configManager.forceRefresh()
    },

    /**
     * Export current configuration
     * @returns {string} JSON configuration
     */
    exportConfiguration: () => {
      return configManager.exportConfiguration()
    },

    /**
     * Import configuration from JSON
     * @param {string} jsonConfig - JSON configuration
     * @returns {boolean} Success status
     */
    importConfiguration: (jsonConfig) => {
      console.log('useConfig: Importing configuration')
      const success = configManager.importConfiguration(jsonConfig)
      if (success) {
        // Force refresh after import
        configManager.forceRefresh()
      }
      return success
    }
  }

  return {
    // State
    config,
    serverConfig,
    connectionStatus,
    configStats,
    
    // Computed values
    isConnected: connectionStatus.isConnected,
    baseURL: serverConfig.baseURL,
    
    // Methods
    ...methods
  }
}

/**
 * Hook for server configuration only
 * @returns {Object} Server configuration state and methods
 */
export function useServerConfig() {
  const { serverConfig, setServerConfig, isConnected, baseURL } = useConfig()
  
  return {
    host: serverConfig.host,
    port: serverConfig.port,
    baseURL,
    isConnected,
    setServerConfig
  }
}

/**
 * Hook for connection status only
 * @returns {Object} Connection status state and methods
 */
export function useConnectionStatus() {
  const { connectionStatus, updateConnectionStatus } = useConfig()
  
  return {
    status: connectionStatus.status,
    lastConnected: connectionStatus.lastConnected,
    isConnected: connectionStatus.isConnected,
    updateConnectionStatus
  }
}

