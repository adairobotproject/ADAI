#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clase 1 Espanol 5to
Materia: Robótica Industrial
Generado por ADAI Class Builder el 2025-10-27 09:16:04

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
        explain_slides_with_sequences_and_questions,
        RandomQuestionManager, evaluate_student_answer, process_question,
        execute_esp32_sequence, summarize_text, ask_openai, QUESTION_BANK
    )
    print("✅ Funciones importadas desde demo_sequence_manager")
except ImportError as e:
    print(f"❌ Error importando funciones: {e}")
    print("⚠️ Asegúrate de que demo_sequence_manager.py esté en la carpeta main/")
    print(f"🔍 Buscando en: {main_dir}")
    sys.exit(1)

# ======================
#  BANCO DE PREGUNTAS PERSONALIZADAS
# ======================
# CUSTOM_QUESTION_BANK = ['La neutralización ocurre cuando un ácido y una base reaccionan. Verdadero o falso?', 'El bicarbonato de sodio es una sustancia básica. Verdadero o falso?', 'El vinagre contiene ácido acético. Verdadero o falso?', 'La col morada puede actuar como indicador de pH. Verdadero o falso?', 'La reacción entre ácido y bicarbonato libera oxígeno. Verdadero o falso?', 'El pH neutro corresponde aproximadamente al valor 7. Verdadero o falso?', 'La fenolftaleína se vuelve rosa en medio ácido. Verdadero o falso?']

CUSTOM_QUESTION_BANK = [
'Los fonemas son las unidades más pequeñas de sonido que se usan en la comunicación oral. Verdadero o falso?',
'En español existen veinticuatro fonemas. Verdadero o falso?',
'Cambiar un fonema en una palabra puede alterar su significado. Verdadero o falso?',
'Los fonemas se representan con letras. Verdadero o falso?',
'Las vocales abiertas son a, e, o. Verdadero o falso?',
'Las consonantes se diferencian de las vocales por la presencia de obstáculos en la salida del aire. Verdadero o falso?',
'Los fonemas son los signos gráficos que usamos para escribir palabras. Verdadero o falso?',
'Los grafemas son las unidades más pequeñas del lenguaje escrito. Verdadero o falso?',
'Las palabras “pasta” y “basta” se diferencian por un grafema. Verdadero o falso?',
'Los trazos curvos y rectos son rasgos distintivos de los grafemas. Verdadero o falso?',
'Un grafema puede tener ascendentes o descendentes. Verdadero o falso?',
'Los fonemas y grafemas son exactamente lo mismo. Verdadero o falso?',
'Las palabras “sien” y “cien” suenan igual pero se escriben diferente. Verdadero o falso?'
]

