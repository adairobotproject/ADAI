# 🔧 Configuration Troubleshooting Guide

## ❌ "Save Configuration button doesn't change IP/Port"

### **Problem Description**
The "Save Configuration" button in the ServerConfigScreen doesn't update the IP address or port when clicked.

### **Root Causes**

#### **1. localStorage Not Available**
ReactLynx may not have access to localStorage in some environments.

**Symptoms:**
- Console shows "localStorage not available" warnings
- Configuration appears to save but doesn't persist
- Values reset after page reload

**Solution:**
- Check if localStorage is available in your environment
- Use the ConfigTestScreen (⚡ tab) to test storage functionality
- Look for console warnings about localStorage

#### **2. State Not Updating**
The component state isn't being updated after saving.

**Symptoms:**
- Configuration saves but input fields don't update
- Current configuration display shows old values
- Console shows successful save but UI doesn't reflect changes

**Solution:**
- Check that `setHost()` and `setPort()` are called after successful save
- Verify that `setCurrentConfig()` is called with new values
- Look for console logs showing the new configuration

#### **3. RobotAPI Instance Issues**
Multiple instances of RobotAPI might be created.

**Symptoms:**
- Configuration appears to save but doesn't affect other components
- Different screens show different configurations
- Changes don't persist across navigation

**Solution:**
- Ensure RobotAPI is imported as a singleton
- Check that all components use the same RobotAPI instance
- Verify that configuration changes are reflected in all components

### **Debugging Steps**

#### **Step 1: Check Console Logs**
Look for these console messages:

```javascript
// Should see these when saving:
setServerConfig called with: { host: "10.136.166.163", port: "8080" }
Setting robotAPI_host: 10.136.166.163
Setting robotAPI_port: 8080
Verified robotAPI_host: 10.136.166.163
Verified robotAPI_port: 8080
Robot API configuration updated: http://10.136.166.163:8080/api
Storage save results: { hostSaved: true, portSaved: true }
Current config after update: { host: "10.136.166.163", port: "8080", baseURL: "http://10.136.166.163:8080/api" }
```

#### **Step 2: Use ConfigTestScreen**
Navigate to the ⚡ tab to test configuration functionality:

1. **Check Current Configuration**
   - Verify the displayed values match what you expect
   - Look for any discrepancies

2. **Test Save Function**
   - Enter new host and port values
   - Click "💾 Save"
   - Check if the current configuration updates
   - Look for success/error messages

3. **Test Reset Function**
   - Click "🔄 Reset"
   - Verify values return to defaults
   - Check if localStorage is cleared

4. **Test Reload Function**
   - Click "🔄 Reload"
   - Verify values are loaded from storage
   - Check if they match what was saved

#### **Step 3: Check localStorage Directly**
Open browser developer tools and check localStorage:

```javascript
// In browser console:
localStorage.getItem('robotAPI_host')
localStorage.getItem('robotAPI_port')
```

#### **Step 4: Verify Component Updates**
Check that the ServerConfigScreen updates correctly:

1. **Input Fields**
   - Should update to show saved values
   - Should reflect current configuration

2. **Current Configuration Display**
   - Should show the actual saved values
   - Should update immediately after save

3. **Status Message**
   - Should show "Configuration saved successfully"
   - Should show the new URL

### **Common Solutions**

#### **Solution 1: Fix State Updates**
Ensure the component updates its state after saving:

```javascript
const saveConfiguration = () => {
  const success = robotAPI.setServerConfig(host, port)
  if (success) {
    const newConfig = robotAPI.getServerConfig()
    setCurrentConfig(newConfig)
    // Update input fields with saved values
    setHost(newConfig.host)
    setPort(newConfig.port)
    setConnectionStatus('Configuration saved successfully')
  }
}
```

#### **Solution 2: Add Error Handling**
Add better error handling and user feedback:

```javascript
const saveConfiguration = () => {
  try {
    const success = robotAPI.setServerConfig(host, port)
    if (success) {
      // Update state
      const newConfig = robotAPI.getServerConfig()
      setCurrentConfig(newConfig)
      setHost(newConfig.host)
      setPort(newConfig.port)
      setConnectionStatus('Configuration saved successfully')
    } else {
      setConnectionStatus('Failed to save configuration')
    }
  } catch (error) {
    console.error('Save configuration error:', error)
    setConnectionStatus('Error saving configuration')
  }
}
```

#### **Solution 3: Verify localStorage**
Add localStorage verification:

```javascript
// Test localStorage availability
const testLocalStorage = () => {
  try {
    localStorage.setItem('test', 'test')
    const result = localStorage.getItem('test')
    localStorage.removeItem('test')
    return result === 'test'
  } catch (error) {
    console.warn('localStorage not available:', error)
    return false
  }
}
```

### **Testing Checklist**

- [ ] ConfigTestScreen (⚡ tab) loads current configuration
- [ ] Save button updates configuration
- [ ] Reset button restores defaults
- [ ] Reload button loads from storage
- [ ] Console shows detailed logging
- [ ] localStorage contains correct values
- [ ] ServerConfigScreen (🔧 tab) shows updated values
- [ ] Other components reflect configuration changes

### **Environment-Specific Issues**

#### **ReactLynx Environment**
- localStorage may not be available
- Use in-memory storage as fallback
- Test with ConfigTestScreen

#### **Browser Environment**
- localStorage should work normally
- Check for browser restrictions
- Verify storage permissions

#### **Mobile Environment**
- localStorage may have limitations
- Check for storage quotas
- Test persistence across app restarts

### **Quick Fix Commands**

If you need to reset the configuration manually:

```javascript
// In browser console:
localStorage.removeItem('robotAPI_host')
localStorage.removeItem('robotAPI_port')
// Then reload the page
```

### **Contact Support**

If the issue persists after trying these solutions:

1. **Collect Debug Information**
   - Console logs
   - localStorage contents
   - Current configuration values
   - Steps to reproduce

2. **Test with ConfigTestScreen**
   - Use the ⚡ tab for isolated testing
   - Document any error messages
   - Note which functions work/don't work

3. **Environment Details**
   - ReactLynx version
   - Browser/device information
   - Any error messages
