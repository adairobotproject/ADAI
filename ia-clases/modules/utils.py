"""
Módulo de utilidades generales para ADAI
=======================================

Contiene funciones de utilidad general que pueden ser utilizadas
por múltiples módulos del sistema.
"""

import os
import cv2
import face_recognition
import mediapipe as mp
import time
import winsound
from .config import FACE_DETECTION_CONFIG

def summarize_text(text):
    """
    Resumir texto usando OpenAI
    """
    try:
        from .config import client
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

def ask_openai(question, context, student_name=None):
    """
    Versión mejorada de ask_openai para respuestas más naturales
    """
    try:
        from .config import client
        # Sistema mejorado para respuestas naturales
        system_prompt = """Eres ADAI, un asistente educativo androide amigable y conversacional que SOLO
        responde preguntas relacionadas con el contenido educativo. Mantén un tono profesional pero 
        accesible, como un profesor entusiasta. Si la pregunta no está relacionada con el contenido 
        educativo, explica amablemente que solo puedes ayudar con temas académicos."""
        
        user_prompt = f"Pregunta: {question}\n\nContexto del material: {context}"
        
        if student_name:
            user_prompt = f"Estudiante: {student_name}\n\n{user_prompt}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Error en OpenAI: {e}")
        return "Lo siento, tuve un problema al procesar tu pregunta. ¿Podrías reformularla?"

