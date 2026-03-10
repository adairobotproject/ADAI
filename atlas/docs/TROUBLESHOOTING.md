# 🛠️ Troubleshooting Guide - Robot Atlas Mobile App

## Common Errors and Solutions

### ❌ "Load card failed type error"

This error typically occurs when there are issues with component imports or ReactLynx syntax compatibility.

#### **Solution 1: Check Component Imports**

Make sure all components are using the correct ReactLynx syntax:

```javascript
// ✅ Correct - ReactLynx
import { useState, useEffect } from '@lynx-js/react'

// ❌ Incorrect - Standard React
import React, { useState, useEffect } from 'react'
```

#### **Solution 2: Component Export Format**

Ensure components are exported correctly:

```javascript
// ✅ Correct - Named export
export function ComponentName() {
  // component code
}

// ❌ Incorrect - Default export
export default function ComponentName() {
  // component code
}
```

#### **Solution 3: JSX Elements**

Use ReactLynx elements instead of HTML:

```javascript
// ✅ Correct - ReactLynx
<view className="container">
  <text className="title">Hello</text>
</view>

// ❌ Incorrect - HTML
<div className="container">
  <h1 className="title">Hello</h1>
</div>
```

#### **Solution 4: Event Handlers**

Use ReactLynx event syntax:

```javascript
// ✅ Correct - ReactLynx
<view bindtap={handleClick}>
  <text>Click me</text>
</view>

// ❌ Incorrect - Standard React
<button onClick={handleClick}>
  Click me
</button>
```

### 🔧 **Quick Fix Steps**

1. **Restart the Development Server**
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart
   npm run dev
   ```

2. **Clear Browser Cache**
   - Clear the LynxExplorer app cache
   - Restart the LynxExplorer app

3. **Check Console Logs**
   - Open browser developer tools
   - Check for specific error messages
   - Look for import/export issues

4. **Verify File Structure**
   ```
   src/
   ├── components/
   │   ├── ServerConfigScreen.jsx  ✅
   │   ├── ControlScreen.jsx       ✅
   │   └── ...
   ├── services/
   │   └── RobotAPI.js             ✅
   └── App.jsx                     ✅
   ```

### 🚨 **Other Common Issues**

#### **"Cannot read property of undefined"**

This usually means a component is trying to access a property that doesn't exist.

**Solution:**
- Add null checks
- Use optional chaining (`?.`)
- Provide default values

```javascript
// ✅ Safe access
const value = data?.property || 'default'

// ❌ Unsafe access
const value = data.property
```

#### **"localStorage is not defined"**

This occurs when localStorage is not available in the environment.

**Solution:**
- The RobotAPI now handles this automatically
- Configuration will fall back to defaults
- Check if you're in a supported environment

#### **"Network request failed"**

This happens when the app can't connect to the robot server.

**Solution:**
1. Verify `robot_gui.py` is running
2. Check the IP address and port
3. Ensure both devices are on the same network
4. Test with `localhost` first

### 📱 **ReactLynx Specific Issues**

#### **Component Not Rendering**

Check for these common issues:

1. **Missing export**
   ```javascript
   // ✅ Make sure to export
   export function MyComponent() {
     return <view>Content</view>
   }
   ```

2. **Incorrect import**
   ```javascript
   // ✅ Use named import
   import { MyComponent } from './components/MyComponent'
   
   // ❌ Don't use default import
   import MyComponent from './components/MyComponent'
   ```

3. **Wrong JSX syntax**
   ```javascript
   // ✅ Use ReactLynx elements
   <view className="container">
     <text>Hello World</text>
   </view>
   ```

#### **State Not Updating**

Ensure you're using ReactLynx hooks correctly:

```javascript
// ✅ Correct usage
const [value, setValue] = useState('')

// ✅ Update state
setValue('new value')

