import cv2
import face_recognition
import numpy as np
import pyttsx3
import speech_recognition as sr
import os
import fitz  # PyMuPDF
import openai
import time
import dill
import multiprocessing
from multiprocessing import Process, Value, Event
import mediapipe as mp
import pytesseract
import random
import threading
import msvcrt
import winsound
import time

# Set path to Tesseract executable for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ======================
#  CONFIGURACIÓN OPENAI
# ======================
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Get absolute path for the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
faces_dir = os.path.join(script_dir, "faces")
if not os.path.exists(faces_dir):
    os.makedirs(faces_dir)\
    
# ======================
#  RUTAS DE LOS QR
# ======================
QR_PATHS = {
    'diagnostic': os.path.join(script_dir, "RobotsMedicosExamen", "pruebadiagnosticaRobotsMedicos.jpeg"),
    'diagnostic_Exoesqueletos': os.path.join(script_dir, "ExoesqueletosExamen", "pruebadiagnosticaExoesqueletos.jpeg"),
    'diagnostic_IoMT': os.path.join(script_dir, "DesafiosIoMTExamen", "pruebadiagnosticaDesafiosIoMT.jpeg"),
    'final_examI': os.path.join(script_dir, "RobotsMedicosExamen", "RobotsMedicosExamenI.jpeg"),
    'final_examII': os.path.join(script_dir, "RobotsMedicosExamen", "RobotsMedicosExamenII.jpeg"),
    'final_examExoI': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenI.jpeg"),
    'final_examExoII': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenII.jpeg"),
    'final_examExoIII': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenIII.jpeg"),
    'final_examExoIV': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenIV.jpeg"),
    'final_examExoV': os.path.join(script_dir, "ExoesqueletosExamen", "ExoesqueletosExamenV.jpeg"),
    'final_examIoMT': os.path.join(script_dir, "DesafiosIoMTExamen", "DesafiosIoMTExamenI.png")

}

# ======================
#  BANCO DE PREGUNTAS
# ======================
QUESTION_BANK = [
    "El IoMT genera grandes volúmenes de datos. Verdadero o falso?",
    "La computación cuántica es relevante para la seguridad del IoMT. Verdadero o falso?",
    "El IoMP promueve estándares éticos para datos de pacientes. Verdadero o falso?",
    "Los dispositivos IoMT no necesitan eficiencia energética. Verdadero o falso?",
    "El IoMT solo se aplica en hospitales. Verdadero o falso?",
    "La pandemia de COVID-19 redujo el uso del IoMT. Verdadero o falso?",
    "Blockchain mejora la seguridad en el IoMT. Verdadero o falso?"
]

QUESTION_BANK_IoMT = [
    "El IoMT no genera grandes volúmenes de datos. Verdadero o falso?",
    "La computación cuántica es relevante para la seguridad del IoMT. Verdadero o falso?",
    "El IoMP promueve estándares éticos para datos de pacientes. Verdadero o falso?",
    "Los dispositivos IoMT no necesitan eficiencia energética. Verdadero o falso?",
    "El IoMT solo se aplica en hospitales. Verdadero o falso?",
    "La pandemia de COVID-19 redujo el uso del IoMT. Verdadero o falso?",
    "Blockchain mejora la seguridad en el IoMT. Verdadero o falso?"
]

def evaluate_student_answer(question, answer, context, student_name):
    """
    Función específica para evaluar respuestas de estudiantes
    Separada de ask_openai para evitar conflictos
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """Eres ADAI, un profesor robot amigable que evalúa respuestas de estudiantes sobre robótica médica. 
                
INSTRUCCIONES IMPORTANTES:
- NO uses asteriscos, guiones, viñetas, ni formato especial
- NO uses emojis ni símbolos especiales  
- Habla de manera natural como un profesor amigable
- Máximo 3 oraciones
- Si el estudiante dice "no sé", sé comprensivo y educativo
- NO digas palabras como "retroalimentación", "corrección", "evaluación"
- Responde como si estuvieras hablando directamente al estudiante"""},
                
                {"role": "user", "content": f"""Un estudiante llamado {student_name} respondió a la pregunta: "{question}"
                
Su respuesta fue: "{answer}"

Contexto del material de clase: {context[:1000]}...

