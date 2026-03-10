"""
Módulo de funciones de voz y reconocimiento para ADAI
===================================================

Contiene todas las funciones relacionadas con:
- Text-to-Speech (TTS)
- Speech Recognition
- Animación facial durante el habla
"""

import pyttsx3
import speech_recognition as sr
import cv2
import numpy as np
import random
import time
from .config import TTS_VOICE, SPEECH_CONFIG

def initialize_tts():
    """
    Inicializa el motor de Text-to-Speech
    
    Returns:
        pyttsx3.Engine: Motor TTS inicializado o None si hay error
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('voice', TTS_VOICE)
        return engine
    except Exception as e:
        print(f"❌ Error al inicializar TTS: {e}")
        return None

def listen(timeout=5, phrase_time_limit=None):
    """
    Función mejorada de escucha con mejor manejo de errores.
    Intenta reconocer el habla y maneja graciosamente los errores de conexión.
    
    Args:
        timeout (int): Tiempo máximo de espera para comenzar a escuchar
        phrase_time_limit (int): Tiempo máximo para una frase
        
    Returns:
        str: Texto reconocido o código de error
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("🎤 Escuchando...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            recognizer.energy_threshold = SPEECH_CONFIG['energy_threshold']
            recognizer.pause_threshold = SPEECH_CONFIG['pause_threshold']
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                print("⚠️ Tiempo de espera agotado")
                return "timeout"
            except Exception as e:
                print(f"⚠️ Error al capturar audio: {e}")
                return "error_capture"
        
        try:
            text = recognizer.recognize_google(audio, language=SPEECH_CONFIG['language'])
            print(f"🎤 Usuario dijo: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("⚠️ No se pudo reconocer lo que dijiste")
            return ""
        except sr.RequestError as e:
            print(f"⚠️ Error de servicio Google: {e}")
            return "error_google"
        except Exception as e:
            print(f"⚠️ Error inesperado en reconocimiento: {e}")
            return "error_unknown"
    except Exception as e:
        print(f"⚠️ Error general en la función listen: {e}")
        return "error_general"

def draw_stylish_eye(img, center_x, center_y):
    """
    Dibuja un ojo estilo caricatura:
      - Círculo blanco con borde negro (esclerótica)
      - Anillo azul (iris)
      - Pupila negra grande
      - Brillo blanco
    
    Args:
        img: Imagen donde dibujar
        center_x (int): Coordenada X del centro del ojo
        center_y (int): Coordenada Y del centro del ojo
    """
    sclera_radius = 60
    # Borde negro
    cv2.circle(img, (center_x, center_y), sclera_radius, (0, 0, 0), 2)
    # Relleno blanco un poco más pequeño
    cv2.circle(img, (center_x, center_y), sclera_radius - 2, (255, 255, 255), -1)

    # Iris azul
    iris_radius = 40
    iris_color = (255, 150, 50)  # BGR (azul claro)
    cv2.circle(img, (center_x, center_y), iris_radius, iris_color, -1)

    # Pupila negra grande
    pupil_radius = 30
    cv2.circle(img, (center_x, center_y), pupil_radius, (0, 0, 0), -1)

    # Brillo blanco
    cv2.circle(img, (center_x - 10, center_y - 10), 8, (255, 255, 255), -1)

def draw_fun_face(width=600, height=400, mouth_state=0):
    """
    Dibuja un rostro con 2 ojos 'azules' y boca con 3 estados:
      0 = cerrada
      1 = semiabierta
      2 = muy abierta (sin dientes)
    
    Args:
        width (int): Ancho de la imagen
        height (int): Alto de la imagen
        mouth_state (int): Estado de la boca (0, 1, 2)
        
    Returns:
        numpy.ndarray: Imagen del rostro
    """
    face = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Posiciones de los ojos
    eye_y = height // 3
    eye_x_left  = width // 3
    eye_x_right = 2 * width // 3

    # Dibujar ojos
    draw_stylish_eye(face, eye_x_left, eye_y)
    draw_stylish_eye(face, eye_x_right, eye_y)

    # Boca
    mouth_center = (width // 2, int(height * 0.7))
    arc_width, arc_height = 140, 40

    if mouth_state == 0:
        # Boca cerrada (arco fino)
        cv2.ellipse(face, mouth_center, (arc_width, arc_height),
                    0, 0, 180, (0, 0, 0), 3)
    elif mouth_state == 1:
        # Boca semiabierta (arco más grande)
        cv2.ellipse(face, mouth_center, (arc_width, arc_height + 10),
                    0, 0, 180, (0, 0, 0), 4)
    else:
        # Boca muy abierta (rellena)
        cv2.ellipse(face, mouth_center, (arc_width, arc_height + 20),
                    0, 0, 180, (0, 0, 0), -1)

    return face

def speak_with_animation(engine, text):
    """
    Habla 'text' usando pyttsx3 (modo manual) mientras dibuja
    un 'rostro animado' en la ventana "ADAI Robot Face".
    Alterna la boca entre 1 (semiabierta) y 2 (muy abierta).
    Al terminar, dibuja la boca cerrada (0).
    
    Args:
        engine: Motor de TTS
        text (str): Texto a pronunciar
    """
    print(f"🗣️ Asistente: {text}")
    engine.startLoop(False)
    engine.say(text)

    while engine.isBusy():
        engine.iterate()
        mouth_state = random.choice([1, 2])
        face_img = draw_fun_face(600, 400, mouth_state)
        cv2.imshow("ADAI Robot Face", face_img)
        if cv2.waitKey(50) & 0xFF == 27:  # ESC
            break

    engine.endLoop()

    # Boca cerrada
    final_face = draw_fun_face(600, 400, 0)
    cv2.imshow("ADAI Robot Face", final_face)
    cv2.waitKey(300)
