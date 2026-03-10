"""
Módulo de manejo de diapositivas para ADAI
=========================================

Contiene todas las funciones relacionadas con:
- Procesamiento de PDFs
- Explicación de diapositivas
- Integración con secuencias ESP32
- Manejo de preguntas durante presentaciones
"""

import cv2
import fitz  # PyMuPDF
import numpy as np
import time
import os
import openai
import pytesseract
from .config import OPENAI_API_KEY, TESSERACT_PATH, WINDOW_CONFIG
from .esp32 import execute_esp32_sequence

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Configurar cliente OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def extract_text_from_pdf(pdf_path):
    """
    Extrae texto de un archivo PDF
    
    Args:
        pdf_path (str): Ruta al archivo PDF
        
    Returns:
        str: Texto extraído del PDF o None si hay error
    """
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"❌ Error al leer el PDF: {e}")
        return None

def show_pdf_page_in_opencv(page):
    """
    Convierte la página PyMuPDF en una imagen BGR de OpenCV,
    manejando RGBA, RGB o escala de grises.
    
    Args:
        page: Página de PyMuPDF
        
    Returns:
        numpy.ndarray: Imagen BGR de OpenCV
    """
    pix = page.get_pixmap()
    data = np.frombuffer(pix.samples, dtype=np.uint8)
    mode = pix.n  # canales
    if mode == 4:
        img_rgba = data.reshape((pix.h, pix.w, 4))
        img_bgr = cv2.cvtColor(img_rgba, cv2.COLOR_RGBA2BGR)
    elif mode == 3:
        img_rgb = data.reshape((pix.h, pix.w, 3))
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    elif mode == 1:
        img_gray = data.reshape((pix.h, pix.w))
        img_bgr = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
    else:
        raise ValueError(f"Número de canales no soportado: {mode}")
    return img_bgr

def summarize_text(text):
    """
    Resume texto usando OpenAI
    
    Args:
        text (str): Texto a resumir
        
    Returns:
        str: Resumen del texto
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente educativo que resume el contenido de los documentos."},
                {"role": "user", "content": f"Por favor, resume el siguiente texto:\n\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error en OpenAI: {e}")
        return "Lo siento, hubo un error al procesar el resumen."

def interpret_image(image_path):
    """
    Interpreta una imagen usando OCR y OpenAI
    
    Args:
        image_path (str): Ruta a la imagen
        
    Returns:
        str: Interpretación de la imagen
    """
    try:
        text = pytesseract.image_to_string(image_path, lang='spa')
        if text.strip():
            return summarize_text(text)
        else:
            # Si tesseract no encuentra texto, usamos una descripción genérica
            return "Esta diapositiva contiene principalmente elementos visuales. Se trata de una imagen ilustrativa relacionada con el tema de la clase."
    except Exception as e:
        print(f"❌ Error al interpretar la imagen: {e}")
        return "Lo siento, hubo un error al interpretar la imagen."

def ask_openai(question, context, student_name=None):
    """
    Versión mejorada de ask_openai para respuestas más naturales
    
    Args:
        question (str): Pregunta a realizar
        context (str): Contexto del material
        student_name (str): Nombre del estudiante (opcional)
        
    Returns:
        str: Respuesta de OpenAI
    """
    try:
        # Sistema mejorado para respuestas naturales
        system_prompt = """Eres ADAI, un asistente educativo androide amigable y conversacional que SOLO 
        responde preguntas relacionadas con el contenido del PDF proporcionado. Si la pregunta no está relacionada con el PDF, 
        indica claramente que solo puedes responder preguntas sobre el tema del PDF." 

