# Estructura del Proyecto ADAI

## 📁 Visión General de la Arquitectura

El proyecto ADAI ha sido diseñado con una arquitectura modular que separa las responsabilidades en componentes específicos. Esta estructura facilita el mantenimiento, la escalabilidad y la reutilización del código.

```
ia-clases/
├── 📁 config/                 # Configuración centralizada
├── 📁 utils/                  # Utilidades generales
├── 📁 ai/                     # Inteligencia artificial
├── 📁 vision/                 # Visión por computadora
├── 📁 audio/                  # Audio y síntesis de voz
├── 📁 ui/                     # Interfaz de usuario
├── 📁 exams/                  # Exámenes y evaluaciones
├── 📁 documentacion/          # Documentación del proyecto
├── 📄 main_organized.py       # Sistema principal reorganizado
├── 📄 ejemplo_uso_modulos.py  # Ejemplos de uso
└── 📄 README.md              # README original
```

## 🏗️ Detalle de Módulos

### 1. **config/** - Configuración del Sistema

**Propósito**: Centralizar toda la configuración del sistema en un solo lugar.

#### Archivos:
- `__init__.py` - Inicializador del módulo
- `settings.py` - Configuración centralizada

#### Funcionalidades:
```python
# Ejemplo de uso
from config.settings import settings

# Obtener configuraciones
camera_config = settings.get_camera_config()
openai_client = settings.get_openai_client()
qr_path = settings.get_qr_path('diagnostic')
```

#### Configuraciones Incluidas:
- **OpenAI**: API key y cliente
- **Tesseract**: Ruta del ejecutable OCR
- **Ventanas**: Configuración de tamaños y nombres
- **Cámara**: FPS, buffer, formato
- **Gestos**: Sensibilidad y parámetros de detección
- **Rutas**: Directorios y archivos del sistema

### 2. **utils/** - Utilidades Generales

**Propósito**: Funciones auxiliares para manejo de archivos y directorios.

#### Archivos:
- `__init__.py` - Inicializador del módulo
- `file_utils.py` - Manejo de archivos y directorios

#### Funcionalidades Principales:
```python
from utils.file_utils import setup_directories, extract_text_from_pdf

# Configurar directorios
directories = setup_directories(base_dir)

# Extraer texto de PDF
text = extract_text_from_pdf("documento.pdf")

# Cargar caras conocidas
known_faces, known_names = load_known_faces(faces_dir)
```

#### Funciones Incluidas:
- `setup_directories()` - Crear estructura de directorios
- `extract_text_from_pdf()` - Extraer texto de PDFs
- `save_new_face()` - Guardar nuevas caras
- `load_known_faces()` - Cargar caras conocidas

### 3. **ai/** - Inteligencia Artificial

**Propósito**: Manejar todas las interacciones con servicios de IA.

#### Archivos:
- `__init__.py` - Inicializador del módulo
- `openai_client.py` - Cliente de OpenAI

#### Clase Principal:
```python
class OpenAIClient:
    def __init__(self, api_key: str)
    def evaluate_student_answer(question, answer, context, student_name)
    def ask_openai(question, context, student_name=None)
    def summarize_text(text)
    def interpret_image(image_path)
```

#### Funcionalidades:
- **Evaluación de Respuestas**: Evaluar respuestas de estudiantes
- **Preguntas y Respuestas**: Hacer preguntas con contexto
- **Resumen de Textos**: Resumir contenido largo
- **Interpretación de Imágenes**: Analizar imágenes con IA

### 4. **vision/** - Visión por Computadora

**Propósito**: Manejar reconocimiento facial y detección de gestos.

#### Archivos:
- `__init__.py` - Inicializador del módulo
- `face_recognition_utils.py` - Reconocimiento facial
- `hand_detection.py` - Detección de gestos

#### Reconocimiento Facial:
```python
class FaceRecognitionManager:
    def __init__(self, faces_dir: str)
    def recognize_user(frame) -> Tuple[Optional[str], bool]
    def save_new_face(frame, name: str) -> bool
    def get_known_faces() -> Tuple[List, List]
```