// ❌ Don't mutate directly
value = 'new value' // This won't trigger re-render
```

### 🔍 **Debugging Steps**

1. **Check the Console**
   - Open browser developer tools
   - Look for error messages
   - Check for warnings

2. **Verify Imports**
   - Ensure all imports are correct
   - Check file paths
   - Verify export/import syntax

3. **Test Components Individually**
   - Comment out other components
   - Test one component at a time
   - Identify which component causes the issue

4. **Check ReactLynx Version**
   - Ensure you're using a compatible version
   - Check for updates
   - Review breaking changes

### 📞 **Getting Help**

If you're still experiencing issues:

1. **Check the Console Logs**
   - Copy the exact error message
   - Note the line number and file

2. **Verify Your Setup**
   - Node.js version
   - ReactLynx version
   - Dependencies

3. **Test with Minimal Code**
   - Create a simple test component
   - Verify basic functionality
   - Add complexity gradually

### 🎯 **Prevention Tips**

1. **Use Consistent Syntax**
   - Stick to ReactLynx patterns
   - Avoid mixing React and ReactLynx syntax

2. **Test Regularly**
   - Test after each major change
   - Use the development server
   - Check on actual devices

3. **Keep Dependencies Updated**
   - Update ReactLynx regularly
   - Check for breaking changes
   - Review migration guides

4. **Use Type Checking**
   - Consider using TypeScript
   - Add PropTypes for validation
   - Use default values

---

**💡 Remember:** Most "load card failed type error" issues are related to syntax compatibility between React and ReactLynx. Always use ReactLynx-specific syntax and patterns.

### ❌ "Buttons not working / Los botones no funcionan"

This is a common issue in ReactLynx applications where buttons don't respond to clicks.

#### **Solution 1: Use Correct Event Syntax**

ReactLynx uses `bindtap` instead of `onClick`:

```javascript
// ✅ Correct - ReactLynx
<view className="button" bindtap={handleClick}>
  <text>Click me</text>
</view>

// ❌ Incorrect - Standard React
<button onClick={handleClick}>
  Click me
</button>
```

#### **Solution 2: Check Function Definitions**

Make sure your functions are defined correctly:

```javascript
// ✅ Correct - Simple function
const handleClick = () => {
  console.log('Button clicked!')
  // Your logic here
}

// ✅ Correct - With parameters
const handleClick = (param) => {
  console.log('Button clicked with:', param)
}

// ❌ Incorrect - Async without proper handling
const handleClick = async () => {
  // This might cause issues in ReactLynx
}
```

#### **Solution 3: Add Debugging**

Add console logs to verify the function is being called:

```javascript
const handleClick = () => {
  console.log('Button clicked!')
  alert('Button works!') // This will show if the function is called
}
```

#### **Solution 4: Check CSS Styles**

Ensure buttons have proper styling:

```css
.button {
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
}

.button:active {
  transform: scale(0.98);
  opacity: 0.8;
}
```

#### **Solution 5: Verify Component Structure**

Make sure your component structure is correct:

```javascript
// ✅ Correct structure
export function MyComponent() {
  const handleClick = () => {
    console.log('Clicked!')
  }

  return (
    <view className="container">
      <view className="button" bindtap={handleClick}>
        <text>Click me</text>
      </view>
    </view>
  )
}
```

### 🔧 **Quick Fix Steps for Buttons**

1. **Check Event Syntax**
   - Use `bindtap` instead of `onClick`
   - Verify function names are correct

2. **Add Console Logs**
   ```javascript
   const handleClick = () => {
     console.log('Button clicked!')
     // Your logic here
   }
   ```

3. **Test with Simple Function**
   ```javascript
   <view bindtap={() => alert('Test')}>
     <text>Test Button</text>
   </view>
   ```

4. **Check Browser Console**
   - Open developer tools
   - Look for error messages
   - Check if console logs appear

5. **Verify CSS**
   - Ensure buttons have `cursor: pointer`
   - Check for overlapping elements
   - Verify z-index values

### 🚨 **Common Button Issues**

#### **"Function not defined"**

This happens when the function isn't properly defined or imported.

**Solution:**
- Define the function in the same component
- Check for typos in function names
- Ensure proper scope

#### **"Event not firing"**

The button doesn't respond to clicks.

**Solution:**
- Use `bindtap` instead of `onClick`
- Check for CSS issues (z-index, pointer-events)
- Verify the element is clickable

#### **"Async function issues"**

Async functions might not work properly in ReactLynx.

**Solution:**
- Use simple synchronous functions when possible
- Handle async operations carefully
- Add proper error handling

#### **"State not updating"**

Button click works but state doesn't change.

**Solution:**
- Use ReactLynx hooks correctly
- Check for state update logic
- Verify component re-renders

### ❌ "Async/Await Errors"

ReactLynx may have issues with async/await functions.

#### **Solution 1: Use Synchronous Functions**

Replace async functions with synchronous ones:

```javascript
// ✅ Correct - Synchronous
const handleClick = () => {
  console.log('Button clicked!')
  // Your logic here
}

// ❌ Incorrect - Async
const handleClick = async () => {
  // This might cause issues in ReactLynx
}
```

#### **Solution 2: Use setTimeout for Async Operations**

If you need async-like behavior:

```javascript
const handleAsyncOperation = () => {
  console.log('Starting operation...')
  
  setTimeout(() => {
    console.log('Operation completed!')
    // Update state here
  }, 1000)
}
```

#### **Solution 3: Simplify API Calls**

For API calls, use simple functions:

```javascript
// ✅ Correct - Simple API call
const testConnection = () => {
  const result = robotAPI.testConnection()
  return result.success
}

