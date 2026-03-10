"""
Configuración centralizada del sistema
"""
import os
import sys
import openai
from typing import Dict, Any
from dotenv import load_dotenv

# paths.py lives in the parent directory (ia-clases/); ensure it is importable
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)
from paths import get_data_dir

class Settings:
    """Clase para manejar la configuración del sistema."""

    def __init__(self):
        """Inicializa la configuración."""
        self.base_dir = get_data_dir()
        self._load_config()
    
    def _load_config(self):
        """Carga la configuración."""
        # Cargar variables de entorno desde .env
        load_dotenv(os.path.join(self.base_dir, ".env"))

        # Configuración de OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
    
        
        # Configuración de Tesseract OCR
        self.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Configuración de ventanas
        self.window_config = {
            'face_window': {
                'name': "ADAI Robot Face",
                'width': 600,
                'height': 400
            },
            'presentation_window': {
                'name': "Presentacion",
                'width': 800,
                'height': 600
            },
            'camera_window': {
                'name': "Clase Virtual",
                'width': 640,
                'height': 480
            }
        }
        
        # Configuración de la cámara
        self.camera_config = {
            'fps': 30,
            'buffer_size': 1,
            'fourcc': 'MJPG'
        }
        
        # Configuración de detección de gestos
        self.gesture_config = {
            'hand_detection_confidence': 0.85,
            'hand_tracking_confidence': 0.7,
            'max_hands': 4,
            'max_consecutive_frames': 8,
            'gesture_cooldown': 3
        }
        
        # Rutas de archivos
        self.paths = {
            'faces_dir': os.path.join(self.base_dir, "faces"),
            'temp_dir': os.path.join(self.base_dir, "temp"),
            'data_dir': os.path.join(self.base_dir, "data"),
            'exams': {
                'robots_medicos': os.path.join(self.base_dir, "RobotsMedicosExamen"),
                'exoesqueletos': os.path.join(self.base_dir, "ExoesqueletosExamen"),
                'iomt': os.path.join(self.base_dir, "DesafiosIoMTExamen")
            }
        }
        
        # Rutas de QR
        self.qr_paths = {
            'diagnostic': os.path.join(self.paths['exams']['robots_medicos'], "pruebadiagnosticaRobotsMedicos.jpeg"),
            'diagnostic_Exoesqueletos': os.path.join(self.paths['exams']['exoesqueletos'], "pruebadiagnosticaExoesqueletos.jpeg"),
            'diagnostic_IoMT': os.path.join(self.paths['exams']['iomt'], "pruebadiagnosticaDesafiosIoMT.jpeg"),
            'final_examI': os.path.join(self.paths['exams']['robots_medicos'], "RobotsMedicosExamenI.jpeg"),
            'final_examII': os.path.join(self.paths['exams']['robots_medicos'], "RobotsMedicosExamenII.jpeg"),
            'final_examExoI': os.path.join(self.paths['exams']['exoesqueletos'], "ExoesqueletosExamenI.jpeg"),
            'final_examExoII': os.path.join(self.paths['exams']['exoesqueletos'], "ExoesqueletosExamenII.jpeg"),
            'final_examExoIII': os.path.join(self.paths['exams']['exoesqueletos'], "ExoesqueletosExamenIII.jpeg"),
            'final_examExoIV': os.path.join(self.paths['exams']['exoesqueletos'], "ExoesqueletosExamenIV.jpeg"),
            'final_examExoV': os.path.join(self.paths['exams']['exoesqueletos'], "ExoesqueletosExamenV.jpeg"),
            'final_examIoMT': os.path.join(self.paths['exams']['iomt'], "DesafiosIoMTExamenI.png")
        }
    
    def setup_directories(self) -> bool:
        """
        Configura los directorios necesarios.
        
        Returns:
            bool: True si se configuraron correctamente
        """
        try:
            print("🏗️ Configurando directorios del sistema...")
            
            # Crear directorios principales
            for dir_path in self.paths.values():
                if isinstance(dir_path, dict):
                    for sub_dir in dir_path.values():
                        if not os.path.exists(sub_dir):
                            os.makedirs(sub_dir)
                            print(f"✅ Creado directorio: {sub_dir}")
                else:
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                        print(f"✅ Creado directorio: {dir_path}")
            
            print("✅ Configuración de directorios completada")
            return True
            
        except Exception as e:
            print(f"❌ Error al configurar directorios: {e}")
            return False
    
    def get_openai_client(self):
        """Obtiene el cliente de OpenAI."""
        return self.openai_client
    
    def get_qr_path(self, qr_type: str) -> str:
        """
        Obtiene la ruta de un QR específico.
        
        Args:
            qr_type: Tipo de QR
            
        Returns:
            str: Ruta del QR
        """
        return self.qr_paths.get(qr_type, "")
    
    def get_window_config(self, window_type: str) -> Dict[str, Any]:
        """
        Obtiene la configuración de una ventana.
        
        Args:
            window_type: Tipo de ventana
            
        Returns:
            Dict[str, Any]: Configuración de la ventana
        """
        return self.window_config.get(window_type, {})
    
    def get_camera_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de la cámara."""
        return self.camera_config
    
    def get_gesture_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de detección de gestos."""
        return self.gesture_config

# Instancia global de configuración
settings = Settings() 