#### Detección de Gestos:
```python
class HandGestureDetector:
    def __init__(self)
    def detect_hand_raise(frame) -> Tuple[bool, List]
    def draw_hand_landmarks(frame, hand_landmarks_list)
    def release()
```

#### Funcionalidades:
- **Reconocimiento de Usuarios**: Identificar estudiantes
- **Detección de Manos**: Detectar manos levantadas
- **Tracking de Usuarios**: Seguir movimientos
- **Landmarks**: Visualizar puntos de referencia

### 5. **audio/** - Audio y Síntesis de Voz

**Propósito**: Manejar síntesis de voz y reconocimiento de voz.

#### Archivos:
- `__init__.py` - Inicializador del módulo
- `tts_manager.py` - Texto a voz
- `speech_recognition_utils.py` - Reconocimiento de voz

#### Texto a Voz:
```python
class TTSManager:
    def __init__(self)
    def speak(text: str, block: bool = True)
    def set_rate(rate: int)
    def set_volume(volume: float)
    def cleanup()
```

#### Reconocimiento de Voz:
```python
class SpeechRecognitionManager:
    def __init__(self)
    def listen(timeout: int = 5) -> Tuple[Optional[str], bool]
    def listen_for_keywords(keywords: list, timeout: int = 10)
    def listen_for_yes_no(timeout: int = 5) -> Optional[bool]
```

#### Funcionalidades:
- **Síntesis de Voz**: Convertir texto a voz
- **Reconocimiento de Voz**: Escuchar comandos
- **Detección de Palabras Clave**: Identificar comandos específicos
- **Respuestas Sí/No**: Procesar respuestas binarias

### 6. **ui/** - Interfaz de Usuario

**Propósito**: Manejar animaciones y elementos visuales.

#### Archivos:
- `__init__.py` - Inicializador del módulo
- `animations.py` - Animaciones y elementos visuales

#### Funciones Principales:
```python
def draw_fun_face(width: int = 600, height: int = 400, mouth_state: int = 0)
def create_qr_display_frame(qr_image_path: str, title: str = "", subtitle: str = "")
def show_pdf_page_in_opencv(page)
def create_loading_animation(frames: int = 30)
def create_success_animation()
```

#### Funcionalidades:
- **Animaciones del Robot**: Cara expresiva del asistente
- **Visualización de QR**: Mostrar códigos QR
- **Conversión de PDF**: Renderizar páginas de PDF
- **Animaciones de Carga**: Indicadores visuales

### 7. **exams/** - Exámenes y Evaluaciones

**Propósito**: Manejar preguntas, exámenes y evaluaciones.

#### Archivos:
- `__init__.py` - Inicializador del módulo
- `question_manager.py` - Gestión de preguntas

#### Clases Principales:
```python
class RandomQuestionManager:
    def __init__(self, students: List[str], question_bank: Optional[List[str]] = None)
    def select_random_student() -> str
    def select_random_question() -> str
    def conduct_random_question(tts_manager, pdf_text: str)
    def get_statistics() -> Dict

class ExamManager:
    def __init__(self)
    def get_exam_questions(exam_type: str) -> List[str]
    def get_exam_title(exam_type: str) -> str
    def create_custom_exam(title: str, questions: List[str]) -> str
```

#### Funcionalidades:
- **Preguntas Aleatorias**: Selección inteligente de preguntas
- **Gestión de Estudiantes**: Seguimiento de participación
- **Tipos de Examen**: Diferentes categorías de evaluación
- **Estadísticas**: Seguimiento de rendimiento

## 🔄 Flujo de Datos

### 1. **Inicialización del Sistema**
```
main_organized.py
    ↓
config/settings.py (cargar configuración)
    ↓
utils/file_utils.py (configurar directorios)
    ↓
Inicializar módulos (ai, vision, audio, ui, exams)
```

### 2. **Proceso de Reconocimiento**
```
Cámara → vision/face_recognition_utils.py
    ↓
Reconocer usuario → Actualizar lista de usuarios
    ↓
vision/hand_detection.py → Detectar gestos
    ↓
audio/speech_recognition_utils.py → Escuchar preguntas
```

