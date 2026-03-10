# Sistema de Clases ADAI - Estructura y Funcionamiento

## Descripción General

El sistema de clases ADAI (Asistente Docente Androide de Ingeniería) es una plataforma educativa interactiva que combina inteligencia artificial, reconocimiento facial, control robótico y presentaciones multimedia para crear experiencias de aprendizaje inmersivas.

## Estructura del Sistema

### 📁 Organización de Directorios

```
ia-clases/clases/
├── main/                           # Clase principal funcional
│   ├── demo_sequence_manager.py   # ⭐ EJEMPLO FUNCIONAL PRINCIPAL
│   ├── main.py                     # Versión original
│   ├── main_modular.py             # Versión modularizada
│   ├── class_config.json          # Configuración de la clase
│   ├── faces/                      # Caras conocidas para reconocimiento
│   ├── pdfs/                       # Presentaciones PDF
│   ├── exams/                      # Códigos QR de exámenes
│   └── resources/                  # Recursos multimedia
├── sequences/                      # Secuencias de movimiento del robot
│   ├── SecuenciaBeta1Parte1.json
│   ├── SecuenciaBeta1Parte2.json
│   └── [otras secuencias...]
├── [clase_nombre]/                 # Clases individuales
│   ├── [nombre_clase].py          # Archivo principal de la clase
│   └── class_config.json          # Configuración específica
├── classes_metadata.json          # Metadatos de todas las clases
└── ejemplo_clase_personalizada.py # Ejemplo de clase personalizada
```

## 🎯 Clase Funcional Principal: `demo_sequence_manager.py`

### Características Principales

`demo_sequence_manager.py` es el ejemplo funcional más completo del sistema, que incluye:

#### 🔧 Funcionalidades Core
- **Sistema de Voz**: TTS (Text-to-Speech) con animaciones faciales
- **Reconocimiento Facial**: Identificación automática de estudiantes
- **Control Robótico**: Integración con ESP32 para movimientos del robot
- **Presentaciones Interactivas**: Manejo de PDFs con navegación por diapositivas
- **Sistema de Preguntas**: Evaluación automática con IA
- **Códigos QR**: Evaluaciones diagnósticas y exámenes finales

#### 🏗️ Arquitectura del Sistema

```python
# Flujo principal de demo_sequence_manager.py
def main():
    # 1. Inicialización del sistema
    engine = initialize_tts()
    
    # 2. Verificación de cámara
    if not verify_camera_for_iriun():
        return
    
    # 3. Identificación de usuarios
    current_users, _ = identify_users(engine, current_slide_num, exit_flag)
    
    # 4. Carga de caras conocidas
    known_faces = load_known_faces()
    
    # 5. Inicio del proceso de cámara
    camera_proc = Process(target=camera_process, ...)
    
    # 6. Explicación de diapositivas con secuencias ESP32
    sequence_mapping = {
        3: "SecuenciaBeta1Parte1",
        4: "SecuenciaBeta1Parte2"
    }
    explain_slides_with_sequences(engine, pdf_path, pdf_text, ...)
```

### 🎮 Componentes Principales

#### 1. **Sistema de Voz y Animación**
```python
def speak_with_animation(engine, text):
    """Habla con animación facial sincronizada"""
    # Dibuja cara animada mientras habla
    # Controla duración y sincronización
```

#### 2. **Reconocimiento Facial**
```python
def identify_users(engine, current_slide_num, exit_flag):
    """Identifica estudiantes de izquierda a derecha"""
    # Detecta caras en tiempo real
    # Asigna posiciones automáticamente
    # Registra nuevos usuarios
```

#### 3. **Control Robótico ESP32**
```python
def execute_esp32_sequence(sequence_name: str) -> bool:
    """Ejecuta secuencias predefinidas del robot"""
    # Carga secuencia desde JSON
    # Envía comandos al ESP32
    # Controla brazos, manos y muñecas
```

#### 4. **Sistema de Preguntas Inteligente**
```python
class RandomQuestionManager:
    """Gestiona preguntas aleatorias y evaluación"""
    def select_random_student(self)
    def select_random_question(self)
    def conduct_random_question(self, engine, pdf_text)
```

