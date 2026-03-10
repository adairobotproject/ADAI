"""
Módulo de funciones de códigos QR para ADAI
==========================================

Contiene todas las funciones relacionadas con:
- Mostrar códigos QR de diagnóstico
- Mostrar códigos QR de examen final
- Interfaz visual para códigos QR
"""

import cv2
import numpy as np
import time
from .config import COLORS, WINDOW_CONFIG

def show_diagnostic_qr(qr_image_path, display_time=15):
    """
    Muestra un código QR con diseño estético mejorado para evaluación diagnóstica
    
    Args:
        qr_image_path (str): Ruta al archivo de imagen del QR
        display_time (int): Tiempo en segundos para mostrar el QR
        
    Returns:
        bool: True si se mostró exitosamente, False en caso contrario
    """
    try:
        print("📱 Mostrando código QR para evaluación diagnóstica...")
        
        # Cargar imagen del QR
        qr_image = cv2.imread(qr_image_path)
        
        if qr_image is None:
            print(f"❌ Error: No se pudo cargar la imagen QR desde {qr_image_path}")
            return False
        
        # Configuración de diseño
        window_width = WINDOW_CONFIG['qr_diagnostic']['width']
        window_height = WINDOW_CONFIG['qr_diagnostic']['height']
        
        # Crear ventana
        cv2.namedWindow("Evaluación Diagnóstica", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Evaluación Diagnóstica", window_width, window_height)
        
        # Colores elegantes
        colors = COLORS['qr_diagnostic']
        bg_color = colors['bg_color']
        header_color = colors['header_color']
        text_color = colors['text_color']
        accent_color = colors['accent_color']
        
        # Obtener dimensiones del QR
        original_height, original_width = qr_image.shape[:2]
        
        # Tamaño del QR (más grande y centrado)
        qr_size = 350
        qr_resized = cv2.resize(qr_image, (qr_size, qr_size))
        
        # Crear lienzo principal
        canvas = np.full((window_height, window_width, 3), bg_color, dtype=np.uint8)
        
        # === HEADER ELEGANTE ===
        header_height = 120
        cv2.rectangle(canvas, (0, 0), (window_width, header_height), header_color, -1)
        
        # Título principal
        title = "ADAI - ASISTENTE DOCENTE ANDROIDE"
        title_font_scale = 1.1
        title_thickness = 3
        (title_w, title_h), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, title_font_scale, title_thickness)
        title_x = (window_width - title_w) // 2
        cv2.putText(canvas, title, (title_x, 45), cv2.FONT_HERSHEY_SIMPLEX, title_font_scale, (255, 255, 255), title_thickness)
        
        # Subtítulo
        subtitle = "Evaluacion Diagnostica Previa"
        subtitle_font_scale = 0.8
        subtitle_thickness = 2
        (subtitle_w, subtitle_h), _ = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, subtitle_font_scale, subtitle_thickness)
        subtitle_x = (window_width - subtitle_w) // 2
        cv2.putText(canvas, subtitle, (subtitle_x, 85), cv2.FONT_HERSHEY_SIMPLEX, subtitle_font_scale, (255, 255, 255), subtitle_thickness)
        
        # === ÁREA DEL QR CON MARCO ELEGANTE ===
        qr_area_y = header_height + 40
        qr_x = (window_width - qr_size) // 2
        qr_y = qr_area_y + 20
        
        # Marco con sombra para el QR
        shadow_offset = 8
        shadow_color = (200, 200, 200)
        
        # Sombra
        cv2.rectangle(canvas, 
                     (qr_x + shadow_offset, qr_y + shadow_offset), 
                     (qr_x + qr_size + shadow_offset, qr_y + qr_size + shadow_offset), 
                     shadow_color, -1)
        
        # Marco blanco
        margin = 15
        cv2.rectangle(canvas, 
                     (qr_x - margin, qr_y - margin), 
                     (qr_x + qr_size + margin, qr_y + qr_size + margin), 
                     (255, 255, 255), -1)
        
        # Insertar QR
        canvas[qr_y:qr_y + qr_size, qr_x:qr_x + qr_size] = qr_resized
        
        # === INSTRUCCIONES ELEGANTES ===
        instructions_y = qr_y + qr_size + 60
        
        # Instrucción principal
        instruction_main = "Escanea el codigo QR con tu dispositivo movil"
        instruction_sub = "Completa la evaluacion antes de que inicie la clase"
        
        # Instrucción principal
        main_font_scale = 0.9
        main_thickness = 2
        (main_w, main_h), _ = cv2.getTextSize(instruction_main, cv2.FONT_HERSHEY_SIMPLEX, main_font_scale, main_thickness)
        main_x = (window_width - main_w) // 2
        cv2.putText(canvas, instruction_main, (main_x, instructions_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, main_font_scale, text_color, main_thickness)
        
        # Instrucción secundaria
        sub_font_scale = 0.7
        sub_thickness = 2
        (sub_w, sub_h), _ = cv2.getTextSize(instruction_sub, cv2.FONT_HERSHEY_SIMPLEX, sub_font_scale, sub_thickness)
        sub_x = (window_width - sub_w) // 2
        cv2.putText(canvas, instruction_sub, (sub_x, instructions_y + 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, sub_font_scale, text_color, sub_thickness)
        
        # === ÁREA DE TIEMPO CON DISEÑO ELEGANTE ===
        start_time = time.time()
        
        print(f"📱 Mostrando QR por {display_time} segundos...")
        print("💡 Presiona 'q' para continuar antes de tiempo")
        
        while True:
            # Crear copia del canvas
            display_canvas = canvas.copy()
            
            # Calcular tiempo restante
            elapsed_time = time.time() - start_time
            remaining_time = max(0, display_time - int(elapsed_time))
            
            # === CONTADOR ELEGANTE ===
            counter_area_y = window_height - 80
            counter_width = 300
            counter_height = 50
            counter_x = (window_width - counter_width) // 2
            
            # Fondo del contador con bordes redondeados (simulado)
            cv2.rectangle(display_canvas, 
                         (counter_x, counter_area_y), 
                         (counter_x + counter_width, counter_area_y + counter_height), 
                         (255, 255, 255), -1)
            
            # Borde del contador
            cv2.rectangle(display_canvas, 
                         (counter_x, counter_area_y), 
                         (counter_x + counter_width, counter_area_y + counter_height), 
                         accent_color, 2)
            
            # Texto del contador
            if remaining_time > 10:
                counter_color = text_color
                counter_text = f"Tiempo restante: {remaining_time}s"
            elif remaining_time > 5:
                counter_color = (230, 126, 34)  # Naranja
                counter_text = f"Tiempo restante: {remaining_time}s"
            else:
                counter_color = accent_color  # Rojo
                counter_text = f"FINALIZANDO EN: {remaining_time}s"
            
            counter_font_scale = 0.8
            counter_thickness = 2
            (counter_w, counter_h), _ = cv2.getTextSize(counter_text, cv2.FONT_HERSHEY_SIMPLEX, counter_font_scale, counter_thickness)
            counter_text_x = counter_x + (counter_width - counter_w) // 2
            counter_text_y = counter_area_y + (counter_height + counter_h) // 2
            
            cv2.putText(display_canvas, counter_text, (counter_text_x, counter_text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, counter_font_scale, counter_color, counter_thickness)
            
            # === BARRA DE PROGRESO ===
            progress_y = counter_area_y - 30
            progress_width = 400
            progress_height = 8
            progress_x = (window_width - progress_width) // 2
            
            # Fondo de la barra
            cv2.rectangle(display_canvas, 
                         (progress_x, progress_y), 
                         (progress_x + progress_width, progress_y + progress_height), 
                         (220, 220, 220), -1)
            
            # Progreso actual
            progress_percentage = (display_time - remaining_time) / display_time
            progress_current_width = int(progress_width * progress_percentage)
            
            if remaining_time > 10:
                progress_color = header_color
            elif remaining_time > 5:
                progress_color = (230, 126, 34)  # Naranja
            else:
                progress_color = accent_color  # Rojo
            
            if progress_current_width > 0:
                cv2.rectangle(display_canvas, 
                             (progress_x, progress_y), 
                             (progress_x + progress_current_width, progress_y + progress_height), 
                             progress_color, -1)
            
            # === INSTRUCCIÓN DE ESCAPE ===
            escape_text = "Presiona 'Q' para continuar"
            escape_font_scale = 0.6
            escape_thickness = 1
            (escape_w, escape_h), _ = cv2.getTextSize(escape_text, cv2.FONT_HERSHEY_SIMPLEX, escape_font_scale, escape_thickness)
            escape_x = window_width - escape_w - 20
            escape_y = window_height - 20
            cv2.putText(display_canvas, escape_text, (escape_x, escape_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, escape_font_scale, (150, 150, 150), escape_thickness)
            
            # Mostrar imagen
            cv2.imshow("Evaluación Diagnóstica", display_canvas)
            
            # Verificar teclas y tiempo
            key = cv2.waitKey(1000) & 0xFF
            if key == ord('q') or key == ord('Q') or elapsed_time >= display_time:
                break
        
        # Animación de cierre suave
        for alpha in range(10, 0, -1):
            fade_canvas = display_canvas.copy()
            overlay = np.full_like(fade_canvas, bg_color, dtype=np.uint8)
            faded = cv2.addWeighted(fade_canvas, alpha/10.0, overlay, 1-alpha/10.0, 0)
            cv2.imshow("Evaluación Diagnóstica", faded)
            cv2.waitKey(100)
        
        # Cerrar ventana
        cv2.destroyWindow("Evaluación Diagnóstica")
        print("✅ QR mostrado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error mostrando QR: {e}")
        return False

def show_final_exam_qr(qr_image_path, display_time=20):
    """
    Muestra el código QR del examen final con diseño estético
    
    Args:
        qr_image_path (str): Ruta al archivo de imagen del QR del examen
        display_time (int): Tiempo en segundos para mostrar el QR (por defecto 20s)
        
    Returns:
        bool: True si se mostró exitosamente, False en caso contrario
    """
    try:
        print("📋 Mostrando código QR para examen final...")
        
        # Cargar imagen del QR
        qr_image = cv2.imread(qr_image_path)
        
        if qr_image is None:
            print(f"❌ Error: No se pudo cargar la imagen QR desde {qr_image_path}")
            return False
        
        # Configuración de diseño para examen final
        window_width = WINDOW_CONFIG['qr_exam']['width']
        window_height = WINDOW_CONFIG['qr_exam']['height']
        
        # Crear ventana
        cv2.namedWindow("Examen Final", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Examen Final", window_width, window_height)
        
        # Colores para examen final (más serios/académicos)
        colors = COLORS['qr_exam']
        bg_color = colors['bg_color']
        header_color = colors['header_color']
        text_color = colors['text_color']
        accent_color = colors['accent_color']
        success_color = colors['success_color']
        
        # Obtener dimensiones del QR
        original_height, original_width = qr_image.shape[:2]
        
        # Tamaño del QR
        qr_size = 350
        qr_resized = cv2.resize(qr_image, (qr_size, qr_size))
        
        # Crear lienzo principal
        canvas = np.full((window_height, window_width, 3), bg_color, dtype=np.uint8)
        
        # === HEADER PARA EXAMEN FINAL ===
        header_height = 140
        cv2.rectangle(canvas, (0, 0), (window_width, header_height), header_color, -1)
        
        # Título principal
        title = "EXAMEN FINAL - ROBOTS MEDICOS"
        title_font_scale = 1.2
        title_thickness = 3
        (title_w, title_h), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, title_font_scale, title_thickness)
        title_x = (window_width - title_w) // 2
        cv2.putText(canvas, title, (title_x, 50), cv2.FONT_HERSHEY_SIMPLEX, title_font_scale, (255, 255, 255), title_thickness)
        
        # Subtítulo
        subtitle = "Evaluacion Post-Clase con ADAI"
        subtitle_font_scale = 0.9
        subtitle_thickness = 2
        (subtitle_w, subtitle_h), _ = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, subtitle_font_scale, subtitle_thickness)
        subtitle_x = (window_width - subtitle_w) // 2
        cv2.putText(canvas, subtitle, (subtitle_x, 85), cv2.FONT_HERSHEY_SIMPLEX, subtitle_font_scale, (255, 255, 255), subtitle_thickness)
        
        # Línea decorativa
        line_y = 110
        cv2.line(canvas, (100, line_y), (window_width - 100, line_y), (255, 255, 255), 3)
        
        # === ÁREA DEL QR CON MARCO ACADÉMICO ===
        qr_area_y = header_height + 40
        qr_x = (window_width - qr_size) // 2
        qr_y = qr_area_y + 20
        
        # Marco con sombra elegante
        shadow_offset = 10
        shadow_color = (180, 180, 180)
        
        # Sombra
        cv2.rectangle(canvas, 
                     (qr_x + shadow_offset, qr_y + shadow_offset), 
                     (qr_x + qr_size + shadow_offset, qr_y + qr_size + shadow_offset), 
                     shadow_color, -1)
        
        # Marco dorado/académico
        margin = 20
        cv2.rectangle(canvas, 
                     (qr_x - margin, qr_y - margin), 
                     (qr_x + qr_size + margin, qr_y + qr_size + margin), 
                     (255, 255, 255), -1)
        
        # Borde dorado
        cv2.rectangle(canvas, 
                     (qr_x - margin, qr_y - margin), 
                     (qr_x + qr_size + margin, qr_y + qr_size + margin), 
                     (0, 215, 255), 4)  # Gold color
        
        # Insertar QR
        canvas[qr_y:qr_y + qr_size, qr_x:qr_x + qr_size] = qr_resized
        
        # === INSTRUCCIONES DEL EXAMEN ===
        instructions_y = qr_y + qr_size + 70
        
        # Instrucción principal
        main_instruction = "Escanea el codigo QR para acceder al examen final"
        main_font_scale = 1.0
        main_thickness = 2
        (main_w, main_h), _ = cv2.getTextSize(main_instruction, cv2.FONT_HERSHEY_SIMPLEX, main_font_scale, main_thickness)
        main_x = (window_width - main_w) // 2
        cv2.putText(canvas, main_instruction, (main_x, instructions_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, main_font_scale, text_color, main_thickness)
        
        # Instrucción secundaria
        sub_instruction = "Demuestra lo que aprendiste sobre robotica medica"
        sub_font_scale = 0.8
        sub_thickness = 2
        (sub_w, sub_h), _ = cv2.getTextSize(sub_instruction, cv2.FONT_HERSHEY_SIMPLEX, sub_font_scale, sub_thickness)
        sub_x = (window_width - sub_w) // 2
        cv2.putText(canvas, sub_instruction, (sub_x, instructions_y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, sub_font_scale, text_color, sub_thickness)
        
        # === MENSAJE MOTIVACIONAL ===
        motivational_msg = "¡Has completado la clase con ADAI exitosamente!"
        motivational_font_scale = 0.7
        motivational_thickness = 2
        (motivational_w, motivational_h), _ = cv2.getTextSize(motivational_msg, cv2.FONT_HERSHEY_SIMPLEX, motivational_font_scale, motivational_thickness)
        motivational_x = (window_width - motivational_w) // 2
        cv2.putText(canvas, motivational_msg, (motivational_x, instructions_y + 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, motivational_font_scale, success_color, motivational_thickness)
        
        # === CONTADOR Y BARRA DE PROGRESO ===
        start_time = time.time()
        
        print(f"📋 Mostrando QR de examen final por {display_time} segundos...")
        print("💡 Presiona 'q' para continuar antes de tiempo")
        
        while True:
            # Crear copia del canvas
            display_canvas = canvas.copy()
            
            # Calcular tiempo restante
            elapsed_time = time.time() - start_time
            remaining_time = max(0, display_time - int(elapsed_time))
            
            # === CONTADOR ELEGANTE PARA EXAMEN ===
            counter_area_y = window_height - 100
            counter_width = 350
            counter_height = 60
            counter_x = (window_width - counter_width) // 2
            
            # Fondo del contador
            cv2.rectangle(display_canvas, 
                         (counter_x, counter_area_y), 
                         (counter_x + counter_width, counter_area_y + counter_height), 
                         (255, 255, 255), -1)
            
            # Borde del contador (cambia color según tiempo)
            if remaining_time > 15:
                counter_border_color = success_color
                counter_text = f"Tiempo para el examen: {remaining_time}s"
                counter_color = text_color
            elif remaining_time > 5:
                counter_border_color = (255, 165, 0)  # Orange
                counter_text = f"Tiempo restante: {remaining_time}s"
                counter_color = (255, 140, 0)
            else:
                counter_border_color = accent_color
                counter_text = f"CERRANDO EN: {remaining_time}s"
                counter_color = accent_color
            
            cv2.rectangle(display_canvas, 
                         (counter_x, counter_area_y), 
                         (counter_x + counter_width, counter_area_y + counter_height), 
                         counter_border_color, 3)
            
            # Texto del contador
            counter_font_scale = 0.9
            counter_thickness = 2
            (counter_w, counter_h), _ = cv2.getTextSize(counter_text, cv2.FONT_HERSHEY_SIMPLEX, counter_font_scale, counter_thickness)
            counter_text_x = counter_x + (counter_width - counter_w) // 2
            counter_text_y = counter_area_y + (counter_height + counter_h) // 2
            
            cv2.putText(display_canvas, counter_text, (counter_text_x, counter_text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, counter_font_scale, counter_color, counter_thickness)
            
            # === BARRA DE PROGRESO ===
            progress_y = counter_area_y - 40
            progress_width = 500
            progress_height = 12
            progress_x = (window_width - progress_width) // 2
            
            # Fondo de la barra
            cv2.rectangle(display_canvas, 
                         (progress_x, progress_y), 
                         (progress_x + progress_width, progress_y + progress_height), 
                         (220, 220, 220), -1)
            
            # Progreso actual
            progress_percentage = (display_time - remaining_time) / display_time
            progress_current_width = int(progress_width * progress_percentage)
            
            if remaining_time > 15:
                progress_color = success_color
            elif remaining_time > 5:
                progress_color = (255, 165, 0)  # Orange
            else:
                progress_color = accent_color
            
            if progress_current_width > 0:
                cv2.rectangle(display_canvas, 
                             (progress_x, progress_y), 
                             (progress_x + progress_current_width, progress_y + progress_height), 
                             progress_color, -1)
            
            # === INSTRUCCIÓN DE ESCAPE ===
            escape_text = "Presiona 'Q' para finalizar la clase"
            escape_font_scale = 0.6
            escape_thickness = 1
            (escape_w, escape_h), _ = cv2.getTextSize(escape_text, cv2.FONT_HERSHEY_SIMPLEX, escape_font_scale, escape_thickness)
            escape_x = window_width - escape_w - 20
            escape_y = window_height - 15
            cv2.putText(display_canvas, escape_text, (escape_x, escape_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, escape_font_scale, (120, 120, 120), escape_thickness)
            
            # Mostrar imagen
            cv2.imshow("Examen Final", display_canvas)
            
            # Verificar teclas y tiempo
            key = cv2.waitKey(1000) & 0xFF
            if key == ord('q') or key == ord('Q') or elapsed_time >= display_time:
                break
        
        # Animación de cierre suave
        for alpha in range(10, 0, -1):
            fade_canvas = display_canvas.copy()
            overlay = np.full_like(fade_canvas, bg_color, dtype=np.uint8)
            faded = cv2.addWeighted(fade_canvas, alpha/10.0, overlay, 1-alpha/10.0, 0)
            cv2.imshow("Examen Final", faded)
            cv2.waitKey(100)
        
        # Cerrar ventana
        cv2.destroyWindow("Examen Final")
        print("✅ QR de examen final mostrado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error mostrando QR de examen final: {e}")
        return False
