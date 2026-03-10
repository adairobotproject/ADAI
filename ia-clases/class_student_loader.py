#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class Student Loader - Cargar estudiantes registrados en las clases
"""

import os
import json
from typing import List, Dict, Optional
from paths import get_data_dir

class ClassStudentLoader:
    """Cargador de estudiantes para uso en clases"""

    def __init__(self, students_file: str = None):
        if students_file is None:
            students_file = os.path.join(get_data_dir(), "students_data.json")
        self.students_file = students_file
    
    def load_active_students_for_class(self) -> List[str]:
        """Cargar lista de nombres de estudiantes activos para usar en clases"""
        try:
            if not os.path.exists(self.students_file):
                print(f"⚠️ Archivo de estudiantes no encontrado: {self.students_file}")
                return []
            
            with open(self.students_file, 'r', encoding='utf-8') as f:
                students_data = json.load(f)
            
            # Filtrar solo estudiantes activos
            active_students = []
            for student in students_data:
                if student.get('estado') == 'Activo':
                    name = student.get('nombre', '')
                    if name:
                        active_students.append(name)
            
            print(f"✅ Cargados {len(active_students)} estudiantes activos para la clase")
            return active_students
            
        except Exception as e:
            print(f"❌ Error cargando estudiantes para clase: {e}")
            return []
    
    def get_student_info(self, student_name: str) -> Optional[Dict]:
        """Obtener información completa de un estudiante por nombre"""
        try:
            if not os.path.exists(self.students_file):
                return None
            
            with open(self.students_file, 'r', encoding='utf-8') as f:
                students_data = json.load(f)
            
            # Buscar estudiante por nombre
            for student in students_data:
                if student.get('nombre', '').lower() == student_name.lower():
                    return student
            
            return None
            
        except Exception as e:
            print(f"❌ Error obteniendo información del estudiante {student_name}: {e}")
            return None
    
    def create_student_list_for_question_manager(self) -> List[str]:
        """Crear lista de estudiantes para RandomQuestionManager"""
        return self.load_active_students_for_class()
    
    def get_students_with_details(self) -> List[Dict]:
        """Obtener lista de estudiantes activos con todos sus detalles"""
        try:
            if not os.path.exists(self.students_file):
                return []
            
            with open(self.students_file, 'r', encoding='utf-8') as f:
                students_data = json.load(f)
            
            # Filtrar solo estudiantes activos
            active_students = [s for s in students_data if s.get('estado') == 'Activo']
            
            return active_students
            
        except Exception as e:
            print(f"❌ Error obteniendo estudiantes con detalles: {e}")
            return []
