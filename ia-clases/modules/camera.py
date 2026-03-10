"""
Módulo de funciones de cámara y detección para ADAI
==================================================

Contiene todas las funciones relacionadas con:
- Captura de video
- Detección facial
- Detección de manos
- Reconocimiento facial
- Procesamiento de frames
"""

import cv2
import face_recognition
import mediapipe as mp
import numpy as np
import time
import os
from .config import (
    CAMERA_CONFIGS, RESOLUTIONS_TO_TRY, MEDIAPIPE_CONFIG, 
    FACE_DETECTION_CONFIG, HAND_DETECTION_CONFIG, COLORS
)

def verify_camera_for_iriun():
    """
    Verifica que la cámara funcione correctamente con iriun
    
    Returns:
        bool: True si la cámara funciona, False en caso contrario
    """
    print("🔍 Verificando cámara para iriun...")
    
    for index, backend, name in CAMERA_CONFIGS:
        try:
            if backend is None:
                cap = cv2.VideoCapture(index)
            else:
                cap = cv2.VideoCapture(index, eval(backend))
            
            if cap.isOpened():
                # Intentar leer un frame
                for _ in range(5):
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✅ Cámara funcionando con configuración: {name}")
                        cap.release()
                        return True
                    time.sleep(0.2)
            
            cap.release()
            print(f"❌ No funciona con configuración: {name}")
        except Exception as e:
            print(f"❌ Error con configuración {name}: {e}")
    
    return False

def capture_frame():
    """
    Captura un frame de la cámara con diferentes configuraciones
    
    Returns:
        numpy.ndarray: Frame capturado o None si hay error
    """
    for index, backend in [(0, None), (0, cv2.CAP_DSHOW), (1, None), (2, None)]:
        try:
            if backend is None:
                cap = cv2.VideoCapture(index)
            else:
                cap = cv2.VideoCapture(index, backend)
                
            if not cap.isOpened():
                continue
            
            # Configurar para máxima resolución disponible
            for width, height, name in RESOLUTIONS_TO_TRY:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                
                # Verificar si se aplicó la resolución
                actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                
                if actual_width >= width * 0.9 and actual_height >= height * 0.9:
                    print(f"✅ Resolución configurada: {actual_width}x{actual_height}")
                    break
            
            # Dar tiempo para que se estabilice
            for _ in range(8):
                cap.read()
                time.sleep(0.1)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None and frame.size > 0:
                print(f"✅ Frame capturado: {frame.shape[1]}x{frame.shape[0]} con configuración: índice {index}")
                return frame
                
        except Exception as e:
            print(f"❌ Error con configuración índice {index}: {e}")
            if 'cap' in locals() and cap.isOpened():
                cap.release()
    
    return None

def load_known_faces(faces_dir):
    """
    Carga las caras conocidas desde el directorio especificado
    
    Args:
        faces_dir (str): Directorio donde están las imágenes de caras
        
    Returns:
        dict: Diccionario con nombres y encodings de caras conocidas
    """
    known_faces = {}
    for file in os.listdir(faces_dir):
        if file.endswith(".jpg"):
            path = os.path.join(faces_dir, file)
            image = face_recognition.load_image_file(path)
            encoding = face_recognition.face_encodings(image)
            if encoding:
                known_faces[file.split(".")[0]] = encoding[0]
    return known_faces

def recognize_user(frame, known_faces):
    """
    Reconoce un usuario en el frame usando face_recognition
    
    Args:
        frame: Frame de la cámara
        known_faces (dict): Diccionario de caras conocidas
        
    Returns:
        str: Nombre del usuario reconocido o None
    """
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in face_encodings:
            for name, known_encoding in known_faces.items():
                match = face_recognition.compare_faces([known_encoding], encoding, tolerance=FACE_DETECTION_CONFIG['tolerance'])
                if match[0]:
                    return name
        return None
    except Exception as e:
        print(f"❌ Error al reconocer usuario: {e}")
        return None

