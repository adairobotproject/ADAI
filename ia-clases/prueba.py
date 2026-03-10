import cv2
import face_recognition
import numpy as np
import pyttsx3
import speech_recognition as sr
import os
import fitz  # PyMuPDF
import openai
import time
import multiprocessing
from multiprocessing import Process, Value, Event
import mediapipe as mp
import pytesseract
import threading
import winsound

# Set path to Tesseract executable for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ======================
#  CONFIGURACIÓN OPENAI
# ======================
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Get absolute path for the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
faces_dir = os.path.join(script_dir, "tribunal_faces")
if not os.path.exists(faces_dir):
    os.makedirs(faces_dir)

# ============================
#   FUNCIONES DE TTS SIN CARA
# ============================
def speak_technical(engine, text):
    """
    Función de habla técnica sin animación facial
    """
    print(f"🎓 ADAI: {text}")
    engine.say(text)
    engine.runAndWait()

# ============================
#    MOSTRAR PDF EN OPENCV
# ============================
def show_pdf_page_in_opencv(page):
    """
    Convierte la página PyMuPDF en una imagen BGR de OpenCV,
    manejando RGBA, RGB o escala de grises.
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

# ============================
#    PROCESO DE LA CÁMARA PARA TRIBUNAL
# ============================
def camera_process_tribunal(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, tribunal_members):
    """
    Proceso de cámara adaptado para tribunal de tesis
    """
    try:
        print("🎥 [CAMERA] Iniciando monitoreo del tribunal...")
        print(f"🎥 [CAMERA] Miembros del tribunal: {tribunal_members}")
        
        # Configuración MediaPipe
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=6,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.2
        )
        mp_draw = mp.solutions.drawing_utils
        
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.05
        )
        
        print("🎥 [CAMERA] MediaPipe configurado para tribunal")
        
        # Configuración de cámara
        cap = None
        camera_configs = [
            (0, cv2.CAP_DSHOW, "DirectShow"),
            (0, None, "Default"),
            (1, cv2.CAP_DSHOW, "DirectShow Index 1"),
        ]
        
        for index, backend, name in camera_configs:
            try:
                if backend is None:
                    cap = cv2.VideoCapture(index)
                else:
                    cap = cv2.VideoCapture(index, backend)
                
                if cap.isOpened():
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        print(f"🎥 [CAMERA] ✅ {name} funcionando para monitoreo del tribunal")
                        break
                    else:
                        cap.release()
                        cap = None
            except Exception as e:
                print(f"🎥 [CAMERA] ❌ Error con {name}: {e}")
                if cap:
                    cap.release()
                cap = None
        
        if cap is None:
            print("🎥 [CAMERA] ❌ ERROR: No se pudo inicializar cámara para tribunal")
            exit_flag.value = 1
            return
        
        # Configuración básica de cámara
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Crear ventana para monitoreo del tribunal
        cv2.namedWindow("Monitoreo del Tribunal", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Monitoreo del Tribunal", 1000, 700)
        
        # Variables de seguimiento para tribunal
        hand_raisers = {}
        max_consecutive = 6
        max_tribunal_members = len(tribunal_members)
        
        user_tracking = {}
        for i in range(max_tribunal_members):
            user_tracking[i] = {
                'positions': [],
                'last_seen': 0,
                'stable_count': 0,
                'lost_count': 0
            }
        
        # Colores para miembros del tribunal
        tribunal_colors = [
            (0, 128, 255),    # Naranja
            (255, 0, 128),    # Rosa  
            (128, 255, 0),    # Verde lima
            (255, 128, 0),    # Azul claro
            (128, 0, 255),    # Púrpura
            (0, 255, 128),    # Verde agua
        ]
        
        def calculate_distance(pos1, pos2):
            return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
        
        frame_count = 0
        
        print("🎥 [CAMERA] 🚀 Iniciando monitoreo del tribunal...")
        
        while exit_flag.value == 0:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            h, w = frame.shape[:2]
            frame_count += 1
            
            # Preprocesamiento
            enhanced_frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
            rgb_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB)
            
            # Detección facial para tribunal
            current_detections = []
            try:
                face_results = face_detection.process(rgb_frame)
                
                if face_results.detections:
                    for i, detection in enumerate(face_results.detections):
                        bbox = detection.location_data.relative_bounding_box
                        x1 = int(bbox.xmin * w)
                        y1 = int(bbox.ymin * h)
                        width = int(bbox.width * w)
                        height = int(bbox.height * h)
                        
                        face_area = width * height
                        min_face_area = (w * h) * 0.0001
                        max_face_area = (w * h) * 0.4
                        
                        if (min_face_area <= face_area <= max_face_area and 
                            width > 30 and height > 30 and
                            width < w * 0.8 and height < h * 0.8 and
                            x1 >= 0 and y1 >= 0 and 
                            x1 + width <= w and y1 + height <= h):
                            
                            face_center_x = x1 + width // 2
                            face_center_y = y1 + height // 2
                            confidence = detection.score[0] if detection.score else 0.5
                            
                            current_detections.append({
                                'bbox': (x1, y1, width, height),
                                'center': (face_center_x, face_center_y),
                                'area': face_area,
                                'confidence': confidence
                            })
            except Exception as e:
                print(f"🎥 [CAMERA] ❌ Error en detección facial: {e}")
            
            # Asignar detecciones a miembros del tribunal (izquierda a derecha)
            assignments = {}
            if current_detections:
                detections_with_x = []
                for idx, detection in enumerate(current_detections):
                    x1, y1, width, height = detection['bbox']
                    x_center = x1 + width // 2
                    detections_with_x.append((idx, x_center))
                
                detections_with_x.sort(key=lambda item: item[1])
                for position, (original_idx, x_center) in enumerate(detections_with_x):
                    if position < max_tribunal_members:
                        assignments[original_idx] = position
                
                for det_idx, member_id in assignments.items():
                    detection = current_detections[det_idx]
                    center = detection['center']
                    
                    # Actualizar tracking
                    user_tracking[member_id]['positions'].append(center)
                    if len(user_tracking[member_id]['positions']) > 10:
                        user_tracking[member_id]['positions'].pop(0)
                    
                    user_tracking[member_id]['last_seen'] = frame_count
                    user_tracking[member_id]['stable_count'] += 1
                    
                    # Dibujar miembro del tribunal
                    x1, y1, width, height = detection['bbox']
                    color = tribunal_colors[member_id % len(tribunal_colors)]
                    
                    thickness = max(2, int(width / 40))
                    cv2.rectangle(frame, (x1, y1), (x1 + width, y1 + height), color, thickness)
                    
                    # Nombre del miembro del tribunal
                    font_scale = max(0.6, width / 120)
                    member_name = tribunal_members[member_id] if member_id < len(tribunal_members) else f"Evaluador {member_id+1}"
                    cv2.putText(frame, member_name, (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
            
            # Detección de manos levantadas en el tribunal
            raised_hands_in_frame = {}
            try:
                results = hands.process(rgb_frame)
                
                if results.multi_hand_landmarks and current_detections and assignments:
                    for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                        
                        if middle_tip.y < wrist.y - 0.03:
                            wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                            
                            hand_is_above_face = False
                            closest_member_id = None
                            min_distance = float('inf')
                            
                            for det_idx, member_id in assignments.items():
                                detection = current_detections[det_idx]
                                face_x1, face_y1, face_width, face_height = detection['bbox']
                                face_center_x = face_x1 + face_width // 2
                                face_center_y = face_y1 + face_height // 2
                                
                                horizontal_distance = abs(wrist_x - face_center_x)
                                max_horizontal_distance = face_width * 1.5
                                
                                vertical_clearance = face_y1 - wrist_y
                                min_vertical_clearance = 20
                                max_vertical_clearance = face_height * 3
                                
                                if (horizontal_distance <= max_horizontal_distance and 
                                    min_vertical_clearance <= vertical_clearance <= max_vertical_clearance):
                                    
                                    hand_is_above_face = True
                                    total_distance = ((face_center_x - wrist_x) ** 2 + (face_center_y - wrist_y) ** 2) ** 0.5
                                    
                                    if total_distance < min_distance:
                                        min_distance = total_distance
                                        closest_member_id = member_id
                            
                            if hand_is_above_face and closest_member_id is not None:
                                raised_hands_in_frame[closest_member_id] = True
                                member_color = tribunal_colors[closest_member_id % len(tribunal_colors)]
                                
                                mp_draw.draw_landmarks(
                                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                    mp_draw.DrawingSpec(color=(255, 255, 255), thickness=3, circle_radius=3),
                                    mp_draw.DrawingSpec(color=(0, 0, 255), thickness=3)
                                )
                                
                                cv2.circle(frame, (wrist_x, wrist_y), 15, member_color, -1)
                                
                                if closest_member_id in hand_raisers:
                                    hand_raisers[closest_member_id] += 1
                                else:
                                    hand_raisers[closest_member_id] = 1
                                
                                member_name = tribunal_members[closest_member_id] if closest_member_id < len(tribunal_members) else f"Evaluador {closest_member_id+1}"
                                cv2.putText(frame, f"Pregunta {member_name}: {hand_raisers[closest_member_id]}/{max_consecutive}",
                                            (10, 120 + closest_member_id * 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                            member_color, 2)
                                
                                if hand_raisers[closest_member_id] >= max_consecutive:
                                    hand_raised_counter.value += 1
                                    current_hand_raiser.value = closest_member_id
                                    hand_raisers[closest_member_id] = 0
                                    print(f"🎥 [CAMERA] ✋ Pregunta del tribunal por {member_name}! Contador: {hand_raised_counter.value}")

            except Exception as e:
                print(f"🎥 [CAMERA] ❌ Error en detección de manos: {e}")
            
            # Resetear contadores
            for member_id in list(hand_raisers.keys()):
                if member_id not in raised_hands_in_frame:
                    hand_raisers[member_id] = max(0, hand_raisers[member_id] - 1)
            
            # Información en pantalla del tribunal
            cv2.putText(frame, f"Preguntas detectadas: {hand_raised_counter.value}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
            cv2.putText(frame, f"Diapositiva {current_slide_num.value}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
            
            # Info del tribunal
            members_tracked = len([u for u in user_tracking.values() if u['last_seen'] > frame_count - 30])
            faces_detected = len(current_detections)
            
            cv2.putText(frame, f"Tribunal: {members_tracked}/{max_tribunal_members}", (w - 300, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Evaluadores presentes: {faces_detected}", (w - 300, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Estado de miembros del tribunal
            for member_id in range(min(max_tribunal_members, 4)):
                status = "PRESENTE" if user_tracking[member_id]['last_seen'] > frame_count - 10 else "AUSENTE"
                color = (0, 255, 0) if status == "PRESENTE" else (0, 0, 255)
                member_name = tribunal_members[member_id] if member_id < len(tribunal_members) else f"Eval{member_id+1}"
                cv2.putText(frame, f"{member_name}: {status}", (10, h - 80 + member_id * 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            cv2.imshow("Monitoreo del Tribunal", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                exit_flag.value = 1
                break
                
    except Exception as e:
        print(f"🎥 [CAMERA] ❌ ERROR CRÍTICO: {e}")
        exit_flag.value = 1
    finally:
        try:
            if 'cap' in locals() and cap and cap.isOpened():
                cap.release()
            if 'hands' in locals():
                hands.close()
            if 'face_detection' in locals():
                face_detection.close()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"🎥 [CAMERA] ⚠️ Error al limpiar: {e}")

# ===============
#   INITIALIZE TTS
# ===============
def initialize_tts():
    try:
        engine = pyttsx3.init()
        engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0')
        engine.setProperty('rate', 180)  # Velocidad más técnica
        return engine
    except Exception as e:
        print(f"❌ Error al inicializar TTS: {e}")
        return None

# =================
#   LISTEN
# =================
def listen_technical(timeout=8, phrase_time_limit=None):
    """
    Función de escucha adaptada para defensa de tesis
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("🎤 Escuchando al tribunal...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            recognizer.energy_threshold = 400
            recognizer.pause_threshold = 1.0  # Más tiempo para preguntas técnicas
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                print("⚠️ Tiempo de espera agotado")
                return "timeout"
            except Exception as e:
                print(f"⚠️ Error al capturar audio: {e}")
                return "error_capture"
        
        try:
            text = recognizer.recognize_google(audio, language="es-ES")
            print(f"🎤 Tribunal: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("⚠️ No se pudo reconocer la pregunta")
            return ""
        except sr.RequestError as e:
            print(f"⚠️ Error de servicio Google: {e}")
            return "error_google"
    except Exception as e:
        print(f"⚠️ Error general en reconocimiento: {e}")
        return "error_general"

# =====================
#   UTILIDADES
# =====================
def load_tribunal_faces():
    """Cargar caras conocidas del tribunal"""
    known_faces = {}
    for file in os.listdir(faces_dir):
        if file.endswith(".jpg"):
            path = os.path.join(faces_dir, file)
            image = face_recognition.load_image_file(path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_faces[file.split(".")[0]] = encoding[0]
    return known_faces

def capture_frame():
    """Capturar frame de la cámara"""
    configs = [
        (0, None),
        (0, cv2.CAP_DSHOW),
        (1, None),
    ]
    
    for index, backend in configs:
        try:
            if backend is None:
                cap = cv2.VideoCapture(index)
            else:
                cap = cv2.VideoCapture(index, backend)
                
            if not cap.isOpened():
                continue
            
            resolutions = [(1280, 720), (640, 480)]
            for width, height in resolutions:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                if actual_width >= width * 0.9 and actual_height >= height * 0.9:
                    break
            
            for _ in range(8):
                cap.read()
                time.sleep(0.1)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                return frame
                
        except Exception as e:
            print(f"❌ Error con configuración índice {index}: {e}")
            if 'cap' in locals() and cap.isOpened():
                cap.release()
    
    return None

def extract_text_from_pdf(pdf_path):
    """Extraer texto del PDF de la tesis"""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"❌ Error al leer PDF de tesis: {e}")
        return None

def ask_thesis_question(question, context, evaluator_name=None):
    """
    Respuesta técnica a preguntas del tribunal
    """
    try:
        system_prompt = """Eres ADAI, un sistema de defensa automatizada de tesis de ingeniería. 
        Respondes preguntas técnicas del tribunal evaluador basándote únicamente en el contenido 
        de la tesis proporcionada. Tus respuestas deben ser:

- Técnicas y precisas
- Formales y académicas  
- Basadas exclusivamente en el contenido del PDF
- Máximo 4 oraciones para mantener claridad
- Sin formato especial (asteriscos, viñetas, etc.)
- Si la pregunta no está relacionada con la tesis, indica que solo puedes responder sobre el proyecto presentado"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexto de la tesis: {context}\n\nPregunta del tribunal: {question}"}
            ]
        )
        
        answer = response.choices[0].message.content
        answer = answer.replace("*", "").replace("**", "").replace("***", "")
        answer = answer.replace("- ", "").replace("• ", "")
        answer = answer.strip()
        
        return answer
        
    except Exception as e:
        print(f"❌ Error en respuesta técnica: {e}")
        return "Disculpe, experimenté una dificultad técnica. ¿Podría reformular la pregunta?"

# =====================================================
#   PROCESAMIENTO DE PREGUNTAS DEL TRIBUNAL
# =====================================================
def process_tribunal_question(engine, tribunal_members, pdf_text, hand_raised_counter, current_hand_raiser):
    """
    Procesamiento de preguntas del tribunal durante la defensa
    """
    print("🤔 Procesando pregunta del tribunal...")
    
    try:
        evaluator_id = current_hand_raiser.value
        
        if evaluator_id < 0 or evaluator_id >= len(tribunal_members):
            if len(tribunal_members) > 1:
                speak_technical(engine, "Disculpe, ¿cuál miembro de la terna desea hacer una pregunta?")
                response = listen_technical()
                if response and response not in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""]:
                    current_evaluator = tribunal_members[0]  # Default al primer evaluador
                else:
                    current_evaluator = tribunal_members[0]
            else:
                current_evaluator = tribunal_members[0]
        else:
            current_evaluator = tribunal_members[evaluator_id] if evaluator_id < len(tribunal_members) else tribunal_members[0]
        
        speak_technical(engine, f"Sí, {current_evaluator}, escucho su pregunta.")
        
        question = listen_technical(timeout=15)  # Más tiempo para preguntas técnicas
        hand_raised_counter.value = 0
        
        if not question or question in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""]:
            if question and question.startswith("error"):
                speak_technical(engine, "Disculpe, hubo una interferencia en el sistema de audio. ¿Podría repetir su pregunta?")
            else:
                speak_technical(engine, "No logré procesar su pregunta. ¿Podría reformularla?")
            return True
        
        try:
            answer = ask_thesis_question(question, pdf_text, current_evaluator)
            speak_technical(engine, answer)
        except Exception as e:
            print(f"❌ Error al procesar respuesta técnica: {e}")
            speak_technical(engine, "Disculpe, experimenté una dificultad técnica al procesar su pregunta. Continuemos con la presentación.")
        
        speak_technical(engine, "¿Algún otro miembro de la terna evaluadora tiene alguna pregunta sobre este punto?")
        time.sleep(2)  # Pausa para permitir respuesta
        
        return True
        
    except Exception as e:
        print(f"❌ Error en procesamiento de pregunta del tribunal: {e}")
        speak_technical(engine, "Disculpe, hubo un problema técnico. Continuemos con la defensa.")
        return True

# ================================
#   PRESENTACIÓN DE TESIS
# ================================
def present_thesis(engine, pdf_path, pdf_text, tribunal_members, hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser):
    """
    Presentación formal de la tesis
    """
    try:
        print("📊 Iniciando presentación formal de tesis...")
        
        cv2.namedWindow("Defensa de Tesis", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Defensa de Tesis", 900, 700)

        with fitz.open(pdf_path) as doc:
            total_slides = len(doc)
            slide_num = 0
            
            while slide_num < total_slides and exit_flag.value == 0:
                current_slide_num.value = slide_num + 1
                print(f"📝 Presentando diapositiva {current_slide_num.value} de {total_slides}")
                
                # Verificar preguntas del tribunal
                if hand_raised_counter.value > 0:
                    print(f"✋ Pregunta del tribunal detectada: {hand_raised_counter.value}")
                    process_tribunal_question(engine, tribunal_members, pdf_text, hand_raised_counter, current_hand_raiser)
                    continue
                
                page = doc[slide_num]
                page_img = show_pdf_page_in_opencv(page)
                cv2.imshow("Defensa de Tesis", page_img)
                cv2.waitKey(50)

                page_text = page.get_text()

                if page_text.strip():
                    prompt = f"""
                    Explica el siguiente contenido de tesis de ingeniería de manera técnica y formal, 
                    como lo haría un tesista presentando ante un tribunal académico. 
                    Sé preciso, técnico pero comprensible. Máximo 5 oraciones:
                    
                    Contenido:
                    {page_text}
                    """
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": """Eres ADAI, sistema de defensa automatizada de tesis. 
                                    Presenta contenido técnico de manera formal y académica. 
                                    NO uses emojis, símbolos especiales, ni caracteres no alfabéticos.
                                    Mantén un tono académico y profesional."""},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        explanation = response.choices[0].message.content
                        explanation = explanation.replace("*", "").replace("**", "").replace("***", "")
                        explanation = explanation.replace("- ", "").replace("• ", "")
                    except Exception as e:
                        print(f"❌ Error en OpenAI: {e}")
                        explanation = f"En esta sección se presenta: {page_text[:200]}..."
                else:
                    explanation = "Esta diapositiva presenta elementos visuales complementarios al proyecto de tesis."
                
                # Presentación formal
                slide_info = f"Diapositiva {slide_num + 1}. "
                speak_technical(engine, slide_info)

                # Explicación técnica en segmentos
                sentences = []
                for part in explanation.split("."):
                    if part.strip():
                        sentences.append(part.strip() + ".")

                for i, sentence in enumerate(sentences):
                    if hand_raised_counter.value > 0:
                        print(f"✋ Interrupción del tribunal detectada")
                        process_tribunal_question(engine, tribunal_members, pdf_text, hand_raised_counter, current_hand_raiser)
                        continue
                    
                    if exit_flag.value != 0:
                        return False
                    
                    if sentence.strip():
                        speak_technical(engine, sentence)
                    
                    time.sleep(0.3)
                
                # Pausa entre diapositivas
                for _ in range(8):
                    if hand_raised_counter.value > 0 or exit_flag.value != 0:
                        break
                    time.sleep(0.2)
                
                if hand_raised_counter.value > 0:
                    process_tribunal_question(engine, tribunal_members, pdf_text, hand_raised_counter, current_hand_raiser)
                    continue
                
                slide_num += 1
        
        print("✅ Presentación de tesis completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en presentación de tesis: {e}")
        return False

# ==========================
#  IDENTIFICACIÓN DEL TRIBUNAL - CÓDIGO ORIGINAL RESTAURADO
# ==========================
def identify_tribunal(engine, current_slide_num, exit_flag):
    """
    Identificación del tribunal evaluador - CÓDIGO ORIGINAL DE ADAI que funcionaba
    """
    print("👥 Iniciando identificación del tribunal evaluador")
    known_faces = load_tribunal_faces()
    tribunal_members = []
    
    # Inicializar MediaPipe para detección facial
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        model_selection=1,  # Para distancias largas (hasta 5 metros)
        min_detection_confidence=0.03  # Sensible para detectar a 3-5m
    )
    
    speak_technical(engine, "Buenos días honorables miembros de la terna evaluadora. Procederé a identificar a los evaluadores presentes para iniciar la defensa formal.")
    
    # Capturar varios frames para tener una buena imagen
    frames = []
    for attempt in range(10):
        print(f"🔍 Intento {attempt + 1} de capturar frame...")
        frame = capture_frame()
        if frame is not None:
            frames.append(frame)
            print(f"✅ Frame capturado exitosamente (intento {attempt + 1})")
        else:
            print(f"❌ No se pudo capturar frame (intento {attempt + 1})")
        time.sleep(0.5)
    
    if not frames:
        print("❌ No se pudieron capturar frames después de múltiples intentos")
        speak_technical(engine, "Experimento dificultades técnicas con el sistema de identificación. Procederé con evaluadores genéricos.")
        tribunal_members = ["Evaluador 1"]
        return tribunal_members, tribunal_members[0]
    
    print(f"✅ Se capturaron {len(frames)} frames para análisis")
    
    # Seleccionar mejor frame
    best_frame = None
    max_faces = 0
    best_detections = None
    
    for frame in frames:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)
        num_faces = len(results.detections) if results.detections else 0
        print(f"📊 Frame analizando: {num_faces} caras detectadas")
        
        if num_faces > max_faces:
            max_faces = num_faces
            best_frame = frame
            best_detections = results.detections
    
    if best_frame is None or max_faces == 0:
        print("❌ No se detectaron caras en ningún frame")
        speak_technical(engine, "No se detectan evaluadores en el campo visual. Procederé con un evaluador genérico.")
        tribunal_members = ["Evaluador 1"]
        return tribunal_members, tribunal_members[0]
    
    print(f"✅ Mejor frame seleccionado con {max_faces} caras")
    
    # Procesamos el mejor frame
    frame = best_frame
    h, w = frame.shape[:2]
    debug_frame = frame.copy()
    detected_faces = []
    
    # CONFIGURACIÓN PARA 3-5 METROS
    min_face_area = (w * h) * 0.00005  # Para caras a 3-5m
    max_face_area = (w * h) * 0.1
    
    for i, detection in enumerate(best_detections):
        # Obtenemos el bounding box
        bbox = detection.location_data.relative_bounding_box
        x1 = int(bbox.xmin * w)
        y1 = int(bbox.ymin * h)
        width = int(bbox.width * w)
        height = int(bbox.height * h)
        
        # Filtrar caras según tamaño para 3-5m
        face_area = width * height
        
        if (min_face_area <= face_area <= max_face_area and 
            width > 30 and height > 30 and  # Tamaño mínimo para 3-5m
            width < w * 0.6 and height < h * 0.6 and
            x1 >= 0 and y1 >= 0 and 
            x1 + width <= w and y1 + height <= h):
            
            # Guardamos la información del rostro CON POSICIÓN X
            detected_faces.append({
                'id': i,
                'bbox': (x1, y1, width, height),
                'x_center': x1 + width // 2,  # POSICIÓN X PARA ORDENAR
                'y_center': y1 + height // 2
            })
            
            # Dibujamos un rectángulo alrededor de la cara
            cv2.rectangle(debug_frame, (x1, y1), (x1 + width, y1 + height), (0, 255, 0), 2)
            cv2.putText(debug_frame, f"Detectado {i+1}", (x1, y1-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    print(f"📊 Caras válidas detectadas: {len(detected_faces)}")

    if len(detected_faces) == 0:
        print("❌ No se detectaron caras válidas")
        speak_technical(engine, "No se detectan evaluadores válidos. Procederé con un evaluador genérico.")
        tribunal_members = ["Evaluador 1"]
        return tribunal_members, tribunal_members[0]

    # Ordenar tribunal de izquierda a derecha
    detected_faces.sort(key=lambda face: face['x_center'])
    print("📋 Ordenando evaluadores de izquierda a derecha...")
    
    # Reasignar IDs según el orden de izquierda a derecha
    for new_id, face_data in enumerate(detected_faces):
        face_data['sorted_id'] = new_id
        x1, y1, width, height = face_data['bbox']
        cv2.rectangle(debug_frame, (x1, y1), (x1 + width, y1 + height), (255, 128, 0), 3)
        cv2.putText(debug_frame, f"Evaluador {new_id + 1}", (x1, y1-15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 128, 0), 2)
    
    # Mostrar la imagen con las caras ordenadas
    display_frame = cv2.resize(debug_frame, (800, 600))  # Tamaño fijo más pequeño
    cv2.imshow("Detección ordenada (Izq → Der)", display_frame)
    cv2.waitKey(3000)  # Mostrar por 3 segundos

    # LISTA DE NOMBRES VÁLIDOS PARA FILTRAR RESPUESTAS INVÁLIDAS
    invalid_responses = [
        "sí", "si", "no", "seguimos", "continuar", "siguiente", "ok", "vale", 
        "bien", "listo", "ya", "ahora", "vamos", "adelante", "error_capture", 
        "error_google", "error_unknown", "error_general", "timeout", ""
    ]
    
    # PROCESAR CADA CARA EN ORDEN DE IZQUIERDA A DERECHA
    for face_data in detected_faces:
        sorted_id = face_data['sorted_id']
        x1, y1, width, height = face_data['bbox']
        
        print(f"🔍 Procesando Evaluador {sorted_id + 1} (de izquierda a derecha)")
        
        # Extraemos el rostro para face_recognition
        face_img = frame[y1:y1+height, x1:x1+width]
        
        if face_img.size == 0:
            print(f"❌ Error: imagen de cara vacía para Evaluador {sorted_id + 1}")
            name = f"Evaluador {sorted_id + 1}"
            tribunal_members.append(name)
            speak_technical(engine, f"Identifico al {name}.")
            continue
        
        # Lo convertimos a RGB para face_recognition
        try:
            rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"❌ Error convirtiendo cara a RGB: {e}")
            name = f"Evaluador {sorted_id + 1}"
            tribunal_members.append(name)
            speak_technical(engine, f"Identifico al {name}.")
            continue
        
        # Intentamos obtener encodings
        try:
            face_locations = face_recognition.face_locations(rgb_face)
            if not face_locations:
                print(f"⚠️ No se pudo procesar la cara de Evaluador {sorted_id + 1}")
                name = f"Evaluador {sorted_id + 1}"
                tribunal_members.append(name)
                speak_technical(engine, f"Identifico al {name}.")
                continue
            
            face_encodings = face_recognition.face_encodings(rgb_face, face_locations)
            if not face_encodings:
                print(f"⚠️ No se pudo generar encoding para Evaluador {sorted_id + 1}")
                name = f"Evaluador {sorted_id + 1}"
                tribunal_members.append(name)
                speak_technical(engine, f"Identifico al {name}.")
                continue
            
            face_encoding = face_encodings[0]
            
        except Exception as e:
            print(f"❌ Error procesando cara de Evaluador {sorted_id + 1}: {e}")
            name = f"Evaluador {sorted_id + 1}"
            tribunal_members.append(name)
            speak_technical(engine, f"Identifico al {name}.")
            continue
        
        # Verificar si coincide con alguna cara conocida
        face_recognized = False
        for existing_name, known_encoding in known_faces.items():
            try:
                match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.55)
                if match[0]:
                    # VERIFICAR QUE NO ESTÉ YA EN LA LISTA
                    if existing_name not in tribunal_members:
                        tribunal_members.append(existing_name)
                        face_recognized = True
                        print(f"✅ Evaluador reconocido en posición {sorted_id + 1}: {existing_name}")
                        speak_technical(engine, f"Identifico al {existing_name}.")
                        break
                    else:
                        print(f"⚠️ {existing_name} ya está registrado, continuando búsqueda...")
                        continue
            except Exception as e:
                print(f"❌ Error comparando con {existing_name}: {e}")
                continue
        
        # SI NO FUE RECONOCIDO, PEDIR NOMBRE
        if not face_recognized:
            speak_technical(engine, f"Estimado evaluador en posición {sorted_id + 1}, por favor indique su nombre.")
            time.sleep(1)  # Pausa pequeña
            winsound.Beep(800, 500) 

            # Intentamos capturar el nombre con timeout más largo
            attempts = 0
            max_attempts = 3
            name = None
            
            while attempts < max_attempts and not name:
                attempts += 1
                print(f"🎤 Intento {attempts} de capturar nombre para Evaluador {sorted_id + 1}")
                
                raw_name = listen_technical(timeout=8)
                
                if raw_name and raw_name.lower().strip() not in invalid_responses:
                    # Limpiar el nombre
                    cleaned_name = raw_name.strip().lower()
                    
                    # Verificar que sea un nombre válido (al menos 2 caracteres, solo letras/espacios)
                    if len(cleaned_name) >= 2 and all(c.isalpha() or c.isspace() for c in cleaned_name):
                        name = cleaned_name
                        break
                    else:
                        print(f"⚠️ Nombre inválido: '{cleaned_name}'. Intento {attempts}/{max_attempts}")
                        if attempts < max_attempts:
                            speak_technical(engine, "No entendí su nombre. Intente de nuevo.")
                            time.sleep(1)  # Pausa pequeña
                else:
                    print(f"⚠️ Respuesta inválida: '{raw_name}'. Intento {attempts}/{max_attempts}")
                    if attempts < max_attempts:
                        speak_technical(engine, "No pude escuchar su nombre. Por favor repita.")
            
            if name:
                # Verificar si ya existe este nombre
                original_name = name
                counter = 1
                while name in tribunal_members:
                    counter += 1
                    name = f"{original_name}_{counter}"
                
                if name != original_name:
                    speak_technical(engine, f"Ya existe un evaluador con ese nombre. Lo registraré como {name}.")
                
                # Guardar la cara con el nombre
                try:
                    path = os.path.join(faces_dir, f"{name}.jpg")
                    cv2.imwrite(path, face_img)
                    
                    # Actualizar known_faces para futuras comparaciones
                    known_faces[name] = face_encoding
                    tribunal_members.append(name)
                    
                    speak_technical(engine, f"Registrado, {name}. Es un honor presentar ante usted.")
                    print(f"✅ Nuevo evaluador registrado en posición {sorted_id + 1}: {name}")
                    
                except Exception as e:
                    print(f"❌ Error guardando cara de {name}: {e}")
                    name = f"Evaluador {sorted_id + 1}"
                    tribunal_members.append(name)
                    speak_technical(engine, f"Hubo un problema técnico. Lo identificaré como {name}.")
            else:
                # No se pudo capturar un nombre válido después de varios intentos
                name = f"Evaluador {sorted_id + 1}"
                tribunal_members.append(name)
                speak_technical(engine, f"No pude entender su nombre. Lo registraré como {name}.")
                print(f"⚠️ No se pudo capturar nombre válido para Evaluador {sorted_id + 1}")
    
    # Limpiar recursos
    face_detection.close()
    cv2.destroyWindow("Detección ordenada (Izq → Der)")
    
    # Verificamos si tenemos usuarios registrados
    if not tribunal_members:
        speak_technical(engine, "No detecté ningún evaluador. Continuaré la defensa con un evaluador genérico.")
        tribunal_members = ["Evaluador 1"]
    
    # MENSAJE DE BIENVENIDA CON ORDEN
    try:
        num_evaluators = len(tribunal_members)
        
        if num_evaluators > 1:
            speak_technical(engine, f"Perfecto. He registrado a {num_evaluators} evaluadores.")
        
        speak_technical(engine, f"Procederemos con la defensa formal ante {num_evaluators} evaluador{'es' if num_evaluators > 1 else ''}.")
        
    except Exception as e:
        print(f"❌ Error al finalizar registro: {e}")
        speak_technical(engine, "Hubo un problema al finalizar el registro, pero continuaremos con la defensa.")
        if not tribunal_members:
            tribunal_members = ["Evaluador 1"]
    
    print(f"✅ Identificación completada de izquierda a derecha. Evaluadores finales: {tribunal_members}")
    return tribunal_members, tribunal_members[0] if tribunal_members else "Evaluador 1"

# ================================
#   SESIÓN DE PREGUNTAS Y RESPUESTAS
# ================================
def qa_session(engine, tribunal_members, pdf_text, hand_raised_counter, current_hand_raiser, exit_flag):
    """
    Sesión de preguntas y respuestas al final de la presentación
    """
    print("🎓 Iniciando sesión de preguntas y respuestas")
    
    speak_technical(engine, "Hemos concluido la presentación formal. Ahora estoy disponible para responder las preguntas de la terna de evaluadores.")
    speak_technical(engine, "Por favor, levanten la mano para formular sus consultas. Cuando no haya más preguntas, indiquen 'ya no hay más preguntas' para concluir la defensa.")
    
    questions_answered = 0
    
    try:
        while exit_flag.value == 0:
            # Escuchar continuamente por señales de finalización
            print("🎤 Escuchando por preguntas de la terna de evaluadores o señal de finalización...")
            
            # Verificar si hay manos levantadas
            if hand_raised_counter.value > 0:
                questions_answered += 1
                print(f"✋ Procesando pregunta #{questions_answered} del tribunal")
                process_tribunal_question(engine, tribunal_members, pdf_text, hand_raised_counter, current_hand_raiser)
                continue
            
            # Escuchar por un tiempo corto para detectar "ya no hay más preguntas"
            response = listen_technical(timeout=3)
            
            if response and ("ya no hay" in response or "no hay más" in response or "no hay mas" in response or 
                           "terminar" in response or "finalizar" in response or "concluir" in response):
                print("🎓 Señal de finalización detectada")
                break
            
            # Pequeña pausa para no sobrecargar el sistema
            time.sleep(0.5)
        
        # Mensaje de cierre formal
        speak_technical(engine, f"Agradezco a la terna de evaluadores por sus {questions_answered} pregunta{'s' if questions_answered != 1 else ''}.")
        speak_technical(engine, "Con esto concluyo la defensa formal de mi proyecto de tesis de ingeniería en sistemas y mecatrónica.")
        speak_technical(engine, "Quedo a disposición de la terna de evaluadores para cualquier aclaración adicional. Muchas gracias por su atención.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en sesión de Q&A: {e}")
        speak_technical(engine, "Disculpe, experimento dificultades técnicas. Muchas gracias por su atención.")
        return False

# ============
#   MAIN PARA DEFENSA DE TESIS
# ============
def main():
    """
    Función principal para la defensa de tesis
    """
    try:
        print("🎓 Iniciando ADAI - Sistema de Defensa de Tesis")
        print("="*60)
        
        # Inicialización básica
        hand_raised_counter = multiprocessing.Value('i', 0)
        current_slide_num   = multiprocessing.Value('i', 1)
        exit_flag           = multiprocessing.Value('i', 0)
        current_hand_raiser = multiprocessing.Value('i', -1)

        engine = initialize_tts()
        if not engine:
            print("❌ Error crítico: No se pudo inicializar sistema de síntesis de voz")
            return

        # Saludo formal inicial
        speak_technical(engine, "Buenos días. Soy ADAI, Asistente Docente Androide de Ingeniería.")
        speak_technical(engine, "Procederé a presentar el proyecto de tesis de ingeniería en sistemas y mecatrónica.")

        # Configuración del PDF de tesis
        pdf_path = os.path.join(script_dir, "DefensaTesis2.pdf")  # Cambia el nombre según tu archivo
        if not os.path.exists(pdf_path):
            # Buscar PDFs alternativos en el directorio
            pdf_files = [f for f in os.listdir(script_dir) if f.endswith('.pdf')]
            if pdf_files:
                pdf_path = os.path.join(script_dir, pdf_files[0])
                print(f"📄 Usando PDF encontrado: {pdf_files[0]}")
            else:
                print("❌ No se encontró archivo PDF de tesis")
                speak_technical(engine, "Error crítico: No se encontró el archivo de tesis. Abortando defensa.")
                return
        
        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text:
            print("❌ No se pudo extraer texto del PDF")
            speak_technical(engine, "Error crítico: No se pudo procesar el contenido de la tesis.")
            return
        
        print(f"✅ PDF de tesis cargado: {len(pdf_text)} caracteres")
        
        # Identificar tribunal evaluador
        print("🔍 Fase 1: Identificación del tribunal evaluador")
        tribunal_members, _ = identify_tribunal(engine, current_slide_num, exit_flag)
        
        # Cargar caras conocidas del tribunal
        known_faces = load_tribunal_faces()

        # Iniciar monitoreo del tribunal
        camera_proc = Process(
            target=camera_process_tribunal,
            args=(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, tribunal_members)
        )
        camera_proc.daemon = True
        camera_proc.start()

        print("⏳ Inicializando sistema de monitoreo del tribunal...")
        time.sleep(3)

        # Anuncio de inicio de presentación
        speak_technical(engine, "La terna evaluadora ha sido identificado correctamente. Iniciaremos la presentación formal del proyecto.")

        # Presentación de la tesis
        print("📊 Fase 2: Presentación formal de tesis")
        if present_thesis(engine, pdf_path, pdf_text, tribunal_members,
                         hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser):
            
            # Sesión de preguntas y respuestas
            print("🎓 Fase 3: Sesión de preguntas y respuestas")
            qa_session(engine, tribunal_members, pdf_text, hand_raised_counter, current_hand_raiser, exit_flag)
        
        print("🛑 Finalizando defensa de tesis")
        exit_flag.value = 1

        print("⏳ Cerrando procesos del sistema...")
        camera_proc.join(timeout=5)
        
        if camera_proc.is_alive():
            camera_proc.terminate()
            camera_proc.join(timeout=2)
        
        speak_technical(engine, "Sistema ADAI desconectado. Defensa de tesis finalizada exitosamente.")
        print("✅ Defensa de tesis completada")
    
    except Exception as e:
        print(f"❌ Error crítico en defensa: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'exit_flag' in locals():
            exit_flag.value = 1
        if 'camera_proc' in locals() and camera_proc.is_alive():
            camera_proc.terminate()
            camera_proc.join(timeout=2)
        
        cv2.destroyAllWindows()
        print("🔚 Sistema ADAI desactivado")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()