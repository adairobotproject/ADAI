# -*- coding: utf-8 -*-
"""
Base Tab class for RobotGUI modular tabs
"""

import tkinter as tk
from tkinter import ttk
import os

class BaseTab:
    """Base class for all tabs in RobotGUI"""
    
    def __init__(self, parent_gui, notebook):
        """
        Initialize base tab
        
        Args:
            parent_gui: Reference to main RobotGUI instance
            notebook: The ttk.Notebook where this tab will be added
        """
        self.parent_gui = parent_gui
        self.notebook = notebook
        self.tab_frame = None
        self.tab_name = "Base Tab"
        
        # Access to parent GUI attributes
        self.root = parent_gui.root if hasattr(parent_gui, 'root') else None
        
        # Responsive design attributes
        self.window_width = getattr(parent_gui, 'window_width', 1200)
        self.window_height = getattr(parent_gui, 'window_height', 600)
        
    def create_tab(self):
        """Create and setup the tab. Override in subclasses."""
        self.tab_frame = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(self.tab_frame, text=self.tab_name)
        self.setup_tab_content()
        
    def setup_tab_content(self):
        """Setup the content of the tab. Override in subclasses."""
        pass
        
    def create_scrollable_frame(self, parent):
        """
        Create a scrollable frame - copied from parent GUI
        
        Args:
            parent: Parent widget
            
        Returns:
            tuple: (scrollable_frame, canvas, container)
        """
        # Create main container
        container = tk.Frame(parent, bg='#1e1e1e')
        container.pack(fill="both", expand=True)
        
        # Create canvas and scrollbars
        canvas = tk.Canvas(container, bg='#1e1e1e', highlightthickness=0)
        v_scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        
        # Create scrollable frame
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        # Configure canvas
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        def on_mousewheel(event):
            # Vertical scrolling
            if not (event.state & 0x1):  # No Shift key
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            else:  # Shift + scroll = horizontal
                canvas.xview_scroll(int(-1*(event.delta/120)), "units")
                
        def bind_mousewheel(widget):
            """Recursively bind mousewheel to widget and children"""
            widget.bind("<MouseWheel>", on_mousewheel)
            widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
            
            for child in widget.winfo_children():
                bind_mousewheel(child)
                
        def configure_canvas(event):
            # Update the scrollable frame width to match canvas width if needed
            canvas_width = event.width
            if scrollable_frame.winfo_reqwidth() != canvas_width:
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        # Bind events
        scrollable_frame.bind('<Configure>', configure_scroll_region)
        canvas.bind('<Configure>', configure_canvas)
        bind_mousewheel(scrollable_frame)
        
        return scrollable_frame, canvas, container
        
    def log_message(self, message, log_widget=None):
        """
        Log a message to specified text widget or parent GUI log
        
        Args:
            message (str): Message to log
            log_widget (tk.Text, optional): Specific text widget to log to
        """
        try:
            if log_widget and hasattr(log_widget, 'insert'):
                log_widget.insert(tk.END, f"{message}\n")
                log_widget.see(tk.END)
            elif hasattr(self.parent_gui, 'log_mobile_message'):
                self.parent_gui.log_mobile_message(message)
            else:
                print(f"[{self.tab_name}] {message}")
        except Exception as e:
            print(f"Error logging message: {e}")
    
    def on_resize(self, width, height):
        """
        Handle window resize events for responsive design
        
        Args:
            width (int): New window width
            height (int): New window height
        """
        try:
            self.window_width = width
            self.window_height = height
            self.update_responsive_elements()
        except Exception as e:
            print(f"Error in {self.tab_name} resize handler: {e}")
    
    def update_responsive_elements(self):
        """
        Update responsive elements when window size changes.
        Override in subclasses to implement specific responsive behavior.
        """
        pass
    
    def get_responsive_font_size(self, base_size=12, min_size=8, max_size=16, divisor=100):
        """
        Calculate responsive font size based on window width
        
        Args:
            base_size (int): Base font size
            min_size (int): Minimum font size
            max_size (int): Maximum font size
            divisor (int): Divisor for responsive calculation
            
        Returns:
            int: Responsive font size
        """
        return max(min_size, min(max_size, self.window_width // divisor))
    
    def get_responsive_dimensions(self, base_width=25, base_height=10, width_divisor=50, height_divisor=50):
        """
        Calculate responsive widget dimensions
        
        Args:
            base_width (int): Base width
            base_height (int): Base height
            width_divisor (int): Divisor for width calculation
            height_divisor (int): Divisor for height calculation
            
        Returns:
            tuple: (width, height)
        """
        width = max(base_width // 2, min(base_width * 2, self.window_width // width_divisor))
        height = max(base_height // 2, min(base_height * 2, self.window_height // height_divisor))
        return width, height
