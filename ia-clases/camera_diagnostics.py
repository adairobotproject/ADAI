import cv2
import numpy as np
import time
import os
import sys

def print_camera_info(camera_index):
    """
    Imprime información detallada sobre la cámara
    """
    print(f"\n=== INFORMACIÓN DE CÁMARA ÍNDICE {camera_index} ===")
    
    # Intenta abrir la cámara con diferentes backends
    backends = [
        (None, "Default"),
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_ANY, "Cualquiera")
    ]
    
    best_backend = None
    for backend, name in backends:
        if backend is None:
            cap = cv2.VideoCapture(camera_index)
        else:
            cap = cv2.VideoCapture(camera_index, backend)
        
        if not cap.isOpened():
            print(f"❌ No se pudo abrir la cámara con backend {name}")
            continue
        
        print(f"✅ Cámara abierta con backend {name}")
        
        # Si es el primer backend exitoso, guardarlo como el mejor
        if best_backend is None:
            best_backend = (backend, name)
        
        # Propiedades de la cámara
        properties = [
            ("CAP_PROP_FRAME_WIDTH", cv2.CAP_PROP_FRAME_WIDTH, "Ancho"),
            ("CAP_PROP_FRAME_HEIGHT", cv2.CAP_PROP_FRAME_HEIGHT, "Alto"),
            ("CAP_PROP_FPS", cv2.CAP_PROP_FPS, "FPS"),
            ("CAP_PROP_FOURCC", cv2.CAP_PROP_FOURCC, "Códec"),
            ("CAP_PROP_BRIGHTNESS", cv2.CAP_PROP_BRIGHTNESS, "Brillo"),
            ("CAP_PROP_CONTRAST", cv2.CAP_PROP_CONTRAST, "Contraste"),
            ("CAP_PROP_SATURATION", cv2.CAP_PROP_SATURATION, "Saturación"),
            ("CAP_PROP_HUE", cv2.CAP_PROP_HUE, "Tono"),
            ("CAP_PROP_GAIN", cv2.CAP_PROP_GAIN, "Ganancia"),
            ("CAP_PROP_EXPOSURE", cv2.CAP_PROP_EXPOSURE, "Exposición"),
            ("CAP_PROP_AUTO_EXPOSURE", cv2.CAP_PROP_AUTO_EXPOSURE, "Auto Exposición"),
            ("CAP_PROP_BUFFERSIZE", cv2.CAP_PROP_BUFFERSIZE, "Tamaño Buffer")
        ]
        
        print(f"\n-- Propiedades de la cámara con backend {name} --")
        
        for prop_name, prop_id, display_name in properties:
            value = cap.get(prop_id)
            
            # Convertir FOURCC a texto legible
            if prop_id == cv2.CAP_PROP_FOURCC:
                fourcc_int = int(value)
                fourcc_chars = ""
                for i in range(4):
                    fourcc_chars += chr(fourcc_int & 0xFF)
                    fourcc_int >>= 8
                value = f"{value} ({fourcc_chars})"
            
            print(f"{display_name} ({prop_name}): {value}")
        
        # Leer un frame para probar
        ret, frame = cap.read()
        if ret:
            print("\n-- Información del frame --")
            print(f"Shape: {frame.shape}")
            print(f"Tipo de datos: {frame.dtype}")
            print(f"Valor mínimo: {frame.min()}, Valor máximo: {frame.max()}")
            print(f"Canales: {frame.shape[2] if len(frame.shape) > 2 else 1}")
            
            # Guardar una imagen para referencia
            try:
                save_dir = "camera_diagnostics"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                
                filename = f"{save_dir}/camera_{camera_index}_{name.replace(' ', '_')}.jpg"
                cv2.imwrite(filename, frame)
                print(f"✅ Imagen guardada como {filename}")
            except Exception as e:
                print(f"❌ Error al guardar imagen: {e}")
        else:
            print("❌ No se pudo leer un frame")
        
        # Prueba de rendimiento: capturar 100 frames y medir FPS
        print("\n-- Prueba de rendimiento --")
        frames = 0
        start_time = time.time()
        
        for _ in range(100):
            ret, frame = cap.read()
            if ret:
                frames += 1
            else:
                break
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        if frames > 0:
            print(f"Capturados {frames} frames en {elapsed:.2f} segundos")
            print(f"FPS real: {frames / elapsed:.2f}")
        else:
            print("❌ No se pudieron capturar frames para la prueba de rendimiento")
        
        # Prueba de formatos de códec
        print("\n-- Prueba de formatos de códec --")
        
        codecs = [
            ('MJPG', 'Motion JPEG'),
            ('YUY2', 'YUY2'),
            ('NV12', 'NV12'),
            ('H264', 'H.264'),
            ('IYUV', 'IYUV'),
            ('RGB3', 'RGB')
        ]
        
        for codec, name in codecs:
            codec_value = cv2.VideoWriter_fourcc(*codec)
            cap.set(cv2.CAP_PROP_FOURCC, codec_value)
            actual_codec = int(cap.get(cv2.CAP_PROP_FOURCC))
            
            # Convertir a texto
            actual_codec_str = ""
            for i in range(4):
                actual_codec_str += chr(actual_codec & 0xFF)
                actual_codec >>= 8
            
            print(f"Intentando establecer {codec} ({name}): {'✅ Éxito' if actual_codec_str == codec else f'❌ Actual: {actual_codec_str}'}")
        
        # Prueba de resoluciones
        print("\n-- Prueba de resoluciones --")
        
        resolutions = [
            (320, 240, "320x240"),
            (640, 480, "640x480"),
            (800, 600, "800x600"),
            (1280, 720, "1280x720"),
            (1920, 1080, "1920x1080")
        ]
        
        for width, height, name in resolutions:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            print(f"Intentando establecer {name}: {'✅ Éxito' if actual_width == width and actual_height == height else f'❌ Actual: {actual_width}x{actual_height}'}")
        
        cap.release()
        
        print(f"\n=== FIN DE LA INFORMACIÓN DE CÁMARA {camera_index} CON BACKEND {name} ===\n")
    
    return best_backend

