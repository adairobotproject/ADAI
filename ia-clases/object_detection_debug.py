#!/usr/bin/env python3
"""
Debug de Detección de Objetos y Alumnos
=======================================

Script especializado para debuggear la detección de objetos geométricos
(círculos, triángulos, X) y alumnos en el sistema ADAI.

Funcionalidades:
- Detección de objetos geométricos (círculos, triángulos, X) SOLO dentro de hojas naranjas
- Detección y reconocimiento de alumnos
- Análisis de rendimiento en tiempo real
- Guardado de resultados y capturas
- Interfaz visual con cajas de detección
"""

import cv2
import numpy as np
import time
import os
import sys
import json
from datetime import datetime
from typing import List, Tuple, Optional, Dict
import math

# Configuración de rutas
script_dir = os.path.dirname(os.path.abspath(__file__))
faces_dir = os.path.join(script_dir, "faces")
debug_dir = os.path.join(script_dir, "debug_camera")

# Crear directorios necesarios
for directory in [faces_dir, debug_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

class ObjectDetectionDebugger:
    """
    Clase principal para debuggear la detección de objetos y alumnos
    """
    
    def __init__(self):
        self.camera_index = 0
        self.cap = None
        self.is_running = False
        self.debug_data = {
            "camera_info": {},
            "object_detection": {},
            "student_recognition": {},
            "performance_metrics": {}
        }
        
        # Parámetros de detección
        self.circle_params = {
            'min_radius': 20,
            'max_radius': 100,
            'param1': 50,
            'param2': 30
        }
        
        self.triangle_params = {
            'min_area': 500,
            'max_area': 10000,
            'epsilon_factor': 0.02
        }
        
        self.x_detection_params = {
            'min_line_length': 50,
            'max_line_gap': 10,
            'threshold': 50
        }
        
        # Parámetros para detección de hoja naranja
        self.orange_detection_params = {
            'lower_orange': np.array([5, 50, 50]),    # HSV lower bound para naranja
            'upper_orange': np.array([15, 255, 255]),  # HSV upper bound para naranja
            'min_area': 1000,  # Área mínima para considerar una hoja naranja
            'blur_kernel': 5   # Kernel para blur
        }
        
    def initialize_camera(self, camera_index: int = 0):
        """
        Inicializa la cámara
        """
        print(f"🔧 Inicializando cámara {camera_index}...")
        
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            print(f"❌ No se pudo abrir la cámara {camera_index}")
            return False
        
        # Configurar resolución óptima para detección
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.camera_index = camera_index
        
        print(f"✅ Cámara {camera_index} inicializada correctamente")
        return True
    
    def detect_orange_sheets(self, frame):
        """
        Detecta hojas naranjas en el frame
        Retorna: lista de contornos de hojas naranjas
        """
        # Convertir a HSV para mejor detección de color
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Aplicar blur para reducir ruido
        blurred = cv2.GaussianBlur(hsv, (self.orange_detection_params['blur_kernel'], 
                                         self.orange_detection_params['blur_kernel']), 0)
        
        # Crear máscara para color naranja
        mask = cv2.inRange(blurred, 
                          self.orange_detection_params['lower_orange'],
                          self.orange_detection_params['upper_orange'])
        
        # Operaciones morfológicas para limpiar la máscara
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos por área mínima
        orange_sheets = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.orange_detection_params['min_area']:
                orange_sheets.append(contour)
        
        return orange_sheets, mask
    
    def detect_circles(self, frame, orange_sheets):
        """
        Detecta círculos SOLO dentro de hojas naranjas
        """
        circles = []
        
        for sheet_contour in orange_sheets:
            # Crear máscara para la hoja naranja actual
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [sheet_contour], 255)
            
            # Aplicar máscara al frame
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
            
            # Convertir a escala de grises para detección de círculos
            gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            
            # Detectar círculos
            detected_circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=50,
                param1=self.circle_params['param1'],
                param2=self.circle_params['param2'],
                minRadius=self.circle_params['min_radius'],
                maxRadius=self.circle_params['max_radius']
            )
            
            if detected_circles is not None:
                detected_circles = np.uint16(np.around(detected_circles))
                
                for circle in detected_circles[0, :]:
                    x, y, r = circle
                    # Verificar que el círculo esté dentro de la hoja naranja
                    if cv2.pointPolygonTest(sheet_contour, (x, y), False) >= 0:
                        circles.append({
                            'center': (x, y),
                            'radius': r,
                            'sheet_contour': sheet_contour
                        })
        
        return circles
    
    def detect_triangles(self, frame, orange_sheets):
        """
        Detecta triángulos SOLO dentro de hojas naranjas
        """
        triangles = []
        
        for sheet_contour in orange_sheets:
            # Crear máscara para la hoja naranja actual
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [sheet_contour], 255)
            
            # Aplicar máscara al frame
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
            
            # Aplicar umbral adaptativo
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if (self.triangle_params['min_area'] < area < self.triangle_params['max_area']):
                    # Aproximar el contorno a un polígono
                    epsilon = self.triangle_params['epsilon_factor'] * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # Verificar si es un triángulo (3 vértices)
                    if len(approx) == 3:
                        # Verificar que el centro del triángulo esté dentro de la hoja naranja
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            
                            if cv2.pointPolygonTest(sheet_contour, (cx, cy), False) >= 0:
                                triangles.append({
                                    'contour': contour,
                                    'approx': approx,
                                    'center': (cx, cy),
                                    'sheet_contour': sheet_contour
                                })
        
        return triangles
    
    def detect_x_marks(self, frame, orange_sheets):
        """
        Detecta marcas X SOLO dentro de hojas naranjas
        """
        x_marks = []
        
        for sheet_contour in orange_sheets:
            # Crear máscara para la hoja naranja actual
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [sheet_contour], 255)
            
            # Aplicar máscara al frame
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar líneas
            lines = cv2.HoughLinesP(
                gray,
                rho=1,
                theta=np.pi/180,
                threshold=self.x_detection_params['threshold'],
                minLineLength=self.x_detection_params['min_line_length'],
                maxLineGap=self.x_detection_params['max_line_gap']
            )
            
            if lines is not None:
                # Agrupar líneas que forman X
                for i, line1 in enumerate(lines):
                    x1, y1, x2, y2 = line1[0]
                    
                    # Verificar que el centro de la línea esté dentro de la hoja naranja
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    if cv2.pointPolygonTest(sheet_contour, (center_x, center_y), False) >= 0:
                        for j, line2 in enumerate(lines[i+1:], i+1):
                            x3, y3, x4, y4 = line2[0]
                            
                            # Verificar que el centro de la segunda línea esté dentro de la hoja naranja
                            center_x2 = (x3 + x4) // 2
                            center_y2 = (y3 + y4) // 2
                            
                            if cv2.pointPolygonTest(sheet_contour, (center_x2, center_y2), False) >= 0:
                                # Calcular ángulo entre las líneas
                                angle1 = math.atan2(y2 - y1, x2 - x1)
                                angle2 = math.atan2(y4 - y3, x4 - x3)
                                angle_diff = abs(angle1 - angle2)
                                
                                # Normalizar ángulo
                                if angle_diff > np.pi:
                                    angle_diff = 2 * np.pi - angle_diff
                                
                                # Verificar si las líneas se cruzan y forman una X (ángulo cercano a 90°)
                                if 0.7 < angle_diff < 1.4:  # Aproximadamente 40° a 80°
                                    # Calcular punto de intersección
                                    intersection = self.line_intersection((x1, y1), (x2, y2), (x3, y3), (x4, y4))
                                    
                                    if intersection is not None:
                                        ix, iy = intersection
                                        # Verificar que la intersección esté dentro de la hoja naranja
                                        if cv2.pointPolygonTest(sheet_contour, (int(ix), int(iy)), False) >= 0:
                                            x_marks.append({
                                                'line1': (x1, y1, x2, y2),
                                                'line2': (x3, y3, x4, y4),
                                                'intersection': (int(ix), int(iy)),
                                                'sheet_contour': sheet_contour
                                            })
        
        return x_marks
    
    def line_intersection(self, p1, p2, p3, p4):
        """
        Calcula el punto de intersección entre dos líneas
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if denominator == 0:
            return None
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        
        if 0 <= t <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return (x, y)
        
        return None
    
    def detect_students(self, frame):
        """
        Detecta y reconoce alumnos en el frame
        """
        try:
            import face_recognition
        except ImportError:
            return []
        
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
                    except Exception as e:
                        print(f"❌ Error al cargar {filename}: {e}")
        
        detected_students = []
        
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
            
            # Escalar coordenadas
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            detected_students.append((name, (left, top, right, bottom)))
        
        return detected_students
    
    def draw_detection_boxes(self, frame, detections):
        """
        Dibuja cajas de detección en el frame
        """
        # Dibujar hojas naranjas
        if 'orange_sheets' in detections:
            for sheet_contour in detections['orange_sheets']:
                cv2.drawContours(frame, [sheet_contour], -1, (0, 165, 255), 2)  # Naranja
                # Calcular centro para texto
                M = cv2.moments(sheet_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.putText(frame, "Hoja Naranja", (cx - 50, cy), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        # Dibujar círculos
        for circle in detections['circles']:
            x, y = circle['center']
            r = circle['radius']
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), 3)
            cv2.putText(frame, "Circulo", (x - 30, y - r - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Dibujar triángulos
        for triangle in detections['triangles']:
            cx, cy = triangle['center']
            approx = triangle['approx']
            cv2.drawContours(frame, [approx], 0, (255, 0, 0), 2)
            cv2.circle(frame, (cx, cy), 3, (255, 0, 0), -1)
            cv2.putText(frame, "Triangulo", (cx - 30, cy - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Dibujar X marks
        for x_mark in detections['x_marks']:
            line1 = x_mark['line1']
            line2 = x_mark['line2']
            intersection = x_mark['intersection']
            
            x1, y1, x2, y2 = line1
            x3, y3, x4, y4 = line2
            
            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.line(frame, (x3, y3), (x4, y4), (0, 0, 255), 2)
            cv2.circle(frame, intersection, 3, (0, 0, 255), -1)
            cv2.putText(frame, "X", (intersection[0] - 10, intersection[1] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Dibujar alumnos
        for name, (left, top, right, bottom) in detections['students']:
            color = (0, 255, 0) if name != "Desconocido" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def test_object_detection(self, duration: int = 15):
        """
        Prueba la detección de objetos y alumnos
        """
        print(f"🔍 Probando detección de objetos y alumnos...")
        
        results = {
            "frames_processed": 0,
            "circles_detected": 0,
            "triangles_detected": 0,
            "x_marks_detected": 0,
            "students_detected": 0,
            "avg_processing_time": 0.0,
            "errors": []
        }
        
        start_time = time.time()
        processing_times = []
        
        # Crear ventana
        cv2.namedWindow("Object Detection Debug", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Object Detection Debug", 800, 600)
        
        print(f"🔍 Detectando objetos durante {duration} segundos... (presiona 'q' para salir)")
        
        while time.time() - start_time < duration:
            ret, frame = self.cap.read()
            if not ret:
                results["errors"].append("Error al leer frame")
                continue
            
            frame_start = time.time()
            results["frames_processed"] += 1
            
            try:
                # Detectar hojas naranjas
                orange_sheets, _ = self.detect_orange_sheets(frame)
                
                # Detectar objetos dentro de hojas naranjas
                circles = self.detect_circles(frame, orange_sheets)
                triangles = self.detect_triangles(frame, orange_sheets)
                x_marks = self.detect_x_marks(frame, orange_sheets)
                students = self.detect_students(frame)
                
                # Contar detecciones
                if circles:
                    results["circles_detected"] += len(circles)
                if triangles:
                    results["triangles_detected"] += len(triangles)
                if x_marks:
                    results["x_marks_detected"] += len(x_marks)
                if students:
                    results["students_detected"] += len(students)
                
                # Preparar detecciones para dibujar
                detections = {
                    'orange_sheets': orange_sheets,
                    'circles': circles,
                    'triangles': triangles,
                    'x_marks': x_marks,
                    'students': students
                }
                
                # Dibujar cajas de detección
                self.draw_detection_boxes(frame, detections)
                
                processing_time = time.time() - frame_start
                processing_times.append(processing_time)
                
                # Mostrar información en el frame
                cv2.putText(frame, f"Frames: {results['frames_processed']}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Circulos: {len(circles)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Triangulos: {len(triangles)}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(frame, f"X Marks: {len(x_marks)}", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Alumnos: {len(students)}", (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, f"Tiempo: {processing_time:.3f}s", (10, 180), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow("Object Detection Debug", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except Exception as e:
                results["errors"].append(f"Error en procesamiento: {str(e)}")
        
        # Calcular métricas
        total_time = time.time() - start_time
        if results["frames_processed"] > 0:
            results["avg_processing_time"] = np.mean(processing_times) if processing_times else 0
            results["fps"] = results["frames_processed"] / total_time
        
        cv2.destroyAllWindows()
        return results
    
    def adjust_detection_parameters(self):
        """
        Permite ajustar los parámetros de detección en tiempo real
        """
        print("🔧 Ajustando parámetros de detección...")
        
        # Crear ventanas de trackbars
        cv2.namedWindow("Circle Parameters", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Triangle Parameters", cv2.WINDOW_NORMAL)
        cv2.namedWindow("X Detection Parameters", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Orange Sheet Parameters", cv2.WINDOW_NORMAL)
        
        # Trackbars para círculos
        cv2.createTrackbar("Min Radius", "Circle Parameters", self.circle_params['min_radius'], 100, lambda x: setattr(self.circle_params, 'min_radius', x))
        cv2.createTrackbar("Max Radius", "Circle Parameters", self.circle_params['max_radius'], 200, lambda x: setattr(self.circle_params, 'max_radius', x))
        cv2.createTrackbar("Param1", "Circle Parameters", self.circle_params['param1'], 100, lambda x: setattr(self.circle_params, 'param1', x))
        cv2.createTrackbar("Param2", "Circle Parameters", self.circle_params['param2'], 100, lambda x: setattr(self.circle_params, 'param2', x))
        
        # Trackbars para triángulos
        cv2.createTrackbar("Min Area", "Triangle Parameters", self.triangle_params['min_area'], 2000, lambda x: setattr(self.triangle_params, 'min_area', x))
        cv2.createTrackbar("Max Area", "Triangle Parameters", self.triangle_params['max_area'], 20000, lambda x: setattr(self.triangle_params, 'max_area', x))
        cv2.createTrackbar("Epsilon Factor", "Triangle Parameters", int(self.triangle_params['epsilon_factor'] * 1000), 100, lambda x: setattr(self.triangle_params, 'epsilon_factor', x/1000))
        
        # Trackbars para X detection
        cv2.createTrackbar("Min Line Length", "X Detection Parameters", self.x_detection_params['min_line_length'], 200, lambda x: setattr(self.x_detection_params, 'min_line_length', x))
        cv2.createTrackbar("Max Line Gap", "X Detection Parameters", self.x_detection_params['max_line_gap'], 50, lambda x: setattr(self.x_detection_params, 'max_line_gap', x))
        cv2.createTrackbar("Threshold", "X Detection Parameters", self.x_detection_params['threshold'], 200, lambda x: setattr(self.x_detection_params, 'threshold', x))
        
        # Trackbars para detección de hojas naranjas
        cv2.createTrackbar("Min Area", "Orange Sheet Parameters", self.orange_detection_params['min_area'], 5000, lambda x: setattr(self.orange_detection_params, 'min_area', x))
        cv2.createTrackbar("Blur Kernel", "Orange Sheet Parameters", self.orange_detection_params['blur_kernel'], 15, lambda x: setattr(self.orange_detection_params, 'blur_kernel', x if x % 2 == 1 else x + 1))
        
        print("Ajusta los parámetros en las ventanas y presiona 'q' para salir")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Detectar hojas naranjas
            orange_sheets, _ = self.detect_orange_sheets(frame)
            
            # Detectar objetos con parámetros actuales
            circles = self.detect_circles(frame, orange_sheets)
            triangles = self.detect_triangles(frame, orange_sheets)
            x_marks = self.detect_x_marks(frame, orange_sheets)
            students = self.detect_students(frame)
            
            detections = {
                'orange_sheets': orange_sheets,
                'circles': circles,
                'triangles': triangles,
                'x_marks': x_marks,
                'students': students
            }
            
            # Dibujar detecciones
            self.draw_detection_boxes(frame, detections)
            
            # Mostrar información
            cv2.putText(frame, f"Hojas Naranjas: {len(orange_sheets)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            cv2.putText(frame, f"Circulos: {len(circles)}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Triangulos: {len(triangles)}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(frame, f"X Marks: {len(x_marks)}", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Alumnos: {len(students)}", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow("Object Detection Debug", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
    
    def run_comprehensive_debug(self, camera_index: int = 0, duration: int = 15):
        """
        Ejecuta un debug completo de detección de objetos y alumnos
        """
        print("="*60)
        print("🔍 DEBUG COMPLETO DE DETECCIÓN DE OBJETOS Y ALUMNOS")
        print("="*60)
        
        # Inicializar cámara
        if not self.initialize_camera(camera_index):
            print("❌ No se pudo inicializar la cámara")
            return
        
        # Información de la cámara
        print("\n📊 INFORMACIÓN DE LA CÁMARA")
        print("-" * 30)
        ret, frame = self.cap.read()
        if ret:
            print(f"Resolución: {frame.shape[1]}x{frame.shape[0]}")
            print(f"Canales: {frame.shape[2]}")
        
        # Prueba de detección de objetos
        print(f"\n🔍 PRUEBA DE DETECCIÓN DE OBJETOS ({duration}s)")
        print("-" * 40)
        results = self.test_object_detection(duration)
        self.debug_data["object_detection"] = results
        
        print(f"Frames procesados: {results['frames_processed']}")
        print(f"Círculos detectados: {results['circles_detected']}")
        print(f"Triángulos detectados: {results['triangles_detected']}")
        print(f"X marks detectados: {results['x_marks_detected']}")
        print(f"Alumnos detectados: {results['students_detected']}")
        print(f"Tiempo promedio: {results['avg_processing_time']:.3f}s")
        print(f"FPS: {results.get('fps', 0):.2f}")
        
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
        results_file = os.path.join(debug_dir, f"object_detection_results_{timestamp}.json")
        
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
        
        object_results = self.debug_data.get("object_detection", {})
        if object_results:
            print(f"🔍 Detección de Objetos:")
            print(f"   Círculos detectados: {object_results.get('circles_detected', 0)}")
            print(f"   Triángulos detectados: {object_results.get('triangles_detected', 0)}")
            print(f"   X marks detectados: {object_results.get('x_marks_detected', 0)}")
            print(f"   Alumnos detectados: {object_results.get('students_detected', 0)}")
            print(f"   FPS: {object_results.get('fps', 0):.2f}")
        
        print("\n✅ Debug completado. Revisa los resultados guardados para más detalles.")

def main():
    """
    Función principal
    """
    print("🔍 DEBUG DE DETECCIÓN DE OBJETOS Y ALUMNOS")
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
        print("⚠️ face_recognition no está instalado. La detección de alumnos no estará disponible.")
    
    # Crear debugger
    debugger = ObjectDetectionDebugger()
    
    # Menú de opciones
    print("\n📋 OPCIONES DE DEBUG:")
    print("1. Debug completo de objetos y alumnos")
    print("2. Solo detección de objetos")
    print("3. Ajustar parámetros de detección")
    print("4. Salir")
    
    while True:
        try:
            choice = input("\nSelecciona una opción (1-4): ").strip()
            
            if choice == "1":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                duration = int(input("Duración de pruebas en segundos (15): ") or "15")
                debugger.run_comprehensive_debug(camera_index, duration)
                break
                
            elif choice == "2":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                duration = int(input("Duración en segundos (15): ") or "15")
                if debugger.initialize_camera(camera_index):
                    results = debugger.test_object_detection(duration)
                    print(f"\n🔍 RESULTADOS DE DETECCIÓN:")
                    for key, value in results.items():
                        print(f"{key}: {value}")
                break
                
            elif choice == "3":
                camera_index = int(input("Índice de cámara (0): ") or "0")
                if debugger.initialize_camera(camera_index):
                    debugger.adjust_detection_parameters()
                break
                
            elif choice == "4":
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