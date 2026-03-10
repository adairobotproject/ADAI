# Sistema ADAI - Versión Organizada

## 📁 Estructura del Proyecto

El proyecto ha sido reorganizado en módulos específicos para mejorar la mantenibilidad y reutilización del código:

```
ia-clases/
├── config/                 # Configuración del sistema
│   ├── __init__.py
│   └── settings.py        # Configuración centralizada
├── utils/                  # Utilidades generales
│   ├── __init__.py
│   └── file_utils.py      # Manejo de archivos y directorios
├── ai/                     # Inteligencia artificial
│   ├── __init__.py
│   └── openai_client.py   # Cliente de OpenAI
├── vision/                 # Visión por computadora
│   ├── __init__.py
│   ├── face_recognition_utils.py  # Reconocimiento facial
│   └── hand_detection.py          # Detección de gestos
├── audio/                  # Audio y síntesis de voz
│   ├── __init__.py
│   ├── tts_manager.py     # Texto a voz
│   └── speech_recognition_utils.py # Reconocimiento de voz
├── ui/                     # Interfaz de usuario
│   ├── __init__.py
│   └── animations.py       # Animaciones y elementos visuales
├── exams/                  # Exámenes y evaluaciones
│   ├── __init__.py
│   └── question_manager.py # Gestión de preguntas
├── main_organized.py       # Sistema principal reorganizado
└── README_ORGANIZADO.md    # Este archivo
```

## 🚀 Características Principales

### 1. **Configuración Centralizada** (`config/settings.py`)
- Configuración de OpenAI
- Configuración de ventanas y cámara
- Rutas de archivos y directorios
- Configuración de detección de gestos

### 2. **Utilidades de Archivos** (`utils/file_utils.py`)
- Configuración de directorios
- Extracción de texto de PDFs
- Manejo de caras reconocidas
- Carga de caras conocidas

### 3. **Inteligencia Artificial** (`ai/openai_client.py`)
- Cliente de OpenAI para preguntas y respuestas
- Evaluación de respuestas de estudiantes
- Resumen de textos
- Interpretación de imágenes

### 4. **Visión por Computadora** (`vision/`)
- **Reconocimiento Facial** (`face_recognition_utils.py`)
  - Detección y reconocimiento de usuarios
  - Guardado de nuevas caras
  - Captura de frames

- **Detección de Gestos** (`hand_detection.py`)
  - Detección de manos levantadas
  - Tracking de usuarios
  - Gestión de landmarks

### 5. **Audio** (`audio/`)
- **Texto a Voz** (`tts_manager.py`)
  - Síntesis de voz
  - Configuración de velocidad y volumen
  - Habla en hilos separados

- **Reconocimiento de Voz** (`speech_recognition_utils.py`)
  - Escucha de comandos
  - Detección de palabras clave
  - Respuestas sí/no

### 6. **Interfaz de Usuario** (`ui/animations.py`)
- Animaciones del robot
- Visualización de QR
- Elementos visuales interactivos
- Conversión de PDF a imágenes

### 7. **Exámenes** (`exams/question_manager.py`)
- Gestión de preguntas aleatorias
- Diferentes tipos de exámenes
- Estadísticas de preguntas
- Evaluación de respuestas

## 🔧 Instalación y Uso

### Requisitos
```bash
pip install -r requirements.txt
```

### Ejecutar el Sistema
```bash
python main_organized.py
```

## 📋 Funcionalidades

### 1. **Modo Diagnóstico**
- Identificación de usuarios
- Mostrar QR de diagnóstico
- Configuración inicial

### 2. **Modo Presentación**
- Explicación de diapositivas
- Preguntas aleatorias
- Reconocimiento de gestos
- Evaluación en tiempo real

### 3. **Modo Examen**
- Diferentes tipos de examen
- Preguntas específicas por tema
- Evaluación automática
- QR de acceso

## 🎯 Ventajas de la Nueva Estructura

### ✅ **Modularidad**
- Cada funcionalidad está en su propio módulo
- Fácil mantenimiento y actualización
- Reutilización de código

### ✅ **Configuración Centralizada**
- Todas las configuraciones en un lugar
- Fácil modificación de parámetros
- Configuración por entorno

### ✅ **Separación de Responsabilidades**
- Audio separado de visión
- IA separada de UI
- Gestión de archivos independiente

### ✅ **Escalabilidad**
- Fácil agregar nuevas funcionalidades
- Módulos independientes
- Testing unitario posible

### ✅ **Mantenibilidad**
- Código organizado y documentado
- Funciones específicas
- Fácil debugging

## 🔄 Migración desde la Versión Anterior

Para migrar desde el código original:

1. **Mantener archivos originales**: `main.py`, `config.py`, etc.
2. **Usar nueva estructura**: `main_organized.py`
3. **Importar módulos específicos** según necesidad

## 📝 Ejemplo de Uso

```python
from config.settings import settings
from ai.openai_client import OpenAIClient
from audio.tts_manager import TTSManager

# Inicializar componentes
openai_client = OpenAIClient(settings.openai_api_key)
tts_manager = TTSManager()

# Usar funcionalidades
response = openai_client.ask_openai("¿Qué es IoMT?", "contexto...")
tts_manager.speak(response)
```

## 🛠️ Desarrollo

### Agregar Nueva Funcionalidad
1. Crear módulo en carpeta correspondiente
2. Implementar funcionalidad
3. Importar en `main_organized.py`
4. Documentar cambios

### Testing
```python
# Ejemplo de test para un módulo
from vision.face_recognition_utils import FaceRecognitionManager

def test_face_recognition():
    manager = FaceRecognitionManager("faces_dir")
    # Test implementation
```

## 📊 Comparación de Estructuras

| Aspecto | Versión Original | Versión Organizada |
|---------|------------------|-------------------|
| **Archivos** | 1 archivo grande | Múltiples módulos |
| **Mantenimiento** | Difícil | Fácil |
| **Reutilización** | Limitada | Alta |
| **Testing** | Complejo | Simple |
| **Escalabilidad** | Baja | Alta |

## 🎉 Conclusión

La nueva estructura organizada proporciona:
- **Mejor organización** del código
- **Mayor reutilización** de funciones
- **Fácil mantenimiento** y desarrollo
- **Escalabilidad** para nuevas funcionalidades
- **Testing** más sencillo

El sistema mantiene todas las funcionalidades originales pero con una arquitectura mucho más robusta y profesional. 