REGLAS IMPORTANTES:
- NO uses asteriscos, guiones, viñetas, ni formato especial
- NO uses emojis ni símbolos especiales  
- Habla de manera natural y conversacional como un profesor amigable
- Máximo 3 oraciones por respuesta
- NO uses palabras como "retroalimentación", "corrección", "evaluación"
- Si corriges algo, hazlo de manera educativa pero natural"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexto: {context}\n\nPregunta: {question}"}
            ]
        )
        
        # Limpiar respuesta de cualquier formato
        answer = response.choices[0].message.content
        answer = answer.replace("*", "").replace("**", "").replace("***", "")
        answer = answer.replace("- ", "").replace("• ", "")
        answer = answer.strip()
        
        return answer
    except Exception as e:
        print(f"❌ Error en OpenAI natural: {e}")
        return "Lo siento, hubo un problema. Continuemos con la clase."

def process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser):
    """
    Procesamiento de preguntas basado en la identificación de estudiantes
    
    Args:
        engine: Motor de TTS
        current_users: Lista de usuarios actuales
        known_faces: Diccionario de caras conocidas
        pdf_text: Texto del PDF
        hand_raised_counter: Contador de manos levantadas
        current_hand_raiser: ID del usuario que levantó la mano
        
    Returns:
        bool: True si se procesó exitosamente
    """
    print("🤔 Procesando preguntas de usuarios...")
    
    try:
        # Importar funciones necesarias
        from .speech import speak_with_animation, listen
        
        # Determinar quién hizo la pregunta
        student_id = current_hand_raiser.value
        
        # Si no tenemos un ID concreto, preguntamos quién hizo la pregunta
        if student_id < 0 or student_id >= len(current_users):
            if len(current_users) > 1:
                speak_with_animation(engine, "Alguien ha levantado la mano. ¿Quién desea preguntar?")
                name = listen()
                if name and name not in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""] and name.lower() in [user.lower() for user in current_users]:
                    current_user = next(user for user in current_users if user.lower() == name.lower())
                else:
                    # Si no entendemos el nombre o no coincide, usamos el primer usuario
                    current_user = list(current_users)[0]
            else:
                current_user = list(current_users)[0]
        else:
            # Convertir el ID numérico al nombre del estudiante 
            if student_id < len(current_users):
                current_user = list(current_users)[student_id]
            else:
                # Si el ID está fuera de rango, usar el primer estudiante
                current_user = list(current_users)[0]
        
        speak_with_animation(engine, f"Sí, {current_user}, ¿cuál es tu pregunta?")
        
        # Escuchar la pregunta con mejor manejo de errores
        question = listen(timeout=10)  # Aumentamos el timeout para preguntas
        hand_raised_counter.value = 0
        
        if not question or question in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""]:
            if question and question.startswith("error"):
                speak_with_animation(engine, "Hubo un problema con el reconocimiento de voz. Continuemos con la clase.")
            else:
                speak_with_animation(engine, "No pude entender tu pregunta. Continuemos con la clase.")
            return True
        
        try:
            answer = ask_openai(question, pdf_text)
            speak_with_animation(engine, answer)
        except Exception as e:
            print(f"❌ Error al procesar la respuesta con OpenAI: {e}")
            speak_with_animation(engine, "Lo siento, tuve un problema al generar una respuesta. Continuemos con la clase.")
        
        # Preguntar si hay más preguntas solo si no se detectó una mano levantada
        if hand_raised_counter.value == 0:
            speak_with_animation(engine, "¿Alguien más tiene alguna pregunta sobre el tema del PDF?")
            follow_up = listen()
            
            if follow_up and follow_up not in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""] and "sí" in follow_up.lower():
                return process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
            else:
                speak_with_animation(engine, "Bien, continuemos con la clase.")
        else:
            speak_with_animation(engine, "Continuemos con la clase.")
        
        return True
    except Exception as e:
        print(f"❌ Error general en proceso de preguntas: {e}")
        speak_with_animation(engine, "Hubo un problema al procesar la pregunta. Continuemos con la clase.")
        return True

