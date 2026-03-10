#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Student Sync Manager - Sincronización entre StudentsManager y Clases Dinámicas
"""

import os
import json
import datetime
from typing import List, Dict, Optional

class StudentSyncManager:
    """Gestor de sincronización entre sistemas de estudiantes"""
    
    def __init__(self, students_file: str = "students_data.json", classes_dir: str = "clases"):
        self.students_file = students_file
        self.classes_dir = classes_dir
        self.faces_dir = os.path.join(classes_dir, "main", "faces")
        
    def load_registered_students(self) -> List[Dict]:
        """Cargar estudiantes registrados desde students_data.json"""
        try:
            if os.path.exists(self.students_file):
                with open(self.students_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"❌ Error cargando estudiantes registrados: {e}")
            return []
    
    def save_registered_students(self, students: List[Dict]) -> bool:
        """Guardar estudiantes registrados en students_data.json"""
        try:
            with open(self.students_file, 'w', encoding='utf-8') as f:
                json.dump(students, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error guardando estudiantes: {e}")
            return False
    
    def get_detected_students_from_classes(self) -> List[str]:
        """Obtener lista de estudiantes detectados en las clases (desde carpeta faces)"""
        detected_students = []
        
        try:
            if os.path.exists(self.faces_dir):
                for file in os.listdir(self.faces_dir):
                    if file.endswith('.jpg') or file.endswith('.png'):
                        # Extraer nombre del archivo (sin extensión)
                        student_name = os.path.splitext(file)[0]
                        detected_students.append(student_name)
        except Exception as e:
            print(f"❌ Error obteniendo estudiantes detectados: {e}")
        
        return detected_students
    
    def sync_detected_to_registered(self) -> Dict:
        """Sincronizar estudiantes detectados en clases con el registro administrativo"""
        try:
            # Cargar estudiantes registrados
            registered_students = self.load_registered_students()
            registered_names = {s.get('nombre', '').lower() for s in registered_students}
            
            # Obtener estudiantes detectados
            detected_students = self.get_detected_students_from_classes()
            
            # Encontrar nuevos estudiantes
            new_students = []
            for detected_name in detected_students:
                if detected_name.lower() not in registered_names:
                    # Crear nuevo registro de estudiante
                    new_student = {
                        "id": self._generate_new_id(registered_students),
                        "nombre": detected_name.split('_')[0],  # Remover sufijos como _1, _2
                        "apellido": "",
                        "grado": "No especificado",
                        "estado": "Activo",
                        "email": f"{detected_name.lower().replace('_', '.')}@email.com",
                        "detected_in_class": True,
                        "detection_date": datetime.datetime.now().isoformat()
                    }
                    new_students.append(new_student)
                    registered_students.append(new_student)
            
            # Guardar actualización
            if new_students:
                self.save_registered_students(registered_students)
            
            return {
                "success": True,
                "new_students": new_students,
                "total_detected": len(detected_students),
                "total_registered": len(registered_students)
            }
            
        except Exception as e:
            print(f"❌ Error en sincronización: {e}")
            return {
                "success": False,
                "error": str(e),
                "new_students": [],
                "total_detected": 0,
                "total_registered": 0
            }
    
    def sync_registered_to_class(self, class_name: str) -> Dict:
        """Sincronizar estudiantes registrados para usar en una clase específica"""
        try:
            registered_students = self.load_registered_students()
            active_students = [s for s in registered_students if s.get('estado') == 'Activo']
            
            # Crear lista de nombres para la clase
            student_names = []
            for student in active_students:
                name = student.get('nombre', '')
                if name:
                    student_names.append(name)
            
            return {
                "success": True,
                "student_names": student_names,
                "total_students": len(student_names)
            }
            
        except Exception as e:
            print(f"❌ Error sincronizando para clase {class_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "student_names": [],
                "total_students": 0
            }
    
    def get_sync_statistics(self) -> Dict:
        """Obtener estadísticas de sincronización"""
        try:
            registered_students = self.load_registered_students()
            detected_students = self.get_detected_students_from_classes()
            
            active_registered = len([s for s in registered_students if s.get('estado') == 'Activo'])
            detected_in_class = len(detected_students)
            
            return {
                "registered_total": len(registered_students),
                "registered_active": active_registered,
                "detected_in_classes": detected_in_class,
                "sync_status": "✅ Sincronizado" if detected_in_class <= active_registered else "⚠️ Desactualizado"
            }
            
        except Exception as e:
            return {
                "registered_total": 0,
                "registered_active": 0,
                "detected_in_classes": 0,
                "sync_status": f"❌ Error: {e}"
            }
    
    def _generate_new_id(self, students: List[Dict]) -> int:
        """Generar nuevo ID para estudiante"""
        if not students:
            return 1
        
        max_id = max(s.get('id', 0) for s in students)
        return max_id + 1
    
    def export_detected_students(self, export_file: str) -> bool:
        """Exportar estudiantes detectados en clases a archivo JSON"""
        try:
            detected_students = self.get_detected_students_from_classes()
            
            export_data = {
                "export_date": datetime.datetime.now().isoformat(),
                "source": "class_detection",
                "students": [
                    {
                        "name": name,
                        "detected": True,
                        "face_file": f"{name}.jpg"
                    }
                    for name in detected_students
                ]
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Error exportando estudiantes detectados: {e}")
            return False
