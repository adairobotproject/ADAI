/**
 * React Hook for Classes State Management
 * Provides reactive access to classes state with persistence across page navigation
 */

import { useState, useEffect, useCallback } from '@lynx-js/react'
import classesStateManager from './ClassesStateManager.js'
import robotAPI from './RobotAPI.js'

/**
 * Custom hook for accessing and managing classes state
 * @returns {Object} Classes state and methods
 */
export function useClassesState() {
  const [state, setState] = useState(classesStateManager.getState())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    console.log('useClassesState: Setting up classes state listeners')
    
    // Listen for state changes
    const unsubscribeStateChange = classesStateManager.addEventListener('classesStateChanged', (data) => {
      console.log('useClassesState: State changed event received', data)
      setState(classesStateManager.getState())
    })

    // Listen for state refresh
    const unsubscribeStateRefresh = classesStateManager.addEventListener('classesStateRefreshed', (data) => {
      console.log('useClassesState: State refreshed event received', data)
      setState(classesStateManager.getState())
    })

    // Cleanup listeners on unmount
    return () => {
      console.log('useClassesState: Cleaning up classes state listeners')
      unsubscribeStateChange()
      unsubscribeStateRefresh()
    }
  }, [])

  // Classes state methods
  const methods = {
    /**
     * Set selected class
     * @param {string|null} className - Class name to select
     * @returns {boolean} Success status
     */
    setSelectedClass: (className) => {
      console.log('useClassesState: Setting selected class:', className)
      const success = classesStateManager.setSelectedClass(className)
      if (success) {
        setState(classesStateManager.getState())
      }
      return success
    },

    /**
     * Set playing status
     * @param {boolean} isPlaying - Whether a class is playing
     * @returns {boolean} Success status
     */
    setIsPlaying: (isPlaying) => {
      console.log('useClassesState: Setting isPlaying:', isPlaying)
      const success = classesStateManager.setIsPlaying(isPlaying)
      if (success) {
        setState(classesStateManager.getState())
      }
      return success
    },

    /**
     * Set connection status
     * @param {boolean} isConnected - Whether robot is connected
     * @returns {boolean} Success status
     */
    setIsConnected: (isConnected) => {
      console.log('useClassesState: Setting isConnected:', isConnected)
      const success = classesStateManager.setIsConnected(isConnected)
      if (success) {
        setState(classesStateManager.getState())
      }
      return success
    },

    /**
     * Set classes list
     * @param {Array} classes - Array of classes
     * @returns {boolean} Success status
     */
    setClasses: (classes) => {
      console.log('useClassesState: Setting classes list:', classes.length, 'classes')
      const success = classesStateManager.setClasses(classes)
      if (success) {
        setState(classesStateManager.getState())
      }
      return success
    },

    /**
     * Set class progress
     * @param {Object|null} progress - Class progress object
     * @returns {boolean} Success status
     */
    setClassProgress: (progress) => {
      console.log('useClassesState: Setting class progress:', progress)
      const success = classesStateManager.setClassProgress(progress)
      if (success) {
        setState(classesStateManager.getState())
      }
      return success
    },

    /**
     * Update class status in the classes list
     * @param {string} className - Class name to update
     * @param {string} status - New status ('running', 'available', 'completed')
     * @returns {boolean} Success status
     */
    updateClassStatus: (className, status) => {
      console.log('useClassesState: Updating class status:', className, 'to', status)
      const success = classesStateManager.updateClassStatus(className, status)
      if (success) {
        setState(classesStateManager.getState())
      }
      return success
    },

    /**
     * Get class by name
     * @param {string} className - Class name
     * @returns {Object|null} Class object or null
     */
    getClassByName: (className) => {
      return classesStateManager.getClassByName(className)
    },

    /**
     * Get classes by status
     * @param {string} status - Status to filter by
     * @returns {Array} Array of classes with the specified status
     */
    getClassesByStatus: (status) => {
      return classesStateManager.getClassesByStatus(status)
    },

    /**
     * Reset state to defaults
     * @returns {boolean} Success status
     */
    resetToDefaults: () => {
      console.log('useClassesState: Resetting to defaults')
      const success = classesStateManager.resetToDefaults()
      if (success) {
        setState(classesStateManager.getState())
      }
      return success
    },

    /**
     * Force refresh state from storage
     * @returns {boolean} Success status
     */
    forceRefresh: () => {
      console.log('useClassesState: Force refreshing state')
      return classesStateManager.forceRefresh()
    },

    /**
     * Export current state
     * @returns {string} JSON state
     */
    exportState: () => {
      return classesStateManager.exportState()
    },

    /**
     * Import state from JSON
     * @param {string} jsonState - JSON state
     * @returns {boolean} Success status
     */
    importState: (jsonState) => {
      console.log('useClassesState: Importing state')
      const success = classesStateManager.importState(jsonState)
      if (success) {
        setState(classesStateManager.getState())
      }
      return success
    }
  }

  return {
    // State
    selectedClass: state.selectedClass,
    isPlaying: state.isPlaying,
    isConnected: state.isConnected,
    classes: state.classes,
    classProgress: state.classProgress,
    lastLoaded: state.lastLoaded,
    classesVersion: state.classesVersion,
    loading,
    error,
    
    // Computed values
    totalClasses: state.classes.length,
    runningClasses: state.classes.filter(c => c.status === 'running').length,
    availableClasses: state.classes.filter(c => c.status === 'available').length,
    completedClasses: state.classes.filter(c => c.status === 'completed').length,
    hasSelectedClass: state.selectedClass !== null,
    isClassActive: state.isPlaying && state.selectedClass !== null,
    
    // Methods
    ...methods
  }
}

