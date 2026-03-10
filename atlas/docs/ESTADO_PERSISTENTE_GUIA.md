# Guía de Estado Persistente - Administrador de Clases

## Descripción

Se ha implementado un sistema completo de gestión de estado persistente para el administrador de clases que mantiene el estado cuando navegas entre páginas. El estado se guarda automáticamente en `localStorage` y se restaura al volver a la aplicación.

## Componentes del Sistema

### 1. ClassesStateManager (`src/services/ClassesStateManager.js`)

**Propósito**: Gestiona la persistencia del estado de clases en localStorage.

**Características**:
- Almacena automáticamente el estado en localStorage
- Proporciona eventos para notificar cambios de estado
- Incluye métodos para importar/exportar estado
- Maneja estadísticas del estado

**Estado que persiste**:
- `selectedClass`: Clase seleccionada actualmente
- `isPlaying`: Si una clase está ejecutándose
- `isConnected`: Estado de conexión con el robot
- `classes`: Lista completa de clases disponibles
- `classProgress`: Progreso de la clase actual
- `lastLoaded`: Timestamp de la última carga

### 2. useClassesState Hook (`src/services/useClassesState.js`)

**Propósito**: Hook de React para acceso reactivo al estado de clases.

**Hooks disponibles**:
- `useClassesState()`: Estado completo de clases
- `useClassesLoader()`: Carga de clases desde la API del robot
- `useClassControl()`: Control de inicio/parada de clases

**Características**:
- Estado reactivo que se actualiza automáticamente
- Métodos para modificar el estado
- Valores computados (totalClasses, runningClasses, etc.)
- Manejo de errores y estados de carga

### 3. GlobalStateProvider (`src/services/GlobalStateProvider.jsx`)

**Propósito**: Proveedor de estado global que inicializa y mantiene el estado en toda la aplicación.

**Características**:
- Inicializa el estado global al cargar la aplicación
- Proporciona hooks para acceso al estado global
- Combina estado de clases y configuración
- Logging para debugging

## Cómo Funciona

### 1. Inicialización
```javascript
// Al cargar la aplicación, el GlobalStateProvider inicializa el estado
<GlobalStateProvider>
  <App />
</GlobalStateProvider>
```

### 2. Persistencia Automática
```javascript
// Cualquier cambio en el estado se guarda automáticamente
const { setSelectedClass, setIsPlaying } = useClassesState()

// Estos cambios se persisten automáticamente
setSelectedClass('mi-clase')
setIsPlaying(true)
```

### 3. Restauración del Estado
```javascript
// Al volver a la página de clases, el estado se restaura automáticamente
const { selectedClass, isPlaying, classes } = useClassesState()
// El estado se mantiene igual que cuando saliste de la página
```

## Uso en Componentes

### Acceso Básico al Estado
```javascript
import { useClassesState } from '../services/useClassesState'

function MiComponente() {
  const { 
    selectedClass, 
    isPlaying, 
    classes, 
    totalClasses 
  } = useClassesState()
  
  // El estado se mantiene al navegar entre páginas
}
```

### Control de Clases
```javascript
import { useClassControl } from '../services/useClassesState'

function ControlComponent() {
  const { handleStartClass, handleStopClass } = useClassControl()
  
  // Los métodos mantienen el estado persistente
  const startClass = () => handleStartClass('mi-clase')
  const stopClass = () => handleStopClass()
}
```

### Estado Global
```javascript
import { useGlobalState } from '../services/GlobalStateProvider'

function GlobalComponent() {
  const { classes, config, global } = useGlobalState()
  
  // Acceso a todo el estado de la aplicación
  console.log('Clase activa:', global.isAnyClassActive)
  console.log('Robot conectado:', global.isRobotConnected)
}
```

## Beneficios

### 1. **Persistencia Transparente**
- El estado se mantiene automáticamente sin código adicional
- No necesitas manejar localStorage manualmente
- Los cambios se guardan inmediatamente

### 2. **Navegación Sin Pérdida**
- Puedes navegar entre páginas sin perder el estado
- La clase seleccionada se mantiene
- El progreso de la clase se conserva

### 3. **Estado Reactivo**
- Los componentes se actualizan automáticamente
- Cambios en una página se reflejan en otras
- Eventos de estado para sincronización

### 4. **Debugging y Monitoreo**
- Logs detallados de cambios de estado
- Estadísticas del estado actual
- Exportación/importación de estado

## Casos de Uso

### 1. **Navegación Durante Clase Activa**
```javascript
// Usuario inicia una clase
handleStartClass('matematicas-basicas')

// Usuario navega a otra página
// El estado se mantiene: isPlaying=true, selectedClass='matematicas-basicas'

// Usuario regresa a la página de clases
// Ve la clase activa y puede detenerla
```

### 2. **Recarga de Página**
```javascript
// Usuario recarga la página durante una clase
// El estado se restaura desde localStorage
// La clase continúa mostrándose como activa
```

### 3. **Múltiples Pestañas**
```javascript
// Usuario abre la app en múltiples pestañas
// El estado se sincroniza entre pestañas
// Cambios en una pestaña se reflejan en otras
```

## Configuración de Almacenamiento

### Claves de localStorage
- `classes_selected_class`: Clase seleccionada
- `classes_is_playing`: Estado de reproducción
- `classes_is_connected`: Estado de conexión
- `classes_list`: Lista de clases
- `classes_progress`: Progreso de la clase
- `classes_last_loaded`: Última carga
- `classes_version`: Versión del estado

### Límites de Almacenamiento
- localStorage tiene límites de tamaño (~5-10MB)
- El estado de clases es pequeño (<1KB típicamente)
- Se incluye validación de errores de almacenamiento

## Troubleshooting

### Estado No Se Persiste
1. Verificar que localStorage esté disponible
2. Revisar la consola para errores de almacenamiento
3. Verificar que el GlobalStateProvider esté configurado

### Estado No Se Restaura
1. Verificar que las claves de localStorage existan
2. Revisar la versión del estado
3. Usar `forceRefresh()` para recargar desde localStorage

### Debugging
```javascript
// Ver estado actual
const state = useClassesState()
console.log('Estado actual:', state)

// Exportar estado para debugging
const exported = state.exportState()
console.log('Estado exportado:', exported)

// Forzar recarga del estado
state.forceRefresh()
```

## Migración

### De Estado Local a Persistente
```javascript
// ANTES: Estado local que se pierde al navegar
const [selectedClass, setSelectedClass] = useState(null)

// DESPUÉS: Estado persistente que se mantiene
const { selectedClass, setSelectedClass } = useClassesState()
```

### Integración con Componentes Existentes
```javascript
// Reemplazar useState local con hooks de estado persistente
import { useClassesState } from '../services/useClassesState'

// El resto del código permanece igual
const { classes, isPlaying } = useClassesState()
```

## Conclusión

El sistema de estado persistente garantiza que el administrador de clases mantenga su estado al navegar entre páginas, proporcionando una experiencia de usuario fluida y consistente. El estado se guarda automáticamente y se restaura transparentemente, sin requerir cambios en el código de los componentes existentes.
