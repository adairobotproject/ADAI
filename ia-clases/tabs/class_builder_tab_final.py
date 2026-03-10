# -*- coding: utf-8 -*-
"""
Class Builder Tab for RobotGUI - Final Version
Versión final que genera clases funcionales sin errores
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .base_tab import BaseTab
import os
import datetime
import time

class ClassBuilderTabFinal(BaseTab):
    """Final class builder tab that creates functional classes"""
    
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
        
        # Question bank variables
        self.selected_question_bank = tk.StringVar(value="Preguntas Generales de Química")
        self.available_question_banks = {}
        
        self.generated_class_code = ""
        
        # Cargar bancos de preguntas disponibles
        self.load_question_banks()
        
    def load_question_banks(self):
        """Cargar bancos de preguntas desde demo_sequence_manager.py"""
        try:
            # Importar el extractor de preguntas
            import sys
            import os
            current_dir = os.path.dirname(os.path.dirname(__file__))
            extractor_path = os.path.join(current_dir, "question_bank_extractor.py")
            
            if os.path.exists(extractor_path):
                sys.path.insert(0, current_dir)
                from question_bank_extractor import get_available_question_banks
                self.available_question_banks = get_available_question_banks()
                print(f"✅ Cargados {len(self.available_question_banks)} bancos de preguntas")
            else:
                print("⚠️ No se encontró question_bank_extractor.py")
                self.available_question_banks = {}
        except Exception as e:
            print(f"❌ Error cargando bancos de preguntas: {e}")
            self.available_question_banks = {}
        
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
        self.setup_step_4_question_bank(workflow_frame)
        self.setup_step_5_final_exam(workflow_frame)
        self.setup_step_6_class_generation(workflow_frame)
        
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
        
    def setup_step_4_question_bank(self, parent):
        """Step 4: Question bank selection"""
        step4_frame = tk.LabelFrame(parent, text="❓ Paso 4: Banco de Preguntas", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step4_frame.pack(fill="x", pady=(0, 15))
        
        content_frame = tk.Frame(step4_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Question bank selection
        selection_frame = tk.Frame(content_frame, bg='#2d2d2d')
        selection_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(selection_frame, text="Seleccionar Banco de Preguntas:", 
                bg='#2d2d2d', fg='#ffffff', font=('Arial', 10, 'bold')).pack(anchor="w")
        
        # Dropdown for question bank selection
        bank_options = list(self.available_question_banks.keys()) if self.available_question_banks else ["Sin bancos disponibles"]
        if not self.available_question_banks:
            bank_options = ["Preguntas Generales de Química", "Preguntas Específicas de Química"]
        
        bank_dropdown = ttk.Combobox(selection_frame, textvariable=self.selected_question_bank,
                                   values=bank_options, state="readonly", width=40)
        bank_dropdown.pack(fill="x", pady=(5, 0))
        
        # Question preview
        preview_frame = tk.Frame(content_frame, bg='#2d2d2d')
        preview_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        tk.Label(preview_frame, text="Vista Previa de Preguntas:", 
                bg='#2d2d2d', fg='#ffffff', font=('Arial', 10, 'bold')).pack(anchor="w")
        
        # Listbox for question preview
        listbox_frame = tk.Frame(preview_frame, bg='#2d2d2d')
        listbox_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        self.questions_preview = tk.Listbox(listbox_frame, bg='#3d3d3d', fg='#ffffff',
                                          font=('Arial', 9), height=4)
        self.questions_preview.pack(side="left", fill="both", expand=True)
        
        # Scrollbar for listbox
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.questions_preview.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.questions_preview.yview)
        
        # Update preview when selection changes
        bank_dropdown.bind('<<ComboboxSelected>>', self.update_questions_preview)
        
        # Load initial preview
        self.update_questions_preview()
        
    def update_questions_preview(self, event=None):
        """Update the questions preview listbox"""
        try:
            # Clear current preview
            self.questions_preview.delete(0, tk.END)
            
            # Get selected bank
            selected_bank = self.selected_question_bank.get()
            
            if selected_bank in self.available_question_banks:
                questions = self.available_question_banks[selected_bank]
                
                # Add questions to preview (limit to first 10)
                for i, question in enumerate(questions[:10]):
                    self.questions_preview.insert(tk.END, f"{i+1}. {question}")
                
                if len(questions) > 10:
                    self.questions_preview.insert(tk.END, f"... y {len(questions) - 10} preguntas más")
            else:
                self.questions_preview.insert(tk.END, "No hay preguntas disponibles")
                
        except Exception as e:
            print(f"❌ Error actualizando vista previa: {e}")
            self.questions_preview.insert(tk.END, "Error cargando preguntas")
        
    def setup_step_5_final_exam(self, parent):
        """Step 5: Final exam configuration"""
        step5_frame = tk.LabelFrame(parent, text="🎓 Paso 5: Examen Final", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step5_frame.pack(fill="x", pady=(0, 15))
        
        content_frame = tk.Frame(step5_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Final exam QR selection
        qr_frame = tk.Frame(content_frame, bg='#2d2d2d')
        qr_frame.pack(fill="x")
        
        tk.Label(qr_frame, text="QR Examen Final:", 
                bg='#2d2d2d', fg='#ffffff', font=('Arial', 10, 'bold')).pack(anchor="w")
        
        path_frame = tk.Frame(qr_frame, bg='#2d2d2d')
        path_frame.pack(fill="x", pady=(5, 0))
        
        tk.Entry(path_frame, textvariable=self.final_exam_qr_path, 
                bg='#3d3d3d', fg='#ffffff', font=('Arial', 9), width=50).pack(side="left", fill="x", expand=True)
        
        tk.Button(path_frame, text="📁 Seleccionar", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'),
                 command=lambda: self.select_qr_file(self.final_exam_qr_path)).pack(side="right", padx=(10, 0))
        
    def setup_step_6_class_generation(self, parent):
        """Step 6: Class generation and execution"""
        step6_frame = tk.LabelFrame(parent, text="🚀 Paso 6: Generación y Ejecución", 
                                   font=('Arial', 14, 'bold'),
                                   bg='#2d2d2d', fg='#ffffff')
        step6_frame.pack(fill="both", expand=True)
        
        content_frame = tk.Frame(step6_frame, bg='#2d2d2d')
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
                
            # Generate clean class code
            class_code = self._generate_final_class_code()
            
            self.class_code_preview.delete("1.0", tk.END)
            self.class_code_preview.insert("1.0", class_code)
            
            self.generated_class_code = class_code
            self.update_class_status("✅ Clase generada exitosamente")
            
            messagebox.showinfo("Éxito", "¡Clase generada exitosamente!")
            
        except Exception as e:
            self.update_class_status(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error generando clase: {e}")

    def _generate_final_class_code(self):
        """Generate final class code with correct imports and structure"""
        class_title = self.class_title_var.get().strip()
        class_subject = self.class_subject_var.get()
        
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
        
        # Asegurar que las rutas estén correctamente formateadas
        diagnostic_qr = diagnostic_qr.replace("\\", "/") if diagnostic_qr else ""
        class_pdf = class_pdf.replace("\\", "/") if class_pdf else ""
        final_exam_qr = final_exam_qr.replace("\\", "/") if final_exam_qr else ""
        
        # Obtener banco de preguntas seleccionado
        selected_bank_name = self.selected_question_bank.get()
        selected_questions = self.available_question_banks.get(selected_bank_name, [])
        
        # Generar código Python completamente funcional
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
# Buscar demo_sequence_manager en la carpeta main del directorio clases
classes_dir = os.path.dirname(current_dir)
main_dir = os.path.join(classes_dir, "main")

# Verificar que existe el archivo demo_sequence_manager.py
demo_manager_path = os.path.join(main_dir, "demo_sequence_manager.py")
if not os.path.exists(demo_manager_path):
    print(f"❌ No se encontró demo_sequence_manager.py en: {{demo_manager_path}}")
    print("⚠️ Asegúrate de que el archivo existe en la carpeta main/")
    sys.exit(1)

# Agregar al path
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
        execute_esp32_sequence, summarize_text, ask_openai, QUESTION_BANK
    )
    print("✅ Funciones importadas desde demo_sequence_manager")
except ImportError as e:
    print(f"❌ Error importando funciones: {{e}}")
    print("⚠️ Asegúrate de que demo_sequence_manager.py esté en la carpeta main/")
    print(f"🔍 Buscando en: {{main_dir}}")
    sys.exit(1)

# ======================
#  BANCO DE PREGUNTAS PERSONALIZADAS
# ======================
CUSTOM_QUESTION_BANK = {selected_questions}

def main():
    """Función principal que ejecuta la clase completa"""
    try:
        print("🚀 Iniciando clase: {class_title}")
        print("📚 Materia: {class_subject}")
        
        # Definir rutas de archivos
        diagnostic_qr = "{diagnostic_qr}"
        class_pdf = "{class_pdf}"
        final_exam_qr = "{final_exam_qr}"
        
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
            print(f"⚠️ No se encontró QR diagnóstico: {diagnostic_qr}")
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
                # Usar preguntas personalizadas si están disponibles
                if CUSTOM_QUESTION_BANK:
                    print("🎯 Usando preguntas personalizadas")
                    # Temporalmente reemplazar QUESTION_BANK con preguntas personalizadas
                    original_question_bank = QUESTION_BANK.copy()
                    QUESTION_BANK.clear()
                    QUESTION_BANK.extend(CUSTOM_QUESTION_BANK)
                    
                    # Explicar diapositivas con preguntas personalizadas
                    explain_slides_with_random_questions(
                        engine, class_pdf, pdf_text, current_users,
                        hand_raised_counter, current_slide_num, exit_flag, 
                        known_faces, current_hand_raiser
                    )
                    
                    # Restaurar QUESTION_BANK original
                    QUESTION_BANK.clear()
                    QUESTION_BANK.extend(original_question_bank)
                else:
                    print("🎯 Usando preguntas por defecto")
                    # Explicar diapositivas con preguntas aleatorias por defecto
                    explain_slides_with_random_questions(
                        engine, class_pdf, pdf_text, current_users,
                        hand_raised_counter, current_slide_num, exit_flag, 
                        known_faces, current_hand_raiser
                    )
            else:
                print("❌ No se pudo leer el PDF")
        else:
            print(f"⚠️ No se encontró PDF: {class_pdf}")
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
            print(f"⚠️ No se encontró QR examen: {final_exam_qr}")
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
        """Save the generated class with complete folder structure and resources"""
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
            
            # Crear directorio principal para la clase
            classes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "clases")
            class_folder = os.path.join(classes_dir, f"{clean_name}_clase")
            
            # Crear estructura de carpetas completa
            self._create_complete_class_structure(class_folder, clean_name)
            
            # Guardar archivo principal de la clase
            class_file_path = os.path.join(class_folder, suggested_name)
            with open(class_file_path, 'w', encoding='utf-8') as f:
                f.write(self.generated_class_code)
            
            # Copiar recursos seleccionados
            self._copy_class_resources(class_folder)
            
            # Crear archivos de configuración
            self._create_class_config_files(class_folder, clean_name, title, subject, description, duration)
            
            # Crear archivo README para la clase
            self._create_class_readme(class_folder, clean_name, title, subject, description)
            
            # Actualizar metadata de clases
            self._update_classes_metadata(class_folder, clean_name, title, subject, description, duration)
            
            self.update_class_status(f"✅ Clase completa guardada en: {class_folder}")
            messagebox.showinfo("Éxito", f"Clase completa guardada exitosamente en:\n{class_folder}\n\nIncluye:\n- Código principal\n- Recursos (PDFs, QRs)\n- Configuración\n- README")
                
        except Exception as e:
            self.update_class_status(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Error guardando: {e}")
    
    def _create_complete_class_structure(self, class_folder, clean_name):
        """Create complete folder structure for the class"""
        try:
            # Crear directorio principal
            if not os.path.exists(class_folder):
                os.makedirs(class_folder)
            
            # Crear subdirectorios
            subdirs = [
                "qrs",           # QR codes
                "pdfs",          # PDF files
                "images",        # Images
                "faces",         # Face recognition data
                "resources",     # Other resources
                "sequences",     # Robot sequences
                "exams"          # Exam files
            ]
            
            for subdir in subdirs:
                subdir_path = os.path.join(class_folder, subdir)
                if not os.path.exists(subdir_path):
                    os.makedirs(subdir_path)
                    print(f"✅ Creado directorio: {subdir}")
            
        except Exception as e:
            print(f"⚠️ Error creando estructura: {e}")
    
    def _copy_class_resources(self, class_folder):
        """Copy selected resources to class folder"""
        try:
            import shutil
            
            # Copiar QR diagnóstico
            if self.diagnostic_qr_path.get() and os.path.exists(self.diagnostic_qr_path.get()):
                src = self.diagnostic_qr_path.get()
                dst = os.path.join(class_folder, "qrs", "diagnostic_qr" + os.path.splitext(src)[1])
                shutil.copy2(src, dst)
                print(f"✅ QR diagnóstico copiado: {dst}")
            
            # Copiar PDF de clase
            if self.class_pdf_path.get() and os.path.exists(self.class_pdf_path.get()):
                src = self.class_pdf_path.get()
                dst = os.path.join(class_folder, "pdfs", "class_content" + os.path.splitext(src)[1])
                shutil.copy2(src, dst)
                print(f"✅ PDF de clase copiado: {dst}")
            
            # Copiar QR examen final
            if self.final_exam_qr_path.get() and os.path.exists(self.final_exam_qr_path.get()):
                src = self.final_exam_qr_path.get()
                dst = os.path.join(class_folder, "qrs", "final_exam_qr" + os.path.splitext(src)[1])
                shutil.copy2(src, dst)
                print(f"✅ QR examen final copiado: {dst}")
            
            # Copiar recursos por defecto según la materia
            self._copy_default_resources(class_folder)
                
        except Exception as e:
            print(f"⚠️ Error copiando recursos: {e}")
    
    def _copy_default_resources(self, class_folder):
        """Copy default resources based on subject"""
        try:
            import shutil
            
            subject = self.class_subject_var.get()
            main_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "clases", "main")
            
            # Mapear recursos por defecto
            default_resources = {
                "Robots Médicos": {
                    "qrs": ["RobotsMedicosExamen/pruebadiagnosticaRobotsMedicos.jpeg", "RobotsMedicosExamen/RobotsMedicosExamenI.jpeg"],
                    "pdfs": ["RobotMedico.pdf"]
                },
                "Exoesqueletos": {
                    "qrs": ["ExoesqueletosExamen/pruebadiagnosticaExoesqueletos.jpeg", "ExoesqueletosExamen/ExoesqueletosExamenI.jpeg"],
                    "pdfs": ["ExoesqueletosDeRehabilitacion.pdf"]
                },
                "IoMT": {
                    "qrs": ["DesafiosIoMTExamen/pruebadiagnosticaDesafiosIoMT.jpeg", "DesafiosIoMTExamen/DesafiosIoMTExamenI.png"],
                    "pdfs": ["DesafiosDeIoMT.pdf"]
                }
            }
            
            resources = default_resources.get(subject, default_resources["Robots Médicos"])
            
            # Copiar QRs
            for qr_file in resources.get("qrs", []):
                src_path = os.path.join(main_dir, "qrs", qr_file)
                if os.path.exists(src_path):
                    dst_path = os.path.join(class_folder, "qrs", os.path.basename(qr_file))
                    shutil.copy2(src_path, dst_path)
                    print(f"✅ QR por defecto copiado: {os.path.basename(qr_file)}")
            
            # Copiar PDFs
            for pdf_file in resources.get("pdfs", []):
                src_path = os.path.join(main_dir, "pdfs", pdf_file)
                if os.path.exists(src_path):
                    dst_path = os.path.join(class_folder, "pdfs", os.path.basename(pdf_file))
                    shutil.copy2(src_path, dst_path)
                    print(f"✅ PDF por defecto copiado: {os.path.basename(pdf_file)}")
                    
        except Exception as e:
            print(f"⚠️ Error copiando recursos por defecto: {e}")
    
    def _create_class_config_files(self, class_folder, clean_name, title, subject, description, duration):
        """Create configuration files for the class"""
        try:
            # Crear class_config.json
            config_data = {
                "title": title,
                "subject": subject,
                "description": description,
                "duration": duration,
                "created_at": datetime.datetime.now().isoformat(),
                "main_file": f"{clean_name}_clase.py",
                "folder_name": f"{clean_name}_clase",
                "resources": {
                    "diagnostic_qr": "qrs/diagnostic_qr.jpeg",
                    "class_pdf": "pdfs/class_content.pdf",
                    "final_exam_qr": "qrs/final_exam_qr.jpeg"
                },
                "phases": {
                    "diagnostic": True,
                    "class_content": True,
                    "final_exam": True
                }
            }
            
            config_file_path = os.path.join(class_folder, "class_config.json")
            with open(config_file_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # Crear requirements.txt
            requirements = [
                "opencv-python>=4.5.0",
                "pyttsx3>=2.90",
                "speech_recognition>=3.8.1",
                "face_recognition>=1.3.0",
                "mediapipe>=0.8.0",
                "PyMuPDF>=1.20.0",
                "openai>=0.27.0",
                "requests>=2.25.0",
                "numpy>=1.21.0",
                "Pillow>=8.3.0"
            ]
            
            requirements_path = os.path.join(class_folder, "requirements.txt")
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(requirements))
            
            print(f"✅ Archivos de configuración creados")
            
        except Exception as e:
            print(f"⚠️ Error creando archivos de configuración: {e}")
    
    def _create_class_readme(self, class_folder, clean_name, title, subject, description):
        """Create README file for the class"""
        try:
            readme_content = f"""# {title}

