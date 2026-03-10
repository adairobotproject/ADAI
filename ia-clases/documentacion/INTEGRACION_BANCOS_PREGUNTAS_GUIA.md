# 🎯 Guía de Integración de Bancos de Preguntas

## 📋 Resumen

Se ha integrado exitosamente la funcionalidad para usar las preguntas de `demo_sequence_manager.py` en el Class Builder del `robot_gui_conmodulos.py`.

## 🔧 Componentes Implementados

### 1. **Extractor de Bancos de Preguntas**
- **Archivo:** `question_bank_extractor.py`
- **Función:** Extrae automáticamente los bancos de preguntas de `demo_sequence_manager.py`
- **Bancos disponibles:**
  - `QUESTION_BANK` → "Preguntas Generales de Química" (7 preguntas)
  - `QUESTION_BANK_CHEM` → "Preguntas Específicas de Química" (7 preguntas)

### 2. **Interfaz de Usuario en Class Builder**
- **Paso 4:** Nueva sección "❓ Paso 4: Banco de Preguntas"
- **Características:**
  - Dropdown para seleccionar banco de preguntas
  - Vista previa de preguntas seleccionadas
  - Actualización automática al cambiar selección

### 3. **Generación de Código Mejorada**
- **Variables agregadas:**
  - `self.selected_question_bank` - Banco seleccionado
  - `self.available_question_banks` - Bancos disponibles
- **Código generado incluye:**
  - `CUSTOM_QUESTION_BANK` con preguntas seleccionadas
  - Lógica condicional para usar preguntas personalizadas
  - Integración con `RandomQuestionManager`

## 🚀 Funcionalidades

### ✅ **Selección de Bancos de Preguntas**
```python
# Bancos disponibles automáticamente:
available_banks = {
    "Preguntas Generales de Química": [...],
    "Preguntas Específicas de Química": [...]
}
```

### ✅ **Vista Previa de Preguntas**
- Muestra las primeras 10 preguntas del banco seleccionado
- Actualización automática al cambiar selección
- Indicador de preguntas adicionales

### ✅ **Generación de Código Inteligente**
```python
# Código generado incluye:
CUSTOM_QUESTION_BANK = [preguntas_seleccionadas]

# Lógica condicional:
if CUSTOM_QUESTION_BANK:
    print("🎯 Usando preguntas personalizadas")
    question_manager = RandomQuestionManager(current_users, CUSTOM_QUESTION_BANK)
    # Usar preguntas personalizadas
else:
    print("🎯 Usando preguntas por defecto")
    # Usar preguntas por defecto
```

## 📁 Estructura de Archivos

```
ia-clases/
├── question_bank_extractor.py          # Extractor de bancos
├── tabs/
│   └── class_builder_tab_final.py      # Class Builder mejorado
└── clases/main/
    └── demo_sequence_manager.py        # Fuente de preguntas
```

## 🎯 Flujo de Trabajo

### 1. **Carga Automática**
- Al inicializar el Class Builder, se cargan automáticamente los bancos de preguntas
- Se extraen las preguntas de `demo_sequence_manager.py`

### 2. **Selección de Usuario**
- El usuario selecciona el banco de preguntas deseado
- Se muestra una vista previa de las preguntas

### 3. **Generación de Clase**
- El código generado incluye las preguntas seleccionadas
- Se crea un `CUSTOM_QUESTION_BANK` con las preguntas
- Se implementa lógica condicional para usar las preguntas

### 4. **Ejecución de Clase**
- La clase generada usa las preguntas seleccionadas
- Se integra con `RandomQuestionManager` para gestión de preguntas
- Funciona con el sistema de reconocimiento facial

## 🔍 Ejemplos de Preguntas

### **Preguntas Generales de Química:**
1. "La neutralización ocurre cuando un ácido y una base reaccionan. Verdadero o falso?"
2. "El bicarbonato de sodio es una sustancia básica. Verdadero o falso?"
3. "El vinagre contiene ácido acético. Verdadero o falso?"

### **Preguntas Específicas de Química:**
1. "La neutralización produce siempre agua y una sal. Verdadero o falso?"
2. "El bicarbonato de sodio reacciona con ácidos liberando dióxido de carbono (CO₂). Verdadero o falso?"
3. "El jugo de limón contiene ácido cítrico. Verdadero o falso?"

## ✅ Beneficios

### **Para el Usuario:**
- ✅ Acceso fácil a preguntas predefinidas
- ✅ Vista previa antes de generar la clase
- ✅ Flexibilidad para elegir el tipo de preguntas
- ✅ Integración automática con el sistema existente

### **Para el Sistema:**
- ✅ Reutilización de preguntas existentes
- ✅ Consistencia en el tipo de preguntas
- ✅ Mantenimiento centralizado de preguntas
- ✅ Extensibilidad para agregar más bancos

## 🚀 Uso

### **En el Class Builder:**
1. **Paso 1-3:** Configurar información básica, diagnóstico y contenido
2. **Paso 4:** Seleccionar banco de preguntas
3. **Paso 5:** Configurar examen final
4. **Paso 6:** Generar y ejecutar clase

### **Resultado:**
- Clase generada con preguntas personalizadas
- Integración completa con `demo_sequence_manager.py`
- Funcionalidad de preguntas aleatorias mejorada

## 🔧 Mantenimiento

### **Agregar Nuevos Bancos:**
1. Agregar banco en `demo_sequence_manager.py`
2. Actualizar `question_bank_extractor.py` si es necesario
3. El Class Builder detectará automáticamente el nuevo banco

### **Modificar Preguntas:**
1. Editar preguntas en `demo_sequence_manager.py`
2. Reiniciar el Class Builder para cargar cambios
3. Las clases generadas usarán las preguntas actualizadas

## 🎉 Estado Actual

**✅ INTEGRACIÓN COMPLETADA**
- ✅ Extracción automática de preguntas
- ✅ Interfaz de usuario funcional
- ✅ Generación de código mejorada
- ✅ Pruebas exitosas
- ✅ Documentación completa

**El Class Builder ahora puede usar las preguntas de `demo_sequence_manager.py` de manera completamente integrada y funcional.**
