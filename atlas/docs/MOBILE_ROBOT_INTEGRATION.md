# 🤖 Robot Atlas - Integración Móvil

## Descripción General

Esta aplicación móvil ReactLynx se conecta directamente con el `robot_gui.py` para controlar el robot InMoov a través de una API HTTP. La aplicación permite:

- **Control en tiempo real** del robot (cabeza, brazos, manos)
- **Ejecución de clases programadas** con movimientos y habla sincronizados
- **Presets de movimiento** predefinidos (saludo, aplauso, etc.)
- **Monitoreo de estado** del robot y conexiones
- **Parada de emergencia** remota

## 🚀 Configuración e Inicio

### 1. Iniciar el Robot GUI
```bash
cd ia-clases
python robot_gui.py
```

El servidor API se iniciará automáticamente en `localhost:8080`

### 2. Iniciar la App Móvil
```bash
cd atlas
npm install  # Solo la primera vez
npm run dev
```

### 3. Configuración de Red (Opcional)
Para usar desde un dispositivo móvil real, actualiza la URL en `src/services/RobotAPI.js`:
```javascript
const API_BASE_URL = 'http://[IP_DE_TU_PC]:8080/api';
```

## 📱 Funcionalidades de la App

### 🎮 Control Screen
- **Estado del Robot**: Batería, temperatura, conexión
- **Control de Cabeza**: Rotación X, Y, Z
- **Control de Brazos**: Hombro, codo, muñeca (izquierdo/derecho)
- **Control de Manos**: Dedos individuales
- **Presets**: Movimientos predefinidos
- **Emergencia**: Parada inmediata de todos los movimientos

### 🎓 Classes Screen
- **Clases Programadas**: Lista de clases educativas disponibles
- **Ejecutar Clases**: Inicio automático de secuencias de movimientos y habla
- **Control de Clases**: Pausar/detener clases en progreso
- **Progreso**: Monitoreo del progreso de las clases

### 🔗 Connections Screen
- **Estado de Conexiones**: Robot, cámara, base de datos
- **Pruebas de Conexión**: Verificar conectividad
- **Reconexión**: Intentos automáticos de reconexión
- **Registro**: Historial de conexiones

## 🛠️ API Endpoints

### GET Endpoints
- `GET /api/status` - Estado del robot
- `GET /api/position` - Posición actual del robot
- `GET /api/classes` - Clases disponibles
- `GET /api/connection` - Estado de conexiones
- `GET /api/presets` - Presets de movimiento

### POST Endpoints
- `POST /api/robot/move` - Mover parte del robot
- `POST /api/robot/speak` - Hacer hablar al robot
- `POST /api/class/start` - Iniciar clase
- `POST /api/class/stop` - Detener clase
- `POST /api/preset/execute` - Ejecutar preset
- `POST /api/robot/emergency` - Parada de emergencia

## 📋 Clases Programadas

### Clase 1: Introducción a la Robótica
- **Duración**: 45 minutos
- **Movimientos**: 
  - Saludo inicial
  - Demostración de articulaciones
  - Interacción con estudiantes
- **Habla**: Explicación de conceptos básicos

### Clase 2: Programación de Movimientos
- **Duración**: 60 minutos
- **Movimientos**:
  - Secuencias sincronizadas
  - Movimientos complejos
  - Demostración de algoritmos
- **Habla**: Explicación de programación

### Clase 3: Inteligencia Artificial
- **Duración**: 90 minutos
- **Movimientos**:
  - Gestos expresivos
  - Movimientos adaptativos
  - Demostración de percepción
- **Habla**: Conceptos de IA y ML

## 🎯 Presets de Movimiento

| Preset | Descripción | Movimientos |
|--------|-------------|-------------|
| **Saludo** | Levantar brazo y saludar | Brazo derecho arriba + movimiento de muñeca |
| **Aplauso** | Aplaudir | Ambos brazos + movimiento sincronizado |
| **Señalar** | Apuntar con el dedo | Brazo derecho extendido |
| **OK** | Gesto de aprobación | Pulgar arriba |
| **Paz** | Signo de paz | Dedos en V |
| **Pensativo** | Postura reflexiva | Mano en barbilla + cabeza inclinada |

## 🔧 Desarrollo y Personalización

### Añadir Nueva Clase
1. Edita `robot_gui.py` en `get_available_classes()`
2. Define movimientos en el array `movements`:
```python
{
    "action": "speak", 
    "text": "Texto a decir"
},
{
    "action": "move", 
    "part": "head", 
    "x": 15, "y": 0, "z": 0, 
    "duration": 2
},
{
    "action": "preset", 
    "name": "saludo"
}
```

### Añadir Nuevo Preset
1. Añade el preset en `get_movement_presets()`
2. Implementa la función `execute_[nombre]_preset()`
3. Actualiza el handler en `handle_execute_preset()`

### Personalizar Movimientos
Los rangos de movimiento son:
- **Cabeza**: X(-45,45°), Y(-30,30°), Z(-90,90°)
- **Brazos**: Hombro(-90,90°), Codo(0,120°), Muñeca(-45,45°)
- **Manos**: Dedos(0,90°)

## 🚨 Solución de Problemas

### Robot No Conecta
1. Verificar que `robot_gui.py` esté ejecutándose
2. Revisar que el puerto 8080 esté libre
3. Comprobar firewall/antivirus

### Movimientos No Funcionan
1. Verificar conexión ESP32 en robot_gui
2. Revisar logs en consola de robot_gui
3. Probar parada de emergencia y reinicio

### App No Carga Datos
1. Verificar URL en `RobotAPI.js`
2. Revisar conectividad de red
3. Comprobar CORS en navegador

## 📞 Soporte

Para problemas o sugerencias:
1. Revisar logs en consola del robot_gui
2. Verificar consola del navegador en la app móvil
3. Comprobar estado de conexiones en la app

## 🔄 Actualizaciones Futuras

- [ ] WebSocket para actualizaciones en tiempo real
- [ ] Grabación de secuencias personalizadas
- [ ] Control de voz desde la app
- [ ] Modo automático/programado
- [ ] Integración con cámara del robot
- [ ] Dashboard de análisis de movimientos