def save_new_face(frame, name, faces_dir):
    """
    Guarda una nueva cara en el directorio de caras
    
    Args:
        frame: Frame de la cámara
        name (str): Nombre del usuario
        faces_dir (str): Directorio donde guardar la cara
        
    Returns:
        numpy.ndarray: Encoding de la cara o None si hay error
    """
    try:
        path = os.path.join(faces_dir, f"{name}.jpg")
        cv2.imwrite(path, frame)
        image = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(image)[0]
        return encoding
    except Exception as e:
        print(f"❌ Error al guardar nueva cara: {e}")
        return None

def identify_users(engine, current_slide_num, exit_flag):
    """
    Identificar usuarios presentes en la clase
    """
    print("👥 Iniciando identificación de usuarios")
    
    # Cargar caras conocidas
    from .config import get_faces_dir
    faces_dir = get_faces_dir()
    known_faces = load_known_faces(faces_dir)
    current_users = []
    
    try:
        # Inicializar MediaPipe para detección facial
        import mediapipe as mp
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.03
        )
        
        # Mensaje de bienvenida
        from .speech import speak_with_animation
        speak_with_animation(engine, "Bienvenidos a la clase. Voy a identificar a todos los estudiantes presentes.")
        
        # Capturar frame
        frame = capture_frame()
        if frame is None:
            print("❌ No se pudo capturar frame")
            current_users = ["Estudiante 1"]
            return current_users, current_users[0]
        
        # Detectar caras
        import cv2
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)
        
        if results.detections:
            print(f"✅ Se detectaron {len(results.detections)} caras")
            for i, detection in enumerate(results.detections):
                user_name = f"Estudiante {i+1}"
                current_users.append(user_name)
        else:
            print("❌ No se detectaron caras")
            current_users = ["Estudiante 1"]
        
        # Mensaje final
        speak_with_animation(engine, f"Identificados {len(current_users)} estudiantes. Continuemos con la clase.")
        
    except Exception as e:
        print(f"❌ Error en identificación: {e}")
        current_users = ["Estudiante 1"]
    
    return current_users, current_users[0] if current_users else "Estudiante 1"

