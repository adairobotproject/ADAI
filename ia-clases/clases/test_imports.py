"""
Script de prueba para verificar que todos los módulos se pueden importar correctamente
"""

def test_imports():
    """
    Prueba la importación de todos los módulos
    """
    print("🧪 Probando importaciones de módulos...")
    
    try:
        # Probar importación de config
        print("📋 Probando config...")
        from modules.config import get_qr_paths, QUESTION_BANK, OPENAI_API_KEY
        print("✅ config importado correctamente")
        
        # Probar importación de speech
        print("🗣️ Probando speech...")
        from modules.speech import initialize_tts, speak_with_animation, listen
        print("✅ speech importado correctamente")
        
        # Probar importación de camera
        print("🎥 Probando camera...")
        from modules.camera import verify_camera_for_iriun, camera_process
        print("✅ camera importado correctamente")
        
        # Probar importación de esp32
        print("🤖 Probando esp32...")
        from modules.esp32 import execute_esp32_sequence, esp32_action_resolver
        print("✅ esp32 importado correctamente")
        
        # Probar importación de qr
        print("📱 Probando qr...")
        from modules.qr import show_diagnostic_qr, show_final_exam_qr
        print("✅ qr importado correctamente")
        
        # Probar importación de questions
        print("❓ Probando questions...")
        from modules.questions import RandomQuestionManager, evaluate_student_answer
        print("✅ questions importado correctamente")
        
        # Probar importación de slides
        print("📚 Probando slides...")
        from modules.slides import extract_text_from_pdf, explain_slides_with_sequences
        print("✅ slides importado correctamente")
        
        # Probar importación de utils
        print("🔧 Probando utils...")
        from modules.utils import identify_users
        print("✅ utils importado correctamente")
        
        print("\n🎉 ¡Todas las importaciones fueron exitosas!")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_basic_functionality():
    """
    Prueba funcionalidad básica de algunos módulos
    """
    print("\n🔧 Probando funcionalidad básica...")
    
    try:
        # Probar configuración
        from modules.config import get_qr_paths, QUESTION_BANK
        script_dir = "."
        qr_paths = get_qr_paths(script_dir)
        print(f"✅ Configuración: {len(qr_paths)} rutas QR, {len(QUESTION_BANK)} preguntas")
        
        # Probar gestor de preguntas
        from modules.questions import RandomQuestionManager
        students = ["Ana", "Carlos", "María"]
        question_manager = RandomQuestionManager(students)
        print(f"✅ Gestor de preguntas: {len(question_manager.students)} estudiantes")
        
        # Probar selección de estudiante
        student, index = question_manager.select_random_student()
        print(f"✅ Estudiante seleccionado: {student} (índice {index})")
        
        print("🎉 ¡Funcionalidad básica probada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema modular ADAI")
    print("=" * 50)
    
    # Probar importaciones
    imports_ok = test_imports()
    
    if imports_ok:
        # Probar funcionalidad básica
        functionality_ok = test_basic_functionality()
        
        if functionality_ok:
            print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
            print("✅ El sistema modular está listo para usar")
        else:
            print("\n⚠️ Algunas pruebas de funcionalidad fallaron")
    else:
        print("\n❌ Las pruebas de importación fallaron")
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")
