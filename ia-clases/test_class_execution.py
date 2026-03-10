#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que las clases modulares se ejecutan correctamente
"""

import os
import sys
import subprocess
import tempfile

def test_modular_class_execution():
    """Test que una clase modular se puede ejecutar correctamente"""
    print("🧪 Test de ejecución de clase modular")
    print("="*50)
    
    # Crear una clase modular de prueba
    test_class_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clase de prueba modular
"""

import cv2
import os
import time
import multiprocessing
from multiprocessing import Process, Value

# Agregar el directorio de módulos al path
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, "modules")
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

# Import modular functions
from modules.config import client, script_dir, faces_dir
from modules.speech import initialize_tts, speak_with_animation

class TestModularClass:
    """Clase de prueba modular"""
    
    def __init__(self):
        self.config = {
            "name": "TestModularClass",
            "title": "Clase de Prueba Modular"
        }
        self.engine = None
        
    def initialize_systems(self):
        """Initialize TTS and other systems"""
        print("🚀 Inicializando sistemas de prueba...")
        
        # Initialize TTS
        self.engine = initialize_tts()
        if not self.engine:
            print("❌ No se pudo inicializar el motor TTS")
            return False
            
        return True
    
    def run_test(self):
        """Run a simple test"""
        try:
            print(f"🚀 Iniciando clase de prueba: {self.config['title']}")
            
            # Initialize systems
            if not self.initialize_systems():
                return False
            
            # Test simple
            speak_with_animation(self.engine, "Esta es una clase de prueba modular.")
            time.sleep(1)
            speak_with_animation(self.engine, "La estructura modular está funcionando correctamente.")
            
            print("✅ Clase de prueba completada exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error en clase de prueba: {e}")
            return False

def main():
    """Main function to run the test class"""
    try:
        # Create and run the test class
        class_instance = TestModularClass()
        success = class_instance.run_test()
        
        if success:
            print("✅ Test completado exitosamente")
        else:
            print("❌ Test falló")
            
    except Exception as e:
        print(f"❌ Error en main: {e}")
        return False
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
'''
    
    # Crear directorio temporal para la clase
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Directorio temporal: {temp_dir}")
        
        # Crear la clase de prueba
        class_file = os.path.join(temp_dir, "test_modular_class.py")
        with open(class_file, 'w', encoding='utf-8') as f:
            f.write(test_class_code)
        
        # Crear directorio modules simulado
        modules_dir = os.path.join(temp_dir, "modules")
        os.makedirs(modules_dir, exist_ok=True)
        
        # Crear __init__.py
        init_file = os.path.join(modules_dir, "__init__.py")
        with open(init_file, 'w') as f:
            f.write("# Modules package")
        
        # Crear config.py simulado
        config_code = '''import openai
import os

# Configuración simulada
client = openai.OpenAI(api_key="test-key")
script_dir = os.path.dirname(os.path.abspath(__file__))
faces_dir = os.path.join(script_dir, "faces")
'''
        config_file = os.path.join(modules_dir, "config.py")
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_code)
        
        # Crear speech.py simulado
        speech_code = '''import pyttsx3

def initialize_tts():
    """Initialize TTS engine"""
    try:
        engine = pyttsx3.init()
        return engine
    except Exception as e:
        print(f"Error inicializando TTS: {e}")
        return None

def speak_with_animation(engine, text):
    """Speak text with animation"""
    print(f"🗣️ ADAI dice: {text}")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error en TTS: {e}")
    import time
    time.sleep(0.5)
'''
        speech_file = os.path.join(modules_dir, "speech.py")
        with open(speech_file, 'w', encoding='utf-8') as f:
            f.write(speech_code)
        
        print("📝 Archivos de prueba creados")
        
        # Ejecutar la clase de prueba
        try:
            print("🚀 Ejecutando clase de prueba...")
            result = subprocess.run([sys.executable, class_file], 
                                  cwd=temp_dir,
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            
            print("📤 Salida:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Errores:")
                print(result.stderr)
            
            if result.returncode == 0:
                print("✅ Clase modular ejecutada exitosamente")
                return True
            else:
                print(f"❌ Clase falló con código: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout ejecutando la clase")
            return False
        except Exception as e:
            print(f"❌ Error ejecutando clase: {e}")
            return False

def main():
    """Ejecutar test de ejecución"""
    print("🚀 Test de Ejecución de Clases Modulares")
    print("="*60)
    
    success = test_modular_class_execution()
    
    if success:
        print("\n🎉 ¡Test exitoso!")
        print("✅ Las clases modulares se pueden ejecutar correctamente")
    else:
        print("\n❌ Test falló")
        print("⚠️ Hay problemas con la ejecución de clases modulares")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

