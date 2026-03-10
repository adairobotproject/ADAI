#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador Automático de Clase de Química
===========================================

Script para configurar automáticamente la clase de química usando el Class Builder
"""

import os
import sys
import json
import datetime
from pathlib import Path

def configurar_clase_quimica():
    """Configurar la clase de química automáticamente"""
    
    print("🧪 Configurando Clase de Química...")
    print("="*50)
    
    # Rutas de archivos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clases_dir = os.path.join(script_dir, "clases")
    quimica_dir = os.path.join(clases_dir, "clase_quimica")
    
    # Verificar que existen los archivos
    pdf_principal = os.path.join(quimica_dir, "Clase_Neutralizacion_Bicarbonato.pdf")
    pdf_demo = os.path.join(quimica_dir, "Demo_Paso_a_Paso.pdf")
    
    if not os.path.exists(pdf_principal):
        print(f"❌ No se encontró: {pdf_principal}")
        return False
    
    if not os.path.exists(pdf_demo):
        print(f"❌ No se encontró: {pdf_demo}")
        return False
    
    print("✅ Archivos PDF encontrados")
    
    # Crear la clase usando el Class Builder
    from tabs.class_builder_tab import ClassBuilderTab
    from class_manager import get_class_manager
    
    # Obtener el class manager
    class_manager = get_class_manager()
    
    # Configuración de la clase
    class_config = {
        "title": "Neutralización con Bicarbonato de Sodio",
        "subject": "Química",
        "description": "Clase práctica sobre neutralización de ácidos usando bicarbonato de sodio",
        "duration": "60 minutos",
        "pdf_path": pdf_principal,
        "demo_pdf_path": pdf_demo
    }
    
    # Generar código de la clase
    class_code = generar_codigo_clase_quimica(class_config)
    
    # Guardar la clase
    class_name = "clase_quimica_neutralizacion"
    success = class_manager.save_class_file(
        class_name=class_name,
        content=class_code,
        title=class_config["title"],
        subject=class_config["subject"],
        description=class_config["description"],
        duration=class_config["duration"]
    )
    
    if success:
        print(f"✅ Clase guardada: {class_name}")
        
        # Agregar recursos
        class_manager.add_resource_to_class(class_name, pdf_principal, "pdfs")
        class_manager.add_resource_to_class(class_name, pdf_demo, "pdfs")
        
        print("✅ Recursos agregados")
        
        # Crear metadata adicional
        crear_metadata_quimica(class_name, class_config)
        
        print("🎉 Clase de química configurada exitosamente!")
        return True
    else:
        print("❌ Error guardando la clase")
        return False

def generar_codigo_clase_quimica(config):
    """Generar el código específico para la clase de química"""
    
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{config['title']}
Materia: {config['subject']}
Generado automáticamente el {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Clase especializada en química con demostración práctica
"""

import cv2
import numpy as np
import pyttsx3
import speech_recognition as sr
import os
import fitz
import time
import multiprocessing
from multiprocessing import Process, Value, Event
import random
import winsound
import sys

