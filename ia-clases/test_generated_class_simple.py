#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mi Clase de Prueba
Materia: Robots Médicos
Generado por ADAI Class Builder el 2025-09-15 16:40:19

Clase automática usando estructura modular
"""

import cv2
import os
import time
import multiprocessing
from multiprocessing import Process, Value

# Agregar el directorio de módulos al path
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
# Los módulos están en ia-clases/modules/
# Desde: ia-clases/clases/mi_clase_de_prueba/
# Hacia: ia-clases/modules/
parent_dir = os.path.dirname(current_dir)  # ia-clases/clases/
parent_parent_dir = os.path.dirname(parent_dir)  # ia-clases/
modules_dir = os.path.join(parent_parent_dir, "modules")  # ia-clases/modules/
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)
print(f"🔍 Agregando módulos desde: {modules_dir}")

# Import modular functions
try:
    from modules.config import client, script_dir, faces_dir, QR_PATHS, QUESTION_BANK, QUESTION_BANK_CHEM
    from modules.speech import initialize_tts, speak_with_animation, listen
    from modules.camera import verify_camera_for_iriun, camera_process, identify_users, load_known_faces
    from modules.qr import show_diagnostic_qr, show_final_exam_qr
    from modules.slides import show_pdf_page_in_opencv, extract_text_from_pdf, explain_slides_with_random_questions, explain_slides_with_sequences
    from modules.questions import RandomQuestionManager, evaluate_student_answer, process_question
    from modules.esp32 import execute_esp32_sequence
    from modules.utils import summarize_text, ask_openai
    from modules.class_config import get_class_config
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("🔧 Intentando importar desde rutas alternativas...")
    
    # Rutas alternativas para los módulos
    try:
        from config import client, script_dir, faces_dir, QR_PATHS, QUESTION_BANK, QUESTION_BANK_CHEM
        from speech import initialize_tts, speak_with_animation, listen
        from camera import verify_camera_for_iriun, camera_process, identify_users, load_known_faces
        from qr import show_diagnostic_qr, show_final_exam_qr
        from slides import show_pdf_page_in_opencv, extract_text_from_pdf, explain_slides_with_random_questions, explain_slides_with_sequences
        from questions import RandomQuestionManager, evaluate_student_answer, process_question
        from esp32 import execute_esp32_sequence
        from utils import summarize_text, ask_openai
        print("✅ Módulos importados desde rutas alternativas")
    except ImportError as e2:
        print(f"❌ Error importando desde rutas alternativas: {e2}")
        print("🔧 Intentando importar desde el main original...")
        
        # Última opción: importar desde el main original
        try:
            main_dir = os.path.join(parent_parent_dir, "clases", "main")
            if main_dir not in sys.path:
                sys.path.insert(0, main_dir)
            
            # Importar funciones del main original
            import main
            
            # Mapear funciones del main a las variables esperadas
            client = main.client
            script_dir = main.script_dir
            faces_dir = main.faces_dir
            QR_PATHS = main.QR_PATHS
            QUESTION_BANK = main.QUESTION_BANK
            QUESTION_BANK_CHEM = main.QUESTION_BANK_CHEM
            
            # Mapear funciones
            initialize_tts = main.initialize_tts
            speak_with_animation = main.speak_with_animation
            listen = main.listen
            verify_camera_for_iriun = main.verify_camera_for_iriun
            camera_process = main.camera_process
            identify_users = main.identify_users
            load_known_faces = main.load_known_faces
            show_diagnostic_qr = main.show_diagnostic_qr
            show_final_exam_qr = main.show_final_exam_qr
            show_pdf_page_in_opencv = main.show_pdf_page_in_opencv
            extract_text_from_pdf = main.extract_text_from_pdf
            explain_slides_with_random_questions = main.explain_slides_with_random_questions
            explain_slides_with_sequences = main.explain_slides_with_sequences
            RandomQuestionManager = main.RandomQuestionManager
            evaluate_student_answer = main.evaluate_student_answer
            process_question = main.process_question
            execute_esp32_sequence = main.execute_esp32_sequence
            summarize_text = main.summarize_text
            ask_openai = main.ask_openai
            
            print("✅ Funciones importadas desde main original")
            
        except ImportError as e3:
            print(f"❌ Error importando desde main original: {e3}")
            raise ImportError("No se pudieron importar los módulos necesarios desde ninguna fuente")

# ======================
#  CONFIGURACIÓN DE LA CLASE
# ======================
CLASS_NAME = "mi_clase_de_prueba"

# Cargar configuración desde el sistema modular
try:
    CLASS_CONFIG = get_class_config(CLASS_NAME)
except Exception as e:
    print(f"⚠️ No se pudo cargar configuración modular: {e}")
    # Configuración de respaldo si no se puede cargar la modular
    CLASS_CONFIG = {
        "name": "mi_clase_de_prueba",
        "title": "Mi Clase de Prueba",
        "subject": "Robots Médicos",
        "diagnostic_qr": "test_diagnostic.jpg",
        "pdf_path": "test_presentation.pdf",
        "demo_pdf_path": "test_demo.pdf",
        "final_exam_qr": "test_exam.jpg",
        "use_diagnostic": True,
        "use_pdf": True,
        "use_demo": true,
        "use_final_exam": True
    }

# Demo sequences configuration
DEMO_SEQUENCES = [
    {
        'page': 1,
        'sequence_file': '/path/to/sequence1.json',
        'sequence_name': 'Saludo',
        'description': 'Secuencia de saludo inicial',
        'enabled': True
    },
    {
        'page': 3,
        'sequence_file': '/path/to/sequence2.json',
        'sequence_name': 'Gesto',
        'description': 'Gesto de explicación',
        'enabled': True
    }
]

class mi_clase_de_prueba:
    """
    Mi Clase de Prueba
    
    Materia: Robots Médicos
    Generado por ADAI Class Builder
    """
    
    def __init__(self):
        self.config = CLASS_CONFIG
        self.engine = None
        self.current_users = []
        self.known_faces = {}
        self.hand_raised_counter = None
        self.current_slide_num = None
        self.exit_flag = None
        self.current_hand_raiser = None
        self.camera_proc = None
        
    def initialize_systems(self):
        """Initialize TTS and other systems"""
        print(f"🚀 Inicializando sistemas de {self.config['name']}")
        
        # Create multiprocessing variables
        self.hand_raised_counter = multiprocessing.Value('i', 0)
        self.current_slide_num = multiprocessing.Value('i', 1)
        self.exit_flag = multiprocessing.Value('i', 0)
        self.current_hand_raiser = multiprocessing.Value('i', -1)
        
        # Initialize TTS
        self.engine = initialize_tts()
        if not self.engine:
            print("❌ No se pudo inicializar el motor TTS")
            return False
            
        # Create faces directory
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
            
        return True
    
    def run_diagnostic_phase(self):
        """Run diagnostic test phase if enabled"""
        if not self.config['use_diagnostic'] or not self.config['diagnostic_qr']:
            return True
            
        print("\n" + "="*50)
        print("📱 FASE 1: EVALUACIÓN DIAGNÓSTICA")
        print("="*50)
        
        diagnostic_qr = self.config['diagnostic_qr']
        print(f"🔍 Mostrando QR diagnóstico: {diagnostic_qr}")
        
        if os.path.exists(diagnostic_qr):
            return show_diagnostic_qr(diagnostic_qr, display_time=40)
        else:
            print(f"⚠️ No se encontró: {diagnostic_qr}")
            return True
    
    def run_class_initialization(self):
        """Initialize class and identify users"""
        print("\n" + "="*50)
        print("🤖 FASE 2: INICIO DE CLASE")
        print("="*50)
        
        # Create window for animated face
        cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("ADAI Robot Face", 600, 400)
        
        # Initial greeting
        speak_with_animation(self.engine, f"Hola, soy ADAI. Bienvenidos a la clase: {self.config['title']}")
        
        # Verify camera
        if not verify_camera_for_iriun():
            print("⚠️ Problemas detectados con la cámara.")
        
        # Identify users
        print("🔍 Identificando usuarios de izquierda a derecha...")
        self.current_users, _ = identify_users(self.engine, self.current_slide_num, self.exit_flag)
        
        # Load known faces
        self.known_faces = load_known_faces()
        
        # Start camera process
        self.camera_proc = Process(
            target=camera_process,
            args=(self.hand_raised_counter, self.current_slide_num, self.exit_flag, self.current_hand_raiser, self.current_users)
        )
        self.camera_proc.daemon = True
        self.camera_proc.start()
        
        print("⏳ Esperando a que la cámara se inicialice...")
        time.sleep(3)
        
        return True
    
    def run_pdf_phase(self):
        """Run PDF presentation phase if enabled"""
        if not self.config['use_pdf'] or not self.config['pdf_path']:
            return True
            
        print("\n" + "="*50)
        print("📚 FASE 3: PRESENTACIÓN DE CONTENIDO")
        print("="*50)
        
        pdf_path = self.config['pdf_path']
        if not os.path.exists(pdf_path):
            print(f"❌ No se encontró el PDF: {pdf_path}")
            return False
            
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text:
            print("❌ No se pudo leer el PDF")
            return False
            
        # Start presentation
        speak_with_animation(self.engine, f"Ahora comenzaremos con la presentación sobre {self.config['subject']}.")
        
        # Explain slides with random questions
        return explain_slides_with_random_questions(
            self.engine, pdf_path, pdf_text, self.current_users,
            self.hand_raised_counter, self.current_slide_num, self.exit_flag, 
            self.known_faces, self.current_hand_raiser
        )
    
    def run_demo_phase(self):
        """Run demo phase if enabled"""
        if not self.config['use_demo'] or not self.config['demo_pdf_path']:
            return True
            
        print("\n" + "="*50)
        print("🎬 FASE 4: DEMOSTRACIÓN PRÁCTICA")
        print("="*50)
        
        demo_pdf_path = self.config['demo_pdf_path']
        if not os.path.exists(demo_pdf_path):
            print(f"❌ No se encontró el PDF de demo: {demo_pdf_path}")
            return False
            
        # Extract text from demo PDF
        demo_pdf_text = extract_text_from_pdf(demo_pdf_path)
        if not demo_pdf_text:
            print("❌ No se pudo leer el PDF de demo")
            return False
            
        # Start demo presentation
        speak_with_animation(self.engine, "Ahora realizaremos una demostración práctica paso a paso.")
        
        # Generate sequence mapping from demo sequences
        sequence_mapping = {}
        if hasattr(self, 'demo_sequences') and self.demo_sequences:
            for seq in self.demo_sequences:
                page = seq.get('page', 1)
                sequence_name = seq.get('sequence_name', 'Rutina1')
                sequence_mapping[page] = sequence_name
        
        # Explain slides with sequences
        return explain_slides_with_sequences(
            self.engine, demo_pdf_path, demo_pdf_text, self.current_users,
            self.hand_raised_counter, self.current_slide_num, self.exit_flag, 
            self.known_faces, self.current_hand_raiser, sequence_mapping
        )
    
    def run_final_exam_phase(self):
        """Run final exam phase if enabled"""
        if not self.config['use_final_exam'] or not self.config['final_exam_qr']:
            return True
            
        print("\n" + "="*60)
        print("🎓 FASE FINAL: EXAMEN")
        print("="*60)
        
        final_exam_qr = self.config['final_exam_qr']
        print(f"🔍 Mostrando QR examen: {final_exam_qr}")
        
        if os.path.exists(final_exam_qr):
            # Message from ADAI
            speak_with_animation(self.engine, "Excelente trabajo. Ahora es momento del examen final.")
            speak_with_animation(self.engine, "Por favor, escanea el código QR que aparecerá en pantalla.")
            
            # Show exam QR
            show_final_exam_qr(final_exam_qr, display_time=40)
            
            # Final message
            speak_with_animation(self.engine, "Perfecto. ¡Mucha suerte en el examen!")
            speak_with_animation(self.engine, f"Gracias por participar en la clase: {self.config['title']}. ¡Hasta la próxima!")
            return True
        else:
            print(f"⚠️ No se encontró: {final_exam_qr}")
            speak_with_animation(self.engine, "La clase ha terminado. ¡Gracias por participar!")
            return True
            
    def cleanup(self):
        """Clean up resources"""
        print("🛑 Finalizando clase")
        if self.exit_flag:
            self.exit_flag.value = 1
        
        if self.camera_proc and self.camera_proc.is_alive():
            print("⏳ Esperando procesos...")
            self.camera_proc.join(timeout=3)
            
            if self.camera_proc.is_alive():
                self.camera_proc.terminate()
                self.camera_proc.join(timeout=1)
        
        cv2.destroyAllWindows()
        print("✅ Clase finalizada")
    
    def run_complete_class(self):
        """Run the complete class workflow"""
        try:
            print(f"🚀 Iniciando clase: {self.config['title']}")
            
            # Initialize systems
            if not self.initialize_systems():
                return False
            
            # Run diagnostic phase
            if not self.run_diagnostic_phase():
                print("⚠️ Error en fase diagnóstica, continuando...")
            
            # Run class initialization
            if not self.run_class_initialization():
                print("❌ Error en inicialización de clase")
                return False
            
            # Run PDF phase
            if not self.run_pdf_phase():
                print("⚠️ Error en fase de presentación, continuando...")
            
            # Run demo phase
            if not self.run_demo_phase():
                print("⚠️ Error en fase de demo, continuando...")
            
            # Run final exam phase
            if not self.run_final_exam_phase():
                print("⚠️ Error en fase de examen, continuando...")
            
            return True
            
        except Exception as e:
            print(f"❌ Error ejecutando clase: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()

def main():
    """Main function to run the class"""
    try:
        # Create and run the class
        class_instance = mi_clase_de_prueba()
        success = class_instance.run_complete_class()
        
        if success:
            print("✅ Clase completada exitosamente")
        else:
            print("❌ La clase tuvo errores")
            
    except Exception as e:
        print(f"❌ Error en main: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
