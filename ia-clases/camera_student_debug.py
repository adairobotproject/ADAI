#!/usr/bin/env python3
"""
Script de Debug para Cámara con Detección de Alumnos
====================================================

Este script está diseñado específicamente para debuggear la cámara
y la detección de alumnos en el sistema ADAI.

Funcionalidades:
- Diagnóstico completo de la cámara
- Pruebas de detección facial con face_recognition
- Pruebas de detección con MediaPipe
- Simulación de reconocimiento de alumnos
- Análisis de rendimiento en tiempo real
- Captura y guardado de imágenes de prueba
"""

import cv2
import numpy as np
import time
import os
import sys
import json
from datetime import datetime
from typing import List, Tuple, Optional, Dict
import threading

# Configuración de rutas
script_dir = os.path.dirname(os.path.abspath(__file__))
faces_dir = os.path.join(script_dir, "faces")
debug_dir = os.path.join(script_dir, "debug_camera")

# Crear directorios necesarios
for directory in [faces_dir, debug_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

class CameraStudentDebugger:
    """
    Clase principal para debuggear la cámara y detección de alumnos
    """
    
    def __init__(self):
        self.camera_index = 0
        self.camera_backend = None
        self.cap = None
        self.is_running = False
        self.debug_data = {
            "camera_info": {},
            "detection_tests": {},
            "performance_metrics": {},
            "student_recognition": {}
        }
        
    def initialize_camera(self, camera_index: int = 0, backend=None):
        """
        Inicializa la cámara con el backend especificado
        """
        print(f"🔧 Inicializando cámara {camera_index}...")
        
        if backend is None:
            self.cap = cv2.VideoCapture(camera_index)
        else:
            self.cap = cv2.VideoCapture(camera_index, backend)
        
        if not self.cap.isOpened():
            print(f"❌ No se pudo abrir la cámara {camera_index}")
            return False
        
        # Configurar resolución óptima para detección
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.camera_index = camera_index
        self.camera_backend = backend
        
        print(f"✅ Cámara {camera_index} inicializada correctamente")
        return True
    
    def get_camera_info(self) -> Dict:
        """
        Obtiene información detallada de la cámara
        """
        if not self.cap or not self.cap.isOpened():
            return {}
        
        info = {
            "index": self.camera_index,
            "backend": str(self.camera_backend) if self.camera_backend else "Default",
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "brightness": self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
            "contrast": self.cap.get(cv2.CAP_PROP_CONTRAST),
            "exposure": self.cap.get(cv2.CAP_PROP_EXPOSURE),
            "auto_exposure": self.cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        }
        
        # Probar lectura de frame
        ret, frame = self.cap.read()
        if ret:
            info["frame_shape"] = frame.shape
            info["frame_dtype"] = str(frame.dtype)
            info["frame_min"] = int(frame.min())
            info["frame_max"] = int(frame.max())
        
        return info
    
    def test_face_recognition_detection(self, duration: int = 10) -> Dict:
        """
        Prueba la detección facial usando face_recognition
        """
        print(f"🧠 Probando detección facial con face_recognition...")
        
        try:
            import face_recognition
        except ImportError:
            print("❌ face_recognition no está instalado")
            return {"error": "face_recognition no instalado"}
        
        results = {
            "frames_processed": 0,
            "faces_detected": 0,
            "detection_rate": 0.0,
            "avg_processing_time": 0.0,
            "errors": []
        }
        
        start_time = time.time()
        processing_times = []
        
        while time.time() - start_time < duration:
            ret, frame = self.cap.read()
            if not ret:
                results["errors"].append("Error al leer frame")
                continue
            
            frame_start = time.time()
            results["frames_processed"] += 1
            
            try:
                # Reducir escala para mejor rendimiento
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Detectar caras
                face_locations = face_recognition.face_locations(rgb_small_frame)
                
                if face_locations:
                    results["faces_detected"] += 1
                    
                    # Obtener encodings para reconocimiento
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    
                    # Dibujar cajas en el frame original
                    for (top, right, bottom, left) in face_locations:
                        # Escalar coordenadas
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4
                        
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(frame, "Cara Detectada", (left, top - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                processing_time = time.time() - frame_start
                processing_times.append(processing_time)
                
                # Mostrar frame con información
                cv2.putText(frame, f"Frames: {results['frames_processed']}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Caras: {results['faces_detected']}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Tiempo: {processing_time:.3f}s", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("Face Recognition Debug", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except Exception as e:
                results["errors"].append(f"Error en procesamiento: {str(e)}")
        
        # Calcular métricas
        total_time = time.time() - start_time
        if results["frames_processed"] > 0:
            results["detection_rate"] = results["faces_detected"] / results["frames_processed"]
            results["avg_processing_time"] = np.mean(processing_times) if processing_times else 0
            results["fps"] = results["frames_processed"] / total_time
        
        cv2.destroyAllWindows()
        return results
    
    def test_mediapipe_detection(self, duration: int = 10) -> Dict:
        """
        Prueba la detección usando MediaPipe
        """
        print(f"🎯 Probando detección con MediaPipe...")
        
        try:
            import mediapipe as mp
        except ImportError:
            print("❌ MediaPipe no está instalado")
            return {"error": "MediaPipe no instalado"}
        
        results = {
            "frames_processed": 0,
            "faces_detected": 0,
            "hands_detected": 0,
            "detection_rate": 0.0,
            "avg_processing_time": 0.0,
            "errors": []
        }
        
        # Inicializar MediaPipe
        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        
        start_time = time.time()
        processing_times = []
        
        with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
            with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
                
                while time.time() - start_time < duration:
                    ret, frame = self.cap.read()
                    if not ret:
                        results["errors"].append("Error al leer frame")
                        continue
                    
                    frame_start = time.time()
                    results["frames_processed"] += 1
                    
                    try:
                        # Convertir a RGB para MediaPipe
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Procesar con detectores
                        face_results = face_detection.process(rgb_frame)
                        hands_results = hands.process(rgb_frame)
                        
                        # Procesar detecciones de cara
                        if face_results.detections:
                            results["faces_detected"] += 1
                            for detection in face_results.detections:
                                mp_drawing.draw_detection(frame, detection)
                        
                        # Procesar detecciones de manos
                        if hands_results.multi_hand_landmarks:
                            results["hands_detected"] += 1
                            for hand_landmarks in hands_results.multi_hand_landmarks:
                                mp_drawing.draw_landmarks(
                                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        
                        processing_time = time.time() - frame_start
                        processing_times.append(processing_time)
                        
                        # Mostrar información
                        cv2.putText(frame, f"Frames: {results['frames_processed']}", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, f"Caras: {results['faces_detected']}", (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, f"Manos: {results['hands_detected']}", (10, 90), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, f"Tiempo: {processing_time:.3f}s", (10, 120), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        cv2.imshow("MediaPipe Debug", frame)
                        
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                            
                    except Exception as e:
                        results["errors"].append(f"Error en procesamiento: {str(e)}")
        
        # Calcular métricas
        total_time = time.time() - start_time
        if results["frames_processed"] > 0:
            results["detection_rate"] = (results["faces_detected"] + results["hands_detected"]) / results["frames_processed"]
            results["avg_processing_time"] = np.mean(processing_times) if processing_times else 0
            results["fps"] = results["frames_processed"] / total_time
        
        cv2.destroyAllWindows()
        return results
    
    def test_student_recognition(self, duration: int = 15) -> Dict:
        """
        Prueba el reconocimiento de alumnos específicos
        """
        print(f"👨‍🎓 Probando reconocimiento de alumnos...")
        
        try:
            import face_recognition
        except ImportError:
            print("❌ face_recognition no está instalado")
            return {"error": "face_recognition no instalado"}
        
        # Cargar caras conocidas
        known_face_encodings = []
        known_face_names = []
        
        if os.path.exists(faces_dir):
            for filename in os.listdir(faces_dir):
                if filename.endswith((".jpg", ".jpeg", ".png")):
                    name = os.path.splitext(filename)[0]
                    image_path = os.path.join(faces_dir, filename)
                    
                    try:
                        image = face_recognition.load_image_file(image_path)
                        encoding = face_recognition.face_encodings(image)[0]
                        known_face_encodings.append(encoding)
                        known_face_names.append(name)
                        print(f"✅ Cargada cara conocida: {name}")
                    except Exception as e:
                        print(f"❌ Error al cargar {filename}: {e}")
        
        if not known_face_encodings:
            print("⚠️ No se encontraron caras conocidas. Creando caras de prueba...")
            # Crear caras de prueba
            self.create_test_faces()
            return {"warning": "No hay caras conocidas, ejecuta el modo de captura"}
        
        results = {
            "frames_processed": 0,
            "faces_detected": 0,
            "students_recognized": 0,
            "recognition_rate": 0.0,
            "recognized_students": [],
            "avg_processing_time": 0.0,
            "errors": []
        }
        
        start_time = time.time()
        processing_times = []
        
        while time.time() - start_time < duration:
            ret, frame = self.cap.read()
            if not ret:
                results["errors"].append("Error al leer frame")
                continue
            
            frame_start = time.time()
            results["frames_processed"] += 1
            
            try:
                # Reducir escala para procesamiento
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Detectar caras
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                if face_locations:
                    results["faces_detected"] += 1
                    
                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        # Comparar con caras conocidas
                        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                        name = "Desconocido"
                        
                        if True in matches:
                            first_match_index = matches.index(True)
                            name = known_face_names[first_match_index]
                            results["students_recognized"] += 1
                            
                            if name not in results["recognized_students"]:
                                results["recognized_students"].append(name)
                        
                        # Escalar coordenadas para dibujar
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4
                        
                        # Dibujar caja y nombre
                        color = (0, 255, 0) if name != "Desconocido" else (0, 0, 255)
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        cv2.putText(frame, name, (left, top - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                processing_time = time.time() - frame_start
                processing_times.append(processing_time)
                
                # Mostrar información
                cv2.putText(frame, f"Frames: {results['frames_processed']}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Caras: {results['faces_detected']}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Reconocidos: {results['students_recognized']}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Tiempo: {processing_time:.3f}s", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("Student Recognition Debug", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except Exception as e:
                results["errors"].append(f"Error en procesamiento: {str(e)}")
        
        # Calcular métricas
        total_time = time.time() - start_time
        if results["frames_processed"] > 0:
            results["recognition_rate"] = results["students_recognized"] / results["frames_processed"]
            results["avg_processing_time"] = np.mean(processing_times) if processing_times else 0
            results["fps"] = results["frames_processed"] / total_time
        
        cv2.destroyAllWindows()
        return results
    
    def create_test_faces(self):
        """
        Crea caras de prueba para el debug
        """
        print("📸 Creando caras de prueba...")
        
        test_names = ["Estudiante_1", "Estudiante_2", "Estudiante_3"]
        
        for i, name in enumerate(test_names):
            print(f"Capturando cara para {name}...")
            print("Mira a la cámara y presiona 'c' para capturar, 'q' para cancelar")
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                cv2.putText(frame, f"Capturando: {name}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Presiona 'c' para capturar, 'q' para cancelar", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                cv2.imshow("Captura de Cara", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c'):
                    # Guardar cara
                    face_path = os.path.join(faces_dir, f"{name}.jpg")
                    cv2.imwrite(face_path, frame)
                    print(f"✅ Cara guardada para {name}")
                    break
                elif key == ord('q'):
                    print(f"❌ Cancelada captura para {name}")
                    break
        
        cv2.destroyAllWindows()
    
    def run_comprehensive_debug(self, camera_index: int = 0, duration: int = 10):
        """
        Ejecuta un debug completo de la cámara y detección de alumnos
        """
        print("="*60)
        print("🔍 DEBUG COMPLETO DE CÁMARA Y DETECCIÓN DE ALUMNOS")
        print("="*60)
        
        # Inicializar cámara
        if not self.initialize_camera(camera_index):
            print("❌ No se pudo inicializar la cámara")
            return
        
        # Información de la cámara
        print("\n📊 INFORMACIÓN DE LA CÁMARA")
        print("-" * 30)
        camera_info = self.get_camera_info()
        for key, value in camera_info.items():
            print(f"{key}: {value}")
        
        # Guardar información de la cámara
        self.debug_data["camera_info"] = camera_info
        
        # Prueba de detección facial
        print(f"\n🧠 PRUEBA DE DETECCIÓN FACIAL ({duration}s)")
        print("-" * 40)
        face_results = self.test_face_recognition_detection(duration)
        self.debug_data["detection_tests"]["face_recognition"] = face_results
        
        if "error" not in face_results:
            print(f"Frames procesados: {face_results['frames_processed']}")
            print(f"Caras detectadas: {face_results['faces_detected']}")
            print(f"Tasa de detección: {face_results['detection_rate']:.2%}")
            print(f"Tiempo promedio: {face_results['avg_processing_time']:.3f}s")
            print(f"FPS: {face_results.get('fps', 0):.2f}")
        
        # Prueba de MediaPipe
        print(f"\n🎯 PRUEBA DE MEDIAPIPE ({duration}s)")
        print("-" * 30)
        mediapipe_results = self.test_mediapipe_detection(duration)
        self.debug_data["detection_tests"]["mediapipe"] = mediapipe_results
        
        if "error" not in mediapipe_results:
            print(f"Frames procesados: {mediapipe_results['frames_processed']}")
            print(f"Caras detectadas: {mediapipe_results['faces_detected']}")
            print(f"Manos detectadas: {mediapipe_results['hands_detected']}")
            print(f"Tasa de detección: {mediapipe_results['detection_rate']:.2%}")
            print(f"Tiempo promedio: {mediapipe_results['avg_processing_time']:.3f}s")
            print(f"FPS: {mediapipe_results.get('fps', 0):.2f}")
        
        # Prueba de reconocimiento de alumnos
        print(f"\n👨‍🎓 PRUEBA DE RECONOCIMIENTO DE ALUMNOS ({duration + 5}s)")
        print("-" * 50)
        student_results = self.test_student_recognition(duration + 5)
        self.debug_data["student_recognition"] = student_results
        
        if "error" not in student_results and "warning" not in student_results:
            print(f"Frames procesados: {student_results['frames_processed']}")
            print(f"Caras detectadas: {student_results['faces_detected']}")
            print(f"Alumnos reconocidos: {student_results['students_recognized']}")
            print(f"Tasa de reconocimiento: {student_results['recognition_rate']:.2%}")
            print(f"Alumnos identificados: {', '.join(student_results['recognized_students'])}")
            print(f"Tiempo promedio: {student_results['avg_processing_time']:.3f}s")
            print(f"FPS: {student_results.get('fps', 0):.2f}")
        
        # Guardar resultados
        self.save_debug_results()
        
        # Mostrar resumen
        self.show_debug_summary()
        
        # Limpiar
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def save_debug_results(self):
        """
        Guarda los resultados del debug
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(debug_dir, f"debug_results_{timestamp}.json")
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.debug_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultados guardados en: {results_file}")
        except Exception as e:
            print(f"❌ Error al guardar resultados: {e}")
    
    def show_debug_summary(self):
        """
        Muestra un resumen del debug
        """
        print("\n" + "="*60)
        print("📋 RESUMEN DEL DEBUG")
        print("="*60)
        
        # Información de la cámara
        camera_info = self.debug_data.get("camera_info", {})
        if camera_info:
            print(f"📷 Cámara {camera_info.get('index', 'N/A')}")
            print(f"   Resolución: {camera_info.get('width', 'N/A')}x{camera_info.get('height', 'N/A')}")
            print(f"   FPS: {camera_info.get('fps', 'N/A')}")
        
        # Resultados de detección
        detection_tests = self.debug_data.get("detection_tests", {})
        
        if "face_recognition" in detection_tests:
            fr_results = detection_tests["face_recognition"]
            if "error" not in fr_results:
                print(f"🧠 Face Recognition:")
                print(f"   Tasa de detección: {fr_results.get('detection_rate', 0):.2%}")
                print(f"   FPS: {fr_results.get('fps', 0):.2f}")
        
        if "mediapipe" in detection_tests:
            mp_results = detection_tests["mediapipe"]
            if "error" not in mp_results:
                print(f"🎯 MediaPipe:")
                print(f"   Tasa de detección: {mp_results.get('detection_rate', 0):.2%}")
                print(f"   FPS: {mp_results.get('fps', 0):.2f}")
        
        # Resultados de reconocimiento de alumnos
        student_results = self.debug_data.get("student_recognition", {})
        if "error" not in student_results and "warning" not in student_results:
            print(f"👨‍🎓 Reconocimiento de Alumnos:")
            print(f"   Tasa de reconocimiento: {student_results.get('recognition_rate', 0):.2%}")
            print(f"   Alumnos identificados: {len(student_results.get('recognized_students', []))}")
        
        print("\n✅ Debug completado. Revisa los resultados guardados para más detalles.")

def main():
    """
    Función principal
    """
    print("🔍 SCRIPT DE DEBUG DE CÁMARA CON DETECCIÓN DE ALUMNOS")
    print("=" * 60)
    
    # Verificar dependencias
    print("🔧 Verificando dependencias...")
    
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV no está instalado")
        return
    
    try:
        import face_recognition
        print("✅ face_recognition instalado")
    except ImportError:
        print("⚠️ face_recognition no está instalado. Algunas funciones no estarán disponibles.")
    
    try:
        import mediapipe
        print("✅ MediaPipe instalado")
    except ImportError:
        print("⚠️ MediaPipe no está instalado. Algunas funciones no estarán disponibles.")
    
    # Crear debugger
    debugger = CameraStudentDebugger()
    
    # Menú de opciones
    print("\n📋 OPCIONES DE DEBUG:")
    print("1. Debug completo (recomendado)")
    print("2. Solo información de cámara")
    print("3. Solo prueba de detección facial")
    print("4. Solo prueba de MediaPipe")
    print("5. Solo prueba de reconocimiento de alumnos")
    print("6. Crear caras de prueba")
    print("7. Salir")
    
    while True:
        try:
            choice = input("\nSelecciona una opción (1-7): ").strip()
            
            if choice == "1":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                duration = int(input("Duración de pruebas en segundos (10): ") or "10")
                debugger.run_comprehensive_debug(camera_index, duration)
                break
                
            elif choice == "2":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                if debugger.initialize_camera(camera_index):
                    camera_info = debugger.get_camera_info()
                    print("\n📊 INFORMACIÓN DE LA CÁMARA:")
                    for key, value in camera_info.items():
                        print(f"{key}: {value}")
                break
                
            elif choice == "3":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                duration = int(input("Duración en segundos (10): ") or "10")
                if debugger.initialize_camera(camera_index):
                    results = debugger.test_face_recognition_detection(duration)
                    print(f"\n🧠 RESULTADOS DE DETECCIÓN FACIAL:")
                    for key, value in results.items():
                        print(f"{key}: {value}")
                break
                
            elif choice == "4":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                duration = int(input("Duración en segundos (10): ") or "10")
                if debugger.initialize_camera(camera_index):
                    results = debugger.test_mediapipe_detection(duration)
                    print(f"\n🎯 RESULTADOS DE MEDIAPIPE:")
                    for key, value in results.items():
                        print(f"{key}: {value}")
                break
                
            elif choice == "5":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                duration = int(input("Duración en segundos (15): ") or "15")
                if debugger.initialize_camera(camera_index):
                    results = debugger.test_student_recognition(duration)
                    print(f"\n👨‍🎓 RESULTADOS DE RECONOCIMIENTO:")
                    for key, value in results.items():
                        print(f"{key}: {value}")
                break
                
            elif choice == "6":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                if debugger.initialize_camera(camera_index):
                    debugger.create_test_faces()
                break
                
            elif choice == "7":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida. Intenta de nuevo.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Limpiar
    if debugger.cap:
        debugger.cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 