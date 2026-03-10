/**
 * React Hook for IP Configuration Management
 * Provides reactive access to IP configuration state with persistence
 * Solves ReactLynx input bug by using programmatic updates
 */

import { useState, useEffect, useCallback } from '@lynx-js/react'
import ipConfigStore from './IPConfigStore.js'
import configManager from './ConfigManager.js'

/**
 * Custom hook for accessing and managing IP configuration
 * @returns {Object} IP configuration state and methods
 */
export function useIPConfig() {
  const [state, setState] = useState(ipConfigStore.getState())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    console.log('useIPConfig: Setting up IP config listeners')
    
    // Listen for state changes
    const unsubscribeStateChange = ipConfigStore.addEventListener('ipConfigChanged', (data) => {
      console.log('useIPConfig: State changed event received', data)
      setState(ipConfigStore.getState())
    })

    // Listen for state refresh
    const unsubscribeStateRefresh = ipConfigStore.addEventListener('ipConfigRefreshed', (data) => {
      console.log('useIPConfig: State refreshed event received', data)
      setState(ipConfigStore.getState())
    })

    // Cleanup listeners on unmount
    return () => {
      console.log('useIPConfig: Cleaning up IP config listeners')
      unsubscribeStateChange()
      unsubscribeStateRefresh()
    }
  }, [])

  // IP configuration methods
  const methods = {
    /**
     * Set current IP
     * @param {string} ip - IP address
     * @returns {boolean} Success status
     */
    setCurrentIP: (ip) => {
      console.log('useIPConfig: Setting current IP:', ip)
      const success = ipConfigStore.setCurrentIP(ip)
      if (success) {
        setState(ipConfigStore.getState())
      }
      return success
    },

    /**
     * Set current port
     * @param {string} port - Port number
     * @returns {boolean} Success status
     */
    setCurrentPort: (port) => {
      console.log('useIPConfig: Setting current port:', port)
      const success = ipConfigStore.setCurrentPort(port)
      if (success) {
        setState(ipConfigStore.getState())
      }
      return success
    },

    /**
     * Set both IP and port
     * @param {string} ip - IP address
     * @param {string} port - Port number
     * @returns {boolean} Success status
     */
    setIPAndPort: (ip, port) => {
      console.log('useIPConfig: Setting IP and port:', { ip, port })
      const success = ipConfigStore.setIPAndPort(ip, port)
      if (success) {
        setState(ipConfigStore.getState())
      }
      return success
    },

    /**
     * Update IP configuration and sync with main config
     * @param {string} ip - IP address
     * @param {string} port - Port number
     * @returns {boolean} Success status
     */
    updateIPConfig: (ip, port) => {
      console.log('useIPConfig: Updating IP config:', { ip, port })
      
      // Update IP store
      const ipSuccess = ipConfigStore.setIPAndPort(ip, port)
      
      // Update main config manager
      const configSuccess = configManager.setServerConfig(ip, port)
      
      if (ipSuccess && configSuccess) {
        setState(ipConfigStore.getState())
        return true
      }
      
      return false
    },

    /**
     * Get recent update history
     * @param {number} limit - Number of recent entries to return
     * @returns {Array} Recent update history
     */
    getRecentHistory: (limit = 5) => {
      return ipConfigStore.getRecentHistory(limit)
    },

    /**
     * Clear update history
     * @returns {boolean} Success status
     */
    clearHistory: () => {
      console.log('useIPConfig: Clearing history')
      const success = ipConfigStore.clearHistory()
      if (success) {
        setState(ipConfigStore.getState())
      }
      return success
    },

    /**
     * Reset to defaults
     * @returns {boolean} Success status
     */
    resetToDefaults: () => {
      console.log('useIPConfig: Resetting to defaults')
      const success = ipConfigStore.resetToDefaults()
      if (success) {
        setState(ipConfigStore.getState())
      }
      return success
    },

    /**
     * Force refresh state from storage
     * @returns {boolean} Success status
     */
    forceRefresh: () => {
      console.log('useIPConfig: Force refreshing state')
      return ipConfigStore.forceRefresh()
    },

    /**
     * Export current state
     * @returns {string} JSON state
     */
    exportState: () => {
      return ipConfigStore.exportState()
    },

    /**
     * Import state from JSON
     * @param {string} jsonState - JSON state
     * @returns {boolean} Success status
     */
    importState: (jsonState) => {
      console.log('useIPConfig: Importing state')
      const success = ipConfigStore.importState(jsonState)
      if (success) {
        setState(ipConfigStore.getState())
      }
      return success
    }
  }

  return {
    // State
    currentIP: state.currentIP,
    currentPort: state.currentPort,
    lastUpdated: state.lastUpdated,
    updateHistory: state.updateHistory,
    version: state.version,
    loading,
    error,
    
    // Computed values
    isConfigured: ipConfigStore.isConfigured(),
    formattedAddress: ipConfigStore.getFormattedAddress(),
    currentURL: ipConfigStore.getCurrentURL(),
    stateStats: ipConfigStore.getStateStats(),
    
    // Methods
    ...methods
  }
}

