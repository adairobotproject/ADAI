# 📱 Mobile App Tab - Guía de Uso

## Descripción

La nueva tab **📱 Mobile App** en el `robot_gui.py` proporciona una interfaz completa para gestionar y monitorear la conexión con la aplicación móvil ReactLynx. Esta tab centraliza todo el control del servidor API y las estadísticas de uso.

## 🖥️ Funcionalidades de la Tab

### Panel Izquierdo: Configuración del Servidor API

#### 🟢 Estado del Servidor
- **Indicador Visual**: Círculo verde (ejecutándose) o rojo (detenido)
- **Estado de Texto**: "Ejecutándose" o "Detenido"
- **Actualización en Tiempo Real**: Se actualiza automáticamente cada 5 segundos

#### ⚙️ Configuración del Puerto
- **Campo de Puerto**: Permite cambiar el puerto del servidor API
- **Botón "Aplicar"**: Aplica el nuevo puerto y reinicia el servidor
- **URL del Servidor**: Muestra la URL completa del API (`http://localhost:PUERTO/api`)

#### 🎛️ Controles del Servidor
- **🟢 Iniciar Servidor**: Inicia el servidor API manualmente
- **🔴 Detener Servidor**: Detiene el servidor API
- **🔄 Reiniciar**: Reinicia el servidor (útil para aplicar cambios)

#### 📝 Registro de Conexiones
- **Log en Tiempo Real**: Muestra todas las peticiones entrantes
- **Timestamping**: Cada entrada incluye hora exacta
- **Auto-scroll**: Se desplaza automáticamente a las nuevas entradas
- **Limitación**: Mantiene las últimas 1000 líneas para optimizar memoria

### Panel Derecho: Dispositivos y Estadísticas

#### 📱 Dispositivos Móviles Conectados
- **Lista de IPs**: Muestra las direcciones IP de dispositivos conectados
- **Timestamp**: Hora de última conexión de cada dispositivo
- **Actualización Automática**: Se actualiza cuando llegan nuevas conexiones

#### 📊 Estadísticas de la API
- **Total Requests**: Número total de peticiones recibidas
- **Successful**: Peticiones exitosas
- **Failed**: Peticiones fallidas
- **Active Connections**: Conexiones activas actuales
- **Uptime (min)**: Tiempo que el servidor ha estado ejecutándose

#### 🔗 Estado de Endpoints
- **Lista Completa**: Todos los endpoints disponibles
- **Descripción**: Función de cada endpoint
- **Métodos HTTP**: GET/POST claramente identificados

## 🚀 Cómo Usar la Tab

### 1. Inicio Automático
El servidor se inicia automáticamente cuando abres `robot_gui.py`. La tab muestra el estado actual inmediatamente.

### 2. Cambiar Puerto
```
1. Modificar el valor en "Puerto del Servidor"
2. Hacer clic en "Aplicar"
3. El servidor se reinicia automáticamente en el nuevo puerto
4. Actualizar la URL en la app móvil si es necesario
```

### 3. Monitoreo en Tiempo Real
```
- Estado del servidor: Indicador visual verde/rojo
- Peticiones entrantes: Aparecen en el log en tiempo real
- Estadísticas: Se actualizan automáticamente cada 5 segundos
- Dispositivos: Se añaden automáticamente cuando se conectan
```

### 4. Control Manual del Servidor
```
- Detener: Útil para mantenimiento o cambios
- Iniciar: Reanudar después de detener
- Reiniciar: Aplicar cambios o resolver problemas de conexión
```

## 📋 Endpoints Disponibles

### GET Endpoints (Consulta de Estado)
| Endpoint | Descripción |
|----------|-------------|
| `/api/status` | Estado general del robot |
| `/api/position` | Posición actual de todas las partes |
| `/api/classes` | Clases educativas disponibles |
| `/api/connection` | Estado de conexiones del sistema |
| `/api/presets` | Presets de movimiento disponibles |

### POST Endpoints (Comandos de Control)
| Endpoint | Descripción |
|----------|-------------|
| `/api/robot/move` | Mover partes del robot |
| `/api/robot/speak` | Hacer hablar al robot |
| `/api/class/start` | Iniciar clase educativa |
| `/api/class/stop` | Detener clase en progreso |
| `/api/preset/execute` | Ejecutar preset de movimiento |
| `/api/robot/emergency` | Parada de emergencia |

## 🔍 Interpretación de Logs

### Formato de Logs
```
[HH:MM:SS] MÉTODO /endpoint - IP_CLIENTE
[HH:MM:SS] ERROR MÉTODO /endpoint: descripción_error
[HH:MM:SS] Servidor iniciado en puerto XXXX
```

### Ejemplos de Logs
```
[14:30:25] GET /api/status - 10.136.166.163
[14:30:26] POST /api/robot/move - 10.136.166.163
[14:30:27] ERROR POST /api/class/start: Class not found
[14:31:00] Servidor reiniciado exitosamente
```

## 📈 Interpretación de Estadísticas

### Métricas Importantes
- **Ratio Éxito/Fallo**: `Successful / Total Requests`
- **Uptime**: Estabilidad del servidor
- **Active Connections**: Dispositivos móviles usando la app
- **Failed Requests**: Indicador de problemas potenciales

### Resolución de Problemas

#### Servidor No Inicia
```
1. Verificar que el puerto no esté en uso
2. Comprobar permisos de firewall
3. Revisar logs para errores específicos
4. Intentar cambiar a otro puerto
```

#### Muchas Peticiones Fallidas
```
1. Verificar conexión de red
2. Comprobar que la app móvil use la URL correcta
3. Revisar logs para tipos de errores
4. Reiniciar el servidor si es necesario
```

#### Dispositivos No Aparecen
```
1. Verificar que la app móvil esté haciendo peticiones
2. Comprobar que ambos dispositivos estén en la misma red
3. Verificar configuración de firewall
4. Revisar la URL en RobotAPI.js
```

## 🔧 Configuración Avanzada

### Cambio de IP del Servidor
Para acceso desde red local, editar en `robot_gui.py`:
```python
# En el método start_api_server()
self.api_server = MobileAPIServer(self, host='0.0.0.0', port=self.api_port)
```

### Configuración de CORS
El servidor ya incluye headers CORS para permitir acceso desde cualquier origen.

### Logging Personalizado
Los logs se pueden extender modificando el método `log_mobile_message()` en `robot_gui.py`.

## 🔒 Seguridad

### Consideraciones
- El servidor acepta conexiones de cualquier IP
- No hay autenticación implementada
- Ideal para uso en red local cerrada
- Para producción, considerar añadir autenticación

### Recomendaciones
- Usar solo en redes confiables
- Monitorear regularmente las IPs conectadas
- Cambiar puerto por defecto si es necesario
- Limitar acceso por firewall si se requiere

## 🎯 Próximas Mejoras

- [ ] Autenticación de dispositivos
- [ ] WebSocket para notificaciones en tiempo real
- [ ] Exportación de estadísticas
- [ ] Filtros de log por tipo de petición
- [ ] Alertas de seguridad
- [ ] Dashboard de métricas avanzadas