#### 5. **Navegación de Diapositivas**
```python
def explain_slides_with_sequences(engine, pdf_path, pdf_text, ...):
    """Explica diapositivas con secuencias robóticas"""
    # Navega por PDF
    # Ejecuta secuencias en diapositivas específicas
    # Maneja interacciones de estudiantes
```

## 📋 Estructura de Clases Individuales

### Configuración de Clase (`class_config.json`)

```json
{
  "title": "Nombre de la Clase",
  "subject": "Materia",
  "description": "Descripción de la clase",
  "duration": "45 minutos",
  "created_at": "2025-08-30T17:34:22.572390",
  "main_file": "archivo_principal.py",
  "folder_name": "nombre_carpeta"
}
```

### Metadatos del Sistema (`classes_metadata.json`)

El archivo `classes_metadata.json` mantiene un registro completo de todas las clases:

```json
{
  "classes": [
    {
      "name": "demo_sequence_manager.py",
      "folder": "main",
      "file_path": "clases\\main\\demo_sequence_manager.py",
      "title": "main.py",
      "subject": "Robótica",
      "description": "Clase para TESTING",
      "duration": "45 minutos",
      "resources": {
        "files": [...],
        "images": [...],
        "pdfs": [...],
        "qrs": [...]
      }
    }
  ]
}
```

## 🤖 Sistema de Secuencias Robóticas

### Estructura de Secuencias JSON

```json
{
  "name": "SecuenciaBeta1Parte1",
  "title": "Secuencia Beta Parte 1",
  "created_at": "2025-09-16T13:39:52.429296",
  "movements": [
    {
      "id": 5,
      "name": "Movement_5",
      "actions": [
        {
          "command": "BRAZOS",
          "parameters": {
            "BI": 10.0,    # Brazo Izquierdo
            "BD": 35.0,    # Brazo Derecho
            "FI": 80.0,    # Forearm Izquierdo
            "FD": 70.0,    # Forearm Derecho
            "HI": 80.0,    # Hombro Izquierdo
            "HD": 80.0,    # Hombro Derecho
            "PD": 45.0     # Pecho Derecho
          },
          "duration": 1000,
          "description": "Arm movement 6"
        }
      ]
    }
  ]
}
```

### Tipos de Comandos Robóticos

1. **BRAZOS**: Control de brazos y hombros
2. **MANO**: Gestos de manos (abrir, cerrar, paz, rock, etc.)
3. **MUNECA**: Control de muñecas
4. **DEDO**: Control individual de dedos

## 🎓 Flujo de una Clase Completa

### Fase 1: Inicialización
```python
# 1. Verificar cámara
verify_camera_for_iriun()

# 2. Inicializar TTS
engine = initialize_tts()

# 3. Crear ventana de animación
cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
```

### Fase 2: Identificación de Estudiantes
```python
# Identificar usuarios de izquierda a derecha
current_users, _ = identify_users(engine, current_slide_num, exit_flag)

# Cargar caras conocidas
known_faces = load_known_faces()
```

### Fase 3: Proceso de Cámara
```python
# Iniciar proceso de cámara en paralelo
camera_proc = Process(target=camera_process, args=(...))
camera_proc.daemon = True
camera_proc.start()
```

### Fase 4: Presentación Interactiva
```python
# Mapeo de secuencias por diapositiva
sequence_mapping = {
    3: "SecuenciaBeta1Parte1",
    4: "SecuenciaBeta1Parte2"
}

# Explicar diapositivas con secuencias
explain_slides_with_sequences(engine, pdf_path, pdf_text, ...)
```

### Fase 5: Evaluación
```python
# Mostrar QR de diagnóstico
show_diagnostic_qr(qr_image_path, display_time=15)

# Mostrar QR de examen final
show_final_exam_qr(qr_image_path, display_time=20)
```

## 🛠️ Creación de Clases Personalizadas

### Ejemplo Básico

```python
from modules.speech import initialize_tts, speak_with_animation
from modules.slides import extract_text_from_pdf
from modules.qr import show_diagnostic_qr

def mi_clase_personalizada():
    # Inicializar sistema
    engine = initialize_tts()
    
    # Saludo personalizado
    speak_with_animation(engine, "Bienvenidos a mi clase personalizada")
    
    # Cargar PDF
    pdf_text = extract_text_from_pdf("mi_presentacion.pdf")
    
    # Mostrar QR diagnóstico
    show_diagnostic_qr("diagnostico.png")
    
    # Lógica de la clase...
```

