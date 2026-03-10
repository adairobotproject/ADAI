/**
 * Test script for mobile progress bar functionality
 * This script tests the integration between the mobile app and the robot GUI progress system
 */

import robotAPI from './src/services/RobotAPI.js'

async function testProgressSystem() {
  console.log('🧪 Testing Mobile Progress Bar System...\n')

  // Test 1: Connection to robot
  console.log('1. Testing connection to robot...')
  const connectionTest = await robotAPI.testConnection()
  if (connectionTest.success) {
    console.log('✅ Connection successful')
    console.log(`   Server: ${connectionTest.config.baseURL}`)
  } else {
    console.log('❌ Connection failed:', connectionTest.message)
    return
  }

  // Test 2: Get available classes
  console.log('\n2. Testing class retrieval...')
  const classesResult = await robotAPI.getAvailableClasses()
  if (classesResult.success && classesResult.data.classes) {
    console.log(`✅ Found ${classesResult.data.classes.length} classes`)
    classesResult.data.classes.forEach((cls, index) => {
      console.log(`   ${index + 1}. ${cls.title} (${cls.name})`)
    })
  } else {
    console.log('❌ Failed to retrieve classes:', classesResult.error)
    return
  }

  // Test 3: Get class progress (should be inactive initially)
  console.log('\n3. Testing progress retrieval (inactive state)...')
  const progressResult = await robotAPI.getClassProgress()
  if (progressResult.success) {
    const progress = progressResult.data
    console.log('✅ Progress API working')
    console.log(`   Active: ${progress.is_active}`)
    console.log(`   Class: ${progress.class_name || 'None'}`)
    console.log(`   Phase: ${progress.phase}`)
    console.log(`   Percentage: ${progress.progress_percentage}%`)
    console.log(`   Status: ${progress.status}`)
  } else {
    console.log('❌ Failed to get progress:', progressResult.error)
  }

  // Test 4: Start a test class (if available)
  if (classesResult.data.classes.length > 0) {
    const testClass = classesResult.data.classes[0]
    console.log(`\n4. Testing class execution with: ${testClass.name}`)
    
    try {
      const startResult = await robotAPI.startClass(testClass.name)
      if (startResult.success) {
        console.log('✅ Class started successfully')
        
        // Wait a moment and check progress
        console.log('\n5. Testing progress during execution...')
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        const activeProgress = await robotAPI.getClassProgress()
        if (activeProgress.success) {
          const progress = activeProgress.data
          console.log('✅ Active progress retrieved')
          console.log(`   Active: ${progress.is_active}`)
          console.log(`   Class: ${progress.class_name}`)
          console.log(`   Phase: ${progress.phase}`)
          console.log(`   Percentage: ${progress.progress_percentage}%`)
          console.log(`   Elapsed: ${progress.elapsed_time}`)
          console.log(`   Status: ${progress.status}`)
          
          // Stop the class
          console.log('\n6. Stopping test class...')
          const stopResult = await robotAPI.stopClass()
          if (stopResult.success) {
            console.log('✅ Class stopped successfully')
          } else {
            console.log('❌ Failed to stop class:', stopResult.error)
          }
        } else {
          console.log('❌ Failed to get active progress:', activeProgress.error)
        }
      } else {
        console.log('❌ Failed to start class:', startResult.error)
      }
    } catch (error) {
      console.log('❌ Error during class execution test:', error.message)
    }
  }

  // Test 5: Test progress API response format
  console.log('\n7. Testing progress API response format...')
  const formatTest = await robotAPI.getClassProgress()
  if (formatTest.success) {
    const progress = formatTest.data
    const requiredFields = [
      'class_name', 'phase', 'progress_percentage', 'elapsed_time', 
      'remaining_time', 'current_phase', 'phase_emoji', 'is_active', 'status'
    ]
    
    const missingFields = requiredFields.filter(field => !(field in progress))
    if (missingFields.length === 0) {
      console.log('✅ All required progress fields present')
      console.log('   Response format is correct for mobile app')
    } else {
      console.log('❌ Missing required fields:', missingFields)
    }
  }

  console.log('\n🎉 Mobile Progress Bar System Test Complete!')
  console.log('\n📱 Next steps:')
  console.log('   1. Start the mobile app: npm start')
  console.log('   2. Navigate to Classes screen')
  console.log('   3. Start a class to see the progress bar in action')
  console.log('   4. The progress bar should update every 2 seconds')
  console.log('   5. Check that colors change based on progress percentage')
}

// Run the test
testProgressSystem().catch(console.error)
