import { useEffect, useState } from '@lynx-js/react'
import { Navbar } from './components/Navbar'
import { HomeScreen } from './components/HomeScreen'
import { DashboardScreen } from './components/DashboardScreen'
import { ClassesScreen } from './components/ClassesScreen'
import { ConnectionsScreen } from './components/ConnectionsScreen'
import { ControlScreen } from './components/ControlScreen'
import { RobotControlScreen } from './components/RobotControlScreen'
import { ManualConfigScreen } from './components/ManualConfigScreen'
import { ConfigDebugScreen } from './components/ConfigDebugScreen'
import { TeacherControlScreen } from './components/TeacherControlScreen'
import { GlobalStateProvider } from './services/GlobalStateProvider'

import './App.css'

export function App(props) {
  const [currentRoute, setCurrentRoute] = useState('home')

  useEffect(() => {
    console.info('Hello, ReactLynx')
    props.onMounted?.()
  }, [])

  const handleRouteChange = (route) => {
    setCurrentRoute(route)
  }

  const renderScreen = () => {
    switch (currentRoute) {
      case 'home':
        return <HomeScreen />
      case 'dashboard':
        return <DashboardScreen />
      case 'classes':
        return <ClassesScreen />
      case 'connections':
        return <ConnectionsScreen />
      case 'control':
        return <ControlScreen />
      case 'robotcontrol':
        return <RobotControlScreen />
      case 'manualconfig':
        return <ManualConfigScreen />
      case 'debug':
        return <ConfigDebugScreen />
      case 'teacher':
        return <TeacherControlScreen />
      default:
        return <HomeScreen />
    }
  }

  return (
    <GlobalStateProvider>
      <view>
        <view className='Background' />
        <view className='App'>
          <scroll-view className='MainContent' scroll-orientation='vertical'>
            {renderScreen()}
          </scroll-view>
          <Navbar activeRoute={currentRoute} onRouteChange={handleRouteChange} />
        </view>
      </view>
    </GlobalStateProvider>
  )
}
