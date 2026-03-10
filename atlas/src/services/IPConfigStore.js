/**
 * IP Configuration Store
 * Handles IP configuration state with persistence and real-time updates
 * Solves ReactLynx input bug by using programmatic updates
 */

class IPConfigStore {
  constructor() {
    this.STORAGE_KEYS = {
      CURRENT_IP: 'ipconfig_current_ip',
      CURRENT_PORT: 'ipconfig_current_port',
      LAST_UPDATED: 'ipconfig_last_updated',
      UPDATE_HISTORY: 'ipconfig_update_history',
      IP_VERSION: 'ipconfig_version'
    };

    this.DEFAULT_STATE = {
      currentIP: '',
      currentPort: '',
      lastUpdated: null,
      updateHistory: [],
      version: '1.0.0'
    };

    // Event listeners for state changes
    this.listeners = [];

    this.currentState = this.loadState();
    console.log('IPConfigStore initialized with state:', this.currentState);
  }

  /**
   * Load state from localStorage
   * @returns {Object} Current state
   */
  loadState() {
    try {
      const state = { ...this.DEFAULT_STATE };

      // Load current IP and port
      state.currentIP = this.getStorageItem(this.STORAGE_KEYS.CURRENT_IP, this.DEFAULT_STATE.currentIP);
      state.currentPort = this.getStorageItem(this.STORAGE_KEYS.CURRENT_PORT, this.DEFAULT_STATE.currentPort);
      
      // Load last updated timestamp
      state.lastUpdated = this.getStorageItem(this.STORAGE_KEYS.LAST_UPDATED, this.DEFAULT_STATE.lastUpdated);
      
      // Load update history
      const savedHistory = this.getStorageItem(this.STORAGE_KEYS.UPDATE_HISTORY, null);
      if (savedHistory) {
        try {
          state.updateHistory = JSON.parse(savedHistory);
        } catch (error) {
          console.warn('Error parsing update history, using empty array:', error);
          state.updateHistory = [];
        }
      }
      
      // Load version
      state.version = this.getStorageItem(this.STORAGE_KEYS.IP_VERSION, this.DEFAULT_STATE.version);

      console.log('IP config state loaded:', state);
      return state;
    } catch (error) {
      console.error('Error loading IP config state:', error);
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
      
      // Save current IP and port
      this.setStorageItem(this.STORAGE_KEYS.CURRENT_IP, newState.currentIP);
      this.setStorageItem(this.STORAGE_KEYS.CURRENT_PORT, newState.currentPort);
      
      // Save last updated timestamp
      this.setStorageItem(this.STORAGE_KEYS.LAST_UPDATED, newState.lastUpdated);
      
      // Save update history
      this.setStorageItem(this.STORAGE_KEYS.UPDATE_HISTORY, JSON.stringify(newState.updateHistory));
      
      // Save version
      this.setStorageItem(this.STORAGE_KEYS.IP_VERSION, newState.version);
      
      this.currentState = newState;
      console.log('IP config state saved:', newState);
      
      // Notify listeners of state change
      this.notifyListeners('ipConfigChanged', {
        oldState,
        newState,
        changedKeys: Object.keys(stateUpdate)
      });
      
      return true;
    } catch (error) {
      console.error('Error saving IP config state:', error);
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
   * Set current IP
   * @param {string} ip - IP address
   * @returns {boolean} Success status
   */
  setCurrentIP(ip) {
    console.log('Setting current IP:', ip);
    const timestamp = new Date().toISOString();
    
    // Add to history
    const historyEntry = {
      ip,
      timestamp,
      action: 'ip_updated'
    };
    
    const newHistory = [historyEntry, ...this.currentState.updateHistory].slice(0, 10); // Keep last 10 entries
    
    return this.saveState({ 
      currentIP: ip,
      lastUpdated: timestamp,
      updateHistory: newHistory
    });
  }

  /**
   * Set current port
   * @param {string} port - Port number
   * @returns {boolean} Success status
   */
  setCurrentPort(port) {
    console.log('Setting current port:', port);
    const timestamp = new Date().toISOString();
    
    // Add to history
    const historyEntry = {
      port,
      timestamp,
      action: 'port_updated'
    };
    
    const newHistory = [historyEntry, ...this.currentState.updateHistory].slice(0, 10); // Keep last 10 entries
    
    return this.saveState({ 
      currentPort: port,
      lastUpdated: timestamp,
      updateHistory: newHistory
    });
  }

  /**
   * Set both IP and port
   * @param {string} ip - IP address
   * @param {string} port - Port number
   * @returns {boolean} Success status
   */
  setIPAndPort(ip, port) {
    console.log('Setting IP and port:', { ip, port });
    const timestamp = new Date().toISOString();
    
    // Add to history
    const historyEntry = {
      ip,
      port,
      timestamp,
      action: 'ip_port_updated'
    };
    
    const newHistory = [historyEntry, ...this.currentState.updateHistory].slice(0, 10); // Keep last 10 entries
    
    return this.saveState({ 
      currentIP: ip,
      currentPort: port,
      lastUpdated: timestamp,
      updateHistory: newHistory
    });
  }

  /**
   * Get current IP and port as URL
   * @returns {string} Complete URL
   */
  getCurrentURL() {
    if (this.currentState.currentIP && this.currentState.currentPort) {
      return `http://${this.currentState.currentIP}:${this.currentState.currentPort}/api`;
    }
    return '';
  }

  /**
   * Get formatted display string
   * @returns {string} Formatted IP:Port string
   */
  getFormattedAddress() {
    if (this.currentState.currentIP && this.currentState.currentPort) {
      return `${this.currentState.currentIP}:${this.currentState.currentPort}`;
    }
    return 'No configurado';
  }

  /**
   * Check if IP and port are set
   * @returns {boolean} True if both are configured
   */
  isConfigured() {
    return !!(this.currentState.currentIP && this.currentState.currentPort);
  }

  /**
   * Get recent update history
   * @param {number} limit - Number of recent entries to return
   * @returns {Array} Recent update history
   */
  getRecentHistory(limit = 5) {
    return this.currentState.updateHistory.slice(0, limit);
  }

  /**
   * Clear update history
   * @returns {boolean} Success status
   */
  clearHistory() {
    console.log('Clearing IP config history');
    return this.saveState({ updateHistory: [] });
  }

  /**
   * Reset to defaults
   * @returns {boolean} Success status
   */
  resetToDefaults() {
    try {
      this.currentState = { ...this.DEFAULT_STATE };
      
      // Clear all storage items
      Object.values(this.STORAGE_KEYS).forEach(key => {
        this.removeStorageItem(key);
      });
      
      console.log('IP config state reset to defaults');
      return true;
    } catch (error) {
      console.error('Error resetting IP config state:', error);
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
      console.error('Error exporting IP config state:', error);
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
      console.error('Error importing IP config state:', error);
      return false;
    }
  }

  /**
   * Get state statistics
   * @returns {Object} State statistics
   */
  getStateStats() {
    const stats = {
      isConfigured: this.isConfigured(),
      currentIP: this.currentState.currentIP,
      currentPort: this.currentState.currentPort,
      formattedAddress: this.getFormattedAddress(),
      currentURL: this.getCurrentURL(),
      lastUpdated: this.currentState.lastUpdated,
      historyCount: this.currentState.updateHistory.length,
      version: this.currentState.version
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
    
    console.log(`IP config event listener added for '${event}'. Total listeners: ${this.listeners.length}`);
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
        console.log(`IP config event listener removed for '${event}'. Total listeners: ${this.listeners.length}`);
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
    console.log(`IP config event listeners removed for '${event}'. Total listeners: ${this.listeners.length}`);
  }
  
  /**
   * Notify all listeners of an event
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  notifyListeners(event, data) {
    const relevantListeners = this.listeners.filter(listener => listener.event === event);
    console.log(`Notifying ${relevantListeners.length} IP config listeners for event '${event}'`);
    
    relevantListeners.forEach(listener => {
      try {
        listener.callback(data);
      } catch (error) {
        console.error(`Error in IP config event listener for '${event}':`, error);
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
      
      console.log('IP config state force refreshed:', this.currentState);
      
      // Notify listeners of state refresh
      this.notifyListeners('ipConfigRefreshed', {
        oldState,
        newState: this.currentState
      });
      
      return true;
    } catch (error) {
      console.error('Error force refreshing IP config state:', error);
      return false;
    }
  }
}

// Create singleton instance
const ipConfigStore = new IPConfigStore();

export default ipConfigStore;
