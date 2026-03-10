# 📁 Estructura Completa de Clase Generada por Class Builder

## 🎯 Ejemplo: "Mi Clase de Robótica"

Cuando el Class Builder genera una clase completa, crea la siguiente estructura:

```
clases/
└── mi_clase_de_robótica_clase/
    ├── mi_clase_de_robótica_clase.py    # 🐍 Código principal ejecutable
    ├── class_config.json                # ⚙️ Configuración de la clase
    ├── requirements.txt                  # 📦 Dependencias Python
    ├── README.md                         # 📖 Documentación completa
    ├── qrs/                             # 📱 Códigos QR
    │   ├── diagnostic_qr.jpeg          # QR evaluación diagnóstica
    │   ├── final_exam_qr.jpeg           # QR examen final
    │   ├── pruebadiagnosticaRobotsMedicos.jpeg  # QR por defecto
    │   └── RobotsMedicosExamenI.jpeg    # QR examen por defecto
    ├── pdfs/                            # 📚 Archivos PDF
    │   ├── class_content.pdf            # PDF seleccionado por usuario
    │   └── RobotMedico.pdf              # PDF por defecto según materia
    ├── images/                          # 🖼️ Imágenes
    ├── faces/                           # 👤 Datos de reconocimiento facial
    ├── resources/                       # 📁 Otros recursos
    ├── sequences/                       # 🤖 Secuencias del robot
    └── exams/                           # 📝 Archivos de examen
```

## 🔧 Archivos Generados

### 1. **Código Principal** (`mi_clase_de_robótica_clase.py`)
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mi Clase de Robótica
Materia: Robots Médicos
Generado por ADAI Class Builder el 2025-01-30 10:30:00

Clase automática usando demo_sequence_manager
"""

import cv2
import os
import time
import multiprocessing
from multiprocessing import Process, Value
import sys

# Configurar path para importar desde demo_sequence_manager
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.join(current_dir, "main")
if main_dir not in sys.path:
    sys.path.insert(0, main_dir)

# Importar funciones directamente desde demo_sequence_manager
try:
    from demo_sequence_manager import (
        initialize_tts, speak_with_animation, listen,
        verify_camera_for_iriun, camera_process, identify_users, load_known_faces,
        show_diagnostic_qr, show_final_exam_qr,
        show_pdf_page_in_opencv, extract_text_from_pdf, 
        explain_slides_with_random_questions, explain_slides_with_sequences,
        RandomQuestionManager, evaluate_student_answer, process_question,
        execute_esp32_sequence, summarize_text, ask_openai
    )
    print("✅ Funciones importadas desde demo_sequence_manager")
except ImportError as e:
    print(f"❌ Error importando funciones: {e}")
    print("⚠️ Asegúrate de que demo_sequence_manager.py esté en la carpeta main/")
    raise

def main():
    """Función principal que ejecuta la clase completa"""
    # ... código completo de la clase ...
```

### 2. **Configuración** (`class_config.json`)
```json
{
  "title": "Mi Clase de Robótica",
  "subject": "Robots Médicos",
  "description": "Una clase sobre robots en medicina",
  "duration": "45 minutos",
  "created_at": "2025-01-30T10:30:00",
  "main_file": "mi_clase_de_robótica_clase.py",
  "folder_name": "mi_clase_de_robótica_clase",
  "resources": {
    "diagnostic_qr": "qrs/diagnostic_qr.jpeg",
    "class_pdf": "pdfs/class_content.pdf",
    "final_exam_qr": "qrs/final_exam_qr.jpeg"
  },
  "phases": {
    "diagnostic": true,
    "class_content": true,
    "final_exam": true
  }
}
```

### 3. **Dependencias** (`requirements.txt`)
```
opencv-python>=4.5.0
pyttsx3>=2.90
speech_recognition>=3.8.1
face_recognition>=1.3.0
mediapipe>=0.8.0
PyMuPDF>=1.20.0
openai>=0.27.0
requests>=2.25.0
numpy>=1.21.0
Pillow>=8.3.0
```

### 4. **Documentación** (`README.md`)
```markdown
# Mi Clase de Robótica

## Información de la Clase
- **Materia:** Robots Médicos
- **Descripción:** Una clase sobre robots en medicina
- **Archivo principal:** `mi_clase_de_robótica_clase.py`
- **Generado por:** ADAI Class Builder
- **Fecha de creación:** 2025-01-30 10:30:00

## Cómo Ejecutar la Clase

### Prerrequisitos
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Asegúrate de que `demo_sequence_manager.py` esté en la carpeta `main/`

### Ejecución
```bash
python mi_clase_de_robótica_clase.py
```

## Flujo de la Clase

1. **FASE 1: Evaluación Diagnóstica**
   - Muestra QR code para prueba inicial
   - Tiempo configurable de visualización

2. **FASE 2: Inicio de Clase**
   - Saludo de ADAI con texto a voz
   - Introducción al tema seleccionado

3. **FASE 3: Contenido Principal**
   - Presentación de diapositivas del PDF
   - Explicación automática de cada slide
   - Preguntas aleatorias durante la presentación

4. **FASE 4: Examen Final**
   - QR code del examen correspondiente
   - Mensaje de finalización
```

## 🚀 Características del Class Builder Mejorado

### ✅ **Estructura Completa**
- **Carpetas organizadas** por tipo de recurso
- **Archivos de configuración** para personalización
- **Documentación automática** con README
- **Dependencias listadas** en requirements.txt

### ✅ **Recursos Automáticos**
- **Copia recursos seleccionados** por el usuario
- **Incluye recursos por defecto** según la materia
- **Organiza archivos** en carpetas apropiadas
- **Mantiene referencias** en configuración

### ✅ **Código Ejecutable**
- **Python válido** sin errores de sintaxis
- **Imports correctos** desde demo_sequence_manager
- **Flujo completo** de 4 fases
- **Manejo de errores** robusto

### ✅ **Metadata Actualizada**
- **Registro automático** en classes_metadata.json
- **Información completa** de la clase
- **Rutas correctas** a todos los archivos
- **Timestamps** de creación y modificación

## 🎯 **Resultado Final**

El Class Builder ahora genera una **carpeta completa de clase** que incluye:

1. **🐍 Código ejecutable** - Listo para correr
2. **📁 Estructura organizada** - Carpetas por tipo de recurso
3. **⚙️ Configuración** - Archivos JSON y TXT
4. **📖 Documentación** - README completo
5. **📦 Dependencias** - requirements.txt
6. **🔄 Metadata** - Registro en sistema
7. **📱 Recursos** - QRs, PDFs, imágenes
8. **🤖 Secuencias** - Para robot ESP32

**¡La clase está lista para ejecutarse inmediatamente!**
