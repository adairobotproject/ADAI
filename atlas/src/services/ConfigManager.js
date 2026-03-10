/**
 * Configuration Manager Service
 * Handles all configuration persistence and management for the mobile app
 */

class ConfigManager {
  constructor() {
    this.STORAGE_KEYS = {
      SERVER_HOST: 'robotAPI_host',
      SERVER_PORT: 'robotAPI_port',
      CONNECTION_STATUS: 'connection_status',
      LAST_CONNECTED: 'last_connected',
      CONFIG_VERSION: 'config_version',
      USER_PREFERENCES: 'user_preferences'
    };

    this.DEFAULT_CONFIG = {
      host: '10.136.166.163',
      port: '8080',
      connectionStatus: 'disconnected',
      lastConnected: null,
      configVersion: '1.0.0',
      userPreferences: {
        autoConnect: false,
        connectionTimeout: 5000,
        retryAttempts: 3,
        theme: 'dark'
      }
    };

    // Event listeners for configuration changes
    this.listeners = [];

    this.currentConfig = this.loadConfiguration();
    console.log('ConfigManager initialized with config:', this.currentConfig);
  }

  /**
   * Load configuration from localStorage
   * @returns {Object} Current configuration
   */
  loadConfiguration() {
    try {
      const config = { ...this.DEFAULT_CONFIG };

      // Load server configuration
      config.host = this.getStorageItem(this.STORAGE_KEYS.SERVER_HOST, this.DEFAULT_CONFIG.host);
      config.port = this.getStorageItem(this.STORAGE_KEYS.SERVER_PORT, this.DEFAULT_CONFIG.port);
      
      // Load connection status
      config.connectionStatus = this.getStorageItem(this.STORAGE_KEYS.CONNECTION_STATUS, this.DEFAULT_CONFIG.connectionStatus);
      config.lastConnected = this.getStorageItem(this.STORAGE_KEYS.LAST_CONNECTED, this.DEFAULT_CONFIG.lastConnected);
      
      // Load version
      config.configVersion = this.getStorageItem(this.STORAGE_KEYS.CONFIG_VERSION, this.DEFAULT_CONFIG.configVersion);
      
      // Load user preferences
      const savedPreferences = this.getStorageItem(this.STORAGE_KEYS.USER_PREFERENCES, null);
      if (savedPreferences) {
        try {
          config.userPreferences = { ...this.DEFAULT_CONFIG.userPreferences, ...JSON.parse(savedPreferences) };
        } catch (error) {
          console.warn('Error parsing user preferences, using defaults:', error);
        }
      }

      console.log('Configuration loaded:', config);
      return config;
    } catch (error) {
      console.error('Error loading configuration:', error);
      return { ...this.DEFAULT_CONFIG };
    }
  }

  /**
   * Save configuration to localStorage
   * @param {Object} config - Configuration to save
   * @returns {boolean} Success status
   */
  saveConfiguration(config) {
    try {
      const oldConfig = { ...this.currentConfig };
      const configToSave = { ...this.currentConfig, ...config };
      
      // Save server configuration
      this.setStorageItem(this.STORAGE_KEYS.SERVER_HOST, configToSave.host);
      this.setStorageItem(this.STORAGE_KEYS.SERVER_PORT, configToSave.port);
      
      // Save connection status
      this.setStorageItem(this.STORAGE_KEYS.CONNECTION_STATUS, configToSave.connectionStatus);
      this.setStorageItem(this.STORAGE_KEYS.LAST_CONNECTED, configToSave.lastConnected);
      
      // Save version
      this.setStorageItem(this.STORAGE_KEYS.CONFIG_VERSION, configToSave.configVersion);
      
      // Save user preferences
      this.setStorageItem(this.STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(configToSave.userPreferences));
      
      this.currentConfig = configToSave;
      console.log('Configuration saved:', configToSave);
      
      // Notify listeners of configuration change
      this.notifyListeners('configurationChanged', {
        oldConfig,
        newConfig: configToSave,
        changedKeys: Object.keys(config)
      });
      
      return true;
    } catch (error) {
      console.error('Error saving configuration:', error);
      return false;
    }
  }

  /**
   * Get current configuration
   * @returns {Object} Current configuration
   */
  getConfiguration() {
    return { ...this.currentConfig };
  }

  /**
   * Get server configuration
   * @returns {Object} Server host, port, and baseURL
   */
  getServerConfig() {
    return {
      host: this.currentConfig.host,
      port: this.currentConfig.port,
      baseURL: `http://${this.currentConfig.host}:${this.currentConfig.port}/api`
    };
  }

