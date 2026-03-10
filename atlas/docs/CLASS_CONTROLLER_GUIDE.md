# 🎮 Class Controller - Guía Completa

## 📋 Descripción General

El **Class Controller** es una nueva pestaña en `robot_gui.py` que permite gestionar y ejecutar tanto las clases generadas por el **Class Builder** como las secuencias creadas por el **Sequence Builder**. Esta funcionalidad centraliza el control de ejecución de todos los elementos programables del robot ADAI.

## 🎯 Funcionalidades Principales

### 📚 **Gestión de Clases**
- **Listado automático** de clases Python generadas
- **Visualización de detalles** del código fuente
- **Eliminación segura** con confirmación
- **Actualización automática** de la lista

### 🎬 **Gestión de Secuencias**
- **Listado de secuencias** guardadas en formato JSON
- **Visualización de datos** de secuencia estructurados
- **Eliminación segura** con confirmación
- **Actualización automática** de la lista

### 🎮 **Control de Ejecución**
- **Ejecución en tiempo real** de clases y secuencias
- **Controles de reproducción**: Iniciar, Pausar, Reanudar, Detener
- **Monitoreo de progreso** con logs en tiempo real
- **Ejecución en hilo separado** sin bloquear la interfaz

## 🖥️ Interfaz de Usuario

### Layout Principal
```
┌─────────────────────────────────────────────────────────────────────┐
│                    🎮 Class & Sequence Controller                   │
├──────────────────┬──────────────────┬──────────────────────────────┤
│  📚 Clases       │  🎬 Secuencias   │      🎮 Control Ejecución    │
│  Disponibles     │  Disponibles     │                              │
│                  │                  │                              │
│ ┌──────────────┐ │ ┌──────────────┐ │ Estado: ⏸️ Inactivo          │
│ │ class1.py    │ │ │ sequence1.js │ │                              │
│ │ thesis_def.py│ │ │ sequence2.js │ │ ○ Ejecutar Clase             │
│ │ present.py   │ │ │ demo_seq.js  │ │ ○ Ejecutar Secuencia         │
│ └──────────────┘ │ └──────────────┘ │                              │
│                  │                  │ ┌─────────────────────────┐  │
│ [🔄][📋][🗑️]    │ [🔄][📋][🗑️]    │ │      ▶️ INICIAR         │  │
│                  │                  │ └─────────────────────────┘  │
│                  │                  │ ┌─────────────────────────┐  │
│                  │                  │ │      ⏸️ PAUSAR          │  │
│                  │                  │ └─────────────────────────┘  │
│                  │                  │ ┌─────────────────────────┐  │
│                  │                  │ │      ⏹️ DETENER         │  │
│                  │                  │ └─────────────────────────┘  │
│                  │                  │                              │
│                  │                  │ Progreso de Ejecución:       │
│                  │                  │ ┌─────────────────────────┐  │
│                  │                  │ │[10:30:15] Cargando...   │  │
│                  │                  │ │[10:30:16] Ejecutando... │  │
│                  │                  │ │[10:30:17] Completado ✅ │  │
│                  │                  │ └─────────────────────────┘  │
└──────────────────┴──────────────────┴──────────────────────────────┘
```

## 🚀 Uso del Class Controller

### 1️⃣ **Ejecutar una Clase**

1. **Seleccionar clase**: Clic en una clase de la lista izquierda
2. **Seleccionar tipo**: Marcar "Ejecutar Clase"
3. **Iniciar ejecución**: Clic en "▶️ INICIAR"
4. **Monitorear progreso**: Ver logs en tiempo real
5. **Controlar ejecución**: Usar PAUSAR/DETENER según necesidad

```python
# Ejemplo de clase ejecutable
class ThesisDefense_Document:
    def __init__(self):
        self.engine = initialize_tts()
    
    def execute(self):
        # Método principal de ejecución
        self.speak("Iniciando defensa de tesis...")
        # ... lógica de la clase
```

### 2️⃣ **Ejecutar una Secuencia**

1. **Seleccionar secuencia**: Clic en una secuencia de la lista central
2. **Seleccionar tipo**: Marcar "Ejecutar Secuencia"
3. **Iniciar ejecución**: Clic en "▶️ INICIAR"
4. **Monitorear progreso**: Ver posiciones ejecutándose
5. **Controlar ejecución**: Usar PAUSAR/DETENER según necesidad

```json
// Ejemplo de estructura de secuencia
{
  "name": "Demo Sequence",
  "positions": [
    {
      "esp32_data": {
        "neck_yaw": 90,
        "neck_pitch": 45,
        "left_shoulder": 60
      },
      "duration": 2.0
    }
  ]
}
```

