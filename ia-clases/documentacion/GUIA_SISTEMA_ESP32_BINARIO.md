# Sistema de Configuración Binaria ESP32 para Clases
==================================================

## Descripción General
Este sistema permite que las clases lean automáticamente la configuración de conexión ESP32 desde un archivo binario y se conecten directamente al ESP32 para enviar comandos durante su ejecución.

## Componentes del Sistema

### 1. ESP32 Binary Configuration Manager (`esp32_config_binary.py`)
Gestor de configuración ESP32 en formato binario que permite:
- Guardar configuración en archivo binario
- Cargar configuración desde archivo binario
- Validar configuración
- Probar conexión
- Exportar/importar a JSON

### 2. ESP32 Client (`esp32_client.py`)
Cliente simplificado para que las clases se conecten al ESP32:
- Conexión automática usando configuración binaria
- Envío de comandos (movimiento, gestos, habla, acciones)
- Manejo de errores y reconexión
- Cliente global para uso compartido

### 3. Sequence Executor con ESP32 (`sequence_executor_with_logging.py`)
Ejecutor de secuencias actualizado para usar el cliente ESP32 real:
- Integración con cliente ESP32
- Logging de señales enviadas al ESP32
- Ejecución de comandos reales

## Estructura del Archivo Binario

El archivo `esp32_config.bin` tiene la siguiente estructura:

```
Magic Header (8 bytes): "ESP32CONF"
Version (4 bytes): 1
Timestamp (8 bytes): Unix timestamp
Host Length (4 bytes): Longitud del host
Host (variable): Dirección IP del ESP32
Port (4 bytes): Puerto del ESP32
Timeout (8 bytes): Timeout de conexión
Enable Control (1 byte): Habilitar control
Auto Connect (1 byte): Auto-conexión
Retry Attempts (4 bytes): Intentos de reconexión
Retry Delay (8 bytes): Delay entre intentos
Last Connection (8 bytes): Última conexión
Connection Status Length (4 bytes): Longitud del estado
Connection Status (variable): Estado actual
Firmware Version Length (4 bytes): Longitud de versión
Firmware Version (variable): Versión del firmware
Device Name Length (4 bytes): Longitud del nombre
Device Name (variable): Nombre del dispositivo
```

## Uso en Clases

### Configuración Automática
Las clases pueden usar el sistema de configuración binaria automáticamente:

```python
# En cualquier clase
try:
    from esp32_client import get_esp32_client, connect_to_esp32
    ESP32_AVAILABLE = True
except ImportError:
    ESP32_AVAILABLE = False

class MiClase:
    def __init__(self):
        # Conectar al ESP32 automáticamente
        self.esp32_client = None
        if ESP32_AVAILABLE:
            if connect_to_esp32():
                self.esp32_client = get_esp32_client()
                print("✅ Conectado al ESP32")
    
    def ejecutar_comandos(self):
        if self.esp32_client and self.esp32_client.is_connected():
            # Enviar comandos al ESP32
            self.esp32_client.send_speech("¡Hola estudiantes!")
            self.esp32_client.send_gesture('wave', {'intensity': 0.8})
            self.esp32_client.send_movement('arm', {'x': 0, 'y': 45, 'z': 90})
```

### Funciones de Conveniencia
El sistema proporciona funciones de conveniencia para uso directo:

```python
from esp32_client import (
    send_esp32_command,
    send_esp32_movement,
    send_esp32_gesture,
    send_esp32_speech,
    connect_to_esp32
)

# Conectar automáticamente
if connect_to_esp32():
    # Enviar comandos
    send_esp32_speech("¡Hola!")
    send_esp32_gesture('wave', {'intensity': 0.8})
    send_esp32_movement('arm', {'x': 0, 'y': 45, 'z': 90})
```

## Configuración del Sistema

### 1. Crear Configuración Inicial
```python
from esp32_config_binary import ESP32BinaryConfig, ESP32Config

config_manager = ESP32BinaryConfig()

# Crear configuración por defecto
config = config_manager.create_default_config()

# Personalizar configuración
config.host = "192.168.1.100"
config.port = 80
config.timeout = 5.0
config.enable_control = True

# Guardar configuración
config_manager.save_config(config)
```

### 2. Probar Conexión
```python
# Probar conexión usando configuración guardada
if config_manager.test_connection():
    print("✅ Conexión exitosa")
else:
    print("❌ Conexión fallida")
```

### 3. Exportar/Importar Configuración
```python
# Exportar a JSON
config_manager.export_to_json("esp32_config.json")

# Importar desde JSON
config_manager.import_from_json("esp32_config.json")
```

## Integración con Sequence Executor

El `SequenceExecutor` ahora puede usar el cliente ESP32 real:

```python
from sequence_executor_with_logging import SequenceExecutor

# Crear secuencia
sequence_data = {
    'name': 'Demo_ESP32',
    'steps': [
        {
            'action': 'saludo',
            'parameters': {'message': '¡Hola!'}
        },
        {
            'action': 'movimiento',
            'parameters': {'part': 'arm', 'x': 0, 'y': 45}
        }
    ]
}

# Ejecutar con ESP32 real
executor = SequenceExecutor(sequence_data, enable_logging=True)
executor.execute_sequence()  # Usará cliente ESP32 si está disponible
```

## Comandos Disponibles

### Movimiento
```python
coordinates = {'x': 0, 'y': 45, 'z': 90}
client.send_movement('arm', coordinates, duration=1.0)
```

