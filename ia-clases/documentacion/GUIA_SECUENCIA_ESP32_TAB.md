# Guía de Uso: Carga y Ejecución de Secuencias en ESP32 Tab

## 📋 Resumen

El ESP32 Tab ahora incluye funcionalidad completa para cargar y ejecutar secuencias de demostración en el simulador. Esta funcionalidad permite:

- **Cargar secuencias JSON** desde el directorio `sequences/`
- **Ejecutar secuencias en el simulador** con visualización en tiempo real
- **Controlar la ejecución** (pausar, reanudar, detener)
- **Logging detallado** de todas las acciones ejecutadas

## 🎯 Funcionalidades Implementadas

### 1. Carga de Secuencias
- **Botón "📁 Load Sequence"**: Abre un diálogo para seleccionar archivos JSON
- **Campo de ruta**: Muestra la secuencia cargada actualmente
- **Validación**: Verifica que el archivo sea un JSON válido con estructura de secuencia

### 2. Ejecución de Secuencias
- **Botón "🎬 Execute Sequence"**: Inicia la ejecución de la secuencia cargada
- **Ejecución en hilo separado**: No bloquea la interfaz de usuario
- **Control de estado**: Pausar, reanudar y detener la ejecución

### 3. Simulación de Acciones
- **Movimientos de brazos**: Simula comandos `BRAZOS` con parámetros BI, BD, FI, FD, HI, HD, PD
- **Movimientos de cuello**: Simula comandos `CUELLO` con parámetros L, I, S
- **Gestos de manos**: Simula comandos `MANO` con gestos y ángulos
- **Comandos de habla**: Simula comandos `HABLAR` con texto
- **Esperas**: Simula comandos `ESPERAR` con duración

### 4. Logging y Monitoreo
- **Log en tiempo real**: Todas las acciones se registran en el log del ESP32
- **Categorización**: Las acciones se categorizan por tipo (MOVEMENT, NECK, HAND, SPEECH, etc.)
- **Información de progreso**: Muestra el movimiento y acción actual

## 🚀 Cómo Usar

### Paso 1: Abrir el ESP32 Tab
1. Inicia la aplicación RobotGUI
2. Ve a la pestaña "🔌 ESP32 Controller"
3. Haz clic en la subpestaña "🤖 Arms Simulator"

### Paso 2: Cargar una Secuencia
1. En la sección "🎬 Sequence Demo", haz clic en "📁 Load Sequence"
2. Navega al directorio `sequences/`
3. Selecciona un archivo JSON de secuencia (ej: `sequence_Quimica_Neutralizacion_Completa.json`)
4. La secuencia se cargará y mostrará información en el campo de ruta

### Paso 3: Ejecutar la Secuencia
1. Una vez cargada la secuencia, haz clic en "🎬 Execute Sequence"
2. La ejecución comenzará automáticamente
3. Observa el log para ver las acciones ejecutándose
4. El simulador se actualizará con los movimientos

### Paso 4: Controlar la Ejecución
- **⏸️ Pause**: Pausa la ejecución actual
- **▶️ Resume**: Reanuda la ejecución desde donde se pausó
- **⏹️ Stop**: Detiene completamente la ejecución

## 📁 Formato de Secuencias Soportadas

