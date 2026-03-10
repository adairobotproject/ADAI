# Guía de Demo de Química - Neutralización de Ácido

## Resumen

Esta guía explica cómo usar el sistema de demostración de química para neutralización de ácido con el robot ADAI. El sistema incluye scripts Python y secuencias JSON que controlan el robot de manera segura para realizar demostraciones educativas.

## Archivos del Sistema

### 1. Scripts Python

#### `demo_clase_quimica_neutralizacion.py`
- **Propósito**: Controlador principal del robot para demo de química
- **Funcionalidades**:
  - Conexión con ESP32
  - Validación de límites de seguridad
  - Control de brazos, cuello, manos y muñecas
  - Demo completa automática
  - Demo interactiva con pausas
  - Modo simulación (sin conexión real)

#### `ejecutar_secuencia_quimica.py`
- **Propósito**: Ejecutor de secuencias JSON
- **Funcionalidades**:
  - Carga de secuencias desde archivos JSON
  - Ejecución paso a paso
  - Control de progreso
  - Modo interactivo
  - Pausa/reanudación

### 2. Secuencias JSON

#### `sequences/sequence_Quimica_Neutralizacion_Completa.json`
- **Propósito**: Definición completa de la demo de neutralización
- **Contenido**:
  - 10 movimientos principales
  - 50+ acciones individuales
  - Límites de seguridad
  - Objetivos educativos
  - Materiales necesarios

## Límites de Seguridad del Robot

### Brazos (ESP32 → Mega)
```
BI (Brazo Izquierdo): 10-30 grados
FI (Frente Izquierdo): 60-120 grados
HI (High Izquierdo): 70-90 grados
BD (Brazo Derecho): 30-55 grados
FD (Frente Derecho): 70-110 grados
HD (High Derecho): 70-90 grados
PD (Pollo Derecho): 0-90 grados
```

### Cuello (ESP32 → Mega)
```
L (Lateral): 120-160 grados
I (Inferior): 60-130 grados
S (Superior): 109-110 grados
```

### Manos y Dedos (ESP32 → Mega → UNO)
```
Dedos: 0-180 grados
Muñecas: 0-160 grados
```

## Comandos ESP32 Utilizados

### Control de Brazos
```python
# Ejemplo de comando
"BRAZOS BI=10 FI=80 HI=80 BD=40 FD=90 HD=80 PD=45"
```

### Control de Cuello
```python
# Ejemplo de comando
"CUELLO L=155 I=95 S=110"
```

### Control de Manos
```python
# Ejemplo de comando
"MANO M=derecha GESTO=SALUDO"
```

### Control de Muñecas
```python
# Ejemplo de comando
"MUNECA M=derecha ANG=80"
```

### Hablar
```python
# Ejemplo de comando
"HABLAR texto=¡Hola estudiantes!"
```

## Estructura de la Secuencia JSON

### Formato General
```json
{
  "name": "Nombre_secuencia",
  "title": "Título descriptivo",
  "description": "Descripción detallada",
  "created_at": "2025-01-27T10:00:00.000000",
  "version": "1.0",
  "author": "ADAI Class Builder",
  "subject": "Química",
  "duration_minutes": 15,
  "safety_mode": true,
  "movements": [...],
  "total_duration": 900000,
  "safety_notes": [...],
  "educational_objectives": [...],
  "materials_needed": [...]
}
```

### Estructura de Movimientos
```json
{
  "id": 1,
  "name": "Nombre del movimiento",
  "type": "tipo_movimiento",
  "description": "Descripción del movimiento",
  "actions": [
    {
      "command": "COMANDO",
      "parameters": {
        "param1": "valor1",
        "param2": "valor2"
      },
      "duration": 1000,
      "description": "Descripción de la acción"
    }
  ]
}
```

## Instalación y Configuración

### 1. Requisitos
```bash
pip install requests
```

### 2. Configuración del ESP32
- Asegúrate de que el ESP32 esté conectado a la red WiFi
- Anota la IP del ESP32 (por defecto: 192.168.1.100)
- Verifica que el servidor web esté funcionando

### 3. Verificación de Conexión
```bash
# Probar conexión al ESP32
curl http://192.168.1.100/
```

## Uso del Sistema

### 1. Demo Completa Automática

#### Usando el script principal:
```bash
python demo_clase_quimica_neutralizacion.py
```

#### Opciones disponibles:
1. **Demo Completa Automática**: Ejecuta toda la demo sin interrupciones
2. **Demo Interactiva**: Pausa entre secciones para preguntas
3. **Solo Saludo**: Ejecuta solo el saludo inicial
4. **Solo Demostración de Reactivos**: Muestra los reactivos
5. **Solo Neutralización**: Ejecuta la reacción
6. **Posición de Descanso**: Vuelve a posición segura

### 2. Ejecución de Secuencia JSON

#### Usando el ejecutor de secuencias:
```bash
python ejecutar_secuencia_quimica.py
```

#### Opciones disponibles:
1. **Ejecutar Secuencia Completa**: Ejecuta toda la secuencia
2. **Ejecutar Modo Interactivo**: Control manual de cada movimiento
3. **Ver Progreso**: Muestra el progreso actual
4. **Pausar/Reanudar**: Control de ejecución
5. **Detener**: Detiene la ejecución

### 3. Modo Simulación

Si no hay conexión al ESP32, el sistema funciona en modo simulación:
- Los comandos se muestran en consola
- No se envían comandos reales al robot
- Útil para pruebas y desarrollo

## Flujo de la Demo de Neutralización