Da una respuesta natural y educativa como profesor. Si la respuesta es incorrecta o es "no sé", corrige de manera amable pero sin usar palabras técnicas como "retroalimentación"."""}
            ]
        )
        
        # Limpiar respuesta de cualquier formato
        evaluation = response.choices[0].message.content
        evaluation = evaluation.replace("*", "").replace("**", "").replace("***", "")
        evaluation = evaluation.replace("- ", "").replace("• ", "")
        evaluation = evaluation.strip()
        
        return evaluation
        
    except Exception as e:
        print(f"❌ Error evaluando respuesta de {student_name}: {e}")
        # Respuesta de emergencia natural
        if "no sé" in answer.lower() or "no se" in answer.lower():
            return f"No hay problema, {student_name}. Estas son preguntas complejas sobre robótica médica. Continuemos con la clase."
        else:
            return f"Gracias por tu respuesta, {student_name}. Continuemos con la clase."

# ======================
#  CLASE CONTROLADOR DE PREGUNTAS
# ======================
class RandomQuestionManager:
    def __init__(self, students, question_bank=None):
        """
        Inicializa el gestor de preguntas aleatorias
        
        Args:
            students (list): Lista de estudiantes registrados
            question_bank (list): Banco de preguntas (opcional)
        """
        self.students = students.copy()
        self.question_bank = question_bank or QUESTION_BANK.copy()
        self.original_question_bank = QUESTION_BANK.copy()
        
        # Tracking de estudiantes y preguntas
        self.available_students = students.copy()
        self.used_questions = []
        self.student_question_history = {student: [] for student in students}
        
        # Estadísticas
        self.total_questions_asked = 0
        self.questions_per_student = {student: 0 for student in students}
        
        print(f"🎯 Gestor de preguntas inicializado:")
        print(f"   - {len(self.students)} estudiantes registrados")
        print(f"   - {len(self.question_bank)} preguntas disponibles")
    
    def reset_cycle_if_needed(self):
        """
        Reinicia el ciclo si todos los estudiantes ya fueron preguntados
        """
        if not self.available_students:
            print("🔄 Todos los estudiantes han sido preguntados. Reiniciando ciclo...")
            self.available_students = self.students.copy()
            return True
        return False
    
    def reset_questions_if_needed(self):
        """
        Reinicia el banco de preguntas si se agotaron
        """
        if not self.question_bank:
            print("🔄 Banco de preguntas agotado. Reiniciando...")
            self.question_bank = self.original_question_bank.copy()
            # Remover preguntas ya usadas en esta sesión para evitar repetición inmediata
            for used_q in self.used_questions[-10:]:  # Solo evitar las últimas 10
                if used_q in self.question_bank:
                    self.question_bank.remove(used_q)
            return True
        return False
    
    def select_random_student(self):
        """
        Selecciona un estudiante aleatorio que no haya sido preguntado en esta ronda
        
        Returns:
            tuple: (student_name, student_index) o (None, None) si no hay estudiantes
        """
        self.reset_cycle_if_needed()
        
        if not self.available_students:
            print("⚠️ No hay estudiantes disponibles para preguntas")
            return None, None
        
        # Seleccionar estudiante aleatorio
        selected_student = random.choice(self.available_students)
        student_index = self.students.index(selected_student)
        
        # Remover de disponibles
        self.available_students.remove(selected_student)
        
        print(f"🎯 Estudiante seleccionado: {selected_student} (posición {student_index + 1})")
        return selected_student, student_index
    
    def select_random_question(self):
        """
        Selecciona una pregunta aleatoria del banco
        
        Returns:
            str: Pregunta seleccionada o None si no hay preguntas
        """
        self.reset_questions_if_needed()
        
        if not self.question_bank:
            print("⚠️ No hay preguntas disponibles")
            return None
        
        # Seleccionar pregunta aleatoria
        selected_question = random.choice(self.question_bank)
        
        # Remover de banco para evitar repetición
        self.question_bank.remove(selected_question)
        self.used_questions.append(selected_question)
        
        print(f"❓ Pregunta seleccionada: {selected_question[:50]}...")
        return selected_question
    
    def conduct_random_question(self, engine, pdf_text):
        """
        Conduce una pregunta aleatoria completa - VERSIÓN TRADICIONAL
        
        Returns:
            bool: True si se completó exitosamente, False si hubo error
        """
        try:
            # Seleccionar estudiante y pregunta
            student_name, student_index = self.select_random_student()
            question = self.select_random_question()
            
            if not student_name or not question:
                print("⚠️ No se pudo realizar pregunta aleatoria")
                return False
            
            # Anunciar pregunta aleatoria
            announcement = f"Momento de verificación de aprendizaje. {student_name}, tienes una pregunta especial."
            speak_with_animation(engine, announcement)
            
            # Hacer la pregunta
            speak_with_animation(engine, question)
            
            # Escuchar respuesta
            print(f"🎤 Esperando respuesta de {student_name}...")
            answer = listen(timeout=15)  # Más tiempo para respuesta reflexiva
            
            # Procesar respuesta
            if answer and answer not in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""]:
                print(f"💬 Respuesta de {student_name}: {answer}")
                
                # Registrar en historial
                self.student_question_history[student_name].append({
                    'question': question,
                    'answer': answer,
                    'slide_number': None  # Se puede agregar después
                })
                self.questions_per_student[student_name] += 1
                self.total_questions_asked += 1
                
                # Evaluar respuesta con OpenAI
                try:
                    
                    evaluation = evaluate_student_answer(question, answer, pdf_text, student_name)
                    
                    # Dar retroalimentación
                    speak_with_animation(engine, evaluation)
                    
                    # Mensaje de continuación basado en la evaluación
                    if "excelente" in evaluation.lower() or "correcta" in evaluation.lower():
                        speak_with_animation(engine, f"¡Muy bien, {student_name}! Continuemos con la clase.")
                    else:
                        speak_with_animation(engine, f"Gracias por tu respuesta, {student_name}. Continuemos.")
                    
                except Exception as e:
                    print(f"❌ Error evaluando respuesta: {e}")
                    speak_with_animation(engine, f"Gracias por tu respuesta, {student_name}. Continuemos con la clase.")
                
            else:
                # No se obtuvo respuesta válida
                print(f"⚠️ No se obtuvo respuesta válida de {student_name}")
                speak_with_animation(engine, f"No hay problema, {student_name}. Continuemos con la clase.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en pregunta aleatoria: {e}")
            speak_with_animation(engine, "Continuemos con la clase.")
            return False
    
    def get_statistics(self):
        """
        Retorna estadísticas del sistema de preguntas
        """
        return {
            'total_questions': self.total_questions_asked,
            'questions_per_student': self.questions_per_student,
            'available_students': len(self.available_students),
            'available_questions': len(self.question_bank),
            'student_history': self.student_question_history
        }

# ===============================================
#  MOSTRAR CÓDIGO QR PARA EVALUACIÓN DIAGNÓSTICA
# ===============================================

def show_diagnostic_qr(qr_image_path, display_time=15):
    """
    Muestra un código QR con diseño estético mejorado
    """
    try:
        print("📱 Mostrando código QR para evaluación diagnóstica...")
        
        # Cargar imagen del QR
        qr_image = cv2.imread(qr_image_path)
        
        if qr_image is None:
            print(f"❌ Error: No se pudo cargar la imagen QR desde {qr_image_path}")
            return False
        
        # Configuración de diseño
        window_width = 1000
        window_height = 700
        
        # Crear ventana
        cv2.namedWindow("Evaluación Diagnóstica", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Evaluación Diagnóstica", window_width, window_height)
        
        # Colores elegantes
        bg_color = (245, 245, 245)  # Gris muy claro
        header_color = (41, 128, 185)  # Azul elegante
        text_color = (52, 73, 94)  # Gris oscuro elegante
        accent_color = (231, 76, 60)  # Rojo para tiempo
        
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
        
        # Icono de celular (simulado con texto)
        phone_icon = "📱"
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
    """
    try:
        print("📋 Mostrando código QR para examen final...")
        
        # Cargar imagen del QR
        qr_image = cv2.imread(qr_image_path)
        
        if qr_image is None:
            print(f"❌ Error: No se pudo cargar la imagen QR desde {qr_image_path}")
            return False
        
        # Configuración de diseño para examen final
        window_width = 1000
        window_height = 700
        
        # Crear ventana
        cv2.namedWindow("Examen Final", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Examen Final", window_width, window_height)
        
        # Colores para examen final (más serios/académicos)
        bg_color = (240, 248, 255)  # Alice blue - más formal
        header_color = (25, 25, 112)  # Midnight blue - académico
        text_color = (25, 25, 112)   # Mismo azul oscuro
        accent_color = (220, 20, 60)  # Crimson para urgencia
        success_color = (34, 139, 34)  # Forest green
        
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

# ===============================================
#  MOSTRAR CÓDIGO QR PARA EVALUACIÓN DIAGNÓSTICA
# ===============================================

def display_final_exam_phase(engine, exam_qr_filename="examen_final.png"):
    """
    Muestra la fase de examen final con mensaje de ADAI y QR
    
    Args:
        engine: Motor de TTS
        exam_qr_filename (str): Nombre del archivo QR en la carpeta RobotsMedicosExamen
    """
    try:
        print("\n" + "="*60)
        print("📋 FASE FINAL: EXAMEN POST-CLASE")
        print("="*60)
        
        # Mensaje de ADAI antes del examen
        speak_with_animation(engine, "Excelente trabajo durante la clase. Ahora es momento de demostrar lo que has aprendido.")
        time.sleep(1.0)
        
        speak_with_animation(engine, "He preparado un examen final sobre robots médicos. Por favor, escanea el código QR que aparecerá en pantalla.")
        time.sleep(1.0)
        
        # Construir ruta al QR del examen
        exam_folder = os.path.join(script_dir, "RobotsMedicosExamen")
        exam_qr_path = os.path.join(exam_folder, exam_qr_filename)
        
        # Debug de la ruta
        print(f"🔍 Buscando examen QR en: {exam_qr_path}")
        print(f"📁 Carpeta de examen existe: {os.path.exists(exam_folder)}")
        print(f"📄 Archivo QR existe: {os.path.exists(exam_qr_path)}")
        
        # Verificar que existe la carpeta
        if not os.path.exists(exam_folder):
            print(f"⚠️ No se encontró la carpeta: {exam_folder}")
            speak_with_animation(engine, "No se encontró la carpeta del examen. La clase ha terminado.")
            return False
        
        # Listar archivos en la carpeta para debug
        try:
            files_in_exam_folder = os.listdir(exam_folder)
            print(f"📂 Archivos en carpeta de examen: {files_in_exam_folder}")
        except Exception as e:
            print(f"❌ Error listando carpeta de examen: {e}")
        
        # Verificar que existe el archivo QR
        if os.path.exists(exam_qr_path):
            # Mostrar QR del examen (20 segundos por defecto)
            success = show_final_exam_qr(exam_qr_path, display_time=20)
            
            if success:
                # Mensaje final de ADAI
                speak_with_animation(engine, "Perfecto. El examen ha sido presentado. ¡Mucha suerte!")
                time.sleep(1.0)
                speak_with_animation(engine, "Gracias por participar en esta clase con tecnología robótica. ¡Hasta la próxima!")
                return True
            else:
                speak_with_animation(engine, "Hubo un problema mostrando el examen, pero la clase ha terminado exitosamente.")
                return False
        else:
            print(f"⚠️ No se encontró el archivo QR: {exam_qr_path}")
            speak_with_animation(engine, "No se encontró el archivo del examen. La clase ha terminado.")
            
            # Sugerir archivos disponibles
            if files_in_exam_folder:
                print(f"💡 Archivos disponibles en la carpeta:")
                for file in files_in_exam_folder:
                    print(f"   - {file}")
                print(f"💡 Asegúrate de que el archivo se llame exactamente '{exam_qr_filename}'")
            
            return False
            
    except Exception as e:
        print(f"❌ Error en fase de examen final: {e}")
        speak_with_animation(engine, "Hubo un problema con el examen, pero la clase ha terminado exitosamente.")
        return False
    
# ======================
#  FUNCIONES DE DIBUJO
# ======================
def draw_stylish_eye(img, center_x, center_y):
    """
    Ojo estilo caricatura:
      - Círculo blanco con borde negro (esclerótica)
      - Anillo azul (iris)
      - Pupila negra grande
      - Brillo blanco
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
    Dibuja un rostro con 2 ojos 'azules' (draw_stylish_eye)
    y boca con 3 estados:
      0 = cerrada
      1 = semiabierta
      2 = muy abierta (sin dientes)
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

# ================================
#   FUNCIÓN HABLAR CON ANIMACIÓN
# ================================
def speak_with_animation(engine, text):
    """
    Habla 'text' usando pyttsx3 (modo manual) mientras dibuja
    un 'rostro animado' en la ventana "ADAI Robot Face".
    Alterna la boca entre 1 (semiabierta) y 2 (muy abierta).
    Al terminar, dibuja la boca cerrada (0).
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

# ============================
#   MOSTRAR PDF EN OPENCV
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
#    PROCESO DE LA CÁMARA
# ============================
# ============================
#   CAMERA_PROCESS CORREGIDO Y CON DIAGNÓSTICO
# ============================
def camera_process(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, registered_users):
    """
    Proceso de cámara corregido con mejor detección facial para múltiples usuarios
    """
    try:
        print("🎥 [CAMERA] Iniciando proceso de cámara...")
        print(f"🎥 [CAMERA] Usuarios registrados: {registered_users}")
        
        # Configuración MediaPipe MEJORADA
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=8,
            min_detection_confidence=0.3,  # AUMENTADO de 0.4
            min_tracking_confidence=0.2    # REDUCIDO de 0.25
        )
        mp_draw = mp.solutions.drawing_utils
        
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.05  # REDUCIDO de 0.1 - MÁS SENSIBLE
        )
        
        print("🎥 [CAMERA] MediaPipe configurado correctamente")
        
        # Intentar abrir la cámara con múltiples métodos
        cap = None
        camera_configs = [
            (0, cv2.CAP_DSHOW, "DirectShow"),
            (0, None, "Default"),
            (1, cv2.CAP_DSHOW, "DirectShow Index 1"),
            (1, None, "Default Index 1"),
        ]
        
        for index, backend, name in camera_configs:
            try:
                print(f"🎥 [CAMERA] Probando {name}...")
                if backend is None:
                    cap = cv2.VideoCapture(index)
                else:
                    cap = cv2.VideoCapture(index, backend)
                
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
        resolutions_to_try = [
            (1280, 720, "HD"),
            (640, 480, "VGA"),
            (320, 240, "QVGA")
        ]
        
        resolution_set = False
        for width, height, name in resolutions_to_try:
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
        max_consecutive = 6
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
        
        student_colors = [
            (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 128, 255), (255, 128, 0)
        ]
        
        def calculate_distance(pos1, pos2):
            return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
        
        def find_best_match(current_detections, user_tracking, threshold=120):
            """Función de asignación mejorada para múltiples usuarios"""
            assignments = {}
            used_users = set()
            
            if not current_detections:
                return assignments
            
            # Calcular distancias para todas las combinaciones
            distances = {}
            for det_idx, detection in enumerate(current_detections):
                det_center = detection['center']
                distances[det_idx] = {}
                
                for user_id in range(max_registered_users):
                    if user_tracking[user_id]['positions']:
                        # Usar posiciones recientes para predecir ubicación
                        recent_positions = user_tracking[user_id]['positions'][-5:]
                        avg_x = sum(pos[0] for pos in recent_positions) / len(recent_positions)
                        avg_y = sum(pos[1] for pos in recent_positions) / len(recent_positions)
                        avg_pos = (avg_x, avg_y)
                        
                        dist = calculate_distance(det_center, avg_pos)
                        distances[det_idx][user_id] = dist
                    else:
                        # Para usuarios sin historial, usar distancia 0 (nueva detección)
                        distances[det_idx][user_id] = 0
            
            # Algoritmo de asignación óptima
            while len(assignments) < min(len(current_detections), max_registered_users):
                best_dist = float('inf')
                best_det = None
                best_user = None
                
                for det_idx in range(len(current_detections)):
                    if det_idx in assignments:
                        continue
                    for user_id in range(max_registered_users):
                        if user_id in used_users:
                            continue
                        if distances[det_idx][user_id] < best_dist:
                            best_dist = distances[det_idx][user_id]
                            best_det = det_idx
                            best_user = user_id
                
                if best_det is not None and best_user is not None:
                    # Aplicar umbral, pero ser más permisivo para nuevas detecciones
                    effective_threshold = threshold
                    if user_tracking[best_user]['positions'] == []:
                        effective_threshold = threshold * 3  # Más permisivo para usuarios nuevos
                    
                    if best_dist < effective_threshold:
                        assignments[best_det] = best_user
                        used_users.add(best_user)
                    else:
                        break
            
            return assignments
        
        frame_count = 0
        last_status_print = 0
        
        print("🎥 [CAMERA] 🚀 INICIANDO LOOP PRINCIPAL...")
        
        while exit_flag.value == 0:
            ret, frame = cap.read()
            if not ret:
                print("🎥 [CAMERA] ⚠️ No se pudo leer frame, reintentando...")
                time.sleep(0.01)
                continue
            
            #frame = cv2.flip(frame, 1)
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
                        min_face_area = (w * h) * 0.0001  # REDUCIDO de 0.0002
                        max_face_area = (w * h) * 0.4      # Máximo 40% de la imagen
                        
                        # FILTROS MEJORADOS para caras válidas
                        if (min_face_area <= face_area <= max_face_area and 
                            width > 30 and height > 30 and  # Tamaño mínimo absoluto
                            width < w * 0.8 and height < h * 0.8 and  # No demasiado grande
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
                    assignments = {}
                    if current_detections:
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
                                
                        # Debug opcional
                        if frame_count % 120 == 0 and assignments:
                            print(f"🎯 [CAMERA] Asignaciones: {len(assignments)} caras ordenadas de izq→der")
                    
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
                        if middle_tip.y < wrist.y - 0.03:
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
                                max_horizontal_distance = face_width * 1.5  # 1.5 veces el ancho de la cara
                                
                                # CONDICIÓN 2: La mano debe estar ENCIMA de la cara
                                vertical_clearance = face_y1 - wrist_y  # Distancia positiva = mano arriba
                                min_vertical_clearance = 20  # Al menos 20 píxeles arriba
                                max_vertical_clearance = face_height * 3  # Máximo 3 veces la altura de la cara
                                
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

# ===============
#   INITIALIZE TTS
# ===============
def initialize_tts():
    try:
        engine = pyttsx3.init()
        engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0')
        return engine
    except Exception as e:
        print(f"❌ Error al inicializar TTS: {e}")
        return None

# =================
#   LISTEN
# =================
def listen(timeout=5, phrase_time_limit=None):
    """
    Función mejorada de escucha con mejor manejo de errores.
    Intenta reconocer el habla y maneja graciosamente los errores de conexión.
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("🎤 Escuchando...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            recognizer.energy_threshold = 400
            recognizer.pause_threshold = 0.8
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

# =====================
#   UTILIDADES
# =====================
def load_known_faces():
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
    configs = [
        (0, None),           # iriun/default
        (0, cv2.CAP_DSHOW),  # DirectShow
        (1, None),           # índice 1
        (2, None)            # índice 2
    ]
    
    for index, backend in configs:
        try:
            if backend is None:
                cap = cv2.VideoCapture(index)
            else:
                cap = cv2.VideoCapture(index, backend)
                
            if not cap.isOpened():
                continue
            
            # MEJORADO: Configurar para máxima resolución disponible
            # Intentar primero con alta resolución
            resolutions = [
                (1920, 1080),  # Full HD
                (1280, 720),   # HD
                (1024, 768),   # XGA
                (640, 480)     # VGA (fallback)
            ]
            
            for width, height in resolutions:
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

def recognize_user(frame, known_faces):
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in face_encodings:
            for name, known_encoding in known_faces.items():
                match = face_recognition.compare_faces([known_encoding], encoding, tolerance=0.5)
                if match[0]:
                    return name
        return None
    except Exception as e:
        print(f"❌ Error al reconocer usuario: {e}")
        return None

def save_new_face(frame, name):
    try:
        path = os.path.join(faces_dir, f"{name}.jpg")
        cv2.imwrite(path, frame)
        image = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(image)[0]
        return encoding
    except Exception as e:
        print(f"❌ Error al guardar nueva cara: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"❌ Error al leer el PDF: {e}")
        return None

def summarize_text(text):
    try:
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
        # Sistema mejorado para respuestas naturales
        system_prompt = """Eres ADAI, un asistente educativo androide amigable y conversacional que SOLO 
        responde preguntas relacionadas con el contenido del PDF proporcionado. Si la pregunta no está relacionada con el PDF, 
        indica claramente que solo puedes responder preguntas sobre el tema del PDF." 

REGLAS IMPORTANTES:
- NO uses asteriscos, guiones, viñetas, ni formato especial
- NO uses emojis ni símbolos especiales  
- Habla de manera natural y conversacional como un profesor amigable
- Máximo 3 oraciones por respuesta
- NO uses palabras como "retroalimentación", "corrección", "evaluación"
- Si corriges algo, hazlo de manera educativa pero natural"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexto: {context}\n\nPregunta: {question}"}
            ]
        )
        
        # Limpiar respuesta de cualquier formato
        answer = response.choices[0].message.content
        answer = answer.replace("*", "").replace("**", "").replace("***", "")
        answer = answer.replace("- ", "").replace("• ", "")
        answer = answer.strip()
        
        return answer
    except Exception as e:
        print(f"❌ Error en OpenAI natural: {e}")
        return "Lo siento, hubo un problema. Continuemos con la clase."