// ❌ Incorrect - Async API call
const testConnection = async () => {
  const result = await robotAPI.testConnection()
  return result.success
}
```

### 🔧 **Quick Fix Steps for Async Errors**

1. **Remove async/await**
   - Convert async functions to regular functions
   - Use setTimeout for delayed operations

2. **Simplify API calls**
   - Make API functions synchronous
   - Return simple objects instead of promises

3. **Use setTimeout**
   - For operations that need delay
   - For simulating async behavior

4. **Test with simple functions**
   - Start with basic synchronous functions
   - Add complexity gradually

### 🚨 **Common Async Issues**

#### **"Function is not defined"**

This happens when async functions aren't properly handled.

**Solution:**
- Convert to synchronous functions
- Use setTimeout for delays
- Simplify the logic

#### **"Promise not handled"**

Async functions return promises that ReactLynx can't handle.

**Solution:**
- Remove async/await
- Use synchronous functions
- Handle results directly

#### **"State not updating"**

Async state updates might not work properly.

**Solution:**
- Use synchronous state updates
- Use setTimeout for delayed updates
- Test with simple state changes

### 🎯 **Best Practices for ReactLynx**

1. **Keep Functions Simple**
   - Use synchronous functions when possible
   - Avoid complex async operations
   - Test thoroughly

2. **Use setTimeout for Delays**
   ```javascript
   const delayedOperation = () => {
     setTimeout(() => {
       // Your delayed logic here
     }, 1000)
   }
   ```

3. **Simplify API Calls**
   ```javascript
   const apiCall = () => {
     // Simple synchronous API call
     return { success: true, data: {} }
   }
   ```

4. **Test Components Individually**
   - Create simple test components
   - Verify basic functionality
   - Add features gradually

### ❌ "CSS Parse Error: user-select is not supported"

ReactLynx has limited CSS support and doesn't support certain CSS properties.

#### **Solution 1: Remove Unsupported CSS Properties**

Remove these unsupported properties from your CSS:

```css
/* ❌ Not supported in ReactLynx */
user-select: none;
-webkit-user-select: none;
-moz-user-select: none;
-ms-user-select: none;
```

#### **Solution 2: Simplify Transforms and Animations**

Replace complex transforms with simpler alternatives:

```css
/* ❌ Complex transforms */
transform: translateY(-2px);
transform: scale(1.05);
transform: rotate(360deg);

/* ✅ Simple alternatives */
opacity: 0.8;
background-color: rgba(255, 255, 255, 0.1);
```

#### **Solution 3: Remove Keyframe Animations**

Remove or simplify CSS animations:

```css
/* ❌ Complex animations */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ✅ Simple alternatives */
.opacity-animation {
  opacity: 0.8;
}
```

### 🔧 **Quick Fix Steps for CSS Errors**

1. **Remove user-select**
   - Search for `user-select` in CSS files
   - Remove all instances
   - Use alternative styling if needed

2. **Simplify transforms**
   - Replace `transform: translateY()` with `opacity`
   - Replace `transform: scale()` with `opacity`
   - Remove `transform: rotate()` animations

3. **Remove keyframe animations**
   - Remove `@keyframes` definitions
   - Remove `animation` properties
   - Use simple CSS properties instead

4. **Test with simple styles**
   - Use inline styles for testing
   - Gradually add CSS classes
   - Test each component individually

### 🚨 **Common CSS Issues**

#### **"Property not supported"**

ReactLynx doesn't support all CSS properties.

**Solution:**
- Use only basic CSS properties
- Test with simple styles first
- Check ReactLynx documentation

#### **"Animation not working"**

CSS animations may not work properly.

**Solution:**
- Remove keyframe animations
- Use simple transitions
- Use JavaScript for animations

#### **"Transform not working"**

Transform properties may cause issues.

**Solution:**
- Replace transforms with opacity
- Use background-color changes
- Use simple positioning

### 🎯 **CSS Best Practices for ReactLynx**

1. **Use Simple Properties**
   ```css
   /* ✅ Good */
   .button {
     background-color: #3b82f6;
     border-radius: 8px;
     padding: 12px;
     opacity: 0.8;
   }
   ```

2. **Avoid Complex Transforms**
   ```css
   /* ❌ Avoid */
   .button:hover {
     transform: translateY(-2px) scale(1.05);
   }
   
   /* ✅ Use instead */
   .button:hover {
     opacity: 0.8;
     background-color: rgba(59, 130, 246, 0.8);
   }
   ```

3. **Use Inline Styles for Testing**
   ```javascript
   <view style={{ 
     padding: '20px', 
     backgroundColor: '#3b82f6',
     borderRadius: '8px'
   }}>
   ```

4. **Test Components Individually**
   - Create simple test components
   - Add styles gradually
   - Verify each addition works
