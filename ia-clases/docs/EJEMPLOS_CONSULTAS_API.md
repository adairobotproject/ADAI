# Ejemplos de Consultas API

Este documento contiene ejemplos prácticos de las consultas que se realizan entre los diferentes componentes del sistema.

## 📱 App Móvil → Servidor Python

La app móvil (ReactLynx) se comunica con el servidor Python mediante HTTP REST API.

### Base URL
```
http://[IP_SERVIDOR]:[PUERTO]
Ejemplo: http://192.168.1.50:8000
```

### 1. Obtener Estado del Robot

**Endpoint:** `GET /api/status`

**Ejemplo en JavaScript (RobotAPI.js):**
```javascript
const result = await robotAPI.getRobotStatus();
// O directamente:
const result = await robotAPI.makeRequest('/api/status');
```

**Request:**
```http
GET /api/status HTTP/1.1
Host: 192.168.1.50:8000
Content-Type: application/json
```

**Response:**
```json
{
  "status": "active",
  "battery": 87,
  "temperature": 42.5,
  "connection": "connected",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### 2. Obtener Posición Actual del Robot

**Endpoint:** `GET /api/position`

**Ejemplo en JavaScript:**
```javascript
const result = await robotAPI.getRobotPosition();
```

**Response:**
```json
{
  "head": {"x": 0, "y": 0, "z": 0},
  "leftArm": {"shoulder": 0, "elbow": 0, "wrist": 0},
  "rightArm": {"shoulder": 0, "elbow": 0, "wrist": 0},
  "torso": {"rotation": 0, "tilt": 0},
  "leftHand": {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 0},
  "rightHand": {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 0}
}
```

---

### 3. Obtener Clases Disponibles

**Endpoint:** `GET /api/classes`

**Ejemplo en JavaScript:**
```javascript
const result = await robotAPI.getAvailableClasses();
```

**Response:**
```json
{
  "success": true,
  "classes": [
    {
      "name": "Clase_2_Espanol_Quinto_Grado_clase.py",
      "title": "Español Quinto Grado",
      "subject": "Español",
      "description": "Clase de español para quinto grado",
      "duration": "45 min",
      "created_date": "2024-01-15",
      "status": "available"
    }
  ]
}
```

---

### 4. Ejecutar una Clase

**Endpoint:** `POST /api/class/execute`

**Ejemplo en JavaScript:**
```javascript
const result = await robotAPI.startClass("Clase_2_Espanol_Quinto_Grado_clase.py");
// O directamente:
const result = await robotAPI.makeRequest('/api/class/execute', {
  method: 'POST',
  body: JSON.stringify({ class_name: "Clase_2_Espanol_Quinto_Grado_clase.py" })
});
```

**Request:**
```http
POST /api/class/execute HTTP/1.1
Host: 192.168.1.50:8000
Content-Type: application/json

{
  "class_name": "Clase_2_Espanol_Quinto_Grado_clase.py"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Class executed successfully",
  "class_name": "Clase_2_Espanol_Quinto_Grado_clase.py"
}
```

---

### 5. Mover el Robot

**Endpoint:** `POST /api/robot/move`

**Ejemplo en JavaScript:**
```javascript
// Mover brazo izquierdo
const result = await robotAPI.moveArm('leftArm', 45, 90, 0);

// Mover cuello
const result = await robotAPI.moveHead(10, -5, 0);

// Mover mano
const result = await robotAPI.moveHand('leftHand', {
  thumb: 90,
  index: 45,
  middle: 0,
  ring: 0,
  pinky: 0
});

// O directamente:
const result = await robotAPI.moveRobot({
  action: 'neck_yes',
  part: 'neck',
  name: 'Asentir'
});
```

**Request:**
```http
POST /api/robot/move HTTP/1.1
Host: 192.168.1.50:8000
Content-Type: application/json

{
  "action": "neck_yes",
  "part": "neck",
  "name": "Asentir"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Movement executed successfully"
}
```

---

### 6. Hacer Hablar al Robot

**Endpoint:** `POST /api/robot/speak`

**Ejemplo en JavaScript:**
```javascript
const result = await robotAPI.speakText("¡Hola! Soy el robot ADAI");
```

**Request:**
```http
POST /api/robot/speak HTTP/1.1
Host: 192.168.1.50:8000
Content-Type: application/json