/**
 * Hook for loading classes from robot API with state persistence
 * @returns {Object} Classes loading state and methods
 */
export function useClassesLoader() {
  const { 
    classes, 
    isConnected
  } = useClassesState()
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  /**
   * Load classes from robot API
   */
  const loadClassesFromAPI = useCallback(async () => {
    // Prevent multiple simultaneous loads
    if (loading) {
      console.log('Classes already loading, skipping...')
      return
    }
    
    try {
      setLoading(true)
      setError(null)
      
      console.log('Loading classes from robot API...')
      
      const connected = await robotAPI.testConnection()
      classesStateManager.setIsConnected(connected.success)
      
      if (connected.success) {
        const result = await robotAPI.getAvailableClasses()
        if (result.success && result.data.classes) {
          classesStateManager.setClasses(result.data.classes)
          console.log('Classes loaded successfully:', result.data.classes.length)
        } else {
          const errorMsg = 'No se pudieron cargar las clases'
          setError(errorMsg)
        }
      } else {
        const errorMsg = 'No se pudo conectar con el robot'
        setError(errorMsg)
      }
    } catch (error) {
      console.error('Failed to load classes from robot:', error)
      const errorMsg = 'Error al cargar las clases'
      setError(errorMsg)
      classesStateManager.setIsConnected(false)
    } finally {
      setLoading(false)
    }
  }, [loading])

  /**
   * Start a class
   * @param {string} className - Class name to start
   */
  const startClass = useCallback(async (className) => {
    if (!isConnected) {
      console.log('Robot not connected')
      return false
    }
    
    try {
      console.log(`Starting class ${className}`)
      
      const result = await robotAPI.startClass(className)
      if (result.success) {
        console.log(`Class ${className} started successfully`)
        return true
      } else {
        console.error('Failed to start class:', result.error)
        return false
      }
    } catch (error) {
      console.error('Error starting class:', error)
      return false
    }
  }, [isConnected])

  /**
   * Stop current class
   */
  const stopClass = useCallback(async () => {
    if (!isConnected) {
      console.log('Robot not connected')
      return false
    }
    
    try {
      const result = await robotAPI.stopClass()
      if (result.success) {
        console.log('Class stopped successfully')
        return true
      } else {
        console.error('Failed to stop class:', result.error)
        return false
      }
    } catch (error) {
      console.error('Error stopping class:', error)
      return false
    }
  }, [isConnected])

  return {
    // State
    classes,
    isConnected,
    loading,
    error,
    
    // Methods
    loadClassesFromAPI,
    startClass,
    stopClass
  }
}

/**
 * Hook for class control operations
 * @returns {Object} Class control state and methods
 */
export function useClassControl() {
  const { 
    selectedClass, 
    isPlaying, 
    setSelectedClass, 
    setIsPlaying, 
    updateClassStatus 
  } = useClassesState()
  
  const { startClass, stopClass } = useClassesLoader()

  /**
   * Handle starting a class
   * @param {string} className - Class name to start
   */
  const handleStartClass = useCallback(async (className) => {
    try {
      setIsPlaying(true)
      setSelectedClass(className)
      updateClassStatus(className, 'running')
      
      const success = await startClass(className)
      if (!success) {
        setIsPlaying(false)
        setSelectedClass(null)
        updateClassStatus(className, 'available')
      }
      
      return success
    } catch (error) {
      console.error('Error in handleStartClass:', error)
      setIsPlaying(false)
      setSelectedClass(null)
      updateClassStatus(className, 'available')
      return false
    }
  }, [setIsPlaying, setSelectedClass, updateClassStatus, startClass])

  /**
   * Handle stopping current class
   */
  const handleStopClass = useCallback(async () => {
    try {
      const success = await stopClass()
      if (success) {
        if (selectedClass) {
          updateClassStatus(selectedClass, 'completed')
        }
        setIsPlaying(false)
        setSelectedClass(null)
      }
      
      return success
    } catch (error) {
      console.error('Error in handleStopClass:', error)
      return false
    }
  }, [stopClass, selectedClass, updateClassStatus, setIsPlaying, setSelectedClass])

  return {
    // State
    selectedClass,
    isPlaying,
    
    // Methods
    handleStartClass,
    handleStopClass
  }
}