### Clase Personalizada Avanzada

```python
class MiClasePersonalizada:
    def __init__(self, nombre_clase):
        self.nombre_clase = nombre_clase
        self.engine = initialize_tts()
    
    def ejecutar_clase_completa(self, pdf_path):
        # 1. Inicializar sistema
        self.inicializar_sistema()
        
        # 2. Mostrar evaluación diagnóstica
        self.mostrar_evaluacion_diagnostica()
        
        # 3. Identificar estudiantes
        self.identificar_estudiantes()
        
        # 4. Impartir clase
        self.impartir_clase_con_preguntas(pdf_path)
        
        # 5. Mostrar examen final
        self.mostrar_examen_final()
        
        # 6. Finalizar
        self.finalizar_clase()
```

## 🔧 Configuración y Dependencias

### Dependencias Principales

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

### Configuración de OpenAI

```python
# En modules/config.py
OPENAI_API_KEY = "tu_clave_api_aqui"
```

### Configuración de Cámara

```python
# Verificar cámara para Iriun
if not verify_camera_for_iriun():
    print("Problemas con la cámara")
    return
```

## 📊 Sistema de Monitoreo

### Variables Compartidas (Multiprocessing)

```python
# Variables compartidas entre procesos
hand_raised_counter = multiprocessing.Value('i', 0)
current_slide_num = multiprocessing.Value('i', 1)
exit_flag = multiprocessing.Value('i', 0)
current_hand_raiser = multiprocessing.Value('i', -1)
```

### Proceso de Cámara

```python
def camera_process(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, registered_users):
    """Proceso principal de cámara que detecta manos levantadas"""
    # Detección de MediaPipe
    # Seguimiento de usuarios
    # Detección de gestos
```

## 🎯 Mejores Prácticas

### 1. **Estructura de Archivos**
- Mantener cada clase en su propia carpeta
- Incluir `class_config.json` en cada clase
- Usar nombres descriptivos para archivos

### 2. **Gestión de Recursos**
- Siempre cerrar procesos de cámara al finalizar
- Limpiar ventanas OpenCV
- Manejar excepciones apropiadamente

### 3. **Secuencias Robóticas**
- Probar secuencias antes de usar en clase
- Mantener duraciones apropiadas
- Documentar comandos y parámetros

### 4. **Interacción con Estudiantes**
- Usar reconocimiento facial para personalización
- Implementar sistema de preguntas equilibrado
- Mantener feedback visual y auditivo

## 🚀 Ejecución del Sistema

### Ejecutar Clase Principal

```bash
cd ia-clases/clases/main
python demo_sequence_manager.py
```

### Ejecutar Clase Personalizada

```bash
cd ia-clases/clases
python ejemplo_clase_personalizada.py
```

## 📈 Monitoreo y Debugging

### Logs del Sistema

```python
print("🔍 Identificando usuarios de izquierda a derecha...")
print("⏳ Esperando a que la cámara se inicialice...")
print("✅ Sistema inicializado correctamente")
```

### Verificación de Componentes

```python
# Verificar TTS
if not engine:
    print("❌ No se pudo inicializar el motor TTS")

# Verificar cámara
if not verify_camera_for_iriun():
    print("⚠️ Problemas detectados con la cámara")

# Verificar PDF
if not pdf_text:
    print("❌ No se pudo leer el PDF")
```

## 🔄 Flujo de Datos

```
Usuario → Cámara → Reconocimiento Facial → Identificación
    ↓
PDF → Extracción de Texto → IA → Preguntas Aleatorias
    ↓
Secuencias JSON → ESP32 → Movimientos del Robot
    ↓
Respuestas → Evaluación IA → Feedback
```

## 📝 Notas Importantes

1. **demo_sequence_manager.py** es el ejemplo más completo y funcional
2. Todas las clases siguen la misma estructura básica
3. El sistema es modular y extensible
4. Las secuencias robóticas son independientes y reutilizables
5. El reconocimiento facial requiere configuración inicial
6. Las evaluaciones usan códigos QR para integración con plataformas externas

---

*Este README proporciona una guía completa del sistema de clases ADAI, con `demo_sequence_manager.py` como referencia principal para entender la funcionalidad completa del sistema.*
