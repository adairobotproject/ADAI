#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Class with Students Integration - Ejemplo de clase con integración de estudiantes
"""

import os
import sys

# Agregar path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar funciones de integración
try:
    from integrate_students_with_classes import (
        get_registered_students_for_class,
        create_enhanced_question_manager,
        integrate_with_existing_class,
        get_student_statistics
    )
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    print("⚠️ Sistema de integración de estudiantes no disponible")

def example_class_with_students():
    """Ejemplo de cómo usar la integración de estudiantes en una clase"""
    
    print("🎓 Ejemplo de Clase con Integración de Estudiantes")
    print("=" * 50)
    
    if not INTEGRATION_AVAILABLE:
        print("❌ Sistema de integración no disponible")
        return
    
    # 1. Obtener estudiantes registrados
    print("\n1. 📋 Cargando estudiantes registrados...")
    registered_students = get_registered_students_for_class()
    
    if registered_students:
        print(f"✅ Estudiantes cargados: {registered_students}")
    else:
        print("⚠️ No se encontraron estudiantes registrados")
        return
    
    # 2. Crear question manager mejorado
    print("\n2. 🎯 Creando gestor de preguntas...")
    question_manager = create_enhanced_question_manager(registered_students)
    
    if question_manager:
        print("✅ Gestor de preguntas creado exitosamente")
        
        # Mostrar estadísticas del question manager
        stats = question_manager.get_statistics()
        print(f"📊 Estadísticas del gestor:")
        print(f"   - Total preguntas: {stats.get('total_questions', 0)}")
        print(f"   - Estudiantes: {stats.get('total_students', 0)}")
        print(f"   - Preguntas por estudiante: {stats.get('avg_questions_per_student', 0)}")
    else:
        print("❌ Error creando gestor de preguntas")
        return
    
    # 3. Obtener estadísticas generales
    print("\n3. 📊 Estadísticas del sistema...")
    stats = get_student_statistics()
    print(f"✅ {stats['message']}")
    
    # 4. Simular uso en una clase
    print("\n4. 🎬 Simulando uso en clase...")
    
    # Simular que tenemos una instancia de clase
    class MockClass:
        def __init__(self):
            self.current_users = []
            self.question_manager = None
    
    mock_class = MockClass()
    
    # Integrar estudiantes con la clase
    success = integrate_with_existing_class(mock_class)
    
    if success:
        print("✅ Integración exitosa con la clase")
        print(f"   - Estudiantes en clase: {mock_class.current_users}")
        print(f"   - Question manager: {'✅ Configurado' if mock_class.question_manager else '❌ No configurado'}")
    else:
        print("❌ Error en la integración con la clase")
    
    print("\n🎉 Ejemplo completado!")

def demonstrate_sync_workflow():
    """Demostrar el flujo completo de sincronización"""
    
    print("\n🔄 Flujo de Sincronización de Estudiantes")
    print("=" * 50)
    
    print("1. 📝 Estudiantes se registran en StudentsManager")
    print("2. 🎯 Estudiantes se detectan en clases (reconocimiento facial)")
    print("3. 🔄 Sincronización automática entre sistemas")
    print("4. 📊 Estadísticas y reportes integrados")
    
    print("\n💡 Beneficios:")
    print("• Gestión centralizada de estudiantes")
    print("• Detección automática en clases")
    print("• Sincronización bidireccional")
    print("• Estadísticas unificadas")
    print("• Integración con sistema de preguntas")

if __name__ == "__main__":
    # Ejecutar ejemplo
    example_class_with_students()
    
    # Mostrar flujo de sincronización
    demonstrate_sync_workflow()
