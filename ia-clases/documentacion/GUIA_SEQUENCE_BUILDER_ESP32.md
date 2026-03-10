# Guía Completa: Sequence Builder con Integración ESP32

## 📋 Resumen

El **Sequence Builder** ha sido completamente rediseñado para incluir integración directa con el ESP32, permitiendo crear secuencias de movimientos robóticos de manera intuitiva y práctica. Ahora puedes:

- **Conectarte directamente al ESP32** para controlar el robot en tiempo real
- **Grabar movimientos** mientras controlas el robot
- **Crear secuencias complejas** con movimientos, gestos, habla y acciones
- **Guardar y cargar secuencias** en formato JSON
- **Vincular secuencias a clases** para demostraciones automáticas

## 🎯 Funcionalidades Principales

### 1. **Integración ESP32 Completa**
- Conexión directa al ESP32 usando configuración binaria
- Control en tiempo real de todos los servomotores
- Envío de comandos de movimiento, gestos y habla
- Prueba de conexión integrada

### 2. **Grabación de Secuencias en Tiempo Real**
- Grabación automática de movimientos mientras controlas el robot
- Captura de posiciones específicas con botón dedicado
- Grabación de gestos, habla y acciones rápidas
- Visualización en tiempo real de la secuencia en construcción

### 3. **Controles de Robot Completos**
- **Control de Brazos**: Sliders para todos los servomotores (BI, BD, FI, FD, HI, HD, PD)
- **Acciones Rápidas**: Home, Wave, Hug, Look Around
- **Control de Habla**: Entrada de texto y envío de comandos de habla
- **Gestos**: Saludo, Abrazo, y otros gestos predefinidos

### 4. **Gestión de Secuencias**
- Guardado en formato JSON compatible con el sistema de clases
- Carga de secuencias existentes
- Visualización detallada de movimientos y acciones
- Eliminación de secuencias

## 🚀 Cómo Usar el Sequence Builder

### Paso 1: Conectar al ESP32

1. **Abrir el Sequence Builder**
   - Ve a la pestaña "🎬 Sequence Builder"
   - Verifica que el ESP32 esté encendido y conectado a la red

2. **Configurar Conexión**
   - En la sección "🔌 ESP32 Connection", haz clic en "🔗 Connect"
   - El sistema cargará automáticamente la configuración guardada
   - Si la conexión es exitosa, verás "🟢 Connected"

3. **Probar Conexión**
   - Haz clic en "🧪 Test" para verificar que el ESP32 responde
   - Deberías ver un mensaje de éxito

### Paso 2: Controlar el Robot

1. **Control de Brazos**
   - Usa los sliders en la sección "💪 Arms Control"
   - **Left Arm**: Brazo, Frente, High
   - **Right Arm**: Brazo, Frente, High, Pollo
   - Los movimientos se envían automáticamente al ESP32

2. **Acciones Rápidas**
   - **🏠 Home**: Posición de descanso
   - **👋 Wave**: Gesto de saludo
   - **🤗 Hug**: Gesto de abrazo
   - **👀 Look Around**: Movimiento de cuello

3. **Control de Habla**
   - Escribe el texto en el campo de entrada
   - Haz clic en "🗣️ Speak" para enviar el comando

### Paso 3: Grabar una Secuencia

1. **Iniciar Grabación**
   - Haz clic en "🔴 Start Recording"
   - Verás "🔴 Recording..." en el estado
   - Aparecerá un mensaje confirmando el inicio

2. **Crear Movimientos**
   - **Mover los sliders** para crear movimientos de brazos
   - **Usar acciones rápidas** para gestos y posiciones
   - **Enviar comandos de habla** para narrar la secuencia
   - **Hacer clic en "📍 Capture Position"** para capturar posiciones específicas

3. **Observar la Secuencia**
   - En el panel derecho verás la secuencia en construcción
   - Cada movimiento y acción se muestra en tiempo real
   - Los parámetros se registran automáticamente

4. **Detener Grabación**
   - Haz clic en "⏹️ Stop Recording"
   - La secuencia se guarda en memoria
   - Puedes revisar todos los movimientos grabados

### Paso 4: Guardar la Secuencia

1. **Configurar Información**
   - El nombre y título se pueden editar
   - Por defecto: "New_Sequence" y "New Sequence"

2. **Guardar Archivo**
   - Haz clic en "💾 Save" en la sección de gestión
   - Selecciona ubicación y nombre del archivo
   - El archivo se guarda en formato JSON

3. **Verificar Guardado**
   - La secuencia aparece en la lista de secuencias guardadas
   - Puedes cargarla más tarde para editar o usar

## 📁 Formato de Secuencias

### Estructura JSON
```json
{
  "name": "Mi_Secuencia",
  "title": "Secuencia de Demostración",
  "created_at": "2024-01-15T10:30:00",
  "movements": [
    {
      "id": 1,
      "name": "Movement_1",
      "actions": [
        {
          "command": "BRAZOS",
          "parameters": {
            "BI": 10, "BD": 40, "FI": 80, "FD": 90,
            "HI": 80, "HD": 80, "PD": 45
          },
          "duration": 1000,
          "description": "Home Position",
          "timestamp": 1705312200.123
        },
        {
          "command": "HABLAR",
          "parameters": {
            "texto": "¡Hola estudiantes!"
          },
          "duration": 1000,
          "description": "Speech: ¡Hola estudiantes!",
          "timestamp": 1705312201.456
        }
      ]
    }
  ]
}
```

