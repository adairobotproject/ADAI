import { useState, useCallback } from '@lynx-js/react'

export function ContactScreen() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')

  const handleSubmit = useCallback(() => {
    'background only'
    // Aquí se procesaría el envío del formulario
    console.log('Formulario enviado:', { name, email, message })
    alert('¡Mensaje enviado con éxito!')
    setName('')
    setEmail('')
    setMessage('')
  }, [name, email, message])

  return (
    <view className="screen">
      <view className="contact-content">
        <text className="contact-title">Contacto</text>
        
        <view className="contact-info">
          <text className="contact-subtitle">Información de contacto:</text>
          <text className="contact-item">📧 Email: info@reactlynx.com</text>
          <text className="contact-item">📱 Teléfono: +1 (555) 123-4567</text>
          <text className="contact-item">📍 Dirección: Calle Principal 123</text>
        </view>
        
        <view className="contact-form">
          <text className="form-title">Envíanos un mensaje:</text>
          
          <view className="form-group">
            <text className="form-label">Nombre:</text>
            <input 
              className="form-input"
              value={name}
              onInput={(e) => setName(e.target.value)}
              placeholder="Tu nombre"
            />
          </view>
          
          <view className="form-group">
            <text className="form-label">Email:</text>
            <input 
              className="form-input"
              value={email}
              onInput={(e) => setEmail(e.target.value)}
              placeholder="tu@email.com"
            />
          </view>
          
          <view className="form-group">
            <text className="form-label">Mensaje:</text>
            <textarea 
              className="form-textarea"
              value={message}
              onInput={(e) => setMessage(e.target.value)}
              placeholder="Escribe tu mensaje aquí..."
            />
          </view>
          
          <view className="form-button" bindtap={handleSubmit}>
            <text className="button-text">Enviar Mensaje</text>
          </view>
        </view>
      </view>
    </view>
  )
} 