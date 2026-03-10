#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mi Clase de Prueba
Materia: Robots Médicos
Generado por ADAI Class Builder el 2025-01-15 10:30:00

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
parent_dir = os.path.dirname(current_dir)
parent_parent_dir = os.path.dirname(parent_dir)
modules_dir = os.path.join(parent_parent_dir, "modules")
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)
print(f"🔍 Agregando módulos desde: {modules_dir}")

# Import modular functions with fallback
try:
    from modules.config import client, script_dir, faces_dir, QR_PATHS, QUESTION_BANK, QUESTION_BANK_CHEM
    from modules.speech import initialize_tts, speak_with_animation, listen
    from modules.camera import verify_camera_for_iriun, camera_process, identify_users, load_known_faces
    from modules.qr import show_diagnostic_qr, show_final_exam_qr
    from modules.slides import show_pdf_page_in_opencv, extract_text_from_pdf, explain_slides_with_random_questions, explain_slides_with_sequences
    from modules.questions import RandomQuestionManager, evaluate_student_answer, process_question
    from modules.esp32 import execute_esp32_sequence
    from modules.utils import summarize_text, ask_openai
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("🔧 Intentando importar desde rutas alternativas...")
    
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
        
        try:
            main_dir = os.path.join(parent_parent_dir, "clases", "main")
            if main_dir not in sys.path:
                sys.path.insert(0, main_dir)
            
            import main
            
            client = main.client
            script_dir = main.script_dir
            faces_dir = main.faces_dir
            QR_PATHS = main.QR_PATHS
            QUESTION_BANK = main.QUESTION_BANK
            QUESTION_BANK_CHEM = main.QUESTION_BANK_CHEM
            
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

CLASS_CONFIG = {
    "name": "mi_clase_de_prueba",
    "title": "Mi Clase de Prueba",
    "subject": "Robots Médicos",
    "diagnostic_qr": "RobotsMedicosExamen/pruebadiagnosticaRobotsMedicos.jpeg",
    "pdf_path": "RobotMedico.pdf",
    "demo_pdf_path": "",
    "final_exam_qr": "RobotsMedicosExamen/RobotsMedicosExamenI.jpeg",
    "use_diagnostic": True,
    "use_pdf": True,
    "use_demo": False,
    "use_final_exam": True
}

class Mi_Clase_de_Prueba:
    """Mi Clase de Prueba
    
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
        print("🚀 Inicializando sistemas de {self.config['name']}")
        
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
            
        return True
    
    def run_diagnostic_phase(self):
        """Run diagnostic evaluation phase"""
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
        print("👥 FASE 2: INICIO DE CLASE")
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
        self.current_users = identify_users(self.engine, self.current_slide_num, self.exit_flag)
        
        return True
    
    def run_pdf_phase(self):
        """Run PDF presentation phase"""
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
    
    def run_final_exam_phase(self):
        """Run final exam phase"""
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
        if self.camera_proc and self.camera_proc.is_alive():
            self.exit_flag.value = True
            self.camera_proc.join(timeout=5)
            if self.camera_proc.is_alive():
                self.camera_proc.terminate()
        
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
                print("⚠️ Error en fase de diagnóstico, continuando...")
            
            # Run class initialization
            if not self.run_class_initialization():
                print("⚠️ Error en inicialización de clase, continuando...")
            
            # Run PDF phase
            if not self.run_pdf_phase():
                print("⚠️ Error en fase de presentación, continuando...")
            
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
        class_instance = Mi_Clase_de_Prueba()
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