def test_mediapipe_detection(camera_index, backend=None):
    """
    Prueba las capacidades de detección de MediaPipe
    """
    try:
        import mediapipe as mp
        
        print(f"\n=== PRUEBA DE MEDIAPIPE EN CÁMARA {camera_index} ===")
        
        # Inicializar MediaPipe Face Detection
        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils
        
        # Inicializar MediaPipe Hands
        mp_hands = mp.solutions.hands
        
        # Abrir cámara
        if backend is None:
            cap = cv2.VideoCapture(camera_index)
        else:
            cap = cv2.VideoCapture(camera_index, backend)
        
        if not cap.isOpened():
            print(f"❌ No se pudo abrir la cámara para pruebas de MediaPipe")
            return
        
        # Establecer resolución óptima para detección
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Crear ventana para mostrar resultados
        cv2.namedWindow("MediaPipe Tests", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("MediaPipe Tests", 800, 600)
        
        # Inicializar detectores
        with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
            with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
                
                # Contadores de detección
                frames_processed = 0
                faces_detected = 0
                hands_detected = 0
                
                print("Ejecutando prueba de MediaPipe... Presiona 'q' para salir")
                
                # 5 segundos de prueba
                start_time = time.time()
                while time.time() - start_time < 5:
                    ret, frame = cap.read()
                    if not ret:
                        print("❌ Error al leer frame")
                        break
                    
                    frames_processed += 1
                    
                    # Convertir a RGB para MediaPipe
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Procesar con detectores
                    face_results = face_detection.process(rgb_frame)
                    hands_results = hands.process(rgb_frame)
                    
                    # Verificar detecciones
                    if face_results.detections:
                        faces_detected += 1
                        
                        # Dibujar detecciones
                        for detection in face_results.detections:
                            mp_drawing.draw_detection(frame, detection)
                    
                    if hands_results.multi_hand_landmarks:
                        hands_detected += 1
                        
                        # Dibujar landmarks de manos
                        for hand_landmarks in hands_results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Mostrar información en la imagen
                    cv2.putText(frame, f"Frames: {frames_processed}", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Caras: {faces_detected}", (10, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Manos: {hands_detected}", (10, 90), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Mostrar resultado
                    cv2.imshow("MediaPipe Tests", frame)
                    
                    # Salir con 'q'
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Resultados
                total_time = time.time() - start_time
                print(f"\n-- Resultados de la prueba de MediaPipe --")
                print(f"Tiempo total: {total_time:.2f} segundos")
                print(f"Frames procesados: {frames_processed}")
                print(f"FPS promedio: {frames_processed / total_time:.2f}")
                print(f"Caras detectadas: {faces_detected}/{frames_processed} ({faces_detected/frames_processed*100:.2f}%)")
                print(f"Manos detectadas: {hands_detected}/{frames_processed} ({hands_detected/frames_processed*100:.2f}%)")
                
                # Guardar una captura final
                ret, frame = cap.read()
                if ret:
                    try:
                        save_dir = "camera_diagnostics"
                        if not os.path.exists(save_dir):
                            os.makedirs(save_dir)
                        
                        filename = f"{save_dir}/mediapipe_test_camera_{camera_index}.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"✅ Imagen final guardada como {filename}")
                    except Exception as e:
                        print(f"❌ Error al guardar imagen final: {e}")
                
                cap.release()
                cv2.destroyAllWindows()
        
        print(f"=== FIN DE LA PRUEBA DE MEDIAPIPE EN CÁMARA {camera_index} ===\n")
        
    except ImportError:
        print("❌ MediaPipe no está instalado. Instálalo con: pip install mediapipe")
    except Exception as e:
        print(f"❌ Error durante la prueba de MediaPipe: {e}")
        import traceback
        traceback.print_exc()

def test_dlib_detection(camera_index, backend=None):
    """
    Prueba las capacidades de detección de Dlib/face_recognition
    """
    try:
        import face_recognition
        
        print(f"\n=== PRUEBA DE FACE_RECOGNITION EN CÁMARA {camera_index} ===")
        
        # Abrir cámara
        if backend is None:
            cap = cv2.VideoCapture(camera_index)
        else:
            cap = cv2.VideoCapture(camera_index, backend)
        
        if not cap.isOpened():
            print(f"❌ No se pudo abrir la cámara para pruebas de face_recognition")
            return
        
        # Establecer resolución
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Crear ventana para mostrar resultados
        cv2.namedWindow("Face Recognition Tests", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Face Recognition Tests", 800, 600)
        
        # Contadores
        frames_processed = 0
        faces_detected = 0
        total_landmarks = 0
        
        print("Ejecutando prueba de face_recognition... Presiona 'q' para salir")
        
        # 5 segundos de prueba
        start_time = time.time()
        while time.time() - start_time < 5:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error al leer frame")
                break
            
            frames_processed += 1
            
            # Procesar frame con face_recognition
            # Reducir escala para mejor rendimiento
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            
            # Convertir a RGB para face_recognition
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Encontrar todas las caras en el frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            
            if face_locations:
                faces_detected += 1
                
                # Intentar obtener landmarks faciales
                face_landmarks_list = face_recognition.face_landmarks(rgb_small_frame, face_locations)
                total_landmarks += len(face_landmarks_list)
                
                # Dibujar cajas de caras
                for (top, right, bottom, left) in face_locations:
                    # Escalar coordenadas
                    top *= 2
                    right *= 2
                    bottom *= 2
                    left *= 2
                    
                    # Dibujar caja
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Dibujar landmarks
                for face_landmarks in face_landmarks_list:
                    # Escalar coordenadas
                    for feature, points in face_landmarks.items():
                        for point in points:
                            scaled_point = (point[0] * 2, point[1] * 2)
                            cv2.circle(frame, scaled_point, 2, (0, 0, 255), -1)
            
            # Mostrar información en la imagen
            cv2.putText(frame, f"Frames: {frames_processed}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Caras: {faces_detected}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Mostrar resultado
            cv2.imshow("Face Recognition Tests", frame)
            
            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Resultados
        total_time = time.time() - start_time
        print(f"\n-- Resultados de la prueba de face_recognition --")
        print(f"Tiempo total: {total_time:.2f} segundos")
        print(f"Frames procesados: {frames_processed}")
        print(f"FPS promedio: {frames_processed / total_time:.2f}")
        print(f"Caras detectadas: {faces_detected}/{frames_processed} ({faces_detected/frames_processed*100:.2f}%)")
        print(f"Landmarks faciales detectados: {total_landmarks}")
        
        # Guardar una captura final
        ret, frame = cap.read()
        if ret:
            try:
                save_dir = "camera_diagnostics"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                
                filename = f"{save_dir}/face_recognition_test_camera_{camera_index}.jpg"
                cv2.imwrite(filename, frame)
                print(f"✅ Imagen final guardada como {filename}")
            except Exception as e:
                print(f"❌ Error al guardar imagen final: {e}")
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"=== FIN DE LA PRUEBA DE FACE_RECOGNITION EN CÁMARA {camera_index} ===\n")
        
    except ImportError:
        print("❌ face_recognition no está instalado. Instálalo con: pip install face-recognition")
    except Exception as e:
        print(f"❌ Error durante la prueba de face_recognition: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Función principal para el diagnóstico
    """
    print("="*50)
    print("HERRAMIENTA DE DIAGNÓSTICO DE CÁMARA PARA ADAI")
    print("="*50)
    print("\nEste programa analiza las cámaras disponibles y su compatibilidad")
    print("con las bibliotecas de visión por computadora utilizadas en ADAI.\n")
    
    # Información del sistema
    print("=== INFORMACIÓN DEL SISTEMA ===")
    print(f"Sistema Operativo: {sys.platform}")
    print(f"Versión de Python: {sys.version}")
    print(f"Versión de OpenCV: {cv2.__version__}")
    
    try:
        import mediapipe
        print(f"Versión de MediaPipe: {mediapipe.__version__}")
    except ImportError:
        print("MediaPipe: No instalado")
    
    try:
        import face_recognition
        print(f"face_recognition: Instalado")
    except ImportError:
        print("face_recognition: No instalado")
    
    # Buscar todas las cámaras disponibles
    print("\n=== BÚSQUEDA DE CÁMARAS DISPONIBLES ===")
    available_cameras = []
    
    for i in range(10):  # Probar índices del 0 al 9
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Cámara encontrada en índice {i}")
                available_cameras.append(i)
            cap.release()
    
    if not available_cameras:
        print("❌ No se encontraron cámaras disponibles.")
        return
    
    print(f"Se encontraron {len(available_cameras)} cámaras: {available_cameras}")
    
    # Analizar cada cámara encontrada
    best_backends = []
    for camera_index in available_cameras:
        best_backend = print_camera_info(camera_index)
        if best_backend:
            best_backends.append((camera_index, best_backend))
    
    # Ejecutar pruebas de detección para cada cámara 
    for camera_index in available_cameras:
        backend_to_use = None
        backend_name = "Default"
        
        # Buscar el mejor backend para esta cámara
        for cam_idx, (backend, name) in best_backends:
            if cam_idx == camera_index:
                backend_to_use = backend
                backend_name = name
                break
        
        print(f"\nEjecutando pruebas de detección para cámara {camera_index} con backend {backend_name}")
        
        # Prueba MediaPipe
        test_mediapipe_detection(camera_index, backend_to_use)
        
        # Prueba face_recognition
        test_dlib_detection(camera_index, backend_to_use)
    
    print("\n=== DIAGNÓSTICO COMPLETO ===")
    print("El diagnóstico ha terminado. Los resultados y capturas se han guardado en la carpeta 'camera_diagnostics'.")
    print("Esta información puede ayudar a determinar la mejor configuración para tu webcam.")

if __name__ == "__main__":
    main()