## Información de la Clase
- **Materia:** {subject}
- **Descripción:** {description}
- **Archivo principal:** `{clean_name}_clase.py`
- **Generado por:** ADAI Class Builder
- **Fecha de creación:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Estructura de la Clase

```
{class_folder}/
├── {clean_name}_clase.py          # Código principal de la clase
├── class_config.json              # Configuración de la clase
├── requirements.txt                # Dependencias Python
├── README.md                       # Este archivo
├── qrs/                           # Códigos QR
│   ├── diagnostic_qr.jpeg         # QR evaluación diagnóstica
│   └── final_exam_qr.jpeg         # QR examen final
├── pdfs/                          # Archivos PDF
│   └── class_content.pdf          # Contenido de la clase
├── images/                        # Imágenes
├── faces/                         # Datos de reconocimiento facial
├── resources/                     # Otros recursos
├── sequences/                     # Secuencias del robot
└── exams/                         # Archivos de examen
```

## Cómo Ejecutar la Clase

### Prerrequisitos
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Asegúrate de que `demo_sequence_manager.py` esté en la carpeta `main/`

### Ejecución
```bash
python {clean_name}_clase.py
```

## Flujo de la Clase

1. **FASE 1: Evaluación Diagnóstica**
   - Muestra QR code para prueba inicial
   - Tiempo configurable de visualización

