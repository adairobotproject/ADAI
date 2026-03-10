# Guía de Barras de Progreso en la Aplicación Móvil

## 📱 Descripción General

Las barras de progreso en la aplicación móvil permiten a los usuarios ver en tiempo real el progreso de las clases que está ejecutando el robot. Esta funcionalidad se integra con el sistema de progreso del `robot_gui` y proporciona una experiencia visual intuitiva.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **ClassProgressBar.jsx** - Componente reutilizable para mostrar el progreso
2. **ClassesScreen.jsx** - Pantalla principal que integra las barras de progreso
3. **RobotAPI.js** - Servicio que comunica con el robot_gui
4. **App.css** - Estilos para las barras de progreso

### Flujo de Datos

```
Mobile App → RobotAPI → robot_gui → ClassProgressManager → Mobile App
```

## 🎨 Características Visuales

### Barra de Progreso Principal
- **Colores dinámicos**: Cambian según el porcentaje de progreso
  - 🔴 Rojo (0-30%): Inicio de la clase
  - 🟡 Amarillo (30-70%): Desarrollo de la clase
  - 🔵 Azul (70-100%): Finalización de la clase
- **Animación shimmer**: Efecto de brillo que se mueve a través de la barra
- **Transiciones suaves**: Cambios de ancho y color con animaciones

### Información Mostrada
- **Icono de fase**: Emoji que representa la fase actual
- **Porcentaje de progreso**: Número exacto de completado
- **Tiempo transcurrido**: Formato MM:SS
- **Tiempo restante**: Estimación del tiempo faltante
- **Estado actual**: Descripción de la fase en curso

## 🔧 Implementación Técnica

### ClassProgressBar Component

```jsx
<ClassProgressBar 
  className={selectedClass}
  isActive={isPlaying}
  onProgressUpdate={setClassProgress}
/>
```

**Props:**
- `className`: Nombre de la clase en ejecución
- `isActive`: Estado de ejecución (true/false)
- `onProgressUpdate`: Callback para actualizar el estado del progreso

### Actualización Automática

- **Intervalo**: Cada 2 segundos
- **Condición**: Solo cuando hay una clase activa
- **Cleanup**: Se limpia automáticamente al desmontar el componente

### Manejo de Estados

```javascript
const [progress, setProgress] = useState(null)
const [loading, setLoading] = useState(false)
```

## 📊 Fases de Clase Soportadas

### Fases Estándar
- **⏳ not_started**: Clase no iniciada
- **🚀 initialization**: Inicialización
- **📖 presentation**: Presentación
- **💡 explanation**: Explicación
- **🎯 demonstration**: Demostración
- **🤝 interaction**: Interacción
- **✍️ practice**: Práctica
- **📝 evaluation**: Evaluación
- **📋 summary**: Resumen
- **✅ completion**: Completado
- **❌ error**: Error
- **⏸️ paused**: Pausado

### Fases por Tipo de Clase

#### Clases Experimentales
1. Preparación de materiales
2. Explicación del experimento
3. Ejecución del experimento
4. Observación de resultados
5. Análisis de datos
6. Conclusiones

#### Clases Teóricas
1. Introducción al tema
2. Desarrollo del contenido
3. Ejemplos prácticos
4. Preguntas y respuestas
5. Resumen y conclusiones

## 🎯 Funcionalidades

### 1. Visualización en Tiempo Real
- Actualización automática cada 2 segundos
- Indicadores visuales de progreso
- Información detallada de la fase actual

### 2. Responsive Design
- Adaptación a diferentes tamaños de pantalla
- Layout optimizado para móviles
- Controles táctiles intuitivos

### 3. Integración con Robot GUI
- Comunicación bidireccional con el robot
- Sincronización de estados
- Manejo de errores robusto

### 4. Experiencia de Usuario
- Feedback visual inmediato
- Información contextual relevante
- Interfaz limpia y moderna

## 🚀 Uso de la Aplicación

### 1. Iniciar una Clase
1. Navegar a la pantalla "Clases"
2. Seleccionar una clase disponible
3. Tocar "Iniciar Clase"
4. La barra de progreso aparecerá automáticamente

### 2. Monitorear el Progreso
- La barra se actualiza automáticamente
- Ver el porcentaje de completado
- Observar el tiempo transcurrido
- Identificar la fase actual

### 3. Detener una Clase
- Tocar el botón "Detener" en el banner
- La barra de progreso desaparecerá
- El estado se reseteará

## 🔍 Solución de Problemas

### Problema: Barra de Progreso No Aparece
**Causas posibles:**
- No hay clase activa
- Error de conexión con el robot
- Problema en la API de progreso

**Soluciones:**
1. Verificar conexión con el robot
2. Revisar logs de la aplicación
3. Reiniciar la aplicación móvil

### Problema: Progreso No Se Actualiza
**Causas posibles:**
- Problema de red
- Error en el robot_gui
- Intervalo de actualización interrumpido

**Soluciones:**
1. Verificar conectividad de red
2. Revisar estado del robot_gui
3. Reiniciar la clase

### Problema: Información Incorrecta
**Causas posibles:**
- Desincronización entre móvil y robot
- Error en el ClassProgressManager
- Datos corruptos

**Soluciones:**
1. Detener y reiniciar la clase
2. Verificar logs del robot_gui
3. Reiniciar ambos sistemas

## 📱 Compatibilidad

### Dispositivos Soportados
- **iOS**: iPhone 6s y posteriores
- **Android**: Android 6.0 y posteriores
- **Web**: Navegadores modernos

### Resoluciones Optimizadas
- **Móvil**: 375px - 414px de ancho
- **Tablet**: 768px - 1024px de ancho
- **Desktop**: 1024px y superior

## 🔄 Actualizaciones Futuras

### Funcionalidades Planificadas
1. **Notificaciones push**: Alertas de progreso
2. **Historial de clases**: Registro de clases completadas
3. **Estadísticas avanzadas**: Métricas detalladas
4. **Personalización**: Temas y colores personalizables

### Mejoras Técnicas
1. **WebSocket**: Comunicación en tiempo real
2. **Cache local**: Almacenamiento offline
3. **Sincronización**: Múltiples dispositivos
4. **Analytics**: Métricas de uso

## 📚 Recursos Adicionales

### Archivos Relacionados
- `ClassProgressBar.jsx`: Componente principal
- `ClassesScreen.jsx`: Integración en pantalla
- `RobotAPI.js`: Comunicación con robot
- `App.css`: Estilos y animaciones

### Documentación Técnica
- `GUIA_SISTEMA_PROGRESO.md`: Sistema de progreso del robot
- `RESUMEN_SISTEMA_PROGRESO.md`: Resumen del sistema
- `test_progress_mobile.js`: Script de pruebas

### APIs Utilizadas
- `GET /api/class/progress`: Obtener progreso actual
- `POST /api/class/execute`: Ejecutar clase
- `POST /api/class/stop`: Detener clase

## ✅ Estado del Sistema

**Estado**: ✅ **COMPLETAMENTE IMPLEMENTADO**

**Funcionalidades activas:**
- ✅ Barras de progreso visuales
- ✅ Actualización automática
- ✅ Integración con robot_gui
- ✅ Diseño responsive
- ✅ Manejo de errores
- ✅ Documentación completa

**Próximos pasos:**
1. Probar en dispositivos reales
2. Optimizar rendimiento
3. Implementar funcionalidades adicionales