### Comandos Soportados

#### BRAZOS (Movimiento de Brazos)
```json
{
  "command": "BRAZOS",
  "parameters": {
    "BI": 10,   // Brazo Izquierdo (10-30)
    "BD": 40,   // Brazo Derecho (30-55)
    "FI": 80,   // Frente Izquierdo (60-120)
    "FD": 90,   // Frente Derecho (70-110)
    "HI": 80,   // High Izquierdo (70-90)
    "HD": 80,   // High Derecho (70-90)
    "PD": 45    // Pollo Derecho (0-90)
  }
}
```

#### HABLAR (Comandos de Habla)
```json
{
  "command": "HABLAR",
  "parameters": {
    "texto": "Texto a pronunciar"
  }
}
```

#### MANO (Gestos de Manos)
```json
{
  "command": "MANO",
  "parameters": {
    "M": "derecha",     // Mano: "derecha", "izquierda", "ambas"
    "GESTO": "SALUDO"   // Gesto: "SALUDO", "ABRAZO", etc.
  }
}
```

#### CUELLO (Movimiento de Cuello)
```json
{
  "command": "CUELLO",
  "parameters": {
    "L": 155,   // Lateral (120-160)
    "I": 95,    // Inferior (60-130)
    "S": 110    // Superior (90-120)
  }
}
```

## 🔧 Configuración y Personalización

### Configuración ESP32
- **Archivo de configuración**: `services/esp32_services/esp32_config.bin`
- **Configuración automática**: Se carga desde el ESP32 Tab
- **Configuración manual**: Editar en ESP32 Tab si es necesario

### Límites de Seguridad
- **Brazo Izquierdo**: 10-30 grados
- **Brazo Derecho**: 30-55 grados
- **Frente Izquierdo**: 60-120 grados
- **Frente Derecho**: 70-110 grados
- **High**: 70-90 grados
- **Pollo**: 0-90 grados

### Personalización de Secuencias
- **Nombres personalizados**: Editar antes de guardar
- **Descripciones detalladas**: Agregar en cada acción
- **Duración personalizada**: Modificar en el JSON si es necesario

## 🔗 Integración con Sistema de Clases

### Vinculación a Clases
1. **Crear secuencia** en Sequence Builder
2. **Guardar secuencia** en formato JSON
3. **Copiar a carpeta de clase**:
   ```bash
   cp mi_secuencia.json clases/mi_clase/demo/
   ```
4. **Configurar en clase**: La clase puede cargar y ejecutar la secuencia

### Uso en Demostraciones
- **Ejecución automática**: Durante fases de demostración
- **Control manual**: Desde ESP32 Tab
- **Sincronización**: Con contenido de la clase

## 🐛 Solución de Problemas

### Problema: No se puede conectar al ESP32
**Causa**: ESP32 no está encendido o configuración incorrecta
**Solución**:
1. Verificar que el ESP32 esté encendido
2. Verificar la configuración en ESP32 Tab
3. Probar conexión desde ESP32 Tab primero

### Problema: Los movimientos no se graban
**Causa**: No se inició la grabación o no hay conexión
**Solución**:
1. Verificar que esté conectado al ESP32
2. Iniciar grabación con "🔴 Start Recording"
3. Verificar que aparezca "🔴 Recording..."

### Problema: La secuencia no se guarda
**Causa**: No hay movimientos grabados o error de archivo
**Solución**:
1. Verificar que haya movimientos en la secuencia
2. Verificar permisos de escritura en la carpeta
3. Revisar el log para errores específicos

### Problema: Los movimientos no se envían al ESP32
**Causa**: Conexión perdida o ESP32 no responde
**Solución**:
1. Verificar estado de conexión
2. Probar con "🧪 Test"
3. Reconectar si es necesario

## 📊 Ejemplos de Uso

### Ejemplo 1: Secuencia de Saludo
1. **Conectar al ESP32**
2. **Iniciar grabación**
3. **Enviar saludo**: "¡Hola estudiantes!"
4. **Mover brazos**: Posición de saludo
5. **Gesto de saludo**: Wave
6. **Detener grabación**
7. **Guardar como**: "Saludo_Inicial.json"

### Ejemplo 2: Secuencia de Demostración
1. **Conectar al ESP32**
2. **Iniciar grabación**
3. **Narrar**: "Vamos a hacer una demostración"
4. **Mover brazos**: Posiciones de demostración
5. **Gestos**: Abrazo, Look Around
6. **Narrar**: "Esto es todo por hoy"
7. **Posición final**: Home
8. **Guardar como**: "Demo_Completa.json"

## 🔮 Próximas Mejoras

- **Editor visual**: Interfaz gráfica para editar secuencias
- **Biblioteca de secuencias**: Gestión centralizada
- **Sincronización con diapositivas**: Vinculación automática
- **Grabación de audio**: Incluir audio en las secuencias
- **Exportación a otros formatos**: Compatibilidad con otros sistemas

## 📞 Soporte

Para problemas o preguntas sobre el Sequence Builder:
1. Revisar esta guía completa
2. Verificar la configuración del ESP32
3. Revisar los logs de la aplicación
4. Probar con secuencias simples primero

---

**Nota**: El Sequence Builder está diseñado para trabajar con el sistema ESP32 del robot ADAI. Asegúrate de que el ESP32 esté correctamente configurado y funcionando antes de usar esta funcionalidad.