def explain_slides_with_random_questions(engine, pdf_path, pdf_text, current_users,
                                        hand_raised_counter, current_slide_num, exit_flag, 
                                        known_faces, current_hand_raiser):
    """
    Explicación de diapositivas con preguntas aleatorias cada 3 slides - CÓDIGO TRADICIONAL
    
    Args:
        engine: Motor de TTS
        pdf_path: Ruta al archivo PDF
        pdf_text: Texto del PDF
        current_users: Lista de usuarios actuales
        hand_raised_counter: Contador de manos levantadas
        current_slide_num: Número de diapositiva actual
        exit_flag: Bandera de salida
        known_faces: Diccionario de caras conocidas
        current_hand_raiser: ID del usuario que levantó la mano
        
    Returns:
        bool: True si se completó exitosamente
    """
    try:
        print("📊 Iniciando explicación con sistema de preguntas aleatorias...")
        
        # Importar funciones necesarias
        from .speech import speak_with_animation
        from .questions import RandomQuestionManager
        
        # Inicializar gestor de preguntas
        question_manager = RandomQuestionManager(current_users)

        # Crear ventana "Presentacion" para mostrar cada página
        cv2.namedWindow("Presentacion", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Presentacion", 800, 600)

        with fitz.open(pdf_path) as doc:
            total_slides = len(doc)
            slide_num = 0
            
            while slide_num < total_slides and exit_flag.value == 0:
                current_slide_num.value = slide_num + 1
                print(f"📝 Explicando diapositiva {current_slide_num.value} de {total_slides}")
                
                # Verificar manos levantadas antes de continuar
                if hand_raised_counter.value > 0:
                    print(f"✋ Manos levantadas detectadas: {hand_raised_counter.value}")
                    process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                    continue
                
                page = doc[slide_num]
                # Mostrar la imagen de la diapositiva
                page_img = show_pdf_page_in_opencv(page)
                cv2.imshow("Presentacion", page_img)
                cv2.waitKey(50)

                # Obtener texto y generar explicación
                page_text = page.get_text()

                if page_text.strip():
                    prompt = f"""
                    El siguiente texto es de una diapositiva de clase sobre robótica. 
                    No resumas simplemente el contenido, sino explícalo como lo haría un profesor 
                    entusiasta en clase pero hacerlo CONCISO máximo (4-5 frases),
                    añadiendo contexto y haciéndolo interesante y conversacional:
                    
                    Contenido:
                    {page_text}
                    """
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": """Eres ADAI, Asistente Docente Androide de Ingeniería. 
                                    IMPORTANTE: NO uses emojis, símbolos especiales, ni caracteres no alfabéticos en tus respuestas 
                                    ya que serán leídas en voz alta por un sintetizador de voz. 
                                    Usa solo texto simple, claro y profesional. Sé entusiasta pero con palabras, no con símbolos."""},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        explanation = response.choices[0].message.content
                    except Exception as e:
                        print(f"❌ Error en OpenAI: {e}")
                        explanation = summarize_text(page_text)
                else:
                    # Si no hay texto en la página
                    image_path = os.path.join(os.path.dirname(pdf_path), f"page{slide_num + 1}.png")
                    page.get_pixmap().save(image_path)
                    explanation = interpret_image(image_path)
                
                # Mensaje inicial
                slide_info = f"Diapositiva {slide_num + 1}: "
                speak_with_animation(engine, slide_info)

                # Explicación en frases
                sentences = []
                for part in explanation.split("."):
                    if part.strip():
                        sentences.append(part.strip() + ".")

                for i, sentence in enumerate(sentences):
                    if hand_raised_counter.value > 0:
                        print(f"✋ Manos levantadas detectadas: {hand_raised_counter.value}")
                        process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                        continue
                    
                    if exit_flag.value != 0:
                        print("🛑 Señal de salida detectada")
                        return False
                    
                    if sentence.strip():
                        print(f"🗣️ Fragmento {i+1}/{len(sentences)}: {sentence[:30]}...")
                        speak_with_animation(engine, sentence)
                    
                    time.sleep(0.2)
                
                # Pequeña pausa
                for _ in range(5):
                    if hand_raised_counter.value > 0 or exit_flag.value != 0:
                        break
                    time.sleep(0.2)
                
                if hand_raised_counter.value > 0:
                    print(f"✋ Manos levantadas tras la diapositiva: {hand_raised_counter.value}")
                    process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                    continue
                
                slide_num += 1
                
                # *** PREGUNTA ALEATORIA CADA 3 DIAPOSITIVAS ***
                if slide_num % 3 == 0 and slide_num < total_slides:
                    print(f"\n🎯 === PREGUNTA ALEATORIA (después de diapositiva {slide_num}) ===")
                    
                    # Pausa antes de la pregunta
                    speak_with_animation(engine, "Muy bien. Ahora haremos una pausa para verificar el aprendizaje.")
                    time.sleep(1.0)
                    
                    # Realizar pregunta aleatoria
                    question_manager.conduct_random_question(engine, pdf_text)
                    
                    # Pausa después de la pregunta antes de continuar
                    time.sleep(1.0)
                    
                    # Anunciar continuación
                    if slide_num < total_slides:
                        speak_with_animation(engine, "Excelente. Continuemos con la siguiente sección.")
                    
                    print(f"🎯 === FIN DE PREGUNTA ALEATORIA ===\n")
        
        # Mostrar estadísticas finales
        stats = question_manager.get_statistics()
        print("\n📊 === ESTADÍSTICAS DE PREGUNTAS ===")
        print(f"Total de preguntas realizadas: {stats['total_questions']}")
        print("Preguntas por estudiante:")
        for student, count in stats['questions_per_student'].items():
            print(f"  - {student}: {count}")
        
        print("✅ Explicación de diapositivas completada")
        return True
        
    except Exception as e:
        print(f"❌ Error al explicar diapositivas: {e}")
        return False

def explain_slides_with_sequences(engine, pdf_path, pdf_text, current_users,
                                 hand_raised_counter, current_slide_num, exit_flag, 
                                 known_faces, current_hand_raiser, sequence_mapping=None):
    """
    Explicación de diapositivas con secuencias ESP32 después de cada página
    
    Args:
        engine: Motor de TTS
        pdf_path: Ruta al archivo PDF
        pdf_text: Texto del PDF
        current_users: Lista de usuarios actuales
        hand_raised_counter: Contador de manos levantadas
        current_slide_num: Número de diapositiva actual
        exit_flag: Bandera de salida
        known_faces: Diccionario de caras conocidas
        current_hand_raiser: ID del usuario que levantó la mano
        sequence_mapping: Diccionario que mapea número de diapositiva -> nombre de secuencia
        
    Returns:
        bool: True si se completó exitosamente
    """
    try:
        print("🎬 Iniciando explicación con secuencias ESP32...")
        
        # Importar funciones necesarias
        from .speech import speak_with_animation
        from .config import get_script_dir
        
        # Mapeo de secuencias por defecto si no se proporciona
        if sequence_mapping is None:
            sequence_mapping = {
                1: "saludo_inicial",
                3: "gesto_paz", 
                5: "hablar_clase",
                7: "gesto_ok",
                9: "despedida"
            }
        
        print(f"📋 Mapeo de secuencias: {sequence_mapping}")

        # Crear ventana "Presentacion" para mostrar cada página
        cv2.namedWindow("Presentacion", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Presentacion", 800, 600)

        with fitz.open(pdf_path) as doc:
            total_slides = len(doc)
            slide_num = 0
            
            while slide_num < total_slides and exit_flag.value == 0:
                current_slide_num.value = slide_num + 1
                print(f"📝 Explicando diapositiva {current_slide_num.value} de {total_slides}")
                
                # Verificar manos levantadas antes de continuar
                if hand_raised_counter.value > 0:
                    print(f"✋ Manos levantadas detectadas: {hand_raised_counter.value}")
                    process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                    continue
                
                page = doc[slide_num]
                # Mostrar la imagen de la diapositiva
                page_img = show_pdf_page_in_opencv(page)
                cv2.imshow("Presentacion", page_img)
                cv2.waitKey(50)

                # Obtener texto y generar explicación
                page_text = page.get_text()

                if page_text.strip():
                    prompt = f"""
                    El siguiente texto es de una diapositiva de clase sobre robótica. 
                    No resumas simplemente el contenido, sino explícalo como lo haría un profesor 
                    entusiasta en clase pero hacerlo CONCISO máximo (4-5 frases),
                    añadiendo contexto y haciéndolo interesante y conversacional:
                    
                    Contenido:
                    {page_text}
                    """
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": """Eres ADAI, Asistente Docente Androide de Ingeniería. 
                                    IMPORTANTE: NO uses emojis, símbolos especiales, ni caracteres no alfabéticos en tus respuestas 
                                    ya que serán leídas en voz alta por un sintetizador de voz. 
                                    Usa solo texto simple, claro y profesional. Sé entusiasta pero con palabras, no con símbolos."""},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        explanation = response.choices[0].message.content
                    except Exception as e:
                        print(f"❌ Error en OpenAI: {e}")
                        explanation = summarize_text(page_text)
                else:
                    # Si no hay texto en la página
                    script_dir = get_script_dir()
                    image_path = os.path.join(script_dir, f"page{slide_num + 1}.png")
                    page.get_pixmap().save(image_path)
                    explanation = interpret_image(image_path)
                
                # Mensaje inicial
                slide_info = f"Diapositiva {slide_num + 1}: "
                speak_with_animation(engine, slide_info)

                # Explicación en frases
                sentences = []
                for part in explanation.split("."):
                    if part.strip():
                        sentences.append(part.strip() + ".")

                for i, sentence in enumerate(sentences):
                    if hand_raised_counter.value > 0:
                        print(f"✋ Manos levantadas detectadas: {hand_raised_counter.value}")
                        process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                        continue
                    
                    if exit_flag.value != 0:
                        print("🛑 Señal de salida detectada")
                        return False
                    
                    if sentence.strip():
                        print(f"🗣️ Fragmento {i+1}/{len(sentences)}: {sentence[:30]}...")
                        speak_with_animation(engine, sentence)
                    
                    time.sleep(0.2)
                
                # *** EJECUTAR SECUENCIA ESP32 DESPUÉS DE LA DIAPOSITIVA ***
                current_slide_number = slide_num + 1
                if current_slide_number in sequence_mapping:
                    sequence_name = sequence_mapping[current_slide_number]
                    print(f"\n🤖 === EJECUTANDO SECUENCIA ESP32 (después de diapositiva {current_slide_number}) ===")
                    print(f"🎬 Secuencia: {sequence_name}")
                    
                    # Anunciar la secuencia
                    speak_with_animation(engine, f"Ahora ejecutaré una secuencia de movimientos del robot.")
                    time.sleep(1.0)
                    
                    # Ejecutar la secuencia
                    success = execute_esp32_sequence(sequence_name)
                    
                    if success:
                        print(f"✅ Secuencia '{sequence_name}' ejecutada exitosamente")
                        speak_with_animation(engine, "Secuencia completada.")
                    else:
                        print(f"❌ Error ejecutando secuencia '{sequence_name}'")
                        speak_with_animation(engine, "Hubo un problema con la secuencia, continuemos.")
                    
                    # Pausa después de la secuencia
                    time.sleep(2.0)
                    
                    print(f"🤖 === FIN DE SECUENCIA ESP32 ===\n")
                
                # Pequeña pausa
                for _ in range(5):
                    if hand_raised_counter.value > 0 or exit_flag.value != 0:
                        break
                    time.sleep(0.2)
                
                if hand_raised_counter.value > 0:
                    print(f"✋ Manos levantadas tras la diapositiva: {hand_raised_counter.value}")
                    process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                    continue
                
                slide_num += 1
        
        print("✅ Explicación con secuencias completada")
        return True
        
    except Exception as e:
        print(f"❌ Error al explicar diapositivas con secuencias: {e}")
        return False