2. **FASE 2: Inicio de Clase**
   - Saludo de ADAI con texto a voz
   - Introducción al tema seleccionado

3. **FASE 3: Contenido Principal**
   - Presentación de diapositivas del PDF
   - Explicación automática de cada slide
   - Preguntas aleatorias durante la presentación

4. **FASE 4: Examen Final**
   - QR code del examen correspondiente
   - Mensaje de finalización

## Características Técnicas

- **Reconocimiento facial:** Identificación automática de estudiantes
- **Texto a voz:** Saludos y explicaciones automáticas
- **Multiprocessing:** Procesamiento paralelo para cámara
- **Preguntas interactivas:** Sistema de preguntas aleatorias
- **Limpieza automática:** Gestión de recursos al finalizar

## Personalización

Puedes modificar:
- `class_config.json` para cambiar la configuración
- Agregar recursos en las carpetas correspondientes
- Modificar el código principal para funcionalidades específicas

## Soporte

Para problemas o dudas, consulta la documentación de ADAI o contacta al administrador del sistema.
"""
            
            readme_path = os.path.join(class_folder, "README.md")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"✅ README creado: {readme_path}")
            
        except Exception as e:
            print(f"⚠️ Error creando README: {e}")
    
    def _update_classes_metadata(self, class_folder, clean_name, title, subject, description, duration):
        """Update the classes metadata file"""
        try:
            import json
            
            # Ruta al archivo de metadata
            classes_dir = os.path.dirname(class_folder)
            metadata_file = os.path.join(classes_dir, "classes_metadata.json")
            
            # Cargar metadata existente o crear nueva
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                metadata = {"classes": []}
            
            # Crear entrada para la nueva clase
            class_entry = {
                "name": f"{clean_name}_clase.py",
                "folder": f"{clean_name}_clase",
                "file_path": os.path.join(class_folder, f"{clean_name}_clase.py").replace("\\", "/"),
                "folder_path": class_folder.replace("\\", "/"),
                "modified": datetime.datetime.now().isoformat(),
                "size": os.path.getsize(os.path.join(class_folder, f"{clean_name}_clase.py")),
                "title": title,
                "subject": subject,
                "description": description,
                "duration": duration,
                "created_at": datetime.datetime.now().isoformat(),
                "resources": {
                    "files": [{"name": f"{clean_name}_clase.py", "path": os.path.join(class_folder, f"{clean_name}_clase.py").replace("\\", "/"), "size": os.path.getsize(os.path.join(class_folder, f"{clean_name}_clase.py")), "modified": datetime.datetime.now().isoformat()}],
                    "images": [],
                    "pdfs": [],
                    "qrs": [],
                    "demo": [],
                    "other": [{"name": "class_config.json", "path": os.path.join(class_folder, "class_config.json").replace("\\", "/"), "size": 0, "modified": datetime.datetime.now().isoformat()}]
                },
                "config": {
                    "title": title,
                    "subject": subject,
                    "description": description,
                    "duration": duration,
                    "created_at": datetime.datetime.now().isoformat(),
                    "main_file": f"{clean_name}_clase.py",
                    "folder_name": f"{clean_name}_clase"
                }
            }
            
            # Agregar nueva clase
            metadata["classes"].append(class_entry)
            metadata["last_scan"] = datetime.datetime.now().isoformat()
            
            # Guardar metadata actualizada
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Metadata actualizada para: {clean_name}")
            
        except Exception as e:
            print(f"⚠️ Error actualizando metadata: {e}")
    
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