def identify_users(engine, current_slide_num, exit_flag, script_dir, listen_func):
    """
    Versión modificada que registra usuarios de IZQUIERDA A DERECHA
    
    Args:
        engine: Motor de TTS
        current_slide_num: Número de diapositiva actual
        exit_flag: Bandera de salida
        script_dir: Directorio del script
        listen_func: Función de escucha de voz
        
    Returns:
        tuple: (current_users, first_user)
    """
    print("👥 Iniciando identificación de usuarios (izquierda a derecha)")
    
    # Crear directorio de caras si no existe
    faces_dir = os.path.join(script_dir, "faces")
    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)
    
    # Importar funciones necesarias
    from .camera import load_known_faces, save_new_face, capture_frame
    
    known_faces = load_known_faces(faces_dir)
    current_users = []
    
    # Inicializar MediaPipe para detección facial
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        model_selection=1,  # Para distancias largas (hasta 5 metros)
        min_detection_confidence=0.03  # Sensible para detectar a 3-5m
    )
    
    engine.say("Bienvenidos a la clase. Voy a identificar a todos los estudiantes presentes de izquierda a derecha. Mantengan la vista hacia la cámara, porfavor.")
    
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
        engine.say("No puedo acceder a la cámara correctamente. Continuaré sin identificación facial.")
        current_users = ["Estudiante 1"]
        return current_users, current_users[0]
    
    print(f"✅ Se capturaron {len(frames)} frames para análisis")
    
    # Seleccionamos el frame con más caras
    best_frame = None
    max_faces = 0
    best_detections = None
    
    for i, frame in enumerate(frames):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)
        num_faces = len(results.detections) if results.detections else 0
        print(f"📊 Frame {i+1}: {num_faces} caras detectadas")
        
        if num_faces > max_faces:
            max_faces = num_faces
            best_frame = frame
            best_detections = results.detections
    
    if best_frame is None or max_faces == 0:
        print("❌ No se detectaron caras en ningún frame")
        engine.say("No detecto ninguna cara. Continuaré con un estudiante genérico.")
        current_users = ["Estudiante 1"]
        return current_users, current_users[0]
    
    print(f"✅ Mejor frame seleccionado con {max_faces} caras")
    
    # Procesamos el mejor frame
    frame = best_frame
    h, w = frame.shape[:2]
    
    # Variables para mostrar las caras detectadas
    debug_frame = frame.copy()
    
    # Lista para almacenar rostros detectados con sus coordenadas
    detected_faces = []
    
    # CONFIGURACIÓN PARA 3-5 METROS
    min_face_area = (w * h) * FACE_DETECTION_CONFIG['min_face_area_ratio']
    max_face_area = (w * h) * FACE_DETECTION_CONFIG['max_face_area_ratio']
    
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
            width > FACE_DETECTION_CONFIG['min_face_size'] and height > FACE_DETECTION_CONFIG['min_face_size'] and
            width < w * FACE_DETECTION_CONFIG['max_face_size_ratio'] and height < h * FACE_DETECTION_CONFIG['max_face_size_ratio'] and
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

    print("=== POSICIONES ANTES DE ORDENAR ===")
    for i, face in enumerate(detected_faces):
        print(f"Cara {i}: x_center = {face['x_center']}")
    
    # *** ORDENAR DE IZQUIERDA A DERECHA ***
    detected_faces.sort(key=lambda face: face['x_center'])
    print("📋 Ordenando caras de izquierda a derecha...")
    
    # Reasignar IDs según el orden de izquierda a derecha
    for new_id, face_data in enumerate(detected_faces):
        face_data['sorted_id'] = new_id
        x1, y1, width, height = face_data['bbox']
        
        # Actualizar visualización con nuevo orden
        cv2.rectangle(debug_frame, (x1, y1), (x1 + width, y1 + height), (255, 0, 0), 3)
        cv2.putText(debug_frame, f"Persona {new_id + 1}", (x1, y1-15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.putText(debug_frame, f"Pos: {face_data['x_center']}", (x1, y1 + height + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    # Mostrar la imagen con las caras ordenadas
    display_frame = cv2.resize(debug_frame, (800, 600))  # Tamaño fijo más pequeño
    cv2.imshow("Detección ordenada (Izq → Der)", display_frame)
    cv2.waitKey(3000)  # Mostrar por 3 segundos

    detected_faces.sort(key=lambda face: face['x_center'])
    print("=== POSICIONES DESPUÉS DE ORDENAR ===")
    for i, face in enumerate(detected_faces):
        print(f"Posición {i+1}: x_center = {face['x_center']}")
    
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
        
        print(f"🔍 Procesando Persona {sorted_id + 1} (de izquierda a derecha)")
        
        # Extraemos el rostro para face_recognition
        face_img = frame[y1:y1+height, x1:x1+width]
        
        if face_img.size == 0:
            print(f"❌ Error: imagen de cara vacía para Persona {sorted_id + 1}")
            name = f"Estudiante {sorted_id + 1}"
            current_users.append(name)
            engine.say(f"Te registraré como {name}.")
            continue
        
        # Lo convertimos a RGB para face_recognition
        try:
            rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"❌ Error convirtiendo cara a RGB: {e}")
            name = f"Estudiante {sorted_id + 1}"
            current_users.append(name)
            engine.say(f"Te registraré como {name}.")
            continue
        
        # Intentamos obtener encodings
        try:
            face_locations = face_recognition.face_locations(rgb_face)
            if not face_locations:
                print(f"⚠️ No se pudo procesar la cara de Persona {sorted_id + 1}")
                name = f"Estudiante {sorted_id + 1}"
                current_users.append(name)
                engine.say(f"Te registraré como {name}.")
                continue
            
            face_encodings = face_recognition.face_encodings(rgb_face, face_locations)
            if not face_encodings:
                print(f"⚠️ No se pudo generar encoding para Persona {sorted_id + 1}")
                name = f"Estudiante {sorted_id + 1}"
                current_users.append(name)
                engine.say(f"Te registraré como {name}.")
                continue
            
            face_encoding = face_encodings[0]
            
        except Exception as e:
            print(f"❌ Error procesando cara de Persona {sorted_id + 1}: {e}")
            name = f"Estudiante {sorted_id + 1}"
            current_users.append(name)
            engine.say(f"Te registraré como {name}.")
            continue
        
        # Verificar si coincide con alguna cara conocida
        face_recognized = False
        for existing_name, known_encoding in known_faces.items():
            try:
                match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=FACE_DETECTION_CONFIG['tolerance'])
                if match[0]:
                    # VERIFICAR QUE NO ESTÉ YA EN LA LISTA
                    if existing_name not in current_users:
                        current_users.append(existing_name)
                        face_recognized = True
                        print(f"✅ Usuario reconocido en posición {sorted_id + 1}: {existing_name}")
                        engine.say(f"Hola {existing_name}, te reconozco.")
                        break
                    else:
                        print(f"⚠️ {existing_name} ya está registrado, continuando búsqueda...")
                        continue
            except Exception as e:
                print(f"❌ Error comparando con {existing_name}: {e}")
                continue
        
        # SI NO FUE RECONOCIDO, PEDIR NOMBRE
        if not face_recognized:
            engine.say(f"Persona en posición {sorted_id + 1}, por favor di tu nombre despues del bip.")
            time.sleep(1)  # Pausa pequeña
            winsound.Beep(800, 500) 
            
            # Intentamos capturar el nombre con timeout más largo
            attempts = 0
            max_attempts = 3
            name = None
            
            while attempts < max_attempts and not name:
                attempts += 1
                print(f"🎤 Intento {attempts} de capturar nombre para Persona {sorted_id + 1}")
                
                raw_name = listen_func(timeout=8)
                
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
                            engine.say("No entendí tu nombre. Intenta de nuevo despues del bip.")
                            time.sleep(1)  # Pausa pequeña
                            winsound.Beep(800, 500)
                else:
                    print(f"⚠️ Respuesta inválida: '{raw_name}'. Intento {attempts}/{max_attempts}")
                    if attempts < max_attempts:
                        engine.say("No pude escuchar tu nombre. Por favor repite.")
            
            if name:
                # Verificar si ya existe este nombre
                original_name = name
                counter = 1
                while name in current_users:
                    counter += 1
                    name = f"{original_name}_{counter}"
                
                if name != original_name:
                    engine.say(f"Ya existe un usuario con ese nombre. Te registraré como {name}.")
                
                # Guardar la cara con el nombre
                try:
                    face_encoding = save_new_face(face_img, name, faces_dir)
                    if face_encoding is not None:
                        # Actualizar known_faces para futuras comparaciones
                        known_faces[name] = face_encoding
                        current_users.append(name)
                        
                        engine.say(f"Gracias, {name}. Gusto en conocerte.")
                        print(f"✅ Nuevo usuario registrado en posición {sorted_id + 1}: {name}")
                    else:
                        raise Exception("No se pudo generar encoding")
                        
                except Exception as e:
                    print(f"❌ Error guardando cara de {name}: {e}")
                    name = f"Estudiante {sorted_id + 1}"
                    current_users.append(name)
                    engine.say(f"Hubo un problema al registrarte. Te llamaré {name}.")
            else:
                # No se pudo capturar un nombre válido después de varios intentos
                name = f"Estudiante {sorted_id + 1}"
                current_users.append(name)
                engine.say(f"No pude entender tu nombre. Te registraré como {name}.")
                print(f"⚠️ No se pudo capturar nombre válido para Persona {sorted_id + 1}")
    
    # Limpiar recursos
    face_detection.close()
    cv2.destroyWindow("Detección ordenada (Izq → Der)")
    
    # Verificamos si tenemos usuarios registrados
    if not current_users:
        engine.say("No detecté ningún estudiante. Continuaré la clase con un estudiante genérico.")
        current_users = ["Estudiante 1"]
    
    # MENSAJE DE BIENVENIDA CON ORDEN
    try:
        num_students = len(current_users)
        
        if num_students > 1:
            engine.say(f"Perfecto. He registrado a {num_students} estudiantes.")
        
        engine.say(f"Comenzaremos la clase con {num_students} estudiante{'s' if num_students > 1 else ''}.")
        
    except Exception as e:
        print(f"❌ Error al finalizar registro: {e}")
        engine.say("Hubo un problema al finalizar el registro, pero continuaremos con la clase.")
        if not current_users:
            current_users = ["Estudiante 1"]
    
    print(f"✅ Identificación completada de izquierda a derecha. Usuarios finales: {current_users}")
    return current_users, current_users[0] if current_users else "Estudiante 1"