### Formato Principal (Chemistry Sequence)
```json
{
  "name": "Nombre de la Secuencia",
  "title": "Título de la Secuencia",
  "movements": [
    {
      "id": 1,
      "name": "Nombre del Movimiento",
      "actions": [
        {
          "command": "BRAZOS",
          "parameters": {
            "BI": 10,
            "FI": 80,
            "HI": 80,
            "BD": 40,
            "FD": 90,
            "HD": 80,
            "PD": 45
          },
          "duration": 1000,
          "description": "Descripción de la acción"
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
    "FI": 80,   // Frente Izquierdo (60-120)
    "HI": 80,   // High Izquierdo (70-90)
    "BD": 40,   // Brazo Derecho (30-55)
    "FD": 90,   // Frente Derecho (70-110)
    "HD": 80,   // High Derecho (70-90)
    "PD": 45    // Pollo Derecho (0-90)
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

#### MANO (Gestos de Manos)
```json
{
  "command": "MANO",
  "parameters": {
    "M": "derecha",     // Mano: "derecha", "izquierda", "ambas"
    "GESTO": "SALUDO"   // Gesto: "SALUDO", "DESCANSO", etc.
  }
}
```

#### HABLAR (Comandos de Habla)
```json
{
  "command": "HABLAR",
  "parameters": {
    "texto": "¡Hola estudiantes! Bienvenidos a la clase"
  }
}
```

## 🔧 Configuración y Personalización

### Logging
- **Habilitar/Deshabilitar**: Usa el checkbox "📝 Enable Command Log"
- **Limpiar log**: Botón "🗑️ Clear Log"
- **Exportar log**: Botón "💾 Export Log"

### Simulador
- **Habilitar/Deshabilitar**: Usa el checkbox "🎮 Enable Simulator"
- **Actualización en tiempo real**: Usa el checkbox "⚡ Real-time Update"

## 🐛 Solución de Problemas

### Problema: "Unknown action type: unknown"
**Causa**: La secuencia no tiene el formato esperado
**Solución**: Verifica que la secuencia use el formato de comandos (`command` field) en lugar de tipos (`type` field)

### Problema: La secuencia no se ejecuta
**Causa**: Archivo JSON inválido o estructura incorrecta
**Solución**: 
1. Verifica que el archivo sea JSON válido
2. Asegúrate de que tenga la estructura correcta con `movements` y `actions`
3. Revisa el log para errores específicos

### Problema: El simulador no se actualiza
**Causa**: Simulador deshabilitado o error en la actualización
**Solución**:
1. Verifica que "🎮 Enable Simulator" esté activado
2. Verifica que "⚡ Real-time Update" esté activado
3. Revisa el log para errores de actualización

### Problema: Los brazos no se mueven en el simulador
**Causa**: Mapeo incorrecto de parámetros entre secuencia y simulador
**Solución**:
1. Verifica que la secuencia use los parámetros correctos (BI, FI, HI, BD, FD, HD, PD)
2. Asegúrate de que el simulador esté habilitado
3. Revisa el log para mensajes "SIMULATOR" que confirmen las actualizaciones

## 🔧 Mapeo de Parámetros

### Secuencia → Simulador
Los parámetros de la secuencia se mapean automáticamente a las variables del simulador:

| Secuencia | Simulador | Descripción |
|-----------|-----------|-------------|
| `BI` | `left_brazo_var` | Brazo Izquierdo |
| `FI` | `left_frente_var` | Frente Izquierdo |
| `HI` | `left_high_var` | High Izquierdo |
| `BD` | `right_brazo_var` | Brazo Derecho |
| `FD` | `right_frente_var` | Frente Derecho |
| `HD` | `right_high_var` | High Derecho |
| `PD` | `right_pollo_var` | Pollo Derecho |

### Ejemplo de Mapeo
```json
{
  "command": "BRAZOS",
  "parameters": {
    "BI": 30,   // → left_brazo_var.set(30)
    "FI": 120,  // → left_frente_var.set(120)
    "HI": 85,   // → left_high_var.set(85)
    "BD": 55,   // → right_brazo_var.set(55)
    "FD": 110,  // → right_frente_var.set(110)
    "HD": 85,   // → right_high_var.set(85)
    "PD": 60    // → right_pollo_var.set(60)
  }
}
```

## 📊 Ejemplos de Uso

### Ejemplo 1: Secuencia de Química
```bash
# Cargar la secuencia de neutralización
1. Abrir ESP32 Tab > Arms Simulator
2. Clic en "📁 Load Sequence"
3. Seleccionar: sequences/sequence_Quimica_Neutralizacion_Completa.json
4. Clic en "🎬 Execute Sequence"
5. Observar la ejecución en el log y simulador
```

### Ejemplo 2: Crear Secuencia Personalizada
```json
{
  "name": "Mi_Secuencia",
  "title": "Secuencia Personalizada",
  "movements": [
    {
      "id": 1,
      "name": "Saludo",
      "actions": [
        {
          "command": "HABLAR",
          "parameters": {"texto": "¡Hola!"},
          "duration": 2000
        },
        {
          "command": "BRAZOS",
          "parameters": {"BD": 30, "FD": 110},
          "duration": 1000
        }
      ]
    }
  ]
}
```

## 🔮 Próximas Mejoras

- **Visualización 3D**: Simulador 3D más avanzado
- **Grabación de secuencias**: Grabar secuencias desde la interfaz
- **Sincronización con ESP32 real**: Ejecutar secuencias en el robot físico
- **Editor de secuencias**: Editor visual para crear secuencias
- **Biblioteca de secuencias**: Gestión de múltiples secuencias

## 📞 Soporte

Para problemas o preguntas sobre la funcionalidad de secuencias:
1. Revisa el log del ESP32 para errores específicos
2. Verifica que los archivos JSON tengan el formato correcto
3. Asegúrate de que las secuencias estén en el directorio `sequences/`

---

**Nota**: Esta funcionalidad está diseñada para simulación y demostración. Para ejecutar secuencias en el robot físico, se requiere configuración adicional del ESP32.
