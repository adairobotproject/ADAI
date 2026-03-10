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
# Los módulos están en ia-clases/modules
# Desde: ia-clases/clases/nombre_clase/
# Hacia: ia-clases/modules/
parent_dir = os.path.dirname(current_dir)  # ia-clases/clases/
parent_parent_dir = os.path.dirname(parent_dir)  # ia-clases/
modules_dir = os.path.join(parent_parent_dir, "modules")  # ia-clases/modules/
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

class Mi_Clase_de_Prueba:
    """Clase generada por Class Builder"""
    
    def __init__(self):
        self.config = {
            'title': 'Mi Clase de Prueba',
            'subject': 'Robots Médicos',
            'diagnostic_qr': 'RobotsMedicosExamen/pruebadiagnosticaRobotsMedicos.jpeg',
            'pdf_path': 'RobotMedico.pdf',
            'final_exam_qr': 'RobotsMedicosExamen/RobotsMedicosExamenI.jpeg'
        }
        self.engine = None
        self.current_users = []
        self.known_faces = []
        
    def run_complete_class(self):
        """Ejecutar la clase completa"""
        try:
            print("🎓 Iniciando clase: Mi Clase de Prueba")
            
            # Inicializar TTS
            self.engine = initialize_tts()
            
            # Cargar caras conocidas
            self.known_faces = load_known_faces()
            
            # Fase 1: Diagnóstico
            if self.run_diagnostic_phase():
                print("✅ Fase de diagnóstico completada")
            else:
                print("⚠️ Fase de diagnóstico falló, continuando...")
            
            # Fase 2: PDF
            if self.run_pdf_phase():
                print("✅ Fase de PDF completada")
            else:
                print("⚠️ Fase de PDF falló, continuando...")
            
            # Fase 3: Examen final
            if self.run_final_exam_phase():
                print("✅ Fase de examen final completada")
            else:
                print("⚠️ Fase de examen final falló, continuando...")
            
            print("🎉 Clase completada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error en clase: {e}")
            return False
    
    def run_diagnostic_phase(self):
        """Ejecutar fase de diagnóstico"""
        try:
            diagnostic_qr = self.config['diagnostic_qr']
            if not os.path.exists(diagnostic_qr):
                print(f"❌ No se encontró el QR de diagnóstico: {diagnostic_qr}")
                return False
            
            print("📋 Mostrando QR de diagnóstico...")
            show_diagnostic_qr(diagnostic_qr, display_time=15)
            return True
            
        except Exception as e:
            print(f"❌ Error en fase de diagnóstico: {e}")
            return False
    
    def run_pdf_phase(self):
        """Ejecutar fase de PDF"""
        try:
            pdf_path = self.config['pdf_path']
            if not os.path.exists(pdf_path):
                print(f"❌ No se encontró el PDF: {pdf_path}")
                return False
            
            print("📖 Procesando PDF...")
            pdf_text = extract_text_from_pdf(pdf_path)
            if not pdf_text:
                print("❌ No se pudo leer el PDF")
                return False
            
            # Variables para el proceso de cámara
            hand_raised_counter = Value('i', 0)
            current_slide_num = Value('i', 1)
            exit_flag = Value('b', False)
            current_hand_raiser = Value('i', -1)
            
            # Iniciar proceso de cámara
            camera_proc = Process(target=camera_process, 
                                args=(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, self.current_users))
            camera_proc.start()
            
            try:
                # Identificar usuarios
                self.current_users = identify_users(self.engine, current_slide_num, exit_flag)
                
                # Explicar slides
                explain_slides_with_random_questions(
                    self.engine, pdf_path, pdf_text, self.current_users,
                    hand_raised_counter, current_slide_num, exit_flag,
                    self.known_faces, current_hand_raiser
                )
                
            finally:
                # Terminar proceso de cámara
                exit_flag.value = True
                camera_proc.join(timeout=5)
                if camera_proc.is_alive():
                    camera_proc.terminate()
            
            return True
            
        except Exception as e:
            print(f"❌ Error en fase de PDF: {e}")
            return False
    
    def run_final_exam_phase(self):
        """Ejecutar fase de examen final"""
        try:
            final_exam_qr = self.config['final_exam_qr']
            if not os.path.exists(final_exam_qr):
                print(f"❌ No se encontró el QR de examen: {final_exam_qr}")
                return False
            
            print("📝 Mostrando QR de examen final...")
            show_final_exam_qr(final_exam_qr, display_time=20)
            return True
            
        except Exception as e:
            print(f"❌ Error en fase de examen final: {e}")
            return False

def main():
    """Función principal"""
    try:
        multiprocessing.freeze_support()
        
        # Crear instancia de la clase
        clase = Mi_Clase_de_Prueba()
        
        # Ejecutar clase completa
        success = clase.run_complete_class()
        
        if success:
            print("🎉 Clase ejecutada exitosamente")
        else:
            print("❌ La clase falló")
        
        return success
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return False

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
