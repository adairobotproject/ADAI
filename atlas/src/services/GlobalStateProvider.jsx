/**
 * Global State Provider Component
 * Provides persistent state management across all screens
 * Ensures state is maintained when navigating between pages
 */

import { useEffect } from '@lynx-js/react'
import { useClassesState } from './useClassesState'
import { useConfig } from './useConfig'

/**
 * Global State Provider Component
 * This component should be used at the App level to initialize
 * and maintain global state across all screens
 */
export function GlobalStateProvider({ children }) {
  // Initialize all global state hooks
  const classesState = useClassesState()
  const configState = useConfig()

  useEffect(() => {
    console.log('GlobalStateProvider: Initializing global state')
    
    // Log current state for debugging
    console.log('Classes state:', {
      selectedClass: classesState.selectedClass,
      isPlaying: classesState.isPlaying,
      isConnected: classesState.isConnected,
      totalClasses: classesState.totalClasses,
      lastLoaded: classesState.lastLoaded
    })
    
    console.log('Config state:', {
      isConnected: configState.isConnected,
      baseURL: configState.baseURL,
      host: configState.serverConfig.host,
      port: configState.serverConfig.port
    })
  }, [])

  // This component doesn't render anything, it just provides state management
  return children
}

/**
 * Hook to access global state from any component
 * @returns {Object} Global state object
 */
export function useGlobalState() {
  const classesState = useClassesState()
  const configState = useConfig()

  return {
    // Classes state
    classes: {
      selectedClass: classesState.selectedClass,
      isPlaying: classesState.isPlaying,
      isConnected: classesState.isConnected,
      classes: classesState.classes,
      classProgress: classesState.classProgress,
      totalClasses: classesState.totalClasses,
      runningClasses: classesState.runningClasses,
      availableClasses: classesState.availableClasses,
      completedClasses: classesState.completedClasses,
      hasSelectedClass: classesState.hasSelectedClass,
      isClassActive: classesState.isClassActive,
      lastLoaded: classesState.lastLoaded,
      classesVersion: classesState.classesVersion
    },
    
    // Config state
    config: {
      isConnected: configState.isConnected,
      baseURL: configState.baseURL,
      host: configState.serverConfig.host,
      port: configState.serverConfig.port,
      connectionStatus: configState.connectionStatus,
      configStats: configState.configStats
    },
    
    // Combined state
    global: {
      isAnyClassActive: classesState.isClassActive,
      isRobotConnected: configState.isConnected && classesState.isConnected,
      hasClasses: classesState.totalClasses > 0,
      lastActivity: classesState.lastLoaded || configState.connectionStatus.lastConnected
    }
  }
}

/**
 * Hook for classes state only
 * @returns {Object} Classes state and methods
 */
export function useGlobalClassesState() {
  return useClassesState()
}

/**
 * Hook for config state only
 * @returns {Object} Config state and methods
 */
export function useGlobalConfigState() {
  return useConfig()
}