{
  "text": "¡Hola! Soy el robot ADAI"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Speech executed successfully"
}
```

---

### 7. Obtener Progreso de la Clase

**Endpoint:** `GET /api/class/progress`

**Ejemplo en JavaScript:**
```javascript
const result = await robotAPI.getClassProgress();
```

**Response:**
```json
{
  "class_name": "Clase_2_Espanol_Quinto_Grado_clase.py",
  "phase": "presentation",
  "progress_percentage": 45,
  "elapsed_time": "20s",
  "remaining_time": "25s",
  "current_phase": "Presentación",
  "phase_emoji": "📚",
  "is_active": true,
  "status": "Clase en progreso"
}
```

---

### 8. Solicitud del Profesor

**Endpoint:** `POST /api/teacher/request`

**Ejemplo en JavaScript:**
```javascript
const result = await robotAPI.handleTeacherRequest('general');
// Tipos: 'general', 'examples', 'repeat_question'
```

**Request:**
```http
POST /api/teacher/request HTTP/1.1
Host: 192.168.1.50:8000
Content-Type: application/json

{
  "request_type": "general"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Teacher request 'general' processed"
}
```

---

### 9. Pausar/Reanudar Clase

**Endpoint:** `POST /api/teacher/pause`

**Ejemplo en JavaScript:**
```javascript
// Pausar
const result = await robotAPI.pauseClass(true);

// Reanudar
const result = await robotAPI.pauseClass(false);
```

**Request:**
```http
POST /api/teacher/pause HTTP/1.1
Host: 192.168.1.50:8000
Content-Type: application/json

{
  "is_paused": true
}
```

---

### 10. Parada de Emergencia

**Endpoint:** `POST /api/robot/emergency`

**Ejemplo en JavaScript:**
```javascript
const result = await robotAPI.emergencyStop();
```

**Request:**
```http
POST /api/robot/emergency HTTP/1.1
Host: 192.168.1.50:8000
Content-Type: application/json

{
  "action": "emergency_stop"
}
```

---

### 11. Obtener Estado de Conexión

**Endpoint:** `GET /api/connection`

**Ejemplo en JavaScript:**
```javascript
const result = await robotAPI.getConnectionStatus();
```

**Response:**
```json
{
  "mainServer": "connected",
  "robotServer": "connected",
  "database": "connected",
  "camera": "connected",
  "mobileAPI": "connected"
}
```

---

### 12. Probar Conexión

**Endpoint:** `GET /status` (sin /api)

**Ejemplo en JavaScript:**
```javascript
const result = await robotAPI.testConnection();
// O:
const result = await robotAPI.pingServer();
```

---

## 🖥️ Servidor Python → ESP32

El servidor Python se comunica con el ESP32 mediante HTTP REST API.

### Base URL
```
http://[IP_ESP32]:80
Ejemplo: http://192.168.1.100:80
```

### 1. Mover Brazos

**Endpoint:** `POST /brazos/mover`

**Ejemplo en Python (esp32_connector.py):**
```python
from services.esp32_services.esp32_connector import ESP32Connector, ESP32Config

config = ESP32Config(host="192.168.1.100", port=80)
connector = ESP32Connector(config)
connector.connect()

# Mover brazos: brazo_izq, frente_izq, brazo_der, frente_der
success, response = connector.move_arms(
    bi=10,   # Brazo izquierdo (0-40)
    fi=100,  # Frente izquierdo (60-120)
    bd=20,   # Brazo derecho (0-40)
    fd=90    # Frente derecho (70-110)
)
```

**Request HTTP:**
```http
POST /brazos/mover HTTP/1.1
Host: 192.168.1.100:80
Content-Type: application/x-www-form-urlencoded

bi=10&fi=100&bd=20&fd=90
```

**Response:**
```
OK - Brazos movidos
```

---

### 2. Mover Cuello

**Endpoint:** `POST /cuello/mover`

**Ejemplo en Python:**
```python
# Mover cuello: lateral, inferior, superior
success, response = connector.move_neck(
    lateral=155,   # Lateral (120-190)
    inferior=95,   # Inferior (60-130)
    superior=105   # Superior (90-120)
)
```

**Request HTTP:**
```http
POST /cuello/mover HTTP/1.1
Host: 192.168.1.100:80
Content-Type: application/x-www-form-urlencoded

