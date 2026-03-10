"""
Módulo de configuración y constantes para ADAI
==============================================

Contiene todas las configuraciones, rutas y constantes utilizadas
en el sistema ADAI.
"""

import os
import sys
import openai
from dotenv import load_dotenv

# Ensure paths.py is importable (it lives in ia-clases/)
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)
from paths import get_data_dir

# ======================
#  CONFIGURACIÓN OPENAI
# ======================
# Cargar variables de entorno desde .env en el directorio de datos
load_dotenv(os.path.join(get_data_dir(), ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Cliente de OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Directorio del script (se actualizará dinámicamente)
script_dir = None

def set_script_dir(path):
    """Establecer el directorio del script"""
    global script_dir
    script_dir = path

def get_script_dir():
    """Obtener el directorio del script"""
    return script_dir

# Directorio de caras (se actualizará dinámicamente)
faces_dir = None

def set_faces_dir(path):
    """Establecer el directorio de caras"""
    global faces_dir
    faces_dir = path

def get_faces_dir():
    """Obtener el directorio de caras"""
    return faces_dir

# ======================
#  RUTAS DE LOS QR
# ======================
def get_qr_paths(script_dir):
    """Obtiene las rutas de los códigos QR basadas en el directorio del script"""
    return {
        'diagnostic': os.path.join(script_dir, "RobotsMedicosExamen", "pruebadiagnosticaRobotsMedicos.jpeg"),
        'diagnostic_Exoesqueletos': os.path.join(script_dir, "ExoesqueletosExamen", "pruebadiagnosticaExoesqueletos.jpeg"),
        'diagnostic_IoMT': os.path.join(script_dir, "DesafiosIoMTExamen", "pruebadiagnosticaDesafiosIoMT.jpeg"),
        'final_examI': os.path.join(script_dir, "RobotsMedicosExamen", "RobotsMedicosExamenI.jpeg"),
        'final_examII': os.path.join(script_dir, "RobotsMedicosExamen", "RobotsMedicosExamenII.jpeg"),
        'final_examExoI': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenI.jpeg"),
        'final_examExoII': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenII.jpeg"),
        'final_examExoIII': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenIII.jpeg"),
        'final_examExoIV': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenIV.jpeg"),
        'final_examExoV': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenV.jpeg"),
        'final_examIoMT': os.path.join(script_dir, "DesafiosIoMTExamen", "DesafiosIoMTExamenI.png"),
        "examen_quimica": os.path.join(script_dir, "exams", "Examen Quimica.png"),
        "diagnostico_quimica": os.path.join(script_dir, "exams", "DiagnosticoQuimica.png")
    }

# ======================
#  BANCO DE PREGUNTAS
# ======================
QUESTION_BANK = [
    "La neutralización ocurre cuando un ácido y una base reaccionan. Verdadero o falso?",
    "El bicarbonato de sodio es una sustancia básica. Verdadero o falso?",
    "El vinagre contiene ácido acético. Verdadero o falso?",
    "La col morada puede actuar como indicador de pH. Verdadero o falso?",
    "La reacción entre ácido y bicarbonato libera oxígeno. Verdadero o falso?",
    "El pH neutro corresponde aproximadamente al valor 7. Verdadero o falso?",
    "La fenolftaleína se vuelve rosa en medio ácido. Verdadero o falso?"
]

QUESTION_BANK_CHEM = [
    "La neutralización produce siempre agua y una sal. Verdadero o falso?",
    "El bicarbonato de sodio reacciona con ácidos liberando dióxido de carbono (CO₂). Verdadero o falso?",
    "El jugo de limón contiene ácido cítrico. Verdadero o falso?",
    "El papel tornasol cambia de color según el pH. Verdadero o falso?",
    "Un pH menor que 7 indica una sustancia ácida. Verdadero o falso?",
    "El cambio de color de la col morada se debe a pigmentos llamados antocianinas. Verdadero o falso?",
    "La efervescencia en la reacción ácido + bicarbonato se debe a la liberación de nitrógeno. Verdadero o falso?"
]

# ======================
#  CONFIGURACIÓN DE CÁMARA
# ======================
CAMERA_CONFIGS = [
    (0, None, "iriun/default"),
    (0, "cv2.CAP_DSHOW", "DirectShow"),
    (1, None, "índice 1"),
    (2, None, "índice 2")
]

# ======================
#  CONFIGURACIÓN DE RESOLUCIÓN
# ======================
RESOLUTIONS_TO_TRY = [
    (1920, 1080, "Full HD"),
    (1280, 720, "HD"),
    (1024, 768, "XGA"),
    (640, 480, "VGA")
]

# ======================
#  CONFIGURACIÓN DE MEDIAPIPE
# ======================
MEDIAPIPE_CONFIG = {
    'hands': {
        'static_image_mode': False,
        'max_num_hands': 8,
        'min_detection_confidence': 0.3,
        'min_tracking_confidence': 0.2
    },
    'face_detection': {
        'model_selection': 1,
        'min_detection_confidence': 0.05
    }
}

# ======================
#  CONFIGURACIÓN DE TESSERACT
# ======================
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ======================
#  CONFIGURACIÓN DE ESP32
# ======================
ESP32_DEFAULT_CONFIG = {
    'host': '192.168.1.100',
    'port': 80
}

# ======================
#  CONFIGURACIÓN DE TTS
# ======================
TTS_VOICE = 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0'

# ======================
#  CONFIGURACIÓN DE RECONOCIMIENTO DE VOZ
# ======================
SPEECH_CONFIG = {
    'language': 'es-ES',
    'timeout': 5,
    'energy_threshold': 400,
    'pause_threshold': 0.8
}

# ======================
#  CONFIGURACIÓN DE DETECCIÓN FACIAL
# ======================
FACE_DETECTION_CONFIG = {
    'tolerance': 0.55,
    'min_face_area_ratio': 0.00005,  # Para caras a 3-5m
    'max_face_area_ratio': 0.1,
    'min_face_size': 15,
    'max_face_size_ratio': 0.6
}

# ======================
#  CONFIGURACIÓN DE DETECCIÓN DE MANOS
# ======================
HAND_DETECTION_CONFIG = {
    'max_consecutive': 6,
    'hand_raise_threshold': -0.03,
    'min_vertical_clearance': 20,
    'max_horizontal_distance_ratio': 1.5,
    'max_vertical_clearance_ratio': 3
}

# ======================
#  CONFIGURACIÓN DE VENTANAS
# ======================
WINDOW_CONFIG = {
    'robot_face': {'width': 600, 'height': 400},
    'presentation': {'width': 800, 'height': 600},
    'camera': {'width': 1000, 'height': 700},
    'qr_diagnostic': {'width': 1000, 'height': 700},
    'qr_exam': {'width': 1000, 'height': 700}
}

# ======================
#  CONFIGURACIÓN DE COLORES
# ======================
COLORS = {
    'student_colors': [
        (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (128, 128, 255), (255, 128, 0)
    ],
    'qr_diagnostic': {
        'bg_color': (245, 245, 245),
        'header_color': (41, 128, 185),
        'text_color': (52, 73, 94),
        'accent_color': (231, 76, 60)
    },
    'qr_exam': {
        'bg_color': (240, 248, 255),
        'header_color': (25, 25, 112),
        'text_color': (25, 25, 112),
        'accent_color': (220, 20, 60),
        'success_color': (34, 139, 34)
    }
}
