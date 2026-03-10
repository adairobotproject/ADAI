/**
 * Classes State Manager Service
 * Handles all classes state persistence and management for the mobile app
 * Maintains state across page navigation
 */

class ClassesStateManager {
  constructor() {
    this.STORAGE_KEYS = {
      SELECTED_CLASS: 'classes_selected_class',
      IS_PLAYING: 'classes_is_playing',
      IS_CONNECTED: 'classes_is_connected',
      CLASSES_LIST: 'classes_list',
      CLASS_PROGRESS: 'classes_progress',
      LAST_LOADED: 'classes_last_loaded',
      CLASSES_VERSION: 'classes_version'
    };

    this.DEFAULT_STATE = {
      selectedClass: null,
      isPlaying: false,
      isConnected: false,
      classes: [],
      classProgress: null,
      lastLoaded: null,
      classesVersion: '1.0.0'
    };

    // Event listeners for state changes
    this.listeners = [];

    this.currentState = this.loadState();
    console.log('ClassesStateManager initialized with state:', this.currentState);
  }

  /**
   * Load state from localStorage
   * @returns {Object} Current state
   */
  loadState() {
    try {
      const state = { ...this.DEFAULT_STATE };

      // Load selected class
      state.selectedClass = this.getStorageItem(this.STORAGE_KEYS.SELECTED_CLASS, this.DEFAULT_STATE.selectedClass);
      
      // Load playing status
      state.isPlaying = this.getStorageItem(this.STORAGE_KEYS.IS_PLAYING, this.DEFAULT_STATE.isPlaying) === 'true';
      
      // Load connection status
      state.isConnected = this.getStorageItem(this.STORAGE_KEYS.IS_CONNECTED, this.DEFAULT_STATE.isConnected) === 'true';
      
      // Load classes list
      const savedClasses = this.getStorageItem(this.STORAGE_KEYS.CLASSES_LIST, null);
      if (savedClasses) {
        try {
          state.classes = JSON.parse(savedClasses);
        } catch (error) {
          console.warn('Error parsing classes list, using empty array:', error);
          state.classes = [];
        }
      }
      
      // Load class progress
      const savedProgress = this.getStorageItem(this.STORAGE_KEYS.CLASS_PROGRESS, null);
      if (savedProgress) {
        try {
          state.classProgress = JSON.parse(savedProgress);
        } catch (error) {
          console.warn('Error parsing class progress, using null:', error);
          state.classProgress = null;
        }
      }
      
      // Load last loaded timestamp
      state.lastLoaded = this.getStorageItem(this.STORAGE_KEYS.LAST_LOADED, this.DEFAULT_STATE.lastLoaded);
      
      // Load version
      state.classesVersion = this.getStorageItem(this.STORAGE_KEYS.CLASSES_VERSION, this.DEFAULT_STATE.classesVersion);

      console.log('Classes state loaded:', state);
      return state;
    } catch (error) {
      console.error('Error loading classes state:', error);
      return { ...this.DEFAULT_STATE };
    }
  }

  /**
   * Save state to localStorage
   * @param {Object} stateUpdate - State updates to save
   * @returns {boolean} Success status
   */
  saveState(stateUpdate) {
    try {
      const oldState = { ...this.currentState };
      const newState = { ...this.currentState, ...stateUpdate };
      
      // Save selected class
      this.setStorageItem(this.STORAGE_KEYS.SELECTED_CLASS, newState.selectedClass);
      
      // Save playing status
      this.setStorageItem(this.STORAGE_KEYS.IS_PLAYING, newState.isPlaying.toString());
      
      // Save connection status
      this.setStorageItem(this.STORAGE_KEYS.IS_CONNECTED, newState.isConnected.toString());
      
      // Save classes list
      this.setStorageItem(this.STORAGE_KEYS.CLASSES_LIST, JSON.stringify(newState.classes));
      
      // Save class progress
      this.setStorageItem(this.STORAGE_KEYS.CLASS_PROGRESS, JSON.stringify(newState.classProgress));
      
      // Save last loaded timestamp
      this.setStorageItem(this.STORAGE_KEYS.LAST_LOADED, newState.lastLoaded);
      
      // Save version
      this.setStorageItem(this.STORAGE_KEYS.CLASSES_VERSION, newState.classesVersion);
      
      this.currentState = newState;
      console.log('Classes state saved:', newState);
      
      // Notify listeners of state change
      this.notifyListeners('classesStateChanged', {
        oldState,
        newState,
        changedKeys: Object.keys(stateUpdate)
      });
      
      return true;
    } catch (error) {
      console.error('Error saving classes state:', error);
      return false;
    }
  }

  /**
   * Get current state
   * @returns {Object} Current state
   */
  getState() {
    return { ...this.currentState };
  }

  /**
   * Set selected class
   * @param {string|null} className - Class name to select
   * @returns {boolean} Success status
   */
  setSelectedClass(className) {
    console.log('Setting selected class:', className);
    return this.saveState({ selectedClass: className });
  }

  /**
   * Set playing status
   * @param {boolean} isPlaying - Whether a class is playing
   * @returns {boolean} Success status
   */
  setIsPlaying(isPlaying) {
    console.log('Setting isPlaying:', isPlaying);
    return this.saveState({ isPlaying });
  }

  /**
   * Set connection status
   * @param {boolean} isConnected - Whether robot is connected
   * @returns {boolean} Success status
   */
  setIsConnected(isConnected) {
    console.log('Setting isConnected:', isConnected);
    return this.saveState({ isConnected });
  }

