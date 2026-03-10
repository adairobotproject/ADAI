import { useCallback } from '@lynx-js/react'

export function Navbar({ activeRoute, onRouteChange }) {
  const handleRouteChange = useCallback((route) => {
    onRouteChange?.(route)
  }, [onRouteChange])

  return (
    <view className="footer-nav">
      <view 
        className={`footer-nav-item ${activeRoute === 'home' ? 'active' : ''}`}
        bindtap={() => handleRouteChange('home')}
      >
        <text className="nav-icon">⌂</text>
      </view>
      
      <view 
        className={`footer-nav-item ${activeRoute === 'dashboard' ? 'active' : ''}`}
        bindtap={() => handleRouteChange('dashboard')}
      >
        <text className="nav-icon">☰</text>
      </view>
      
      <view 
        className={`footer-nav-item ${activeRoute === 'control' ? 'active' : ''}`}
        bindtap={() => handleRouteChange('control')}
      >
        <text className="nav-icon">●</text>
      </view>
      
      <view 
        className={`footer-nav-item ${activeRoute === 'robotcontrol' ? 'active' : ''}`}
        bindtap={() => handleRouteChange('robotcontrol')}
      >
        <text className="nav-icon">🤖</text>
      </view>
      
      <view 
        className={`footer-nav-item ${activeRoute === 'classes' ? 'active' : ''}`}
        bindtap={() => handleRouteChange('classes')}
      >
        <text className="nav-icon">★</text>
      </view>
      
      <view 
        className={`footer-nav-item ${activeRoute === 'connections' ? 'active' : ''}`}
        bindtap={() => handleRouteChange('connections')}
      >
        <text className="nav-icon">⚙</text>
      </view>
      
      <view 
        className={`footer-nav-item ${activeRoute === 'teacher' ? 'active' : ''}`}
        bindtap={() => handleRouteChange('teacher')}
      >
        <text className="nav-icon">🎓</text>
      </view>
      
      <view 
        className={`footer-nav-item ${activeRoute === 'manualconfig' ? 'active' : ''}`}
        bindtap={() => handleRouteChange('manualconfig')}
      >
        <text className="nav-icon">🛠️</text>
      </view>
      
      <view 
        className={`footer-nav-item ${activeRoute === 'debug' ? 'active' : ''}`}
        bindtap={() => handleRouteChange('debug')}
      >
        <text className="nav-icon">🐛</text>
      </view>
    </view>
  )
} 