## 🎛️ Controles de Ejecución

### ▶️ **Botón INICIAR**
- **Función**: Inicia la ejecución del elemento seleccionado
- **Estado**: Se desactiva durante ejecución
- **Requisito**: Debe tener un elemento seleccionado

### ⏸️ **Botón PAUSAR/REANUDAR**
- **Función**: Pausa o reanuda la ejecución en curso
- **Estado**: Cambia entre "PAUSAR" y "REANUDAR"
- **Disponible**: Solo durante ejecución activa

### ⏹️ **Botón DETENER**
- **Función**: Detiene completamente la ejecución
- **Estado**: Se desactiva cuando no hay ejecución
- **Efecto**: Cancela la ejecución y resetea el estado

## 📊 Estados de Ejecución

| Estado | Descripción | Color | Acciones Disponibles |
|--------|-------------|-------|---------------------|
| ⏸️ Inactivo | Sin ejecución en curso | 🟡 Amarillo | INICIAR |
| ▶️ Ejecutando | Ejecución en progreso | 🟢 Verde | PAUSAR, DETENER |
| ⏸️ Pausado | Ejecución pausada | 🟠 Naranja | REANUDAR, DETENER |
| ⏹️ Detenido | Ejecución cancelada | 🔴 Rojo | INICIAR (después de 2s) |

## 🔧 Funciones de Gestión

### 📚 **Gestión de Clases**

#### 🔄 Actualizar Lista
```python
def refresh_available_classes(self):
    # Busca archivos *.py con keywords específicos
    keywords = ['thesis', 'defense', 'presentation', 'class_']
    # Actualiza listbox automáticamente
```

#### 📋 Ver Detalles
- **Abre ventana emergente** con código fuente completo
- **Editor de solo lectura** con syntax highlighting
- **Scrollbar vertical** para archivos largos

#### 🗑️ Eliminar Clase
- **Confirmación obligatoria** antes de eliminar
- **Eliminación del archivo** del sistema de archivos
- **Actualización automática** de la lista

### 🎬 **Gestión de Secuencias**

#### 🔄 Actualizar Lista
```python
def refresh_available_sequences(self):
    # Busca archivos sequence_*.json en directorio sequences/
    # Actualiza listbox automáticamente
```

#### 📋 Ver Detalles
- **Muestra estructura JSON** formateada
- **Datos de posiciones** con indentación
- **Información de duración** y metadatos

#### 🗑️ Eliminar Secuencia
- **Confirmación obligatoria** antes de eliminar
- **Eliminación del archivo JSON** del directorio sequences/
- **Actualización automática** de la lista

## 🔄 Integración con ESP32

### Ejecución de Secuencias
```python
# Envío automático de posiciones al ESP32
if hasattr(self, 'esp32_connector') and self.esp32_connector.is_connected:
    esp32_data = position.get('esp32_data', {})
    if esp32_data:
        self.esp32_connector.send_position_data(esp32_data)
        self.log_controller_message("✅ Posición enviada al ESP32")
```

### Verificación de Conexión
- **Detección automática** de ESP32 conectado
- **Envío condicional** de comandos
- **Logs informativos** del estado de conexión

## 📝 Sistema de Logging

### Formato de Logs
```
[HH:MM:SS] Mensaje de estado
[10:30:15] Cargando clase: thesis_defense.py
[10:30:16] ✅ Clase cargada: ThesisDefense
[10:30:17] 🚀 Ejecutando método: execute
[10:30:18] Progreso: 50.0% - Paso 5/10
[10:30:19] ✅ Ejecución de clase completada
```

### Tipos de Mensajes
- **ℹ️ Información**: Estado general y progreso
- **✅ Éxito**: Operaciones completadas exitosamente
- **⚠️ Advertencia**: Problemas no críticos
- **❌ Error**: Errores que impiden la ejecución

## 🛠️ Configuración y Personalización

### Directorios de Búsqueda
```python
# Clases: Directorio actual (*.py)
class_files = glob.glob("*.py")

# Secuencias: Directorio sequences/ (sequence_*.json)
sequences_dir = "sequences"
sequence_files = glob.glob(os.path.join(sequences_dir, "sequence_*.json"))
```

### Filtros de Clases
```python
# Keywords para identificar clases generadas
keywords = ['thesis', 'defense', 'presentation', 'class_']
```

### Límites de Logging
```python
# Máximo 100 líneas en el log (para evitar uso excesivo de memoria)
if len(lines) > 100:
    self.execution_progress.delete("1.0", f"{len(lines) - 100}.0")
```

## 🚨 Manejo de Errores

