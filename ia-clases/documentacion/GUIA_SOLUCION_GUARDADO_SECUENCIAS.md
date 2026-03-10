# Guía para Solucionar el Problema de Guardado de Secuencias

## Problema Identificado

El problema principal es que **necesitas estar conectado al ESP32 (o en modo debug) antes de poder grabar y guardar secuencias**. Esto puede ser confuso para usuarios que quieren probar el sistema sin hardware.

## Soluciones Implementadas

### ✅ **Solución 1: Modo Debug Mejorado**

Ahora puedes grabar secuencias sin conexión ESP32:

1. **Habilitar Modo Debug**:
   - Ve al panel "🔌 ESP32 Connection"
   - Haz clic en el botón "🐛 Debug Mode" (naranja)
   - El botón cambiará a "🐛 Debug Active" (verde)
   - El estado mostrará "🟢 Debug Connected"

2. **Grabar Secuencia**:
   - Haz clic en "🔴 Start Recording"
   - Usa los controles del robot para crear movimientos
   - Haz clic en "⏹️ Stop Recording"
   - Ahora puedes guardar la secuencia

### ✅ **Solución 2: Secuencia de Ejemplo**

Si no quieres grabar, puedes crear una secuencia de ejemplo:

1. **Crear Secuencia de Ejemplo**:
   - Ve al panel "📁 Sequence Management"
   - Haz clic en el botón "📝 Sample" (naranja)
   - Se creará automáticamente una secuencia con:
     - Posición de inicio (Home Position)
     - Gesto de saludo (Wave Gesture)
     - Mensaje de voz de ejemplo

2. **Guardar la Secuencia**:
   - Haz clic en "💾 Save"
   - Elige la ubicación y nombre del archivo
   - La secuencia se guardará como archivo JSON

### ✅ **Solución 3: Grabación Sin Conexión ESP32**

Ahora puedes grabar incluso sin conexión ESP32:

1. **Intentar Grabar Sin Conexión**:
   - Haz clic en "🔴 Start Recording"
   - Aparecerá un diálogo preguntando si quieres continuar
   - Selecciona "Sí" para continuar en modo demo

2. **Usar Controles**:
   - Mueve los sliders de brazos, manos, etc.
   - Usa los botones de acciones rápidas
   - Las acciones se grabarán (aunque no se envíen al ESP32)

## Pasos para Guardar una Secuencia

### Opción A: Con ESP32 Real
1. Conecta el ESP32
2. Haz clic en "🔗 Connect"
3. Haz clic en "🔴 Start Recording"
4. Usa los controles del robot
5. Haz clic en "⏹️ Stop Recording"
6. Haz clic en "💾 Save"

### Opción B: Con Modo Debug
1. Haz clic en "🐛 Debug Mode"
2. Haz clic en "🔴 Start Recording"
3. Usa los controles del robot
4. Haz clic en "⏹️ Stop Recording"
5. Haz clic en "💾 Save"

### Opción C: Secuencia de Ejemplo
1. Haz clic en "📝 Sample"
2. Haz clic en "💾 Save"

## Estructura del Archivo JSON Guardado

```json
{
  "name": "Mi_Secuencia",
  "title": "Mi Secuencia",
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
          "timestamp": 1705312200.0
        }
      ]
    }
  ],
  "total_movements": 1,
  "total_actions": 1
}
```

## Mensajes de Error Comunes

### "No sequence to save. Please record some actions first."
**Solución**: 
- Asegúrate de haber grabado acciones o creado una secuencia de ejemplo
- Verifica que estés en modo debug o conectado al ESP32

### "Please connect to ESP32 first before recording"
**Solución**:
- Habilita el modo debug haciendo clic en "🐛 Debug Mode"
- O conecta un ESP32 real

### "Error saving sequence"
**Solución**:
- Verifica que tienes permisos de escritura en la carpeta
- Asegúrate de que el nombre del archivo sea válido
- Revisa que hay acciones grabadas para guardar

## Consejos de Uso

### Para Desarrollo y Pruebas
1. **Usa Modo Debug**: Es la forma más fácil de probar sin hardware
2. **Crea Secuencias de Ejemplo**: Útil para entender la estructura
3. **Guarda en Ubicaciones Conocidas**: Usa carpetas donde tengas permisos

### Para Producción
1. **Conecta ESP32 Real**: Para control real del robot
2. **Prueba las Secuencias**: Reproduce las secuencias guardadas
3. **Backup de Secuencias**: Guarda copias de secuencias importantes

## Verificación de Funcionamiento

### Verificar que el Guardado Funciona
1. Crea una secuencia de ejemplo
2. Haz clic en "💾 Save"
3. Elige una ubicación y nombre
4. Verifica que el archivo se creó
5. Abre el archivo para verificar el contenido JSON

### Verificar que la Carga Funciona
1. Haz clic en "📂 Load"
2. Selecciona un archivo JSON guardado previamente
3. Verifica que la secuencia se carga correctamente
4. Revisa que los movimientos aparecen en la lista

## Solución de Problemas Avanzados

### Si el Modo Debug No Funciona
1. Reinicia la aplicación
2. Verifica que los servicios ESP32 estén disponibles
3. Revisa la consola para mensajes de error

### Si No Puedes Guardar Archivos
1. Verifica permisos de escritura en la carpeta
2. Intenta guardar en el escritorio o documentos
3. Verifica que hay espacio en disco

### Si las Secuencias No Se Reproducen
1. Verifica que el archivo JSON es válido
2. Asegúrate de estar conectado al ESP32 o en modo debug
3. Revisa que los comandos en la secuencia son compatibles

## Comandos Soportados en Secuencias

### BRAZOS (Movimiento de Brazos)
```json
{
  "command": "BRAZOS",
  "parameters": {
    "BI": 10,  // Brazo izquierdo
    "BD": 40,  // Brazo derecho
    "FI": 80,  // Frente izquierdo
    "FD": 90,  // Frente derecho
    "HI": 80,  // High izquierdo
    "HD": 80,  // High derecho
    "PD": 45   // Pollo derecho
  }
}
```

### MANO (Control de Manos)
```json
{
  "command": "MANO",
  "parameters": {
    "M": "derecha",     // mano: izquierda, derecha, ambas
    "GESTO": "SALUDO",  // gesto: SALUDO, ABRAZO, ABRIR, CERRAR, PAZ
    "DEDO": "pulgar",   // dedo: pulgar, indice, medio, anular, menique
    "ANG": 90           // ángulo (0-180 para dedos, 0-160 para muñecas)
  }
}
```

### HABLAR (Síntesis de Voz)
```json
{
  "command": "HABLAR",
  "parameters": {
    "texto": "Hola estudiantes"
  }
}
```

### CUELLO (Movimiento de Cuello)
```json
{
  "command": "CUELLO",
  "parameters": {
    "L": 155,  // Left
    "I": 95,   // Inclination
    "S": 110   // Side
  }
}
```

---

*Esta guía te ayudará a resolver el problema de guardado de secuencias. Si sigues teniendo problemas, revisa los mensajes de error en la consola y verifica que todos los pasos se han seguido correctamente.*