### 1. Inicialización (Movimiento 1)
- Posición de descanso inicial
- Configuración de cuello central
- Manos en posición de descanso

### 2. Saludo Inicial (Movimiento 2)
- Saludo verbal a los estudiantes
- Gesto de saludo con brazo derecho
- Movimientos de saludo repetitivos

### 3. Introducción al Tema (Movimiento 3)
- Explicación del tema de neutralización
- Gestos de explicación
- Movimientos de cuello para mirar reactivos

### 4. Demostración de Reactivos (Movimiento 4)
- Presentación de ácido clorhídrico y bicarbonato
- Gestos de señalar reactivos
- Advertencias de seguridad

### 5. Preparación del Experimento (Movimiento 5)
- Explicación del proceso de preparación
- Gestos de preparación
- Simulación de colocación de reactivos

### 6. Realización de la Neutralización (Movimiento 6)
- Explicación del proceso de neutralización
- Gestos de agregar gota a gota
- Observación de la reacción
- Confirmación de éxito

### 7. Explicación de Resultados (Movimiento 7)
- Explicación de la reacción química
- Mostrar ecuación química
- Gestos de escribir en pizarra

### 8. Conclusión y Despedida (Movimiento 8)
- Conclusión principal
- Recordatorio de seguridad
- Gestos de despedida

### 9. Saludo Final (Movimiento 9)
- Saludo final de despedida
- Gestos de saludo

### 10. Posición Final de Descanso (Movimiento 10)
- Vuelta a posición de descanso segura
- Configuración final de todos los componentes

## Objetivos Educativos

1. **Comprender el concepto de neutralización química**
2. **Identificar los reactivos y productos de la reacción**
3. **Reconocer la importancia de la seguridad en el laboratorio**
4. **Apreciar la aplicación práctica de las reacciones químicas**
5. **Desarrollar habilidades de observación científica**

## Materiales Necesarios

- Ácido clorhídrico (HCl) diluido
- Bicarbonato de sodio (NaHCO3)
- Matraz Erlenmeyer
- Equipo de protección personal
- Indicador de pH
- Agitador magnético

## Ecuación Química

```
HCl + NaHCO3 → NaCl + H2O + CO2
```

**Tipo de reacción**: Neutralización ácido-base
**Cambio de pH**: De ácido a neutro

## Observaciones Esperadas

1. **Formación de burbujas (CO2)**
2. **Cambio de pH**
3. **Formación de sal (NaCl)**
4. **Liberación de calor**

## Solución de Problemas

### Error de Conexión al ESP32
```
❌ Error conectando al ESP32: [Errno 111] Connection refused
```
**Solución**: Verificar que el ESP32 esté encendido y conectado a la red

### Comandos No Reconocidos
```
❌ Error ejecutando comando: HTTP 404
```
**Solución**: Verificar que el endpoint `/api/command` esté disponible en el ESP32

### Valores Fuera de Límites
```
❌ Valor fuera de límites seguros: BI=50 (rango: 10-30)
```
**Solución**: Revisar los valores en la secuencia JSON y ajustar a los límites seguros

### Archivo de Secuencia No Encontrado
```
❌ Archivo de secuencia no encontrado: sequences/sequence_Quimica_Neutralizacion_Completa.json
```
**Solución**: Verificar que el archivo JSON esté en la ubicación correcta

## Personalización

### Crear Nueva Secuencia

1. **Copiar la secuencia base**:
```bash
cp sequences/sequence_Quimica_Neutralizacion_Completa.json sequences/mi_nueva_secuencia.json
```

2. **Modificar los parámetros**:
- Cambiar título y descripción
- Ajustar movimientos y acciones
- Modificar duraciones
- Actualizar objetivos educativos

3. **Validar límites de seguridad**:
- Verificar que todos los valores estén dentro de los rangos seguros
- Probar en modo simulación primero

### Agregar Nuevos Comandos

1. **En el ESP32**: Implementar el nuevo endpoint
2. **En el script Python**: Agregar método para el nuevo comando
3. **En la secuencia JSON**: Usar el nuevo comando en las acciones

## Seguridad

### Límites Automáticos
- Todos los movimientos se validan contra los límites de seguridad
- El sistema rechaza comandos fuera de rango
- Posiciones de descanso seguras entre movimientos

### Modo de Emergencia
- Presionar Ctrl+C para detener la ejecución
- El robot vuelve automáticamente a posición de descanso
- Verificar estado del robot después de una detención

### Recomendaciones
- Siempre probar en modo simulación primero
- Verificar conexiones antes de ejecutar
- Mantener espacio libre alrededor del robot
- Tener un plan de emergencia

## Desarrollo y Extensión

### Agregar Nuevas Demos
1. Crear nueva secuencia JSON
2. Implementar métodos específicos en el script Python
3. Agregar opciones al menú principal
4. Probar y validar

### Integración con GUI
- Los scripts pueden integrarse con la GUI principal
- Usar callbacks para actualizar progreso
- Implementar controles de pausa/reanudación

### Logging y Monitoreo
- Los scripts incluyen logging detallado
- Monitoreo de progreso en tiempo real
- Registro de errores y eventos

## Conclusión

El sistema de demo de química proporciona una base sólida para crear demostraciones educativas con el robot ADAI. La estructura modular permite fácil personalización y extensión para diferentes temas y experimentos.

La seguridad es prioritaria, con validación automática de límites y posiciones de descanso seguras. El sistema funciona tanto en modo real como en simulación, facilitando el desarrollo y pruebas.

Para más información o soporte, consultar la documentación del robot ADAI y los archivos de configuración del ESP32.
