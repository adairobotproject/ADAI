# Sistema ADAI - Asistente Docente con Inteligencia Artificial

## 🤖 Descripción General

ADAI es un sistema de asistente docente inteligente que combina tecnologías de visión por computadora, reconocimiento de voz, inteligencia artificial y robótica educativa para crear una experiencia de aprendizaje interactiva y personalizada.

## 🚀 Características Principales

### 🎯 **Funcionalidades Core**
- **Reconocimiento Facial**: Identificación automática de estudiantes
- **Detección de Gestos**: Detección de manos levantadas para preguntas
- **Síntesis de Voz**: Comunicación verbal natural con estudiantes
- **Reconocimiento de Voz**: Escucha y procesamiento de preguntas
- **Inteligencia Artificial**: Respuestas inteligentes usando OpenAI
- **Evaluación Automática**: Evaluación de respuestas de estudiantes
- **Gestión de Exámenes**: Diferentes tipos de evaluaciones

### 📚 **Modos de Operación**
1. **Modo Diagnóstico**: Identificación inicial de usuarios
2. **Modo Presentación**: Explicación interactiva con preguntas
3. **Modo Examen**: Evaluaciones estructuradas por tema

## 🛠️ Tecnologías Utilizadas

- **Python 3.10+**
- **OpenCV** - Visión por computadora
- **MediaPipe** - Detección de gestos
- **Face Recognition** - Reconocimiento facial
- **OpenAI GPT** - Inteligencia artificial
- **PyTTSx3** - Síntesis de voz
- **Speech Recognition** - Reconocimiento de voz
- **PyMuPDF** - Procesamiento de PDFs
- **Tesseract OCR** - Reconocimiento de texto

## 📋 Requisitos del Sistema

### Software
- Python 3.10 o superior
- Tesseract OCR
- Cámara web
- Micrófono

### Hardware Recomendado
- CPU: Intel i5 o superior
- RAM: 8GB o más
- Cámara: 720p o superior
- Micrófono: Calidad estándar

## 🔧 Instalación

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd BOT-UNITEC
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Tesseract OCR
- **Windows**: Descargar desde [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr`
- **Mac**: `brew install tesseract`

### 5. Configurar OpenAI API
Editar `config/settings.py` y agregar tu clave API de OpenAI:
```python
self.openai_api_key = "tu-clave-api-aqui"
```

## 🚀 Uso Rápido

### Ejecutar Sistema Completo
```bash
python main_organized.py
```

### Ejecutar Ejemplos de Módulos
```bash
python ejemplo_uso_modulos.py
```

### Usar Módulos Individuales
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

## 📁 Estructura del Proyecto

Ver [ESTRUCTURA_PROYECTO.md](ESTRUCTURA_PROYECTO.md) para detalles completos de la organización del código.

## 🎯 Casos de Uso

### 1. **Clase de Robótica Médica**
- ADAI presenta diapositivas sobre robots médicos
- Detecta estudiantes que levantan la mano
- Responde preguntas usando IA
- Evalúa respuestas de estudiantes

### 2. **Examen de Exoesqueletos**
- Muestra QR para acceso al examen
- Pregunta específicas sobre exoesqueletos
- Evalúa respuestas automáticamente
- Proporciona retroalimentación

### 3. **Diagnóstico de IoMT**
- Identifica estudiantes en la clase
- Presenta material sobre Internet de las Cosas Médicas
- Hace preguntas aleatorias
- Mantiene estadísticas de participación

## 🔧 Configuración Avanzada

### Personalizar Preguntas
Editar `exams/question_manager.py`:
```python
def _get_default_questions(self) -> List[str]:
    return [
        "Tu pregunta personalizada aquí",
        "Otra pregunta...",
        # Agregar más preguntas
    ]
```

### Cambiar Configuración de Cámara
Editar `config/settings.py`:
```python
self.camera_config = {
    'fps': 30,           # Frames por segundo
    'buffer_size': 1,    # Tamaño del buffer
    'fourcc': 'MJPG'     # Formato de compresión
}
```

### Ajustar Detección de Gestos
```python
self.gesture_config = {
    'hand_detection_confidence': 0.85,  # Sensibilidad
    'hand_tracking_confidence': 0.7,    # Precisión
    'max_hands': 4,                     # Máximo manos
    'gesture_cooldown': 3               # Tiempo entre detecciones
}
```

## 🐛 Solución de Problemas

### Error: "No se pudo abrir la cámara"
- Verificar que la cámara esté conectada
- Comprobar permisos de acceso
- Cambiar índice de cámara en el código

### Error: "Tesseract no encontrado"
- Instalar Tesseract OCR
- Verificar ruta en `config/settings.py`
- Windows: `r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

### Error: "OpenAI API key inválida"
- Verificar clave API en `config/settings.py`
- Comprobar conexión a internet
- Revisar límites de uso de OpenAI

### Error: "No se pudo inicializar TTS"
- Verificar instalación de PyTTSx3
- Comprobar voces del sistema
- Windows: Instalar Microsoft Speech Platform

## 📊 Rendimiento

### Optimizaciones Recomendadas
- **CPU**: Usar procesador multi-core
- **GPU**: Opcional para aceleración de visión
- **RAM**: Mínimo 8GB para procesamiento fluido
- **Almacenamiento**: SSD para acceso rápido a archivos

### Monitoreo de Recursos
```python
import psutil
import time

def monitor_resources():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    print(f"CPU: {cpu_percent}%, RAM: {memory_percent}%")
```

## 🤝 Contribución

### Guías de Desarrollo
1. Seguir la estructura modular existente
2. Documentar nuevas funcionalidades
3. Mantener compatibilidad con módulos existentes
4. Agregar tests para nuevas funciones

### Reportar Bugs
- Describir el problema detalladamente
- Incluir información del sistema
- Proporcionar logs de error
- Especificar pasos para reproducir

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.

## 👥 Autores

- **Desarrollador Principal**: [Tu Nombre]
- **Contribuidores**: [Lista de contribuidores]

## 📞 Soporte

- **Email**: [tu-email@ejemplo.com]
- **Issues**: [GitHub Issues]
- **Documentación**: [Wiki del proyecto]

## 🔄 Historial de Versiones

### v2.0.0 - Estructura Modular
- Reorganización completa del código
- Separación en módulos específicos
- Mejora en mantenibilidad
- Documentación completa

### v1.0.0 - Versión Original
- Funcionalidades básicas implementadas
- Sistema monolítico
- Configuración básica

---

**¡Gracias por usar ADAI! 🤖✨** 