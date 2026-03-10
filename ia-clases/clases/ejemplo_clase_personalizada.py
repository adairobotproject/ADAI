"""
Ejemplo de Clase Personalizada usando Módulos ADAI
================================================

Este archivo demuestra cómo crear una clase personalizada
utilizando los módulos modulares de ADAI.

Autor: ADAI Team
Versión: 1.0.0
"""

import os
import cv2
import multiprocessing
from multiprocessing import Process
import time

# Importar módulos necesarios
from modules.config import get_qr_paths
from modules.speech import initialize_tts, speak_with_animation, listen
from modules.camera import verify_camera_for_iriun, camera_process
from modules.slides import extract_text_from_pdf, explain_slides_with_random_questions
from modules.qr import show_diagnostic_qr, show_final_exam_qr
from modules.utils import identify_users

class ClasePersonalizada:
    """
    Clase personalizada que demuestra el uso de los módulos ADAI
    """
    
    def __init__(self, nombre_clase="Clase Personalizada"):
        """
        Inicializa la clase personalizada
        
        Args:
            nombre_clase (str): Nombre de la clase
        """
        self.nombre_clase = nombre_clase
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.engine = None
        self.current_users = []
        
        # Variables compartidas para multiprocessing
        self.hand_raised_counter = multiprocessing.Value('i', 0)
        self.current_slide_num = multiprocessing.Value('i', 1)
        self.exit_flag = multiprocessing.Value('i', 0)
        self.current_hand_raiser = multiprocessing.Value('i', -1)
        
        print(f"🎓 Inicializando {self.nombre_clase}")
    
    def inicializar_sistema(self):
        """
        Inicializa el sistema ADAI
        """
        print("🔧 Inicializando sistema...")
        
        # Inicializar TTS
        self.engine = initialize_tts()
        if not self.engine:
            print("❌ No se pudo inicializar el motor TTS")
            return False
        
        # Verificar cámara
        if not verify_camera_for_iriun():
            print("⚠️ Problemas detectados con la cámara.")
            return False
        
        # Crear ventana para la cara animada
        cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("ADAI Robot Face", 600, 400)
        
        print("✅ Sistema inicializado correctamente")
        return True
    
    def mostrar_evaluacion_diagnostica(self, tiempo_display=30):
        """
        Muestra la evaluación diagnóstica
        
        Args:
            tiempo_display (int): Tiempo en segundos para mostrar el QR
        """
        print("\n" + "="*50)
        print("📱 FASE: EVALUACIÓN DIAGNÓSTICA")
        print("="*50)
        
        # Obtener rutas de QR
        qr_paths = get_qr_paths(self.script_dir)
        diagnostic_qr = qr_paths['diagnostico_quimica']
        
        if os.path.exists(diagnostic_qr):
            speak_with_animation(self.engine, "Vamos a comenzar con una evaluación diagnóstica.")
            show_diagnostic_qr(diagnostic_qr, display_time=tiempo_display)
        else:
            print(f"⚠️ No se encontró QR diagnóstico: {diagnostic_qr}")
            speak_with_animation(self.engine, "Continuaremos sin evaluación diagnóstica.")
    
    def identificar_estudiantes(self):
        """
        Identifica a los estudiantes presentes
        """
        print("\n" + "="*50)
        print("👥 FASE: IDENTIFICACIÓN DE ESTUDIANTES")
        print("="*50)
        
        speak_with_animation(self.engine, f"Bienvenidos a {self.nombre_clase}.")
        speak_with_animation(self.engine, "Voy a identificar a todos los estudiantes presentes.")
        
        self.current_users, _ = identify_users(
            self.engine, 
            self.current_slide_num, 
            self.exit_flag, 
            self.script_dir, 
            listen
        )
        
        print(f"✅ Estudiantes identificados: {self.current_users}")
    
    def iniciar_camara(self):
        """
        Inicia el proceso de cámara
        """
        print("🎥 Iniciando proceso de cámara...")
        
        self.camera_proc = Process(
            target=camera_process,
            args=(self.hand_raised_counter, self.current_slide_num, self.exit_flag, 
                  self.current_hand_raiser, self.current_users)
        )
        self.camera_proc.daemon = True
        self.camera_proc.start()
        
        print("⏳ Esperando a que la cámara se inicialice...")
        time.sleep(3)
    
    def impartir_clase_con_preguntas(self, pdf_path):
        """
        Imparte la clase con sistema de preguntas aleatorias
        
        Args:
            pdf_path (str): Ruta al archivo PDF de la clase
        """
        print("\n" + "="*50)
        print("📚 FASE: IMPARTIR CLASE CON PREGUNTAS")
        print("="*50)
        
        # Cargar PDF
        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text:
            print("❌ No se pudo leer el PDF")
            return False
        
        speak_with_animation(self.engine, "Ahora comenzaremos con la presentación.")
        
        # Explicar diapositivas con preguntas aleatorias
        success = explain_slides_with_random_questions(
            self.engine, 
            pdf_path, 
            pdf_text, 
            self.current_users,
            self.hand_raised_counter, 
            self.current_slide_num, 
            self.exit_flag, 
            {},  # known_faces vacío por simplicidad
            self.current_hand_raiser, 
            listen
        )
        
        return success
    
    def mostrar_examen_final(self, tiempo_display=30):
        """
        Muestra el examen final
        
        Args:
            tiempo_display (int): Tiempo en segundos para mostrar el QR
        """
        print("\n" + "="*50)
        print("🎓 FASE: EXAMEN FINAL")
        print("="*50)
        
        # Obtener rutas de QR
        qr_paths = get_qr_paths(self.script_dir)
        final_exam_qr = qr_paths['examen_quimica']
        
        if os.path.exists(final_exam_qr):
            speak_with_animation(self.engine, "Excelente trabajo. Ahora es momento del examen final.")
            speak_with_animation(self.engine, "Por favor, escanea el código QR que aparecerá en pantalla.")
            
            show_final_exam_qr(final_exam_qr, display_time=tiempo_display)
            
            speak_with_animation(self.engine, "Perfecto. ¡Mucha suerte en el examen!")
        else:
            print(f"⚠️ No se encontró QR examen: {final_exam_qr}")
            speak_with_animation(self.engine, "La clase ha terminado.")
    
    def finalizar_clase(self):
        """
        Finaliza la clase y limpia recursos
        """
        print("\n" + "="*50)
        print("🏁 FINALIZANDO CLASE")
        print("="*50)
        
        speak_with_animation(self.engine, f"Gracias por participar en {self.nombre_clase}. ¡Hasta la próxima!")
        
        # Señalar salida
        self.exit_flag.value = 1
        
        # Esperar proceso de cámara
        if hasattr(self, 'camera_proc'):
            print("⏳ Esperando proceso de cámara...")
            self.camera_proc.join(timeout=3)
            
            if self.camera_proc.is_alive():
                self.camera_proc.terminate()
                self.camera_proc.join(timeout=1)
        
        # Limpiar ventanas
        cv2.destroyAllWindows()
        print("✅ Clase finalizada correctamente")
    
    def ejecutar_clase_completa(self, pdf_path):
        """
        Ejecuta una clase completa con todas las fases
        
        Args:
            pdf_path (str): Ruta al archivo PDF de la clase
        """
        try:
            print(f"🚀 Iniciando {self.nombre_clase}")
            
            # 1. Inicializar sistema
            if not self.inicializar_sistema():
                return False
            
            # 2. Mostrar evaluación diagnóstica
            self.mostrar_evaluacion_diagnostica()
            
            # 3. Identificar estudiantes
            self.identificar_estudiantes()
            
            # 4. Iniciar cámara
            self.iniciar_camara()
            
            # 5. Impartir clase
            if not self.impartir_clase_con_preguntas(pdf_path):
                print("⚠️ Error en la clase, continuando...")
            
            # 6. Mostrar examen final
            self.mostrar_examen_final()
            
            # 7. Finalizar
            self.finalizar_clase()
            
            return True
            
        except Exception as e:
            print(f"❌ Error en la clase: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """
    Función principal que demuestra el uso de la clase personalizada
    """
    # Crear instancia de clase personalizada
    mi_clase = ClasePersonalizada("Mi Clase de Robótica Médica")
    
    # Definir ruta del PDF
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, "main", "pdfs", "Demo_Paso_a_Paso.pdf")
    
    # Verificar que existe el PDF
    if not os.path.exists(pdf_path):
        print(f"❌ No se encontró el PDF: {pdf_path}")
        print("💡 Asegúrate de que el archivo PDF existe en la ruta especificada")
        return
    
    # Ejecutar clase completa
    success = mi_clase.ejecutar_clase_completa(pdf_path)
    
    if success:
        print("🎉 ¡Clase completada exitosamente!")
    else:
        print("❌ La clase tuvo problemas, pero se completó")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