### 3. **Procesamiento de IA**
```
Pregunta → ai/openai_client.py
    ↓
Contexto del PDF → utils/file_utils.py
    ↓
Respuesta de IA → audio/tts_manager.py
    ↓
Síntesis de voz → Usuario
```

### 4. **Gestión de Exámenes**
```
exams/question_manager.py → Seleccionar pregunta
    ↓
ai/openai_client.py → Evaluar respuesta
    ↓
ui/animations.py → Mostrar resultados
    ↓
audio/tts_manager.py → Proporcionar feedback
```

## 🎯 Patrones de Diseño Utilizados

### 1. **Singleton Pattern**
- `config/settings.py`: Configuración global única
- `audio/tts_manager.py`: Motor TTS único

### 2. **Factory Pattern**
- `exams/question_manager.py`: Crear diferentes tipos de preguntas
- `ai/openai_client.py`: Crear diferentes tipos de respuestas

### 3. **Observer Pattern**
- `vision/hand_detection.py`: Notificar cuando se detectan gestos
- `audio/speech_recognition_utils.py`: Notificar cuando se escucha voz

### 4. **Strategy Pattern**
- `exams/question_manager.py`: Diferentes estrategias de selección de preguntas
- `ai/openai_client.py`: Diferentes estrategias de evaluación

## 📊 Métricas de Código

| Módulo | Archivos | Líneas | Funciones | Clases |
|--------|----------|--------|-----------|--------|
| **config** | 2 | ~150 | 8 | 1 |
| **utils** | 2 | ~120 | 6 | 0 |
| **ai** | 2 | ~200 | 8 | 1 |
| **vision** | 3 | ~300 | 15 | 3 |
| **audio** | 3 | ~250 | 12 | 2 |
| **ui** | 2 | ~180 | 8 | 0 |
| **exams** | 2 | ~200 | 10 | 2 |
| **documentacion** | 2 | ~400 | 0 | 0 |

## 🔧 Configuración por Entorno

### Desarrollo
```python
# config/settings.py
self.debug_mode = True
self.log_level = "DEBUG"
self.camera_index = 0
```

### Producción
```python
# config/settings.py
self.debug_mode = False
self.log_level = "INFO"
self.camera_index = 0
```

### Testing
```python
# config/settings.py
self.test_mode = True
self.mock_camera = True
self.mock_tts = True
```

## 🚀 Optimizaciones Implementadas

### 1. **Lazy Loading**
- Módulos se cargan solo cuando se necesitan
- Configuración se inicializa bajo demanda

### 2. **Caching**
- Caras reconocidas se cachean en memoria
- Configuraciones se mantienen en singleton

### 3. **Threading**
- Audio se ejecuta en hilos separados
- Cámara se procesa en background

### 4. **Error Handling**
- Manejo robusto de errores en cada módulo
- Fallbacks para funcionalidades críticas

## 📈 Escalabilidad

### Agregar Nuevo Módulo
1. Crear carpeta en raíz del proyecto
2. Agregar `__init__.py`
3. Implementar funcionalidades específicas
4. Documentar en este archivo
5. Actualizar `main_organized.py`

### Agregar Nueva Funcionalidad
1. Identificar módulo apropiado
2. Implementar función/clase
3. Agregar documentación
4. Crear tests
5. Actualizar ejemplos

### Migración de Versiones
1. Mantener compatibilidad hacia atrás
2. Documentar cambios
3. Proporcionar guías de migración
4. Actualizar ejemplos

## 🎉 Beneficios de la Estructura

### ✅ **Mantenibilidad**
- Código organizado por responsabilidades
- Fácil localización de problemas
- Documentación específica por módulo

### ✅ **Reutilización**
- Módulos independientes
- Funciones específicas
- Fácil importación

### ✅ **Testing**
- Tests unitarios por módulo
- Mocks específicos
- Cobertura completa

### ✅ **Escalabilidad**
- Fácil agregar funcionalidades
- Módulos independientes
- Configuración flexible

### ✅ **Colaboración**
- Responsabilidades claras
- Documentación completa
- Estándares consistentes

---

**Esta estructura modular hace que ADAI sea un sistema robusto, mantenible y escalable para el futuro desarrollo de tecnologías educativas.** 🚀 