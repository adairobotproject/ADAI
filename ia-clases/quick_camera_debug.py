#!/usr/bin/env python3
"""
Debug Rápido de Cámara con Detección de Alumnos
===============================================

Script simple para debuggear rápidamente la cámara y la detección de alumnos.
Ideal para pruebas rápidas y verificación de funcionamiento.
"""

import cv2
import numpy as np
import time
import os
import sys

def quick_camera_test(camera_index=0):
    """
    Prueba rápida de la cámara
    """
    print(f"🔧 Probando cámara {camera_index}...")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir la cámara {camera_index}")
        return False
    
    # Configurar resolución
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("✅ Cámara abierta correctamente")
    print(f"Resolución: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    
    # Probar lectura de frames
    frames_read = 0
    start_time = time.time()
    
    print("📹 Probando lectura de frames... (presiona 'q' para salir)")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error al leer frame")
            break
        
        frames_read += 1
        
        # Mostrar información en el frame
        cv2.putText(frame, f"Frame: {frames_read}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Tiempo: {time.time() - start_time:.1f}s", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Quick Camera Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    elapsed_time = time.time() - start_time
    fps = frames_read / elapsed_time if elapsed_time > 0 else 0
    
    print(f"\n📊 Resultados:")
    print(f"Frames leídos: {frames_read}")
    print(f"Tiempo: {elapsed_time:.2f}s")
    print(f"FPS real: {fps:.2f}")
    
    cap.release()
    cv2.destroyAllWindows()
    return True

def quick_face_detection_test(camera_index=0, duration=10):
    """
    Prueba rápida de detección facial
    """
    print(f"🧠 Probando detección facial...")
    
    try:
        import face_recognition
    except ImportError:
        print("❌ face_recognition no está instalado")
        return False
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir la cámara {camera_index}")
        return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    faces_detected = 0
    frames_processed = 0
    start_time = time.time()
    
    print(f"🔍 Detectando caras durante {duration} segundos... (presiona 'q' para salir)")
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frames_processed += 1
        
        # Reducir escala para mejor rendimiento
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detectar caras
        face_locations = face_recognition.face_locations(rgb_small_frame)
        
        if face_locations:
            faces_detected += 1
            
            # Dibujar cajas en el frame original
            for (top, right, bottom, left) in face_locations:
                # Escalar coordenadas
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Cara", (left, top - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Mostrar información
        cv2.putText(frame, f"Frames: {frames_processed}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Caras: {faces_detected}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Face Detection Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    elapsed_time = time.time() - start_time
    detection_rate = faces_detected / frames_processed if frames_processed > 0 else 0
    fps = frames_processed / elapsed_time if elapsed_time > 0 else 0
    
    print(f"\n📊 Resultados de detección:")
    print(f"Frames procesados: {frames_processed}")
    print(f"Caras detectadas: {faces_detected}")
    print(f"Tasa de detección: {detection_rate:.2%}")
    print(f"FPS: {fps:.2f}")
    
    cap.release()
    cv2.destroyAllWindows()
    return True

def quick_student_recognition_test(camera_index=0, duration=15):
    """
    Prueba rápida de reconocimiento de alumnos
    """
    print(f"👨‍🎓 Probando reconocimiento de alumnos...")
    
    try:
        import face_recognition
    except ImportError:
        print("❌ face_recognition no está instalado")
        return False
    
    # Cargar caras conocidas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    faces_dir = os.path.join(script_dir, "faces")
    
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
                    print(f"✅ Cargada cara: {name}")
                except Exception as e:
                    print(f"❌ Error al cargar {filename}: {e}")
    
    if not known_face_encodings:
        print("⚠️ No se encontraron caras conocidas")
        print("💡 Usa el script principal para crear caras de prueba")
        return False
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir la cámara {camera_index}")
        return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    students_recognized = 0
    frames_processed = 0
    recognized_students = set()
    start_time = time.time()
    
    print(f"🔍 Reconociendo alumnos durante {duration} segundos... (presiona 'q' para salir)")
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frames_processed += 1
        
        # Reducir escala para procesamiento
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detectar caras
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Comparar con caras conocidas
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            name = "Desconocido"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                students_recognized += 1
                recognized_students.add(name)
            
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
        
        # Mostrar información
        cv2.putText(frame, f"Frames: {frames_processed}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Reconocidos: {students_recognized}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Student Recognition Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    elapsed_time = time.time() - start_time
    recognition_rate = students_recognized / frames_processed if frames_processed > 0 else 0
    fps = frames_processed / elapsed_time if elapsed_time > 0 else 0
    
    print(f"\n📊 Resultados de reconocimiento:")
    print(f"Frames procesados: {frames_processed}")
    print(f"Alumnos reconocidos: {students_recognized}")
    print(f"Tasa de reconocimiento: {recognition_rate:.2%}")
    print(f"Alumnos identificados: {', '.join(recognized_students)}")
    print(f"FPS: {fps:.2f}")
    
    cap.release()
    cv2.destroyAllWindows()
    return True

def main():
    """
    Función principal
    """
    print("🔍 DEBUG RÁPIDO DE CÁMARA CON DETECCIÓN DE ALUMNOS")
    print("=" * 50)
    
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
        print("⚠️ face_recognition no está instalado")
    
    # Menú simple
    print("\n📋 OPCIONES:")
    print("1. Prueba rápida de cámara")
    print("2. Prueba de detección facial")
    print("3. Prueba de reconocimiento de alumnos")
    print("4. Todas las pruebas")
    print("5. Salir")
    
    while True:
        try:
            choice = input("\nSelecciona una opción (1-5): ").strip()
            
            if choice == "1":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                quick_camera_test(camera_index)
                break
                
            elif choice == "2":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                duration = int(input("Duración en segundos (10): ") or "10")
                quick_face_detection_test(camera_index, duration)
                break
                
            elif choice == "3":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                duration = int(input("Duración en segundos (15): ") or "15")
                quick_student_recognition_test(camera_index, duration)
                break
                
            elif choice == "4":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                print("\n🔧 Ejecutando todas las pruebas...")
                
                print("\n1️⃣ Prueba de cámara:")
                quick_camera_test(camera_index)
                
                print("\n2️⃣ Prueba de detección facial:")
                quick_face_detection_test(camera_index, 10)
                
                print("\n3️⃣ Prueba de reconocimiento de alumnos:")
                quick_student_recognition_test(camera_index, 15)
                
                print("\n✅ Todas las pruebas completadas")
                break
                
            elif choice == "5":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida. Intenta de nuevo.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 