  /**
   * Set classes list
   * @param {Array} classes - Array of classes
   * @returns {boolean} Success status
   */
  setClasses(classes) {
    console.log('Setting classes list:', classes.length, 'classes');
    const lastLoaded = new Date().toISOString();
    return this.saveState({ classes, lastLoaded });
  }

  /**
   * Set class progress
   * @param {Object|null} progress - Class progress object
   * @returns {boolean} Success status
   */
  setClassProgress(progress) {
    console.log('Setting class progress:', progress);
    return this.saveState({ classProgress: progress });
  }

  /**
   * Update class status in the classes list
   * @param {string} className - Class name to update
   * @param {string} status - New status ('running', 'available', 'completed')
   * @returns {boolean} Success status
   */
  updateClassStatus(className, status) {
    try {
      const updatedClasses = this.currentState.classes.map(cls => 
        cls.name === className ? { ...cls, status } : cls
      );
      return this.setClasses(updatedClasses);
    } catch (error) {
      console.error('Error updating class status:', error);
      return false;
    }
  }

  /**
   * Get class by name
   * @param {string} className - Class name
   * @returns {Object|null} Class object or null
   */
  getClassByName(className) {
    return this.currentState.classes.find(cls => cls.name === className) || null;
  }

  /**
   * Get classes by status
   * @param {string} status - Status to filter by
   * @returns {Array} Array of classes with the specified status
   */
  getClassesByStatus(status) {
    return this.currentState.classes.filter(cls => cls.status === status);
  }

  /**
   * Reset state to defaults
   * @returns {boolean} Success status
   */
  resetToDefaults() {
    try {
      this.currentState = { ...this.DEFAULT_STATE };
      
      // Clear all storage items
      Object.values(this.STORAGE_KEYS).forEach(key => {
        this.removeStorageItem(key);
      });
      
      console.log('Classes state reset to defaults');
      return true;
    } catch (error) {
      console.error('Error resetting classes state:', error);
      return false;
    }
  }

  /**
   * Export state as JSON
   * @returns {string} JSON string of current state
   */
  exportState() {
    try {
      return JSON.stringify(this.currentState, null, 2);
    } catch (error) {
      console.error('Error exporting classes state:', error);
      return null;
    }
  }

  /**
   * Import state from JSON
   * @param {string} jsonState - JSON string of state
   * @returns {boolean} Success status
   */
  importState(jsonState) {
    try {
      const importedState = JSON.parse(jsonState);
      return this.saveState(importedState);
    } catch (error) {
      console.error('Error importing classes state:', error);
      return false;
    }
  }

  /**
   * Get state statistics
   * @returns {Object} State statistics
   */
  getStateStats() {
    const stats = {
      totalClasses: this.currentState.classes.length,
      runningClasses: this.getClassesByStatus('running').length,
      availableClasses: this.getClassesByStatus('available').length,
      completedClasses: this.getClassesByStatus('completed').length,
      isPlaying: this.currentState.isPlaying,
      isConnected: this.currentState.isConnected,
      selectedClass: this.currentState.selectedClass,
      lastLoaded: this.currentState.lastLoaded,
      classesVersion: this.currentState.classesVersion
    };

    return stats;
  }

  // Storage helper methods
  getStorageItem(key, defaultValue) {
    try {
      if (typeof localStorage !== 'undefined') {
        const item = localStorage.getItem(key);
        return item !== null ? item : defaultValue;
      }
    } catch (error) {
      console.warn('localStorage not available:', error);
    }
    return defaultValue;
  }

  setStorageItem(key, value) {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(key, value);
        return true;
      }
    } catch (error) {
      console.warn('localStorage not available:', error);
    }
    return false;
  }

  removeStorageItem(key) {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem(key);
        return true;
      }
    } catch (error) {
      console.warn('localStorage not available:', error);
    }
    return false;
  }

  // Event management methods
  
  /**
   * Add event listener for state changes
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   * @returns {Function} Unsubscribe function
   */
  addEventListener(event, callback) {
    if (typeof callback !== 'function') {
      console.warn('Event listener callback must be a function');
      return () => {};
    }
    
    const listener = { event, callback };
    this.listeners.push(listener);
    
    console.log(`Classes event listener added for '${event}'. Total listeners: ${this.listeners.length}`);
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
        console.log(`Classes event listener removed for '${event}'. Total listeners: ${this.listeners.length}`);
      }
    };
  }
  
  /**
   * Remove event listener
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  removeEventListener(event, callback) {
    this.listeners = this.listeners.filter(
      listener => !(listener.event === event && listener.callback === callback)
    );
    console.log(`Classes event listeners removed for '${event}'. Total listeners: ${this.listeners.length}`);
  }
  
  /**
   * Notify all listeners of an event
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  notifyListeners(event, data) {
    const relevantListeners = this.listeners.filter(listener => listener.event === event);
    console.log(`Notifying ${relevantListeners.length} classes listeners for event '${event}'`);
    
    relevantListeners.forEach(listener => {
      try {
        listener.callback(data);
      } catch (error) {
        console.error(`Error in classes event listener for '${event}':`, error);
      }
    });
  }
  
  /**
   * Force refresh state from storage
   * @returns {boolean} Success status
   */
  forceRefresh() {
    try {
      const oldState = { ...this.currentState };
      this.currentState = this.loadState();
      
      console.log('Classes state force refreshed:', this.currentState);
      
      // Notify listeners of state refresh
      this.notifyListeners('classesStateRefreshed', {
        oldState,
        newState: this.currentState
      });
      
      return true;
    } catch (error) {
      console.error('Error force refreshing classes state:', error);
      return false;
    }
  }
}

// Create singleton instance
const classesStateManager = new ClassesStateManager();

export default classesStateManager;