def main():
    """Función principal que ejecuta la clase completa"""
    try:
        print("🚀 Iniciando clase: Clase 1 Espanol 5to")
        print("📚 Materia: Robótica Industrial")
        
        # Definir rutas de archivos
        diagnostic_qr = "C:/Users/josue/Desktop/CvLD1_ZUEAAmRG6.jpg"
        class_pdf = "C:/Users/josue/Downloads/Clase 1 español 5to grado.pdf"
        final_exam_qr = "C:/Users/josue/Desktop/CvLD1_ZUEAAmRG6.jpg"
        
        # Inicializar TTS
        engine = initialize_tts()
        if not engine:
            print("❌ No se pudo inicializar el motor TTS")
            return
        
        # Crear ventana para la cara animada
        # cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
        # cv2.resizeWindow("ADAI Robot Face", 600, 400)
        
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
            # speak_with_animation(engine, "Vamos a comenzar con una evaluación diagnóstica.")
            show_diagnostic_qr(diagnostic_qr, display_time=40)
        else:
            print(f"⚠️ No se encontró QR diagnóstico: C:/Users/josue/Desktop/CvLD1_ZUEAAmRG6.jpg")
            speak_with_animation(engine, "Continuaremos sin evaluación diagnóstica.")
        
        # FASE 2: Inicio de Clase
        print("\n" + "="*50)
        print("🤖 FASE 2: INICIO DE CLASE")
        print("="*50)
        
        speak_with_animation(engine, f"Hola, soy ADAI. Bienvenidos a la clase: Clase 1 Espanol 5to")
        speak_with_animation(engine, f"Vamos a aprender sobre Español Quinto Grado")
        
        # FASE 3: Contenido Principal
        print("\n" + "="*50)
        print("📚 FASE 3: PRESENTACIÓN DE CONTENIDO")
        print("="*50)
        
        if class_pdf and os.path.exists(class_pdf):
            speak_with_animation(engine, f"Ahora comenzaremos con la presentación sobre Español Quinto Grado")
            
            # Extraer texto del PDF
            pdf_text = extract_text_from_pdf(class_pdf)
            if pdf_text:
                # Definir mapeo de secuencias ESP32 por número de diapositiva
                sequence_mapping = {
                    1: "HandClassMove",    # Después de la diapositiva 1
                    2: "OpenHand",
                    3: "HandClassMove",    # Después de la diapositiva 3
                    4: "OpenHand",
                    5: "HandClassMove",
                    6: "OpenHand",
                    7: "HandClassMove",
                    8: "OpenHand",
                    9: "HandClassMove",
                }
                
                print("🎬 Usando explicación con secuencias ESP32 EN PARALELO y preguntas aleatorias")
                
                # Usar preguntas personalizadas si están disponibles
                if CUSTOM_QUESTION_BANK:
                    print("🎯 Usando preguntas personalizadas con secuencias")
                    # Temporalmente reemplazar QUESTION_BANK con preguntas personalizadas
                    original_question_bank = QUESTION_BANK.copy()
                    QUESTION_BANK.clear()
                    QUESTION_BANK.extend(CUSTOM_QUESTION_BANK)
                    
                    # Explicar diapositivas con preguntas personalizadas y secuencias EN PARALELO
                    explain_slides_with_sequences_and_questions(
                        engine, class_pdf, pdf_text, current_users,
                        hand_raised_counter, current_slide_num, exit_flag, 
                        known_faces, current_hand_raiser, sequence_mapping
                    )
                    
                    # Restaurar QUESTION_BANK original
                    QUESTION_BANK.clear()
                    QUESTION_BANK.extend(original_question_bank)
                else:
                    print("🎯 Usando preguntas por defecto con secuencias")
                    # Explicar diapositivas con preguntas aleatorias por defecto y secuencias EN PARALELO
                    explain_slides_with_sequences_and_questions(
                        engine, class_pdf, pdf_text, current_users,
                        hand_raised_counter, current_slide_num, exit_flag, 
                        known_faces, current_hand_raiser, sequence_mapping
                    )
            else:
                print("❌ No se pudo leer el PDF")
        else:
            print(f"⚠️ No se encontró PDF: C:/Users/josue/Downloads/Clase 1 español 5to grado.pdf")
            speak_with_animation(engine, "Continuaremos sin presentación de PDF.")
        
        
        # FASE 4: Examen Final
        print("\n" + "="*60)
        print("🎓 FASE FINAL: EXAMEN")
        print("="*60)
        
        if final_exam_qr and os.path.exists(final_exam_qr):
            speak_with_animation(engine, "Excelente trabajo. Ahora es momento de una encuesta escrita.")
            speak_with_animation(engine, "Por favor, completen la encuesta proporcionada por su profesor.")
            
            speak_with_animation(engine, "Perfecto. ¡Mucha suerte en la encuesta!")
        else:
            print(f"⚠️ No se encontró encuesta: C:/Users/josue/Downloads/Clase 1 español 6to grado.pdf")
            speak_with_animation(engine, "La clase ha terminado.")
        
        # Finalización
        speak_with_animation(engine, f"Gracias por participar en la clase: Clase 1 Espanol 5to. ¡Hasta la próxima!")
        
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