lateral=155&inferior=95&superior=105
```

---

### 3. Gestos del Cuello

**Ejemplo en Python:**
```python
# Asentir (sí)
success, response = connector.neck_yes()

# Negar (no)
success, response = connector.neck_no()

# Centrar
success, response = connector.neck_center()

# Aleatorio
success, response = connector.neck_random()
```

**Endpoints:**
- `GET /cuello/si` - Asentir
- `GET /cuello/no` - Negar
- `GET /cuello/centrar` - Centrar
- `GET /cuello/aleatorio` - Movimiento aleatorio

---

### 4. Control de Manos - Gestos

**Endpoint:** `POST /manos/gesto`

**Ejemplo en Python:**
```python
# Realizar gesto con la mano
success, response = connector.hand_gesture(
    hand='derecha',  # 'derecha' o 'izquierda'
    gesture='paz'     # 'paz', 'rock', 'ok', 'senalar', 'abrir', 'cerrar'
)
```

**Request HTTP:**
```http
POST /manos/gesto HTTP/1.1
Host: 192.168.1.100:80
Content-Type: application/x-www-form-urlencoded

mano=derecha&gesto=paz
```

---

### 5. Control de Dedos Individuales

**Endpoint:** `POST /manos/dedo`

**Ejemplo en Python:**
```python
# Mover dedo específico
success, response = connector.move_finger(
    hand='derecha',
    finger='indice',  # 'pulgar', 'indice', 'medio', 'anular', 'menique'
    angle=90          # 0-180 grados
)
```

**Ejemplo en Python (esp32_client.py):**
```python
from services.esp32_services.esp32_client import ESP32Client

client = ESP32Client(host="192.168.1.100", port=80)
client.connect()

success = client.send_finger_control(
    hand='derecha',
    finger='indice',
    angle=90
)
```

**Request HTTP:**
```http
POST /manos/dedo HTTP/1.1
Host: 192.168.1.100:80
Content-Type: application/x-www-form-urlencoded

mano=derecha&dedo=indice&angulo=90
```

---

### 6. Control de Muñecas

**Endpoint:** `POST /munecas/mover`

**Ejemplo en Python:**
```python
# Mover muñeca
success, response = connector.move_wrist(
    hand='derecha',
    angle=80  # 0-160 grados
)
```

**Request HTTP:**
```http
POST /munecas/mover HTTP/1.1
Host: 192.168.1.100:80
Content-Type: application/x-www-form-urlencoded

mano=derecha&angulo=80
```

---

### 7. Brazos - Posición de Descanso

**Endpoint:** `GET /brazos/descanso`

**Ejemplo en Python:**
```python
success, response = connector.arms_rest_position()
```

---

### 8. Brazos - Saludo

**Endpoint:** `GET /brazos/saludo`

**Ejemplo en Python:**
```python
success, response = connector.arms_salute()
```

---

### 9. Brazos - Abrazo

**Endpoint:** `GET /brazos/abrazar`

**Ejemplo en Python:**
```python
success, response = connector.arms_hug()
```

---

### 10. Sistema - Seguridad

**Endpoint:** `POST /system/security`

**Ejemplo en Python:**
```python
# Activar modo seguridad
success, response = connector.system_security(enabled=True)

# Desactivar modo seguridad
success, response = connector.system_security(enabled=False)
```

**Request HTTP:**
```http
POST /system/security HTTP/1.1
Host: 192.168.1.100:80
Content-Type: application/x-www-form-urlencoded

on=true
```

---

### 11. Sistema - Velocidad

**Endpoint:** `POST /system/speed`

**Ejemplo en Python:**
```python
# Modo lento
success, response = connector.system_speed(slow=True)

