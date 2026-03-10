/**
 * Robot API Service
 * Handles communication with the robot_gui.py server
 */

import configManager from './ConfigManager.js';
import requestManager from './RequestManager.js';

class RobotAPI {
  constructor() {
    // Load configuration from ConfigManager
    this.updateBaseURL();
    
    // Listen for configuration changes
    this.configChangeListener = configManager.addEventListener('configurationChanged', (data) => {
      console.log('RobotAPI: Configuration changed, updating base URL');
      this.updateBaseURL();
    });
    
    // Listen for configuration refresh
    this.configRefreshListener = configManager.addEventListener('configurationRefreshed', (data) => {
      console.log('RobotAPI: Configuration refreshed, updating base URL');
      this.updateBaseURL();
    });
    
    console.log('RobotAPI initialized with base URL:', this.baseURL);
  }

  /**
   * Update base URL from current configuration
   */
  updateBaseURL() {
    const config = configManager.getServerConfig();
    this.host = config.host;
    this.port = config.port;
    this.baseURL = config.baseURL;
    console.log('RobotAPI: Base URL updated to:', this.baseURL);
  }

  // Helper method for making HTTP requests
  async makeRequest(endpoint, options = {}) {
    // Update base URL in case configuration changed
    this.updateBaseURL();
    
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const requestOptions = { ...defaultOptions, ...options };

    try {
      // Update connection status to connecting
      configManager.updateConnectionStatus('connecting');
      
      const response = await fetch(url, requestOptions);
      
      if (!response.ok) {
        configManager.updateConnectionStatus('error');
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update connection status to connected
      configManager.updateConnectionStatus('connected');
      
      return { success: true, data };
    } catch (error) {
      console.error('API Request failed:', error);
      configManager.updateConnectionStatus('error');
      return { success: false, error: error.message };
    }
  }

  // CONFIGURATION METHODS

  /**
   * Get current server configuration
   * @returns {Object} Current host, port, and baseURL
   */
  getServerConfig() {
    return configManager.getServerConfig();
  }

  /**
   * Set server configuration
   * @param {string} host - Server host/IP
   * @param {string} port - Server port
   * @returns {boolean} True if configuration was updated
   */
  setServerConfig(host, port) {
    try {
      console.log('setServerConfig called with:', { 
        host, 
        port, 
        hostType: typeof host, 
        portType: typeof port,
        hostLength: host ? host.length : 0,
        portLength: port ? port.length : 0
      });
      
      const success = configManager.setServerConfig(host, port);
      
      if (success) {
        // Update local base URL
        this.updateBaseURL();
        console.log(`Robot API configuration updated: ${this.baseURL}`);
        console.log('Current config after update:', this.getServerConfig());
      }
      
      return success;
    } catch (error) {
      console.error('Error setting server config:', error);
      return false;
    }
  }

  /**
   * Reset to default configuration
   */
  resetToDefault() {
    configManager.resetToDefaults();
    this.updateBaseURL();
    console.log('Robot API configuration reset to default');
  }

  /**
   * Test connection with current configuration
   * @returns {Promise<Object>} Connection test result
   */
  async testConnection() {
    return requestManager.executeRequest('testConnection', async () => {
      try {
        console.log('Testing connection to:', this.baseURL);
        
        // Make a real request to test the connection
        const response = await this.makeRequest('/status');
        
        if (response.success) {
          console.log('Connection test successful');
          return {
            success: true,
            message: 'Connection successful',
            config: this.getServerConfig(),
            serverData: response.data
          };
        } else {
          console.log('Connection test failed:', response.error);
          return {
            success: false,
            message: `Connection failed: ${response.error}`,
            config: this.getServerConfig()
          };
        }
      } catch (error) {
        console.log('Connection test error:', error);
        return {
          success: false,
          message: `Connection error: ${error.message}`,
          config: this.getServerConfig()
        };
      }
    });
  }

  /**
   * Simple ping test for quick connection verification
   * @returns {Promise<Object>} Simple connection test result
   */
  async pingServer() {
    try {
      this.updateBaseURL();
      const url = `${this.baseURL}/status`;
      console.log('Pinging server:', url);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        configManager.updateConnectionStatus('connected');
        return { success: true, status: response.status, message: 'Server is reachable' };
      } else {
        configManager.updateConnectionStatus('error');
        return { success: false, status: response.status, message: `Server returned ${response.status}` };
      }
    } catch (error) {
      configManager.updateConnectionStatus('error');
      if (error.name === 'AbortError') {
        return { success: false, message: 'Connection timeout' };
      }
      return { success: false, message: error.message };
    }
  }

  /**
   * Get connection status
   * @returns {Object} Connection status information
   */
  getConnectionStatus() {
    return configManager.getConnectionStatus();
  }

  /**
   * Get configuration statistics
   * @returns {Object} Configuration statistics
   */
  getConfigStats() {
    return configManager.getConfigStats();
  }

  // GET METHODS - Retrieve data from robot

  /**
   * Get current robot status
   * @returns {Promise<Object>} Robot status including battery, temperature, connection
   */
  async getRobotStatus() {
    return this.makeRequest('/status');
  }

