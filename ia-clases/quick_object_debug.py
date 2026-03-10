#!/usr/bin/env python3
"""
Debug Rápido de Detección de Objetos con Hojas Naranjas
=======================================================

Script simplificado para debuggear rápidamente la detección de objetos geométricos
(círculos, triángulos, X) SOLO dentro de hojas naranjas.

Funcionalidades:
- Detección de hojas naranjas
- Detección de objetos geométricos dentro de hojas naranjas
- Pruebas individuales y combinadas
- Interfaz visual simple
"""

import cv2
import numpy as np
import time
import os
import sys
from typing import List, Tuple, Optional, Dict
import math

# Configuración de rutas
script_dir = os.path.dirname(os.path.abspath(__file__))
faces_dir = os.path.join(script_dir, "faces")

# Crear directorios necesarios
if not os.path.exists(faces_dir):
    os.makedirs(faces_dir)

def detect_orange_sheets(frame):
    """
    Detecta hojas naranjas en el frame
    """
    # Parámetros para detección de hoja naranja
    orange_params = {
        'lower_orange': np.array([5, 50, 50]),    # HSV lower bound para naranja
        'upper_orange': np.array([15, 255, 255]),  # HSV upper bound para naranja
        'min_area': 1000,  # Área mínima para considerar una hoja naranja
        'blur_kernel': 5   # Kernel para blur
    }
    
    # Convertir a HSV para mejor detección de color
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Aplicar blur para reducir ruido
    blurred = cv2.GaussianBlur(hsv, (orange_params['blur_kernel'], 
                                     orange_params['blur_kernel']), 0)
    
    # Crear máscara para color naranja
    mask = cv2.inRange(blurred, 
                      orange_params['lower_orange'],
                      orange_params['upper_orange'])
    
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
        if area > orange_params['min_area']:
            orange_sheets.append(contour)
    
    return orange_sheets, mask

def detect_circles_in_orange(frame, orange_sheets):
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
            param1=50,
            param2=30,
            minRadius=20,
            maxRadius=100
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

def detect_triangles_in_orange(frame, orange_sheets):
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
            
            if 500 < area < 10000:
                # Aproximar el contorno a un polígono
                epsilon = 0.02 * cv2.arcLength(contour, True)
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

def detect_x_marks_in_orange(frame, orange_sheets):
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
            threshold=50,
            minLineLength=50,
            maxLineGap=10
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
                                intersection = line_intersection((x1, y1), (x2, y2), (x3, y3), (x4, y4))
                                
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

def line_intersection(p1, p2, p3, p4):
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

