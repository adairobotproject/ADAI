"""
Sistema ADAI - Versión Organizada
Sistema de asistente docente con inteligencia artificial
"""
import cv2
import numpy as np
import time
import threading
import multiprocessing
from multiprocessing import Process, Value, Event
import msvcrt
import winsound
import pytesseract

# Importar módulos organizados
from config.settings import settings
from utils.file_utils import setup_directories, extract_text_from_pdf
from ai.openai_client import OpenAIClient
from vision.face_recognition_utils import FaceRecognitionManager, capture_frame
from vision.hand_detection import HandGestureDetector, UserTracking
from audio.tts_manager import TTSManager, speak_with_animation
from audio.speech_recognition_utils import SpeechRecognitionManager
from ui.animations import draw_fun_face, create_qr_display_frame, show_pdf_page_in_opencv
from exams.question_manager import RandomQuestionManager, ExamManager

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

class ADAISystem:
    """Sistema principal de ADAI."""
    
    def __init__(self):
        """Inicializa el sistema ADAI."""
        print("🤖 Inicializando sistema ADAI...")
        
        # Configurar directorios
        setup_directories(settings.base_dir)
        
        # Inicializar componentes
        self.openai_client = OpenAIClient(settings.openai_api_key)
        self.tts_manager = TTSManager()
        self.speech_recognizer = SpeechRecognitionManager()
        self.face_recognition = FaceRecognitionManager(settings.paths['faces_dir'])
        self.hand_detector = HandGestureDetector()
        self.user_tracking = UserTracking()
        
        # Inicializar gestores
        self.question_manager = RandomQuestionManager([])
        self.exam_manager = ExamManager()
        
        # Variables de estado
        self.current_users = []
        self.hand_raised_counter = Value('i', 0)
        self.current_hand_raiser = Value('i', -1)
        self.exit_flag = Event()
        
        print("✅ Sistema ADAI inicializado correctamente")
    
    def show_diagnostic_qr(self, qr_image_path: str, display_time: int = 15):
        """
        Muestra un código QR de diagnóstico.
        
        Args:
            qr_image_path: Ruta de la imagen QR
            display_time: Tiempo de visualización en segundos
        """
        try:
            # Crear frame con QR
            frame = create_qr_display_frame(qr_image_path, "Diagnóstico", "Escanea el código QR")
            
            # Mostrar ventana
            window_name = "Diagnóstico QR"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 800, 600)
            
            start_time = time.time()
            while time.time() - start_time < display_time:
                cv2.imshow(window_name, frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cv2.destroyWindow(window_name)
            
        except Exception as e:
            print(f"❌ Error al mostrar QR de diagnóstico: {e}")
    
    def show_final_exam_qr(self, qr_image_path: str, display_time: int = 20):
        """
        Muestra un código QR de examen final.
        
        Args:
            qr_image_path: Ruta de la imagen QR
            display_time: Tiempo de visualización en segundos
        """
        try:
            # Crear frame con QR
            frame = create_qr_display_frame(qr_image_path, "Examen Final", "Escanea para acceder al examen")
            
            # Mostrar ventana
            window_name = "Examen Final QR"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 800, 600)
            
            start_time = time.time()
            while time.time() - start_time < display_time:
                cv2.imshow(window_name, frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cv2.destroyWindow(window_name)
            
        except Exception as e:
            print(f"❌ Error al mostrar QR de examen final: {e}")
    
    def camera_process(self):
        """Proceso de la cámara para detección de gestos y reconocimiento facial."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ No se pudo abrir la cámara")
            return
        
        # Configurar cámara
        camera_config = settings.get_camera_config()
        cap.set(cv2.CAP_PROP_FPS, camera_config['fps'])
        cap.set(cv2.CAP_PROP_BUFFERSIZE, camera_config['buffer_size'])
        
        print("📹 Proceso de cámara iniciado")
        
        while not self.exit_flag.is_set():
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Detectar gestos de manos
            hand_raised, hands_detected = self.hand_detector.detect_hand_raise(frame)
            
            if hand_raised:
                with self.hand_raised_counter.get_lock():
                    self.hand_raised_counter.value += 1
                print("✋ Mano levantada detectada!")
            
            # Reconocer usuarios
            user_name, recognized = self.face_recognition.recognize_user(frame)
            if recognized and user_name not in self.current_users:
                self.current_users.append(user_name)
                print(f"👤 Usuario reconocido: {user_name}")
            
            # Dibujar landmarks de manos
            if hands_detected:
                frame = self.hand_detector.draw_hand_landmarks(frame, hands_detected)
            
            # Mostrar información en el frame
            cv2.putText(frame, f"Usuarios: {len(self.current_users)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Manos levantadas: {self.hand_raised_counter.value}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Mostrar frame
            cv2.imshow("Cámara ADAI", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("📹 Proceso de cámara terminado")
    
    def process_question(self, pdf_text: str):
        """
        Procesa una pregunta del estudiante.
        
        Args:
            pdf_text: Texto del PDF para contexto
        """
        try:
            # Escuchar pregunta
            question, success = self.speech_recognizer.listen(timeout=10)
            
            if success and question:
                # Obtener respuesta de OpenAI
                response = self.openai_client.ask_openai(question, pdf_text)
                
                # Hablar la respuesta
                self.tts_manager.speak(response)
                
                print(f"❓ Pregunta: {question}")
                print(f"🤖 Respuesta: {response}")
            else:
                print("❌ No se pudo entender la pregunta")
                
        except Exception as e:
            print(f"❌ Error al procesar pregunta: {e}")
    
    def explain_slides_with_random_questions(self, pdf_path: str):
        """
        Explica diapositivas con preguntas aleatorias.
        
        Args:
            pdf_path: Ruta del archivo PDF
        """
        try:
            # Extraer texto del PDF
            pdf_text = extract_text_from_pdf(pdf_path)
            if not pdf_text:
                print("❌ No se pudo extraer texto del PDF")
                return
            
            # Configurar gestor de preguntas
            self.question_manager = RandomQuestionManager(self.current_users)
            
            print("📚 Iniciando explicación con preguntas aleatorias...")
            
            # Simular proceso de explicación
            for i in range(3):  # 3 preguntas de ejemplo
                student, question, response = self.question_manager.conduct_random_question(
                    self.tts_manager, pdf_text
                )
                
                # Evaluar respuesta
                evaluation = self.openai_client.evaluate_student_answer(
                    question, response, pdf_text, student
                )
                
                self.tts_manager.speak(evaluation)
                time.sleep(2)
            
            # Mostrar estadísticas
            stats = self.question_manager.get_statistics()
            print(f"📊 Estadísticas: {stats}")
            
        except Exception as e:
            print(f"❌ Error en explicación con preguntas: {e}")
    
    def identify_users(self):
        """Identifica usuarios en la clase."""
        print("👥 Iniciando identificación de usuarios...")
        
        try:
            # Capturar frame
            frame = capture_frame()
            if frame is None:
                print("❌ No se pudo capturar frame")
                return
            
            # Reconocer usuario
            user_name, recognized = self.face_recognition.recognize_user(frame)
            
            if recognized:
                print(f"✅ Usuario reconocido: {user_name}")
                self.tts_manager.speak(f"Hola {user_name}, bienvenido a la clase")
            else:
                print("❓ Usuario no reconocido")
                
                # Preguntar nombre
                self.tts_manager.speak("¿Cuál es tu nombre?")
                name, success = self.speech_recognizer.listen(timeout=5)
                
                if success and name:
                    # Guardar nueva cara
                    if self.face_recognition.save_new_face(frame, name):
                        print(f"✅ Nueva cara guardada para {name}")
                        self.tts_manager.speak(f"Encantado de conocerte {name}")
                    else:
                        print("❌ Error al guardar cara")
                else:
                    print("❌ No se pudo obtener el nombre")
                    
        except Exception as e:
            print(f"❌ Error en identificación: {e}")
    
    def run_diagnostic_mode(self):
        """Ejecuta el modo de diagnóstico."""
        print("🔍 Iniciando modo diagnóstico...")
        
        # Mostrar QR de diagnóstico
        diagnostic_qr = settings.get_qr_path('diagnostic')
        if diagnostic_qr:
            self.show_diagnostic_qr(diagnostic_qr)
        
        # Identificar usuarios
        self.identify_users()
        
        print("✅ Modo diagnóstico completado")
    
    def run_presentation_mode(self, pdf_path: str):
        """
        Ejecuta el modo de presentación.
        
        Args:
            pdf_path: Ruta del archivo PDF
        """
        print("📖 Iniciando modo presentación...")
        
        try:
            # Iniciar proceso de cámara
            camera_thread = threading.Thread(target=self.camera_process)
            camera_thread.daemon = True
            camera_thread.start()
            
            # Explicar diapositivas con preguntas
            self.explain_slides_with_random_questions(pdf_path)
            
            # Esperar a que termine el proceso de cámara
            self.exit_flag.set()
            camera_thread.join()
            
            print("✅ Modo presentación completado")
            
        except Exception as e:
            print(f"❌ Error en modo presentación: {e}")
    
    def run_exam_mode(self, exam_type: str):
        """
        Ejecuta el modo de examen.
        
        Args:
            exam_type: Tipo de examen
        """
        print(f"📝 Iniciando modo examen: {exam_type}")
        
        # Mostrar QR de examen
        exam_qr = settings.get_qr_path(f'final_exam{exam_type}')
        if exam_qr:
            self.show_final_exam_qr(exam_qr)
        
        # Obtener preguntas del examen
        questions = self.exam_manager.get_exam_questions(exam_type)
        title = self.exam_manager.get_exam_title(exam_type)
        
        print(f"📋 Examen: {title}")
        print(f"📝 Preguntas: {len(questions)}")
        
        # Simular examen
        for i, question in enumerate(questions, 1):
            print(f"Pregunta {i}: {question}")
            self.tts_manager.speak(f"Pregunta {i}: {question}")
            time.sleep(3)
        
        print("✅ Modo examen completado")
    
    def cleanup(self):
        """Limpia los recursos del sistema."""
        print("🧹 Limpiando recursos...")
        
        self.exit_flag.set()
        self.tts_manager.cleanup()
        self.hand_detector.release()
        
        print("✅ Limpieza completada")
    
    def run(self):
        """Ejecuta el sistema principal."""
        try:
            print("🚀 Iniciando sistema ADAI...")
            
            # Mostrar cara del robot
            face_img = draw_fun_face(mouth_state=1)
            cv2.imshow("ADAI Robot", face_img)
            cv2.waitKey(2000)
            cv2.destroyAllWindows()
            
            # Menú principal
            while True:
                print("\n🤖 Sistema ADAI - Menú Principal")
                print("1. Modo Diagnóstico")
                print("2. Modo Presentación")
                print("3. Modo Examen")
                print("4. Salir")
                
                choice = input("Selecciona una opción: ")
                
                if choice == '1':
                    self.run_diagnostic_mode()
                elif choice == '2':
                    pdf_path = input("Ingresa la ruta del PDF: ")
                    self.run_presentation_mode(pdf_path)
                elif choice == '3':
                    print("Tipos de examen disponibles:")
                    print("- robots_medicos")
                    print("- exoesqueletos")
                    print("- iomt")
                    exam_type = input("Ingresa el tipo de examen: ")
                    self.run_exam_mode(exam_type)
                elif choice == '4':
                    break
                else:
                    print("❌ Opción no válida")
            
            print("👋 ¡Hasta luego!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Sistema interrumpido por el usuario")
        except Exception as e:
            print(f"❌ Error en el sistema: {e}")
        finally:
            self.cleanup()

def main():
    """Función principal."""
    system = ADAISystem()
    system.run()

if __name__ == "__main__":
    main() 