# -*- coding: utf-8 -*-
"""
Main Tab for RobotGUI - Robot Control Interface
"""

import tkinter as tk
from .base_tab import BaseTab

class MainTab(BaseTab):
    """Main robot control tab with camera, simulator, and object detection"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "🤖 Robot Control"
        
    def setup_tab_content(self):
        """Setup the main tab content"""
        # Top section (Camera + InMoov Sim + Object List)
        top_frame = tk.Frame(self.tab_frame, bg='#1e1e1e')
        top_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Left side container to host Camera and InMoov side-by-side
        left_split = tk.Frame(top_frame, bg='#1e1e1e')
        left_split.pack(side="left", fill="both", expand=True)

        # Left panel (Camera)
        self.setup_camera_panel(left_split)

        # Middle panel (InMoov Simulator)
        self.setup_inmoov_sim_panel(left_split)

        # Right panel (Object Detection + ESP32 Control)
        self.setup_object_panel(top_frame)
        
        # Bottom section (Statistics + Info)
        bottom_frame = tk.Frame(self.tab_frame, bg='#1e1e1e')
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Statistics panel
        self.setup_statistics_panel(bottom_frame)
        
        # Info panel (Position + Connections)
        self.setup_info_panel(bottom_frame)
        
    def setup_camera_panel(self, parent):
        """Setup responsive camera panel - delegated to parent GUI"""
        if hasattr(self.parent_gui, 'setup_camera_panel'):
            self.parent_gui.setup_camera_panel(parent)
        else:
            # Fallback responsive camera panel
            font_size = self.get_responsive_font_size(12, 10, 14, 100)
            camera_frame = tk.LabelFrame(parent, text="📹 Camera", 
                                       font=('Arial', font_size, 'bold'),
                                       bg='#2d2d2d', fg='#ffffff')
            camera_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
            label_font_size = self.get_responsive_font_size(12, 10, 16, 80)
            tk.Label(camera_frame, text="Camera panel not available", 
                    bg='#2d2d2d', fg='#888888',
                    font=('Arial', label_font_size)).pack(pady=20)
            
    def setup_inmoov_sim_panel(self, parent):
        """Setup responsive InMoov simulator panel - delegated to parent GUI"""
        if hasattr(self.parent_gui, 'setup_inmoov_sim_panel'):
            self.parent_gui.setup_inmoov_sim_panel(parent)
        else:
            # Fallback responsive simulator panel
            font_size = self.get_responsive_font_size(12, 10, 14, 100)
            sim_frame = tk.LabelFrame(parent, text="🤖 InMoov Simulator", 
                                    font=('Arial', font_size, 'bold'),
                                    bg='#2d2d2d', fg='#ffffff')
            sim_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
            
            label_font_size = self.get_responsive_font_size(12, 10, 16, 80)
            tk.Label(sim_frame, text="Simulator panel not available", 
                    bg='#2d2d2d', fg='#888888',
                    font=('Arial', label_font_size)).pack(pady=20)
            
    def setup_object_panel(self, parent):
        """Setup responsive object detection panel - delegated to parent GUI"""
        if hasattr(self.parent_gui, 'setup_object_panel'):
            self.parent_gui.setup_object_panel(parent)
        else:
            # Fallback responsive object panel
            font_size = self.get_responsive_font_size(12, 10, 14, 100)
            object_frame = tk.LabelFrame(parent, text="🎯 Object Detection", 
                                       font=('Arial', font_size, 'bold'),
                                       bg='#2d2d2d', fg='#ffffff')
            object_frame.pack(side="right", fill="y", padx=(5, 0))
            
            label_font_size = self.get_responsive_font_size(12, 10, 16, 80)
            tk.Label(object_frame, text="Object detection panel not available", 
                    bg='#2d2d2d', fg='#888888',
                    font=('Arial', label_font_size)).pack(pady=20)
            
    def setup_statistics_panel(self, parent):
        """Setup responsive statistics panel - delegated to parent GUI"""
        if hasattr(self.parent_gui, 'setup_statistics_panel'):
            self.parent_gui.setup_statistics_panel(parent)
        else:
            # Fallback responsive statistics panel
            font_size = self.get_responsive_font_size(12, 10, 14, 100)
            stats_frame = tk.LabelFrame(parent, text="📊 Statistics", 
                                      font=('Arial', font_size, 'bold'),
                                      bg='#2d2d2d', fg='#ffffff')
            stats_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
            label_font_size = self.get_responsive_font_size(12, 10, 16, 80)
            tk.Label(stats_frame, text="Statistics panel not available", 
                    bg='#2d2d2d', fg='#888888',
                    font=('Arial', label_font_size)).pack(pady=10)
            
    def setup_info_panel(self, parent):
        """Setup responsive info panel - delegated to parent GUI"""
        if hasattr(self.parent_gui, 'setup_info_panel'):
            self.parent_gui.setup_info_panel(parent)
        else:
            # Fallback responsive info panel
            font_size = self.get_responsive_font_size(12, 10, 14, 100)
            info_frame = tk.LabelFrame(parent, text="ℹ️ Information", 
                                     font=('Arial', font_size, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
            info_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
            
            label_font_size = self.get_responsive_font_size(12, 10, 16, 80)
            tk.Label(info_frame, text="Info panel not available", 
                    bg='#2d2d2d', fg='#888888',
                    font=('Arial', label_font_size)).pack(pady=10)
    
    def update_responsive_elements(self):
        """Update responsive elements when window size changes"""
        try:
            # Update all panel fonts and sizes
            self.update_panel_fonts()
        except Exception as e:
            print(f"Error updating responsive elements in MainTab: {e}")
    
    def update_panel_fonts(self):
        """Update font sizes for all panels"""
        try:
            # This would update existing widgets if they were stored as attributes
            # For now, the responsive design is handled in the setup methods
            pass
        except Exception as e:
            print(f"Error updating panel fonts: {e}")