def draw_detections(frame, orange_sheets, circles, triangles, x_marks):
    """
    Dibuja todas las detecciones en el frame
    """
    # Dibujar hojas naranjas
    for sheet_contour in orange_sheets:
        cv2.drawContours(frame, [sheet_contour], -1, (0, 165, 255), 2)  # Naranja
        # Calcular centro para texto
        M = cv2.moments(sheet_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(frame, "Hoja Naranja", (cx - 50, cy), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
    
    # Dibujar círculos
    for circle in circles:
        x, y = circle['center']
        r = circle['radius']
        cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
        cv2.circle(frame, (x, y), 2, (0, 255, 0), 3)
        cv2.putText(frame, "Circulo", (x - 30, y - r - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Dibujar triángulos
    for triangle in triangles:
        cx, cy = triangle['center']
        approx = triangle['approx']
        cv2.drawContours(frame, [approx], 0, (255, 0, 0), 2)
        cv2.circle(frame, (cx, cy), 3, (255, 0, 0), -1)
        cv2.putText(frame, "Triangulo", (cx - 30, cy - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    # Dibujar X marks
    for x_mark in x_marks:
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

def quick_orange_sheet_detection(camera_index=0, duration=10):
    """
    Prueba rápida de detección de hojas naranjas
    """
    print(f"🔍 Probando detección de hojas naranjas...")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir la cámara {camera_index}")
        return
    
    start_time = time.time()
    sheets_detected = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Detectar hojas naranjas
        orange_sheets, mask = detect_orange_sheets(frame)
        
        if orange_sheets:
            sheets_detected += len(orange_sheets)
        
        # Dibujar hojas naranjas
        for sheet_contour in orange_sheets:
            cv2.drawContours(frame, [sheet_contour], -1, (0, 165, 255), 2)
        
        # Mostrar información
        cv2.putText(frame, f"Hojas Naranjas: {len(orange_sheets)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        
        cv2.imshow("Orange Sheet Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Hojas naranjas detectadas: {sheets_detected}")

def quick_circle_detection_in_orange(camera_index=0, duration=10):
    """
    Prueba rápida de detección de círculos dentro de hojas naranjas
    """
    print(f"🔍 Probando detección de círculos en hojas naranjas...")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir la cámara {camera_index}")
        return
    
    start_time = time.time()
    circles_detected = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Detectar hojas naranjas y círculos
        orange_sheets, _ = detect_orange_sheets(frame)
        circles = detect_circles_in_orange(frame, orange_sheets)
        
        if circles:
            circles_detected += len(circles)
        
        # Dibujar detecciones
        draw_detections(frame, orange_sheets, circles, [], [])
        
        # Mostrar información
        cv2.putText(frame, f"Hojas Naranjas: {len(orange_sheets)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        cv2.putText(frame, f"Circulos: {len(circles)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Circle Detection in Orange Sheets", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Círculos detectados: {circles_detected}")

def quick_triangle_detection_in_orange(camera_index=0, duration=10):
    """
    Prueba rápida de detección de triángulos dentro de hojas naranjas
    """
    print(f"🔍 Probando detección de triángulos en hojas naranjas...")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir la cámara {camera_index}")
        return
    
    start_time = time.time()
    triangles_detected = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Detectar hojas naranjas y triángulos
        orange_sheets, _ = detect_orange_sheets(frame)
        triangles = detect_triangles_in_orange(frame, orange_sheets)
        
        if triangles:
            triangles_detected += len(triangles)
        
        # Dibujar detecciones
        draw_detections(frame, orange_sheets, [], triangles, [])
        
        # Mostrar información
        cv2.putText(frame, f"Hojas Naranjas: {len(orange_sheets)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        cv2.putText(frame, f"Triangulos: {len(triangles)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        cv2.imshow("Triangle Detection in Orange Sheets", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Triángulos detectados: {triangles_detected}")

def quick_x_detection_in_orange(camera_index=0, duration=10):
    """
    Prueba rápida de detección de X marks dentro de hojas naranjas
    """
    print(f"🔍 Probando detección de X marks en hojas naranjas...")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir la cámara {camera_index}")
        return
    
    start_time = time.time()
    x_marks_detected = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Detectar hojas naranjas y X marks
        orange_sheets, _ = detect_orange_sheets(frame)
        x_marks = detect_x_marks_in_orange(frame, orange_sheets)
        
        if x_marks:
            x_marks_detected += len(x_marks)
        
        # Dibujar detecciones
        draw_detections(frame, orange_sheets, [], [], x_marks)
        
        # Mostrar información
        cv2.putText(frame, f"Hojas Naranjas: {len(orange_sheets)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        cv2.putText(frame, f"X Marks: {len(x_marks)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow("X Mark Detection in Orange Sheets", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ X marks detectados: {x_marks_detected}")

def quick_all_objects_detection_in_orange(camera_index=0, duration=15):
    """
    Prueba rápida de detección de todos los objetos dentro de hojas naranjas
    """
    print(f"🔍 Probando detección de todos los objetos en hojas naranjas...")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir la cámara {camera_index}")
        return
    
    start_time = time.time()
    total_detections = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Detectar hojas naranjas y todos los objetos
        orange_sheets, _ = detect_orange_sheets(frame)
        circles = detect_circles_in_orange(frame, orange_sheets)
        triangles = detect_triangles_in_orange(frame, orange_sheets)
        x_marks = detect_x_marks_in_orange(frame, orange_sheets)
        
        total_objects = len(circles) + len(triangles) + len(x_marks)
        if total_objects > 0:
            total_detections += total_objects
        
        # Dibujar todas las detecciones
        draw_detections(frame, orange_sheets, circles, triangles, x_marks)
        
        # Mostrar información
        cv2.putText(frame, f"Hojas Naranjas: {len(orange_sheets)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        cv2.putText(frame, f"Circulos: {len(circles)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Triangulos: {len(triangles)}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f"X Marks: {len(x_marks)}", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Total: {total_objects}", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("All Objects Detection in Orange Sheets", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Total de objetos detectados: {total_detections}")

def main():
    """
    Función principal con menú de opciones
    """
    print("="*60)
    print("🔍 DEBUG RÁPIDO DE DETECCIÓN DE OBJETOS EN HOJAS NARANJAS")
    print("="*60)
    print()
    print("Opciones disponibles:")
    print("1. Detectar hojas naranjas")
    print("2. Detectar círculos en hojas naranjas")
    print("3. Detectar triángulos en hojas naranjas")
    print("4. Detectar X marks en hojas naranjas")
    print("5. Detectar todos los objetos en hojas naranjas")
    print("6. Salir")
    print()
    
    while True:
        try:
            choice = input("Selecciona una opción (1-6): ").strip()
            
            if choice == '1':
                quick_orange_sheet_detection()
            elif choice == '2':
                quick_circle_detection_in_orange()
            elif choice == '3':
                quick_triangle_detection_in_orange()
            elif choice == '4':
                quick_x_detection_in_orange()
            elif choice == '5':
                quick_all_objects_detection_in_orange()
            elif choice == '6':
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