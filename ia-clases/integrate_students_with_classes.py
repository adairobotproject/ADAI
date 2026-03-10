#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrate Students with Classes - Integración de estudiantes registrados con el sistema de clases
"""

import os
import sys
from typing import List, Dict

# Import student loader
try:
    from class_student_loader import ClassStudentLoader
    STUDENT_LOADER_AVAILABLE = True
except ImportError:
    STUDENT_LOADER_AVAILABLE = False
    print("⚠️ Class Student Loader no disponible")

def get_registered_students_for_class() -> List[str]:
    """
    Función principal para obtener estudiantes registrados para usar en clases
    
    Returns:
        List[str]: Lista de nombres de estudiantes activos
    """
    if not STUDENT_LOADER_AVAILABLE:
        print("⚠️ Sistema de carga de estudiantes no disponible, usando lista vacía")
        return []
    
    try:
        loader = ClassStudentLoader()
        students = loader.load_active_students_for_class()
        
        if students:
            print(f"🎯 Estudiantes registrados cargados para la clase: {students}")
        else:
            print("⚠️ No se encontraron estudiantes registrados activos")
        
        return students
        
    except Exception as e:
        print(f"❌ Error cargando estudiantes registrados: {e}")
        return []

def create_enhanced_question_manager(students: List[str] = None):
    """
    Crear un RandomQuestionManager mejorado con estudiantes registrados
    
    Args:
        students: Lista de estudiantes (opcional, se cargará automáticamente si no se proporciona)
    
    Returns:
        RandomQuestionManager: Instancia configurada con estudiantes registrados
    """
    try:
        # Importar desde demo_sequence_manager
        current_dir = os.path.dirname(os.path.abspath(__file__))
        main_dir = os.path.join(current_dir, "clases", "main")
        
        if main_dir not in sys.path:
            sys.path.insert(0, main_dir)
        
        from demo_sequence_manager import RandomQuestionManager
        
        # Obtener estudiantes si no se proporcionaron
        if students is None:
            students = get_registered_students_for_class()
        
        # Si no hay estudiantes registrados, usar lista vacía
        if not students:
            print("⚠️ No hay estudiantes registrados, usando lista vacía")
            students = []
        
        # Crear RandomQuestionManager con estudiantes registrados
        question_manager = RandomQuestionManager(students)
        
        print(f"✅ RandomQuestionManager creado con {len(students)} estudiantes registrados")
        return question_manager
        
    except ImportError as e:
        print(f"❌ Error importando RandomQuestionManager: {e}")
        return None
    except Exception as e:
        print(f"❌ Error creando RandomQuestionManager: {e}")
        return None

def integrate_with_existing_class(class_instance):
    """
    Integrar estudiantes registrados con una clase existente
    
    Args:
        class_instance: Instancia de la clase a integrar
    """
    try:
        # Obtener estudiantes registrados
        registered_students = get_registered_students_for_class()
        
        if registered_students:
            # Actualizar current_users de la clase
            if hasattr(class_instance, 'current_users'):
                class_instance.current_users = registered_students.copy()
                print(f"✅ Clase actualizada con {len(registered_students)} estudiantes registrados")
            
            # Crear question manager mejorado
            question_manager = create_enhanced_question_manager(registered_students)
            if question_manager:
                # Agregar question manager a la clase si tiene el atributo
                if hasattr(class_instance, 'question_manager'):
                    class_instance.question_manager = question_manager
                    print("✅ Question manager integrado con estudiantes registrados")
            
            return True
        else:
            print("⚠️ No se pudieron cargar estudiantes registrados")
            return False
            
    except Exception as e:
        print(f"❌ Error integrando estudiantes con la clase: {e}")
        return False

def get_student_statistics() -> Dict:
    """
    Obtener estadísticas de estudiantes para mostrar en la interfaz
    
    Returns:
        Dict: Estadísticas de estudiantes
    """
    if not STUDENT_LOADER_AVAILABLE:
        return {
            "total_registered": 0,
            "active_students": 0,
            "students_loaded": False,
            "message": "Sistema de estudiantes no disponible"
        }
    
    try:
        loader = ClassStudentLoader()
        students_with_details = loader.get_students_with_details()
        
        return {
            "total_registered": len(students_with_details),
            "active_students": len(students_with_details),
            "students_loaded": True,
            "message": f"{len(students_with_details)} estudiantes activos cargados"
        }
        
    except Exception as e:
        return {
            "total_registered": 0,
            "active_students": 0,
            "students_loaded": False,
            "message": f"Error: {e}"
        }
