"""
Ejemplo de uso de los módulos organizados del sistema ADAI
"""
import cv2
import time

# Importar módulos organizados
from config.settings import settings
from utils.file_utils import setup_directories, extract_text_from_pdf
from ai.openai_client import OpenAIClient
from vision.face_recognition_utils import FaceRecognitionManager, capture_frame
from vision.hand_detection import HandGestureDetector
from audio.tts_manager import TTSManager
from audio.speech_recognition_utils import SpeechRecognitionManager
from ui.animations import draw_fun_face, create_qr_display_frame
from exams.question_manager import RandomQuestionManager, ExamManager

def ejemplo_configuracion():
    """Ejemplo de uso de la configuración centralizada."""
    print("🔧 Ejemplo de configuración centralizada")
    
    # Configurar directorios
    setup_directories(settings.base_dir)
    
    # Obtener configuraciones
    camera_config = settings.get_camera_config()
    gesture_config = settings.get_gesture_config()
    
    print(f"📹 Configuración de cámara: {camera_config}")
    print(f"✋ Configuración de gestos: {gesture_config}")
    
    # Obtener rutas de QR
    diagnostic_qr = settings.get_qr_path('diagnostic')
    print(f"📱 QR de diagnóstico: {diagnostic_qr}")

def ejemplo_ai():
    """Ejemplo de uso del módulo de inteligencia artificial."""
    print("\n🤖 Ejemplo de inteligencia artificial")
    
    # Inicializar cliente OpenAI
    openai_client = OpenAIClient(settings.openai_api_key)
    
    # Hacer una pregunta
    question = "¿Qué es la robótica médica?"
    context = "La robótica médica es una rama de la ingeniería que combina..."
    
    response = openai_client.ask_openai(question, context)
    print(f"❓ Pregunta: {question}")
    print(f"🤖 Respuesta: {response}")
    
    # Evaluar respuesta de estudiante
    student_answer = "La robótica médica ayuda en cirugías"
    evaluation = openai_client.evaluate_student_answer(
        question, student_answer, context, "Juan"
    )
    print(f"📝 Evaluación: {evaluation}")

def ejemplo_vision():
    """Ejemplo de uso del módulo de visión por computadora."""
    print("\n👁️ Ejemplo de visión por computadora")
    
    # Inicializar reconocimiento facial
    face_manager = FaceRecognitionManager(settings.paths['faces_dir'])
    
    # Capturar frame
    frame = capture_frame()
    if frame is not None:
        # Reconocer usuario
        user_name, recognized = face_manager.recognize_user(frame)
        
        if recognized:
            print(f"✅ Usuario reconocido: {user_name}")
        else:
            print("❓ Usuario no reconocido")
            
            # Guardar nueva cara
            if face_manager.save_new_face(frame, "Nuevo_Usuario"):
                print("✅ Nueva cara guardada")
    
    # Inicializar detector de gestos
    hand_detector = HandGestureDetector()
    
    # Simular detección de gestos
    if frame is not None:
        hand_raised, hands_detected = hand_detector.detect_hand_raise(frame)
        
        if hand_raised:
            print("✋ Mano levantada detectada!")
        
        if hands_detected:
            print(f"👐 {len(hands_detected)} manos detectadas")

def ejemplo_audio():
    """Ejemplo de uso del módulo de audio."""
    print("\n🎵 Ejemplo de audio")
    
    # Inicializar TTS
    tts_manager = TTSManager()
    
    # Hablar texto
    tts_manager.speak("Hola, soy ADAI, tu asistente docente")
    
    # Cambiar velocidad
    tts_manager.set_rate(120)
    tts_manager.speak("Velocidad más lenta")
    
    # Cambiar volumen
    tts_manager.set_volume(0.7)
    tts_manager.speak("Volumen reducido")
    
    # Inicializar reconocimiento de voz
    speech_recognizer = SpeechRecognitionManager()
    
    print("🎤 Escuchando por 5 segundos...")
    text, success = speech_recognizer.listen(timeout=5)
    
    if success:
        print(f"✅ Reconocido: {text}")
    else:
        print("❌ No se pudo reconocer audio")

def ejemplo_ui():
    """Ejemplo de uso del módulo de interfaz de usuario."""
    print("\n🎨 Ejemplo de interfaz de usuario")
    
    # Crear cara del robot
    face_img = draw_fun_face(mouth_state=1)
    
    # Mostrar cara
    cv2.imshow("ADAI Robot", face_img)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()
    
    # Crear frame de QR
    qr_path = settings.get_qr_path('diagnostic')
    if qr_path:
        qr_frame = create_qr_display_frame(qr_path, "Ejemplo QR", "Escanea este código")
        
        # Mostrar QR
        cv2.imshow("QR Ejemplo", qr_frame)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()

def ejemplo_exams():
    """Ejemplo de uso del módulo de exámenes."""
    print("\n📝 Ejemplo de exámenes")
    
    # Inicializar gestores
    question_manager = RandomQuestionManager(["Juan", "María", "Pedro"])
    exam_manager = ExamManager()
    
    # Seleccionar pregunta aleatoria
    question = question_manager.select_random_question()
    student = question_manager.select_random_student()
    
    print(f"👤 Estudiante: {student}")
    print(f"❓ Pregunta: {question}")
    
    # Obtener preguntas de examen
    exam_questions = exam_manager.get_exam_questions('robots_medicos')
    exam_title = exam_manager.get_exam_title('robots_medicos')
    
    print(f"📋 Examen: {exam_title}")
    print(f"📝 Preguntas: {len(exam_questions)}")
    
    for i, q in enumerate(exam_questions, 1):
        print(f"  {i}. {q}")
    
    # Mostrar estadísticas
    stats = question_manager.get_statistics()
    print(f"📊 Estadísticas: {stats}")

def ejemplo_utils():
    """Ejemplo de uso del módulo de utilidades."""
    print("\n🛠️ Ejemplo de utilidades")
    
    # Extraer texto de PDF
    pdf_path = "ejemplo.pdf"  # Ruta de ejemplo
    try:
        text = extract_text_from_pdf(pdf_path)
        if text:
            print(f"📄 Texto extraído: {text[:100]}...")
        else:
            print("❌ No se pudo extraer texto del PDF")
    except FileNotFoundError:
        print("📄 Archivo PDF no encontrado (ejemplo)")
    
    # Configurar directorios
    directories = setup_directories(settings.base_dir)
    print(f"📁 Directorios configurados: {list(directories.keys())}")

def main():
    """Función principal del ejemplo."""
    print("🚀 Ejemplos de uso de módulos ADAI")
    print("=" * 50)
    
    try:
        # Ejecutar ejemplos
        ejemplo_configuracion()
        ejemplo_ai()
        ejemplo_vision()
        ejemplo_audio()
        ejemplo_ui()
        ejemplo_exams()
        ejemplo_utils()
        
        print("\n✅ Todos los ejemplos completados exitosamente")
        
    except Exception as e:
        print(f"❌ Error en ejemplo: {e}")
    
    finally:
        # Limpiar recursos
        cv2.destroyAllWindows()
        print("\n🧹 Recursos limpiados")

if __name__ == "__main__":
    main() 