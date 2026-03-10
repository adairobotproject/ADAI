# -*- coding: utf-8 -*-
"""
Class Builder Tab for RobotGUI - Fixed Version
Versión corregida que genera clases funcionales sin errores de sintaxis
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .base_tab import BaseTab
import os
import datetime
import time

class ClassBuilderTabFixed(BaseTab):
    """Fixed class builder tab that creates functional classes"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "🏗️ Class Builder"
        
        # Initialize class builder variables
        self.class_title_var = tk.StringVar(value="Mi Clase de Robótica")
        self.class_subject_var = tk.StringVar(value="Robots Médicos")
        self.class_description_var = tk.StringVar(value="Una clase sobre robots en medicina")
        self.class_duration_var = tk.StringVar(value="45 minutos")
        
        self.diagnostic_qr_path = tk.StringVar()
        self.class_pdf_path = tk.StringVar()
        self.final_exam_qr_path = tk.StringVar()
        
        self.generated_class_code = ""
        
    def setup_tab_content(self):
        """Setup the class builder tab content"""
        # Create scrollable frame
        main_content, canvas, container = self.create_scrollable_frame(self.tab_frame)
        
        # Title
        builder_title = tk.Label(main_content, text="🎓 Creador de Clases ADAI", 
                                font=('Arial', 18, 'bold'), 
                                bg='#1e1e1e', fg='#ffffff')
        builder_title.pack(pady=(10, 20))
        
        # Subtitle
        subtitle = tk.Label(main_content, text="Crea una clase completa: Prueba Diagnóstica → Clase → Examen Final", 
                           font=('Arial', 11), 
                           bg='#1e1e1e', fg='#888888')
        subtitle.pack(pady=(0, 20))
        
        # Main workflow container
        workflow_frame = tk.Frame(main_content, bg='#1e1e1e')
        workflow_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Setup workflow steps
        self.setup_step_1_basic_info(workflow_frame)
        self.setup_step_2_diagnostic_test(workflow_frame)
        self.setup_step_3_class_content(workflow_frame)
        self.setup_step_4_final_exam(workflow_frame)
        self.setup_step_5_class_generation(workflow_frame)
        
    def setup_step_1_basic_info(self, parent):
        """Step 1: Basic class information"""
        step1_frame = tk.LabelFrame(parent, text="📝 Paso 1: Información Básica", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step1_frame.pack(fill="x", pady=(0, 15))
        
        form_frame = tk.Frame(step1_frame, bg='#2d2d2d')
        form_frame.pack(fill="x", padx=20, pady=15)
        
        # Class title
        tk.Label(form_frame, text="Título:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        tk.Entry(form_frame, textvariable=self.class_title_var, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10), width=50).pack(fill="x", pady=(5, 15))
        
        # Subject selection
        tk.Label(form_frame, text="Materia/Tema:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        subject_combo = ttk.Combobox(form_frame, textvariable=self.class_subject_var, 
                                   values=["Robots Médicos", "Exoesqueletos", "IoMT", "Robótica Industrial"], 
                                   state="readonly")
        subject_combo.pack(fill="x", pady=(5, 15))
        
    def setup_step_2_diagnostic_test(self, parent):
        """Step 2: Diagnostic test configuration"""
        step2_frame = tk.LabelFrame(parent, text="📱 Paso 2: Prueba Diagnóstica", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step2_frame.pack(fill="x", pady=(0, 15))
        
        content_frame = tk.Frame(step2_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # QR selection
        qr_input_frame = tk.Frame(content_frame, bg='#2d2d2d')
        qr_input_frame.pack(fill="x", pady=(5, 15))
        
        tk.Entry(qr_input_frame, textvariable=self.diagnostic_qr_path, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 9), state="readonly").pack(side="left", fill="x", expand=True)
        
        tk.Button(qr_input_frame, text="📁 Seleccionar QR", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=lambda: self.select_qr_file(self.diagnostic_qr_path)).pack(side="right", padx=(10, 0))
        
    def setup_step_3_class_content(self, parent):
        """Step 3: Main class content (PDF)"""
        step3_frame = tk.LabelFrame(parent, text="📚 Paso 3: Contenido Principal", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step3_frame.pack(fill="x", pady=(0, 15))
        
        content_frame = tk.Frame(step3_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # PDF selection
        pdf_input_frame = tk.Frame(content_frame, bg='#2d2d2d')
        pdf_input_frame.pack(fill="x", pady=(5, 15))
        
        tk.Entry(pdf_input_frame, textvariable=self.class_pdf_path, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 9), state="readonly").pack(side="left", fill="x", expand=True)
        
        tk.Button(pdf_input_frame, text="📁 Seleccionar PDF", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=self.select_pdf_file).pack(side="right", padx=(10, 0))
        
    def setup_step_4_final_exam(self, parent):
        """Step 4: Final exam configuration"""
        step4_frame = tk.LabelFrame(parent, text="🎓 Paso 4: Examen Final", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step4_frame.pack(fill="x", pady=(0, 15))
        
        content_frame = tk.Frame(step4_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # QR selection
        qr_input_frame = tk.Frame(content_frame, bg='#2d2d2d')
        qr_input_frame.pack(fill="x", pady=(5, 15))
        
        tk.Entry(qr_input_frame, textvariable=self.final_exam_qr_path, bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 9), state="readonly").pack(side="left", fill="x", expand=True)
        
        tk.Button(qr_input_frame, text="📁 Seleccionar QR", bg='#9C27B0', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=lambda: self.select_qr_file(self.final_exam_qr_path)).pack(side="right", padx=(10, 0))
        
    def setup_step_5_class_generation(self, parent):
        """Step 5: Class generation and execution"""
        step5_frame = tk.LabelFrame(parent, text="🚀 Paso 5: Generación y Ejecución", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step5_frame.pack(fill="both", expand=True)
        
        content_frame = tk.Frame(step5_frame, bg='#2d2d2d')
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Left side - Controls
        left_side = tk.Frame(content_frame, bg='#2d2d2d')
        left_side.pack(side="left", fill="y", padx=(0, 15))
        
        # Generation controls
        tk.Button(left_side, text="🔨 Generar Clase", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.generate_complete_class).pack(fill="x", pady=5)
        
        tk.Button(left_side, text="💾 Guardar Clase", bg='#9C27B0', fg='#ffffff',
                 font=('Arial', 11, 'bold'), command=self.save_generated_class).pack(fill="x", pady=5)
        
        tk.Button(left_side, text="▶️ Ejecutar Clase", bg='#FF5722', fg='#ffffff',
                 font=('Arial', 11, 'bold'), command=self.execute_complete_class).pack(fill="x", pady=5)
        
        # Status
        self.class_status_label = tk.Label(left_side, text="✅ Listo para generar", 
                                         bg='#2d2d2d', fg='#4CAF50', font=('Arial', 10))
        self.class_status_label.pack(pady=10)
        
        # Right side - Preview
        right_side = tk.Frame(content_frame, bg='#2d2d2d')
        right_side.pack(side="right", fill="both", expand=True)
        
        # Code preview
        preview_frame = tk.LabelFrame(right_side, text="Vista Previa del Código", 
                                    font=('Arial', 11, 'bold'),
                                    bg='#3d3d3d', fg='#ffffff')
        preview_frame.pack(fill="both", expand=True)
        
        self.class_code_preview = tk.Text(preview_frame, bg='#1e1e1e', fg='#ffffff',
                                        font=('Consolas', 9), wrap=tk.WORD, height=15)
        self.class_code_preview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize with welcome message
        welcome_msg = """# 🎓 Bienvenido al Creador de Clases ADAI

# Completa los pasos 1-4 y luego genera la clase
# El código seguirá el mismo flujo que demo_sequence_manager.py:

# FASE 1: Evaluación Diagnóstica
#   - Muestra QR code para prueba inicial
#   - Tiempo configurable de visualización

# FASE 2: Inicio de Clase  
#   - Saludo de ADAI con texto a voz
#   - Introducción al tema seleccionado

# FASE 3: Contenido Principal
#   - Presentación de diapositivas del PDF
#   - Explicación automática de cada slide
#   - Soporte para múltiples formatos

# FASE 4: Examen Final
#   - QR code del examen correspondiente
#   - Mensaje de finalización

# ¡La clase será completamente funcional e independiente!"""
        
        self.class_code_preview.insert("1.0", welcome_msg)
    
    def select_qr_file(self, path_var):
        """Select QR code image file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar QR Code",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
            )
            if file_path:
                path_var.set(file_path)
                self.update_class_status(f"✅ QR seleccionado: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error seleccionando QR: {e}")

    def select_pdf_file(self):
        """Select PDF file for class content"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar PDF de la Clase",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if file_path:
                self.class_pdf_path.set(file_path)
                self.update_class_status(f"✅ PDF seleccionado: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error seleccionando PDF: {e}")
    
    def generate_complete_class(self):
        """Generate complete class code"""
        try:
            self.update_class_status("🔨 Generando clase...")
            
            if not self.class_title_var.get().strip():
                messagebox.showwarning("Información faltante", "Por favor ingresa el título")
                return
                
            # Generate simplified class code
            class_code = self._generate_simple_class_code()
            
            self.class_code_preview.delete("1.0", tk.END)
            self.class_code_preview.insert("1.0", class_code)
            
            self.generated_class_code = class_code
            self.update_class_status("✅ Clase generada exitosamente")
            
            messagebox.showinfo("Éxito", "¡Clase generada exitosamente!")
            
        except Exception as e:
            self.update_class_status(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error generando clase: {e}")

    def _generate_simple_class_code(self):
        """Generate simple class code that works with demo_sequence_manager"""
        class_title = self.class_title_var.get().strip()
        class_subject = self.class_subject_var.get()
        
        clean_name = "".join(c for c in class_title if c.isalnum() or c in " _-").replace(" ", "_")
        
        # Mapear las materias a los QR codes correspondientes
        subject_qr_mapping = {
            "Robots Médicos": {
                "diagnostic": "RobotsMedicosExamen/pruebadiagnosticaRobotsMedicos.jpeg",
                "pdf": "RobotMedico.pdf",
                "final_exam": "RobotsMedicosExamen/RobotsMedicosExamenI.jpeg"
            },
            "Exoesqueletos": {
                "diagnostic": "ExoesqueletosExamen/pruebadiagnosticaExoesqueletos.jpeg", 
                "pdf": "ExoesqueletosDeRehabilitacion.pdf",
                "final_exam": "ExoesqueletosExamen/ExoesqueletosExamenI.jpeg"
            },
            "IoMT": {
                "diagnostic": "DesafiosIoMTExamen/pruebadiagnosticaDesafiosIoMT.jpeg",
                "pdf": "DesafiosDeIoMT.pdf", 
                "final_exam": "DesafiosIoMTExamen/DesafiosIoMTExamenI.png"
            },
            "Robótica Industrial": {
                "diagnostic": "RobotsMedicosExamen/pruebadiagnosticaRobotsMedicos.jpeg",
                "pdf": "RobotMedico.pdf",
                "final_exam": "RobotsMedicosExamen/RobotsMedicosExamenI.jpeg"
            }
        }
        
        # Obtener rutas según la materia seleccionada
        selected_subject = subject_qr_mapping.get(class_subject, subject_qr_mapping["Robots Médicos"])
        
        diagnostic_qr = self.diagnostic_qr_path.get() or selected_subject["diagnostic"]
        class_pdf = self.class_pdf_path.get() or selected_subject["pdf"] 
        final_exam_qr = self.final_exam_qr_path.get() or selected_subject["final_exam"]
        
        # Generar código Python válido sin errores de sintaxis
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{class_title}
Materia: {class_subject}
Generado por ADAI Class Builder el {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Clase automática usando demo_sequence_manager
"""

import cv2
import os
import time
import multiprocessing
from multiprocessing import Process, Value
import sys

# Configurar path para importar desde demo_sequence_manager
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.join(current_dir, "main")
if main_dir not in sys.path:
    sys.path.insert(0, main_dir)

# Importar funciones directamente desde demo_sequence_manager
try:
    from demo_sequence_manager import (
        initialize_tts, speak_with_animation, listen,
        verify_camera_for_iriun, camera_process, identify_users, load_known_faces,
        show_diagnostic_qr, show_final_exam_qr,
        show_pdf_page_in_opencv, extract_text_from_pdf, 
        explain_slides_with_random_questions, explain_slides_with_sequences,
        RandomQuestionManager, evaluate_student_answer, process_question,
        execute_esp32_sequence, summarize_text, ask_openai
    )
    print("✅ Funciones importadas desde demo_sequence_manager")
except ImportError as e:
    print(f"❌ Error importando funciones: {{e}}")
    print("⚠️ Asegúrate de que demo_sequence_manager.py esté en la carpeta main/")
    raise

def main():
    """Función principal que ejecuta la clase completa"""
    try:
        print("🚀 Iniciando clase: {class_title}")
        print("📚 Materia: {class_subject}")
        
        # Inicializar TTS
        engine = initialize_tts()
        if not engine:
            print("❌ No se pudo inicializar el motor TTS")
            return
        
        # Crear ventana para la cara animada
        cv2.namedWindow("ADAI Robot Face", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("ADAI Robot Face", 600, 400)
        
        # Verificar cámara
        if not verify_camera_for_iriun():
            print("⚠️ Problemas detectados con la cámara.")
            return
        
        # Variables compartidas para multiprocessing
        hand_raised_counter = multiprocessing.Value('i', 0)
        current_slide_num = multiprocessing.Value('i', 1)
        exit_flag = multiprocessing.Value('i', 0)
        current_hand_raiser = multiprocessing.Value('i', -1)
        
        # Identificar usuarios
        print("🔍 Identificando usuarios de izquierda a derecha...")
        current_users, _ = identify_users(engine, current_slide_num, exit_flag)
        
        # Cargar caras conocidas
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
        
        # FASE 1: Evaluación Diagnóstica
        print("\\n" + "="*50)
        print("📱 FASE 1: EVALUACIÓN DIAGNÓSTICA")
        print("="*50)
        
        if diagnostic_qr and os.path.exists(diagnostic_qr):
            speak_with_animation(engine, "Vamos a comenzar con una evaluación diagnóstica.")
            show_diagnostic_qr(diagnostic_qr, display_time=40)
        else:
            print(f"⚠️ No se encontró QR diagnóstico: {{diagnostic_qr}}")
            speak_with_animation(engine, "Continuaremos sin evaluación diagnóstica.")
        
        # FASE 2: Inicio de Clase
        print("\\n" + "="*50)
        print("🤖 FASE 2: INICIO DE CLASE")
        print("="*50)
        
        speak_with_animation(engine, f"Hola, soy ADAI. Bienvenidos a la clase: {class_title}")
        speak_with_animation(engine, f"Vamos a aprender sobre {class_subject}")
        
        # FASE 3: Contenido Principal
        print("\\n" + "="*50)
        print("📚 FASE 3: PRESENTACIÓN DE CONTENIDO")
        print("="*50)
        
        if class_pdf and os.path.exists(class_pdf):
            speak_with_animation(engine, f"Ahora comenzaremos con la presentación sobre {class_subject}.")
            
            # Extraer texto del PDF
            pdf_text = extract_text_from_pdf(class_pdf)
            if pdf_text:
                # Explicar diapositivas con preguntas aleatorias
                explain_slides_with_random_questions(
                    engine, class_pdf, pdf_text, current_users,
                    hand_raised_counter, current_slide_num, exit_flag, 
                    known_faces, current_hand_raiser
                )
            else:
                print("❌ No se pudo leer el PDF")
        else:
            print(f"⚠️ No se encontró PDF: {{class_pdf}}")
            speak_with_animation(engine, "Continuaremos sin presentación de PDF.")
        
        # FASE 4: Examen Final
        print("\\n" + "="*60)
        print("🎓 FASE FINAL: EXAMEN")
        print("="*60)
        
        if final_exam_qr and os.path.exists(final_exam_qr):
            speak_with_animation(engine, "Excelente trabajo. Ahora es momento del examen final.")
            speak_with_animation(engine, "Por favor, escanea el código QR que aparecerá en pantalla.")
            
            show_final_exam_qr(final_exam_qr, display_time=40)
            
            speak_with_animation(engine, "Perfecto. ¡Mucha suerte en el examen!")
        else:
            print(f"⚠️ No se encontró QR examen: {{final_exam_qr}}")
            speak_with_animation(engine, "La clase ha terminado.")
        
        # Finalización
        speak_with_animation(engine, f"Gracias por participar en la clase: {class_title}. ¡Hasta la próxima!")
        
        # Limpiar recursos
        print("🛑 Finalizando clase")
        exit_flag.value = 1
        
        if camera_proc.is_alive():
            print("⏳ Esperando proceso de cámara...")
            camera_proc.join(timeout=3)
            
            if camera_proc.is_alive():
                camera_proc.terminate()
                camera_proc.join(timeout=1)
        
        cv2.destroyAllWindows()
        print("✅ Clase finalizada")
        
    except Exception as e:
        print(f"❌ Error ejecutando clase: {{e}}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
'''

    def save_generated_class(self):
        """Save the generated class to its own folder"""
        try:
            if not self.generated_class_code:
                messagebox.showwarning("Sin código", "Primero genera la clase")
                return
            
            # Generar nombre del archivo
            clean_name = "".join(c for c in self.class_title_var.get() if c.isalnum() or c in " _-").replace(" ", "_")
            suggested_name = f"{clean_name}_clase.py"
            
            # Obtener información de la clase
            title = self.class_title_var.get()
            subject = self.class_subject_var.get()
            description = self.class_description_var.get()
            duration = self.class_duration_var.get()
            
            # Crear directorio para la clase
            classes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "clases")
            class_folder = os.path.join(classes_dir, f"{clean_name}_clase")
            
            if not os.path.exists(class_folder):
                os.makedirs(class_folder)
            
            # Guardar archivo de la clase
            class_file_path = os.path.join(class_folder, suggested_name)
            with open(class_file_path, 'w', encoding='utf-8') as f:
                f.write(self.generated_class_code)
            
            # Crear class_config.json
            config_data = {
                "title": title,
                "subject": subject,
                "description": description,
                "duration": duration,
                "created_at": datetime.datetime.now().isoformat(),
                "main_file": suggested_name,
                "folder_name": f"{clean_name}_clase"
            }
            
            config_file_path = os.path.join(class_folder, "class_config.json")
            with open(config_file_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.update_class_status(f"✅ Clase guardada en: {class_folder}")
            messagebox.showinfo("Éxito", f"Clase guardada exitosamente en:\n{class_folder}")
                
        except Exception as e:
            self.update_class_status(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error guardando: {e}")
    
    def execute_complete_class(self):
        """Execute the generated class"""
        try:
            if not self.generated_class_code:
                messagebox.showwarning("Sin código", "Primero genera la clase")
                return
                
            if not messagebox.askyesno("Confirmar", "¿Ejecutar la clase completa?"):
                return
                
            self.update_class_status("🚀 Ejecutando...")
            
            # Crear archivo temporal en el directorio de clases
            classes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "clases")
            temp_class_name = f"temp_class_{int(time.time())}.py"
            temp_file_path = os.path.join(classes_dir, temp_class_name)
            
            try:
                # Guardar código generado en archivo temporal
                with open(temp_file_path, 'w', encoding='utf-8') as f:
                    f.write(self.generated_class_code)
                
                # Ejecutar en proceso separado
                def execute_process():
                    try:
                        import subprocess
                        import sys
                        
                        # Cambiar al directorio de clases para que los imports funcionen
                        result = subprocess.run([
                            sys.executable, 
                            temp_file_path
                        ], 
                        capture_output=False,  # No capturar output para permitir ventanas OpenCV
                        text=True,
                        cwd=classes_dir)
                        
                        # Actualizar estado después de la ejecución
                        self.parent_gui.root.after(0, lambda: self.update_class_status("✅ Ejecutado exitosamente"))
                        
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        self.parent_gui.root.after(0, lambda: self.update_class_status(error_msg))
                        self.parent_gui.root.after(0, lambda: messagebox.showerror("Error de Ejecución", f"Error ejecutando la clase:\n{str(e)}"))
                    finally:
                        # Limpiar archivo temporal
                        try:
                            if os.path.exists(temp_file_path):
                                os.unlink(temp_file_path)
                        except:
                            pass
                
                # Ejecutar en hilo separado para no bloquear UI
                import threading
                threading.Thread(target=execute_process, daemon=True).start()
                
            except Exception as e:
                # Limpiar archivo temporal en caso de error
                try:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                except:
                    pass
                raise e
            
        except Exception as e:
            self.update_class_status(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Error ejecutando: {e}")

    def update_class_status(self, message):
        """Update the class status label"""
        try:
            if hasattr(self, 'class_status_label'):
                self.class_status_label.config(text=message)
                
                if "✅" in message:
                    self.class_status_label.config(fg='#4CAF50')
                elif "❌" in message:
                    self.class_status_label.config(fg='#f44336')
                elif "🚀" in message or "🔨" in message:
                    self.class_status_label.config(fg='#2196F3')
                else:
                    self.class_status_label.config(fg='#ffffff')
                    
        except Exception as e:
            print(f"Error updating status: {e}")