  /**
   * Set server configuration
   * @param {string} host - Server host/IP
   * @param {string} port - Server port
   * @returns {boolean} Success status
   */
  setServerConfig(host, port) {
    try {
      console.log('Setting server config:', { host, port });
      
      // Validate inputs
      if (!host || !port) {
        throw new Error('Host and port are required');
      }

      const trimmedHost = String(host).trim();
      const trimmedPort = String(port).trim();
      
      if (!trimmedHost || !trimmedPort) {
        throw new Error('Host and port cannot be empty after trimming');
      }
      
      return this.saveConfiguration({
        host: trimmedHost,
        port: trimmedPort
      });
    } catch (error) {
      console.error('Error setting server config:', error);
      return false;
    }
  }

  /**
   * Update connection status
   * @param {string} status - Connection status ('connected', 'disconnected', 'connecting', 'error')
   * @returns {boolean} Success status
   */
  updateConnectionStatus(status) {
    const timestamp = new Date().toISOString();
    const lastConnected = status === 'connected' ? timestamp : this.currentConfig.lastConnected;
    
    return this.saveConfiguration({
      connectionStatus: status,
      lastConnected
    });
  }

  /**
   * Get connection status
   * @returns {Object} Connection status information
   */
  getConnectionStatus() {
    return {
      status: this.currentConfig.connectionStatus,
      lastConnected: this.currentConfig.lastConnected,
      isConnected: this.currentConfig.connectionStatus === 'connected'
    };
  }

  /**
   * Update user preferences
   * @param {Object} preferences - User preferences to update
   * @returns {boolean} Success status
   */
  updateUserPreferences(preferences) {
    try {
      const updatedPreferences = { ...this.currentConfig.userPreferences, ...preferences };
      return this.saveConfiguration({
        userPreferences: updatedPreferences
      });
    } catch (error) {
      console.error('Error updating user preferences:', error);
      return false;
    }
  }

  /**
   * Get user preferences
   * @returns {Object} Current user preferences
   */
  getUserPreferences() {
    return { ...this.currentConfig.userPreferences };
  }

  /**
   * Reset configuration to defaults
   * @returns {boolean} Success status
   */
  resetToDefaults() {
    try {
      this.currentConfig = { ...this.DEFAULT_CONFIG };
      
      // Clear all storage items
      Object.values(this.STORAGE_KEYS).forEach(key => {
        this.removeStorageItem(key);
      });
      
      console.log('Configuration reset to defaults');
      return true;
    } catch (error) {
      console.error('Error resetting configuration:', error);
      return false;
    }
  }

  /**
   * Export configuration as JSON
   * @returns {string} JSON string of current configuration
   */
  exportConfiguration() {
    try {
      return JSON.stringify(this.currentConfig, null, 2);
    } catch (error) {
      console.error('Error exporting configuration:', error);
      return null;
    }
  }

  /**
   * Import configuration from JSON
   * @param {string} jsonConfig - JSON string of configuration
   * @returns {boolean} Success status
   */
  importConfiguration(jsonConfig) {
    try {
      const importedConfig = JSON.parse(jsonConfig);
      return this.saveConfiguration(importedConfig);
    } catch (error) {
      console.error('Error importing configuration:', error);
      return false;
    }
  }

  /**
   * Get configuration statistics
   * @returns {Object} Configuration statistics
   */
  getConfigStats() {
    const stats = {
      totalKeys: Object.keys(this.STORAGE_KEYS).length,
      savedKeys: 0,
      missingKeys: [],
      configVersion: this.currentConfig.configVersion,
      lastModified: null
    };

    Object.values(this.STORAGE_KEYS).forEach(key => {
      const value = this.getStorageItem(key, null);
      if (value !== null) {
        stats.savedKeys++;
      } else {
        stats.missingKeys.push(key);
      }
    });

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
   * Add event listener for configuration changes
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
    
    console.log(`Event listener added for '${event}'. Total listeners: ${this.listeners.length}`);
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
        console.log(`Event listener removed for '${event}'. Total listeners: ${this.listeners.length}`);
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
    console.log(`Event listeners removed for '${event}'. Total listeners: ${this.listeners.length}`);
  }
  
  /**
   * Notify all listeners of an event
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  notifyListeners(event, data) {
    const relevantListeners = this.listeners.filter(listener => listener.event === event);
    console.log(`Notifying ${relevantListeners.length} listeners for event '${event}'`);
    
    relevantListeners.forEach(listener => {
      try {
        listener.callback(data);
      } catch (error) {
        console.error(`Error in event listener for '${event}':`, error);
      }
    });
  }
  
  /**
   * Force refresh configuration from storage
   * @returns {boolean} Success status
   */
  forceRefresh() {
    try {
      const oldConfig = { ...this.currentConfig };
      this.currentConfig = this.loadConfiguration();
      
      console.log('Configuration force refreshed:', this.currentConfig);
      
      // Notify listeners of configuration refresh
      this.notifyListeners('configurationRefreshed', {
        oldConfig,
        newConfig: this.currentConfig
      });
      
      return true;
    } catch (error) {
      console.error('Error force refreshing configuration:', error);
      return false;
    }
  }
}

// Create singleton instance
const configManager = new ConfigManager();

export default configManager;
