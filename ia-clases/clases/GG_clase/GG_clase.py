#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GG
Materia: Robots Médicos
Generado por ADAI Class Builder el 2025-10-02 11:56:13

Clase automática usando funciones de demo_sequence_manager
"""

import cv2
import os
import time
import multiprocessing
from multiprocessing import Process, Value
import sys

# Configurar path para importar desde demo_sequence_manager
current_dir = os.path.dirname(os.path.abspath(__file__))
# Buscar demo_sequence_manager en la carpeta main del directorio clases
classes_dir = os.path.dirname(current_dir)
main_dir = os.path.join(classes_dir, "main")

# Verificar que existe el archivo demo_sequence_manager.py
demo_manager_path = os.path.join(main_dir, "demo_sequence_manager.py")
if not os.path.exists(demo_manager_path):
    print(f"ERROR: No se encontró demo_sequence_manager.py en: {demo_manager_path}")
    print("AVISO: Asegúrate de que el archivo existe en la carpeta main/")
    sys.exit(1)

# Agregar al path
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
    print(f"ERROR: Error importando funciones: {e}")
    print("AVISO: Asegúrate de que demo_sequence_manager.py esté en la carpeta main/")
    print(f"Buscando en: {main_dir}")
    sys.exit(1)

# ======================
#  CONFIGURACIÓN DE LA CLASE
# ======================
CLASS_CONFIG = {
    "name": "GG",
    "title": "GG",
    "subject": "Robots Médicos",
    "diagnostic_qr": "C:/Users/josue/Downloads/ChatGPT Image 18 sept 2025, 13_14_36.png",
    "pdf_path": "RobotMedico.pdf",
    "demo_pdf_path": "",
    "final_exam_qr": "C:/Users/josue/Downloads/ChatGPT Image 18 sept 2025, 13_14_36.png",
    "use_diagnostic": True,
    "use_pdf": True,
    "use_demo": false,
    "use_final_exam": True
}



class GG:
    """
    GG
    
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
            
        # Create faces directory
        faces_dir = os.path.join(current_dir, "faces")
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
        class_instance = GG()
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