# Velocidad normal
success, response = connector.system_speed(slow=False)
```

---

### 12. Sistema - Verificar Conexiones

**Endpoint:** `GET /system/check`

**Ejemplo en Python:**
```python
success, response = connector.system_check()
```

---

### 13. Sistema - Reset

**Endpoint:** `GET /system/reset`

**Ejemplo en Python:**
```python
success, response = connector.system_reset()
```

---

### 14. Sistema - Posición de Descanso

**Endpoint:** `GET /system/descanso`

**Ejemplo en Python:**
```python
success, response = connector.system_rest_position()
```

---

### 15. Comandos de Secuencia

**Endpoint:** `POST /sequence/command`

**Ejemplo en Python (esp32_client.py):**
```python
# Enviar movimiento de brazos
success = client.send_movement(
    bi=10,  # Brazo Izquierdo
    bd=20,  # Brazo Derecho
    fi=100, # Frente Izquierdo
    fd=90,  # Frente Derecho
    hi=80,  # High Izquierdo
    hd=80,  # High Derecho
    pd=45   # Pollo Derecho
)

# Enviar gesto
success = client.send_gesture(
    hand='derecha',
    gesture='paz'
)

# Enviar habla
success = client.send_speech("¡Hola! Soy el robot ADAI")

# Enviar espera
success = client.send_wait(duration_ms=2000)

# Enviar movimiento de cuello
success = client.send_neck_movement(
    l=155,  # Lateral
    i=95,   # Inferior
    s=105   # Superior
)
```

**Request HTTP (movimiento):**
```http
POST /sequence/command HTTP/1.1
Host: 192.168.1.100:80
Content-Type: application/x-www-form-urlencoded

command=BRAZOS&params=BI=10 BD=20 FI=100 FD=90 HI=80 HD=80 PD=45
```

---

### 16. Obtener Estado del ESP32

**Endpoint:** `GET /debug`

**Ejemplo en Python:**
```python
# Usando esp32_client.py
status = client.get_status()

# Usando esp32_connector.py
success, response = connector.get_debug_info()
```

**Response:**
```
ESP32 Status
Connected: Yes
MEGA: Connected
UNO: Connected
...
```

---

### 17. Obtener Posiciones Actuales

**Endpoint:** `GET /posiciones`

**Ejemplo en Python:**
```python
success, positions = connector.get_positions()
if success:
    print(positions)
    # {
    #   "brazos": [...],
    #   "cuello": [...],
    #   "manos": [...],
    #   "munecas": [...]
    # }
```

---

## 🔄 Flujo Completo de Ejemplo

### Ejemplo: Ejecutar una Clase desde la App Móvil

1. **App Móvil → Servidor:** Obtener clases disponibles
   ```javascript
   const classes = await robotAPI.getAvailableClasses();
   ```

2. **App Móvil → Servidor:** Iniciar clase
   ```javascript
   await robotAPI.startClass("Clase_2_Espanol_Quinto_Grado_clase.py");
   ```

3. **Servidor (clase Python):** Mover brazos del robot
   ```python
   from services.esp32_services.esp32_client import ESP32Client
   
   client = ESP32Client()
   client.connect()
   client.send_movement(bi=10, bd=20, fi=100, fd=90, hi=80, hd=80, pd=45)
   ```

4. **Servidor (clase Python):** Hacer hablar al robot
   ```python
   client.send_speech("¡Buenos días estudiantes!")
   ```

5. **Servidor (clase Python):** Gesto de saludo
   ```python
   client.send_gesture('derecha', 'paz')
   ```

6. **App Móvil → Servidor:** Obtener progreso
   ```javascript
   const progress = await robotAPI.getClassProgress();
   ```

---

## 📝 Notas Importantes

1. **CORS:** El servidor Python incluye headers CORS para permitir peticiones desde la app móvil.

2. **Timeouts:** 
   - App móvil: 5 segundos para GET, 10 segundos para POST
   - Servidor → ESP32: 2-5 segundos por defecto

3. **Formato de Datos:**
   - App móvil → Servidor: JSON (`application/json`)
   - Servidor → ESP32: Form URL-encoded (`application/x-www-form-urlencoded`)

4. **Manejo de Errores:**
   - Todas las funciones retornan objetos con `success: true/false`
   - Los errores incluyen mensajes descriptivos

5. **Validación:**
   - El ESP32 valida los rangos de movimiento antes de ejecutar
   - El servidor valida los datos antes de enviar al ESP32