# =====================================================
#   PROCESAR PREGUNTAS / EXPLICAR DIAPOS / ETC.
# =====================================================
def process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser):
    """
    Procesamiento de preguntas basado en la identificación de estudiantes
    """
    print("🤔 Procesando preguntas de usuarios...")
    
    try:
        # Determinar quién hizo la pregunta
        student_id = current_hand_raiser.value
        
        # Si no tenemos un ID concreto, preguntamos quién hizo la pregunta
        if student_id < 0 or student_id >= len(current_users):
            if len(current_users) > 1:
                speak_with_animation(engine, "Alguien ha levantado la mano. ¿Quién desea preguntar?")
                name = listen()
                if name and name not in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""] and name.lower() in [user.lower() for user in current_users]:
                    current_user = next(user for user in current_users if user.lower() == name.lower())
                else:
                    # Si no entendemos el nombre o no coincide, usamos el primer usuario
                    current_user = list(current_users)[0]
            else:
                current_user = list(current_users)[0]
        else:
            # Convertir el ID numérico al nombre del estudiante 
            # (asumiendo que el orden en current_users coincide con los IDs asignados)
            if student_id < len(current_users):
                current_user = list(current_users)[student_id]
            else:
                # Si el ID está fuera de rango, usar el primer estudiante
                current_user = list(current_users)[0]
        
        speak_with_animation(engine, f"Sí, {current_user}, ¿cuál es tu pregunta?")
        
        # Escuchar la pregunta con mejor manejo de errores
        question = listen(timeout=10)  # Aumentamos el timeout para preguntas
        hand_raised_counter.value = 0
        
        if not question or question in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""]:
            if question and question.startswith("error"):
                speak_with_animation(engine, "Hubo un problema con el reconocimiento de voz. Continuemos con la clase.")
            else:
                speak_with_animation(engine, "No pude entender tu pregunta. Continuemos con la clase.")
            return True
        
        try:
            answer = ask_openai(question, pdf_text)
            speak_with_animation(engine, answer)
        except Exception as e:
            print(f"❌ Error al procesar la respuesta con OpenAI: {e}")
            speak_with_animation(engine, "Lo siento, tuve un problema al generar una respuesta. Continuemos con la clase.")
        
        # Preguntar si hay más preguntas solo si no se detectó una mano levantada
        if hand_raised_counter.value == 0:
            speak_with_animation(engine, "¿Alguien más tiene alguna pregunta sobre el tema del PDF?")
            follow_up = listen()
            
            if follow_up and follow_up not in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""] and "sí" in follow_up.lower():
                return process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
            else:
                speak_with_animation(engine, "Bien, continuemos con la clase.")
        else:
            speak_with_animation(engine, "Continuemos con la clase.")
        
        return True
    except Exception as e:
        print(f"❌ Error general en proceso de preguntas: {e}")
        speak_with_animation(engine, "Hubo un problema al procesar la pregunta. Continuemos con la clase.")
        return True

