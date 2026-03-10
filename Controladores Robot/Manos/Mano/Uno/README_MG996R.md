# Controlador UNO - Adaptado para Servo MG996R

## Descripción
Este controlador ha sido adaptado para usar un servo MG996R de alta potencia en la muñeca derecha del robot Atlas. El MG996R proporciona mayor torque y control de velocidad automático.

## Características del MG996R
- **Voltaje de operación**: 4.8V - 7.2V
- **Velocidad**: ~462°/s a 6V, ~353°/s a 4.8V
- **Torque**: 10kg/cm a 6V, 8.5kg/cm a 4.8V
- **Tiempo para 60°**: 130ms (6V) o 170ms (4.8V)
- **Rango seguro**: 20° - 160° (evita daños mecánicos)

## Configuración
```cpp
// Configuración específica para MG996R (muñeca derecha)
const bool MUNECA_DER_ES_MG996R = true;  // Indicador de que usa MG996R
const float MG996R_T60_MS = 130.0;       // Tiempo para 60° a 6V (ajustar según voltaje)
const float MG996R_MARGEN_MS = 50.0;     // Margen de seguridad en ms
int munecaDerAnguloActual = 90;          // Ángulo actual de la muñeca derecha

// Rangos específicos para MG996R (más restrictivos por seguridad)
const int MG996R_MIN = 20;     // Mínimo para evitar daños
const int MG996R_MAX = 160;    // Máximo para evitar daños
```

## Comandos Especiales

### 1. Probar MG996R
```
PROBAR_MG996R
```
Ejecuta una secuencia de prueba: 90° → 40° → 90° → 140° → 90°

### 2. Calcular Tiempo de Movimiento
```
CALCULAR_TIEMPO INICIAL=90 FINAL=40
```
Calcula el tiempo necesario para mover de un ángulo a otro.

## Funciones Especializadas

### setServoMG996R()
- Valida rangos de seguridad específicos del MG996R
- Calcula tiempo de movimiento automáticamente
- Aplica delay dinámico basado en el cambio de ángulo
- Actualiza el ángulo actual del servo

### moverMunecaDerechaMG996R()
- Función de alto nivel para mover la muñeca derecha
- Usa la función especializada del MG996R
- Incluye validaciones de seguridad

## Cálculo de Velocidad

### Fórmula Base
```
tiempo = (Δángulo / 60°) × T60 + margen
```

### Ejemplos de Tiempo
- **90° → 40°** (Δ50°): ~158ms
- **90° → 140°** (Δ50°): ~158ms  
- **0° → 180°** (Δ180°): ~440ms

### Ajustes por Voltaje
- **6V**: T60 = 130ms
- **4.8V**: T60 = 170ms

## Comandos de Muñeca
```
MUNECA M=derecha ANG=90
MUNECA M=derecha ANG=40
MUNECA M=derecha ANG=140
```

## Seguridad
- **Rango restringido**: 20° - 160° (evita daños mecánicos)
- **Validación automática**: Verifica ángulos antes de ejecutar
- **Margen de seguridad**: 50ms adicional para estabilización
- **Control de velocidad**: Tiempo calculado dinámicamente

## Monitoreo
El sistema proporciona información detallada:
- Ángulo de destino
- Tiempo calculado
- Delta de movimiento
- Duty cycle del PWM
- Confirmación de ejecución

## Troubleshooting

### Si el servo no se mueve:
1. Verificar voltaje de alimentación
2. Comprobar conexiones del PWM
3. Verificar rango de ángulos (20°-160°)
4. Revisar configuración T60_MS

### Si el movimiento es muy lento:
1. Ajustar MG996R_T60_MS según voltaje real
2. Reducir MG996R_MARGEN_MS
3. Verificar que no haya carga mecánica excesiva

### Si el movimiento es muy rápido:
1. Aumentar MG996R_MARGEN_MS
2. Verificar que T60_MS sea correcto
3. Comprobar que no haya daños mecánicos

## Ejemplo de Uso Completo
```cpp
// Secuencia de movimiento suave
moverMunecaDerechaMG996R(40);   // Movimiento calculado automáticamente
delay(1000);                     // Pausa para observación
moverMunecaDerechaMG996R(90);   // Retorno a posición central
delay(1000);                     // Pausa para observación
moverMunecaDerechaMG996R(140);  // Movimiento hacia el otro extremo
```

## Notas Importantes
- El MG996R es más potente que servos estándar
- Usar siempre los rangos de seguridad (20°-160°)
- El tiempo de movimiento se calcula automáticamente
- Incluir pausas entre movimientos para estabilización
- Monitorear la temperatura del servo en uso prolongado
