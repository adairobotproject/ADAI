#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mi Clase de Prueba - All Variable Fixes Test
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

# Configuración de la clase
CLASS_CONFIG = {
    "name": "mi_clase_de_prueba",
    "title": "Mi Clase de Prueba",
    "subject": "Robots Médicos",
    "diagnostic_qr": "test_diagnostic.jpg",
    "pdf_path": "test_presentation.pdf",
    "final_exam_qr": "test_exam.jpg",
    "use_diagnostic": True,
    "use_pdf": True,
    "use_demo": False,
    "use_final_exam": True
}

class Mi_Clase_de_Prueba:
    """Clase de prueba para verificar todas las variables"""
    
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
        try:
            from modules.speech import initialize_tts
            self.engine = initialize_tts()
            print("✅ TTS inicializado")
            return True
        except ImportError:
            print("⚠️ No se pudo importar TTS")
            return False
    
    def run_diagnostic_phase(self):
        """Run diagnostic phase"""
        print("\n" + "="*50)
        print("📱 FASE 1: EVALUACIÓN DIAGNÓSTICA")
        print("="*50)
        
        diagnostic_qr = self.config['diagnostic_qr']
        print(f"🔍 Mostrando QR diagnóstico: {diagnostic_qr}")
        
        if os.path.exists(diagnostic_qr):
            print("✅ QR de diagnóstico encontrado")
            return True
        else:
            print(f"⚠️ No se encontró: {diagnostic_qr}")
            return True
    
    def run_pdf_phase(self):
        """Run PDF presentation phase"""
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
        try:
            from modules.slides import extract_text_from_pdf
            pdf_text = extract_text_from_pdf(pdf_path)
            if not pdf_text:
                print("❌ No se pudo leer el PDF")
                return False
        except ImportError:
            print("⚠️ No se pudo importar funciones de slides")
            return False
            
        # Start presentation
        if self.engine:
            from modules.speech import speak_with_animation
            speak_with_animation(self.engine, f"Ahora comenzaremos con la presentación sobre {self.config['subject']}.")
        
        print("✅ Fase de PDF completada")
        return True
    
    def run_final_exam_phase(self):
        """Run final exam phase"""
        if not self.config['use_final_exam'] or not self.config['final_exam_qr']:
            return True
            
        print("\n" + "="*60)
        print("🎓 FASE FINAL: EXAMEN")
        print("="*60)
        
        final_exam_qr = self.config['final_exam_qr']
        print(f"🔍 Mostrando QR examen: {final_exam_qr}")
        
        if os.path.exists(final_exam_qr):
            if self.engine:
                from modules.speech import speak_with_animation
                speak_with_animation(self.engine, "Excelente trabajo. Ahora es momento del examen final.")
                speak_with_animation(self.engine, f"Gracias por participar en la clase: {self.config['title']}. ¡Hasta la próxima!")
            return True
        else:
            print(f"⚠️ No se encontró: {final_exam_qr}")
            if self.engine:
                from modules.speech import speak_with_animation
                speak_with_animation(self.engine, "La clase ha terminado. ¡Gracias por participar!")
            return True
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Limpiando recursos...")
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
