import { useCallback, useState } from '@lynx-js/react'
import arrow from '../assets/arrow.png'
import lynxLogo from '../assets/lynx-logo.png'
import reactLynxLogo from '../assets/react-logo.png'

export function HomeScreen() {
  const [alterLogo, setAlterLogo] = useState(false)

  const onTap = useCallback(() => {
    'background only'
    setAlterLogo(prevAlterLogo => !prevAlterLogo)
  }, [])

  return (
    <view className="screen home-screen">
      <view className='Banner'>
        <view className='Logo' bindtap={onTap}>
          {alterLogo
            ? <image src={reactLynxLogo} className='Logo--react' />
            : <image src={lynxLogo} className='Logo--lynx' />}
        </view>
        <text className='Title'>Robot Educativo Unitec</text>
        <text className='Subtitle'>Inmoov</text>
      </view>
      <view className='Content'>
        <view className="inmoov-logo">
          <text className="inmoov-text">🤖</text>
        </view>
        <image src={arrow} className='Arrow' />
        <text className='Description'>¡Controla el robot Inmoov desde tu dispositivo!</text>
        <text className='Hint'>
          Usa el panel de<text
            style={{
              fontStyle: 'italic',
              color: 'rgba(255, 255, 255, 0.85)',
            }}
          >
            {' Control '}
          </text>
          para mover el robot
        </text>
      </view>
    </view>
  )
} 