/**
 * Hook for IP input handling with ReactLynx bug workaround
 * @returns {Object} IP input state and methods
 */
export function useIPInput() {
  const { 
    currentIP, 
    currentPort, 
    setCurrentIP, 
    setCurrentPort, 
    setIPAndPort,
    updateIPConfig 
  } = useIPConfig()
  
  const [inputIP, setInputIP] = useState(currentIP)
  const [inputPort, setInputPort] = useState(currentPort)
  const [message, setMessage] = useState('')

  // Sync input values with store values
  useEffect(() => {
    setInputIP(currentIP)
    setInputPort(currentPort)
  }, [currentIP, currentPort])

  /**
   * Handle IP input change (programmatic only due to ReactLynx bug)
   * @param {string} value - New IP value
   */
  const handleIPChange = useCallback((value) => {
    console.log('useIPInput: IP changed to:', value)
    setInputIP(value)
    setMessage('🔄 IP actualizada - Presiona "Actualizar" para aplicar cambios')
  }, [])

  /**
   * Handle port input change (programmatic only due to ReactLynx bug)
   * @param {string} value - New port value
   */
  const handlePortChange = useCallback((value) => {
    console.log('useIPInput: Port changed to:', value)
    setInputPort(value)
    setMessage('🔄 Puerto actualizado - Presiona "Actualizar" para aplicar cambios')
  }, [])

  /**
   * Update IP configuration with current input values
   * @returns {boolean} Success status
   */
  const updateConfiguration = useCallback(() => {
    if (!inputIP || !inputPort) {
      setMessage('❌ Error: IP y puerto son requeridos')
      return false
    }

    const trimmedIP = inputIP.trim()
    const trimmedPort = inputPort.trim()
    
    if (!trimmedIP || !trimmedPort) {
      setMessage('❌ Error: IP y puerto no pueden estar vacíos')
      return false
    }

    const success = updateIPConfig(trimmedIP, trimmedPort)
    if (success) {
      setMessage(`✅ IP actualizada: ${trimmedIP}:${trimmedPort}`)
    } else {
      setMessage('❌ Error: No se pudo actualizar la IP')
    }
    
    return success
  }, [inputIP, inputPort, updateIPConfig])

  /**
   * Set example values
   */
  const setExampleValues = useCallback(() => {
    handleIPChange('10.136.166.163')
    handlePortChange('8080')
    setMessage('📝 Ejemplo establecido - Modifica si es necesario')
  }, [handleIPChange, handlePortChange])

  /**
   * Set static values
   */
  const setStaticValues = useCallback(() => {
    handleIPChange('192.168.1.100')
    handlePortChange('2233')
    setMessage('🔧 Valores estáticos establecidos: 192.168.1.100:2233')
  }, [handleIPChange, handlePortChange])

  /**
   * Clear message
   */
  const clearMessage = useCallback(() => {
    setMessage('')
  }, [])

  return {
    // Input state
    inputIP,
    inputPort,
    message,
    
    // Store state
    currentIP,
    currentPort,
    
    // Methods
    handleIPChange,
    handlePortChange,
    updateConfiguration,
    setExampleValues,
    setStaticValues,
    clearMessage,
    setMessage
  }
}

/**
 * Hook for quick IP updates with common presets
 * @returns {Object} Quick update methods
 */
export function useQuickIPUpdate() {
  const { setIPAndPort, updateIPConfig } = useIPConfig()

  const quickUpdates = {
    /**
     * Set common development IP
     */
    setDevIP: () => {
      console.log('useQuickIPUpdate: Setting dev IP')
      return updateIPConfig('10.136.166.163', '8080')
    },

    /**
     * Set common home IP
     */
    setHomeIP: () => {
      console.log('useQuickIPUpdate: Setting home IP')
      return updateIPConfig('192.168.1.100', '2233')
    },

    /**
     * Set localhost IP
     */
    setLocalhostIP: () => {
      console.log('useQuickIPUpdate: Setting localhost IP')
      return updateIPConfig('127.0.0.1', '8080')
    },

    /**
     * Set custom IP
     * @param {string} ip - IP address
     * @param {string} port - Port number
     */
    setCustomIP: (ip, port) => {
      console.log('useQuickIPUpdate: Setting custom IP:', { ip, port })
      return updateIPConfig(ip, port)
    }
  }

  return quickUpdates
}
