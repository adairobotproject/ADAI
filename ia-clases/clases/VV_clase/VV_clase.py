#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VV
Materia: Robots Médicos
Generado por ADAI Class Builder el 2025-10-03 14:52:36

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
# Buscar demo_sequence_manager en la carpeta main del directorio clases
classes_dir = os.path.dirname(current_dir)
main_dir = os.path.join(classes_dir, "main")

# Verificar que existe el archivo demo_sequence_manager.py
demo_manager_path = os.path.join(main_dir, "demo_sequence_manager.py")
if not os.path.exists(demo_manager_path):
    print(f"❌ No se encontró demo_sequence_manager.py en: {demo_manager_path}")
    print("⚠️ Asegúrate de que el archivo existe en la carpeta main/")
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
    print(f"❌ Error importando funciones: {e}")
    print("⚠️ Asegúrate de que demo_sequence_manager.py esté en la carpeta main/")
    print(f"🔍 Buscando en: {main_dir}")
    sys.exit(1)

def main():
    """Función principal que ejecuta la clase completa"""
    try:
        print("🚀 Iniciando clase: VV")
        print("📚 Materia: Robots Médicos")
        
        # Inicializar TTS
        engine = initialize_tts()
        if not engine:
            print("❌ No se pudo inicializar el motor TTS")
            return
        
        # Crear ventana para la cara animada
        cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("ADAI Robot Face", 600, 400)
        
        # Verificar cámara
        if not verify_camera_for_iriun():
            print("⚠️ Problemas detectados con la cámara.")
            return
        
        # Variables compartidas para multiprocessing
        hand_raised_counter = multiprocessing.Value('i', 0)
        current_slide_num = multiprocessing.Value('i', 1)
        exit_flag = multiprocessing.Value('i', 0)
        current_hand_raiser = multiprocessing.Value('i', -1)
        
        # Identificar usuarios
        print("🔍 Identificando usuarios de izquierda a derecha...")
        current_users, _ = identify_users(engine, current_slide_num, exit_flag)
        
        # Cargar caras conocidas
        known_faces = load_known_faces()
        
        # Iniciar proceso de cámara
        camera_proc = Process(
            target=camera_process,
            args=(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, current_users)
        )
        camera_proc.daemon = True
        camera_proc.start()
        
        print("⏳ Esperando a que la cámara se inicialice...")
        time.sleep(3)
        
        # FASE 1: Evaluación Diagnóstica
        print("\n" + "="*50)
        print("📱 FASE 1: EVALUACIÓN DIAGNÓSTICA")
        print("="*50)
        
        if diagnostic_qr and os.path.exists(diagnostic_qr):
            speak_with_animation(engine, "Vamos a comenzar con una evaluación diagnóstica.")
            show_diagnostic_qr(diagnostic_qr, display_time=40)
        else:
            print(f"⚠️ No se encontró QR diagnóstico: {diagnostic_qr}")
            speak_with_animation(engine, "Continuaremos sin evaluación diagnóstica.")
        
        # FASE 2: Inicio de Clase
        print("\n" + "="*50)
        print("🤖 FASE 2: INICIO DE CLASE")
        print("="*50)
        
        speak_with_animation(engine, f"Hola, soy ADAI. Bienvenidos a la clase: VV")
        speak_with_animation(engine, f"Vamos a aprender sobre Robots Médicos")
        
        # FASE 3: Contenido Principal
        print("\n" + "="*50)
        print("📚 FASE 3: PRESENTACIÓN DE CONTENIDO")
        print("="*50)
        
        if class_pdf and os.path.exists(class_pdf):
            speak_with_animation(engine, f"Ahora comenzaremos con la presentación sobre Robots Médicos.")
            
            # Extraer texto del PDF
            pdf_text = extract_text_from_pdf(class_pdf)
            if pdf_text:
                # Explicar diapositivas con preguntas aleatorias
                explain_slides_with_random_questions(
                    engine, class_pdf, pdf_text, current_users,
                    hand_raised_counter, current_slide_num, exit_flag, 
                    known_faces, current_hand_raiser
                )
            else:
                print("❌ No se pudo leer el PDF")
        else:
            print(f"⚠️ No se encontró PDF: {class_pdf}")
            speak_with_animation(engine, "Continuaremos sin presentación de PDF.")
        
        # FASE 4: Examen Final
        print("\n" + "="*60)
        print("🎓 FASE FINAL: EXAMEN")
        print("="*60)
        
        if final_exam_qr and os.path.exists(final_exam_qr):
            speak_with_animation(engine, "Excelente trabajo. Ahora es momento del examen final.")
            speak_with_animation(engine, "Por favor, escanea el código QR que aparecerá en pantalla.")
            
            show_final_exam_qr(final_exam_qr, display_time=40)
            
            speak_with_animation(engine, "Perfecto. ¡Mucha suerte en el examen!")
        else:
            print(f"⚠️ No se encontró QR examen: {final_exam_qr}")
            speak_with_animation(engine, "La clase ha terminado.")
        
        # Finalización
        speak_with_animation(engine, f"Gracias por participar en la clase: VV. ¡Hasta la próxima!")
        
        # Limpiar recursos
        print("🛑 Finalizando clase")
        exit_flag.value = 1
        
        if camera_proc.is_alive():
            print("⏳ Esperando proceso de cámara...")
            camera_proc.join(timeout=3)
            
            if camera_proc.is_alive():
                camera_proc.terminate()
                camera_proc.join(timeout=1)
        
        cv2.destroyAllWindows()
        print("✅ Clase finalizada")
        
    except Exception as e:
        print(f"❌ Error ejecutando clase: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
