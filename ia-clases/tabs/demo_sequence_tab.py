# -*- coding: utf-8 -*-
"""
Demo Sequence Tab for RobotGUI - Manage sequences associated with PDF demo pages
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .base_tab import BaseTab
import os
import json

class DemoSequenceTab(BaseTab):
    """Demo sequence management tab"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "🎬 Demo Sequences"
        
        # Demo sequence manager
        try:
            from demo_sequence_manager import get_demo_sequence_manager
            self.demo_manager = get_demo_sequence_manager()
        except ImportError:
            self.demo_manager = None
            print("⚠️ Demo Sequence Manager no disponible")
        
        # UI variables
        self.selected_demo = tk.StringVar()
        self.selected_page = tk.IntVar(value=0)
        self.selected_sequence = tk.StringVar()
        self.page_timing = tk.DoubleVar(value=5.0)
        
    def setup_tab_content(self):
        """Setup the demo sequence tab content"""
        # Create scrollable frame
        main_content, canvas, container = self.create_scrollable_frame(self.tab_frame)
        
        # Title
        title = tk.Label(main_content, text="🎬 Demo Sequence Manager", 
                        font=('Arial', 18, 'bold'), 
                        bg='#1e1e1e', fg='#ffffff')
        title.pack(pady=(10, 20))
        
        # Subtitle
        subtitle = tk.Label(main_content, text="Asocia secuencias del robot a páginas de PDF para demostraciones", 
                           font=('Arial', 11), 
                           bg='#1e1e1e', fg='#888888')
        subtitle.pack(pady=(0, 20))
        
        # Main container
        main_container = tk.Frame(main_content, bg='#1e1e1e')
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Demo management
        left_frame = tk.Frame(main_container, bg='#1e1e1e')
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.setup_demo_management_panel(left_frame)
        
        # Right side - Page sequence assignment
        right_frame = tk.Frame(main_container, bg='#1e1e1e')
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.setup_page_sequence_panel(right_frame)
        
    def setup_demo_management_panel(self, parent):
        """Setup demo management panel"""
        demo_frame = tk.LabelFrame(parent, text="📚 Gestión de Demos", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        demo_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        content_frame = tk.Frame(demo_frame, bg='#2d2d2d')
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Demo list
        list_frame = tk.Frame(content_frame, bg='#2d2d2d')
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        tk.Label(list_frame, text="Demos Disponibles:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        # Demo listbox with scrollbar
        list_container = tk.Frame(list_frame, bg='#2d2d2d')
        list_container.pack(fill="both", expand=True, pady=(5, 0))
        
        self.demo_listbox = tk.Listbox(list_container, bg='#3d3d3d', fg='#ffffff',
                                     font=('Arial', 10), height=8)
        self.demo_listbox.pack(side="left", fill="both", expand=True)
        
        demo_scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.demo_listbox.yview)
        demo_scrollbar.pack(side="right", fill="y")
        self.demo_listbox.configure(yscrollcommand=demo_scrollbar.set)
        
        # Bind selection event
        self.demo_listbox.bind('<<ListboxSelect>>', self.on_demo_select)
        
        # Demo controls
        controls_frame = tk.Frame(content_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(controls_frame, text="➕ Crear Demo", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.create_demo).pack(side="left", padx=(0, 5))
        
        tk.Button(controls_frame, text="🗑️ Eliminar Demo", bg='#f44336', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.delete_demo).pack(side="left", padx=5)
        
        tk.Button(controls_frame, text="🔄 Actualizar", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.refresh_demos).pack(side="right")
        
        # Demo info
        info_frame = tk.LabelFrame(content_frame, text="ℹ️ Información del Demo", 
                                 font=('Arial', 11, 'bold'),
                                 bg='#3d3d3d', fg='#ffffff')
        info_frame.pack(fill="x", pady=(10, 0))
        
        self.demo_info_text = tk.Text(info_frame, bg='#2d2d2d', fg='#ffffff',
                                    font=('Arial', 9), height=4, wrap=tk.WORD)
        self.demo_info_text.pack(fill="x", padx=10, pady=10)
        
        # Load demos
        self.refresh_demos()
        
    def setup_page_sequence_panel(self, parent):
        """Setup page sequence assignment panel"""
        sequence_frame = tk.LabelFrame(parent, text="🎯 Asignación de Secuencias", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        sequence_frame.pack(fill="both", expand=True)
        
        content_frame = tk.Frame(sequence_frame, bg='#2d2d2d')
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Page selection
        page_frame = tk.Frame(content_frame, bg='#2d2d2d')
        page_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(page_frame, text="Página:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(side="left")
        
        self.page_spinbox = tk.Spinbox(page_frame, from_=0, to=0, width=10,
                                     textvariable=self.selected_page,
                                     font=('Arial', 10), command=self.on_page_change)
        self.page_spinbox.pack(side="left", padx=(10, 0))
        
        # Sequence selection
        seq_frame = tk.Frame(content_frame, bg='#2d2d2d')
        seq_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(seq_frame, text="Secuencia:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        self.sequence_combo = ttk.Combobox(seq_frame, textvariable=self.selected_sequence,
                                         font=('Arial', 10), state="readonly")
        self.sequence_combo.pack(fill="x", pady=(5, 0))
        
        # Timing
        timing_frame = tk.Frame(content_frame, bg='#2d2d2d')
        timing_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(timing_frame, text="Duración (segundos):", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(side="left")
        
        self.timing_spinbox = tk.Spinbox(timing_frame, from_=1.0, to=60.0, increment=0.5,
                                       textvariable=self.page_timing, width=10,
                                       font=('Arial', 10))
        self.timing_spinbox.pack(side="left", padx=(10, 0))
        
        # Assignment controls
        assign_frame = tk.Frame(content_frame, bg='#2d2d2d')
        assign_frame.pack(fill="x", pady=(0, 15))
        
        tk.Button(assign_frame, text="🔗 Asignar Secuencia", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 11, 'bold'), command=self.assign_sequence).pack(side="left", padx=(0, 5))
        
        tk.Button(assign_frame, text="❌ Remover Secuencia", bg='#f44336', fg='#ffffff',
                 font=('Arial', 11, 'bold'), command=self.remove_sequence).pack(side="left", padx=5)
        
        # Current assignment info
        info_frame = tk.LabelFrame(content_frame, text="📋 Secuencia Actual", 
                                 font=('Arial', 11, 'bold'),
                                 bg='#3d3d3d', fg='#ffffff')
        info_frame.pack(fill="both", expand=True)
        
        self.sequence_info_text = tk.Text(info_frame, bg='#2d2d2d', fg='#ffffff',
                                        font=('Arial', 9), height=6, wrap=tk.WORD)
        self.sequence_info_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load sequences
        self.refresh_sequences()
        
    def refresh_demos(self):
        """Refresh demo list"""
        if not self.demo_manager:
            return
        
        self.demo_listbox.delete(0, tk.END)
        demos = self.demo_manager.get_available_demos()
        
        for demo_name in demos:
            demo_info = self.demo_manager.get_demo_info(demo_name)
            if demo_info:
                page_count = demo_info.get('page_count', 0)
                title = demo_info.get('title', demo_name)
                self.demo_listbox.insert(tk.END, f"{title} ({page_count} páginas)")
            else:
                self.demo_listbox.insert(tk.END, demo_name)
    
    def refresh_sequences(self):
        """Refresh sequence list"""
        if not self.demo_manager:
            return
        
        self.demo_manager.refresh_sequences()
        sequences = list(self.demo_manager.available_sequences.keys())
        
        self.sequence_combo['values'] = sequences
        if sequences:
            self.sequence_combo.set(sequences[0])
    
    def on_demo_select(self, event):
        """Handle demo selection"""
        selection = self.demo_listbox.curselection()
        if not selection:
            return
        
        demo_name = self.demo_listbox.get(selection[0])
        # Extract demo name from display text
        if " (" in demo_name:
            demo_name = demo_name.split(" (")[0]
        
        self.selected_demo.set(demo_name)
        self.update_demo_info(demo_name)
        self.update_page_controls(demo_name)
    
    def update_demo_info(self, demo_name):
        """Update demo information display"""
        if not self.demo_manager:
            return
        
        demo_info = self.demo_manager.get_demo_info(demo_name)
        if not demo_info:
            return
        
        info_text = f"Demo: {demo_info['title']}\n"
        info_text += f"Descripción: {demo_info.get('description', 'Sin descripción')}\n"
        info_text += f"Páginas: {demo_info['page_count']}\n"
        info_text += f"PDF: {os.path.basename(demo_info['pdf_path'])}\n"
        info_text += f"Creado: {demo_info['created_at'][:19]}"
        
        self.demo_info_text.delete(1.0, tk.END)
        self.demo_info_text.insert(1.0, info_text)
    
    def update_page_controls(self, demo_name):
        """Update page controls for selected demo"""
        if not self.demo_manager:
            return
        
        demo_info = self.demo_manager.get_demo_info(demo_name)
        if not demo_info:
            return
        
        page_count = demo_info['page_count']
        self.page_spinbox.configure(to=page_count - 1)
        self.selected_page.set(0)
        self.on_page_change()
    
    def on_page_change(self):
        """Handle page change"""
        demo_name = self.selected_demo.get()
        page_num = self.selected_page.get()
        
        if not demo_name or not self.demo_manager:
            return
        
        # Get current sequence for this page
        sequence_info = self.demo_manager.get_page_sequence(demo_name, page_num)
        
        if sequence_info:
            sequence_name, timing = sequence_info
            self.selected_sequence.set(sequence_name)
            self.page_timing.set(timing)
            
            # Show sequence info
            sequence_data = self.demo_manager.load_sequence_data(sequence_name)
            if sequence_data:
                info_text = f"Secuencia: {sequence_name}\n"
                info_text += f"Duración: {timing} segundos\n"
                info_text += f"Posiciones: {len(sequence_data.get('positions', []))}\n"
                info_text += f"Timestamp: {sequence_data.get('timestamp', 'N/A')}"
            else:
                info_text = f"Secuencia: {sequence_name}\nDuración: {timing} segundos"
        else:
            self.selected_sequence.set("")
            self.page_timing.set(5.0)
            info_text = "Ninguna secuencia asignada a esta página"
        
        self.sequence_info_text.delete(1.0, tk.END)
        self.sequence_info_text.insert(1.0, info_text)
    
    def create_demo(self):
        """Create a new demo"""
        if not self.demo_manager:
            messagebox.showerror("Error", "Demo Sequence Manager no disponible")
            return
        
        # Create demo creation dialog
        dialog = tk.Toplevel(self.parent_gui.root)
        dialog.title("Crear Nuevo Demo")
        dialog.geometry("500x300")
        dialog.configure(bg='#1e1e1e')
        dialog.transient(self.parent_gui.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Content
        content = tk.Frame(dialog, bg='#1e1e1e')
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Demo name
        tk.Label(content, text="Nombre del Demo:", bg='#1e1e1e', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        demo_name_var = tk.StringVar()
        demo_name_entry = tk.Entry(content, textvariable=demo_name_var, bg='#3d3d3d', fg='#ffffff',
                                 font=('Arial', 10), width=40)
        demo_name_entry.pack(fill="x", pady=(5, 15))
        
        # PDF selection
        tk.Label(content, text="Archivo PDF:", bg='#1e1e1e', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        pdf_frame = tk.Frame(content, bg='#1e1e1e')
        pdf_frame.pack(fill="x", pady=(5, 15))
        
        pdf_path_var = tk.StringVar()
        pdf_entry = tk.Entry(pdf_frame, textvariable=pdf_path_var, bg='#3d3d3d', fg='#ffffff',
                           font=('Arial', 10), state="readonly")
        pdf_entry.pack(side="left", fill="x", expand=True)
        
        def select_pdf():
            file_path = filedialog.askopenfilename(
                title="Seleccionar PDF",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if file_path:
                pdf_path_var.set(file_path)
        
        tk.Button(pdf_frame, text="📁 Seleccionar", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=select_pdf).pack(side="right", padx=(10, 0))
        
        # Title and description
        tk.Label(content, text="Título (opcional):", bg='#1e1e1e', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        title_var = tk.StringVar()
        title_entry = tk.Entry(content, textvariable=title_var, bg='#3d3d3d', fg='#ffffff',
                             font=('Arial', 10), width=40)
        title_entry.pack(fill="x", pady=(5, 15))
        
        tk.Label(content, text="Descripción (opcional):", bg='#1e1e1e', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(anchor="w")
        
        desc_text = tk.Text(content, bg='#3d3d3d', fg='#ffffff', font=('Arial', 10),
                          height=3, wrap=tk.WORD)
        desc_text.pack(fill="x", pady=(5, 15))
        
        # Buttons
        button_frame = tk.Frame(content, bg='#1e1e1e')
        button_frame.pack(fill="x", pady=(10, 0))
        
        def create_demo_action():
            demo_name = demo_name_var.get().strip()
            pdf_path = pdf_path_var.get()
            title = title_var.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            
            if not demo_name:
                messagebox.showerror("Error", "El nombre del demo es requerido")
                return
            
            if not pdf_path:
                messagebox.showerror("Error", "Debe seleccionar un archivo PDF")
                return
            
            success = self.demo_manager.create_demo_config(demo_name, pdf_path, title, description)
            
            if success:
                messagebox.showinfo("Éxito", f"Demo '{demo_name}' creado exitosamente")
                self.refresh_demos()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Error creando el demo")
        
        tk.Button(button_frame, text="✅ Crear", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 11, 'bold'), command=create_demo_action).pack(side="left")
        
        tk.Button(button_frame, text="❌ Cancelar", bg='#f44336', fg='#ffffff',
                 font=('Arial', 11, 'bold'), command=dialog.destroy).pack(side="right")
        
        # Focus on name entry
        demo_name_entry.focus()
    
    def delete_demo(self):
        """Delete selected demo"""
        selection = self.demo_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un demo para eliminar")
            return
        
        demo_name = self.demo_listbox.get(selection[0])
        if " (" in demo_name:
            demo_name = demo_name.split(" (")[0]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el demo '{demo_name}'?"):
            if self.demo_manager.delete_demo(demo_name):
                messagebox.showinfo("Éxito", f"Demo '{demo_name}' eliminado")
                self.refresh_demos()
                self.demo_info_text.delete(1.0, tk.END)
                self.sequence_info_text.delete(1.0, tk.END)
            else:
                messagebox.showerror("Error", "Error eliminando el demo")
    
    def assign_sequence(self):
        """Assign sequence to current page"""
        demo_name = self.selected_demo.get()
        page_num = self.selected_page.get()
        sequence_name = self.selected_sequence.get()
        timing = self.page_timing.get()
        
        if not demo_name:
            messagebox.showwarning("Advertencia", "Seleccione un demo")
            return
        
        if not sequence_name:
            messagebox.showwarning("Advertencia", "Seleccione una secuencia")
            return
        
        if self.demo_manager.assign_sequence_to_page(demo_name, page_num, sequence_name, timing):
            messagebox.showinfo("Éxito", f"Secuencia '{sequence_name}' asignada a página {page_num}")
            self.on_page_change()
        else:
            messagebox.showerror("Error", "Error asignando la secuencia")
    
    def remove_sequence(self):
        """Remove sequence from current page"""
        demo_name = self.selected_demo.get()
        page_num = self.selected_page.get()
        
        if not demo_name:
            messagebox.showwarning("Advertencia", "Seleccione un demo")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Remover secuencia de la página {page_num}?"):
            if self.demo_manager.remove_sequence_from_page(demo_name, page_num):
                messagebox.showinfo("Éxito", f"Secuencia removida de página {page_num}")
                self.on_page_change()
            else:
                messagebox.showerror("Error", "Error removiendo la secuencia")
