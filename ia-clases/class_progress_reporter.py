#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class Progress Reporter - Sistema para que las clases reporten su progreso
=======================================================================

Este módulo proporciona una interfaz simple para que las clases puedan
reportar su progreso directamente al sistema de progreso.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Agregar el directorio padre al path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from class_progress_manager import get_progress_manager, ClassPhase
    PROGRESS_MANAGER_AVAILABLE = True
except ImportError:
    PROGRESS_MANAGER_AVAILABLE = False
    print("⚠️ Progress Manager no disponible")

class ClassProgressReporter:
    """Clase para reportar progreso desde las clases"""
    
    def __init__(self, class_name: str, class_type: str = "default", duration: int = 60):
        """
        Inicializar el reporter de progreso
        
        Args:
            class_name: Nombre de la clase
            class_type: Tipo de clase (default, experimental, theoretical)
            duration: Duración estimada en minutos
        """
        self.class_name = class_name
        self.class_type = class_type
        self.duration = duration
        self.progress_manager = None
        
        if PROGRESS_MANAGER_AVAILABLE:
            self.progress_manager = get_progress_manager()
            # Iniciar la clase en el progress manager
            self.progress_manager.start_class(class_name, class_type, duration)
            print(f"🎓 Progreso iniciado para: {class_name}")
        else:
            print(f"⚠️ Progress Manager no disponible para: {class_name}")
    
    def start_phase(self, phase: str, sub_phase: str = "", details: str = ""):
        """
        Iniciar una nueva fase de la clase
        
        Args:
            phase: Nombre de la fase (diagnostic_test, class_intro, theory_presentation, etc.)
            sub_phase: Sub-fase específica
            details: Detalles adicionales
        """
        if not self.progress_manager:
            print(f"📚 Fase: {phase} - {sub_phase}")
            return
        
        try:
            # Mapear fases de string a ClassPhase
            phase_mapping = {
                "diagnostic_test": ClassPhase.DIAGNOSTIC_TEST,
                "class_intro": ClassPhase.CLASS_INTRO,
                "theory_presentation": ClassPhase.THEORY_PRESENTATION,
                "practical_demo": ClassPhase.PRACTICAL_DEMO,
                "interactive_session": ClassPhase.INTERACTIVE_SESSION,
                "final_exam": ClassPhase.FINAL_EXAM,
                "completed": ClassPhase.COMPLETED,
                "paused": ClassPhase.PAUSED,
                "error": ClassPhase.ERROR
            }
            
            class_phase = phase_mapping.get(phase, ClassPhase.CLASS_INTRO)
            self.progress_manager.set_phase(class_phase, sub_phase, details)
            
            print(f"📚 Fase iniciada: {phase} - {sub_phase}")
            
        except Exception as e:
            print(f"❌ Error iniciando fase: {e}")
    
    def update_progress(self, sub_phase: str = "", details: str = ""):
        """
        Actualizar el progreso de la fase actual
        
        Args:
            sub_phase: Sub-fase específica
            details: Detalles adicionales
        """
        if not self.progress_manager:
            print(f"📊 Progreso: {sub_phase} - {details}")
            return
        
        try:
            self.progress_manager.update_sub_phase(sub_phase, details)
            print(f"📊 Progreso actualizado: {sub_phase} - {details}")
            
        except Exception as e:
            print(f"❌ Error actualizando progreso: {e}")
    
    def complete_phase(self, next_phase: str = "", sub_phase: str = "", details: str = ""):
        """
        Completar la fase actual y opcionalmente iniciar la siguiente
        
        Args:
            next_phase: Siguiente fase a iniciar (opcional)
            sub_phase: Sub-fase de la siguiente fase
            details: Detalles de la siguiente fase
        """
        if not self.progress_manager:
            print(f"✅ Fase completada. Siguiente: {next_phase}")
            return
        
        try:
            if next_phase:
                self.start_phase(next_phase, sub_phase, details)
            print(f"✅ Fase completada. Siguiente: {next_phase}")
            
        except Exception as e:
            print(f"❌ Error completando fase: {e}")
    
    def complete_class(self, message: str = "Clase completada exitosamente"):
        """
        Completar la clase
        
        Args:
            message: Mensaje de completación
        """
        if not self.progress_manager:
            print(f"🎉 {message}")
            return
        
        try:
            self.progress_manager.complete_class()
            print(f"🎉 {message}")
            
        except Exception as e:
            print(f"❌ Error completando clase: {e}")
    
    def error_in_class(self, error_message: str):
        """
        Reportar error en la clase
        
        Args:
            error_message: Mensaje de error
        """
        if not self.progress_manager:
            print(f"❌ Error: {error_message}")
            return
        
        try:
            self.progress_manager.error_in_class(error_message)
            print(f"❌ Error reportado: {error_message}")
            
        except Exception as e:
            print(f"❌ Error reportando error: {e}")
    
    def pause_class(self):
        """Pausar la clase"""
        if not self.progress_manager:
            print("⏸️ Clase pausada")
            return
        
        try:
            self.progress_manager.pause_class()
            print("⏸️ Clase pausada")
            
        except Exception as e:
            print(f"❌ Error pausando clase: {e}")
    
    def resume_class(self):
        """Reanudar la clase"""
        if not self.progress_manager:
            print("▶️ Clase reanudada")
            return
        
        try:
            self.progress_manager.resume_class()
            print("▶️ Clase reanudada")
            
        except Exception as e:
            print(f"❌ Error reanudando clase: {e}")
    
    def get_progress_info(self) -> Dict[str, Any]:
        """
        Obtener información del progreso actual
        
        Returns:
            Dict con información del progreso
        """
        if not self.progress_manager:
            return {
                "class_name": self.class_name,
                "is_active": False,
                "error": "Progress Manager no disponible"
            }
        
        try:
            return self.progress_manager.get_progress_summary()
        except Exception as e:
            return {
                "class_name": self.class_name,
                "is_active": False,
                "error": str(e)
            }

# Función de conveniencia para crear un reporter
def create_progress_reporter(class_name: str, class_type: str = "default", duration: int = 60) -> ClassProgressReporter:
    """
    Crear un reporter de progreso para una clase
    
    Args:
        class_name: Nombre de la clase
        class_type: Tipo de clase
        duration: Duración estimada en minutos
        
    Returns:
        ClassProgressReporter instance
    """
    return ClassProgressReporter(class_name, class_type, duration)

# Ejemplo de uso para las clases
def example_class_usage():
    """Ejemplo de cómo usar el reporter en una clase"""
    
    # Crear reporter
    reporter = create_progress_reporter("mi_clase", "default", 45)
    
    # Iniciar fase de introducción
    reporter.start_phase("class_intro", "Presentación del tema", "Explicando objetivos de la clase")
    time.sleep(2)
    
    # Actualizar progreso
    reporter.update_progress("Conceptos básicos", "Definiendo términos fundamentales")
    time.sleep(2)
    
    # Completar fase e iniciar siguiente
    reporter.complete_phase("theory_presentation", "Desarrollo teórico", "Explicando conceptos avanzados")
    time.sleep(2)
    
    # Actualizar progreso en nueva fase
    reporter.update_progress("Ejemplos prácticos", "Mostrando aplicaciones reales")
    time.sleep(2)
    
    # Completar clase
    reporter.complete_class("Clase completada exitosamente")
    
    # Mostrar progreso final
    progress_info = reporter.get_progress_info()
    print(f"📊 Progreso final: {progress_info}")

if __name__ == "__main__":
    example_class_usage()