# Configurar codificación para Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class ClaseQuimicaNeutralizacion:
    """Clase especializada en neutralización con bicarbonato de sodio"""
    
    def __init__(self):
        print("="*60)
        print("🧪 ADAI - Clase de Química")
        print("📚 Tema: Neutralización con Bicarbonato de Sodio")
        print("="*60)
        
        self.class_title = "{config['title']}"
        self.class_subject = "{config['subject']}"
        self.class_description = "{config['description']}"
        self.duration = "{config['duration']}"
        
        # Rutas de archivos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.pdf_principal = os.path.join(script_dir, "Clase_Neutralizacion_Bicarbonato.pdf")
        self.pdf_demo = os.path.join(script_dir, "Demo_Paso_a_Paso.pdf")
        
        # Variables para simulación
        self.hand_raised_counter = multiprocessing.Value('i', 0)
        self.current_slide_num = multiprocessing.Value('i', 1)
        self.exit_flag = multiprocessing.Value('i', 0)
        self.current_hand_raiser = multiprocessing.Value('i', -1)
        
        # Inicializar TTS
        self.engine = self.initialize_tts()
        
        # Configuración específica para química
        self.experiment_phases = [
            "Preparación de materiales",
            "Identificación de reactivos",
            "Medición de volúmenes",
            "Mezcla controlada",
            "Observación de reacción",
            "Registro de resultados"
        ]
        
    def initialize_tts(self):
        """Inicializar motor de texto a voz"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\\\SOFTWARE\\\\Microsoft\\\\Speech\\\\Voices\\\\Tokens\\\\TTS_MS_ES-MX_SABINA_11.0')
            return engine
        except Exception as e:
            print(f"ERROR: Error al inicializar TTS: {{e}}")
            return None
    
    def speak_with_animation(self, text):
        """Hablar texto con animación simple"""
        print(f"🧪 ADAI dice: {{text}}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"ERROR en TTS: {{e}}")
        time.sleep(1)
    
    def show_experiment_intro(self):
        """Mostrar introducción al experimento"""
        try:
            print("🧪 Mostrando introducción al experimento...")
            
            # Crear ventana para introducción
            cv2.namedWindow("Experimento de Química", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Experimento de Química", 1000, 700)
            
            # Crear canvas con información del experimento
            canvas = np.full((700, 1000, 3), (240, 248, 255), dtype=np.uint8)  # Alice blue
            
            # Header
            cv2.rectangle(canvas, (0, 0), (1000, 120), (25, 25, 112), -1)  # Midnight blue
            
            # Título
            title = "EXPERIMENTO DE NEUTRALIZACION"
            cv2.putText(canvas, title, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            
            # Subtítulo
            subtitle = "Bicarbonato de Sodio + Acido"
            cv2.putText(canvas, subtitle, (50, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Información del experimento
            info_y = 150
            info_lines = [
                "Objetivo: Observar la reacción de neutralización",
                "Materiales: Bicarbonato de sodio, ácido cítrico, agua",
                "Tiempo estimado: 30 minutos",
                "Nivel de seguridad: Bajo (supervisión requerida)",
                "",
                "Fases del experimento:",
                "1. Preparación de materiales",
                "2. Identificación de reactivos", 
                "3. Medición de volúmenes",
                "4. Mezcla controlada",
                "5. Observación de reacción",
                "6. Registro de resultados"
            ]
            
            for i, line in enumerate(info_lines):
                color = (25, 25, 112) if i < 5 else (0, 100, 0)  # Azul para info, verde para fases
                cv2.putText(canvas, line, (50, info_y + i * 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Mostrar por 10 segundos
            start_time = time.time()
            while time.time() - start_time < 10:
                cv2.imshow("Experimento de Química", canvas)
                if cv2.waitKey(1000) & 0xFF == ord('q'):
                    break
            
            cv2.destroyWindow("Experimento de Química")
            print("✅ Introducción mostrada")
            return True
            
        except Exception as e:
            print(f"ERROR mostrando introducción: {{e}}")
            return False
    
    def show_safety_guidelines(self):
        """Mostrar guías de seguridad"""
        try:
            print("🛡️ Mostrando guías de seguridad...")
            
            cv2.namedWindow("Guías de Seguridad", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Guías de Seguridad", 900, 600)
            
            canvas = np.full((600, 900, 3), (255, 248, 220), dtype=np.uint8)  # Cornsilk
            
            # Header de seguridad
            cv2.rectangle(canvas, (0, 0), (900, 100), (220, 20, 60), -1)  # Crimson
            
            # Título
            cv2.putText(canvas, "GUÍAS DE SEGURIDAD", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
            cv2.putText(canvas, "Experimento de Química", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Guías de seguridad
            safety_y = 130
            safety_guidelines = [
                "1. Usar bata de laboratorio y gafas de seguridad",
                "2. Trabajar en área bien ventilada",
                "3. No ingerir ningún reactivo",
                "4. Lavar manos después del experimento",
                "5. Mantener reactivos fuera del alcance de niños",
                "6. En caso de contacto con ojos, lavar con agua abundante",
                "7. Disponer residuos según protocolo del laboratorio",
                "8. Reportar cualquier incidente al instructor"
            ]
            
            for i, guideline in enumerate(safety_guidelines):
                color = (220, 20, 60) if i < 3 else (25, 25, 112)  # Rojo para críticas, azul para generales
                cv2.putText(canvas, guideline, (50, safety_y + i * 35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Mostrar por 15 segundos
            start_time = time.time()
            while time.time() - start_time < 15:
                cv2.imshow("Guías de Seguridad", canvas)
                if cv2.waitKey(1000) & 0xFF == ord('q'):
                    break
            
            cv2.destroyWindow("Guías de Seguridad")
            print("✅ Guías de seguridad mostradas")
            return True
            
        except Exception as e:
            print(f"ERROR mostrando guías de seguridad: {{e}}")
            return False
    
    def show_experiment_phase(self, phase_name, phase_description, duration=8):
        """Mostrar una fase específica del experimento"""
        try:
            print(f"🧪 Mostrando fase: {{phase_name}}")
            
            cv2.namedWindow("Fase del Experimento", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Fase del Experimento", 800, 600)
            
            canvas = np.full((600, 800, 3), (245, 245, 245), dtype=np.uint8)  # White smoke
            
            # Header de fase
            cv2.rectangle(canvas, (0, 0), (800, 100), (34, 139, 34), -1)  # Forest green
            
            # Título de la fase
            cv2.putText(canvas, f"FASE: {{phase_name.upper()}}", (50, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
            
            # Descripción
            cv2.putText(canvas, phase_description, (50, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Contenido de la fase
            content_y = 130
            content_lines = [
                f"Instrucciones para {{phase_name.lower()}}:",
                "",
                "• Seguir el protocolo establecido",
                "• Registrar observaciones",
                "• Mantener orden en el área de trabajo",
                "• Consultar al instructor si hay dudas",
                "",
                "Tiempo estimado: 5-10 minutos",
                "",
                "Presiona 'Q' para continuar"
            ]
            
            for i, line in enumerate(content_lines):
                color = (25, 25, 112) if i == 0 else (0, 0, 0)
                cv2.putText(canvas, line, (50, content_y + i * 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Mostrar por el tiempo especificado
            start_time = time.time()
            while time.time() - start_time < duration:
                cv2.imshow("Fase del Experimento", canvas)
                if cv2.waitKey(1000) & 0xFF == ord('q'):
                    break
            
            cv2.destroyWindow("Fase del Experimento")
            print(f"✅ Fase {{phase_name}} mostrada")
            return True
            
        except Exception as e:
            print(f"ERROR mostrando fase {{phase_name}}: {{e}}")
            return False
    
    def show_pdf_slides(self, pdf_path):
        """Mostrar diapositivas del PDF"""
        try:
            if not os.path.exists(pdf_path):
                print(f"PDF no encontrado: {{pdf_path}}")
                return False
            
            print("📚 Mostrando presentación del PDF...")
            
            cv2.namedWindow("Presentación Química", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Presentación Química", 800, 600)
            
            with fitz.open(pdf_path) as doc:
                total_slides = len(doc)
                
                for slide_num in range(total_slides):
                    self.current_slide_num.value = slide_num + 1
                    print(f"Diapositiva {{slide_num + 1}} de {{total_slides}}")
                    
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
                    cv2.imshow("Presentación Química", img_bgr)
                    cv2.waitKey(100)
                    
                    # Obtener texto de la página
                    page_text = page.get_text()
                    
                    # Explicar diapositiva
                    if page_text.strip():
                        explanation = f"Diapositiva {{slide_num + 1}}: {{page_text[:200]}}..."
                    else:
                        explanation = f"Diapositiva {{slide_num + 1}} contiene elementos visuales sobre neutralización química"
                    
                    self.speak_with_animation(explanation)
                    
                    # Pausa entre diapositivas
                    time.sleep(3)
            
            cv2.destroyWindow("Presentación Química")
            return True
            
        except Exception as e:
            print(f"ERROR mostrando PDF: {{e}}")
            return False
    
    def show_results_analysis(self):
        """Mostrar análisis de resultados"""
        try:
            print("📊 Mostrando análisis de resultados...")
            
            cv2.namedWindow("Análisis de Resultados", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Análisis de Resultados", 900, 700)
            
            canvas = np.full((700, 900, 3), (248, 248, 255), dtype=np.uint8)  # Ghost white
            
            # Header
            cv2.rectangle(canvas, (0, 0), (900, 120), (75, 0, 130), -1)  # Indigo
            
            # Título
            cv2.putText(canvas, "ANÁLISIS DE RESULTADOS", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
            cv2.putText(canvas, "Neutralización con Bicarbonato", (50, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Contenido del análisis
            content_y = 150
            analysis_content = [
                "Resultados Esperados:",
                "",
                "• Formación de burbujas (CO2)",
                "• Cambio de temperatura",
                "• Neutralización del pH",
                "• Formación de sales",
                "",
                "Observaciones Importantes:",
                "",
                "• Velocidad de reacción",
                "• Cantidad de gas producido",
                "• Cambios de color",
                "• Temperatura final",
                "",
                "Conclusiones:",
                "",
                "• El bicarbonato actúa como base",
                "• La reacción es exotérmica",
                "• Se produce dióxido de carbono",
                "• El pH se neutraliza"
            ]
            
            for i, line in enumerate(analysis_content):
                if line.startswith("•"):
                    color = (0, 100, 0)  # Verde para puntos
                elif line.endswith(":"):
                    color = (75, 0, 130)  # Indigo para títulos
                else:
                    color = (25, 25, 112)  # Azul para texto
                
                cv2.putText(canvas, line, (50, content_y + i * 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Mostrar por 20 segundos
            start_time = time.time()
            while time.time() - start_time < 20:
                cv2.imshow("Análisis de Resultados", canvas)
                if cv2.waitKey(1000) & 0xFF == ord('q'):
                    break
            
            cv2.destroyWindow("Análisis de Resultados")
            print("✅ Análisis de resultados mostrado")
            return True
            
        except Exception as e:
            print(f"ERROR mostrando análisis: {{e}}")
            return False
    
    def run(self):
        """Ejecutar la clase completa de química"""
        try:
            print("\\n" + "="*60)
            print("🧪 INICIANDO CLASE DE QUÍMICA")
            print("="*60)
            
            # Saludo inicial
            self.speak_with_animation("Bienvenidos a la clase de química. Soy ADAI, su asistente de laboratorio.")
            self.speak_with_animation("Hoy estudiaremos la neutralización usando bicarbonato de sodio.")
            
            # Mostrar introducción al experimento
            self.show_experiment_intro()
            
            # Mostrar guías de seguridad
            self.speak_with_animation("Antes de comenzar, revisemos las guías de seguridad.")
            self.show_safety_guidelines()
            
            # Presentación teórica
            self.speak_with_animation("Ahora revisaremos la teoría detrás de la neutralización.")
            self.show_pdf_slides(self.pdf_principal)
            
            # Fases del experimento
            self.speak_with_animation("Excelente. Ahora procederemos con las fases del experimento.")
            
            phase_descriptions = [
                "Preparación de materiales - Organizar todos los reactivos y equipos necesarios",
                "Identificación de reactivos - Verificar las propiedades de cada sustancia",
                "Medición de volúmenes - Calcular las cantidades exactas para la reacción",
                "Mezcla controlada - Combinar los reactivos de manera segura",
                "Observación de reacción - Registrar todos los cambios observados",
                "Registro de resultados - Documentar las observaciones y mediciones"
            ]
            
            for i, (phase, description) in enumerate(zip(self.experiment_phases, phase_descriptions)):
                self.speak_with_animation(f"Fase {{i+1}}: {{phase}}")
                self.show_experiment_phase(phase, description)
                time.sleep(2)
            
            # Demostración paso a paso
            self.speak_with_animation("Ahora veremos una demostración paso a paso del experimento.")
            self.show_pdf_slides(self.pdf_demo)
            
            # Análisis de resultados
            self.speak_with_animation("Finalmente, analicemos los resultados esperados del experimento.")
            self.show_results_analysis()
            
            # Mensaje final
            self.speak_with_animation("Excelente trabajo. Han completado la clase de neutralización con bicarbonato.")
            self.speak_with_animation("Recuerden siempre seguir las guías de seguridad en el laboratorio.")
            self.speak_with_animation("¡Gracias por participar en esta clase de química con ADAI!")
            
            print("\\n" + "="*60)
            print("🧪 CLASE DE QUÍMICA COMPLETADA")
            print("="*60)
            
        except Exception as e:
            print(f"ERROR durante la ejecución: {{e}}")
            import traceback
            traceback.print_exc()
        finally:
            # Limpiar recursos
            cv2.destroyAllWindows()
            print("Recursos liberados")

def main():
    """Función principal"""
    print("🧪 Iniciando clase de química...")
    
    try:
        # Crear y ejecutar la clase
        clase = ClaseQuimicaNeutralizacion()
        clase.run()
        
    except KeyboardInterrupt:
        print("\\nClase interrumpida por el usuario")
    except Exception as e:
        print(f"ERROR fatal: {{e}}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()
        print("Fin de la clase de química")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
'''

def crear_metadata_quimica(class_name, config):
    """Crear metadata específica para la clase de química"""
    
    metadata = {
        "name": class_name,
        "title": config["title"],
        "subject": config["subject"],
        "description": config["description"],
        "duration": config["duration"],
        "type": "experimental",
        "difficulty": "intermedio",
        "safety_level": "bajo",
        "materials": [
            "Bicarbonato de sodio",
            "Ácido cítrico",
            "Agua destilada",
            "Vasos de precipitado",
            "Probetas",
            "Termómetro",
            "Papel indicador de pH"
        ],
        "learning_objectives": [
            "Comprender el concepto de neutralización",
            "Identificar reactivos ácidos y básicos",
            "Observar reacciones químicas",
            "Registrar observaciones científicas",
            "Aplicar medidas de seguridad"
        ],
        "created_at": datetime.datetime.now().isoformat(),
        "version": "1.0",
        "author": "ADAI Class Builder"
    }
    
    # Guardar metadata
    script_dir = os.path.dirname(os.path.abspath(__file__))
    metadata_file = os.path.join(script_dir, "clases", f"{class_name}_metadata.json")
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Metadata guardada: {metadata_file}")

if __name__ == "__main__":
    configurar_clase_quimica()