def interpret_image(image_path):
    try:
        text = pytesseract.image_to_string(image_path, lang='spa')
        if text.strip():
            return summarize_text(text)
        else:
            # Si tesseract no encuentra texto, usamos una descripción genérica
            return "Esta diapositiva contiene principalmente elementos visuales. Se trata de una imagen ilustrativa relacionada con el tema de la clase."
    except Exception as e:
        print(f"❌ Error al interpretar la imagen: {e}")
        return "Lo siento, hubo un error al interpretar la imagen."

# ================================
#   EXPLAIN_SLIDES 
# ================================
def explain_slides_with_random_questions(engine, pdf_path, pdf_text, current_users,
                                        hand_raised_counter, current_slide_num, exit_flag, 
                                        known_faces, current_hand_raiser):
    """
    Explicación de diapositivas con preguntas aleatorias cada 3 slides - CÓDIGO TRADICIONAL
    """
    try:
        print("📊 Iniciando explicación con sistema de preguntas aleatorias...")
        
        # Inicializar gestor de preguntas
        question_manager = RandomQuestionManager(current_users)

        # Crear ventana "Presentacion" para mostrar cada página
        cv2.namedWindow("Presentacion", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Presentacion", 800, 600)

        with fitz.open(pdf_path) as doc:
            total_slides = len(doc)
            slide_num = 0
            
            while slide_num < total_slides and exit_flag.value == 0:
                current_slide_num.value = slide_num + 1
                print(f"📝 Explicando diapositiva {current_slide_num.value} de {total_slides}")
                
                # Verificar manos levantadas antes de continuar
                if hand_raised_counter.value > 0:
                    print(f"✋ Manos levantadas detectadas: {hand_raised_counter.value}")
                    process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                    continue
                
                page = doc[slide_num]
                # Mostrar la imagen de la diapositiva
                page_img = show_pdf_page_in_opencv(page)
                cv2.imshow("Presentacion", page_img)
                cv2.waitKey(50)

                # Obtener texto y generar explicación
                page_text = page.get_text()

                if page_text.strip():
                    prompt = f"""
                    El siguiente texto es de una diapositiva de clase sobre robótica. 
                    No resumas simplemente el contenido, sino explícalo como lo haría un profesor 
                    entusiasta en clase pero hacerlo CONCISO máximo (4-5 frases),
                    añadiendo contexto y haciéndolo interesante y conversacional:
                    
                    Contenido:
                    {page_text}
                    """
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": """Eres ADAI, Asistente Docente Androide de Ingeniería. 
                                    IMPORTANTE: NO uses emojis, símbolos especiales, ni caracteres no alfabéticos en tus respuestas 
                                    ya que serán leídas en voz alta por un sintetizador de voz. 
                                    Usa solo texto simple, claro y profesional. Sé entusiasta pero con palabras, no con símbolos."""},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        explanation = response.choices[0].message.content
                    except Exception as e:
                        print(f"❌ Error en OpenAI: {e}")
                        explanation = summarize_text(page_text)
                else:
                    # Si no hay texto en la página
                    image_path = os.path.join(script_dir, f"page{slide_num + 1}.png")
                    page.get_pixmap().save(image_path)
                    explanation = interpret_image(image_path)
                
                # Mensaje inicial
                slide_info = f"Diapositiva {slide_num + 1}: "
                speak_with_animation(engine, slide_info)

                # Explicación en frases
                sentences = []
                for part in explanation.split("."):
                    if part.strip():
                        sentences.append(part.strip() + ".")

                for i, sentence in enumerate(sentences):
                    if hand_raised_counter.value > 0:
                        print(f"✋ Manos levantadas detectadas: {hand_raised_counter.value}")
                        process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                        continue
                    
                    if exit_flag.value != 0:
                        print("🛑 Señal de salida detectada")
                        return False
                    
                    if sentence.strip():
                        print(f"🗣️ Fragmento {i+1}/{len(sentences)}: {sentence[:30]}...")
                        speak_with_animation(engine, sentence)
                    
                    time.sleep(0.2)
                
                # Pequeña pausa
                for _ in range(5):
                    if hand_raised_counter.value > 0 or exit_flag.value != 0:
                        break
                    time.sleep(0.2)
                
                if hand_raised_counter.value > 0:
                    print(f"✋ Manos levantadas tras la diapositiva: {hand_raised_counter.value}")
                    process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser)
                    continue
                
                slide_num += 1
                
                # *** PREGUNTA ALEATORIA CADA 3 DIAPOSITIVAS ***
                if slide_num % 3 == 0 and slide_num < total_slides:
                    print(f"\n🎯 === PREGUNTA ALEATORIA (después de diapositiva {slide_num}) ===")
                    
                    # Pausa antes de la pregunta
                    speak_with_animation(engine, "Muy bien. Ahora haremos una pausa para verificar el aprendizaje.")
                    time.sleep(1.0)
                    
                    # Realizar pregunta aleatoria
                    question_manager.conduct_random_question(engine, pdf_text)
                    
                    # Pausa después de la pregunta antes de continuar
                    time.sleep(1.0)
                    
                    # Anunciar continuación
                    if slide_num < total_slides:
                        speak_with_animation(engine, "Excelente. Continuemos con la siguiente sección.")
                    
                    print(f"🎯 === FIN DE PREGUNTA ALEATORIA ===\n")
        
        # Mostrar estadísticas finales
        stats = question_manager.get_statistics()
        print("\n📊 === ESTADÍSTICAS DE PREGUNTAS ===")
        print(f"Total de preguntas realizadas: {stats['total_questions']}")
        print("Preguntas por estudiante:")
        for student, count in stats['questions_per_student'].items():
            print(f"  - {student}: {count}")
        
        print("✅ Explicación de diapositivas completada")
        return True
        
    except Exception as e:
        print(f"❌ Error al explicar diapositivas: {e}")
        return False

# ==========================
#  VERIFY CAMERA / IDENTIFY_USERS / MAIN
# ==========================

def verify_camera_for_iriun():
    """
    Verifica que la cámara funcione correctamente con iriun
    """
    print("🔍 Verificando cámara para iriun...")
    
    # Intentar diferentes configuraciones
    configs = [
        (0, None, "iriun/default"),
        (0, cv2.CAP_DSHOW, "DirectShow"),
        (1, None, "índice 1"),
        (2, None, "índice 2")
    ]
    
    for index, backend, name in configs:
        try:
            if backend is None:
                cap = cv2.VideoCapture(index)
            else:
                cap = cv2.VideoCapture(index, backend)
            
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

def identify_users(engine, current_slide_num, exit_flag):
    """
    Versión modificada que registra usuarios de IZQUIERDA A DERECHA
    """
    print("👥 Iniciando identificación de usuarios (izquierda a derecha)")
    known_faces = load_known_faces()
    current_users = []
    
    # Inicializar MediaPipe para detección facial
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(
        model_selection=1,  # Para distancias largas (hasta 5 metros)
        min_detection_confidence=0.03  # Sensible para detectar a 3-5m
    )
    
    speak_with_animation(engine, "Bienvenidos a la clase. Voy a identificar a todos los estudiantes presentes de izquierda a derecha. Mantengan la vista hacia la cámara, porfavor.")
    
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
        speak_with_animation(engine, "No puedo acceder a la cámara correctamente. Continuaré sin identificación facial.")
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
        speak_with_animation(engine, "No detecto ninguna cara. Continuaré con un estudiante genérico.")
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
            width > 15 and height > 15 and  # Tamaño mínimo para 3-5m
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
            speak_with_animation(engine, f"Te registraré como {name}.")
            continue
        
        # Lo convertimos a RGB para face_recognition
        try:
            rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"❌ Error convirtiendo cara a RGB: {e}")
            name = f"Estudiante {sorted_id + 1}"
            current_users.append(name)
            speak_with_animation(engine, f"Te registraré como {name}.")
            continue
        
        # Intentamos obtener encodings
        try:
            face_locations = face_recognition.face_locations(rgb_face)
            if not face_locations:
                print(f"⚠️ No se pudo procesar la cara de Persona {sorted_id + 1}")
                name = f"Estudiante {sorted_id + 1}"
                current_users.append(name)
                speak_with_animation(engine, f"Te registraré como {name}.")
                continue
            
            face_encodings = face_recognition.face_encodings(rgb_face, face_locations)
            if not face_encodings:
                print(f"⚠️ No se pudo generar encoding para Persona {sorted_id + 1}")
                name = f"Estudiante {sorted_id + 1}"
                current_users.append(name)
                speak_with_animation(engine, f"Te registraré como {name}.")
                continue
            
            face_encoding = face_encodings[0]
            
        except Exception as e:
            print(f"❌ Error procesando cara de Persona {sorted_id + 1}: {e}")
            name = f"Estudiante {sorted_id + 1}"
            current_users.append(name)
            speak_with_animation(engine, f"Te registraré como {name}.")
            continue
        
        # Verificar si coincide con alguna cara conocida
        face_recognized = False
        for existing_name, known_encoding in known_faces.items():
            try:
                match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.55)
                if match[0]:
                    # VERIFICAR QUE NO ESTÉ YA EN LA LISTA
                    if existing_name not in current_users:
                        current_users.append(existing_name)
                        face_recognized = True
                        print(f"✅ Usuario reconocido en posición {sorted_id + 1}: {existing_name}")
                        speak_with_animation(engine, f"Hola {existing_name}, te reconozco.")
                        break
                    else:
                        print(f"⚠️ {existing_name} ya está registrado, continuando búsqueda...")
                        continue
            except Exception as e:
                print(f"❌ Error comparando con {existing_name}: {e}")
                continue
        
        # SI NO FUE RECONOCIDO, PEDIR NOMBRE
        if not face_recognized:
            speak_with_animation(engine, f"Persona en posición {sorted_id + 1}, por favor di tu nombre despues del bip.")
            time.sleep(1)  # Pausa pequeña
            winsound.Beep(800, 500) 
            
            # Intentamos capturar el nombre con timeout más largo
            attempts = 0
            max_attempts = 3
            name = None
            
            while attempts < max_attempts and not name:
                attempts += 1
                print(f"🎤 Intento {attempts} de capturar nombre para Persona {sorted_id + 1}")
                
                raw_name = listen(timeout=8)
                
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
                            speak_with_animation(engine, "No entendí tu nombre. Intenta de nuevo despues del bip.")
                            time.sleep(1)  # Pausa pequeña
                            winsound.Beep(800, 500)
                else:
                    print(f"⚠️ Respuesta inválida: '{raw_name}'. Intento {attempts}/{max_attempts}")
                    if attempts < max_attempts:
                        speak_with_animation(engine, "No pude escuchar tu nombre. Por favor repite.")
            
            if name:
                # Verificar si ya existe este nombre
                original_name = name
                counter = 1
                while name in current_users:
                    counter += 1
                    name = f"{original_name}_{counter}"
                
                if name != original_name:
                    speak_with_animation(engine, f"Ya existe un usuario con ese nombre. Te registraré como {name}.")
                
                # Guardar la cara con el nombre
                try:
                    path = os.path.join(faces_dir, f"{name}.jpg")
                    cv2.imwrite(path, face_img)
                    
                    # Actualizar known_faces para futuras comparaciones
                    known_faces[name] = face_encoding
                    current_users.append(name)
                    
                    speak_with_animation(engine, f"Gracias, {name}. Gusto en conocerte.")
                    print(f"✅ Nuevo usuario registrado en posición {sorted_id + 1}: {name}")
                    
                except Exception as e:
                    print(f"❌ Error guardando cara de {name}: {e}")
                    name = f"Estudiante {sorted_id + 1}"
                    current_users.append(name)
                    speak_with_animation(engine, f"Hubo un problema al registrarte. Te llamaré {name}.")
            else:
                # No se pudo capturar un nombre válido después de varios intentos
                name = f"Estudiante {sorted_id + 1}"
                current_users.append(name)
                speak_with_animation(engine, f"No pude entender tu nombre. Te registraré como {name}.")
                print(f"⚠️ No se pudo capturar nombre válido para Persona {sorted_id + 1}")
    
    # Limpiar recursos
    face_detection.close()
    cv2.destroyWindow("Detección ordenada (Izq → Der)")
    
    # Verificamos si tenemos usuarios registrados
    if not current_users:
        speak_with_animation(engine, "No detecté ningún estudiante. Continuaré la clase con un estudiante genérico.")
        current_users = ["Estudiante 1"]
    
    # MENSAJE DE BIENVENIDA CON ORDEN
    try:
        num_students = len(current_users)
        
        if num_students > 1:
            speak_with_animation(engine, f"Perfecto. He registrado a {num_students} estudiantes.")
        
        speak_with_animation(engine, f"Comenzaremos la clase con {num_students} estudiante{'s' if num_students > 1 else ''}.")
        
    except Exception as e:
        print(f"❌ Error al finalizar registro: {e}")
        speak_with_animation(engine, "Hubo un problema al finalizar el registro, pero continuaremos con la clase.")
        if not current_users:
            current_users = ["Estudiante 1"]
    
    print(f"✅ Identificación completada de izquierda a derecha. Usuarios finales: {current_users}")
    return current_users, current_users[0] if current_users else "Estudiante 1"

# ============
#   MAIN
# ============
def main():
    """
    Main simplificado con rutas configurables
    """
    try:
        print("🚀 Iniciando ADAI")
        
        # *** QR DIAGNÓSTICO - SÚPER SIMPLE ***
        print("\n" + "="*50)
        print("📱 FASE 1: EVALUACIÓN DIAGNÓSTICA")
        print("="*50)
        
        diagnostic_qr = QR_PATHS['diagnostic_IoMT']
        print(f"🔍 Buscando QR diagnóstico: {diagnostic_qr}")
        
        if os.path.exists(diagnostic_qr):
            show_diagnostic_qr(diagnostic_qr, display_time=40)
        else:
            print(f"⚠️ No se encontró: {diagnostic_qr}")
            print("📱 Continúando sin evaluación diagnóstica...")
        
        print("\n" + "="*50)
        print("🤖 FASE 2: INICIO DE CLASE")
        print("="*50)
        
        # Crear ventana para la cara animada
        cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("ADAI Robot Face", 600, 400)

        hand_raised_counter = multiprocessing.Value('i', 0)
        current_slide_num   = multiprocessing.Value('i', 1)
        exit_flag           = multiprocessing.Value('i', 0)
        current_hand_raiser = multiprocessing.Value('i', -1)

        engine = initialize_tts()
        if not engine:
            print("❌ No se pudo inicializar el motor TTS")
            return

        # Saludo inicial
        speak_with_animation(engine, "Hola, soy ADAI, tu Asistente Docente Androide de Ingeniería.")

        # Verificar cámara
        if not verify_camera_for_iriun():
            print("⚠️ Problemas detectados con la cámara.")

        # PDF
        pdf_path = os.path.join(script_dir, "DesafiosDeIoMT.pdf")
        pdf_text = extract_text_from_pdf(pdf_path)
        
        if not pdf_text:
            print("❌ No se pudo leer el PDF")
            return
        
        # Identificar usuarios
        print("🔍 Identificando usuarios de izquierda a derecha...")
        current_users, _ = identify_users(engine, current_slide_num, exit_flag)

        # Cargar caras
        known_faces = load_known_faces()

        # Iniciar proceso de cámara
        camera_proc = Process(
            target=camera_process,
            args=(hand_raised_counter, current_slide_num, exit_flag, current_hand_raiser, current_users)
        )
        camera_proc.daemon = True
        camera_proc.start()

        print("⏳ Esperando a que la cámara se inicialice...")
        time.sleep(3)

        # Inicio de clase
        speak_with_animation(engine, "Perfecto. Ahora comenzaremos con la presentación sobre robots médicos.")

        # Explicar diapositivas con preguntas aleatorias
        if explain_slides_with_random_questions(engine, pdf_path, pdf_text, current_users,
                                               hand_raised_counter, current_slide_num, exit_flag, 
                                               known_faces, current_hand_raiser):
            
            # *** QR EXAMEN FINAL - SÚPER SIMPLE ***
            print("\n" + "="*60)
            print("🎓 FASE FINAL: EXAMEN")
            print("="*60)
            
            final_exam_qr = QR_PATHS['final_examIoMT']
            print(f"🔍 Buscando QR examen: {final_exam_qr}")
            
            if os.path.exists(final_exam_qr):
                # Mensaje de ADAI
                speak_with_animation(engine, "Excelente trabajo. Ahora es momento del examen final.")
                speak_with_animation(engine, "Por favor, escanea el código QR que aparecerá en pantalla.")
                
                # Mostrar QR del examen
                show_final_exam_qr(final_exam_qr, display_time=40)
                
                # Mensaje final
                speak_with_animation(engine, "Perfecto. ¡Mucha suerte en el examen!")
                speak_with_animation(engine, "Gracias por participar en esta clase con ADAI. ¡Hasta la próxima!")
            else:
                print(f"⚠️ No se encontró: {final_exam_qr}")
                speak_with_animation(engine, "La clase ha terminado. ¡Gracias por participar!")
        
        print("🛑 Finalizando programa")
        exit_flag.value = 1

        print("⏳ Esperando procesos...")
        camera_proc.join(timeout=3)
        
        if camera_proc.is_alive():
            camera_proc.terminate()
            camera_proc.join(timeout=1)
        
        print("✅ Programa finalizado")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'exit_flag' in locals():
            exit_flag.value = 1
        if 'camera_proc' in locals() and camera_proc.is_alive():
            camera_proc.terminate()
            camera_proc.join(timeout=1)
        
        cv2.destroyAllWindows()
        print("🔚 Fin")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()