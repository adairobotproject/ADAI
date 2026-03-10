#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clase Defensa de Tesis
Materia: Presentación y Defensa de Tesis
Generado por ADAI Class Builder

Clase automática usando demo_sequence_manager
El robot explicará la defensa de tesis con movimientos pero sin preguntas
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
        explain_slides_with_sequences,
        execute_esp32_sequence, summarize_text, ask_openai
    )
    print("✅ Funciones importadas desde demo_sequence_manager")
except ImportError as e:
    print(f"❌ Error importando funciones: {e}")
    print("⚠️ Asegúrate de que demo_sequence_manager.py esté en la carpeta main/")
    print(f"🔍 Buscando en: {main_dir}")
    sys.exit(1)


def main():
    """Función principal que ejecuta la clase de defensa de tesis"""
    try:
        print("🚀 Iniciando clase: Defensa de Tesis")
        print("📚 Materia: Presentación y Defensa de Tesis")
        
        # Definir rutas de archivos
        # NOTA: Ajusta estas rutas según tu sistema
        class_pdf = "C:/Users/josue/Downloads/defensa_tesis.pdf"
        
        # Inicializar TTS
        engine = initialize_tts()
        if not engine:
            print("❌ No se pudo inicializar el motor TTS")
            return
        
        # Crear ventana para la cara animada
        cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("ADAI Robot Face", 600, 400)
        
        # Sin verificación de cámara para defensa de tesis (no se requiere reconocimiento facial)
        print("✅ Iniciando sin reconocimiento facial")
        
        # Variables compartidas para multiprocessing
        hand_raised_counter = multiprocessing.Value('i', 0)
        current_slide_num = multiprocessing.Value('i', 1)
        exit_flag = multiprocessing.Value('i', 0)
        current_hand_raiser = multiprocessing.Value('i', -1)
        
        # Sin identificación de usuarios para defensa de tesis
        current_users = []
        known_faces = []
        
        # Iniciar proceso de cámara (sin identificación de rostros)
        camera_proc = Process(
            target=camera_process,
            args=(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, current_users)
        )
        camera_proc.daemon = True
        camera_proc.start()
        
        print("⏳ Esperando a que la cámara se inicialice...")
        time.sleep(3)
        
        # FASE 1: Inicio de Presentación
        print("\n" + "="*50)
        print("🎓 FASE 1: INICIO DE DEFENSA DE TESIS")
        print("="*50)
        
        speak_with_animation(engine, "Hola, soy ADAI. Bienvenidos a esta defensa de tesis.")
        speak_with_animation(engine, "A continuación presentaré el trabajo de investigación que se ha desarrollado.")
        
        # FASE 2: Presentación de la Tesis
        print("\n" + "="*50)
        print("📚 FASE 2: PRESENTACIÓN DEL CONTENIDO")
        print("="*50)
        
        if class_pdf and os.path.exists(class_pdf):
            speak_with_animation(engine, "Comenzaremos con la presentación de la tesis.")
            
            # Extraer texto del PDF
            pdf_text = extract_text_from_pdf(class_pdf)
            if pdf_text:
                # Definir mapeo de secuencias ESP32 por número de diapositiva
                # Personaliza estas secuencias según las diapositivas de tu tesis
                sequence_mapping = {
                    1: "ClaseMove",      # Introducción
                    2: "ClaseCuello",    # Planteamiento del problema
                    3: "ClaseMove",      # Objetivos
                    4: "ClaseCuello",    # Marco teórico
                    5: "ClaseMove",      # Metodología
                    6: "ClaseCuello",    # Resultados
                    7: "ClaseMove",      # Análisis
                    8: "ClaseCuello",    # Conclusiones
                    9: "ClaseMove",      # Recomendaciones
                    10: "ClaseCuello",   # Referencias
                }
                
                print("🎬 Explicando tesis con secuencias ESP32 (sin preguntas)")
                
                # Explicar diapositivas CON secuencias pero SIN preguntas
                explain_slides_with_sequences(
                    engine, class_pdf, pdf_text, current_users,
                    hand_raised_counter, current_slide_num, exit_flag, 
                    known_faces, current_hand_raiser, sequence_mapping
                )
            else:
                print("❌ No se pudo leer el PDF")
                speak_with_animation(engine, "Lo siento, no pude cargar el archivo de la tesis.")
        else:
            print(f"⚠️ No se encontró PDF: {class_pdf}")
            speak_with_animation(engine, "No se encontró el archivo de la tesis. Por favor, actualice la ruta del PDF en el código.")
            speak_with_animation(engine, "La ruta actual configurada es: " + class_pdf)
        
        # FASE 3: Cierre
        print("\n" + "="*60)
        print("🎓 FASE FINAL: CIERRE DE DEFENSA")
        print("="*60)
        
        speak_with_animation(engine, "Hemos concluido la presentación de la tesis.")
        speak_with_animation(engine, "Muchas gracias por su atención. Quedo a disposición para responder sus preguntas.")
        speak_with_animation(engine, "¡Gracias por acompañarnos en esta defensa de tesis!")
        
        # Limpiar recursos
        print("🛑 Finalizando presentación")
        exit_flag.value = 1
        
        if camera_proc.is_alive():
            print("⏳ Esperando proceso de cámara...")
            camera_proc.join(timeout=3)
            
            if camera_proc.is_alive():
                camera_proc.terminate()
                camera_proc.join(timeout=1)
        
        cv2.destroyAllWindows()
        print("✅ Defensa de tesis finalizada")
        
    except Exception as e:
        print(f"❌ Error ejecutando defensa de tesis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