### Errores de Carga
- **Archivos no encontrados**: Mensaje informativo
- **Errores de sintaxis**: Detalles específicos del error
- **Clases no ejecutables**: Búsqueda automática de métodos

### Errores de Ejecución
- **Exceptions capturadas**: Logs detallados del error
- **Estado UI consistente**: Reset automático en caso de fallo
- **Timeouts de thread**: Límite de 2 segundos para cerrar hilos

### Errores de ESP32
- **Conexión perdida**: Continúa ejecución sin envío
- **Datos inválidos**: Log de advertencia, no detiene ejecución
- **Timeouts**: Reintentos automáticos con límite

## 🎓 Ejemplos de Uso

### Ejemplo 1: Ejecutar Defensa de Tesis
```python
# 1. Generar clase en Class Builder con PDF de tesis
# 2. Ir a Class Controller
# 3. Seleccionar "thesis_defense_document.py"
# 4. Marcar "Ejecutar Clase"
# 5. Clic en INICIAR
# 6. Monitorear progreso de la defensa
```

### Ejemplo 2: Ejecutar Secuencia de Movimientos
```python
# 1. Crear secuencia en Sequence Builder
# 2. Guardar como "demo_presentation.json"
# 3. Ir a Class Controller
# 4. Seleccionar secuencia en lista central
# 5. Marcar "Ejecutar Secuencia"
# 6. INICIAR y ver movimientos del robot
```

### Ejemplo 3: Pausar y Reanudar Ejecución
```python
# Durante cualquier ejecución:
# 1. Clic en PAUSAR (estado cambia a Pausado)
# 2. El robot se detiene inmediatamente
# 3. Clic en REANUDAR (continúa desde donde pausó)
# 4. O clic en DETENER (cancela completamente)
```

## 🔧 Arquitectura Técnica

### Threading
```python
# Ejecución en hilo separado para no bloquear UI
self.controller_execution_thread = threading.Thread(
    target=self._execute_controller_item,
    args=(execution_type, self.current_execution_item),
    daemon=True
)
```

### Estados de Control
```python
# Variables de estado global
self.controller_execution_active = False
self.controller_execution_paused = False
self.controller_execution_thread = None
self.current_execution_item = None
```

### Comunicación UI-Thread
```python
# Uso de root.after() para thread-safe UI updates
self.root.after(0, self._reset_execution_ui)
```

## 📚 API del Controller

### Métodos Principales
- `setup_class_controller_tab()`: Configuración inicial de la pestaña
- `refresh_available_classes()`: Actualizar lista de clases
- `refresh_available_sequences()`: Actualizar lista de secuencias
- `start_execution()`: Iniciar ejecución
- `pause_execution()`: Pausar/reanudar ejecución
- `stop_execution()`: Detener ejecución
- `_execute_controller_item()`: Ejecución en hilo separado
- `log_controller_message()`: Sistema de logging

### Atributos de Estado
- `available_classes_listbox`: Lista de clases disponibles
- `available_sequences_listbox`: Lista de secuencias disponibles
- `controller_status_label`: Etiqueta de estado actual
- `execution_progress`: Widget de texto para logs
- `execution_type_var`: Variable de tipo de ejecución

## 🎉 Beneficios del Class Controller

1. **🎯 Centralización**: Un solo lugar para ejecutar todo
2. **🎮 Control Total**: Pausar, reanudar, detener en cualquier momento
3. **📊 Monitoreo**: Logs en tiempo real del progreso
4. **🔄 Integración**: Funciona con Class Builder y Sequence Builder
5. **🚀 Performance**: Ejecución en hilos separados
6. **🛡️ Seguridad**: Confirmaciones antes de eliminar
7. **🎨 Interfaz**: UI intuitiva y organizada
8. **🔧 Flexibilidad**: Soporte para clases y secuencias
9. **📱 Compatibilidad**: Integración con API móvil
10. **⚡ Eficiencia**: Gestión automática de recursos

## 🏁 Conclusión

El **Class Controller** completa el ecosistema de control del robot ADAI, proporcionando una interfaz unificada para la ejecución de todos los elementos programables. Con su diseño intuitivo y funcionalidades robustas, permite a los usuarios gestionar eficientemente tanto las clases generadas automáticamente como las secuencias de movimientos personalizadas.

### Próximos Pasos
- **Integración con Mobile App**: Control remoto desde la aplicación móvil
- **Scheduling**: Programación de ejecuciones automáticas
- **Playlists**: Cadenas de ejecución de múltiples elementos
- **Analytics**: Estadísticas de uso y performance
- **Backup**: Sistema de respaldo automático de clases y secuencias