  /**
   * Get current robot position
   * @returns {Promise<Object>} Current positions of all robot parts
   */
  async getRobotPosition() {
    return this.makeRequest('/position');
  }

  /**
   * Get available robot classes
   * @returns {Promise<Object>} List of available classes with movements
   */
  async getAvailableClasses() {
    return requestManager.executeRequest('getAvailableClasses', () => {
      return this.makeRequest('/classes');
    });
  }

  /**
   * Get connection status of all systems
   * @returns {Promise<Object>} Connection status for all components
   */
  async getConnectionStatus() {
    return this.makeRequest('/connection');
  }

  /**
   * Get available movement presets
   * @returns {Promise<Object>} List of available movement presets
   */
  async getMovementPresets() {
    return this.makeRequest('/presets');
  }

  // POST METHODS - Send commands to robot

  /**
   * Move robot part to specified position
   * @param {Object} moveData - Movement data containing part, position, etc.
   * @returns {Promise<Object>} Success status and message
   */
  async moveRobot(moveData) {
    return this.makeRequest('/robot/move', {
      method: 'POST',
      body: JSON.stringify(moveData),
    });
  }

  /**
   * Make robot speak text
   * @param {string} text - Text for robot to speak
   * @returns {Promise<Object>} Success status and message
   */
  async speakText(text) {
    return this.makeRequest('/robot/speak', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  }

  /**
   * Start a robot class
   * @param {string} className - Name of the class to execute
   * @returns {Promise<Object>} Success status and message
   */
  async startClass(className) {
    return this.makeRequest('/class/execute', {
      method: 'POST',
      body: JSON.stringify({ class_name: className }),
    });
  }

  /**
   * Stop current robot class
   * @returns {Promise<Object>} Success status and message
   */
  async stopClass() {
    return this.makeRequest('/class/stop', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  /**
   * Get current class progress
   * @returns {Promise<Object>} Class progress information
   */
  async getClassProgress() {
    return requestManager.executeRequest('getClassProgress', () => {
      return this.makeRequest('/api/class/progress');
    });
  }

  /**
   * Get class details by name
   * @param {string} className - Name of the class to get details for
   * @returns {Promise<Object>} Class details
   */
  async getClassDetails(className) {
    const result = await this.getAvailableClasses();
    if (result.success && result.data.classes) {
      const classDetails = result.data.classes.find(cls => cls.name === className);
      return { success: true, data: classDetails };
    }
    return { success: false, error: 'Class not found' };
  }

  /**
   * Execute a movement preset
   * @param {string} presetName - Name of the preset to execute
   * @returns {Promise<Object>} Success status and message
   */
  async executePreset(presetName) {
    return this.makeRequest('/preset/execute', {
      method: 'POST',
      body: JSON.stringify({ preset: presetName }),
    });
  }

  /**
   * Emergency stop - immediately stop all robot movements
   * @returns {Promise<Object>} Success status and message
   */
  async emergencyStop() {
    return this.makeRequest('/robot/emergency', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // CONVENIENCE METHODS - Common robot movements

  /**
   * Move robot head
   * @param {number} x - X rotation (-45 to 45 degrees)
   * @param {number} y - Y rotation (-30 to 30 degrees)  
   * @param {number} z - Z rotation (-90 to 90 degrees)
   * @returns {Promise<Object>} Success status and message
   */
  async moveHead(x = 0, y = 0, z = 0) {
    return this.moveRobot({
      part: 'head',
      x,
      y,
      z
    });
  }

  /**
   * Move robot arm
   * @param {string} arm - 'leftArm' or 'rightArm'
   * @param {number} shoulder - Shoulder angle (-90 to 90 degrees)
   * @param {number} elbow - Elbow angle (0 to 120 degrees)
   * @param {number} wrist - Wrist angle (-45 to 45 degrees)
   * @returns {Promise<Object>} Success status and message
   */
  async moveArm(arm, shoulder = 0, elbow = 0, wrist = 0) {
    return this.makeRequest('/robot/move', {
      method: 'POST',
      body: JSON.stringify({
        part: arm,
        shoulder,
        elbow,
        wrist
      }),
    });
  }

  /**
   * Move robot hand fingers
   * @param {string} hand - 'leftHand' or 'rightHand'
   * @param {Object} fingers - Object with finger positions (thumb, index, middle, ring, pinky)
   * @returns {Promise<Object>} Success status and message
   */
  async moveHand(hand, fingers) {
    return this.makeRequest('/robot/move', {
      method: 'POST',
      body: JSON.stringify({
        part: hand,
        ...fingers
      }),
    });
  }

  // UTILITY METHODS

  /**
   * Get robot server URL
   * @returns {string} The base URL for the robot API
   */
  getServerURL() {
    this.updateBaseURL();
    return this.baseURL;
  }

  /**
   * Set robot server URL (for different environments)
   * @param {string} url - New base URL
   */
  setServerURL(url) {
    this.baseURL = url;
  }

  /**
   * Export current configuration
   * @returns {string} JSON string of current configuration
   */
  exportConfiguration() {
    return configManager.exportConfiguration();
  }

  /**
   * Import configuration from JSON
   * @param {string} jsonConfig - JSON string of configuration
   * @returns {boolean} Success status
   */
  importConfiguration(jsonConfig) {
    const success = configManager.importConfiguration(jsonConfig);
    if (success) {
      this.updateBaseURL();
    }
    return success;
  }

  // ROBOT MOVEMENT METHODS

  /**
   * Execute a preset movement
   * @param {string} presetName - Name of the preset to execute
   * @returns {Promise<Object>} Result of the operation
   */
  async executePreset(presetName) {
    return await this.makeRequest('/api/preset/execute', {
      method: 'POST',
      body: JSON.stringify({ preset: presetName })
    });
  }

  /**
   * Move robot parts with specific actions
   * @param {Object} movementData - Movement data including action, part, angles, etc.
   * @returns {Promise<Object>} Result of the operation
   */
  async moveRobot(movementData) {
    return await this.makeRequest('/api/robot/move', {
      method: 'POST',
      body: JSON.stringify(movementData)
    });
  }

  /**
   * Make robot speak text
   * @param {string} text - Text for robot to speak
   * @returns {Promise<Object>} Result of the operation
   */
  async speakText(text) {
    return await this.makeRequest('/api/robot/speak', {
      method: 'POST',
      body: JSON.stringify({ text: text })
    });
  }

  /**
   * Get robot status
   * @returns {Promise<Object>} Robot status information
   */
  async getRobotStatus() {
    return requestManager.executeRequest('getRobotStatus', () => {
      return this.makeRequest('/api/status');
    });
  }

  /**
   * Get robot position information
   * @returns {Promise<Object>} Robot position data
   */
  async getRobotPosition() {
    return await this.makeRequest('/api/position');
  }

  /**
   * Get available movement presets
   * @returns {Promise<Object>} Available presets
   */
  async getMovementPresets() {
    return await this.makeRequest('/api/presets');
  }

  /**
   * Emergency stop for robot
   * @returns {Promise<Object>} Result of emergency stop
   */
  async emergencyStop() {
    return await this.makeRequest('/api/robot/emergency', {
      method: 'POST',
      body: JSON.stringify({ action: 'emergency_stop' })
    });
  }

  // SPECIFIC MOVEMENT SHORTCUTS

  /**
   * Move robot to rest position
   * @returns {Promise<Object>} Result of the operation
   */
  async moveToRestPosition() {
    return await this.moveRobot({
      action: 'rest_position',
      name: 'Posición de Descanso'
    });
  }

  /**
   * Move robot to safe position
   * @returns {Promise<Object>} Result of the operation
   */
  async moveToSafePosition() {
    return await this.moveRobot({
      action: 'safe_position',
      name: 'Posición Segura'
    });
  }

  /**
   * Move arms to rest position
   * @returns {Promise<Object>} Result of the operation
   */
  async moveArmsToRest() {
    return await this.moveRobot({
      action: 'arms_rest',
      part: 'arms',
      name: 'Brazos Descanso'
    });
  }

  /**
   * Move arms to hug position
   * @returns {Promise<Object>} Result of the operation
   */
  async moveArmsToHug() {
    return await this.moveRobot({
      action: 'arms_hug',
      part: 'arms', 
      name: 'Abrazo'
    });
  }

  /**
   * Center neck position
   * @returns {Promise<Object>} Result of the operation
   */
  async centerNeck() {
    return await this.moveRobot({
      action: 'neck_center',
      part: 'neck',
      name: 'Cuello Centro'
    });
  }

  /**
   * Neck "yes" gesture
   * @returns {Promise<Object>} Result of the operation
   */
  async neckYes() {
    return await this.moveRobot({
      action: 'neck_yes',
      part: 'neck',
      name: 'Asentir'
    });
  }

  /**
   * Neck "no" gesture
   * @returns {Promise<Object>} Result of the operation
   */
  async neckNo() {
    return await this.moveRobot({
      action: 'neck_no',
      part: 'neck',
      name: 'Negar'
    });
  }

  /**
   * Random neck movement
   * @returns {Promise<Object>} Result of the operation
   */
  async neckRandom() {
    return await this.moveRobot({
      action: 'neck_random',
      part: 'neck',
      name: 'Cuello Aleatorio'
    });
  }

  /**
   * Handle teacher request - Pause class and listen for teacher's request
   * @param {string} requestType - Type of request: 'general', 'examples', 'repeat_question'
   * @returns {Promise<Object>} Result of the operation
   */
  async handleTeacherRequest(requestType = 'general') {
    return await this.makeRequest('/teacher/request', {
      method: 'POST',
      body: JSON.stringify({ request_type: requestType })
    });
  }

  /**
   * Pause or resume class
   * @param {boolean} isPaused - True to pause, false to resume
   * @returns {Promise<Object>} Result of the operation
   */
  async pauseClass(isPaused = true) {
    return await this.makeRequest('/teacher/pause', {
      method: 'POST',
      body: JSON.stringify({ is_paused: isPaused })
    });
  }
}

// Create singleton instance
const robotAPI = new RobotAPI();

export default robotAPI;
