#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Student Sync System - Prueba del sistema de sincronización de estudiantes
"""

import os
import json
import tempfile
import shutil
from datetime import datetime

def create_test_students_file():
    """Crear archivo de prueba con estudiantes"""
    test_students = [
        {
            "id": 1,
            "nombre": "Ana",
            "apellido": "García",
            "grado": "5°",
            "estado": "Activo",
            "email": "ana.garcia@email.com"
        },
        {
            "id": 2,
            "nombre": "Carlos",
            "apellido": "López",
            "grado": "4°",
            "estado": "Activo",
            "email": "carlos.lopez@email.com"
        },
        {
            "id": 3,
            "nombre": "María",
            "apellido": "Rodríguez",
            "grado": "6°",
            "estado": "Graduado",
            "email": "maria.rodriguez@email.com"
        }
    ]
    
    with open("students_data.json", 'w', encoding='utf-8') as f:
        json.dump(test_students, f, indent=2, ensure_ascii=False)
    
    print("✅ Archivo de estudiantes de prueba creado")

def create_test_faces_directory():
    """Crear directorio de prueba con caras detectadas"""
    faces_dir = os.path.join("clases", "main", "faces")
    os.makedirs(faces_dir, exist_ok=True)
    
    # Crear archivos de prueba (simulando caras detectadas)
    test_faces = ["Ana.jpg", "Carlos.jpg", "Pedro.jpg", "Laura.jpg"]
    
    for face_file in test_faces:
        face_path = os.path.join(faces_dir, face_file)
        # Crear archivo vacío para simular imagen
        with open(face_path, 'w') as f:
            f.write("# Simulated face file")
    
    print(f"✅ Directorio de caras de prueba creado: {faces_dir}")
    print(f"   - Caras simuladas: {test_faces}")

def test_sync_manager():
    """Probar StudentSyncManager"""
    print("\n🧪 Probando StudentSyncManager...")
    
    try:
        from student_sync_manager import StudentSyncManager
        
        sync_manager = StudentSyncManager()
        
        # Probar carga de estudiantes registrados
        registered = sync_manager.load_registered_students()
        print(f"✅ Estudiantes registrados cargados: {len(registered)}")
        
        # Probar detección de estudiantes
        detected = sync_manager.get_detected_students_from_classes()
        print(f"✅ Estudiantes detectados: {detected}")
        
        # Probar sincronización
        sync_result = sync_manager.sync_detected_to_registered()
        print(f"✅ Resultado de sincronización: {sync_result['success']}")
        
        if sync_result['success']:
            print(f"   - Nuevos estudiantes: {len(sync_result['new_students'])}")
            print(f"   - Total detectados: {sync_result['total_detected']}")
            print(f"   - Total registrados: {sync_result['total_registered']}")
        
        # Probar estadísticas
        stats = sync_manager.get_sync_statistics()
        print(f"✅ Estadísticas: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando StudentSyncManager: {e}")
        return False

def test_class_student_loader():
    """Probar ClassStudentLoader"""
    print("\n🧪 Probando ClassStudentLoader...")
    
    try:
        from class_student_loader import ClassStudentLoader
        
        loader = ClassStudentLoader()
        
        # Probar carga de estudiantes activos
        active_students = loader.load_active_students_for_class()
        print(f"✅ Estudiantes activos para clase: {active_students}")
        
        # Probar información de estudiante
        if active_students:
            student_info = loader.get_student_info(active_students[0])
            print(f"✅ Información de estudiante: {student_info}")
        
        # Probar estudiantes con detalles
        students_with_details = loader.get_students_with_details()
        print(f"✅ Estudiantes con detalles: {len(students_with_details)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando ClassStudentLoader: {e}")
        return False

def test_integration():
    """Probar sistema de integración"""
    print("\n🧪 Probando sistema de integración...")
    
    try:
        from integrate_students_with_classes import (
            get_registered_students_for_class,
            create_enhanced_question_manager,
            get_student_statistics
        )
        
        # Probar carga de estudiantes
        students = get_registered_students_for_class()
        print(f"✅ Estudiantes cargados para integración: {students}")
        
        # Probar creación de question manager
        question_manager = create_enhanced_question_manager(students)
        if question_manager:
            print("✅ Question manager creado exitosamente")
        else:
            print("⚠️ Question manager no se pudo crear")
        
        # Probar estadísticas
        stats = get_student_statistics()
        print(f"✅ Estadísticas de integración: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando integración: {e}")
        return False

def cleanup_test_files():
    """Limpiar archivos de prueba"""
    try:
        # Limpiar archivo de estudiantes
        if os.path.exists("students_data.json"):
            os.remove("students_data.json")
            print("✅ Archivo students_data.json eliminado")
        
        # Limpiar directorio de caras
        faces_dir = os.path.join("clases", "main", "faces")
        if os.path.exists(faces_dir):
            shutil.rmtree(faces_dir)
            print("✅ Directorio de caras eliminado")
        
        # Limpiar directorio clases si está vacío
        clases_dir = "clases"
        if os.path.exists(clases_dir):
            try:
                os.rmdir(clases_dir)
                print("✅ Directorio clases eliminado")
            except OSError:
                print("ℹ️ Directorio clases no está vacío, se mantiene")
        
    except Exception as e:
        print(f"⚠️ Error limpiando archivos de prueba: {e}")

def main():
    """Función principal de prueba"""
    print("🧪 Sistema de Prueba - Sincronización de Estudiantes")
    print("=" * 60)
    
    # Crear archivos de prueba
    print("\n📁 Creando archivos de prueba...")
    create_test_students_file()
    create_test_faces_directory()
    
    # Ejecutar pruebas
    tests = [
        ("StudentSyncManager", test_sync_manager),
        ("ClassStudentLoader", test_class_student_loader),
        ("Sistema de Integración", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando prueba: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    # Mostrar resumen
    print("\n📊 Resumen de Pruebas")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado Final: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! Sistema funcionando correctamente.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar errores arriba.")
    
    # Limpiar archivos de prueba
    print("\n🧹 Limpiando archivos de prueba...")
    cleanup_test_files()
    
    print("\n✅ Prueba completada!")

if __name__ == "__main__":
    main()