### Gestos
```python
client.send_gesture('wave', {'intensity': 0.8}, duration=2.0)
client.send_gesture('thumbs_up', {'arm': 'right'}, duration=1.5)
```

### Habla
```python
client.send_speech("¡Hola! Soy el robot ADAI")
client.send_speech("Mensaje", {'voice': 'default', 'speed': 1.0})
```

### Acciones Personalizadas
```python
client.send_action('custom_action', {'param1': 'value1'})
```

## Manejo de Errores

El sistema incluye manejo robusto de errores:

```python
try:
    if connect_to_esp32():
        send_esp32_speech("Comando exitoso")
    else:
        print("⚠️ No se pudo conectar al ESP32")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Logging y Monitoreo

### Logs de Señales ESP32
El sistema genera logs detallados de todas las señales enviadas:

```
🎯 SEÑAL ESP32 #1 [SPEECH] - 0.003s
   📋 Paso: Saludo
   📝 Descripción: Mensaje de bienvenida
   ⚙️ Parámetros:
      message: ¡Hola! Bienvenidos
      voice_params: default
```

### Estado de Conexión
```python
# Obtener estado actual
status = client.get_status()
print(f"Estado: {status}")

# Verificar conexión
if client.is_connected():
    print("✅ Conectado al ESP32")
```

## Archivos Generados

El sistema genera los siguientes archivos:

- `esp32_config.bin`: Configuración binaria principal
- `esp32_config.json`: Configuración exportada (opcional)
- `logs/esp32_signals/`: Logs de señales ESP32
- `logs/esp32_signals/esp32_signals_[sequence]_[timestamp].log`: Logs específicos

## Pruebas del Sistema

Ejecutar el script de prueba completo:

```bash
python test_esp32_binary_system.py
```

Este script prueba:
1. Configuración binaria ESP32
2. Cliente ESP32
3. Sequence Executor con ESP32
4. Clase con ESP32

## Ventajas del Sistema

### 1. Configuración Centralizada
- Un solo archivo de configuración para todas las clases
- Fácil actualización de parámetros de conexión
- No necesidad de configurar cada clase individualmente

### 2. Conexión Automática
- Las clases se conectan automáticamente al ESP32
- Manejo transparente de reconexión
- Fallback a simulación si no hay conexión

### 3. Comandos Reales
- Las clases pueden enviar comandos reales al ESP32
- Logging completo de todas las señales
- Integración con el sistema de secuencias

### 4. Flexibilidad
- Funciona con o sin ESP32 conectado
- Configuración personalizable
- Exportación/importación de configuración

## Ejemplo Completo de Clase

```python
#!/usr/bin/env python3
"""
Ejemplo de clase usando el sistema ESP32 binario
"""

import time
import sys
import os

# Agregar directorio padre al path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from esp32_client import get_esp32_client, connect_to_esp32
    from class_progress_reporter import create_progress_reporter
    ESP32_AVAILABLE = True
    PROGRESS_AVAILABLE = True
except ImportError:
    ESP32_AVAILABLE = False
    PROGRESS_AVAILABLE = False

class ClaseEjemplo:
    def __init__(self):
        print("🎓 Clase Ejemplo iniciada")
        
        # Conectar al ESP32
        self.esp32_client = None
        if ESP32_AVAILABLE:
            if connect_to_esp32():
                self.esp32_client = get_esp32_client()
                print("✅ Conectado al ESP32")
            else:
                print("⚠️ No se pudo conectar al ESP32")
        
        # Crear reporter de progreso
        if PROGRESS_AVAILABLE:
            self.reporter = create_progress_reporter("clase_ejemplo", "default", 3)
        else:
            self.reporter = None
    
    def ejecutar_clase(self):
        """Ejecutar la clase con comandos ESP32"""
        try:
            print("🚀 Ejecutando clase ejemplo...")
            
            # Fase 1: Introducción
            if self.reporter:
                self.reporter.start_phase("class_intro", "Introducción", "Iniciando clase")
            
            # Comando ESP32: Saludo
            if self.esp32_client and self.esp32_client.is_connected():
                self.esp32_client.send_speech("¡Hola! Bienvenidos a la clase ejemplo")
                self.esp32_client.send_gesture('wave', {'intensity': 0.8})
            
            time.sleep(2)
            
            # Fase 2: Contenido
            if self.reporter:
                self.reporter.complete_phase("theory_presentation", "Contenido", "Explicando teoría")
            
            # Comando ESP32: Movimiento
            if self.esp32_client and self.esp32_client.is_connected():
                coordinates = {'x': 0, 'y': 45, 'z': 90}
                self.esp32_client.send_movement('arm', coordinates, 1.5)
            
            time.sleep(2)
            
            # Fase 3: Cierre
            if self.reporter:
                self.reporter.complete_phase("completed", "Cierre", "Finalizando clase")
            
            # Comando ESP32: Despedida
            if self.esp32_client and self.esp32_client.is_connected():
                self.esp32_client.send_speech("¡Gracias por su atención!")
                self.esp32_client.send_gesture('thumbs_up', {'arm': 'right'})
            
            print("✅ Clase completada exitosamente")
            
        except Exception as e:
            print(f"❌ Error ejecutando clase: {e}")

if __name__ == "__main__":
    clase = ClaseEjemplo()
    clase.ejecutar_clase()
```

## Conclusión

El sistema de configuración binaria ESP32 proporciona una solución completa y robusta para que las clases se conecten automáticamente al ESP32 y envíen comandos reales durante su ejecución. El sistema es flexible, fácil de usar y proporciona logging completo de todas las operaciones.