def camera_process(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, registered_users):
    """
    Proceso de cámara corregido con mejor detección facial para múltiples usuarios
    
    Args:
        hand_raised_counter: Contador compartido de manos levantadas
        current_slide_num: Número de diapositiva actual
        exit_flag: Bandera de salida
        current_hand_raiser: ID del usuario que levantó la mano
        registered_users: Lista de usuarios registrados
    """
    try:
        print("🎥 [CAMERA] Iniciando proceso de cámara...")
        print(f"🎥 [CAMERA] Usuarios registrados: {registered_users}")
        
        # Configuración MediaPipe MEJORADA
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(**MEDIAPIPE_CONFIG['hands'])
        mp_draw = mp.solutions.drawing_utils
        
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(**MEDIAPIPE_CONFIG['face_detection'])
        
        print("🎥 [CAMERA] MediaPipe configurado correctamente")
        
        # Intentar abrir la cámara con múltiples métodos
        cap = None
        for index, backend, name in CAMERA_CONFIGS:
            try:
                print(f"🎥 [CAMERA] Probando {name}...")
                if backend is None:
                    cap = cv2.VideoCapture(index)
                else:
                    cap = cv2.VideoCapture(index, eval(backend))
                
                if cap.isOpened():
                    # Probar captura rápida
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        print(f"🎥 [CAMERA] ✅ {name} funcionando!")
                        break
                    else:
                        print(f"🎥 [CAMERA] ❌ {name} abre pero no captura")
                        cap.release()
                        cap = None
                else:
                    print(f"🎥 [CAMERA] ❌ {name} no se puede abrir")
                    if cap:
                        cap.release()
                    cap = None
            except Exception as e:
                print(f"🎥 [CAMERA] ❌ Error con {name}: {e}")
                if cap:
                    cap.release()
                cap = None
        
        if cap is None or not cap.isOpened():
            print("🎥 [CAMERA] ❌ ERROR: No se pudo abrir ninguna cámara")
            exit_flag.value = 1
            return
        
        print("🎥 [CAMERA] ✅ Cámara abierta exitosamente")
        
        # Configuración de resolución con fallback
        resolution_set = False
        for width, height, name in RESOLUTIONS_TO_TRY:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            actual_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            if actual_w >= width * 0.8 and actual_h >= height * 0.8:
                print(f"🎥 [CAMERA] ✅ Resolución configurada: {actual_w}x{actual_h} ({name})")
                resolution_set = True
                break
            else:
                print(f"🎥 [CAMERA] ⚠️ {name} no disponible, probando siguiente...")
        
        if not resolution_set:
            print("🎥 [CAMERA] ⚠️ Usando resolución por defecto")
        
        # Optimizaciones básicas
        try:
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            print("🎥 [CAMERA] ✅ Optimizaciones aplicadas")
        except Exception as e:
            print(f"🎥 [CAMERA] ⚠️ No se pudieron aplicar optimizaciones: {e}")
        
        # Crear ventana
        cv2.namedWindow("Clase Virtual", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Clase Virtual", 1000, 700)
        print("🎥 [CAMERA] ✅ Ventana 'Clase Virtual' creada")
        
        # Variables de seguimiento MEJORADAS
        hand_raisers = {}
        max_consecutive = HAND_DETECTION_CONFIG['max_consecutive']
        max_registered_users = len(registered_users)
        face_tracking_threshold = 120  # AUMENTADO de 80 - más permisivo
        
        print(f"🎥 [CAMERA] Configuración: {max_registered_users} usuarios, threshold={face_tracking_threshold}")
        
        user_tracking = {}
        for i in range(max_registered_users):
            user_tracking[i] = {
                'positions': [],
                'last_seen': 0,
                'stable_count': 0,
                'lost_count': 0
            }
        
        student_colors = COLORS['student_colors']
        
        def calculate_distance(pos1, pos2):
            return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
        
        frame_count = 0
        last_status_print = 0
        
        print("🎥 [CAMERA] 🚀 INICIANDO LOOP PRINCIPAL...")
        
        while exit_flag.value == 0:
            ret, frame = cap.read()
            if not ret:
                print("🎥 [CAMERA] ⚠️ No se pudo leer frame, reintentando...")
                time.sleep(0.01)
                continue
            
            h, w = frame.shape[:2]
            frame_count += 1
            
            # Debug cada 150 frames (aprox cada 5 segundos)
            if frame_count - last_status_print > 150:
                print(f"🎥 [CAMERA] 📊 Frame {frame_count}, resolución {w}x{h}")
                last_status_print = frame_count
            
            # MEJORA: Preprocesamiento más agresivo para mejor detección
            enhanced_frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
            rgb_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB)
            
            # DETECCIÓN FACIAL MEJORADA
            current_detections = []
            try:
                face_results = face_detection.process(rgb_frame)
                
                if face_results.detections:
                    if frame_count % 60 == 0:  # Debug cada 2 segundos
                        print(f"🎥 [CAMERA] MediaPipe detectó {len(face_results.detections)} caras")
                    
                    for i, detection in enumerate(face_results.detections):
                        bbox = detection.location_data.relative_bounding_box
                        x1 = int(bbox.xmin * w)
                        y1 = int(bbox.ymin * h)
                        width = int(bbox.width * w)
                        height = int(bbox.height * h)
                        
                        # ÁREA MÍNIMA MÁS PERMISIVA pero realista
                        face_area = width * height
                        min_face_area = (w * h) * FACE_DETECTION_CONFIG['min_face_area_ratio']
                        max_face_area = (w * h) * FACE_DETECTION_CONFIG['max_face_area_ratio']
                        
                        # FILTROS MEJORADOS para caras válidas
                        if (min_face_area <= face_area <= max_face_area and 
                            width > FACE_DETECTION_CONFIG['min_face_size'] and height > FACE_DETECTION_CONFIG['min_face_size'] and
                            width < w * FACE_DETECTION_CONFIG['max_face_size_ratio'] and height < h * FACE_DETECTION_CONFIG['max_face_size_ratio'] and
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
                            
                            if frame_count % 60 == 0:
                                print(f"   Cara {i+1}: área={face_area:.0f}, confianza={confidence:.2f}")
                else:
                    if frame_count % 120 == 0:  # Menos frecuente para no spam
                        print("🎥 [CAMERA] ⚠️ No se detectaron caras válidas")
            
            except Exception as e:
                print(f"🎥 [CAMERA] ❌ Error en detección facial: {e}")
            
            # Asignar detecciones a usuarios registrados
            assignments = {}
            if current_detections:
                try:
                    # Ordenar detecciones por posición X
                    detections_with_x = []
                    for idx, detection in enumerate(current_detections):
                        x1, y1, width, height = detection['bbox']
                        x_center = x1 + width // 2
                        detections_with_x.append((idx, x_center))
                    
                    # Ordenar de izquierda a derecha y asignar secuencialmente
                    detections_with_x.sort(key=lambda item: item[1])
                    for position, (original_idx, x_center) in enumerate(detections_with_x):
                        if position < max_registered_users:
                            assignments[original_idx] = position
                            
                    if frame_count % 60 == 0 and assignments:
                        print(f"🎥 [CAMERA] Asignaciones: {len(assignments)} de {len(current_detections)} caras")
                    
                    for det_idx, user_id in assignments.items():
                        detection = current_detections[det_idx]
                        center = detection['center']
                        
                        # Actualizar tracking
                        user_tracking[user_id]['positions'].append(center)
                        if len(user_tracking[user_id]['positions']) > 10:
                            user_tracking[user_id]['positions'].pop(0)
                        
                        user_tracking[user_id]['last_seen'] = frame_count
                        user_tracking[user_id]['stable_count'] += 1
                        
                        # Dibujar usuario
                        x1, y1, width, height = detection['bbox']
                        color = student_colors[user_id % len(student_colors)]
                        
                        thickness = max(2, int(width / 40))
                        cv2.rectangle(frame, (x1, y1), (x1 + width, y1 + height), color, thickness)
                        
                        # Nombre del usuario
                        font_scale = max(0.6, width / 120)
                        user_name = registered_users[user_id] if user_id < len(registered_users) else f"Usuario {user_id+1}"
                        cv2.putText(frame, user_name, (x1, y1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
                        
                        # Información adicional
                        confidence = detection.get('confidence', 0)
                        cv2.putText(frame, f"{confidence:.2f}", (x1 + width - 50, y1 + 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.7, color, max(1, thickness-1))
                        
                        # Distancia estimada
                        if detection['area'] > 0:
                            distance_est = int(120000 / detection['area'])
                            cv2.putText(frame, f"~{distance_est}cm", (x1, y1 + height + 25),
                                        cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.8, color, thickness)
                
                except Exception as e:
                    print(f"🎥 [CAMERA] ❌ Error en asignación: {e}")
            
            # Actualizar usuarios no asignados
            assigned_users = set(assignments.values()) if current_detections else set()
            for user_id in range(max_registered_users):
                if user_id not in assigned_users:
                    user_tracking[user_id]['lost_count'] += 1
                    user_tracking[user_id]['stable_count'] = 0
                else:
                    user_tracking[user_id]['lost_count'] = 0
            
            # DETECCIÓN DE MANOS MEJORADA - SOLO CON CARAS REALES
            raised_hands_in_frame = {}
            try:
                results = hands.process(rgb_frame)
                
                if results.multi_hand_landmarks and current_detections and assignments:
                    for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                        
                        # Verificar si la mano está levantada
                        if middle_tip.y < wrist.y - HAND_DETECTION_CONFIG['hand_raise_threshold']:
                            wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
                            
                            # NUEVA LÓGICA: Verificar que la mano esté POR ENCIMA de alguna cara
                            hand_is_above_face = False
                            closest_user_id = None
                            min_distance = float('inf')
                            
                            for det_idx, user_id in assignments.items():
                                detection = current_detections[det_idx]
                                face_x1, face_y1, face_width, face_height = detection['bbox']
                                face_x2 = face_x1 + face_width
                                face_y2 = face_y1 + face_height
                                face_center_x = face_x1 + face_width // 2
                                face_center_y = face_y1 + face_height // 2
                                
                                # CONDICIÓN 1: La mano debe estar horizontalmente cerca de la cara
                                horizontal_distance = abs(wrist_x - face_center_x)
                                max_horizontal_distance = face_width * HAND_DETECTION_CONFIG['max_horizontal_distance_ratio']
                                
                                # CONDICIÓN 2: La mano debe estar ENCIMA de la cara
                                vertical_clearance = face_y1 - wrist_y  # Distancia positiva = mano arriba
                                min_vertical_clearance = HAND_DETECTION_CONFIG['min_vertical_clearance']
                                max_vertical_clearance = face_height * HAND_DETECTION_CONFIG['max_vertical_clearance_ratio']
                                
                                # VERIFICAR AMBAS CONDICIONES
                                if (horizontal_distance <= max_horizontal_distance and 
                                    min_vertical_clearance <= vertical_clearance <= max_vertical_clearance):
                                    
                                    hand_is_above_face = True
                                    
                                    # Calcular distancia total para encontrar la cara más cercana
                                    total_distance = ((face_center_x - wrist_x) ** 2 + (face_center_y - wrist_y) ** 2) ** 0.5
                                    
                                    if total_distance < min_distance:
                                        min_distance = total_distance
                                        closest_user_id = user_id
                                    
                                    # DEBUG: Mostrar información de validación
                                    if frame_count % 30 == 0:
                                        user_name = registered_users[user_id] if user_id < len(registered_users) else f"Usuario {user_id+1}"
                                        print(f"🎯 [HAND] Mano válida para {user_name}: h_dist={horizontal_distance:.0f}, v_clear={vertical_clearance:.0f}")
                            
                            # PROCESAR SOLO SI LA MANO ESTÁ REALMENTE ENCIMA DE UNA CARA
                            if hand_is_above_face and closest_user_id is not None:
                                raised_hands_in_frame[closest_user_id] = True
                                person_color = student_colors[closest_user_id % len(student_colors)]
                                
                                # Dibujar landmarks de la mano
                                mp_draw.draw_landmarks(
                                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                    mp_draw.DrawingSpec(color=(255, 255, 255), thickness=3, circle_radius=3),
                                    mp_draw.DrawingSpec(color=(0, 0, 255), thickness=3)
                                )
                                
                                # Círculo en la muñeca
                                cv2.circle(frame, (wrist_x, wrist_y), 15, person_color, -1)
                                
                                # Línea conectando mano con cara (para verificación visual)
                                if closest_user_id in [assignments[idx] for idx in assignments]:
                                    for det_idx, user_id in assignments.items():
                                        if user_id == closest_user_id:
                                            face_center = current_detections[det_idx]['center']
                                            cv2.line(frame, (wrist_x, wrist_y), face_center, person_color, 2)
                                            break
                                
                                # Contador de manos
                                if closest_user_id in hand_raisers:
                                    hand_raisers[closest_user_id] += 1
                                else:
                                    hand_raisers[closest_user_id] = 1
                                
                                user_name = registered_users[closest_user_id] if closest_user_id < len(registered_users) else f"Usuario {closest_user_id+1}"
                                cv2.putText(frame, f"Mano {user_name}: {hand_raisers[closest_user_id]}/{max_consecutive}",
                                            (10, 120 + closest_user_id * 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                            person_color, 2)
                                
                                # Detectar mano completamente levantada
                                if hand_raisers[closest_user_id] >= max_consecutive:
                                    hand_raised_counter.value += 1
                                    current_hand_raiser.value = closest_user_id
                                    hand_raisers[closest_user_id] = 0
                                    print(f"🎥 [CAMERA] ✋ Mano levantada por {user_name}! Contador: {hand_raised_counter.value}")
                                
                                # Debug mejorado
                                if frame_count % 30 == 0:
                                    print(f"🎥 [CAMERA] ✋ Mano válida detectada para {user_name}, contador: {hand_raisers[closest_user_id]}/{max_consecutive}")
                            
                            else:
                                # Mano detectada pero NO está encima de ninguna cara
                                cv2.circle(frame, (wrist_x, wrist_y), 8, (128, 128, 128), -1)  # Círculo gris pequeño
                                cv2.putText(frame, "Mano inválida", (wrist_x + 15, wrist_y),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 128, 128), 1)
                                
                                if frame_count % 60 == 0:
                                    print("🎥 [CAMERA] ⚠️ Mano detectada pero no está encima de ninguna cara")

            except Exception as e:
                print(f"🎥 [CAMERA] ❌ Error en detección de manos: {e}")
            
            # Resetear contadores de manos
            for user_id in list(hand_raisers.keys()):
                if user_id not in raised_hands_in_frame:
                    hand_raisers[user_id] = max(0, hand_raisers[user_id] - 1)
            
            # Información en pantalla
            cv2.putText(frame, f"Manos levantadas: {hand_raised_counter.value}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
            cv2.putText(frame, f"Diapositiva {current_slide_num.value}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 3)
            
            # Info de tracking MEJORADA
            users_tracked = len([u for u in user_tracking.values() if u['last_seen'] > frame_count - 30])
            faces_detected = len(current_detections)
            assignments_count = len(assignments)
            
            cv2.putText(frame, f"Usuarios: {users_tracked}/{max_registered_users}", (w - 300, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Caras: {faces_detected}", (w - 300, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"Asignadas: {assignments_count}", (w - 300, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            
            # Estado de usuarios (todos los registrados)
            for user_id in range(min(max_registered_users, 4)):
                status = "ACTIVO" if user_tracking[user_id]['last_seen'] > frame_count - 10 else "PERDIDO"
                color = (0, 255, 0) if status == "ACTIVO" else (0, 0, 255)
                user_name = registered_users[user_id] if user_id < len(registered_users) else f"U{user_id+1}"
                cv2.putText(frame, f"{user_name}: {status}", (10, h - 80 + user_id * 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Mostrar frame
            cv2.imshow("Clase Virtual", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("🎥 [CAMERA] 🛑 Tecla 'q' presionada, terminando...")
                exit_flag.value = 1
                break
        
        print("🎥 [CAMERA] 🏁 Finalizando loop principal...")
                
    except Exception as e:
        print(f"🎥 [CAMERA] ❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        exit_flag.value = 1
    finally:
        print("🎥 [CAMERA] 🧹 Limpiando recursos...")
        try:
            if 'cap' in locals() and cap and cap.isOpened():
                cap.release()
                print("🎥 [CAMERA] ✅ Cámara liberada")
            if 'hands' in locals():
                hands.close()
                print("🎥 [CAMERA] ✅ MediaPipe hands cerrado")
            if 'face_detection' in locals():
                face_detection.close()
                print("🎥 [CAMERA] ✅ MediaPipe face detection cerrado")
            cv2.destroyAllWindows()
            print("🎥 [CAMERA] ✅ Ventanas cerradas")
        except Exception as e:
            print(f"🎥 [CAMERA] ⚠️ Error al limpiar: {e}")
        
        print("🎥 [CAMERA] 🔚 Proceso de cámara terminado")
