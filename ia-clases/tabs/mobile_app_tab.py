# -*- coding: utf-8 -*-
"""
Mobile App Tab for RobotGUI - Mobile API Server Management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .base_tab import BaseTab
import threading
import time

class MobileAppTab(BaseTab):
    """Mobile app connection and management tab"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "📱 Mobile App"
        
        # Initialize mobile app variables
        self.api_port = 8080
        self.mobile_port_var = tk.IntVar(value=self.api_port)
        self.connected_devices = []
        self.mobile_server_running = False
        self.mobile_start_time = None
        self.log_connection_calls = True
        
        self.api_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'active_connections': 0,
            'uptime': 0
        }
        
        # UI components
        self.server_status_indicator = None
        self.server_status_label = None
        self.server_url_label = None
        self.ip_display_label = None
        self.mobile_log_text = None
        self.devices_listbox = None
        self.endpoints_listbox = None
        self.stats_labels = {}
        self.connection_log_button = None
        
    def setup_tab_content(self):
        """Setup the mobile app tab content"""
        # Create scrollable frame
        main_content, canvas, container = self.create_scrollable_frame(self.tab_frame)
        
        # Title
        mobile_title = tk.Label(main_content, text="Conexión con Aplicación Móvil", 
                               font=('Arial', 18, 'bold'), 
                               bg='#1e1e1e', fg='#ffffff')
        mobile_title.pack(pady=(10, 20))
        
        # Left panel - Server Configuration and Status
        left_panel = tk.LabelFrame(main_content, text="Configuración del Servidor API", 
                                 font=('Arial', 14, 'bold'),
                                 bg='#2d2d2d', fg='#ffffff')
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Server configuration
        self.setup_server_config(left_panel)
        
        # Connection log
        self.setup_connection_log(left_panel)
        
        # Right panel - Devices and Statistics
        right_panel = tk.LabelFrame(main_content, text="Dispositivos y Estadísticas", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Connected devices
        self.setup_devices_section(right_panel)
        
        # API statistics
        self.setup_statistics_section(right_panel)
        
        # API endpoints
        self.setup_endpoints_section(right_panel)
        
        # Start periodic updates
        self.update_mobile_stats()
        
    def setup_server_config(self, parent):
        """Setup server configuration section"""
        status_frame = tk.Frame(parent, bg='#2d2d2d')
        status_frame.pack(fill="x", padx=10, pady=10)
        
        # Server status
        tk.Label(status_frame, text="Estado del Servidor:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        self.server_status_frame = tk.Frame(status_frame, bg='#2d2d2d')
        self.server_status_frame.pack(fill="x", pady=(5, 10))
        
        self.server_status_indicator = tk.Label(self.server_status_frame, text="●", 
                                              font=('Arial', 16), bg='#2d2d2d', fg='#f44336')
        self.server_status_indicator.pack(side="left")
        
        self.server_status_label = tk.Label(self.server_status_frame, text="Desconectado", 
                                          font=('Arial', 12), bg='#2d2d2d', fg='#ffffff')
        self.server_status_label.pack(side="left", padx=(5, 0))
        
        # Port configuration
        config_frame = tk.Frame(parent, bg='#2d2d2d')
        config_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(config_frame, text="Puerto:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        port_frame = tk.Frame(config_frame, bg='#2d2d2d')
        port_frame.pack(fill="x", pady=(5, 10))
        
        port_entry = tk.Entry(port_frame, textvariable=self.mobile_port_var, 
                             bg='#3d3d3d', fg='#ffffff', font=('Arial', 10), width=10)
        port_entry.pack(side="left")
        
        tk.Button(port_frame, text="Aplicar", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.update_mobile_port).pack(side="left", padx=(10, 0))
        
        # Server URL
        tk.Label(config_frame, text="URL del Servidor:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(anchor="w")
        
        local_ip = self.get_local_ip()
        self.server_url_label = tk.Label(config_frame, text=f"http://{local_ip}:{self.api_port}/api", 
                                        bg='#3d3d3d', fg='#4CAF50', font=('Courier New', 10),
                                        relief="sunken", anchor="w")
        self.server_url_label.pack(fill="x", pady=(5, 10))
        
        # IP display
        ip_frame = tk.Frame(config_frame, bg='#2d2d2d')
        ip_frame.pack(fill="x", pady=5)
        
        tk.Label(ip_frame, text="IP Local:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(side="left")
        
        self.ip_display_label = tk.Label(ip_frame, text=local_ip, bg='#4d4d4d', fg='#00ff00',
                                       font=('Courier New', 10, 'bold'), relief="sunken")
        self.ip_display_label.pack(side="left", padx=(10, 0))
        
        tk.Button(ip_frame, text="📋 Copiar", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), 
                 command=lambda: self.copy_to_clipboard(local_ip)).pack(side="right")
        
        # Server controls
        controls_frame = tk.Frame(parent, bg='#2d2d2d')
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(controls_frame, text="🟢 Iniciar", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.start_mobile_server).pack(side="left", padx=5)
        tk.Button(controls_frame, text="🔴 Detener", bg='#f44336', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.stop_mobile_server).pack(side="left", padx=5)
        tk.Button(controls_frame, text="🔄 Reiniciar", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 12, 'bold'), command=self.restart_mobile_server).pack(side="left", padx=5)
        
    def setup_connection_log(self, parent):
        """Setup connection log section"""
        log_frame = tk.LabelFrame(parent, text="Registro de Conexiones", 
                                font=('Arial', 12, 'bold'),
                                bg='#3d3d3d', fg='#ffffff')
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Log controls
        log_controls = tk.Frame(log_frame, bg='#3d3d3d')
        log_controls.pack(fill="x", padx=5, pady=5)
        
        self.connection_log_button = tk.Button(log_controls, text="🔇 Pausar logs", 
                                             bg='#FF5722', fg='#ffffff',
                                             font=('Arial', 10, 'bold'), 
                                             command=self.toggle_connection_logging)
        self.connection_log_button.pack(side="left", padx=(0, 10))
        
        tk.Button(log_controls, text="🗑️ Limpiar", bg='#607D8B', fg='#ffffff',
                 font=('Arial', 10, 'bold'), 
                 command=self.clear_connection_log).pack(side="left")
        
        # Log text
        log_content_frame = tk.Frame(log_frame, bg='#3d3d3d')
        log_content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.mobile_log_text = tk.Text(log_content_frame, bg='#1e1e1e', fg='#ffffff',
                                     font=('Courier New', 9), wrap="word", height=8)
        log_scrollbar = tk.Scrollbar(log_content_frame, orient="vertical")
        self.mobile_log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.mobile_log_text.yview)
        
        self.mobile_log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
    def setup_devices_section(self, parent):
        """Setup connected devices section"""
        devices_frame = tk.LabelFrame(parent, text="Dispositivos Conectados", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#3d3d3d', fg='#ffffff')
        devices_frame.pack(fill="x", padx=10, pady=10)
        
        devices_content = tk.Frame(devices_frame, bg='#3d3d3d')
        devices_content.pack(fill="x", padx=5, pady=5)
        
        self.devices_listbox = tk.Listbox(devices_content, bg='#4d4d4d', fg='#ffffff',
                                        font=('Arial', 10), selectbackground='#4CAF50', height=6)
        devices_scrollbar = tk.Scrollbar(devices_content, orient="vertical")
        self.devices_listbox.config(yscrollcommand=devices_scrollbar.set)
        devices_scrollbar.config(command=self.devices_listbox.yview)
        
        self.devices_listbox.pack(side="left", fill="both", expand=True)
        devices_scrollbar.pack(side="right", fill="y")
        
    def setup_statistics_section(self, parent):
        """Setup API statistics section"""
        stats_frame = tk.LabelFrame(parent, text="Estadísticas de la API", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#3d3d3d', fg='#ffffff')
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        stats_content = tk.Frame(stats_frame, bg='#3d3d3d')
        stats_content.pack(fill="both", expand=True, padx=5, pady=5)
        
        stats_data = [
            ('Total Requests', 'total_requests'),
            ('Successful', 'successful_requests'),
            ('Failed', 'failed_requests'),
            ('Active Connections', 'active_connections'),
            ('Uptime (min)', 'uptime')
        ]
        
        for label_text, key in stats_data:
            row_frame = tk.Frame(stats_content, bg='#3d3d3d')
            row_frame.pack(fill="x", pady=2)
            
            tk.Label(row_frame, text=f"{label_text}:", bg='#3d3d3d', fg='#ffffff',
                    font=('Arial', 10, 'bold')).pack(side="left")
            
            value_label = tk.Label(row_frame, text="0", bg='#3d3d3d', fg='#4CAF50',
                                 font=('Arial', 10, 'bold'))
            value_label.pack(side="right")
            
            self.stats_labels[key] = value_label
    
    def setup_endpoints_section(self, parent):
        """Setup API endpoints section"""
        endpoints_frame = tk.LabelFrame(parent, text="Estado de Endpoints", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#3d3d3d', fg='#ffffff')
        endpoints_frame.pack(fill="x", padx=10, pady=10)
        
        endpoints_content = tk.Frame(endpoints_frame, bg='#3d3d3d')
        endpoints_content.pack(fill="x", padx=5, pady=5)
        
        self.endpoints_listbox = tk.Listbox(endpoints_content, bg='#4d4d4d', fg='#ffffff',
                                          font=('Courier New', 9), selectbackground='#4CAF50', height=8)
        endpoints_scrollbar = tk.Scrollbar(endpoints_content, orient="vertical")
        self.endpoints_listbox.config(yscrollcommand=endpoints_scrollbar.set)
        endpoints_scrollbar.config(command=self.endpoints_listbox.yview)
        
        self.endpoints_listbox.pack(side="left", fill="both", expand=True)
        endpoints_scrollbar.pack(side="right", fill="y")
        
        # Update endpoints list
        self.update_endpoints_list()
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copiado", f"Texto copiado: {text}")
        except Exception as e:
            messagebox.showerror("Error", f"Error copiando al portapapeles: {e}")
    
    def update_mobile_port(self):
        """Update mobile API port"""
        try:
            new_port = self.mobile_port_var.get()
            if 1024 <= new_port <= 65535:
                self.api_port = new_port
                local_ip = self.get_local_ip()
                self.server_url_label.config(text=f"http://{local_ip}:{self.api_port}/api")
                self.log_mobile_message(f"Puerto actualizado a: {new_port}")
            else:
                messagebox.showerror("Error", "Puerto debe estar entre 1024 y 65535")
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando puerto: {e}")
    
    def start_mobile_server(self):
        """Start mobile API server"""
        try:
            if hasattr(self.parent_gui, 'start_mobile_server'):
                self.parent_gui.start_mobile_server()
            else:
                # Simulated server start
                self.mobile_server_running = True
                self.mobile_start_time = time.time()
                
            self.update_mobile_status()
            self.log_mobile_message("Servidor móvil iniciado")
        except Exception as e:
            messagebox.showerror("Error", f"Error iniciando servidor: {e}")
    
    def stop_mobile_server(self):
        """Stop mobile API server"""
        try:
            if hasattr(self.parent_gui, 'stop_mobile_server'):
                self.parent_gui.stop_mobile_server()
            else:
                # Simulated server stop
                self.mobile_server_running = False
                self.mobile_start_time = None
                
            self.update_mobile_status()
            self.log_mobile_message("Servidor móvil detenido")
        except Exception as e:
            messagebox.showerror("Error", f"Error deteniendo servidor: {e}")
    
    def restart_mobile_server(self):
        """Restart mobile API server"""
        self.stop_mobile_server()
        self.tab_frame.after(1000, self.start_mobile_server)  # Wait 1 second before restart
    
    def toggle_connection_logging(self):
        """Toggle connection logging on/off"""
        self.log_connection_calls = not self.log_connection_calls
        if self.connection_log_button:
            if self.log_connection_calls:
                self.connection_log_button.config(text="🔇 Pausar logs", bg='#FF5722')
            else:
                self.connection_log_button.config(text="🔊 Reanudar logs", bg='#4CAF50')
        
        status = "activado" if self.log_connection_calls else "pausado"
        self.log_mobile_message(f"Logging de conexiones {status}")
    
    def clear_connection_log(self):
        """Clear connection log"""
        if self.mobile_log_text:
            self.mobile_log_text.delete("1.0", tk.END)
    
    def log_mobile_message(self, message):
        """Log message to mobile log text widget"""
        if self.mobile_log_text:
            timestamp = time.strftime("%H:%M:%S")
            self.mobile_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.mobile_log_text.see(tk.END)
    
    def update_mobile_status(self):
        """Update mobile server status display"""
        if self.server_status_indicator and self.server_status_label:
            if self.mobile_server_running:
                self.server_status_indicator.config(fg='#4CAF50')
                self.server_status_label.config(text="Conectado")
            else:
                self.server_status_indicator.config(fg='#f44336')
                self.server_status_label.config(text="Desconectado")
    
    def update_endpoints_list(self):
        """Update the endpoints list"""
        if self.endpoints_listbox:
            self.endpoints_listbox.delete(0, tk.END)
            endpoints = [
                "GET  /api/status",
                "GET  /api/position", 
                "GET  /api/classes",
                "GET  /api/connection",
                "GET  /api/presets",
                "POST /api/robot/move",
                "POST /api/robot/speak",
                "POST /api/class/start",
                "POST /api/class/stop",
                "POST /api/preset/execute",
                "POST /api/robot/emergency"
            ]
            for endpoint in endpoints:
                self.endpoints_listbox.insert(tk.END, endpoint)
    
    def update_mobile_stats(self):
        """Update mobile statistics periodically"""
        try:
            # Update uptime
            if self.mobile_server_running and self.mobile_start_time:
                uptime_seconds = time.time() - self.mobile_start_time
                uptime_minutes = int(uptime_seconds / 60)
                self.api_stats['uptime'] = uptime_minutes
            else:
                self.api_stats['uptime'] = 0
            
            # Update statistics labels
            for key, label in self.stats_labels.items():
                if label:
                    label.config(text=str(self.api_stats[key]))
            
            # Schedule next update
            self.tab_frame.after(5000, self.update_mobile_stats)  # Update every 5 seconds
            
        except Exception as e:
            self.log_message(f"Error updating mobile stats: {e}")
    
    def increment_api_stat(self, stat_name):
        """Increment an API statistic"""
        if stat_name in self.api_stats:
            self.api_stats[stat_name] += 1
    
    def add_connected_device(self, device_info):
        """Add a connected device to the list"""
        try:
            if device_info not in self.connected_devices:
                self.connected_devices.append(device_info)
                if self.devices_listbox:
                    self.devices_listbox.insert(tk.END, device_info)
                    # Keep only last 20 devices
                    if len(self.connected_devices) > 20:
                        self.connected_devices.pop(0)
                        self.devices_listbox.delete(0)
        except Exception as e:
            self.log_message(f"Error adding device: {e}")
