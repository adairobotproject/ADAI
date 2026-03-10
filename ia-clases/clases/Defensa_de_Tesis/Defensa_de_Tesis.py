#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defensa de Tesis
Materia: Presentación Académica
Generado por ADAI Class Builder el 2025-10-27 11:35:00

Clase automática usando demo_sequence_manager
"""

import cv2
import os
import time
import multiprocessing
from multiprocessing import Process, Value
import sys
import requests
import tempfile
import pygame
import fitz  # PyMuPDF
import openai
import threading
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

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
        show_pdf_page_in_opencv, extract_text_from_pdf, show_pdf_fullscreen,
        explain_slides_with_sequences,
        execute_esp32_sequence, summarize_text, ask_openai,
        check_teacher_request, check_class_paused, wait_for_resume, process_question, process_teacher_request
    )
    print("✅ Funciones importadas desde demo_sequence_manager")
except ImportError as e:
    print(f"❌ Error importando funciones: {e}")
    print("⚠️ Asegúrate de que demo_sequence_manager.py esté en la carpeta main/")
    print(f"🔍 Buscando en: {main_dir}")
    sys.exit(1)

# ======================
#  CONFIGURACIÓN DE ELEVENLABS
# ======================
# Cargar API keys desde variables de entorno
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_API_KEY_2 = os.getenv("ELEVENLABS_API_KEY_2", "")  # Segunda API key de respaldo

# ID de voz de ElevenLabs (puedes cambiar por otra voz disponible)
# Voces populares: "21m00Tcm4TlvDq8ikWAM" (Rachel), "EXAVITQu4vr4xnSDxMaL" (Bella), 
#                  "ErXwobaYiN019PkySvjV" (Antoni), "VR6AewLTigWG4xSOukaG" (Arnold)
ELEVENLABS_VOICE_ID = "ErXwobaYiN019PkySvjV"  # Antoni - voz masculina profesional

# Configuración del modelo de ElevenLabs
ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"  # Soporta español

# Inicializar pygame para reproducción de audio
pygame.mixer.init()

# Inicializar cliente OpenAI (usando API key desde variables de entorno)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    print("⚠️ ADVERTENCIA: OPENAI_API_KEY no encontrada en variables de entorno")
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

def elevenlabs_speak(text, api_key=None, voice_id=None, stability=0.5, similarity_boost=0.75):
    """
    Función para generar y reproducir voz usando ElevenLabs API
    
    Args:
        text: Texto a convertir en voz
        api_key: API key de ElevenLabs a usar (opcional, usa ELEVENLABS_API_KEY por defecto)
        voice_id: ID de la voz a usar (opcional, usa ELEVENLABS_VOICE_ID por defecto)
        stability: Estabilidad de la voz (0.0 a 1.0)
        similarity_boost: Mejora de similitud (0.0 a 1.0)
    
    Returns:
        bool: True si se reprodujo correctamente, False en caso de error
    """
    api_key = api_key or ELEVENLABS_API_KEY
    if not api_key or api_key == "TU_API_KEY_AQUI":
        return False
    
    voice = voice_id or ELEVENLABS_VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": ELEVENLABS_MODEL_ID,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }
    
    try:
        print(f"🎤 ElevenLabs: Generando audio para: '{text[:50]}...'")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Guardar audio temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            # Reproducir audio
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Esperar a que termine la reproducción
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Limpiar archivo temporal
            try:
                os.unlink(temp_path)
            except:
                pass
            
            print("✅ Audio reproducido correctamente")
            return True
        else:
            print(f"❌ Error ElevenLabs: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout al conectar con ElevenLabs")
        return False
    except Exception as e:
        print(f"❌ Error en ElevenLabs: {e}")
        return False

def speak_elevenlabs_with_animation(engine, text, face_window="ADAI Robot Face"):
    """
    Habla usando ElevenLabs con animación facial
    Intenta con la primera API key, luego con la segunda, y si ambas fallan, usa el engine TTS local como fallback
    
    Args:
        engine: Motor TTS local (pyttsx3) como fallback
        text: Texto a hablar
        face_window: Nombre de la ventana de la cara animada
    """
    print(f"🗣️ ADAI dice: {text}")
    
    # Intentar usar ElevenLabs con la primera API key
    success = elevenlabs_speak(text, api_key=ELEVENLABS_API_KEY)
    
    if not success:
        # Intentar con la segunda API key
        print("🔄 Intentando con segunda API key de ElevenLabs...")
        success = elevenlabs_speak(text, api_key=ELEVENLABS_API_KEY_2)
    
    if not success:
        # Fallback a TTS local si ambas API keys fallaron
        print("🔄 Ambas API keys de ElevenLabs fallaron. Usando TTS local como fallback...")
        speak_with_animation(engine, text)

# ======================
#  MONKEY PATCH PARA IDENTIFY_USERS CON ELEVENLABS
# ======================
def identify_users_with_elevenlabs(engine, current_slide_num, exit_flag):
    """
    Wrapper de identify_users que reemplaza speak_with_animation por speak_elevenlabs_with_animation
    """
    # Importar identify_users desde demo_sequence_manager
    from demo_sequence_manager import identify_users as original_identify_users
    import demo_sequence_manager
    
    # Guardar la función original
    original_speak = demo_sequence_manager.speak_with_animation
    
    # Reemplazar temporalmente speak_with_animation con speak_elevenlabs_with_animation
    demo_sequence_manager.speak_with_animation = lambda eng, txt: speak_elevenlabs_with_animation(eng, txt)
    
    try:
        # Llamar a la función original (ahora usará speak_elevenlabs_with_animation)
        result = original_identify_users(engine, current_slide_num, exit_flag)
        return result
    finally:
        # Restaurar la función original
        demo_sequence_manager.speak_with_animation = original_speak

# ======================
#  FUNCIÓN PERSONALIZADA PARA DEFENSA DE TESIS
# ======================
def explain_thesis_slides_with_memory(engine, pdf_path, pdf_text, current_users,
                                      hand_raised_counter, current_slide_num, exit_flag, 
                                      known_faces, current_hand_raiser, sequence_mapping=None, 
                                      full_thesis_context=None, extra_context_mapping=None):
    """
    Explicación de diapositivas de defensa de tesis con memoria conversacional.
    Mantiene contexto de las diapositivas anteriores y usa un contexto apropiado para defensa académica.
    
    Args:
        full_thesis_context: Texto completo del documento de la tesis para contexto adicional (opcional)
        extra_context_mapping: Diccionario que mapea número de diapositiva a contexto extra (opcional)
                              Ejemplo: {3: "Esta diapositiva muestra un diagrama del sistema...", 5: "..."}
    """
    try:
        print("🎬 Iniciando explicación de defensa de tesis con memoria conversacional...")
        
        # Mapeo de secuencias por defecto si no se proporciona
        if sequence_mapping is None:
            sequence_mapping = {
                1: "ClaseMove",
                2: "CuelloMove",
                3: "ClaseMove",
                4: "CuelloMove",
                5: "ClaseMove",
                6: "CuelloMove",
                7: "ClaseMove",
                8: "CuelloMove",
                9: "ClaseMove",
                10: "CuelloMove",
            }
        
        print(f"📋 Mapeo de secuencias: {sequence_mapping}")
        
        # Mapeo de contexto extra por defecto (vacío)
        if extra_context_mapping is None:
            extra_context_mapping = {}
        
        if extra_context_mapping:
            print(f"📝 Mapeo de contexto extra: {list(extra_context_mapping.keys())} diapositivas")
        
        # Crear ventana "Presentacion" para mostrar cada página
        cv2.namedWindow("Presentacion", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Presentacion", 800, 600)
        
        # Preparar contexto del sistema con información del documento completo si está disponible
        system_content = """Eres ADAI, asistente durante una defensa de tesis académica.
                Estás presentando las diapositivas de una tesis de investigación.
                IMPORTANTE: NO uses emojis, símbolos especiales, ni caracteres no alfabéticos en tus respuestas 
                ya que serán leídas en voz alta por un sintetizador de voz. 
                Usa solo texto simple, claro y profesional.
                Tu tono debe ser formal y académico, apropiado para una defensa de tesis.
                Recuerda el contexto de las diapositivas anteriores cuando expliques cada nueva diapositiva.
                Sé conciso pero completo (4-5 frases por diapositiva)."""
        
        # Agregar contexto del documento completo si está disponible
        if full_thesis_context:
            # Limitar el contexto a los primeros 3000 caracteres para no exceder límites de tokens
            context_preview = full_thesis_context[:3000] if len(full_thesis_context) > 3000 else full_thesis_context
            system_content += f"""
                
                CONTEXTO ADICIONAL DEL DOCUMENTO COMPLETO DE LA TESIS:
                Tienes acceso al documento completo de la tesis para proporcionar contexto adicional.
                Úsalo para enriquecer tus explicaciones con información más detallada cuando sea relevante.
                
                Fragmento del documento completo:
                {context_preview}"""
            if len(full_thesis_context) > 3000:
                system_content += f"\n\n[Nota: El documento completo tiene {len(full_thesis_context)} caracteres. Usa este contexto para proporcionar información más detallada cuando sea relevante.]"
        
        # Abrir PDF PRIMERO para contar diapositivas y calcular tiempos ANTES de configurar el sistema
        print("📊 Revisando número de diapositivas...")
        doc = fitz.open(pdf_path)
        total_slides = len(doc)
        doc.close()
        print(f"✅ Total de diapositivas detectadas: {total_slides}")
        
        # Calcular tiempo disponible (12 minutos = 720 segundos REALES)
        # IMPORTANTE: El tiempo real de habla es aproximadamente el DOBLE del tiempo asignado
        # Por lo tanto, asignamos la MITAD del tiempo para cumplir con el límite de 12 minutos
        MAX_PRESENTATION_TIME_REAL = 12 * 60  # 720 segundos reales = 12 minutos
        MAX_PRESENTATION_TIME = MAX_PRESENTATION_TIME_REAL / 2  # 360 segundos asignados (se convertirán en ~720 reales)
        
        FIRST_SLIDE_TIME = 15  # Primera diapositiva: 15 segundos asignados (~30 reales, menos tiempo)
        
        # Calcular tiempo para el resto de diapositivas
        # Si hay más de 10 diapositivas, dar más tiempo a las después de la 10
        remaining_time = MAX_PRESENTATION_TIME - FIRST_SLIDE_TIME
        
        if total_slides > 10:
            # Más de 10 diapositivas: dar más prioridad a las después de la 10
            slides_2_to_10 = min(9, total_slides - 1)  # Diapositivas 2-10 (máximo 9)
            slides_11_plus = total_slides - 10  # Diapositivas 11 en adelante
            
            # Distribución: 25% para 2-10 (muy resumidas), 75% para 11+ (más tiempo y prioridad)
            time_for_first_group = remaining_time * 0.25
            time_for_second_group = remaining_time * 0.75
            
            if slides_2_to_10 > 0:
                time_per_slide_2_10 = time_for_first_group / slides_2_to_10
            else:
                time_per_slide_2_10 = 0
            
            if slides_11_plus > 0:
                time_per_slide_11_plus = time_for_second_group / slides_11_plus
            else:
                time_per_slide_11_plus = 0
        elif total_slides > 1:
            # 10 o menos diapositivas: distribución normal
            time_per_slide = remaining_time / (total_slides - 1)
            time_per_slide_2_10 = time_per_slide
            time_per_slide_11_plus = 0
        else:
            # Solo 1 diapositiva
            time_per_slide_2_10 = MAX_PRESENTATION_TIME
            time_per_slide_11_plus = 0
        
        # NOTA: Los tiempos asignados se multiplican por ~2 en tiempo real al hablar
        
        # Crear diccionario de tiempos por diapositiva
        slide_times = {}
        for i in range(1, total_slides + 1):
            if i == 1:
                slide_times[i] = FIRST_SLIDE_TIME
            elif i <= 10:
                slide_times[i] = time_per_slide_2_10
            else:
                slide_times[i] = time_per_slide_11_plus
        
        # Mensajes para mantener memoria conversacional
        conversation_messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]
        
        print(f"⏱️ Tiempo total disponible: {MAX_PRESENTATION_TIME_REAL} segundos reales ({MAX_PRESENTATION_TIME_REAL/60:.1f} minutos)")
        print(f"⏱️ Tiempo asignado (se duplica al hablar): {MAX_PRESENTATION_TIME:.0f} segundos ({MAX_PRESENTATION_TIME/60:.1f} minutos)")
        print(f"📊 Total de diapositivas: {total_slides}")
        print(f"⏱️ Distribución de tiempo (asignado → real aproximado):")
        print(f"   - Diapositiva 1: {FIRST_SLIDE_TIME} segundos (~{FIRST_SLIDE_TIME*2:.0f} segundos reales, {FIRST_SLIDE_TIME*2/60:.1f} minutos)")
        if total_slides > 10:
            print(f"   - Diapositivas 2-10: {time_per_slide_2_10:.1f}s asignados (~{time_per_slide_2_10*2:.0f}s reales, {time_per_slide_2_10*2/60:.2f} min) - Prioridad baja")
            print(f"   - Diapositivas 11-{total_slides}: {time_per_slide_11_plus:.1f}s asignados (~{time_per_slide_11_plus*2:.0f}s reales, {time_per_slide_11_plus*2/60:.2f} min) - Prioridad ALTA")
        elif total_slides > 1:
            print(f"   - Diapositivas 2-{total_slides}: {time_per_slide_2_10:.1f}s asignados (~{time_per_slide_2_10*2:.0f}s reales, {time_per_slide_2_10*2/60:.2f} min)")
        
        # Reabrir PDF para procesamiento
        with fitz.open(pdf_path) as doc:
            slide_num = 0
            
            while slide_num < total_slides and exit_flag.value == 0:
                current_slide_num.value = slide_num + 1
                print(f"📝 Explicando diapositiva {current_slide_num.value} de {total_slides}")
                
                # Verificar manos levantadas antes de continuar (deshabilitado - no hay detección de caras/estudiantes)
                # if hand_raised_counter.value > 0:
                #     print(f"✋ Manos levantadas detectadas: {hand_raised_counter.value}")
                #     process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                #     continue
                
                # Verificar solicitudes de profesora
                has_request, request_type = check_teacher_request()
                if has_request:
                    print(f"📚 Solicitud de profesora detectada")
                    process_teacher_request(engine, pdf_text)
                    continue
                
                # Verificar si la clase está pausada
                if check_class_paused():
                    wait_for_resume(engine)
                    continue
                
                page = doc[slide_num]
                # Mostrar la imagen de la diapositiva en pantalla completa
                page_img = show_pdf_page_in_opencv(page)
                show_pdf_fullscreen(page_img, "Presentacion")
                
                # Obtener texto de la diapositiva
                page_text = page.get_text()
                
                # Verificar si hay contexto extra para esta diapositiva
                current_slide_number = slide_num + 1
                extra_context = extra_context_mapping.get(current_slide_number, "")
                
                # Obtener tiempo disponible para esta diapositiva
                available_time = slide_times.get(current_slide_number, 60)  # 60 segundos por defecto
                
                # Combinar texto de la diapositiva con contexto extra si está disponible
                if extra_context:
                    if page_text.strip():
                        # Si hay texto y contexto extra, combinarlos
                        combined_text = f"{page_text}\n\n[Contexto adicional proporcionado]:\n{extra_context}"
                    else:
                        # Si no hay texto pero hay contexto extra, usar solo el contexto extra
                        combined_text = f"[Esta diapositiva contiene principalmente elementos visuales. Contexto proporcionado]:\n{extra_context}"
                else:
                    combined_text = page_text
                
                if combined_text.strip():
                    # Crear prompt con contexto de defensa de tesis y memoria
                    # Incluir resumen de diapositivas anteriores si hay más de una
                    context_summary = ""
                    if len(conversation_messages) > 1:
                        # Extraer las últimas explicaciones para contexto
                        recent_explanations = []
                        for msg in conversation_messages[-min(3, len(conversation_messages)-1):]:
                            if msg["role"] == "assistant":
                                recent_explanations.append(msg["content"][:200])  # Primeros 200 chars
                        if recent_explanations:
                            context_summary = "\n\nContexto de diapositivas anteriores (para mantener coherencia):\n" + "\n".join(recent_explanations)
                    
                    # Incluir referencia al contexto completo si está disponible
                    context_note = ""
                    if full_thesis_context:
                        context_note = "\n\nNota: Tienes acceso al documento completo de la tesis. Úsalo para enriquecer la explicación con detalles adicionales cuando sea relevante."
                    
                    # Determinar si hay contexto extra para mencionarlo
                    extra_context_note = ""
                    if extra_context:
                        extra_context_note = "\n\nIMPORTANTE: Esta diapositiva tiene contexto adicional proporcionado. Úsalo para explicar el contenido visual o enriquecer la explicación."
                    
                    # Calcular tiempo real estimado (se duplica al hablar)
                    estimated_real_time = available_time * 2
                    
                    # Ajustar longitud de explicación según tiempo disponible
                    # Las primeras 10 diapositivas usan máximo 1 frase y son ultra-resumidas para dar más tiempo a las demás
                    if current_slide_number <= 10:
                        time_instruction = f"""TIEMPO MÁXIMO DISPONIBLE: {available_time:.0f} segundos asignados (aproximadamente {estimated_real_time:.0f} segundos reales de habla).
                    CRÍTICO: Esta es una de las primeras 10 diapositivas. Debes ser ULTRA-RESUMIDO y EXTREMADAMENTE BREVE (solo lo esencial) para darle MÁXIMO tiempo y prioridad a las diapositivas posteriores (11+).
                    INSTRUCCIÓN DE BREVEDAD MÁXIMA: Tu respuesta debe ser UNA SOLA FRASE MUY CORTA (máximo 15-20 palabras). 
                    LIMITACIÓN ABSOLUTA: EXACTAMENTE UNA SOLA FRASE CORTA. No uses punto y seguido, no uses más de una frase, no agregues detalles innecesarios. Sé extremadamente directo, específico y conciso. Solo menciona lo esencial del contenido. Esta ultra-brevedad es intencional y crítica para maximizar el tiempo disponible en las diapositivas más importantes que vienen después."""
                    elif extra_context:
                        time_instruction = f"""TIEMPO MÁXIMO DISPONIBLE: {available_time:.0f} segundos asignados (aproximadamente {estimated_real_time:.0f} segundos reales de habla).
                    Debes crear una explicación que pueda leerse en este tiempo máximo.
                    LIMITACIÓN: Usa 4 a 5 frases. Incluye el contexto adicional proporcionado para enriquecer la explicación."""
                    elif available_time <= 15:
                        time_instruction = f"""TIEMPO MÁXIMO DISPONIBLE: {available_time:.0f} segundos asignados (aproximadamente {estimated_real_time:.0f} segundos reales de habla).
                    Debes crear una explicación MUY CONCISA que pueda leerse en este tiempo máximo.
                    LIMITACIÓN: Usa 1 a 2 frases. Sé extremadamente directo y específico."""
                    elif available_time <= 25:
                        time_instruction = f"""TIEMPO MÁXIMO DISPONIBLE: {available_time:.0f} segundos asignados (aproximadamente {estimated_real_time:.0f} segundos reales de habla).
                    Debes crear una explicación CONCISA que pueda leerse en este tiempo máximo.
                    LIMITACIÓN: Usa 2 a 3 frases. Sé directo y eficiente."""
                    else:
                        time_instruction = f"""TIEMPO MÁXIMO DISPONIBLE: {available_time:.0f} segundos asignados (aproximadamente {estimated_real_time:.0f} segundos reales de habla).
                    Debes crear una explicación que pueda leerse en este tiempo máximo.
                    LIMITACIÓN: Usa 3 a 4 frases. Sé conciso pero completo."""
                    
                    prompt = f"""Estás presentando la diapositiva {current_slide_num.value} de {total_slides} de una defensa de tesis.
                    El siguiente texto corresponde al contenido de esta diapositiva.
                    {context_summary}{context_note}{extra_context_note}
                    
                    {time_instruction}
                    
                    INSTRUCCIONES PARA LA EXPLICACIÓN:
                    - Explica este contenido de manera formal y académica, apropiada para una defensa de tesis.
                    - Mantén coherencia con las diapositivas anteriores si es relevante.
                    - Si tienes información adicional relevante del documento completo de la tesis, úsala para enriquecer la explicación.
                    - No simplemente leas el contenido, sino explícalo de manera clara y profesional.
                    - RESPETA ESTRICTAMENTE el tiempo máximo disponible especificado arriba. Ajusta la longitud de tu explicación para que pueda leerse dentro del tiempo límite.
                    
                    Contenido de la diapositiva {current_slide_num.value}:
                    {combined_text}"""
                    
                    # Agregar el prompt a la conversación
                    conversation_messages.append({"role": "user", "content": prompt})
                    
                    try:
                        response = openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=conversation_messages,
                            temperature=0.7
                        )
                        explanation = response.choices[0].message.content
                        
                        # Agregar la explicación a la conversación para memoria
                        conversation_messages.append({"role": "assistant", "content": explanation})
                        
                        # Limitar el tamaño de la conversación para no exceder tokens
                        # Mantener el mensaje del sistema y los últimos 6 intercambios (3 user + 3 assistant)
                        if len(conversation_messages) > 13:  # 1 system + 6 user + 6 assistant = 13
                            conversation_messages = [conversation_messages[0]] + conversation_messages[-12:]
                        
                    except Exception as e:
                        print(f"❌ Error en OpenAI: {e}")
                        explanation = summarize_text(combined_text if combined_text else page_text)
                else:
                    # Si no hay texto ni contexto extra, usar resumen básico
                    explanation = f"Esta diapositiva {current_slide_num.value} contiene principalmente elementos visuales."
                
                # Ejecutar secuencia ESP32 en paralelo si existe
                current_slide_number = slide_num + 1
                if current_slide_number in sequence_mapping:
                    sequence_name = sequence_mapping[current_slide_number]
                    print(f"\n🤖 === INICIANDO SECUENCIA ESP32 EN PARALELO (diapositiva {current_slide_number}) ===")
                    print(f"🎬 Secuencia: {sequence_name}")
                    try:
                        seq_thread = threading.Thread(target=execute_esp32_sequence, args=(sequence_name,), daemon=True)
                        seq_thread.start()
                        print(f"✅ Secuencia '{sequence_name}' iniciada en paralelo")
                    except Exception as e:
                        print(f"❌ No se pudo iniciar la secuencia en paralelo: {e}")
                
                # Registrar tiempo de inicio para esta diapositiva
                slide_start_time = time.time()
                
                # Explicación en frases (sin mencionar el número de diapositiva para ahorrar tiempo)
                sentences = []
                for part in explanation.split("."):
                    if part.strip():
                        sentences.append(part.strip() + ".")
                
                for i, sentence in enumerate(sentences):
                    # Verificación de manos levantadas deshabilitada (no hay detección de caras/estudiantes)
                    # if hand_raised_counter.value > 0:
                    #     print(f"✋ Manos levantadas detectadas: {hand_raised_counter.value}")
                    #     process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                    #     continue
                    
                    # Verificar solicitudes de profesora durante explicación
                    has_request, request_type = check_teacher_request()
                    if has_request:
                        print(f"📚 Solicitud de profesora detectada")
                        process_teacher_request(engine, pdf_text)
                        continue
                    
                    # Verificar si la clase está pausada
                    if check_class_paused():
                        wait_for_resume(engine)
                        continue
                    
                    if exit_flag.value != 0:
                        print("🛑 Señal de salida detectada")
                        return False
                    
                    if sentence.strip():
                        print(f"🗣️ Fragmento {i+1}/{len(sentences)}: {sentence[:30]}...")
                        speak_elevenlabs_with_animation(engine, sentence)
                    
                    time.sleep(0.2)
                
                # Calcular tiempo utilizado y mostrarlo
                slide_elapsed_time = time.time() - slide_start_time
                print(f"⏱️ Tiempo utilizado en diapositiva {current_slide_num.value}: {slide_elapsed_time:.1f}s / {available_time:.1f}s disponible")
                
                # Pequeña pausa
                for _ in range(5):
                    # Verificación de manos levantadas deshabilitada (no hay detección de caras/estudiantes)
                    # if hand_raised_counter.value > 0 or exit_flag.value != 0:
                    if exit_flag.value != 0:
                        break
                    has_request, _ = check_teacher_request()
                    if has_request:
                        break
                    # Verificar pausa
                    if check_class_paused():
                        wait_for_resume(engine)
                        break
                    time.sleep(0.2)
                
                # Verificación de manos levantadas deshabilitada (no hay detección de caras/estudiantes)
                # if hand_raised_counter.value > 0:
                #     print(f"✋ Manos levantadas detectadas: {hand_raised_counter.value}")
                #     process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                #     continue
                
                # Verificar solicitudes de profesora tras la diapositiva
                has_request, request_type = check_teacher_request()
                if has_request:
                    print(f"📚 Solicitud de profesora detectada tras diapositiva")
                    process_teacher_request(engine, pdf_text)
                    continue
                
                slide_num += 1
        
        print("✅ Explicación de defensa de tesis completada")
        return True
        
    except Exception as e:
        print(f"❌ Error al explicar diapositivas de defensa de tesis: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal que ejecuta la defensa de tesis completa"""
    try:
        print("🚀 Iniciando: Defensa de Tesis")
        print("🎓 Evento: Presentación Académica")
        
        # Definir rutas de archivos
        # NOTA: Actualizar estas rutas con los archivos correspondientes
        diagnostic_qr = "C:/Users/josue/Desktop/CvLD1_ZUEAAmRG6.jpg"
        class_pdf = "C:/Users/josue/Downloads/DefensaTesis2026.pdf"  # Actualizar con el PDF de la tesis
        final_exam_qr = "C:/Users/josue/Desktop/CvLD1_ZUEAAmRG6.jpg"
        
        # Inicializar TTS
        engine = initialize_tts()
        if not engine:
            print("❌ No se pudo inicializar el motor TTS")
            return
        
        # Crear ventana para la cara animada
        cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("ADAI Robot Face", 600, 400)
        
        # Verificar cámara - DESHABILITADO (no se detectan caras ni estudiantes)
        # if not verify_camera_for_iriun():
        #     print("⚠️ Problemas detectados con la cámara.")
        #     return
        
        # Variables compartidas para multiprocessing
        hand_raised_counter = multiprocessing.Value('i', 0)
        current_slide_num = multiprocessing.Value('i', 1)
        exit_flag = multiprocessing.Value('i', 0)
        current_hand_raiser = multiprocessing.Value('i', -1)
        
        # NOTA: Para defensa de tesis no se detectan caras ni estudiantes
        # Identificar usuarios (evaluadores y tesista) - DESHABILITADO
        # print("🔍 Identificando participantes de izquierda a derecha...")
        # current_users, _ = identify_users_with_elevenlabs(engine, current_slide_num, exit_flag)
        
        # Cargar caras conocidas - DESHABILITADO
        # known_faces = load_known_faces()
        
        # Iniciar proceso de cámara - DESHABILITADO (no detecta caras ni estudiantes)
        # camera_proc = Process(
        #     target=camera_process,
        #     args=(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, current_users)
        # )
        # camera_proc.daemon = True
        # camera_proc.start()
        
        # Valores por defecto vacíos (no se detectan usuarios ni caras)
        current_users = []
        known_faces = []
        camera_proc = None
        
        # print("⏳ Esperando a que la cámara se inicialice...")
        # time.sleep(3)
        
        # FASE 1: Bienvenida y Presentación del Evento
        print("\n" + "="*50)
        print("🎓 FASE 1: BIENVENIDA A LA DEFENSA DE TESIS")
        print("="*50)
        
        speak_elevenlabs_with_animation(engine, "Buenos días a todos los presentes.")
        speak_elevenlabs_with_animation(engine, "Bienvenidos a esta importante ceremonia académica: la Defensa de Tesis.")
        speak_elevenlabs_with_animation(engine, "Mi nombre es ADAI y seré su asistente durante esta presentación.")
        
        # FASE 2: Introducción al Protocolo
        print("\n" + "="*50)
        print("📋 FASE 2: PROTOCOLO DE LA DEFENSA")
        print("="*50)
        
        speak_elevenlabs_with_animation(engine, "A continuación, les explicaré la presentación de la tesis.")
        # FASE 3: Presentación Principal
        print("\n" + "="*50)
        print("📚 FASE 3: PRESENTACIÓN DE LA TESIS")
        print("="*50)
        
        if class_pdf and os.path.exists(class_pdf):
            speak_elevenlabs_with_animation(engine, "Ahora comenzaremos con la presentación de la tesis.")
            
            # Extraer texto del PDF de presentación
            pdf_text = extract_text_from_pdf(class_pdf)
            
            # Buscar y leer el documento completo de la tesis (si existe)
            full_thesis_text = None
            pdf_dir = os.path.dirname(class_pdf) if os.path.dirname(class_pdf) else os.getcwd()
            pdf_basename = os.path.basename(class_pdf)
            pdf_name_without_ext = os.path.splitext(pdf_basename)[0]
            
            # Buscar archivos PDF en la misma carpeta que podrían ser el documento completo
            # Nombres comunes: tesis_completa.pdf, informe_completo.pdf, documento_completo.pdf, etc.
            possible_names = [
                "tesis_completa.pdf",
                "informe_completo.pdf", 
                "documento_completo.pdf",
                f"{pdf_name_without_ext}_completo.pdf",
                "completo.pdf",
                "tesis.pdf"
            ]
            
            # También buscar en la carpeta pdfs si existe
            class_dir = os.path.dirname(os.path.abspath(__file__))
            pdfs_folder = os.path.join(class_dir, "pdfs")
            search_paths = [pdf_dir]
            if os.path.exists(pdfs_folder):
                search_paths.append(pdfs_folder)
            
            for search_path in search_paths:
                for possible_name in possible_names:
                    possible_path = os.path.join(search_path, possible_name)
                    if os.path.exists(possible_path) and os.path.abspath(possible_path) != os.path.abspath(class_pdf):
                        print(f"📄 Encontrado documento completo: {possible_path}")
                        try:
                            full_thesis_text = extract_text_from_pdf(possible_path)
                            if full_thesis_text:
                                print(f"✅ Documento completo leído exitosamente ({len(full_thesis_text)} caracteres)")
                                break
                        except Exception as e:
                            print(f"⚠️ Error leyendo documento completo: {e}")
                            full_thesis_text = None
                if full_thesis_text:
                    break
            
            if not full_thesis_text:
                print("ℹ️ No se encontró documento completo de la tesis. Se usará solo el texto de la presentación.")
            
            if pdf_text:
                # Definir mapeo de secuencias ESP32 por número de diapositiva
                sequence_mapping = {
                    1: "ClaseMove",        # Introducción
                 # Planteamiento del problema
                2: "ClaseMove",        # Objetivos
                        # Marco teórico
                    3: "ClaseMove",        # Metodología
                          # Resultados
                    5: "ClaseMove",        # Análisis
                      # Conclusiones
                    8: "ClaseMove",        # Recomendaciones
                       # Referencias
                    13: "ClaseMove",
                    21: "ClaseMove",
                }
                
                # Definir mapeo de contexto extra por número de diapositiva
                # Útil para diapositivas que solo contienen imágenes o necesitan contexto adicional
                # Ejemplo: {3: "Esta diapositiva muestra un diagrama de flujo del proceso...", 7: "..."}
                extra_context_mapping = {
                    # Ejemplo (descomentar y modificar según tus necesidades):
                    # 3: "Esta diapositiva muestra un diagrama del sistema propuesto. El diagrama ilustra el flujo de datos entre los componentes principales.",
                    # 7: "Esta diapositiva presenta una gráfica de resultados. La gráfica muestra la comparación entre el método propuesto y los métodos existentes.",
               13: "Con el material preparado y los temas seleccionados, el robot fue incorporado al salón de clase para impartir las lecciones. ADAI tomó el papel principal como mediador del contenido, explicando los temas mientras la docente intervenía únicamente cuando era necesario solicitar ejemplos adicionales o aclarar instrucciones específicas. Para facilitar esta dinámica, se integró en la aplicación móvil un nuevo módulo que permitió a la maestra controlar el desarrollo de la sesión mediante Lynx. Este módulo incorporó funciones para iniciar, pausar y detener por completo una clase previamente configurada en el servidor, manteniendo siempre al robot como protagonista de la actividad. Además del control básico, se añadió un apartado que permitió a la docente interactuar directamente con el robot durante la clase. Desde esta sección, la maestra podía formular preguntas relacionadas con el contenido, solicitar ampliaciones sobre un concepto o indicar que ADAI generara preguntas dirigidas a los alumnos. Esta funcionalidad buscó mantener la fluidez pedagógica sin interrumpir la narrativa del robot, asegurando que la sesión permaneciera estructurada y coherente con los objetivos de aprendizaje establecidos. Para posibilitar esta interacción más dinámica, se realizaron ajustes en el servidor que gestionaba las clases y las secuencias del robot. Dichos cambios permitieron combinar movimientos del humanoide como gestos, señales o desplazamientos de cabeza con la explicación del contenido y la ejecución de preguntas programadas. También se habilitó la capacidad de alternar entre momentos en los que el robot consultaba a los estudiantes y otros en los que atendía preguntas formuladas por ellos. Esta implementación hizo posible observar de primera mano la reacción de los alumnos ante una clase guiada casi por completo por un recurso tecnológico, manteniendo un ambiente natural y evitando que la experiencia se percibiera forzada o fuera de contexto. "
                 ,14: "Al finalizar cada sesión, los estudiantes realizaron una prueba corta elaborada exclusivamente con base en el contenido explicado por el robot durante esa lección. Estas pruebas fueron diseñadas para ser rápidas y precisas, permitiendo evaluar lo que cada estudiante logró asimilar de forma inmediata. Aplicarlas al terminar la clase garantizó que los resultados reflejaran la comprensión real del momento, sin intervenciones externas ni repasos posteriores. Este tipo de evaluación resultó útil para observar cómo respondían los alumnos al estilo particular de enseñanza del robot. "
                 , 17: "En quinto grado se evaluaron tres áreas: • Los medios de comunicación • Valores cívicos y convivencia • Los símbolos patrios Comportamiento general del grupo El grupo de quinto grado mostró un desempeño alto y bastante uniforme. En la figura 11 se observa que la mayoría de los estudiantes obtuvo calificaciones entre 9 y 10, lo que indica una comprensión sólida de los temas explicados por el robot. Las puntuaciones presentan muy poca variación entre asignaturas, lo cual sugiere que el estilo de enseñanza de ADAI: visual, estructurado y dinámico, funcionó de manera consistente independientemente del contenido curricular. Variaciones dentro del grupo En algunos alumnos se observan valores ligeramente más bajos (entre 7 y 8), especialmente cuando el contenido requería más retención factual, como en Los símbolos patrios. Sin embargo, estas variaciones son mínimas y no afectan la tendencia global del grupo, que permanece alta. También se registran casos con espacios en blanco debido a inasistencia, y estos no representan fallas de rendimiento sino falta de datos disponibles. Interpretación pedagógica El comportamiento del grupo demuestra que la metodología aplicada por ADAI permitió que la mayoría de los estudiantes lograra: • mantener la atención durante la explicación, • comprender la información presentada en pantalla, • responder correctamente las evaluaciones de forma inmediata. • En quinto grado, la respuesta académica sugiere que los alumnos encontraron en ADAI un recurso claro, accesible y motivador para el aprendizaje.En sexto grado se evaluaron cinco áreas: • Textos y recursos publicitarios • Lectura silenciosa vs. lectura en voz alta • Los medios de comunicación • Valores cívicos y convivencia • Los símbolos patrios Comportamiento general del grupo El rendimiento en sexto grado también fue altamente satisfactorio, con una concentración de notas entre 9 y 10 en la mayoría de los estudiantes. La gráfica refleja un patrón muy estable: sin importar el tema, los estudiantes lograron adaptarse bien a las explicaciones del robot. Los contenidos relacionados con lenguaje, especialmente Lectura silenciosa vs. lectura en voz alta muestran una participación más variada, lo cual es normal debido a que implican habilidades lectoras individuales. Aun así, el promedio general permanece alto. Variaciones dentro del grupo Al igual que en quinto grado, se observan algunos valores ligeramente inferiores (7 u 8) en temas más interpretativos, como Textos y recursos publicitarios. Estos temas requieren mayor análisis, pero aun así los estudiantes demostraron capacidad para comprenderlos con el apoyo del androide. También hay vacíos correspondientes a estudiantes ausentes en una o más sesiones, los cuales no representan fallas de rendimiento. Interpretación pedagógica Los resultados de sexto grado demuestran que ADAI logró captar el interés de los alumnos y mantener un nivel de comprensión adecuado incluso en temas que exigen mayor análisis. El uso de recursos audiovisuales, la claridad del discurso y el ritmo de la clase influyeron directamente en el buen rendimiento del grupo.",
                 18: "Los promedios obtenidos fueron: P1: 4.72, P2: 4.35, P3: 4.67, P4: 4.49, P5: 4.28, P6: 4.26, P7: 4.51, P8: 4.72, P9: 4.26, P10: 4.63 y P11: 4.58. En otras palabras, todas las preguntas se ubicaron claramente por encima de 4, lo que indica que, en general, los estudiantes estuvieron de acuerdo o totalmente de acuerdo con los enunciados planteados. Las puntuaciones más altas se dieron en la Pregunta 1 (4.72) y la Pregunta 8 (4.72), lo que refleja que la clase les pareció interesante desde el inicio y que, en términos generales, la disfrutaron mucho. También destacan la Pregunta 3 (4.67) y la Pregunta 10 (4.63), ligadas a la claridad y a la percepción de que la clase fue útil para aprender. Esto confirma que la propuesta no solo llamó la atención, sino que se sintió como una experiencia provechosa. Las preguntas con promedios ligeramente menores, como la Pregunta 6 (4.26) y la Pregunta 9 (4.26), sugieren que en algunos momentos hubo pequeñas variaciones en la atención o en cómo cada estudiante vivió la clase, algo normal en grupos numerosos. Aun así, los valores siguen siendo altos y refuerzan la idea de que la mayoría se sintió cómodo, interesado y satisfecho con la forma en que se desarrollaron las sesiones. En conjunto, estos resultados permiten afirmar que el agrado por las clases fue muy positivo. Los estudiantes no solo aceptaron la presencia del androide en el aula, sino que valoraron la experiencia como clara, entretenida y diferente a lo que viven en una clase tradicional, abriendo la puerta a seguir usando este tipo de recursos en el futuro. Los promedios obtenidos, en el orden de las preguntas fueron: 4.74, 4.70, 4.53, 4.47, 4.65, 4.51, 4.65, 4.63, 4.53, 4.70, 4.74, 4.81, 4.65 y 4.72. Desde el inicio, los estudiantes mostraron una percepción muy positiva del robot. La valoración más alta fue la de la Pregunta 12 (4.81), lo que indica que ADAI logró transmitir una sensación especialmente fuerte de cercanía, simpatía o claridad, según el contenido de esa pregunta. Este resultado deja ver que la forma de comunicarse del robot, su tono, sus expresiones y la fluidez de sus explicaciones tuvieron un impacto real en la manera en que los alumnos lo recibieron. También destacan promedios elevados como los de las Preguntas 1 (4.74), 11 (4.74), 2 (4.70) y 10 (4.70). Esto refuerza la idea de que ADAI fue percibido como un recurso confiable, fácil de entender y motivador. Los estudiantes sintieron que el robot “sabía lo que explicaba” y que acompañaba bien el proceso de aprendizaje, algo clave para que una herramienta tecnológica sea aceptada dentro del aula. Los valores ligeramente menores —aunque igualmente altos—, como los de las Preguntas 4 (4.47) y 6 (4.51), muestran pequeños matices en la experiencia. Estas variaciones pueden relacionarse con la adaptación natural de los estudiantes al método, ya que muchos jamás habían tenido contacto con un robot docente, lo que genera expectativas, curiosidad y, en algunos casos, una ligera cautela inicial. A pesar de estos matices, todos los resultados se mantienen por encima de 4.4, lo cual confirma un consenso muy claro: los estudiantes no solo aceptaron al robot como parte de la clase, sino que lo valoraron como un actor educativo legítimo, agradable y útil. En síntesis, la percepción del androide ADAI fue ampliamente positiva. Los estudiantes lo vieron como un guía claro, dinámico y capaz de mantener su atención. Este nivel de aceptación demuestra que la robótica educativa, cuando se integra de manera adecuada, puede generar un ambiente de confianza, curiosidad y apertura hacia nuevas formas de aprender. ",
                 19: "En esta parte del estudio se buscó comprender con más detalle la experiencia emocional de los estudiantes durante las clases impartidas por el androide ADAI. No solo interesaba saber si la sesión había sido agradable, sino también identificar qué tipo de emociones surgían en ellos: tranquilidad, alegría, curiosidad, entusiasmo o incluso nervios al interactuar con una tecnología nueva. Todas estas sensaciones influyen directamente en cómo los alumnos aprenden, prestan atención y participan. Para ello se aplicaron ocho preguntas con una escala del 1 al 5. Los promedios obtenidos, en el orden correspondiente, fueron: 4.56, 4.33, 4.49, 4.23, 4.35, 4.72, 4.74 y 4.65. Desde el inicio se observó una tendencia clara hacia respuestas positivas. Las puntuaciones más altas aparecieron en la pregunta 7 (4.74) y la pregunta 6 (4.72), asociadas a emociones como entusiasmo, comodidad y sensaciones de bienestar durante la clase. Esto sugiere que ADAI logró generar un ambiente emocionalmente seguro y atractivo, donde los alumnos se sintieron acompañados y dispuestos a participar sin temor ni incomodidad. Asimismo, otras preguntas con promedios elevados, como la pregunta 8 (4.65) y la pregunta 1 (4.56), mostraron que el robot no solo despertó interés, sino también emociones que favorecen la concentración y la participación. Varios estudiantes manifestaron sentirse más atentos, más tranquilos o más conectados con la actividad cuando el robot explicaba, lo cual suele traducirse en mayor disposición para seguir instrucciones, mirar los materiales visuales y mantenerse involucrados en la dinámica de clase. Las puntuaciones ligeramente más bajas, aunque igualmente positivas, aparecieron en la pregunta 4 (4.23) y la pregunta 5 (4.35). Estas áreas podrían indicar que ciertas emociones, como la total confianza en la nueva herramienta o la ausencia de nervios, requieren un poco más de tiempo para desarrollarse. Es normal que al introducir una tecnología tan distinta a lo habitual, algunos estudiantes necesiten un proceso de adaptación. No todos reaccionan igual ante algo novedoso, y las primeras experiencias emocionales pueden variar según la personalidad, la expectativa o el nivel de familiaridad con la robótica. A pesar de ello, incluso estos promedios más bajos se mantienen por encima del punto medio, lo que indica que ninguna emoción negativa predominó en el grupo. No hubo señales de rechazo, incomodidad significativa o resistencia hacia el robot. Más bien, los datos revelan un clima emocional general positivo, donde los alumnos experimentaron sensaciones que facilitan la interacción y el aprendizaje. En conjunto, los resultados permiten concluir que ADAI no solo captó la atención de los estudiantes, sino que también generó emociones positivas que favorecieron el ambiente educativo. El robot contribuyó a crear un espacio más dinámico, participativo y emocionalmente estable, donde los niños pudieron aprender con mayor comodidad, confianza y motivación. Esta respuesta afectiva sugiere que la incorporación de ADAI en el aula no solo es funcional desde el punto de vista académico, sino también beneficiosa en términos de bienestar socioemocional."
                }
                
                print("🎬 Usando explicación personalizada para defensa de tesis con memoria conversacional")
                
                # Explicar diapositivas con memoria conversacional y contexto de defensa de tesis
                explain_thesis_slides_with_memory(
                        engine, class_pdf, pdf_text, current_users,
                        hand_raised_counter, current_slide_num, exit_flag, 
                    known_faces, current_hand_raiser, sequence_mapping,
                    full_thesis_context=full_thesis_text,
                    extra_context_mapping=extra_context_mapping if extra_context_mapping else None
                    )
            else:
                print("❌ No se pudo leer el PDF")
        else:
            print(f"⚠️ No se encontró PDF: {class_pdf}")
            speak_elevenlabs_with_animation(engine, "Continuaremos sin la presentación en PDF.")
        
        # FASE 4: Sesión de Preguntas
        print("\n" + "="*60)
        print("❓ FASE 4: SESIÓN DE PREGUNTAS DEL JURADO")
        print("="*60)
        
        speak_elevenlabs_with_animation(engine, "Excelente hemos finalizado la presentación.")
        speak_elevenlabs_with_animation(engine, "Gracias por su participación en esta defensa de tesis.")
        
        speak_elevenlabs_with_animation(engine, "Ahora es el momento de la sesión de preguntas.")
        # speak_elevenlabs_with_animation(engine, "Los miembros del jurado pueden realizar sus preguntas al tesista.")
        # speak_elevenlabs_with_animation(engine, "Tesista, por favor responda con claridad y fundamentación.")
        
        # FASE 5: Cierre y Deliberación
        print("\n" + "="*60)
        print("🎓 FASE 5: CIERRE DE LA DEFENSA")
        print("="*60)
        
        # speak_elevenlabs_with_animation(engine, "El jurado procederá a deliberar.")
        # speak_elevenlabs_with_animation(engine, "Felicitaciones al tesista por su esfuerzo y dedicación.")
        # speak_elevenlabs_with_animation(engine, "¡Les deseo mucho éxito en sus futuros proyectos académicos y profesionales!")
        
        # Limpiar recursos
        print("🛑 Finalizando defensa de tesis")
        exit_flag.value = 1
        
        # Proceso de cámara deshabilitado (no hay detección de caras/estudiantes)
        # if camera_proc and camera_proc.is_alive():
        #     print("⏳ Esperando proceso de cámara...")
        #     camera_proc.join(timeout=3)
        #     
        #     if camera_proc.is_alive():
        #         camera_proc.terminate()
        #         camera_proc.join(timeout=1)
        
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
