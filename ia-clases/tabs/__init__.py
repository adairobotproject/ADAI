# -*- coding: utf-8 -*-
"""
Tabs module for RobotGUI
Contains modular tab implementations
"""

from .base_tab import BaseTab
from .main_tab import MainTab
from .esp32_tab import ESP32Tab
from .sequence_builder_tab import SequenceBuilderTab
from .settings_tab import SettingsTab
from .simulator_tab import SimulatorTab
from .class_builder_tab import ClassBuilderTab
from .class_controller_tab import ClassControllerTab
from .mobile_app_tab import MobileAppTab
from .students_manager_tab import StudentsManagerTab
from .demo_sequence_tab import DemoSequenceTab

# Import ClassesManagerTab
from .classes_manager_tab import ClassesManagerTab

__all__ = [
    'BaseTab', 'MainTab', 'ESP32Tab', 'SequenceBuilderTab', 
    'SettingsTab', 'SimulatorTab', 'ClassBuilderTab', 'ClassControllerTab',
    'MobileAppTab', 'StudentsManagerTab', 'ClassesManagerTab'
]
