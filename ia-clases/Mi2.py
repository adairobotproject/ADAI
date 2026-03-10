#!/usr/bin/env python3
"""
Mi Clase de Robótica
Materia: Robots Médicos
Generado por ADAI Class Builder el 2025-08-30 17:05:26

Clase automática basada en el flujo de main.py
"""

import cv2
import numpy as np
import pyttsx3
import speech_recognition as sr
import os
import fitz
import openai
import time
import multiprocessing
from multiprocessing import Process, Value, Event
import random
import winsound

# ======================
#  CONFIGURACIÓN OPENAI
# ======================
try:
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"⚠️ OpenAI no disponible: {e}")
    client = None

# Obtener directorio actual
script_dir = os.path.dirname(os.path.abspath(__file__))

# ======================
#  RUTAS DE ARCHIVOS
# ======================
QR_PATHS = {
    'diagnostic': os.path.join(script_dir, "C:/Users/josue/Downloads/download (1).jpg"),
    'final_exam': os.path.join(script_dir, "RobotsMedicosExamen/RobotsMedicosExamenI.jpeg")
}

PDF_PATH = os.path.join(script_dir, "C:/Users/josue/Desktop/RobotAtlas/ia-clases/DefensaTesis2.pdf")

class Mi_Clase_de_Robótica:
    """Clase generada automáticamente por ADAI Class Builder"""
    
    def __init__(self):
        print("🚀" + "="*60)
        print(f"🤖 ADAI - Mi Clase de Robótica")
        print(f"📚 Materia: Robots Médicos")
        print("🚀" + "="*60)
        
        self.class_title = "Mi Clase de Robótica"
        self.class_subject = "Robots Médicos"
        self.diagnostic_qr = QR_PATHS['diagnostic']
        self.class_pdf = PDF_PATH
        self.final_exam_qr = QR_PATHS['final_exam']
        
        # Variables para simulación
        self.hand_raised_counter = multiprocessing.Value('i', 0)
        self.current_slide_num = multiprocessing.Value('i', 1)
        self.exit_flag = multiprocessing.Value('i', 0)
        self.current_hand_raiser = multiprocessing.Value('i', -1)
        
        # Inicializar TTS
        self.engine = self.initialize_tts()
        
    def initialize_tts(self):
        """Inicializar motor de texto a voz"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0')
            return engine
        except Exception as e:
            print(f"❌ Error al inicializar TTS: " + str(e))
            return None
    
    def speak_with_animation(self, text):
        """Hablar texto con animación simple"""
        print(f"🗣️ ADAI: " + text)
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"❌ Error en TTS: " + str(e))
        time.sleep(1)
    
    def show_diagnostic_qr(self, display_time=15):
        """Mostrar QR de evaluación diagnóstica"""
        try:
            print("📱 Mostrando código QR para evaluación diagnóstica...")
            
            if not os.path.exists(self.diagnostic_qr):
                print(f"⚠️ No se encontró el QR diagnóstico: " + str(self.diagnostic_qr))
                return False
            
            # Cargar imagen del QR
            qr_image = cv2.imread(self.diagnostic_qr)
            if qr_image is None:
                print(f"❌ Error: No se pudo cargar la imagen QR")
                return False
            
            # Crear ventana y mostrar QR
            cv2.namedWindow("Evaluación Diagnóstica", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Evaluación Diagnóstica", 800, 600)
            
            # Redimensionar QR para visualización
            qr_resized = cv2.resize(qr_image, (600, 600))
            
            # Crear canvas con información
            canvas = np.full((700, 800, 3), (240, 240, 240), dtype=np.uint8)
            
            # Insertar QR en el centro
            start_x = (800 - 600) // 2
            start_y = 50
            canvas[start_y:start_y + 600, start_x:start_x + 600] = qr_resized
            
            # Añadir texto
            cv2.putText(canvas, self.class_title, (50, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            cv2.putText(canvas, "Escanea el codigo QR para la evaluacion diagnostica", 
                       (50, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Mostrar por el tiempo especificado
            start_time = time.time()
            while time.time() - start_time < display_time:
                cv2.imshow("Evaluación Diagnóstica", canvas)
                if cv2.waitKey(1000) & 0xFF == ord('q'):
                    break
            
            cv2.destroyWindow("Evaluación Diagnóstica")
            print("✅ QR diagnóstico mostrado")
            return True
            
        except Exception as e:
            print(f"❌ Error mostrando QR diagnóstico: " + str(e))
            return False
    
    def show_final_exam_qr(self, display_time=20):
        """Mostrar QR de examen final"""
        try:
            print("📋 Mostrando código QR para examen final...")
            
            if not os.path.exists(self.final_exam_qr):
                print(f"⚠️ No se encontró el QR de examen: " + str(self.final_exam_qr))
                return False
            
            # Cargar imagen del QR
            qr_image = cv2.imread(self.final_exam_qr)
            if qr_image is None:
                print(f"❌ Error: No se pudo cargar la imagen QR del examen")
                return False
            
            # Crear ventana y mostrar QR
            cv2.namedWindow("Examen Final", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Examen Final", 800, 600)
            
            # Redimensionar QR para visualización
            qr_resized = cv2.resize(qr_image, (600, 600))
            
            # Crear canvas con información
            canvas = np.full((700, 800, 3), (245, 245, 255), dtype=np.uint8)
            
            # Insertar QR en el centro
            start_x = (800 - 600) // 2
            start_y = 50
            canvas[start_y:start_y + 600, start_x:start_x + 600] = qr_resized
            
            # Añadir texto
            cv2.putText(canvas, f"EXAMEN FINAL - " + self.class_subject.upper(), (50, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(canvas, "Escanea el codigo QR para acceder al examen final", 
                       (50, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Mostrar por el tiempo especificado
            start_time = time.time()
            while time.time() - start_time < display_time:
                cv2.imshow("Examen Final", canvas)
                if cv2.waitKey(1000) & 0xFF == ord('q'):
                    break
            
            cv2.destroyWindow("Examen Final")
            print("✅ QR examen final mostrado")
            return True
            
        except Exception as e:
            print(f"❌ Error mostrando QR examen: " + str(e))
            return False
    
    def extract_text_from_pdf(self):
        """Extraer texto del PDF de la clase"""
        try:
            if not os.path.exists(self.class_pdf):
                print(f"⚠️ No se encontró el PDF: " + str(self.class_pdf))
                return "Contenido de la clase sobre " + self.class_subject
            
            text = ""
            with fitz.open(self.class_pdf) as doc:
                for page in doc:
                    text += page.get_text()
            
            print(f"✅ PDF cargado: " + str(len(text)) + " caracteres")
            return text
            
        except Exception as e:
            print(f"❌ Error al leer PDF: " + str(e))
            return "Contenido de la clase sobre " + self.class_subject
    
    def show_pdf_slides(self, pdf_text):
        """Mostrar diapositivas del PDF y explicar"""
        try:
            if not os.path.exists(self.class_pdf):
                print(f"⚠️ PDF no encontrado, simulando presentación...")
                self.simulate_presentation()
                return True
            
            print("📊 Iniciando presentación...")
            
            # Crear ventana para presentación
            cv2.namedWindow("Presentacion", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Presentacion", 800, 600)
            
            with fitz.open(self.class_pdf) as doc:
                total_slides = len(doc)
                
                for slide_num in range(total_slides):
                    self.current_slide_num.value = slide_num + 1
                    print(f"📝 Diapositiva {slide_num + 1} de {total_slides}")
                    
                    # Obtener página
                    page = doc[slide_num]
                    
                    # Convertir página a imagen
                    pix = page.get_pixmap()
                    img_data = np.frombuffer(pix.samples, dtype=np.uint8)
                    img = img_data.reshape((pix.h, pix.w, pix.n))
                    
                    if pix.n == 4:  # RGBA
                        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                    elif pix.n == 3:  # RGB
                        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    else:  # Escala de grises
                        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    
                    # Mostrar diapositiva
                    cv2.imshow("Presentacion", img_bgr)
                    cv2.waitKey(100)
                    
                    # Obtener texto de la página
                    page_text = page.get_text()
                    
                    # Explicar diapositiva
                    if page_text.strip():
                        explanation = f"Diapositiva " + str(slide_num + 1) + ": " + page_text[:200] + "..."
                    else:
                        explanation = f"Diapositiva " + str(slide_num + 1) + " contiene elementos visuales sobre " + self.class_subject
                    
                    self.speak_with_animation(explanation)
                    
                    # Pausa entre diapositivas
                    time.sleep(2)
            
            cv2.destroyWindow("Presentacion")
            return True
            
        except Exception as e:
            print(f"❌ Error mostrando PDF: " + str(e))
            self.simulate_presentation()
            return True
    
    def simulate_presentation(self):
        """Simular presentación cuando no hay PDF"""
        print("🎭 Simulando presentación...")
        
        slides_content = [
            f"Introducción a " + self.class_subject,
            f"Conceptos fundamentales de " + self.class_subject,
            f"Aplicaciones prácticas en " + self.class_subject,
            f"Casos de estudio en " + self.class_subject,
            f"Futuro y tendencias en " + self.class_subject,
            f"Conclusiones sobre " + self.class_subject
        ]
        
        for i, content in enumerate(slides_content):
            self.current_slide_num.value = i + 1
            print(f"📝 Diapositiva simulada " + str(i + 1) + "/" + str(len(slides_content)))
            self.speak_with_animation(content)
            time.sleep(3)
    
    def run(self):
        """Ejecutar la clase completa siguiendo el flujo de main.py"""
        try:
            print("\n" + "="*60)
            print("📱 FASE 1: EVALUACIÓN DIAGNÓSTICA")
            print("="*60)
            
            # Mostrar evaluación diagnóstica
            self.speak_with_animation("Bienvenidos a la clase. Comenzaremos con una evaluación diagnóstica.")
            self.show_diagnostic_qr(display_time=15)
            
            print("\n" + "="*60)
            print("🤖 FASE 2: INICIO DE CLASE")
            print("="*60)
            
            # Saludo e introducción
            self.speak_with_animation(f"Hola, soy ADAI. Hoy estudiaremos " + self.class_subject + ".")
            
            # Extraer texto del PDF
            pdf_text = self.extract_text_from_pdf()
            
            # Introducción al tema
            self.speak_with_animation(f"En esta clase exploraremos los aspectos fundamentales de " + self.class_subject + ".")
            
            print("\n" + "="*60)
            print("📚 FASE 3: CONTENIDO PRINCIPAL")
            print("="*60)
            
            # Mostrar presentación
            self.speak_with_animation("Ahora comenzaremos con la presentación principal.")
            self.show_pdf_slides(pdf_text)
            
            print("\n" + "="*60)
            print("🎓 FASE 4: EXAMEN FINAL")  
            print("="*60)
            
            # Examen final
            self.speak_with_animation("Excelente trabajo. Ahora es momento del examen final.")
            self.speak_with_animation("Por favor, escanea el código QR que aparecerá en pantalla.")
            self.show_final_exam_qr(display_time=20)
            
            # Mensaje final
            self.speak_with_animation("Perfecto. Mucha suerte en el examen.")
            self.speak_with_animation("Gracias por participar en esta clase con ADAI. Hasta la próxima.")
            
            print("\n" + "="*60)
            print("✅ CLASE COMPLETADA EXITOSAMENTE")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error durante la ejecución: " + str(e))
            import traceback
            traceback.print_exc()
        finally:
            # Limpiar recursos
            cv2.destroyAllWindows()
            print("🧹 Recursos liberados")

def main():
    """Función principal"""
    print("🚀 Iniciando clase generada por ADAI Class Builder...")
    
    try:
        # Crear y ejecutar la clase
        clase = Mi_Clase_de_Robótica()
        clase.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Clase interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: " + str(e))
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()
        print("👋 Fin de la clase")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
