# ADAI - Sistema Modular

## Descripción

ADAI (Asistente Docente Androide de Ingeniería) ha sido modularizado para permitir una mayor flexibilidad y reutilización de código. Ahora las funciones están organizadas en módulos separados que pueden ser utilizados por diferentes clases principales.

## Estructura de Módulos

```
modules/
├── __init__.py          # Inicialización del paquete
├── config.py            # Configuraciones y constantes
├── speech.py            # Funciones de voz y TTS
├── camera.py            # Funciones de cámara y detección
├── esp32.py             # Control del robot ESP32
├── qr.py                # Funciones de códigos QR
├── questions.py         # Sistema de preguntas y evaluación
├── slides.py            # Manejo de diapositivas y PDFs
└── utils.py             # Utilidades generales
```

## Módulos Disponibles

### 1. `config.py`
- **Propósito**: Configuraciones y constantes del sistema
- **Contenido**: 
  - Configuración de OpenAI
  - Rutas de códigos QR
  - Bancos de preguntas
  - Configuraciones de cámara, MediaPipe, Tesseract, etc.
  - Colores y configuraciones de ventanas

### 2. `speech.py`
- **Propósito**: Funciones de voz y reconocimiento
- **Funciones principales**:
  - `initialize_tts()`: Inicializa el motor de TTS
  - `listen()`: Escucha y reconoce voz
  - `speak_with_animation()`: Habla con animación facial
  - `draw_fun_face()`: Dibuja rostro animado

### 3. `camera.py`
- **Propósito**: Funciones de cámara y detección
- **Funciones principales**:
  - `verify_camera_for_iriun()`: Verifica funcionamiento de cámara
  - `capture_frame()`: Captura frames de la cámara
  - `camera_process()`: Proceso principal de cámara
  - `load_known_faces()`: Carga caras conocidas
  - `recognize_user()`: Reconoce usuarios

### 4. `esp32.py`
- **Propósito**: Control del robot ESP32
- **Funciones principales**:
  - `esp32_action_resolver()`: Ejecuta secuencias ESP32
  - `execute_esp32_sequence()`: Alias para compatibilidad

### 5. `qr.py`
- **Propósito**: Funciones de códigos QR
- **Funciones principales**:
  - `show_diagnostic_qr()`: Muestra QR de diagnóstico
  - `show_final_exam_qr()`: Muestra QR de examen final

### 6. `questions.py`
- **Propósito**: Sistema de preguntas y evaluación
- **Funciones principales**:
  - `evaluate_student_answer()`: Evalúa respuestas de estudiantes
  - `RandomQuestionManager`: Clase para gestionar preguntas aleatorias

### 7. `slides.py`
- **Propósito**: Manejo de diapositivas y PDFs
- **Funciones principales**:
  - `extract_text_from_pdf()`: Extrae texto de PDFs
  - `show_pdf_page_in_opencv()`: Muestra páginas PDF en OpenCV
  - `explain_slides_with_random_questions()`: Explica con preguntas aleatorias
  - `explain_slides_with_sequences()`: Explica con secuencias ESP32
  - `process_question()`: Procesa preguntas de estudiantes

### 8. `utils.py`
- **Propósito**: Utilidades generales
- **Funciones principales**:
  - `identify_users()`: Identifica usuarios de izquierda a derecha

## Cómo Usar el Sistema Modular

### 1. Clase Principal Simple

```python
from modules.speech import initialize_tts, speak_with_animation
from modules.slides import extract_text_from_pdf, explain_slides_with_sequences
from modules.qr import show_diagnostic_qr

def main():
    # Inicializar TTS
    engine = initialize_tts()
    
    # Saludo
    speak_with_animation(engine, "Hola, soy ADAI")
    
    # Cargar PDF
    pdf_text = extract_text_from_pdf("mi_clase.pdf")
    
    # Mostrar QR diagnóstico
    show_diagnostic_qr("diagnostico.png")
    
    # Explicar diapositivas
    explain_slides_with_sequences(engine, "mi_clase.pdf", pdf_text, ...)
```

### 2. Clase Personalizada

```python
from modules.config import get_qr_paths
from modules.speech import initialize_tts, speak_with_animation
from modules.slides import extract_text_from_pdf

class MiClasePersonalizada:
    def __init__(self, nombre):
        self.nombre = nombre
        self.engine = initialize_tts()
    
    def impartir_clase(self, pdf_path):
        speak_with_animation(self.engine, f"Bienvenidos a {self.nombre}")
        # ... resto de la lógica
```

### 3. Usando Funciones Específicas

```python
# Solo usar detección de cámara
from modules.camera import verify_camera_for_iriun
if verify_camera_for_iriun():
    print("Cámara funcionando")

# Solo usar ESP32
from modules.esp32 import execute_esp32_sequence
execute_esp32_sequence("mi_secuencia")

# Solo usar preguntas
from modules.questions import RandomQuestionManager
question_manager = RandomQuestionManager(["Ana", "Carlos"])
```

## Archivos de Ejemplo

### 1. `main_modular.py`
- Versión modularizada del main.py original
- Demuestra el uso básico de todos los módulos
- Mantiene la funcionalidad completa del sistema original

### 2. `ejemplo_clase_personalizada.py`
- Ejemplo de cómo crear una clase personalizada
- Demuestra el uso de la clase `ClasePersonalizada`
- Muestra cómo organizar una clase completa usando los módulos

## Ventajas del Sistema Modular

1. **Reutilización**: Los módulos pueden ser utilizados por múltiples clases
2. **Mantenimiento**: Cada módulo es independiente y fácil de mantener
3. **Flexibilidad**: Puedes usar solo los módulos que necesites
4. **Extensibilidad**: Fácil agregar nuevas funcionalidades
5. **Organización**: Código mejor organizado y más legible

## Migración desde el Sistema Original

Para migrar desde el sistema original:

1. **Reemplaza imports**: Cambia las importaciones por los módulos correspondientes
2. **Actualiza llamadas**: Las funciones mantienen la misma interfaz
3. **Configuración**: Usa `config.py` para todas las configuraciones
4. **Prueba**: Verifica que todo funciona correctamente

## Configuración

Todas las configuraciones están centralizadas en `modules/config.py`:

- **OpenAI API Key**: Configura tu clave de API
- **Rutas de QR**: Ajusta las rutas de los códigos QR
- **Configuración de cámara**: Ajusta parámetros de detección
- **Colores y ventanas**: Personaliza la interfaz visual

## Dependencias

Los módulos requieren las mismas dependencias que el sistema original:

```bash
pip install opencv-python
pip install face-recognition
pip install mediapipe
pip install pyttsx3
pip install speechrecognition
pip install openai
pip install pymupdf
pip install pytesseract
pip install numpy
```

## Soporte

Para soporte o preguntas sobre el sistema modular, consulta la documentación de cada módulo o revisa los archivos de ejemplo incluidos.
