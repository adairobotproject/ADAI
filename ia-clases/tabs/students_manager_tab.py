# -*- coding: utf-8 -*-
"""
Students Manager Tab for RobotGUI - Student Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .base_tab import BaseTab
import json
import os
import datetime

# Import student sync manager
try:
    from student_sync_manager import StudentSyncManager
    SYNC_MANAGER_AVAILABLE = True
except ImportError:
    SYNC_MANAGER_AVAILABLE = False
    print("⚠️ Student Sync Manager no disponible")

class StudentsManagerTab(BaseTab):
    """Students management tab"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "👥 Students Manager"
        
        # Initialize student data
        self.students_data = []
        self.filtered_students = []
        self.current_student = None
        
        # Search and filter variables
        self.search_var = tk.StringVar()
        self.filter_grade_var = tk.StringVar(value="Todos")
        self.filter_status_var = tk.StringVar(value="Todos")
        
        # UI components
        self.students_tree = None
        self.student_detail_frame = None
        self.stats_labels = {}
        
        # Initialize sync manager
        self.sync_manager = None
        if SYNC_MANAGER_AVAILABLE:
            self.sync_manager = StudentSyncManager()
        
    def setup_tab_content(self):
        """Setup the students manager tab content"""
        # Title
        title = tk.Label(self.tab_frame, text="👥 Gestor de Estudiantes", 
                        font=('Arial', 18, 'bold'), 
                        bg='#1e1e1e', fg='#ffffff')
        title.pack(pady=(10, 20))
        
        # Main content area
        main_content = tk.Frame(self.tab_frame, bg='#1e1e1e')
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Top controls panel
        self.setup_controls_panel(main_content)
        
        # Content area with students list and details
        content_area = tk.Frame(main_content, bg='#1e1e1e')
        content_area.pack(fill="both", expand=True, pady=10)
        
        # Left panel - Students list
        self.setup_students_list(content_area)
        
        # Right panel - Student details and statistics
        self.setup_student_details(content_area)
        
        # Load initial data
        self.load_students_data()
        
    def setup_controls_panel(self, parent):
        """Setup controls panel with search and filters"""
        controls_frame = tk.LabelFrame(parent, text="Controles y Filtros", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        controls_frame.pack(fill="x", pady=(0, 10))
        
        controls_content = tk.Frame(controls_frame, bg='#2d2d2d')
        controls_content.pack(fill="x", padx=10, pady=10)
        
        # Search bar
        search_frame = tk.Frame(controls_content, bg='#2d2d2d')
        search_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_frame, text="Buscar:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(side="left")
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               bg='#3d3d3d', fg='#ffffff', font=('Arial', 10))
        search_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        tk.Button(search_frame, text="🔍", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.apply_filters).pack(side="right")
        
        # Filters
        filters_frame = tk.Frame(controls_content, bg='#2d2d2d')
        filters_frame.pack(fill="x", pady=(0, 10))
        
        # Grade filter
        tk.Label(filters_frame, text="Grado:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(side="left")
        
        grade_combo = ttk.Combobox(filters_frame, textvariable=self.filter_grade_var,
                                  values=["Todos", "1°", "2°", "3°", "4°", "5°", "6°"], 
                                  state="readonly", width=10)
        grade_combo.pack(side="left", padx=(5, 20))
        grade_combo.bind('<<ComboboxSelected>>', self.on_filter_changed)
        
        # Status filter
        tk.Label(filters_frame, text="Estado:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(side="left")
        
        status_combo = ttk.Combobox(filters_frame, textvariable=self.filter_status_var,
                                   values=["Todos", "Activo", "Inactivo", "Graduado"], 
                                   state="readonly", width=12)
        status_combo.pack(side="left", padx=(5, 20))
        status_combo.bind('<<ComboboxSelected>>', self.on_filter_changed)
        
        # Action buttons
        buttons_frame = tk.Frame(controls_content, bg='#2d2d2d')
        buttons_frame.pack(fill="x")
        
        tk.Button(buttons_frame, text="➕ Agregar Estudiante", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.add_student).pack(side="left", padx=(0, 10))
        
        tk.Button(buttons_frame, text="✏️ Editar", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.edit_student).pack(side="left", padx=(0, 10))
        
        tk.Button(buttons_frame, text="🗑️ Eliminar", bg='#f44336', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.delete_student).pack(side="left", padx=(0, 10))
        
        tk.Button(buttons_frame, text="📄 Exportar", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.export_students).pack(side="left", padx=(0, 10))
        
        tk.Button(buttons_frame, text="📁 Importar", bg='#9C27B0', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.import_students).pack(side="left", padx=(0, 10))
        
        # Sync buttons (if sync manager available)
        if SYNC_MANAGER_AVAILABLE:
            tk.Button(buttons_frame, text="🔄 Sincronizar", bg='#607D8B', fg='#ffffff',
                     font=('Arial', 10, 'bold'), command=self.sync_students).pack(side="left", padx=(0, 10))
            
            tk.Button(buttons_frame, text="📊 Estadísticas", bg='#795548', fg='#ffffff',
                     font=('Arial', 10, 'bold'), command=self.show_sync_statistics).pack(side="left")
        
    def setup_students_list(self, parent):
        """Setup students list with treeview"""
        list_frame = tk.LabelFrame(parent, text="Lista de Estudiantes", 
                                 font=('Arial', 12, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Treeview for students
        tree_frame = tk.Frame(list_frame, bg='#2d2d2d')
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Define columns
        columns = ('ID', 'Nombre', 'Apellido', 'Grado', 'Estado')
        self.students_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.students_tree.heading('ID', text='ID')
        self.students_tree.heading('Nombre', text='Nombre')
        self.students_tree.heading('Apellido', text='Apellido')
        self.students_tree.heading('Grado', text='Grado')
        self.students_tree.heading('Estado', text='Estado')
        
        # Configure column widths
        self.students_tree.column('ID', width=50, minwidth=50)
        self.students_tree.column('Nombre', width=120, minwidth=100)
        self.students_tree.column('Apellido', width=120, minwidth=100)
        self.students_tree.column('Grado', width=80, minwidth=60)
        self.students_tree.column('Estado', width=100, minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.students_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.students_tree.xview)
        self.students_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.students_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.students_tree.bind('<<TreeviewSelect>>', self.on_student_selected)
        
    def setup_student_details(self, parent):
        """Setup student details and statistics panel"""
        right_panel = tk.Frame(parent, bg='#1e1e1e')
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Student details
        details_frame = tk.LabelFrame(right_panel, text="Detalles del Estudiante", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#2d2d2d', fg='#ffffff')
        details_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.student_detail_frame = tk.Frame(details_frame, bg='#2d2d2d')
        self.student_detail_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.show_no_student_selected()
        
        # Statistics
        stats_frame = tk.LabelFrame(right_panel, text="Estadísticas", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        stats_frame.pack(fill="x")
        
        stats_content = tk.Frame(stats_frame, bg='#2d2d2d')
        stats_content.pack(fill="x", padx=10, pady=10)
        
        # Statistics data
        stats_data = [
            ('Total Estudiantes', 'total'),
            ('Activos', 'active'),
            ('Inactivos', 'inactive'),
            ('Graduados', 'graduated')
        ]
        
        for i, (label_text, key) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(stats_content, bg='#2d2d2d')
            stat_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=2)
            
            tk.Label(stat_frame, text=f"{label_text}:", bg='#2d2d2d', fg='#ffffff',
                    font=('Arial', 10, 'bold')).pack(side="left")
            
            value_label = tk.Label(stat_frame, text="0", bg='#2d2d2d', fg='#4CAF50',
                                 font=('Arial', 10, 'bold'))
            value_label.pack(side="right")
            
            self.stats_labels[key] = value_label
        
        stats_content.grid_columnconfigure(0, weight=1)
        stats_content.grid_columnconfigure(1, weight=1)
        
    def show_no_student_selected(self):
        """Show message when no student is selected"""
        for widget in self.student_detail_frame.winfo_children():
            widget.destroy()
            
        tk.Label(self.student_detail_frame, text="Selecciona un estudiante\npara ver los detalles", 
                bg='#2d2d2d', fg='#888888', font=('Arial', 12),
                justify="center").pack(expand=True)
        
    def show_student_details(self, student):
        """Show details of selected student"""
        for widget in self.student_detail_frame.winfo_children():
            widget.destroy()
            
        # Student info
        info_frame = tk.Frame(self.student_detail_frame, bg='#2d2d2d')
        info_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(info_frame, text=f"ID: {student.get('id', 'N/A')}", 
                bg='#2d2d2d', fg='#ffffff', font=('Arial', 12, 'bold')).pack(anchor="w")
        
        tk.Label(info_frame, text=f"Nombre: {student.get('nombre', '')} {student.get('apellido', '')}", 
                bg='#2d2d2d', fg='#ffffff', font=('Arial', 11)).pack(anchor="w", pady=2)
        
        tk.Label(info_frame, text=f"Grado: {student.get('grado', 'N/A')}", 
                bg='#2d2d2d', fg='#ffffff', font=('Arial', 11)).pack(anchor="w", pady=2)
        
        tk.Label(info_frame, text=f"Estado: {student.get('estado', 'N/A')}", 
                bg='#2d2d2d', fg='#ffffff', font=('Arial', 11)).pack(anchor="w", pady=2)
        
        tk.Label(info_frame, text=f"Email: {student.get('email', 'N/A')}", 
                bg='#2d2d2d', fg='#ffffff', font=('Arial', 11)).pack(anchor="w", pady=2)
        
        # Actions
        actions_frame = tk.Frame(self.student_detail_frame, bg='#2d2d2d')
        actions_frame.pack(fill="x", pady=10)
        
        tk.Button(actions_frame, text="✏️ Editar", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.edit_student).pack(side="left", padx=(0, 5))
        
        tk.Button(actions_frame, text="📧 Enviar Email", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.send_email).pack(side="left", padx=5)
        
    def load_students_data(self):
        """Load students data from file or create sample data"""
        try:
            # Try to load from file
            students_file = "students_data.json"
            if os.path.exists(students_file):
                with open(students_file, 'r', encoding='utf-8') as f:
                    self.students_data = json.load(f)
            else:
                # Create sample data
                self.students_data = self.create_sample_students()
                
            self.filtered_students = self.students_data.copy()
            self.update_students_display()
            self.update_statistics()
            
        except Exception as e:
            self.log_message(f"Error loading students data: {e}")
            self.students_data = []
            self.filtered_students = []
            
    def create_sample_students(self):
        """Create sample students data"""
        return [
            {"id": 1, "nombre": "Ana", "apellido": "García", "grado": "5°", "estado": "Activo", "email": "ana.garcia@email.com"},
            {"id": 2, "nombre": "Carlos", "apellido": "López", "grado": "4°", "estado": "Activo", "email": "carlos.lopez@email.com"},
            {"id": 3, "nombre": "María", "apellido": "Rodríguez", "grado": "6°", "estado": "Graduado", "email": "maria.rodriguez@email.com"},
            {"id": 4, "nombre": "José", "apellido": "Martínez", "grado": "3°", "estado": "Inactivo", "email": "jose.martinez@email.com"},
            {"id": 5, "nombre": "Laura", "apellido": "Sánchez", "grado": "5°", "estado": "Activo", "email": "laura.sanchez@email.com"}
        ]
        
    def update_students_display(self):
        """Update the students treeview display"""
        # Clear existing items
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
            
        # Add filtered students
        for student in self.filtered_students:
            self.students_tree.insert('', 'end', values=(
                student.get('id', ''),
                student.get('nombre', ''),
                student.get('apellido', ''),
                student.get('grado', ''),
                student.get('estado', '')
            ))
    
    def update_statistics(self):
        """Update statistics display"""
        total = len(self.students_data)
        active = len([s for s in self.students_data if s.get('estado') == 'Activo'])
        inactive = len([s for s in self.students_data if s.get('estado') == 'Inactivo'])
        graduated = len([s for s in self.students_data if s.get('estado') == 'Graduado'])
        
        stats = {
            'total': total,
            'active': active,
            'inactive': inactive,
            'graduated': graduated
        }
        
        for key, value in stats.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=str(value))
    
    def on_search_changed(self, event=None):
        """Handle search text change"""
        self.apply_filters()
    
    def on_filter_changed(self, event=None):
        """Handle filter change"""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply search and filters to students list"""
        search_text = self.search_var.get().lower()
        grade_filter = self.filter_grade_var.get()
        status_filter = self.filter_status_var.get()
        
        self.filtered_students = []
        
        for student in self.students_data:
            # Search filter
            if search_text:
                search_fields = [
                    student.get('nombre', '').lower(),
                    student.get('apellido', '').lower(),
                    student.get('email', '').lower(),
                    str(student.get('id', '')).lower()
                ]
                if not any(search_text in field for field in search_fields):
                    continue
            
            # Grade filter
            if grade_filter != "Todos" and student.get('grado') != grade_filter:
                continue
                
            # Status filter
            if status_filter != "Todos" and student.get('estado') != status_filter:
                continue
                
            self.filtered_students.append(student)
        
        self.update_students_display()
    
    def on_student_selected(self, event):
        """Handle student selection"""
        selection = self.students_tree.selection()
        if selection:
            item = self.students_tree.item(selection[0])
            student_id = item['values'][0]
            
            # Find student by ID
            self.current_student = next((s for s in self.students_data if s.get('id') == student_id), None)
            
            if self.current_student:
                self.show_student_details(self.current_student)
            else:
                self.show_no_student_selected()
        else:
            self.current_student = None
            self.show_no_student_selected()
    
    def add_student(self):
        """Add new student"""
        messagebox.showinfo("Agregar Estudiante", "Funcionalidad de agregar estudiante por implementar")
    
    def edit_student(self):
        """Edit selected student"""
        if self.current_student:
            messagebox.showinfo("Editar Estudiante", f"Editando: {self.current_student.get('nombre', '')} {self.current_student.get('apellido', '')}")
        else:
            messagebox.showwarning("Sin Selección", "Por favor selecciona un estudiante para editar")
    
    def delete_student(self):
        """Delete selected student"""
        if self.current_student:
            if messagebox.askyesno("Confirmar Eliminación", 
                                 f"¿Estás seguro de eliminar a {self.current_student.get('nombre', '')} {self.current_student.get('apellido', '')}?"):
                self.students_data = [s for s in self.students_data if s.get('id') != self.current_student.get('id')]
                self.apply_filters()
                self.update_statistics()
                self.show_no_student_selected()
                self.log_message(f"Estudiante eliminado: {self.current_student.get('nombre', '')}")
        else:
            messagebox.showwarning("Sin Selección", "Por favor selecciona un estudiante para eliminar")
    
    def export_students(self):
        """Export students data to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Exportar Estudiantes",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.students_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Éxito", f"Estudiantes exportados a: {file_path}")
                self.log_message(f"Estudiantes exportados a: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando estudiantes: {e}")
    
    def import_students(self):
        """Import students data from file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Importar Estudiantes",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_data = json.load(f)
                    
                if isinstance(imported_data, list):
                    self.students_data = imported_data
                    self.apply_filters()
                    self.update_statistics()
                    messagebox.showinfo("Éxito", f"Estudiantes importados desde: {file_path}")
                    self.log_message(f"Estudiantes importados desde: {file_path}")
                else:
                    messagebox.showerror("Error", "Formato de archivo inválido")
        except Exception as e:
            messagebox.showerror("Error", f"Error importando estudiantes: {e}")
    
    def send_email(self):
        """Send email to selected student"""
        if self.current_student:
            email = self.current_student.get('email', '')
            if email:
                messagebox.showinfo("Enviar Email", f"Abriendo cliente de email para: {email}")
                # Here you would integrate with email client
            else:
                messagebox.showwarning("Sin Email", "Este estudiante no tiene email registrado")
        else:
            messagebox.showwarning("Sin Selección", "Por favor selecciona un estudiante")
    
    def sync_students(self):
        """Sincronizar estudiantes detectados en clases con el registro administrativo"""
        if not SYNC_MANAGER_AVAILABLE or not self.sync_manager:
            messagebox.showerror("Error", "Sistema de sincronización no disponible")
            return
        
        try:
            # Mostrar diálogo de confirmación
            result = messagebox.askyesno("Sincronizar Estudiantes", 
                "¿Deseas sincronizar los estudiantes detectados en las clases con el registro administrativo?\n\n"
                "Esto agregará automáticamente los nuevos estudiantes detectados.")
            
            if result:
                # Ejecutar sincronización
                sync_result = self.sync_manager.sync_detected_to_registered()
                
                if sync_result['success']:
                    new_students = sync_result['new_students']
                    
                    if new_students:
                        # Recargar datos
                        self.load_students_data()
                        
                        message = f"✅ Sincronización exitosa!\n\n"
                        message += f"📊 Estadísticas:\n"
                        message += f"• Nuevos estudiantes agregados: {len(new_students)}\n"
                        message += f"• Total detectados en clases: {sync_result['total_detected']}\n"
                        message += f"• Total registrados: {sync_result['total_registered']}\n\n"
                        message += f"Estudiantes agregados:\n"
                        for student in new_students:
                            message += f"• {student['nombre']} ({student['email']})\n"
                        
                        messagebox.showinfo("Sincronización Completada", message)
                        self.log_message(f"Sincronización completada: {len(new_students)} nuevos estudiantes")
                    else:
                        messagebox.showinfo("Sincronización", 
                            "No se encontraron nuevos estudiantes para sincronizar.\n"
                            "Todos los estudiantes detectados ya están registrados.")
                else:
                    messagebox.showerror("Error de Sincronización", 
                        f"Error durante la sincronización:\n{sync_result.get('error', 'Error desconocido')}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error ejecutando sincronización: {e}")
            self.log_message(f"Error en sincronización: {e}")
    
    def show_sync_statistics(self):
        """Mostrar estadísticas de sincronización"""
        if not SYNC_MANAGER_AVAILABLE or not self.sync_manager:
            messagebox.showerror("Error", "Sistema de sincronización no disponible")
            return
        
        try:
            stats = self.sync_manager.get_sync_statistics()
            
            message = f"📊 Estadísticas de Sincronización\n\n"
            message += f"👥 Estudiantes Registrados: {stats['registered_total']}\n"
            message += f"✅ Activos: {stats['registered_active']}\n"
            message += f"🎯 Detectados en Clases: {stats['detected_in_classes']}\n"
            message += f"🔄 Estado: {stats['sync_status']}\n\n"
            
            if stats['detected_in_classes'] > stats['registered_active']:
                message += "💡 Recomendación: Ejecuta 'Sincronizar' para agregar los estudiantes detectados."
            elif stats['detected_in_classes'] == stats['registered_active']:
                message += "✅ Sistema sincronizado correctamente."
            else:
                message += "ℹ️ Hay más estudiantes registrados que detectados en clases."
            
            messagebox.showinfo("Estadísticas de Sincronización", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo estadísticas: {e}")
    
    def export_detected_students(self):
        """Exportar estudiantes detectados en clases"""
        if not SYNC_MANAGER_AVAILABLE or not self.sync_manager:
            messagebox.showerror("Error", "Sistema de sincronización no disponible")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                title="Exportar Estudiantes Detectados",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                success = self.sync_manager.export_detected_students(file_path)
                if success:
                    messagebox.showinfo("Éxito", f"Estudiantes detectados exportados a: {file_path}")
                    self.log_message(f"Estudiantes detectados exportados a: {file_path}")
                else:
                    messagebox.showerror("Error", "Error exportando estudiantes detectados")
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando estudiantes detectados: {e}")
