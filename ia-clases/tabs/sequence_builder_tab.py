# -*- coding: utf-8 -*-
"""
Sequence Builder Tab for RobotGUI - Robot Movement Sequence Creation with ESP32 Integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
import threading
import datetime
import os
import math
from .base_tab import BaseTab

# Import ESP32 services
try:
    from services.esp32_services.esp32_client import ESP32Client
    from services.esp32_services.esp32_config_binary import ESP32BinaryConfig
    ESP32_AVAILABLE = True
except ImportError:
    ESP32_AVAILABLE = False
    print("⚠️ ESP32 services not available")

class SequenceBuilderTab(BaseTab):
    """Sequence builder tab for creating and managing robot movement sequences with ESP32 integration"""
    
    def __init__(self, parent_gui, notebook):
        super().__init__(parent_gui, notebook)
        self.tab_name = "🎬 Sequence Builder"
        
        # Sequence builder state
        self.current_sequence = []
        self.is_recording = False
        self.is_playing = False
        self.recording_start_time = None
        self.sequence_name = tk.StringVar(value="New_Sequence")
        self.sequence_title = tk.StringVar(value="New Sequence")
        
        # ESP32 integration
        self.esp32_client = None
        self.esp32_connected = False
        self.esp32_config = None
        self.debug_mode = False  # Debug mode for simulating ESP32 connection
        
        # Recording state
        self.recorded_actions = []
        self.current_movement = None
        self.movement_counter = 1
        
        # Control mode (sliders vs arrows)
        self.control_mode = tk.StringVar(value="sliders")  # "sliders" or "arrows"

        # Button debouncing variables
        self.button_cooldowns = {}
        self.button_states = {}
        self.COOLDOWN_TIME = 0.5  # Reduced to 0.5 seconds cooldown
        self.instant_buttons = {
            "home_position": True,
            "arm_rest_position": True,
            "arm_up": True,
            "arms_open": True,
            "wave_gesture": True,
            "hug_gesture": True,
            "look_around": True,
            "speak_text": True
        }  # Buttons that can be clicked instantly
        
        # Initialize ESP32 if available
        if ESP32_AVAILABLE:
            self.init_esp32_integration()
    
    def init_esp32_integration(self):
        """Initialize ESP32 integration"""
        try:
            # Load ESP32 configuration
            self.esp32_config = ESP32BinaryConfig()
            config_data = self.esp32_config.load_config()
            
            if config_data:
                print(f"✅ ESP32 config loaded: {config_data.host}:{config_data.port}")
            else:
                print("⚠️ No ESP32 config found, using defaults")
            
            # Initialize ESP32 client
            self.esp32_client = ESP32Client()
            
        except Exception as e:
            print(f"❌ Error initializing ESP32 integration: {e}")
        
    def setup_tab_content(self):
        """Setup the sequence builder tab content with ESP32 integration"""
        # Create scrollable frame for sequence builder content
        content_frame, canvas, container = self.create_scrollable_frame(self.tab_frame)
        
        # Title for sequence builder tab
        sequence_title = tk.Label(content_frame, text="Robot Movement Sequence Builder with ESP32 Integration", 
                                 font=('Arial', 18, 'bold'), 
                                 bg='#1e1e1e', fg='#ffffff')
        sequence_title.pack(pady=(10, 20))
        
        # Main content area with three columns
        main_content = tk.Frame(content_frame, bg='#1e1e1e')
        main_content.pack(fill="both", expand=True)
        
        # Left column - ESP32 Connection and Controls
        left_frame = tk.Frame(main_content, bg='#1e1e1e')
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # ESP32 connection panel
        self.setup_esp32_connection_panel(left_frame)
        
        # ESP32 movement controls panel
        self.setup_esp32_movement_controls(left_frame)
        
        # Center column - Recording, Playback, and Management
        center_frame = tk.Frame(main_content, bg='#1e1e1e')
        center_frame.pack(side="left", fill="both", expand=True, padx=5)

          # Right column - Sequence details
        right_frame = tk.Frame(main_content, bg='#1e1e1e')
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Current sequence details
        self.setup_sequence_details_panel(center_frame)
        
        # Recording panel
        self.setup_sequence_recording_panel(center_frame)
        
        # Sequence management panel (moved here)
        self.setup_sequence_management_panel(center_frame)
        
        # Playback control panel
        self.setup_sequence_playback_panel(center_frame)
        
        
        
    def setup_esp32_connection_panel(self, parent):
        """Setup ESP32 connection panel"""
        if not ESP32_AVAILABLE:
            return
            
        conn_frame = tk.LabelFrame(parent, text="🔌 ESP32 Connection", 
                                       font=('Arial', 14, 'bold'),
                                       bg='#2d2d2d', fg='#ffffff')
        conn_frame.pack(fill="x", pady=(0, 10))
        
        conn_content = tk.Frame(conn_frame, bg='#2d2d2d')
        conn_content.pack(fill="x", padx=10, pady=10)
        
        # Connection status
        self.esp32_status_label = tk.Label(conn_content, text="🔴 Disconnected", 
                                         bg='#2d2d2d', fg='#f44336', 
                                         font=('Arial', 11, 'bold'))
        self.esp32_status_label.pack(anchor="w", pady=(0, 10))
        
        # Connection controls
        controls_frame = tk.Frame(conn_content, bg='#2d2d2d')
        controls_frame.pack(fill="x")
            
        self.connect_btn = tk.Button(controls_frame, text="🔗 Connect", 
                                   bg='#4CAF50', fg='#ffffff',
                                   font=('Arial', 10, 'bold'), 
                                   command=self.connect_esp32)
        self.connect_btn.pack(side="left", padx=(0, 5))
        
        self.disconnect_btn = tk.Button(controls_frame, text="🔌 Disconnect", 
                                      bg='#f44336', fg='#ffffff',
                                      font=('Arial', 10, 'bold'), 
                                      command=self.disconnect_esp32)
        self.disconnect_btn.pack(side="left", padx=5)
        
        self.disconnect_btn.config(state="disabled")
        
        # Test connection button
        tk.Button(controls_frame, text="🧪 Test", 
                 bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), 
                 command=self.test_esp32_connection).pack(side="right")
        
        # Debug mode button
        self.debug_btn = tk.Button(controls_frame, text="🐛 Debug Mode", 
                     bg='#FF9800', fg='#ffffff',
                                 font=('Arial', 10, 'bold'), 
                                 command=self.toggle_debug_mode)
        self.debug_btn.pack(side="right", padx=(5, 0))
    
    def setup_esp32_movement_controls(self, parent):
        """Setup ESP32 movement controls panel"""
        if not ESP32_AVAILABLE:
            return
            
        controls_frame = tk.LabelFrame(parent, text="🤖 Robot Movement Controls", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        controls_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        controls_content = tk.Frame(controls_frame, bg='#2d2d2d')
        controls_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control mode toggle
        mode_frame = tk.Frame(controls_content, bg='#2d2d2d')
        mode_frame.pack(fill="x", pady=(0, 10))

        tk.Label(mode_frame, text="Control Mode:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 11, 'bold')).pack(side="left")

        self.slider_radio = tk.Radiobutton(mode_frame, text="🎚️ Sliders", variable=self.control_mode,
                                         value="sliders", bg='#2d2d2d', fg='#ffffff',
                                         selectcolor='#007bff', activebackground='#2d2d2d',
                                         activeforeground='#ffffff', command=self.update_control_mode)
        self.slider_radio.pack(side="left", padx=(10, 5))

        self.arrow_radio = tk.Radiobutton(mode_frame, text="⬆️⬇️ Arrows", variable=self.control_mode,
                                        value="arrows", bg='#2d2d2d', fg='#ffffff',
                                        selectcolor='#007bff', activebackground='#2d2d2d',
                                        activeforeground='#ffffff', command=self.update_control_mode)
        self.arrow_radio.pack(side="left", padx=5)

        # Container for controls (will be updated based on mode)
        self.controls_container = tk.Frame(controls_content, bg='#2d2d2d')
        self.controls_container.pack(fill="both", expand=True)

        # Initialize with sliders
        self.update_control_mode()

    # ===============================
    # BUTTON DEBOUNCING METHODS
    # ===============================

    def debounce_button(self, button_name, callback, *args):
        """Debounce button clicks to prevent multiple rapid requests"""
        try:
            import time

            # Check if this is an instant button (no cooldown needed)
            is_instant = self.instant_buttons.get(button_name, False)
            
            # For instant buttons, just execute immediately
            if is_instant:
                try:
                    callback(*args)
                    print(f"⚡ Instant execution for '{button_name}'")
                except Exception as e:
                    print(f"❌ Error in instant button callback '{button_name}': {e}")
                return

            # For non-instant buttons, apply cooldown
            if button_name in self.button_cooldowns:
                current_time = time.time()
                if current_time - self.button_cooldowns[button_name] < self.COOLDOWN_TIME:
                    print(f"⏳ Button '{button_name}' is on cooldown. Please wait.")
                    return

            # Set cooldown timestamp
            self.button_cooldowns[button_name] = time.time()

            # Disable button visually if it exists
            if button_name in self.button_states and self.button_states[button_name]:
                try:
                    self.button_states[button_name].config(state="disabled", text="⏳")
                except:
                    pass

            # Execute callback
            try:
                callback(*args)
            except Exception as e:
                print(f"❌ Error in button callback '{button_name}': {e}")

            # Re-enable button after cooldown
            def reenable_button():
                try:
                    if button_name in self.button_states and self.button_states[button_name]:
                        # Get original text from button name
                        text_map = {
                            "home_position": "🏠 Rest Position",
                            "wave_gesture": "👋 Wave",
                            "hug_gesture": "🤗 Hug",
                            "look_around": "👀 Look Around",
                            "arm_rest_position": "🛌 Rest Position",
                            "arm_up": "💪 Arm Up",
                            "arms_open": "🙌 Arms Open",
                            "speak_text": "🗣️ Speak"
                        }
                        original_text = text_map.get(button_name, button_name)
                        self.button_states[button_name].config(state="normal", text=original_text)
                except Exception as e:
                    print(f"❌ Error re-enabling button '{button_name}': {e}")

            # Schedule re-enabling after cooldown
            self.parent_gui.after(int(self.COOLDOWN_TIME * 1000), reenable_button)

        except Exception as e:
            print(f"❌ Error in debounce_button: {e}")

    def store_button_reference(self, button_name, button_widget):
        """Store button reference for debouncing"""
        self.button_states[button_name] = button_widget

    def reset_button_cooldowns(self):
        """Reset all button cooldowns manually"""
        try:
            self.button_cooldowns.clear()
            print("🔄 All button cooldowns reset")
            messagebox.showinfo("Cooldown Reset", "All button cooldowns have been reset!")
        except Exception as e:
            print(f"❌ Error resetting cooldowns: {e}")
            messagebox.showerror("Error", f"Failed to reset cooldowns:\n{str(e)}")

    def configure_instant_buttons(self):
        """Configure which buttons should be instant (no cooldown)"""
        try:
            # Create a simple dialog to configure instant buttons
            config_window = tk.Toplevel(self.parent_gui.root)
            config_window.title("Configure Instant Buttons")
            config_window.geometry("400x500")
            config_window.configure(bg='#2d2d2d')
            config_window.resizable(False, False)
            
            # Center the window
            config_window.transient(self.parent_gui.root)
            config_window.grab_set()
            
            # Title
            title_label = tk.Label(config_window, text="⚡ Configure Instant Buttons", 
                                 font=('Arial', 14, 'bold'), bg='#2d2d2d', fg='#ffffff')
            title_label.pack(pady=10)
            
            # Description
            desc_label = tk.Label(config_window, 
                                text="Instant buttons can be clicked without waiting for cooldown.\nSelect which buttons should be instant:",
                                font=('Arial', 10), bg='#2d2d2d', fg='#cccccc',
                                justify="center")
            desc_label.pack(pady=(0, 20))
            
            # Checkboxes for each button
            checkboxes = {}
            checkbox_frame = tk.Frame(config_window, bg='#2d2d2d')
            checkbox_frame.pack(fill="both", expand=True, padx=20)
            
            button_names = {
                "home_position": "🏠 Rest Position",
                "arm_rest_position": "🛌 Arm Rest Position", 
                "arm_up": "💪 Arm Up",
                "arms_open": "🙌 Arms Open",
                "wave_gesture": "👋 Wave",
                "hug_gesture": "🤗 Hug",
                "look_around": "👀 Look Around",
                "speak_text": "🗣️ Speak"
            }
            
            for button_key, button_text in button_names.items():
                var = tk.BooleanVar(value=self.instant_buttons.get(button_key, False))
                checkboxes[button_key] = var
                
                cb = tk.Checkbutton(checkbox_frame, text=button_text, variable=var,
                                  bg='#2d2d2d', fg='#ffffff', selectcolor='#4d4d4d',
                                  activebackground='#2d2d2d', activeforeground='#ffffff',
                                  font=('Arial', 11))
                cb.pack(anchor="w", pady=2)
            
            # Buttons
            button_frame = tk.Frame(config_window, bg='#2d2d2d')
            button_frame.pack(fill="x", pady=20, padx=20)
            
            def save_config():
                try:
                    # Update instant buttons configuration
                    for button_key, var in checkboxes.items():
                        self.instant_buttons[button_key] = var.get()
                    
                    # Count instant buttons
                    instant_count = sum(1 for v in self.instant_buttons.values() if v)
                    
                    config_window.destroy()
                    messagebox.showinfo("Configuration Saved", 
                                      f"Instant button configuration saved!\n\n"
                                      f"Instant buttons: {instant_count}/{len(button_names)}\n"
                                      f"Regular cooldown: {self.COOLDOWN_TIME}s")
                    
                    print(f"⚡ Updated instant buttons: {[k for k, v in self.instant_buttons.items() if v]}")
                    
                except Exception as e:
                    print(f"❌ Error saving configuration: {e}")
                    messagebox.showerror("Error", f"Failed to save configuration: {e}")
            
            def reset_to_defaults():
                try:
                    # Reset to default instant buttons
                    default_instant = {
                        "home_position": True,
                        "arm_rest_position": True,
                        "arm_up": True,
                        "arms_open": True,
                        "wave_gesture": True,
                        "hug_gesture": True,
                        "look_around": True,
                        "speak_text": True
                    }
                    
                    for button_key, var in checkboxes.items():
                        var.set(default_instant.get(button_key, False))
                    
                    messagebox.showinfo("Reset", "Reset to default instant button configuration!")
                    
                except Exception as e:
                    print(f"❌ Error resetting configuration: {e}")
                    messagebox.showerror("Error", f"Failed to reset configuration: {e}")
            
            tk.Button(button_frame, text="💾 Save", bg='#4CAF50', fg='#ffffff',
                     font=('Arial', 11, 'bold'), command=save_config).pack(side="left", padx=(0, 10))
            
            tk.Button(button_frame, text="🔄 Reset", bg='#FF9800', fg='#ffffff',
                     font=('Arial', 11, 'bold'), command=reset_to_defaults).pack(side="left", padx=10)
            
            tk.Button(button_frame, text="❌ Cancel", bg='#f44336', fg='#ffffff',
                     font=('Arial', 11, 'bold'), command=config_window.destroy).pack(side="right")
            
        except Exception as e:
            print(f"❌ Error configuring instant buttons: {e}")
            messagebox.showerror("Error", f"Failed to open configuration: {e}")

    def get_button_status(self):
        """Get current status of all buttons"""
        try:
            import time
            current_time = time.time()
            status = []

            # Count instant vs regular buttons
            instant_count = 0
            regular_count = 0
            
            for button_name in self.button_states.keys():
                is_instant = self.instant_buttons.get(button_name, False)
                
                if is_instant:
                    instant_count += 1
                    status.append(f"⚡ {button_name}: INSTANT (no cooldown)")
                else:
                    regular_count += 1
                    if button_name in self.button_cooldowns:
                        cooldown_time = self.button_cooldowns[button_name]
                        remaining = max(0, self.COOLDOWN_TIME - (current_time - cooldown_time))
                        if remaining > 0:
                            status.append(f"⏳ {button_name}: {remaining:.1f}s remaining")
                        else:
                            status.append(f"✅ {button_name}: Ready")
                    else:
                        status.append(f"✅ {button_name}: Ready")

            if status:
                status_text = "\n".join(status)
                header = f"Button Status Summary:\n"
                header += f"⚡ Instant buttons: {instant_count}\n"
                header += f"⏳ Regular buttons: {regular_count}\n"
                header += f"📊 Cooldown time: {self.COOLDOWN_TIME}s\n\n"
                header += "Detailed Status:\n" + "="*30 + "\n\n"
                
                messagebox.showinfo("Button Status", header + status_text)
            else:
                messagebox.showinfo("Button Status", "No buttons with cooldown tracking found")

        except Exception as e:
            print(f"❌ Error getting button status: {e}")
            messagebox.showerror("Error", f"Failed to get button status:\n{str(e)}")

    # ===============================
    # ESP32 INTEGRATION METHODS
    # ===============================
    
    def connect_esp32(self):
        """Connect to ESP32"""
        try:
            if not ESP32_AVAILABLE or not self.esp32_client:
                messagebox.showerror("Error", "ESP32 services not available")
                return
            
            # Load config if available
            config_data = None
            if self.esp32_config:
                config_data = self.esp32_config.load_config()
            
            if config_data:
                # config_data is an ESP32Config object, access attributes directly
                host = config_data.host
                port = config_data.port
            else:
                host = '192.168.1.100'
                port = 80
            
            # Update ESP32 client configuration and connect
            self.esp32_client.host = host
            self.esp32_client.port = port
            success = self.esp32_client.connect()
            
            if success:
                self.esp32_connected = True
                self.esp32_status_label.config(text="🟢 Connected", fg='#4CAF50')
                self.connect_btn.config(state="disabled")
                self.disconnect_btn.config(state="normal")
                print(f"✅ Connected to ESP32 at {host}:{port}")
            else:
                messagebox.showerror("Connection Error", f"Failed to connect to ESP32 at {host}:{port}")
                
        except Exception as e:
            print(f"❌ Error connecting to ESP32: {e}")
            messagebox.showerror("Error", f"Error connecting to ESP32: {e}")
    
    def disconnect_esp32(self):
        """Disconnect from ESP32"""
        try:
            if self.esp32_client:
                self.esp32_client.disconnect()
            
            self.esp32_connected = False
            self.esp32_status_label.config(text="🔴 Disconnected", fg='#f44336')
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            print("✅ Disconnected from ESP32")
            
        except Exception as e:
            print(f"❌ Error disconnecting from ESP32: {e}")
    
    def test_esp32_connection(self):
        """Test ESP32 connection"""
        try:
            if not self.esp32_connected:
                messagebox.showwarning("Warning", "Not connected to ESP32")
                return
            
            if self.debug_mode:
                # Simulate test in debug mode
                print(f"🐛 [DEBUG] ESP32 Connection Test: Simulating successful test")
                messagebox.showinfo("Debug Test", "ESP32 connection test successful! (Debug Mode)")
                return
            
            # Send a test command
            response = self.esp32_client.send_movement(0, 0, 0, 0, 0, 0, 0)
            
            if response:
                messagebox.showinfo("Success", "ESP32 connection test successful!")
            else:
                messagebox.showerror("Error", "ESP32 connection test failed")
                
        except Exception as e:
            print(f"❌ Error testing ESP32 connection: {e}")
            messagebox.showerror("Error", f"Error testing connection: {e}")
    
    def toggle_debug_mode(self):
        """Toggle debug mode to simulate ESP32 connection"""
        try:
            if self.debug_mode:
                # Disable debug mode
                self.debug_mode = False
                self.debug_btn.config(text="🐛 Debug Mode", bg='#FF9800')
                self.esp32_status_label.config(text="🔴 Disconnected", fg='#f44336')
                self.esp32_connected = False
                self.connect_btn.config(state="normal")
                self.disconnect_btn.config(state="disabled")
                print("🔴 Debug mode disabled - ESP32 simulation turned off")
                messagebox.showinfo("Debug Mode", "Debug mode disabled. ESP32 simulation turned off.")
            else:
                # Enable debug mode
                self.debug_mode = True
                self.debug_btn.config(text="🐛 Debug Active", bg='#4CAF50')
                self.esp32_status_label.config(text="🟢 Debug Connected", fg='#4CAF50')
                self.esp32_connected = True
                self.connect_btn.config(state="disabled")
                self.disconnect_btn.config(state="normal")
                print("🟢 Debug mode enabled - ESP32 simulation active")
                messagebox.showinfo("Debug Mode", "Debug mode enabled! ESP32 simulation is now active.\n\nAll ESP32 commands will be simulated and logged to console.")
                
        except Exception as e:
            print(f"❌ Error toggling debug mode: {e}")
            messagebox.showerror("Error", f"Error toggling debug mode: {e}")
    
    def on_arm_change(self, arm_part, value):
        """Handle arm control changes"""
        try:
            print(f"💪 [ARM] on_arm_change called: {arm_part} = {value}")

            # Get current arm positions
            bi = self.left_brazo_var.get()
            fi = self.left_frente_var.get()
            hi = self.left_high_var.get()
            pi = self.left_pollo_var.get() if hasattr(self, 'left_pollo_var') else 90
            bd = self.right_brazo_var.get()
            fd = self.right_frente_var.get()
            hd = self.right_high_var.get()
            pd = self.right_pollo_var.get()

            print(f"💪 [ARM] Current positions: BI={bi}, FI={fi}, HI={hi}, PI={pi}, BD={bd}, FD={fd}, HD={hd}, PD={pd}")

            # Send movement command to ESP32 (only if connected)
            if self.esp32_connected and self.esp32_client and not self.debug_mode:
                self.esp32_client.send_movement(bi, bd, fi, fd, hi, hd, pd, pi)

            # Log command in debug mode
            if self.debug_mode:
                print(f"🐛 [DEBUG] ESP32 Movement Command: bi={bi}, bd={bd}, fi={fi}, fd={fd}, hi={hi}, hd={hd}, pd={pd}, pi={pi}")

            # If recording, add to current movement (always update when recording)
            if self.is_recording:
                print(f"💪 [ARM] Recording is active, calling update_current_movement")
                self.update_current_movement()
                print(f"📝 [RECORDING] Arm position captured: BI={bi}, FI={fi}, HI={hi}, PI={pi}, BD={bd}, FD={fd}, HD={hd}, PD={pd}")
            else:
                print(f"💪 [ARM] Not recording, skipping update")

            # Update simulator if enabled
            if hasattr(self, 'sim_enabled_var') and self.sim_enabled_var.get():
                if hasattr(self, 'realtime_update_var') and self.realtime_update_var.get():
                    self.update_simulator_visualization()

        except Exception as e:
            print(f"❌ Error handling arm change: {e}")
    
    def on_neck_change(self, neck_part, value):
        """Handle neck control changes"""
        try:
            print(f"🦴 [NECK] on_neck_change called: {neck_part} = {value}")
            
            # Get current neck positions
            lateral = self.cuello_lateral_var.get()
            inferior = self.cuello_inferior_var.get()
            superior = self.cuello_superior_var.get()
            
            print(f"🦴 [NECK] Current positions: L={lateral}, I={inferior}, S={superior}")
            
            # Send neck movement command to ESP32 (only if connected)
            if self.esp32_connected and self.esp32_client and not self.debug_mode:
                self.esp32_client.send_neck_movement(lateral, inferior, superior)
            
            # Log command in debug mode
            if self.debug_mode:
                print(f"🐛 [DEBUG] ESP32 Neck Command: lateral={lateral}, inferior={inferior}, superior={superior}")
            
            # If recording, add to current movement (always update when recording)
            if self.is_recording:
                print(f"🦴 [NECK] Recording is active, calling update_current_movement")
                self.update_current_movement()
                print(f"📝 [RECORDING] Neck position captured: L={lateral}, I={inferior}, S={superior}")
            else:
                print(f"🦴 [NECK] Not recording, skipping update")

            # Update simulator if enabled
            if hasattr(self, 'sim_enabled_var') and self.sim_enabled_var.get():
                if hasattr(self, 'realtime_update_var') and self.realtime_update_var.get():
                    self.update_simulator_position()

        except Exception as e:
            print(f"❌ Error handling neck change: {e}")
    
    def on_finger_change(self, hand, finger, value):
        """Handle finger control changes"""
        try:
            if not self.esp32_connected:
                return

            # Map hand names to ESP32 format (English → Spanish)
            hand_map = {
                'left': 'izquierda',
                'right': 'derecha'
            }

            # Map finger names to ESP32 format
            finger_map = {
                'thumb': 'pulgar',
                'index': 'indice',
                'middle': 'medio',
                'ring': 'anular',
                'pinky': 'menique'
            }

            esp32_hand = hand_map.get(hand, hand)
            esp32_finger = finger_map.get(finger, finger)

            # Send finger command to ESP32
            if self.esp32_client and not self.debug_mode:
                self.esp32_client.send_finger_control(esp32_hand, esp32_finger, int(value))

            # Log command in debug mode
            if self.debug_mode:
                print(f"🐛 [DEBUG] ESP32 Finger Command: hand={esp32_hand}, finger={esp32_finger}, angle={value}")

            # If recording, add to current movement (usar formato español para grabación)
            if self.is_recording:
                self.add_action_to_sequence("MANO", {
                    "M": esp32_hand,
                    "DEDO": esp32_finger,
                    "ANG": int(value)
                }, f"{esp32_hand} {esp32_finger} finger")

            # Update simulator if enabled (for visual feedback)
            if hasattr(self, 'sim_enabled_var') and self.sim_enabled_var.get():
                if hasattr(self, 'realtime_update_var') and self.realtime_update_var.get():
                    self.update_simulator_visualization()

        except Exception as e:
            print(f"❌ Error handling finger change: {e}")
    
    def on_wrist_change(self, hand, value):
        """Handle wrist control changes"""
        try:
            if not self.esp32_connected:
                return

            # Map hand names to ESP32 format (English → Spanish)
            hand_map = {
                'left': 'izquierda',
                'right': 'derecha'
            }

            esp32_hand = hand_map.get(hand, hand)

            # Send wrist command to ESP32
            if self.esp32_client and not self.debug_mode:
                self.esp32_client.send_wrist_control(esp32_hand, int(value))

            # Log command in debug mode
            if self.debug_mode:
                print(f"🐛 [DEBUG] ESP32 Wrist Command: hand={esp32_hand}, angle={value}")

            # If recording, add to current movement with correct command format
            if self.is_recording:
                # Use MUNECA command for wrist movements (compatible with ESP32)
                self.add_action_to_sequence("MUNECA", {
                    "mano": esp32_hand,
                    "angulo": int(value)
                }, f"{esp32_hand} wrist to {value}°")

            # Update simulator if enabled (for visual feedback)
            if hasattr(self, 'sim_enabled_var') and self.sim_enabled_var.get():
                if hasattr(self, 'realtime_update_var') and self.realtime_update_var.get():
                    self.update_simulator_visualization()

        except Exception as e:
            print(f"❌ Error handling wrist change: {e}")

    def update_control_mode(self):
        """Update the control interface based on selected mode"""
        try:
            # Clear existing controls
            for widget in self.controls_container.winfo_children():
                widget.destroy()

            if self.control_mode.get() == "sliders":
                self.create_slider_controls()
            else:
                self.create_arrow_controls()

        except Exception as e:
            print(f"❌ Error updating control mode: {e}")

    def create_slider_controls(self):
        """Create slider-based controls"""
        try:
            # Arms control section
            arms_frame = tk.LabelFrame(self.controls_container, text="💪 Arms Control",
                                 font=('Arial', 12, 'bold'),
                                 bg='#3d3d3d', fg='#ffffff')
            arms_frame.pack(fill="x", pady=(0, 10))

            arms_content = tk.Frame(arms_frame, bg='#3d3d3d')
            arms_content.pack(fill="x", padx=10, pady=10)

            # Left arm controls
            left_arm_frame = tk.LabelFrame(arms_content, text="Left Arm",
                                     font=('Arial', 10, 'bold'),
                                     bg='#4d4d4d', fg='#ffffff')
            left_arm_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
            # Initialize variables if not exist
            if not hasattr(self, 'left_brazo_var'):
                self.left_brazo_var = tk.IntVar(value=100)
                self.left_frente_var = tk.IntVar(value=95)
                self.left_high_var = tk.IntVar(value=140)
                self.left_pollo_var = tk.IntVar(value=90)
                self.right_brazo_var = tk.IntVar(value=30)
                self.right_frente_var = tk.IntVar(value=160)
                self.right_high_var = tk.IntVar(value=165)
                self.right_pollo_var = tk.IntVar(value=100)
                # Variables de cuello
                self.cuello_lateral_var = tk.IntVar(value=155)
                self.cuello_inferior_var = tk.IntVar(value=95)
                self.cuello_superior_var = tk.IntVar(value=110)

            tk.Label(left_arm_frame, text="Pollo Izq (M5):", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_pollo_scale = tk.Scale(left_arm_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.left_pollo_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_arm_change('left_pollo', v))
            left_pollo_scale.pack(fill="x", pady=(0, 5))

            tk.Label(left_arm_frame, text="Frente Izq (M6):", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_frente_scale = tk.Scale(left_arm_frame, from_=0, to=180, orient="horizontal",
                                        variable=self.left_frente_var, bg='#4d4d4d', fg='#ffffff',
                                        highlightthickness=0, command=lambda v: self.on_arm_change('left_frente', v))
            left_frente_scale.pack(fill="x", pady=(0, 5))

            tk.Label(left_arm_frame, text="Brazo Izq (M7):", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_brazo_scale = tk.Scale(left_arm_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.left_brazo_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_arm_change('left_brazo', v))
            left_brazo_scale.pack(fill="x", pady=(0, 5))

            tk.Label(left_arm_frame, text="High Izq (M8):", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_high_scale = tk.Scale(left_arm_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.left_high_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_arm_change('left_high', v))
            left_high_scale.pack(fill="x", pady=(0, 5))

            # Right arm controls
            right_arm_frame = tk.LabelFrame(arms_content, text="Right Arm",
                                        font=('Arial', 10, 'bold'),
                                        bg='#4d4d4d', fg='#ffffff')
            right_arm_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

            tk.Label(right_arm_frame, text="Pollo Der (M1):", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_pollo_scale = tk.Scale(right_arm_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.right_pollo_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_arm_change('right_pollo', v))
            right_pollo_scale.pack(fill="x", pady=(0, 5))

            tk.Label(right_arm_frame, text="Frente Der (M2):", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_frente_scale = tk.Scale(right_arm_frame, from_=0, to=180, orient="horizontal",
                                        variable=self.right_frente_var, bg='#4d4d4d', fg='#ffffff',
                                        highlightthickness=0, command=lambda v: self.on_arm_change('right_frente', v))
            right_frente_scale.pack(fill="x", pady=(0, 5))

            tk.Label(right_arm_frame, text="Brazo Der (M3):", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_brazo_scale = tk.Scale(right_arm_frame, from_=0, to=180, orient="horizontal",
                                        variable=self.right_brazo_var, bg='#4d4d4d', fg='#ffffff',
                                        highlightthickness=0, command=lambda v: self.on_arm_change('right_brazo', v))
            right_brazo_scale.pack(fill="x", pady=(0, 5))

            tk.Label(right_arm_frame, text="High Der (M4):", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_high_scale = tk.Scale(right_arm_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.right_high_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_arm_change('right_high', v))
            right_high_scale.pack(fill="x", pady=(0, 5))
            
        # Neck Control Section
            neck_frame = tk.LabelFrame(self.controls_container, text="🦴 Neck Control",
                                  font=('Arial', 12, 'bold'),
                                  bg='#3d3d3d', fg='#ffffff')
            neck_frame.pack(fill="x", pady=(0, 10))
            
            neck_content = tk.Frame(neck_frame, bg='#3d3d3d')
            neck_content.pack(fill="x", padx=10, pady=10)
            
            # Neck controls
            tk.Label(neck_content, text="Lateral:", bg='#3d3d3d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            cuello_lateral_scale = tk.Scale(neck_content, from_=0, to=180, orient="horizontal",
                                          variable=self.cuello_lateral_var, bg='#3d3d3d', fg='#ffffff',
                                          highlightthickness=0, command=lambda v: self.on_neck_change('lateral', v))
            cuello_lateral_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(neck_content, text="Inferior:", bg='#3d3d3d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            cuello_inferior_scale = tk.Scale(neck_content, from_=0, to=180, orient="horizontal",
                                           variable=self.cuello_inferior_var, bg='#3d3d3d', fg='#ffffff',
                                           highlightthickness=0, command=lambda v: self.on_neck_change('inferior', v))
            cuello_inferior_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(neck_content, text="Superior:", bg='#3d3d3d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            cuello_superior_scale = tk.Scale(neck_content, from_=0, to=180, orient="horizontal",
                                           variable=self.cuello_superior_var, bg='#3d3d3d', fg='#ffffff',
                                           highlightthickness=0, command=lambda v: self.on_neck_change('superior', v))
            cuello_superior_scale.pack(fill="x", pady=(0, 5))
            
        # Hands Control Section
            hands_frame = tk.LabelFrame(self.controls_container, text="✋ Hands Control",
                                  font=('Arial', 12, 'bold'),
                                  bg='#3d3d3d', fg='#ffffff')
            hands_frame.pack(fill="x", pady=(0, 10))
            
            hands_content = tk.Frame(hands_frame, bg='#3d3d3d')
            hands_content.pack(fill="x", padx=10, pady=10)

                # Initialize hand variables if not exist
            if not hasattr(self, 'left_thumb_var'):
                    self.initialize_hand_variables()

                # Create slider controls for hands (similar to existing implementation)
                    self.create_hand_slider_controls(hands_content)

                    # Quick Actions section
                    self.create_quick_actions_section()

        except Exception as e:
            print(f"❌ Error creating slider controls: {e}")

    def create_arrow_controls(self):
        """Create arrow-based controls"""
        try:
            # Arms control section
            arms_frame = tk.LabelFrame(self.controls_container, text="💪 Arms Control",
                                     font=('Arial', 12, 'bold'),
                                     bg='#3d3d3d', fg='#ffffff')
            arms_frame.pack(fill="x", pady=(0, 10))

            arms_content = tk.Frame(arms_frame, bg='#3d3d3d')
            arms_content.pack(fill="x", padx=10, pady=10)

            # Initialize variables if not exist
            if not hasattr(self, 'left_brazo_var'):
                self.left_brazo_var = tk.IntVar(value=100)
                self.left_frente_var = tk.IntVar(value=95)
                self.left_high_var = tk.IntVar(value=140)
                self.left_pollo_var = tk.IntVar(value=90)
                self.right_brazo_var = tk.IntVar(value=30)
                self.right_frente_var = tk.IntVar(value=160)
                self.right_high_var = tk.IntVar(value=165)
                self.right_pollo_var = tk.IntVar(value=100)
                # Variables de cuello
                self.cuello_lateral_var = tk.IntVar(value=155)
                self.cuello_inferior_var = tk.IntVar(value=95)
                self.cuello_superior_var = tk.IntVar(value=110)

        # Left arm arrows
            left_arm_frame = tk.LabelFrame(arms_content, text="Left Arm",
                                         font=('Arial', 10, 'bold'),
                                         bg='#4d4d4d', fg='#ffffff')
            left_arm_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

            self.create_arm_arrow_control(left_arm_frame, "Pollo Izq (M5)", self.left_pollo_var, 0, 180, 'left_pollo')
            self.create_arm_arrow_control(left_arm_frame, "Frente Izq (M6)", self.left_frente_var, 0, 180, 'left_frente')
            self.create_arm_arrow_control(left_arm_frame, "Brazo Izq (M7)", self.left_brazo_var, 0, 180, 'left_brazo')
            self.create_arm_arrow_control(left_arm_frame, "High Izq (M8)", self.left_high_var, 0, 180, 'left_high')

            # Right arm arrows
            right_arm_frame = tk.LabelFrame(arms_content, text="Right Arm",
                                          font=('Arial', 10, 'bold'),
                                          bg='#4d4d4d', fg='#ffffff')
            right_arm_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

            self.create_arm_arrow_control(right_arm_frame, "Pollo Der (M1)", self.right_pollo_var, 0, 180, 'right_pollo')
            self.create_arm_arrow_control(right_arm_frame, "Frente Der (M2)", self.right_frente_var, 0, 180, 'right_frente')
            self.create_arm_arrow_control(right_arm_frame, "Brazo Der (M3)", self.right_brazo_var, 0, 180, 'right_brazo')
            self.create_arm_arrow_control(right_arm_frame, "High Der (M4)", self.right_high_var, 0, 180, 'right_high')

        # Neck Control Section
            neck_frame = tk.LabelFrame(self.controls_container, text="🦴 Neck Control",
                                  font=('Arial', 12, 'bold'),
                                  bg='#3d3d3d', fg='#ffffff')
            neck_frame.pack(fill="x", pady=(0, 10))
            
            neck_content = tk.Frame(neck_frame, bg='#3d3d3d')
            neck_content.pack(fill="x", padx=10, pady=10)
            
            # Neck arrow controls
            self.create_neck_arrow_control(neck_content, "Lateral", self.cuello_lateral_var, 0, 180, 'lateral')
            self.create_neck_arrow_control(neck_content, "Inferior", self.cuello_inferior_var, 0, 180, 'inferior')
            self.create_neck_arrow_control(neck_content, "Superior", self.cuello_superior_var, 0, 180, 'superior')

            # Hands Control Section
            hands_frame = tk.LabelFrame(self.controls_container, text="✋ Hands Control",
                                      font=('Arial', 12, 'bold'),
                                      bg='#3d3d3d', fg='#ffffff')
            hands_frame.pack(fill="x", pady=(0, 10))

            hands_content = tk.Frame(hands_frame, bg='#3d3d3d')
            hands_content.pack(fill="x", padx=10, pady=10)

            # Initialize hand variables if not exist
            if not hasattr(self, 'left_thumb_var'):
                self.initialize_hand_variables()

            # Create arrow controls for hands
            self.create_hand_arrow_controls(hands_content)

            # Quick Actions section
            self.create_quick_actions_section()

        except Exception as e:
            print(f"❌ Error creating arrow controls: {e}")

    def initialize_hand_variables(self):
        """Initialize hand control variables"""
        self.left_thumb_var = tk.IntVar(value=90)
        self.left_index_var = tk.IntVar(value=90)
        self.left_middle_var = tk.IntVar(value=90)
        self.left_ring_var = tk.IntVar(value=90)
        self.left_pinky_var = tk.IntVar(value=90)
        self.left_wrist_var = tk.IntVar(value=80)

        self.right_thumb_var = tk.IntVar(value=90)
        self.right_index_var = tk.IntVar(value=90)
        self.right_middle_var = tk.IntVar(value=90)
        self.right_ring_var = tk.IntVar(value=90)
        self.right_pinky_var = tk.IntVar(value=90)
        self.right_wrist_var = tk.IntVar(value=80)

    def create_arm_arrow_control(self, parent, label, variable, min_val, max_val, arm_type):
        """Create arrow control for arm joints"""
        control_frame = tk.Frame(parent, bg='#4d4d4d')
        control_frame.pack(fill="x", pady=2)

        # Label and current value
        label_frame = tk.Frame(control_frame, bg='#4d4d4d')
        label_frame.pack(fill="x")

        tk.Label(label_frame, text=f"{label}:", bg='#4d4d4d', fg='#ffffff',
            font=('Arial', 8)).pack(side="left")

        value_label = tk.Label(label_frame, textvariable=variable, bg='#4d4d4d', fg='#00ff00',
                          font=('Arial', 8, 'bold'))
        value_label.pack(side="right")

        # Arrow buttons
        arrows_frame = tk.Frame(control_frame, bg='#4d4d4d')
        arrows_frame.pack(fill="x")

        step = 5 if arm_type in ['left_brazo', 'right_brazo', 'left_high', 'right_high', 'left_pollo', 'right_pollo'] else 10

        decrease_btn = tk.Button(arrows_frame, text="⬅️", bg='#dc3545', fg='#ffffff',
                                font=('Arial', 10, 'bold'), width=3,
                                command=lambda: self.adjust_arm_value(variable, -step, min_val, max_val, arm_type))
        decrease_btn.pack(side="left", padx=2)

        increase_btn = tk.Button(arrows_frame, text="➡️", bg='#28a745', fg='#ffffff',
                                font=('Arial', 10, 'bold'), width=3,
                                command=lambda: self.adjust_arm_value(variable, step, min_val, max_val, arm_type))
        increase_btn.pack(side="right", padx=2)

    def create_neck_arrow_control(self, parent, label, variable, min_val, max_val, neck_type):
        """Create arrow control for neck joints"""
        control_frame = tk.Frame(parent, bg='#3d3d3d')
        control_frame.pack(fill="x", pady=2)

        # Label and current value
        label_frame = tk.Frame(control_frame, bg='#3d3d3d')
        label_frame.pack(fill="x")

        tk.Label(label_frame, text=f"{label}:", bg='#3d3d3d', fg='#ffffff',
            font=('Arial', 8)).pack(side="left")

        value_label = tk.Label(label_frame, textvariable=variable, bg='#3d3d3d', fg='#00ff00',
                          font=('Arial', 8, 'bold'))
        value_label.pack(side="right")

        # Arrow buttons
        arrows_frame = tk.Frame(control_frame, bg='#3d3d3d')
        arrows_frame.pack(fill="x")

        step = 5  # Step size for neck movements

        decrease_btn = tk.Button(arrows_frame, text="⬅️", bg='#dc3545', fg='#ffffff',
                                font=('Arial', 10, 'bold'), width=3,
                                command=lambda: self.adjust_neck_value(variable, -step, min_val, max_val, neck_type))
        decrease_btn.pack(side="left", padx=2)

        increase_btn = tk.Button(arrows_frame, text="➡️", bg='#28a745', fg='#ffffff',
                                font=('Arial', 10, 'bold'), width=3,
                                command=lambda: self.adjust_neck_value(variable, step, min_val, max_val, neck_type))
        increase_btn.pack(side="right", padx=2)

    def create_hand_slider_controls(self, parent):
            """Create slider controls for hands with gesture buttons"""
            # Gesture buttons (always visible)
            gesture_frame = tk.Frame(parent, bg='#3d3d3d')
            gesture_frame.pack(fill="x", pady=(0, 10))

            tk.Label(gesture_frame, text="🤚 Hand Gestures:", bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))

            gesture_buttons = tk.Frame(gesture_frame, bg='#3d3d3d')
            gesture_buttons.pack(fill="x")

            # Initialize variables if not exist
            if not hasattr(self, 'mano_var'):
                self.mano_var = tk.StringVar(value="derecha")

            tk.Label(gesture_buttons, text="Hand:", bg='#3d3d3d', fg='#ffffff').pack(side="left")
            mano_menu = tk.OptionMenu(gesture_buttons, self.mano_var, "derecha", "izquierda", "ambas")
            mano_menu.config(bg='#4d4d4d', fg='#ffffff', highlightthickness=0)
            mano_menu.pack(side="left", padx=(5, 10))

            tk.Button(gesture_buttons, text="✋ Open", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'abrir')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="✊ Close", bg='#f44336', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'cerrar')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="✌️ Peace", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'paz')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="🤘 Rock", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'rock')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="👌 OK", bg='#9C27B0', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'ok')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="👆 Point", bg='#607D8B', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'senalar')).pack(side="left", padx=2)

            # Individual finger controls
            hands_frame = tk.Frame(parent, bg='#3d3d3d')
            hands_frame.pack(fill="both", expand=True)
        
        # Left Hand Controls
            left_hand_frame = tk.LabelFrame(hands_frame, text="Left Hand - Individual Fingers",
                                      font=('Arial', 10, 'bold'),
                                      bg='#4d4d4d', fg='#ffffff')
            left_hand_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
            # Left hand finger controls
            tk.Label(left_hand_frame, text="Thumb:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_thumb_scale = tk.Scale(left_hand_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.left_thumb_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_finger_change('left', 'thumb', v))
            left_thumb_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(left_hand_frame, text="Index:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_index_scale = tk.Scale(left_hand_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.left_index_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_finger_change('left', 'index', v))
            left_index_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(left_hand_frame, text="Middle:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_middle_scale = tk.Scale(left_hand_frame, from_=0, to=180, orient="horizontal",
                                        variable=self.left_middle_var, bg='#4d4d4d', fg='#ffffff',
                                        highlightthickness=0, command=lambda v: self.on_finger_change('left', 'middle', v))
            left_middle_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(left_hand_frame, text="Ring:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_ring_scale = tk.Scale(left_hand_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.left_ring_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_finger_change('left', 'ring', v))
            left_ring_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(left_hand_frame, text="Pinky:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_pinky_scale = tk.Scale(left_hand_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.left_pinky_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_finger_change('left', 'pinky', v))
            left_pinky_scale.pack(fill="x", pady=(0, 5))
            
            # Left wrist control
            tk.Label(left_hand_frame, text="Wrist:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            left_wrist_scale = tk.Scale(left_hand_frame, from_=0, to=160, orient="horizontal",
                                    variable=self.left_wrist_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_wrist_change('left', v))
            left_wrist_scale.pack(fill="x", pady=(0, 5))
        
        # Right Hand Controls
            right_hand_frame = tk.LabelFrame(parent, text="Right Hand",
                                       font=('Arial', 10, 'bold'),
                                       bg='#4d4d4d', fg='#ffffff')
            right_hand_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
            
            # Right hand finger controls
            tk.Label(right_hand_frame, text="Thumb:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_thumb_scale = tk.Scale(right_hand_frame, from_=0, to=180, orient="horizontal",
                                        variable=self.right_thumb_var, bg='#4d4d4d', fg='#ffffff',
                                        highlightthickness=0, command=lambda v: self.on_finger_change('right', 'thumb', v))
            right_thumb_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(right_hand_frame, text="Index:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_index_scale = tk.Scale(right_hand_frame, from_=0, to=180, orient="horizontal",
                                        variable=self.right_index_var, bg='#4d4d4d', fg='#ffffff',
                                        highlightthickness=0, command=lambda v: self.on_finger_change('right', 'index', v))
            right_index_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(right_hand_frame, text="Middle:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_middle_scale = tk.Scale(right_hand_frame, from_=0, to=180, orient="horizontal",
                                        variable=self.right_middle_var, bg='#4d4d4d', fg='#ffffff',
                                        highlightthickness=0, command=lambda v: self.on_finger_change('right', 'middle', v))
            right_middle_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(right_hand_frame, text="Ring:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_ring_scale = tk.Scale(right_hand_frame, from_=0, to=180, orient="horizontal",
                                    variable=self.right_ring_var, bg='#4d4d4d', fg='#ffffff',
                                    highlightthickness=0, command=lambda v: self.on_finger_change('right', 'ring', v))
            right_ring_scale.pack(fill="x", pady=(0, 5))
            
            tk.Label(right_hand_frame, text="Pinky:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_pinky_scale = tk.Scale(right_hand_frame, from_=0, to=180, orient="horizontal",
                                        variable=self.right_pinky_var, bg='#4d4d4d', fg='#ffffff',
                                        highlightthickness=0, command=lambda v: self.on_finger_change('right', 'pinky', v))
            right_pinky_scale.pack(fill="x", pady=(0, 5))
            
            # Right wrist control
            tk.Label(right_hand_frame, text="Wrist:", bg='#4d4d4d', fg='#ffffff',
                    font=('Arial', 9)).pack(anchor="w")
            right_wrist_scale = tk.Scale(right_hand_frame, from_=0, to=180, orient="horizontal",
                                        variable=self.right_wrist_var, bg='#4d4d4d', fg='#ffffff',
                                        highlightthickness=0, command=lambda v: self.on_wrist_change('right', v))
            right_wrist_scale.pack(fill="x", pady=(0, 5))
        
    def create_hand_arrow_controls(self, parent):
            """Create arrow controls for hands with gesture buttons"""
            # Gesture buttons (always visible)
            gesture_frame = tk.Frame(parent, bg='#3d3d3d')
            gesture_frame.pack(fill="x", pady=(0, 10))

            tk.Label(gesture_frame, text="🤚 Hand Gestures:", bg='#3d3d3d', fg='#ffffff',
                font=('Arial', 10, 'bold')).pack(anchor="w", pady=(0, 5))

            gesture_buttons = tk.Frame(gesture_frame, bg='#3d3d3d')
            gesture_buttons.pack(fill="x")

            # Initialize variables if not exist
            if not hasattr(self, 'mano_var'):
                self.mano_var = tk.StringVar(value="derecha")

            tk.Label(gesture_buttons, text="Hand:", bg='#3d3d3d', fg='#ffffff').pack(side="left")
            mano_menu = tk.OptionMenu(gesture_buttons, self.mano_var, "derecha", "izquierda", "ambas")
            mano_menu.config(bg='#4d4d4d', fg='#ffffff', highlightthickness=0)
            mano_menu.pack(side="left", padx=(5, 10))

            tk.Button(gesture_buttons, text="✋ Open", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'abrir')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="✊ Close", bg='#f44336', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'cerrar')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="✌️ Peace", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'paz')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="🤘 Rock", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'rock')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="👌 OK", bg='#9C27B0', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'ok')).pack(side="left", padx=2)

            tk.Button(gesture_buttons, text="👆 Point", bg='#607D8B', fg='#ffffff',
                 font=('Arial', 9, 'bold'), command=lambda: self.hand_gesture(self.mano_var.get(), 'senalar')).pack(side="left", padx=2)

            # Individual finger controls
            hands_frame = tk.Frame(parent, bg='#3d3d3d')
            hands_frame.pack(fill="both", expand=True)

            # Left Hand Controls
            left_hand_frame = tk.LabelFrame(hands_frame, text="Left Hand - Individual Fingers",
                                      font=('Arial', 10, 'bold'),
                                      bg='#4d4d4d', fg='#ffffff')
            left_hand_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

            self.create_finger_arrow_control(left_hand_frame, "Thumb", self.left_thumb_var, 'left', 'thumb')
            self.create_finger_arrow_control(left_hand_frame, "Index", self.left_index_var, 'left', 'index')
            self.create_finger_arrow_control(left_hand_frame, "Middle", self.left_middle_var, 'left', 'middle')
            self.create_finger_arrow_control(left_hand_frame, "Ring", self.left_ring_var, 'left', 'ring')
            self.create_finger_arrow_control(left_hand_frame, "Pinky", self.left_pinky_var, 'left', 'pinky')
            self.create_wrist_arrow_control(left_hand_frame, "Wrist", self.left_wrist_var, 'left')

            # Right Hand Controls
            right_hand_frame = tk.LabelFrame(hands_frame, text="Right Hand - Individual Fingers",
                                       font=('Arial', 10, 'bold'),
                                       bg='#4d4d4d', fg='#ffffff')
            right_hand_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

            self.create_finger_arrow_control(right_hand_frame, "Thumb", self.right_thumb_var, 'right', 'thumb')
            self.create_finger_arrow_control(right_hand_frame, "Index", self.right_index_var, 'right', 'index')
            self.create_finger_arrow_control(right_hand_frame, "Middle", self.right_middle_var, 'right', 'middle')
            self.create_finger_arrow_control(right_hand_frame, "Ring", self.right_ring_var, 'right', 'ring')
            self.create_finger_arrow_control(right_hand_frame, "Pinky", self.right_pinky_var, 'right', 'pinky')
            self.create_wrist_arrow_control(right_hand_frame, "Wrist", self.right_wrist_var, 'right')

    def create_finger_arrow_control(self, parent, label, variable, hand, finger):
            """Create arrow control for fingers"""
            control_frame = tk.Frame(parent, bg='#4d4d4d')
            control_frame.pack(fill="x", pady=1)

            # Label and current value
            label_frame = tk.Frame(control_frame, bg='#4d4d4d')
            label_frame.pack(fill="x")

            tk.Label(label_frame, text=f"{label}:", bg='#4d4d4d', fg='#ffffff',
                font=('Arial', 7)).pack(side="left")

            value_label = tk.Label(label_frame, textvariable=variable, bg='#4d4d4d', fg='#00ff00',
                              font=('Arial', 7, 'bold'))
            value_label.pack(side="right")

            # Arrow buttons
            arrows_frame = tk.Frame(control_frame, bg='#4d4d4d')
            arrows_frame.pack(fill="x")

            decrease_btn = tk.Button(arrows_frame, text="⬆️", bg='#dc3545', fg='#ffffff',
                                font=('Arial', 8), width=2,
                                command=lambda: self.adjust_finger_value(variable, -10, hand, finger))
            decrease_btn.pack(side="left", padx=1)

            increase_btn = tk.Button(arrows_frame, text="⬇️", bg='#28a745', fg='#ffffff',
                                font=('Arial', 8), width=2,
                                command=lambda: self.adjust_finger_value(variable, 10, hand, finger))
            increase_btn.pack(side="right", padx=1)

    def create_wrist_arrow_control(self, parent, label, variable, hand):
            """Create arrow control for wrist"""
            control_frame = tk.Frame(parent, bg='#4d4d4d')
            control_frame.pack(fill="x", pady=1)

            # Label and current value
            label_frame = tk.Frame(control_frame, bg='#4d4d4d')
            label_frame.pack(fill="x")

            tk.Label(label_frame, text=f"{label}:", bg='#4d4d4d', fg='#ffffff',
                font=('Arial', 7)).pack(side="left")

            value_label = tk.Label(label_frame, textvariable=variable, bg='#4d4d4d', fg='#00ff00',
                              font=('Arial', 7, 'bold'))
            value_label.pack(side="right")

            # Arrow buttons
            arrows_frame = tk.Frame(control_frame, bg='#4d4d4d')
            arrows_frame.pack(fill="x")

            decrease_btn = tk.Button(arrows_frame, text="⬅️", bg='#dc3545', fg='#ffffff',
                                font=('Arial', 8), width=2,
                                command=lambda: self.adjust_wrist_value(variable, -20, hand))
            decrease_btn.pack(side="left", padx=1)

            increase_btn = tk.Button(arrows_frame, text="➡️", bg='#28a745', fg='#ffffff',
                                font=('Arial', 8), width=2,
                                command=lambda: self.adjust_wrist_value(variable, 20, hand))
            increase_btn.pack(side="right", padx=1)

    def adjust_arm_value(self, variable, delta, min_val, max_val, arm_type):
            """Adjust arm joint value and trigger command"""
            current = variable.get()
            new_value = max(min_val, min(max_val, current + delta))
            variable.set(new_value)
            self.on_arm_change(arm_type, new_value)

    def adjust_neck_value(self, variable, delta, min_val, max_val, neck_type):
            """Adjust neck joint value and trigger command"""
            current = variable.get()
            new_value = max(min_val, min(max_val, current + delta))
            variable.set(new_value)
            self.on_neck_change(neck_type, new_value)

    def adjust_finger_value(self, variable, delta, hand, finger):
            """Adjust finger value and trigger command"""
            current = variable.get()
            new_value = max(0, min(180, current + delta))
            variable.set(new_value)
            self.on_finger_change(hand, finger, new_value)

    def adjust_wrist_value(self, variable, delta, hand):
            """Adjust wrist value and trigger command"""
            current = variable.get()
            new_value = max(0, min(180, current + delta))
            variable.set(new_value)
            self.on_wrist_change(hand, new_value)

    def create_quick_actions_section(self):
            """Create quick actions section with gesture buttons"""
            try:
                quick_actions_frame = tk.LabelFrame(self.controls_container, text="⚡ Quick Actions",
                                               font=('Arial', 12, 'bold'),
                                               bg='#3d3d3d', fg='#ffffff')
                quick_actions_frame.pack(fill="x", pady=(0, 10))

                actions_content = tk.Frame(quick_actions_frame, bg='#3d3d3d')
                actions_content.pack(fill="x", padx=10, pady=10)

                # Row 1: System actions
                system_row = tk.Frame(actions_content, bg='#3d3d3d')
                system_row.pack(fill="x", pady=(0, 10))

                # Home Position Button
                home_btn = tk.Button(system_row, text="🏠 Rest Position", bg='#2196F3', fg='#ffffff',
                                font=('Arial', 10, 'bold'),
                                command=lambda: self.debounce_button("home_position", self.home_position))
                home_btn.pack(side="left", padx=(0, 5))
                self.store_button_reference("home_position", home_btn)

                # Wave Button
                wave_btn = tk.Button(system_row, text="👋 Wave", bg='#FF9800', fg='#ffffff',
                                font=('Arial', 10, 'bold'),
                                command=lambda: self.debounce_button("wave_gesture", self.wave_gesture))
                wave_btn.pack(side="left", padx=5)
                self.store_button_reference("wave_gesture", wave_btn)

                # Hug Button
                hug_btn = tk.Button(system_row, text="🤗 Hug", bg='#9C27B0', fg='#ffffff',
                                font=('Arial', 10, 'bold'),
                                command=lambda: self.debounce_button("hug_gesture", self.hug_gesture))
                hug_btn.pack(side="left", padx=5)
                self.store_button_reference("hug_gesture", hug_btn)

                # Look Around Button
                look_btn = tk.Button(system_row, text="👀 Look Around", bg='#607D8B', fg='#ffffff',
                                font=('Arial', 10, 'bold'),
                                command=lambda: self.debounce_button("look_around", self.look_around))
                look_btn.pack(side="left", padx=5)
                self.store_button_reference("look_around", look_btn)

                # Row 2: Arm gestures
                arm_row = tk.Frame(actions_content, bg='#3d3d3d')
                arm_row.pack(fill="x", pady=(0, 10))

                tk.Label(arm_row, text="🤖 Arm Actions:", bg='#3d3d3d', fg='#ffffff',
                        font=('Arial', 10, 'bold')).pack(side="left", padx=(0, 10))

                # Arm Rest Position Button
                arm_rest_btn = tk.Button(arm_row, text="🛌 Rest Position", bg='#4CAF50', fg='#ffffff',
                                    font=('Arial', 9, 'bold'),
                                    command=lambda: self.debounce_button("arm_rest_position", self.arm_rest_position))
                arm_rest_btn.pack(side="left", padx=(0, 5))
                self.store_button_reference("arm_rest_position", arm_rest_btn)

                # Arm Up Button
                arm_up_btn = tk.Button(arm_row, text="💪 Arm Up", bg='#FF5722', fg='#ffffff',
                                    font=('Arial', 9, 'bold'),
                                    command=lambda: self.debounce_button("arm_up", self.arm_up))
                arm_up_btn.pack(side="left", padx=5)
                self.store_button_reference("arm_up", arm_up_btn)

                # Arms Open Button
                arms_open_btn = tk.Button(arm_row, text="🙌 Arms Open", bg='#3F51B5', fg='#ffffff',
                                        font=('Arial', 9, 'bold'),
                                        command=lambda: self.debounce_button("arms_open", self.arms_open))
                arms_open_btn.pack(side="left", padx=5)
                self.store_button_reference("arms_open", arms_open_btn)

                # Row 3: Speech
                speech_row = tk.Frame(actions_content, bg='#3d3d3d')
                speech_row.pack(fill="x")

                tk.Label(speech_row, text="🗣️ Speech:", bg='#3d3d3d', fg='#ffffff',
                        font=('Arial', 9, 'bold')).pack(side="left", padx=(0, 5))

                # Initialize speech variable if not exist
                if not hasattr(self, 'speech_text_var'):
                    self.speech_text_var = tk.StringVar(value="Hello students!")

                speech_entry = tk.Entry(speech_row, textvariable=self.speech_text_var,
                                    bg='#4d4d4d', fg='#ffffff', font=('Arial', 9), width=20)
                speech_entry.pack(side="left", padx=(0, 5))

                # Speak Button
                speak_btn = tk.Button(speech_row, text="🗣️ Speak", bg='#4CAF50', fg='#ffffff',
                                    font=('Arial', 9, 'bold'),
                                    command=lambda: self.debounce_button("speak_text", self.speak_text))
                speak_btn.pack(side="left")
                self.store_button_reference("speak_text", speak_btn)

                # Utility buttons row
                utility_row = tk.Frame(actions_content, bg='#3d3d3d')
                utility_row.pack(fill="x", pady=(10, 0))

                tk.Label(utility_row, text="🔧 Utilities:", bg='#3d3d3d', fg='#ffffff',
                        font=('Arial', 9, 'bold')).pack(side="left", padx=(0, 10))

                # Reset Cooldowns Button
                reset_btn = tk.Button(utility_row, text="🔄 Reset Cooldowns", bg='#607D8B', fg='#ffffff',
                                    font=('Arial', 8, 'bold'),
                                    command=self.reset_button_cooldowns)
                reset_btn.pack(side="left", padx=(0, 5))

                # Button Status Button
                status_btn = tk.Button(utility_row, text="📊 Button Status", bg='#9C27B0', fg='#ffffff',
                                    font=('Arial', 8, 'bold'),
                                    command=self.get_button_status)
                status_btn.pack(side="left", padx=(0, 5))
                
                # Configure Instant Buttons Button
                config_btn = tk.Button(utility_row, text="⚡ Configure Instant", bg='#FF5722', fg='#ffffff',
                                     font=('Arial', 8, 'bold'),
                                     command=self.configure_instant_buttons)
                config_btn.pack(side="left", padx=(0, 5))
                
            except Exception as e:
                print(f"❌ Error creating quick actions section: {e}")

    def arm_rest_position(self):
            """Send arm rest position command"""
            try:
                if self.esp32_client and not self.debug_mode:
                    # Call ESP32 endpoint for rest position
                    import requests
                    url = f"http://{self.esp32_client.host}:{self.esp32_client.port}/brazos/descanso"
                    response = requests.get(url, timeout=self.esp32_client.timeout)
                    if response.status_code == 200:
                        print("✅ Arm rest position command sent successfully")
                        messagebox.showinfo("Success", "🛌 Arm rest position command sent!")
                    else:
                        print(f"❌ Error sending arm rest position: HTTP {response.status_code}")
                        messagebox.showerror("Error", f"Failed to send arm rest position command\nHTTP {response.status_code}")
                elif self.debug_mode:
                    print("🐛 [DEBUG] Arm rest position command executed")
                    messagebox.showinfo("Debug", "🛌 Arm rest position command (DEBUG MODE)")
            except Exception as e:
                print(f"❌ Error sending arm rest position: {e}")
                messagebox.showerror("Error", f"Failed to send arm rest position:\n{str(e)}")

    def arm_up(self):
            """Send arm up command"""
            try:
                if self.esp32_client and not self.debug_mode:
                        # Send command to move arms up (use saludo endpoint for now)
                        import requests
                        url = f"http://{self.esp32_client.host}:{self.esp32_client.port}/brazos/saludo"
                        response = requests.get(url, timeout=self.esp32_client.timeout)
                        if response.status_code == 200:
                            print("✅ Arm up command sent successfully")
                            messagebox.showinfo("Success", "💪 Arm up command sent!")
                        else:
                            print(f"❌ Error sending arm up: HTTP {response.status_code}")
                            messagebox.showerror("Error", f"Failed to send arm up command\nHTTP {response.status_code}")
                elif self.debug_mode:
                        print("🐛 [DEBUG] Arm up command executed")
                        messagebox.showinfo("Debug", "💪 Arm up command (DEBUG MODE)")
            except Exception as e:
                print(f"❌ Error sending arm up: {e}")
                messagebox.showerror("Error", f"Failed to send arm up:\n{str(e)}")

    def arms_open(self):
            """Send arms open command"""
            try:
                if self.esp32_client and not self.debug_mode:
                    # Send command to open arms (use abrazo endpoint for now)
                    import requests
                    url = f"http://{self.esp32_client.host}:{self.esp32_client.port}/brazos/abrazar"
                    response = requests.get(url, timeout=self.esp32_client.timeout)
                    if response.status_code == 200:
                        print("✅ Arms open command sent successfully")
                        messagebox.showinfo("Success", "🙌 Arms open command sent!")
                    else:
                        print(f"❌ Error sending arms open: HTTP {response.status_code}")
                        messagebox.showerror("Error", f"Failed to send arms open command\nHTTP {response.status_code}")
                elif self.debug_mode:
                    print("🐛 [DEBUG] Arms open command executed")
                    messagebox.showinfo("Debug", "🙌 Arms open command (DEBUG MODE)")
            except Exception as e:
              print(f"❌ Error sending arms open: {e}")
              messagebox.showerror("Error", f"Failed to send arms open:\n{str(e)}")
    
    def home_position(self):
        """Send home position command"""
        try:
            if self.esp32_connected and self.esp32_client and not self.debug_mode:
                    # Use the ESP32 endpoint for rest position
                    import requests
                    url = f"http://{self.esp32_client.host}:{self.esp32_client.port}/system/descanso"
                    response = requests.get(url, timeout=self.esp32_client.timeout)
                    if response.status_code == 200:
                        print("✅ Rest position command sent successfully")
                        messagebox.showinfo("Success", "🏠 Rest position command sent!")
                    else:
                        print(f"❌ Error sending rest position: HTTP {response.status_code}")
                        messagebox.showwarning("Warning", f"ESP32 endpoint failed (HTTP {response.status_code})\nUsing fallback movement command")
                        # Fallback to direct movement command
                        self.esp32_client.send_movement(100, 30, 95, 160, 140, 165, 100, 90)

            # Log command in debug mode
            elif self.debug_mode:
                    print(f"🐛 [DEBUG] ESP32 Rest Position Command executed")
                    messagebox.showinfo("Debug", "🏠 Rest position command (DEBUG MODE)")

            # If recording, add to sequence
            if self.is_recording:
                self.add_action_to_sequence("BRAZOS", {
                    "BI": 100, "BD": 30, "FI": 95, "FD": 160,
                    "HI": 140, "HD": 165, "PD": 100, "PI": 90
                    }, "Rest Position")
                
        except Exception as e:
                print(f"❌ Error sending rest position: {e}")
                messagebox.showerror("Error", f"Failed to send rest position:\n{str(e)}")
    
    def wave_gesture(self):
        """Send wave gesture command"""
        try:
            if self.esp32_connected and self.esp32_client and not self.debug_mode:
                    # Use ESP32 endpoint for wave gesture
                    import requests
                    url = f"http://{self.esp32_client.host}:{self.esp32_client.port}/brazos/saludo"
                    response = requests.get(url, timeout=self.esp32_client.timeout)
                    if response.status_code == 200:
                        print("✅ Wave gesture command sent successfully")
                        messagebox.showinfo("Success", "👋 Wave gesture command sent!")
                    else:
                        print(f"❌ Error sending wave gesture: HTTP {response.status_code}")
                        messagebox.showwarning("Warning", f"ESP32 endpoint failed (HTTP {response.status_code})\nUsing fallback gesture command")
                        # Fallback to client method
                        self.esp32_client.send_gesture("derecha", "SALUDO")
            
            # Log command in debug mode
            elif self.debug_mode:
                    print(f"🐛 [DEBUG] ESP32 Wave Gesture Command executed")
                    messagebox.showinfo("Debug", "👋 Wave gesture command (DEBUG MODE)")
            
            # If recording, add to sequence
            if self.is_recording:
                self.add_action_to_sequence("MANO", {
                    "M": "derecha", "GESTO": "SALUDO"
                }, "Wave Gesture")
                
        except Exception as e:
            print(f"❌ Error sending wave gesture: {e}")
            messagebox.showerror("Error", f"Failed to send wave gesture:\n{str(e)}")
    
    def hug_gesture(self):
        """Send hug gesture command"""
        try:
            if self.esp32_connected and self.esp32_client and not self.debug_mode:
                    # Use ESP32 endpoint for hug gesture
                    import requests
                    url = f"http://{self.esp32_client.host}:{self.esp32_client.port}/brazos/abrazar"
                    response = requests.get(url, timeout=self.esp32_client.timeout)
                    if response.status_code == 200:
                        print("✅ Hug gesture command sent successfully")
                        messagebox.showinfo("Success", "🤗 Hug gesture command sent!")
                    else:
                        print(f"❌ Error sending hug gesture: HTTP {response.status_code}")
                        messagebox.showwarning("Warning", f"ESP32 endpoint failed (HTTP {response.status_code})\nUsing fallback gesture command")
                        # Fallback to client method
                        self.esp32_client.send_gesture("ambas", "ABRAZO")
            
            # Log command in debug mode
            elif self.debug_mode:
                    print(f"🐛 [DEBUG] ESP32 Hug Gesture Command executed")
                    messagebox.showinfo("Debug", "🤗 Hug gesture command (DEBUG MODE)")
            
            # If recording, add to sequence
            if self.is_recording:
                self.add_action_to_sequence("MANO", {
                    "M": "ambas", "GESTO": "ABRAZO"
                }, "Hug Gesture")
                
        except Exception as e:
            print(f"❌ Error sending hug gesture: {e}")
            messagebox.showerror("Error", f"Failed to send hug gesture:\n{str(e)}")
    
    def look_around(self):
        """Send look around command"""
        try:
            if self.esp32_connected and self.esp32_client and not self.debug_mode:
                    # Try ESP32 endpoint for look around (if exists), otherwise use neck movement
                    try:
                        import requests
                        # Use a predefined look around movement
                        url = f"http://{self.esp32_client.host}:{self.esp32_client.port}/cuello/mover"
                        data = {"lateral": 155, "inferior": 95, "superior": 110}
                        response = requests.post(url, data=data, timeout=self.esp32_client.timeout)
                        if response.status_code == 200:
                            print("✅ Look around command sent successfully")
                            messagebox.showinfo("Success", "👀 Look around command sent!")
                        else:
                            print(f"❌ Error sending look around: HTTP {response.status_code}")
                            messagebox.showwarning("Warning", f"ESP32 endpoint failed (HTTP {response.status_code})\nUsing fallback neck movement")
                            # Fallback to client method
                            self.esp32_client.send_neck_movement(155, 95, 110)
                    except Exception as fallback_error:
                        print(f"⚠️ Endpoint not available, using fallback: {fallback_error}")
                        messagebox.showinfo("Info", "Using fallback neck movement command")
                        # Fallback to client method
                        self.esp32_client.send_neck_movement(155, 95, 110)
            
            # Log command in debug mode
            elif self.debug_mode:
                    print(f"🐛 [DEBUG] ESP32 Look Around Command executed")
                    messagebox.showinfo("Debug", "👀 Look around command (DEBUG MODE)")
            
            # If recording, add to sequence
            if self.is_recording:
                self.add_action_to_sequence("CUELLO", {
                    "L": 155, "I": 95, "S": 110
                }, "Look Around")
                
        except Exception as e:
            print(f"❌ Error sending look around: {e}")
            messagebox.showerror("Error", f"Failed to send look around:\n{str(e)}")
    
    def hand_gesture(self, hand, gesture):
        """Send hand gesture command"""
        try:
            if self.esp32_connected and self.esp32_client and not self.debug_mode:
                self.esp32_client.send_gesture(hand, gesture.upper())
            
            # Log command in debug mode
            if self.debug_mode:
                print(f"🐛 [DEBUG] ESP32 Hand Gesture Command: hand={hand}, gesture={gesture.upper()}")
            
            # If recording, add to sequence
            if self.is_recording:
                self.add_action_to_sequence("MANO", {
                    "M": hand, "GESTO": gesture.upper()
                }, f"{hand} {gesture} gesture")
                
        except Exception as e:
            print(f"❌ Error sending hand gesture: {e}")
    
    def speak_text(self):
        """Send speech command"""
        try:
            text = self.speech_text_var.get()
            if not text:
                return
            
            if self.esp32_connected and self.esp32_client and not self.debug_mode:
                    # Try ESP32 speech endpoint if available
                    try:
                        import requests
                        url = f"http://{self.esp32_client.host}:{self.esp32_client.port}/cmd"
                        data = {"cmd": f"HABLAR TEXTO={text}"}
                        response = requests.post(url, data=data, timeout=self.esp32_client.timeout)
                        if response.status_code == 200:
                            print("✅ Speech command sent")
                        else:
                            print(f"❌ Error sending speech: HTTP {response.status_code}")
                            # Fallback to client method
                            self.esp32_client.send_speech(text)
                    except:
                        # Fallback to client method
                        self.esp32_client.send_speech(text)
            
            # Log command in debug mode
            if self.debug_mode:
                print(f"🐛 [DEBUG] ESP32 Speech Command: text='{text}'")
            
            # If recording, add to sequence
            if self.is_recording:
                self.add_action_to_sequence("HABLAR", {
                    "texto": text
                }, f"Speech: {text}")
                
        except Exception as e:
            print(f"❌ Error sending speech: {e}")
    
    # ===============================
    # SEQUENCE RECORDING METHODS
    # ===============================
    
    def setup_sequence_recording_panel(self, parent):
        """Setup sequence recording panel"""
        recording_frame = tk.LabelFrame(parent, text="🎬 Sequence Recording", 
                                      font=('Arial', 14, 'bold'),
                                      bg='#2d2d2d', fg='#ffffff')
        recording_frame.pack(fill="x", pady=(0, 10))
        
        content_frame = tk.Frame(recording_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=10, pady=10)
        
        # Sequence name
        name_frame = tk.Frame(content_frame, bg='#2d2d2d')
        name_frame.pack(fill="x", pady=5)
        tk.Label(name_frame, text="Sequence Name:", bg='#2d2d2d', fg='#ffffff', 
                font=('Arial', 12)).pack(side="left")
        tk.Entry(name_frame, textvariable=self.sequence_name, width=20, 
                bg='#3d3d3d', fg='#ffffff', font=('Arial', 12)).pack(side="left", padx=10)
        
        # Recording controls
        controls_frame = tk.Frame(content_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x", pady=10)
        
        self.record_button = tk.Button(controls_frame, text="🔴 Start Recording", 
                                     bg='#f44336', fg='white', 
                                     font=('Arial', 12, 'bold'), 
                                      command=self.toggle_recording)
        self.record_button.pack(side="left", padx=(0, 10))
        
        self.stop_record_button = tk.Button(controls_frame, text="⏹️ Stop Recording", 
                                          bg='#666666', fg='white', 
                                          font=('Arial', 12, 'bold'), 
                                          command=self.toggle_recording,
                                          state="disabled")
        self.stop_record_button.pack(side="left", padx=10)
        
        # Movement control buttons
        movement_buttons_frame = tk.Frame(controls_frame, bg='#2d2d2d')
        movement_buttons_frame.pack(side="right")
        
        # Save movement button
        self.save_movement_btn = tk.Button(movement_buttons_frame, text="💾 Save Movement", 
                                         bg='#4CAF50', fg='white', 
                                         font=('Arial', 10, 'bold'), 
                                         command=self.save_current_movement,
                                         state="disabled")
        self.save_movement_btn.pack(side="right", padx=(0, 5))
        
        # Delete last movement button
        self.delete_last_movement_btn = tk.Button(movement_buttons_frame, text="🗑️ Delete Last", 
                                                bg='#f44336', fg='white', 
                                                font=('Arial', 10, 'bold'), 
                                                command=self.delete_last_movement,
                                                state="disabled")
        self.delete_last_movement_btn.pack(side="right", padx=(0, 5))
        
        # Capture position button
        tk.Button(movement_buttons_frame, text="📍 Capture Position", 
                 bg='#FF9800', fg='white', 
                 font=('Arial', 10, 'bold'), 
                 command=self.capture_position).pack(side="right")
        
        # Recording status
        self.recording_status = tk.Label(content_frame, text="⭕ Ready to Record", 
                                       bg='#2d2d2d', fg='#FFD700', 
                                       font=('Arial', 11, 'bold'))
        self.recording_status.pack(anchor="w", pady=(10, 0))
    
    def setup_sequence_playback_panel(self, parent):
        """Setup sequence playback panel"""
        playback_frame = tk.LabelFrame(parent, text="▶️ Playback Controls", 
                                         font=('Arial', 14, 'bold'),
                                         bg='#2d2d2d', fg='#ffffff')
        playback_frame.pack(fill="x", pady=(0, 10))
            
        content_frame = tk.Frame(playback_frame, bg='#2d2d2d')
        content_frame.pack(fill="x", padx=10, pady=10)
            
            # Playback controls
        controls_frame = tk.Frame(content_frame, bg='#2d2d2d')
        controls_frame.pack(fill="x")
            
        self.play_button = tk.Button(controls_frame, text="▶️ Play", 
                                   bg='#4CAF50', fg='white', 
                                   font=('Arial', 12, 'bold'), 
                                    command=self.play_sequence)
        self.play_button.pack(side="left", padx=(0, 5))
        
        self.pause_button = tk.Button(controls_frame, text="⏸️ Pause", 
                                    bg='#FF9800', fg='white', 
                                    font=('Arial', 12, 'bold'), 
                                     command=self.pause_sequence)
        self.pause_button.pack(side="left", padx=5)
        
        self.stop_button = tk.Button(controls_frame, text="⏹️ Stop", 
                                   bg='#f44336', fg='white', 
                                   font=('Arial', 12, 'bold'), 
                                   command=self.stop_sequence)
        self.stop_button.pack(side="left", padx=5)
        
        # Playback status
        self.playback_status = tk.Label(content_frame, text="⏹️ Stopped", 
                                      bg='#2d2d2d', fg='#888888', 
                                      font=('Arial', 11, 'bold'))
        self.playback_status.pack(anchor="w", pady=(10, 0))
            
    def setup_sequence_management_panel(self, parent):
        """Setup sequence management panel"""
        mgmt_frame = tk.LabelFrame(parent, text="📁 Sequence Management", 
                                     font=('Arial', 14, 'bold'),
                                     bg='#2d2d2d', fg='#ffffff')
        mgmt_frame.pack(fill="both", expand=True, pady=(0, 10))
            
        content_frame = tk.Frame(mgmt_frame, bg='#2d2d2d')
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Sequence list
        tk.Label(content_frame, text="Saved Sequences:", bg='#2d2d2d', fg='#ffffff',
                    font=('Arial', 11, 'bold')).pack(anchor="w", pady=(0, 5))
            
        list_frame = tk.Frame(content_frame, bg='#2d2d2d')
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
            
        self.sequence_listbox = tk.Listbox(list_frame, bg='#3d3d3d', fg='#ffffff',
                                             font=('Arial', 10), selectbackground='#2196F3')
        self.sequence_listbox.pack(side="left", fill="both", expand=True)
            
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.sequence_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.sequence_listbox.config(yscrollcommand=scrollbar.set)
            
            # Management buttons
        buttons_frame = tk.Frame(content_frame, bg='#2d2d2d')
        buttons_frame.pack(fill="x")
            
        tk.Button(buttons_frame, text="💾 Save", bg='#4CAF50', fg='#ffffff',
                     font=('Arial', 10, 'bold'), command=self.save_sequence).pack(side="left", padx=(0, 5))
            
        tk.Button(buttons_frame, text="📂 Load", bg='#2196F3', fg='#ffffff',
                     font=('Arial', 10, 'bold'), command=self.load_sequence).pack(side="left", padx=5)
            
        # Add sample sequence button
        tk.Button(buttons_frame, text="📝 Sample", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.create_sample_sequence).pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="🗑️ Delete", bg='#f44336', fg='#ffffff',
                     font=('Arial', 10, 'bold'), command=self.delete_sequence).pack(side="right")
            
    def setup_sequence_details_panel(self, parent):
            """Setup sequence details panel with three tabs: Text, Simulator, and Movement Cards"""
            details_frame = tk.LabelFrame(parent, text="📋 Current Sequence", font=('Arial', 14, 'bold'),
                                        bg='#2d2d2d', fg='#ffffff')
            details_frame.pack(fill="both", expand=True)
                
            content_frame = tk.Frame(details_frame, bg='#2d2d2d')
            content_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create tabbed interface
            self.sequence_tabs = ttk.Notebook(content_frame)
            self.sequence_tabs.pack(fill="both", expand=True)

            # Tab 1: Text View
            text_tab = tk.Frame(self.sequence_tabs, bg='#2d2d2d')
            self.sequence_tabs.add(text_tab, text="📝 Text")

            # Tab 2: Simulator View
            simulator_tab = tk.Frame(self.sequence_tabs, bg='#2d2d2d')
            self.sequence_tabs.add(simulator_tab, text="🤖 Simulator")

            # Tab 3: Movement Cards
            cards_tab = tk.Frame(self.sequence_tabs, bg='#2d2d2d')
            self.sequence_tabs.add(cards_tab, text="🎯 Movements")

            # Setup each tab
            self.setup_text_tab(text_tab)
            self.setup_simulator_tab(simulator_tab)
            self.setup_cards_tab(cards_tab)

            # Bind tab change event to refresh content
            self.sequence_tabs.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
            """Handle tab change events"""
            try:
                current_tab = self.sequence_tabs.select()
                tab_text = self.sequence_tabs.tab(current_tab, "text")

                if "🎯" in tab_text:  # Cards tab
                    self.refresh_movement_cards()
                elif "🤖" in tab_text:  # Simulator tab
                    self.update_simulator_visualization()
                # Text tab doesn't need special refresh

            except Exception as e:
              print(f"❌ Error handling tab change: {e}")

    def setup_text_tab(self, parent):
            """Setup text view tab for sequence display"""
            # Sequence info
            info_frame = tk.Frame(parent, bg='#2d2d2d')
            info_frame.pack(fill="x", pady=(0, 10))
                
            tk.Label(info_frame, text="Actions in sequence:", bg='#2d2d2d', fg='#ffffff',
                        font=('Arial', 11, 'bold')).pack(side="left")
                
            self.position_count = tk.Label(info_frame, text="0", bg='#2d2d2d', fg='#4CAF50',
                                            font=('Arial', 11, 'bold'))
            self.position_count.pack(side="right")
                
            # Actions list
            actions_frame = tk.Frame(parent, bg='#2d2d2d')
            actions_frame.pack(fill="both", expand=True)
            
            self.positions_text = tk.Text(actions_frame, bg='#1e1e1e', fg='#ffffff',
                                            font=('Consolas', 9), height=10, wrap=tk.WORD)
            self.positions_text.pack(side="left", fill="both", expand=True)
                
            pos_scrollbar = tk.Scrollbar(actions_frame, orient="vertical", 
                                        command=self.positions_text.yview)
            pos_scrollbar.pack(side="right", fill="y")
            self.positions_text.config(yscrollcommand=pos_scrollbar.set)
                
                # Initial content
            self.positions_text.insert("1.0", "No actions recorded yet.\n\nStart recording to capture robot actions.")
            
    def setup_simulator_tab(self, parent):
            """Setup simulator tab with 2D robot visualization"""
            # Main simulator frame
            sim_frame = tk.Frame(parent, bg='#2d2d2d')
            sim_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Left side - Controls
            controls_frame = tk.Frame(sim_frame, bg='#2d2d2d')
            controls_frame.pack(side="left", fill="y", padx=(0, 10))

            # Simulator controls
            self.setup_simulator_controls(controls_frame)

            # Right side - 2D Visualization
            viz_frame = tk.Frame(sim_frame, bg='#2d2d2d')
            viz_frame.pack(side="right", fill="both", expand=True)

            # 2D visualization
            self.setup_simulator_visualization(viz_frame)

            # Initialize simulator after everything is set up
            self.init_simulator_visualization()

            # Force initial view setup
            self.change_simulator_view()

    def setup_simulator_controls(self, parent):
            """Setup simulator control panel"""
            # Control panel
            control_panel = tk.LabelFrame(parent, text="🎮 Simulator Controls",
                                    font=('Arial', 12, 'bold'),
                                    bg='#3d3d3d', fg='#ffffff')
            control_panel.pack(fill="x", pady=(0, 10))

            panel_content = tk.Frame(control_panel, bg='#3d3d3d')
            panel_content.pack(fill="x", padx=10, pady=10)

                # Enable simulator toggle
            self.sim_enabled_var = tk.BooleanVar(value=True)
            tk.Checkbutton(panel_content, text="🎮 Enable Simulator",
                      variable=self.sim_enabled_var,
                      bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'),
                      command=self.toggle_sequence_simulator).pack(anchor="w", pady=5)

            # Real-time update toggle
            self.realtime_update_var = tk.BooleanVar(value=True)
            tk.Checkbutton(panel_content, text="⚡ Real-time Update",
                      variable=self.realtime_update_var,
                      bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10)).pack(anchor="w", pady=5)

            # Separator
            tk.Frame(panel_content, height=2, bg='#555555').pack(fill="x", pady=10)

            # Play sequence button
            tk.Button(panel_content, text="🎬 Play Sequence", bg='#4CAF50', fg='#ffffff',
                 font=('Arial', 10, 'bold'),
                 command=self.play_sequence_in_simulator).pack(fill="x", pady=5)

            # Reset position button
            tk.Button(panel_content, text="🔄 Reset Position", bg='#FF9800', fg='#ffffff',
                 font=('Arial', 10, 'bold'),
                 command=self.reset_simulator_position).pack(fill="x", pady=5)

    def setup_simulator_visualization(self, parent):
            """Setup 2D visualization for sequence simulator"""
            # Visualization frame
            viz_panel = tk.LabelFrame(parent, text="🎯 Sequence Simulator",
                                font=('Arial', 12, 'bold'),
                                bg='#3d3d3d', fg='#ffffff')
            viz_panel.pack(fill="both", expand=True)

            viz_content = tk.Frame(viz_panel, bg='#3d3d3d')
            viz_content.pack(fill="both", expand=True, padx=10, pady=10)

            # View controls frame
            view_controls_frame = tk.Frame(viz_content, bg='#3d3d3d')
            view_controls_frame.pack(fill="x", pady=(0, 10))

            # View selection buttons
            self.sim_view_var = tk.StringVar(value="side")
            tk.Radiobutton(view_controls_frame, text="👤 Side View", variable=self.sim_view_var,
                      value="side", bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'), command=self.change_simulator_view).pack(side="left", padx=(0, 10))

            tk.Radiobutton(view_controls_frame, text="👁️ Front View", variable=self.sim_view_var,
                      value="front", bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'), command=self.change_simulator_view).pack(side="left", padx=(0, 10))

            tk.Radiobutton(view_controls_frame, text="🔄 Both Views", variable=self.sim_view_var,
                      value="both", bg='#3d3d3d', fg='#ffffff', selectcolor='#4d4d4d',
                      font=('Arial', 10, 'bold'), command=self.change_simulator_view).pack(side="left")

            # Canvas container
            canvas_container = tk.Frame(viz_content, bg='#3d3d3d')
            canvas_container.pack(fill="both", expand=True)

            # Side view canvas
            self.sim_side_canvas = tk.Canvas(canvas_container, bg='#1a1a1a', highlightthickness=0,
                                           width=400, height=300)

            # Front view canvas
            self.sim_front_canvas = tk.Canvas(canvas_container, bg='#1a1a1a', highlightthickness=0,
                                            width=400, height=300)

            # Initially show only side view (will be configured by change_simulator_view)
            # Don't pack both canvases yet - let change_simulator_view handle it

            # Status bar
            self.sim_status_label = tk.Label(viz_content, text="Simulator: Ready - Side View",
                                       bg='#3d3d3d', fg='#4CAF50',
                                       font=('Arial', 10))
            self.sim_status_label.pack(pady=(5, 0))

            # Note: init_simulator_visualization is called from parent function

    def setup_cards_tab(self, parent):
            """Setup movement cards tab"""
            # Main cards container
            cards_frame = tk.Frame(parent, bg='#2d2d2d')
            cards_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Header with info
            header_frame = tk.Frame(cards_frame, bg='#2d2d2d')
            header_frame.pack(fill="x", pady=(0, 10))

            tk.Label(header_frame, text="Movement Cards:", bg='#2d2d2d', fg='#ffffff',
                font=('Arial', 12, 'bold')).pack(side="left")

            self.cards_count_label = tk.Label(header_frame, text="0 movements", bg='#2d2d2d', fg='#4CAF50',
                                        font=('Arial', 11, 'bold'))
            self.cards_count_label.pack(side="right")

            # Scrollable frame for cards
            self.setup_cards_scrollable_frame(cards_frame)

            # Controls at bottom
            controls_frame = tk.Frame(cards_frame, bg='#2d2d2d')
            controls_frame.pack(fill="x", pady=(10, 0))

            tk.Button(controls_frame, text="🔄 Refresh Cards", bg='#2196F3', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.refresh_movement_cards).pack(side="left")

            tk.Button(controls_frame, text="🗑️ Clear All", bg='#f44336', fg='#ffffff',
                 font=('Arial', 10, 'bold'), command=self.clear_all_movements).pack(side="right")

    def setup_cards_scrollable_frame(self, parent):
            """Setup scrollable frame for movement cards"""
            # Create scrollable frame
            self.cards_canvas = tk.Canvas(parent, bg='#2d2d2d', highlightthickness=0)
            scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.cards_canvas.yview)
            self.cards_scrollable_frame = tk.Frame(self.cards_canvas, bg='#2d2d2d')

            self.cards_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))
            )

            self.cards_canvas.create_window((0, 0), window=self.cards_scrollable_frame, anchor="nw")
            self.cards_canvas.configure(yscrollcommand=scrollbar.set)

            self.cards_canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Bind mousewheel for scrolling
    def _on_mousewheel(event):
            self.cards_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

            self.cards_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ===============================
    # SIMULATOR METHODS
    # ===============================

    def init_simulator_visualization(self):
            """Initialize simulator visualization based on ESP32 tab implementation"""
            try:
            # Initialize arm position variables FIRST (same as ESP32 tab)
                self.left_brazo_var = tk.DoubleVar(value=100)
                self.left_frente_var = tk.DoubleVar(value=95)
                self.left_high_var = tk.DoubleVar(value=140)
                self.left_pollo_var = tk.DoubleVar(value=90)
                self.right_brazo_var = tk.DoubleVar(value=30)
                self.right_frente_var = tk.DoubleVar(value=160)
                self.right_high_var = tk.DoubleVar(value=165)
                self.right_pollo_var = tk.DoubleVar(value=100)

                # Initialize arms state (same as ESP32 tab)
                self.sim_arms_state = {
                    'left_arm': {
                        'brazo': 100,
                        'frente': 95,
                        'high': 140,
                        'pollo': 90
                    },
                    'right_arm': {
                        'brazo': 30,
                        'frente': 160,
                        'high': 165,
                        'pollo': 100
                    }
                }

                # Set current canvas reference
                self.sim_arms_canvas = self.sim_side_canvas

                # Start visualization update
                self.update_simulator_visualization()

            except Exception as e:
                print(f"❌ Error initializing simulator visualization: {e}")
                import traceback
                traceback.print_exc()

    def toggle_sequence_simulator(self):
            """Toggle simulator on/off"""
            try:
                if self.sim_enabled_var.get():
                    self.sim_status_label.config(text="Simulator: Active", fg='#4CAF50')
                    print("🎮 Sequence Simulator enabled")
                else:
                    self.sim_status_label.config(text="Simulator: Disabled", fg='#ff6b6b')
                    print("🎮 Sequence Simulator disabled")
            except Exception as e:
              print(f"❌ Error toggling simulator: {e}")

    def change_simulator_view(self):
            """Change between different simulator views"""
            try:
                view = self.sim_view_var.get()

                # Forget all canvases first
                self.sim_side_canvas.pack_forget()
                self.sim_front_canvas.pack_forget()

                if view == "side":
                    self.sim_side_canvas.pack(fill="both", expand=True)
                    self.sim_arms_canvas = self.sim_side_canvas
                    self.sim_status_label.config(text="Simulator: Ready - Side View")

                elif view == "front":
                    self.sim_front_canvas.pack(fill="both", expand=True)
                    self.sim_arms_canvas = self.sim_front_canvas
                    self.sim_status_label.config(text="Simulator: Ready - Front View")

                elif view == "both":
                    self.sim_side_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
                    self.sim_front_canvas.pack(side="right", fill="both", expand=True, padx=(5, 0))
                    self.sim_arms_canvas = self.sim_side_canvas  # Use side canvas as primary
                    self.sim_status_label.config(text="Simulator: Ready - Both Views")

                # Force update after a short delay
                self.parent_gui.root.after(100, self.force_simulator_view_update)

            except Exception as e:
                print(f"❌ Error changing simulator view: {e}")
                import traceback
                traceback.print_exc()

    def force_simulator_view_update(self):
            """Force update of the simulator view"""
            try:
                view = self.sim_view_var.get()

                if view == "side":
                    self.update_simulator_side_view()
                elif view == "front":
                    self.update_simulator_front_view()
                elif view == "both":
                    self.update_simulator_side_view()
                    self.update_simulator_front_view()

            except Exception as e:
                print(f"❌ Error in force simulator view update: {e}")
                import traceback
                traceback.print_exc()

    def update_simulator_visualization(self):
            """Update simulator visualization (based on ESP32 tab)"""
            try:
                if not hasattr(self, 'sim_enabled_var') or not self.sim_enabled_var.get():
                    return

                view = self.sim_view_var.get()

                # Update side view
                if view in ["side", "both"]:
                    self.update_simulator_side_view()

                # Update front view
                if view in ["front", "both"]:
                    self.update_simulator_front_view()

                # Schedule next update for real-time updates
                if hasattr(self, 'realtime_update_var') and self.realtime_update_var.get():
                    self.parent_gui.root.after(50, self.update_simulator_visualization)

            except Exception as e:
                print(f"❌ Error updating simulator visualization: {e}")
                import traceback
                traceback.print_exc()

    def update_simulator_side_view(self):
            """Update side view visualization (based on ESP32 tab implementation)"""
            try:
                if not hasattr(self, 'sim_side_canvas') or not self.sim_side_canvas:
                    print("❌ sim_side_canvas not available")
                    return

                # Clear canvas
                self.sim_side_canvas.delete('all')

                # Get canvas dimensions
                width = max(200, self.sim_side_canvas.winfo_width())
                height = max(150, self.sim_side_canvas.winfo_height())

                # Ensure minimum dimensions for drawing
                if width < 200 or height < 150:
                    width, height = 400, 300

                # Draw side view
                self.draw_simulator_side_view(width, height)

            except Exception as e:
                print(f"❌ Error updating simulator side view: {e}")
                import traceback
                traceback.print_exc()

    def update_simulator_front_view(self):
            """Update front view visualization (based on ESP32 tab implementation)"""
            try:
                if not hasattr(self, 'sim_front_canvas') or not self.sim_front_canvas:
                    print("❌ sim_front_canvas not available")
                    return

                # Clear canvas
                self.sim_front_canvas.delete('all')

                # Get canvas dimensions
                width = max(200, self.sim_front_canvas.winfo_width())
                height = max(150, self.sim_front_canvas.winfo_height())

                # Ensure minimum dimensions for drawing
                if width < 200 or height < 150:
                    width, height = 400, 300

                # Draw front view
                self.draw_simulator_front_view(width, height)

            except Exception as e:
                print(f"❌ Error updating simulator front view: {e}")
                import traceback
                traceback.print_exc()

    def draw_simulator_side_view(self, width, height):
            """Draw side view of robot arms (from ESP32 tab)"""
            try:
            # Center point
                center_x = width // 2
                center_y = height // 2

                # Draw torso (side view - rectangle)
                torso_width = 80
                torso_height = 120
                torso_x = center_x - torso_width // 2
                torso_y = center_y - 20

                # Torso
                self.sim_side_canvas.create_rectangle(torso_x, torso_y,
                                                torso_x + torso_width, torso_y + torso_height,
                                                fill='#666666', outline='#ffffff', width=2)

                # Draw head (circle)
                head_radius = 25
                head_x = center_x
                head_y = torso_y - head_radius - 10

                self.sim_side_canvas.create_oval(head_x - head_radius, head_y - head_radius,
                                            head_x + head_radius, head_y + head_radius,
                                            fill='#888888', outline='#ffffff', width=2)

                # Draw arms from side view
                self.draw_simulator_side_arm('left', center_x - 50, center_y + 20, width, height)
                self.draw_simulator_side_arm('right', center_x + 50, center_y + 20, width, height)

                # Add labels
                self.sim_side_canvas.create_text(center_x, torso_y + torso_height + 20,
                                            text="Side View - ESP32 Robot", fill='#ffffff',
                                            font=('Arial', 12, 'bold'))

                # Add position info
                pos_text = f"L:({self.left_brazo_var.get():.0f},{self.left_frente_var.get():.0f},{self.left_high_var.get():.0f}) " \
                        f"R:({self.right_brazo_var.get():.0f},{self.right_frente_var.get():.0f},{self.right_high_var.get():.0f})"
                self.sim_side_canvas.create_text(center_x, height - 30,
                                            text=pos_text, fill='#888888',
                                            font=('Arial', 9))

                # Force canvas update
                self.sim_side_canvas.update()

            except Exception as e:
              print(f"❌ Error drawing simulator side view: {e}")

    def draw_simulator_front_view(self, width, height):
            """Draw front view of robot arms (from ESP32 tab)"""
            try:
            # Center point
                center_x = width // 2
                center_y = height // 2

                # Draw torso (front view - wider rectangle)
                torso_width = 120
                torso_height = 100
                torso_x = center_x - torso_width // 2
                torso_y = center_y - 10

                # Torso
                self.sim_front_canvas.create_rectangle(torso_x, torso_y,
                                                    torso_x + torso_width, torso_y + torso_height,
                                                    fill='#666666', outline='#ffffff', width=2)

                # Draw head (circle)
                head_radius = 30
                head_x = center_x
                head_y = torso_y - head_radius - 10

                self.sim_front_canvas.create_oval(head_x - head_radius, head_y - head_radius,
                                                head_x + head_radius, head_y + head_radius,
                                                fill='#888888', outline='#ffffff', width=2)

                # Draw arms from front view
                self.draw_simulator_front_arm('left', center_x - 80, center_y + 20, width, height)
                self.draw_simulator_front_arm('right', center_x + 80, center_y + 20, width, height)

                # Add labels
                self.sim_front_canvas.create_text(center_x, torso_y + torso_height + 20,
                                                text="Front View - ESP32 Robot", fill='#ffffff',
                                                font=('Arial', 12, 'bold'))

                # Add position info
                pos_text = f"L:({self.left_brazo_var.get():.0f},{self.left_frente_var.get():.0f},{self.left_high_var.get():.0f}) " \
                        f"R:({self.right_brazo_var.get():.0f},{self.right_frente_var.get():.0f},{self.right_high_var.get():.0f})"
                self.sim_front_canvas.create_text(center_x, height - 30,
                                                text=pos_text, fill='#888888',
                                                font=('Arial', 9))

                # Force canvas update
                self.sim_front_canvas.update()

            except Exception as e:
                print(f"❌ Error drawing simulator front view: {e}")

    def draw_simulator_side_arm(self, side, base_x, base_y, width, height):
            """Draw individual arm from side view (from ESP32 tab)"""
            try:
                if side == 'left':
                    angles = {
                        'brazo': self.left_brazo_var.get(),
                        'frente': self.left_frente_var.get(),
                        'high': self.left_high_var.get()
                    }
                    color = '#00FF00'  # Bright Green for left arm
                else:
                    angles = {
                        'brazo': self.right_brazo_var.get(),
                        'frente': self.right_frente_var.get(),
                        'high': self.right_high_var.get(),
                        'pollo': self.right_pollo_var.get()
                    }
                    color = '#0080FF'  # Bright Blue for right arm

                # Calculate arm segments for side view
                segment_length = 50

                # Shoulder joint
                shoulder_x = base_x
                shoulder_y = base_y

                # Upper arm (brazo) - side view shows forward/backward movement
                brazo_angle = math.radians(angles['brazo'] - 90)  # Adjust for side view
                upper_x = shoulder_x + segment_length * math.cos(brazo_angle)
                upper_y = shoulder_y - segment_length * math.sin(brazo_angle)

                # Forearm (frente) - side view shows up/down movement
                frente_angle = brazo_angle + math.radians(angles['frente'])
                forearm_x = upper_x + segment_length * math.cos(frente_angle)
                forearm_y = upper_y - segment_length * math.sin(frente_angle)

                # Hand (high) - side view shows wrist rotation
                hand_angle = frente_angle + math.radians(angles['high'])
                hand_x = forearm_x + segment_length * 0.6 * math.cos(hand_angle)
                hand_y = forearm_y - segment_length * 0.6 * math.sin(hand_angle)

                # Draw arm segments
                self.sim_side_canvas.create_line(shoulder_x, shoulder_y, upper_x, upper_y,
                                            fill=color, width=4)
                self.sim_side_canvas.create_line(upper_x, upper_y, forearm_x, forearm_y,
                                            fill=color, width=4)
                self.sim_side_canvas.create_line(forearm_x, forearm_y, hand_x, hand_y,
                                            fill=color, width=3)

                # Draw joints
                joint_radius = 5
                self.sim_side_canvas.create_oval(shoulder_x - joint_radius, shoulder_y - joint_radius,
                                            shoulder_x + joint_radius, shoulder_y + joint_radius,
                                            fill='#ffffff', outline=color, width=2)
                self.sim_side_canvas.create_oval(upper_x - joint_radius, upper_y - joint_radius,
                                            upper_x + joint_radius, upper_y + joint_radius,
                                            fill='#ffffff', outline=color, width=2)
                self.sim_side_canvas.create_oval(forearm_x - joint_radius, forearm_y - joint_radius,
                                            forearm_x + joint_radius, forearm_y + joint_radius,
                                            fill='#ffffff', outline=color, width=2)
                self.sim_side_canvas.create_oval(hand_x - joint_radius, hand_y - joint_radius,
                                            hand_x + joint_radius, hand_y + joint_radius,
                                            fill=color, outline='#ffffff', width=2)

                # Add labels
                self.sim_side_canvas.create_text(shoulder_x, shoulder_y - 15,
                                            text=f"{side.upper()}", fill=color,
                                            font=('Arial', 8, 'bold'))

            except Exception as e:
               print(f"❌ Error drawing {side} arm (simulator side view): {e}")

    def draw_simulator_front_arm(self, side, base_x, base_y, width, height):
            """Draw individual arm from front view (from ESP32 tab)"""
            try:
                if side == 'left':
                    angles = {
                        'brazo': self.left_brazo_var.get(),
                        'frente': self.left_frente_var.get(),
                        'high': self.left_high_var.get()
                    }
                    color = '#00FF00'  # Bright Green for left arm
                else:
                    angles = {
                        'brazo': self.right_brazo_var.get(),
                        'frente': self.right_frente_var.get(),
                        'high': self.right_high_var.get(),
                        'pollo': self.right_pollo_var.get()
                    }
                    color = '#0080FF'  # Bright Blue for right arm

                # Calculate arm segments for front view
                segment_length = 50

                # Shoulder joint
                shoulder_x = base_x
                shoulder_y = base_y

                # Upper arm (brazo) - front view shows left/right movement
                brazo_angle = math.radians(angles['brazo'])
                upper_x = shoulder_x + segment_length * math.cos(brazo_angle)
                upper_y = shoulder_y - segment_length * math.sin(brazo_angle)

                # Forearm (frente) - front view shows up/down movement
                frente_angle = brazo_angle + math.radians(angles['frente'])
                forearm_x = upper_x + segment_length * math.cos(frente_angle)
                forearm_y = upper_y - segment_length * math.sin(frente_angle)

                # Hand (high) - front view shows wrist rotation
                hand_angle = frente_angle + math.radians(angles['high'])
                hand_x = forearm_x + segment_length * 0.6 * math.cos(hand_angle)
                hand_y = forearm_y - segment_length * 0.6 * math.sin(hand_angle)

                # Draw arm segments
                self.sim_front_canvas.create_line(shoulder_x, shoulder_y, upper_x, upper_y,
                                                fill=color, width=4)
                self.sim_front_canvas.create_line(upper_x, upper_y, forearm_x, forearm_y,
                                                fill=color, width=4)
                self.sim_front_canvas.create_line(forearm_x, forearm_y, hand_x, hand_y,
                                                fill=color, width=3)

                # Draw joints
                joint_radius = 5
                self.sim_front_canvas.create_oval(shoulder_x - joint_radius, shoulder_y - joint_radius,
                                                shoulder_x + joint_radius, shoulder_y + joint_radius,
                                                fill='#ffffff', outline=color, width=2)
                self.sim_front_canvas.create_oval(upper_x - joint_radius, upper_y - joint_radius,
                                                upper_x + joint_radius, upper_y + joint_radius,
                                                fill='#ffffff', outline=color, width=2)
                self.sim_front_canvas.create_oval(forearm_x - joint_radius, forearm_y - joint_radius,
                                                forearm_x + joint_radius, forearm_y + joint_radius,
                                                fill='#ffffff', outline=color, width=2)
                self.sim_front_canvas.create_oval(hand_x - joint_radius, hand_y - joint_radius,
                                                hand_x + joint_radius, hand_y + joint_radius,
                                                fill=color, outline='#ffffff', width=2)

                # Add labels
                self.sim_front_canvas.create_text(shoulder_x, shoulder_y - 15,
                                                text=f"{side.upper()}", fill=color,
                                                font=('Arial', 8, 'bold'))

            except Exception as e:
                print(f"❌ Error drawing {side} arm (simulator front view): {e}")

    def play_sequence_in_simulator(self):
            """Play the current sequence in the simulator"""
            try:
                if not self.recorded_actions:
                    messagebox.showwarning("Warning", "No sequence to play. Record some actions first.")
                    return

                if not self.sim_enabled_var.get():
                    messagebox.showwarning("Warning", "Simulator is disabled. Enable it first.")
                    return

                self.sim_status_label.config(text="Simulator: Playing Sequence", fg='#FF9800')

                # Start playback in a separate thread
                sim_thread = threading.Thread(target=self._simulator_playback_thread)
                sim_thread.daemon = True
                sim_thread.start()

            except Exception as e:
                print(f"❌ Error playing sequence in simulator: {e}")
                messagebox.showerror("Error", f"Failed to play sequence in simulator: {e}")

    def _simulator_playback_thread(self):
            """Simulator playback thread"""
            try:
                for i, movement in enumerate(self.recorded_actions):
                    if not self.sim_enabled_var.get():
                        break

                    self.sim_status_label.config(text=f"Simulator: Movement {i+1}/{len(self.recorded_actions)}", fg='#FF9800')

                    for action in movement['actions']:
                        if not self.sim_enabled_var.get():
                            break

                        # Simulate the action by updating the visualization
                        self.simulate_action_in_simulator(action)

                        # Wait between actions
                        time.sleep(1.0)

                    # Wait between movements
                    time.sleep(2.0)

                # Playback finished
                self.sim_status_label.config(text="Simulator: Sequence Complete", fg='#4CAF50')

                # Reset to ready state after a delay
                def reset_status():
                    self.sim_status_label.config(text="Simulator: Ready", fg='#4CAF50')

                self.parent_gui.root.after(2000, reset_status)

            except Exception as e:
                print(f"❌ Error in simulator playback thread: {e}")
                self.sim_status_label.config(text="Simulator: Error", fg='#f44336')

    def simulate_action_in_simulator(self, action):
        """Simulate an action in the simulator"""
        try:
            command = action.get('command', '')
            parameters = action.get('parameters', {})

            if command == 'BRAZOS':
                # Update arm positions in simulator
                # Sequence uses: BI, FI, HI, BD, FD, HD, PD
                # Simulator expects: left_brazo_var, left_frente_var, left_high_var, right_brazo_var, etc.

                bi = parameters.get('BI', 100)  # Brazo Izquierdo
                bd = parameters.get('BD', 30)   # Brazo Derecho
                fi = parameters.get('FI', 95)   # Frente Izquierdo
                fd = parameters.get('FD', 160)  # Frente Derecho
                hi = parameters.get('HI', 140)  # High Izquierdo
                hd = parameters.get('HD', 165)  # High Derecho
                pd = parameters.get('PD', 100)  # Pollo Derecho
                pi = parameters.get('PI', 90)   # Pollo Izquierdo

                # Update simulator variables
                if hasattr(self, 'left_brazo_var'):
                    self.left_brazo_var.set(bi)
                if hasattr(self, 'left_frente_var'):
                    self.left_frente_var.set(fi)
                if hasattr(self, 'left_high_var'):
                    self.left_high_var.set(hi)
                if hasattr(self, 'left_pollo_var'):
                    self.left_pollo_var.set(pi)
                if hasattr(self, 'right_brazo_var'):
                    self.right_brazo_var.set(bd)
                if hasattr(self, 'right_frente_var'):
                    self.right_frente_var.set(fd)
                if hasattr(self, 'right_high_var'):
                    self.right_high_var.set(hd)
                if hasattr(self, 'right_pollo_var'):
                    self.right_pollo_var.set(pd)

                # Update simulator state
                self.sim_arms_state['left_arm']['brazo'] = bi
                self.sim_arms_state['left_arm']['frente'] = fi
                self.sim_arms_state['left_arm']['high'] = hi
                self.sim_arms_state['left_arm']['pollo'] = pi
                self.sim_arms_state['right_arm']['brazo'] = bd
                self.sim_arms_state['right_arm']['frente'] = fd
                self.sim_arms_state['right_arm']['high'] = hd
                self.sim_arms_state['right_arm']['pollo'] = pd

                # Update visualization
                self.update_simulator_visualization()

            elif command == 'MUNECA':
                # Simulate wrist movements with new relative positioning system
                mano = parameters.get('mano', '')
                angulo = parameters.get('angulo', 80)
                
                if mano == 'derecha':
                    # Update right wrist variable if it exists
                    if hasattr(self, 'right_wrist_var'):
                        self.right_wrist_var.set(angulo)
                    print(f"🤖 Simulator: Right wrist moved to {angulo}° (relative positioning)")
                elif mano == 'izquierda':
                    # Update left wrist variable if it exists
                    if hasattr(self, 'left_wrist_var'):
                        self.left_wrist_var.set(angulo)
                    print(f"🤖 Simulator: Left wrist moved to {angulo}°")
                
                # Update visualization
                self.update_simulator_visualization()

            elif command == 'MANO':
                # Simulate hand gestures (just show status for now)
                gesture = parameters.get('GESTO', '')
                if gesture:
                    print(f"🤖 Simulator: Hand gesture {gesture}")

            elif command == 'HABLAR':
                # Simulate speech (just show status for now)
                text = parameters.get('texto', '')
                if text:
                    print(f"🗣️ Simulator: Speaking '{text[:50]}...'")

        except Exception as e:
             print(f"❌ Error simulating action: {e}")

    def reset_simulator_position(self):
            """Reset simulator to default position"""
            try:
            # Reset to default positions (same as ESP32 tab defaults)
                default_positions = {
                    'left_arm': {
                        'brazo': 100,
                        'frente': 95,
                        'high': 140,
                        'pollo': 90
                    },
                    'right_arm': {
                        'brazo': 30,
                        'frente': 160,
                        'high': 165,
                        'pollo': 100
                    }
                }

                # Update simulator variables
                if hasattr(self, 'left_brazo_var'):
                    self.left_brazo_var.set(default_positions['left_arm']['brazo'])
                if hasattr(self, 'left_frente_var'):
                    self.left_frente_var.set(default_positions['left_arm']['frente'])
                if hasattr(self, 'left_high_var'):
                    self.left_high_var.set(default_positions['left_arm']['high'])
                if hasattr(self, 'left_pollo_var'):
                    self.left_pollo_var.set(default_positions['left_arm']['pollo'])
                if hasattr(self, 'right_brazo_var'):
                    self.right_brazo_var.set(default_positions['right_arm']['brazo'])
                if hasattr(self, 'right_frente_var'):
                    self.right_frente_var.set(default_positions['right_arm']['frente'])
                if hasattr(self, 'right_high_var'):
                    self.right_high_var.set(default_positions['right_arm']['high'])
                if hasattr(self, 'right_pollo_var'):
                    self.right_pollo_var.set(default_positions['right_arm']['pollo'])

                # Update simulator state
                self.sim_arms_state = default_positions

                # Update visualization
                self.update_simulator_visualization()

                self.sim_status_label.config(text="Simulator: Position Reset", fg='#4CAF50')
                print("🔄 Simulator position reset")

            except Exception as e:
             print(f"❌ Error resetting simulator position: {e}")

    # ===============================
    # MOVEMENT CARDS METHODS
    # ===============================

    def refresh_movement_cards(self):
            """Refresh the movement cards display"""
            try:
                # Clear existing cards
                for widget in self.cards_scrollable_frame.winfo_children():
                    widget.destroy()

                # Create cards for each movement
                for i, movement in enumerate(self.recorded_actions):
                    self.create_movement_card(movement, i)

                # Update count
                self.cards_count_label.config(text=f"{len(self.recorded_actions)} movements")

                print(f"🔄 Refreshed {len(self.recorded_actions)} movement cards")

            except Exception as e:
              print(f"❌ Error refreshing movement cards: {e}")

    def create_movement_card(self, movement, index):
            """Create a card for a movement"""
            try:
                # Card frame
                card_frame = tk.LabelFrame(self.cards_scrollable_frame,
                                        text=f"🎯 Movement {index + 1}: {movement.get('name', 'Unknown')}",
                                        font=('Arial', 10, 'bold'),
                                        bg='#3d3d3d', fg='#ffffff')
                card_frame.pack(fill="x", pady=(0, 5), padx=5)

                card_content = tk.Frame(card_frame, bg='#3d3d3d')
                card_content.pack(fill="x", padx=10, pady=5)

                # Movement info
                info_frame = tk.Frame(card_content, bg='#3d3d3d')
                info_frame.pack(fill="x", pady=(0, 5))

                tk.Label(info_frame, text=f"Actions: {len(movement.get('actions', []))}",
                        bg='#3d3d3d', fg='#4CAF50', font=('Arial', 9, 'bold')).pack(side="left")

                tk.Label(info_frame, text=f"ID: {movement.get('id', 'N/A')}",
                        bg='#3d3d3d', fg='#ffffff', font=('Arial', 9)).pack(side="right")

                # Actions preview
                actions_text = ""
                for j, action in enumerate(movement.get('actions', [])[:3]):  # Show first 3 actions
                    command = action.get('command', 'Unknown')
                    desc = action.get('description', '')[:30]
                    actions_text += f"• {command}: {desc}\n"

                if len(movement.get('actions', [])) > 3:
                    actions_text += f"... and {len(movement.get('actions', [])) - 3} more actions"

                actions_label = tk.Label(card_content, text=actions_text.strip(),
                                    bg='#3d3d3d', fg='#ffffff', font=('Arial', 8),
                                    justify="left", anchor="w")
                actions_label.pack(fill="x", pady=(0, 5))

                # Control buttons
                buttons_frame = tk.Frame(card_content, bg='#3d3d3d')
                buttons_frame.pack(fill="x")

                # Delete button
                tk.Button(buttons_frame, text="🗑️ Delete", bg='#f44336', fg='#ffffff',
                        font=('Arial', 8, 'bold'),
                        command=lambda idx=index: self.delete_movement_card(idx)).pack(side="right", padx=(5, 0))

                # Move up button
                if index > 0:
                    tk.Button(buttons_frame, text="⬆️ Up", bg='#2196F3', fg='#ffffff',
                            font=('Arial', 8, 'bold'),
                            command=lambda idx=index: self.move_movement_card(idx, -1)).pack(side="right", padx=(0, 5))

                # Move down button
                if index < len(self.recorded_actions) - 1:
                    tk.Button(buttons_frame, text="⬇️ Down", bg='#FF9800', fg='#ffffff',
                            font=('Arial', 8, 'bold'),
                            command=lambda idx=index: self.move_movement_card(idx, 1)).pack(side="right", padx=(0, 5))

            except Exception as e:
             print(f"❌ Error creating movement card: {e}")

    def delete_movement_card(self, index):
            """Delete a movement card"""
            try:
                if 0 <= index < len(self.recorded_actions):
                    deleted_movement = self.recorded_actions.pop(index)
                    self.refresh_movement_cards()
                    self.update_sequence_display()  # Update text tab as well

                    print(f"🗑️ Deleted movement: {deleted_movement.get('name', 'Unknown')}")
                    messagebox.showinfo("Success", f"Movement '{deleted_movement.get('name', 'Unknown')}' deleted successfully!")

            except Exception as e:
                print(f"❌ Error deleting movement card: {e}")
                messagebox.showerror("Error", f"Failed to delete movement: {e}")

    def move_movement_card(self, index, direction):
            """Move a movement card up or down"""
            try:
                new_index = index + direction
                if 0 <= new_index < len(self.recorded_actions):
                    # Swap movements
                    self.recorded_actions[index], self.recorded_actions[new_index] = \
                    self.recorded_actions[new_index], self.recorded_actions[index]

                    self.refresh_movement_cards()
                    self.update_sequence_display()  # Update text tab as well

                    print(f"🔄 Moved movement {index + 1} {'up' if direction == -1 else 'down'}")
                    messagebox.showinfo("Success", f"Movement moved {'up' if direction == -1 else 'down'} successfully!")

            except Exception as e:
                print(f"❌ Error moving movement card: {e}")
                messagebox.showerror("Error", f"Failed to move movement: {e}")

    def clear_all_movements(self):
            """Clear all movements"""
            try:
                if not self.recorded_actions:
                    messagebox.showinfo("Info", "No movements to clear.")
                    return

                result = messagebox.askyesno("Confirm Clear", f"Are you sure you want to clear all {len(self.recorded_actions)} movements?")
                if result:
                    self.recorded_actions.clear()
                    self.refresh_movement_cards()
                    self.update_sequence_display()  # Update text tab as well

                    print("🗑️ All movements cleared")
                    messagebox.showinfo("Success", "All movements cleared successfully!")

            except Exception as e:
                print(f"❌ Error clearing movements: {e}")
                messagebox.showerror("Error", f"Failed to clear movements: {e}")
            
    def toggle_recording(self):
        """Toggle sequence recording"""
        try:
            # Allow recording even without ESP32 connection (for testing/demo purposes)
            if not self.esp32_connected:
                result = messagebox.askyesno("No ESP32 Connection", 
                    "No ESP32 connection detected. You can still record sequences for testing/demo purposes.\n\n"
                    "Would you like to continue with recording?")
                if not result:
                    return
            
            if self.is_recording:
                self.stop_recording_ui()
            else:
                self.start_recording_ui()
                
        except Exception as e:
            print(f"❌ Error toggling recording: {e}")
            messagebox.showerror("Error", f"Error toggling recording: {e}")
                
    def start_recording_ui(self):
        """Update UI for recording state"""
        try:
            self.is_recording = True
            self.recording_start_time = time.time()
            self.recording_status.config(text="🔴 Recording...", fg='#f44336')
            self.record_button.config(text="⏹️ Stop Recording", bg='#FF9800')
            self.stop_record_button.config(state="normal")
            
            # Initialize new movement
            self.current_movement = {
                "id": self.movement_counter,
                "name": f"Movement_{self.movement_counter}",
                "actions": []
            }
            self.movement_counter += 1
            
            # Update sequence display and movement buttons
            self.update_sequence_display()
            self.update_movement_buttons()
            
            print("✅ Started recording sequence")
            messagebox.showinfo("Recording Started", 
                "Sequence recording started!\n\n"
                "To create movements:\n"
                "1. Use robot controls to set positions\n"
                "2. Click '📍 Capture Position' to add actions\n"
                "3. Click '💾 Save Movement' when ready\n"
                "4. Repeat for more movements")
            
        except Exception as e:
            print(f"❌ Error starting recording: {e}")
        
    def stop_recording_ui(self):
        """Update UI for stopped recording state"""
        try:
            self.is_recording = False
            self.recording_status.config(text="⭕ Ready to Record", fg='#FFD700')
            self.record_button.config(text="🔴 Start Recording", bg='#f44336')
            self.stop_record_button.config(state="disabled")
            
            # Save current movement if it has actions
            if self.current_movement and self.current_movement["actions"]:
                self.recorded_actions.append(self.current_movement)
                self.current_movement = None
            
            # Update sequence display and movement buttons
            self.update_sequence_display()
            self.update_movement_buttons()
            
            print("✅ Stopped recording sequence")
            messagebox.showinfo("Recording Stopped", 
                "Sequence recording stopped!\n\n"
                f"Movements recorded: {len(self.recorded_actions)}\n"
                "You can now save the sequence or start a new recording.")
            
        except Exception as e:
            print(f"❌ Error stopping recording: {e}")
    
    def update_current_movement(self):
        """Update current movement with current arm positions"""
        try:
            if not self.is_recording:
                print("⚠️ [DEBUG] update_current_movement called but not recording")
                return
            
            print("🔄 [DEBUG] update_current_movement called - updating positions")
            
            # Get current arm positions
            bi = self.left_brazo_var.get()
            fi = self.left_frente_var.get()
            hi = self.left_high_var.get()
            pi = self.left_pollo_var.get() if hasattr(self, 'left_pollo_var') else 90
            bd = self.right_brazo_var.get()
            fd = self.right_frente_var.get()
            hd = self.right_high_var.get()
            pd = self.right_pollo_var.get()

            # Get current neck positions
            lateral = self.cuello_lateral_var.get()
            inferior = self.cuello_inferior_var.get()
            superior = self.cuello_superior_var.get()

            # Update current movement
            if self.current_movement is None:
                self.current_movement = {
                    "id": self.movement_counter,
                    "name": f"Movement_{self.movement_counter}",
                    "actions": []
                }
                self.movement_counter += 1

            # Update the last BRAZOS action or create new one
            brazos_action = None
            for action in self.current_movement["actions"]:
                if action.get("command") == "BRAZOS":
                    brazos_action = action
                    break

            if brazos_action:
                brazos_action["parameters"] = {
                    "BI": bi, "BD": bd, "FI": fi, "FD": fd,
                    "HI": hi, "HD": hd, "PD": pd, "PI": pi
                }
                brazos_action["timestamp"] = time.time()
            else:
                # Create new BRAZOS action
                self.current_movement["actions"].append({
                    "command": "BRAZOS",
                    "parameters": {
                        "BI": bi, "BD": bd, "FI": fi, "FD": fd,
                        "HI": hi, "HD": hd, "PD": pd, "PI": pi
                    },
                    "duration": 1000,
                    "description": f"Arm movement {self.movement_counter}",
                    "timestamp": time.time()
                })
            
            # Always create new CUELLO action (like BRAZOS)
            self.current_movement["actions"].append({
                "command": "CUELLO",
                "parameters": {
                    "L": lateral, "I": inferior, "S": superior
                },
                "duration": 1000,
                "description": f"Captured Position {len(self.current_movement['actions']) + 1}",
                "timestamp": time.time()
            })
            print(f"➕ [CREATE] New neck action created: L={lateral}, I={inferior}, S={superior}")
            
            # Update sequence display
            self.update_sequence_display()
            
        except Exception as e:
            print(f"❌ Error updating current movement: {e}")
    
    def add_action_to_sequence(self, command, parameters, description):
        """Add an action to the current sequence"""
        try:
            if not self.is_recording:
                return
            
            # Ensure we have a current movement
            if self.current_movement is None:
                self.current_movement = {
                    "id": self.movement_counter,
                    "name": f"Movement_{self.movement_counter}",
                    "actions": []
                }
                self.movement_counter += 1
            
            # Add action to current movement
            action = {
                "command": command,
                "parameters": parameters,
                "duration": 1000,
                "description": description,
                "timestamp": time.time()
            }
            
            self.current_movement["actions"].append(action)
            
            # Update sequence display and movement buttons
            self.update_sequence_display()
            self.update_movement_buttons()
            
            print(f"✅ Added action to sequence: {command} - {description}")
            
        except Exception as e:
            print(f"❌ Error adding action to sequence: {e}")
    
    def update_sequence_display(self):
        """Update the sequence display"""
        try:
            if hasattr(self, 'positions_text'):
                # Clear current display
                self.positions_text.delete(1.0, tk.END)
                
                # Show current sequence info
                info = f"Sequence: {self.sequence_name.get()}\n"
                info += f"Title: {self.sequence_title.get()}\n"
                info += f"Recording: {'🔴 ON' if self.is_recording else '⭕ OFF'}\n"
                info += f"Movements recorded: {len(self.recorded_actions)}\n\n"
                
                # Show recorded movements
                if self.recorded_actions:
                    info += "📋 Recorded Movements:\n"
                    info += "=" * 40 + "\n\n"
                    
                    for i, movement in enumerate(self.recorded_actions):
                        info += f"Movement {i+1}: {movement['name']}\n"
                        info += f"Actions: {len(movement['actions'])}\n"
                        
                        for j, action in enumerate(movement['actions']):
                            info += f"  {j+1}. {action['command']}: {action['description']}\n"
                            info += f"     Parameters: {action['parameters']}\n"
                        info += "\n"
                
                # Show current movement if recording
                if self.current_movement and self.is_recording:
                    info += "🎬 Current Movement:\n"
                    info += "=" * 40 + "\n"
                    info += f"Name: {self.current_movement['name']}\n"
                    info += f"Actions: {len(self.current_movement['actions'])}\n"
                    
                    if self.current_movement['actions']:
                        info += "\nActions in current movement:\n"
                        for i, action in enumerate(self.current_movement['actions']):
                            info += f"  {i+1}. {action['command']}: {action['description']}\n"
                            info += f"     Parameters: {action['parameters']}\n"
                        info += "\n💡 Click '💾 Save Movement' to save this movement!"
                else:
                        info += "\n💡 Use robot controls and click '📍 Capture Position' to add actions\n"
                        info += "   Then click '💾 Save Movement' when ready\n"
                    
                        info += "\n"
                
                # Update position count
                if hasattr(self, 'position_count'):
                    total_actions = sum(len(movement['actions']) for movement in self.recorded_actions)
                    if self.current_movement:
                        total_actions += len(self.current_movement['actions'])
                    self.position_count.config(text=str(total_actions))
                
                self.positions_text.insert(1.0, info)
                
                    # Also refresh movement cards if the cards tab is active
                try:
                        current_tab = self.sequence_tabs.select()
                        if current_tab and "🎯" in str(current_tab):
                            self.refresh_movement_cards()
                except:
                        pass  # Ignore if tabs aren't initialized yet
                    
        except Exception as e:
            print(f"❌ Error updating sequence display: {e}")
    
    def save_current_movement(self):
        """Save the current movement to recorded actions"""
        try:
            if not self.is_recording:
                messagebox.showwarning("Warning", "Not recording. Start recording first.")
                return
            
            if not self.current_movement or not self.current_movement.get("actions"):
                messagebox.showwarning("Warning", "No actions in current movement to save.")
                return
            
            # Save current movement to recorded actions
            self.recorded_actions.append(self.current_movement.copy())
            
            # Create new movement for next actions
            self.current_movement = {
                "id": self.movement_counter,
                "name": f"Movement_{self.movement_counter}",
                "actions": []
            }
            self.movement_counter += 1
            
            # Update UI
            self.update_sequence_display()
            self.update_movement_buttons()

                # Refresh movement cards
            self.refresh_movement_cards()
            
            messagebox.showinfo("Success", 
                f"Movement saved successfully!\n\n"
                f"Actions saved: {len(self.recorded_actions[-1]['actions'])}\n"
                f"Total movements: {len(self.recorded_actions)}")
            
            print(f"✅ Movement saved with {len(self.recorded_actions[-1]['actions'])} actions")
            
        except Exception as e:
            print(f"❌ Error saving movement: {e}")
            messagebox.showerror("Error", f"Error saving movement: {e}")
    
    def delete_last_movement(self):
        """Delete the last recorded movement"""
        try:
            if not self.recorded_actions:
                messagebox.showwarning("Warning", "No movements to delete.")
                return
            
            # Get last movement info
            last_movement = self.recorded_actions[-1]
            action_count = len(last_movement.get("actions", []))
            
            # Confirm deletion
            result = messagebox.askyesno("Confirm Delete", 
                f"Are you sure you want to delete the last movement?\n\n"
                f"Movement: {last_movement.get('name', 'Unknown')}\n"
                f"Actions: {action_count}")
            
            if result:
                # Remove last movement
                deleted_movement = self.recorded_actions.pop()
                
                # Update UI
                self.update_sequence_display()
                self.update_movement_buttons()

                    # Refresh movement cards
                self.refresh_movement_cards()
                
                messagebox.showinfo("Success", 
                    f"Movement deleted successfully!\n\n"
                    f"Deleted: {deleted_movement.get('name', 'Unknown')}\n"
                    f"Remaining movements: {len(self.recorded_actions)}")
                
                print(f"✅ Deleted movement: {deleted_movement.get('name', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error deleting last movement: {e}")
            messagebox.showerror("Error", f"Error deleting last movement: {e}")
    
    def update_movement_buttons(self):
        """Update the state of movement control buttons"""
        try:
            # Save movement button - enabled if recording and has actions
            if self.is_recording and self.current_movement and self.current_movement.get("actions"):
                self.save_movement_btn.config(state="normal")
            else:
                self.save_movement_btn.config(state="disabled")
            
            # Delete last movement button - enabled if there are recorded movements
            if self.recorded_actions:
                self.delete_last_movement_btn.config(state="normal")
            else:
                self.delete_last_movement_btn.config(state="disabled")
                
        except Exception as e:
            print(f"❌ Error updating movement buttons: {e}")
    
    def capture_position(self):
        """Capture current robot position"""
        try:
            if not self.is_recording:
                messagebox.showwarning("Warning", "Not recording. Start recording first.")
                return
            
            # Get current arm positions
            bi = self.left_brazo_var.get()
            fi = self.left_frente_var.get()
            hi = self.left_high_var.get()
            bd = self.right_brazo_var.get()
            fd = self.right_frente_var.get()
            hd = self.right_high_var.get()
            pd = self.right_pollo_var.get()
            
            # Add BRAZOS action to current movement
            self.add_action_to_sequence("BRAZOS", {
                "BI": bi, "BD": bd, "FI": fi, "FD": fd, 
                "HI": hi, "HD": hd, "PD": pd
            }, f"Captured Position {len(self.current_movement['actions']) + 1}")
            
            # Update movement buttons
            self.update_movement_buttons()
            
            messagebox.showinfo("Success", "Position captured and added to sequence!")
            
        except Exception as e:
            print(f"❌ Error capturing position: {e}")
            messagebox.showerror("Error", f"Error capturing position: {e}")
            
    def play_sequence(self):
        """Play current sequence"""
        try:
            if not self.recorded_actions:
                messagebox.showwarning("Warning", "No sequence to play. Record some actions first.")
                return
            
            if not self.esp32_connected:
                messagebox.showwarning("Warning", "Please connect to ESP32 first before playing.")
                return
            
            self.is_playing = True
            self.playback_status.config(text="▶️ Playing", fg='#4CAF50')
            self.play_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.stop_button.config(state="normal")
            
            # Start playback in a separate thread
            playback_thread = threading.Thread(target=self._playback_thread)
            playback_thread.daemon = True
            playback_thread.start()
            
        except Exception as e:
            print(f"❌ Error playing sequence: {e}")
            messagebox.showerror("Error", f"Error playing sequence: {e}")
    
    def _playback_thread(self):
        """Playback thread"""
        try:
            for movement in self.recorded_actions:
                if not self.is_playing:
                    break
                
                for action in movement['actions']:
                    if not self.is_playing:
                        break
                    
                    # Execute action
                    self._execute_action(action)
                    
                    # Wait between actions
                    time.sleep(1.0)
                
                # Wait between movements
                time.sleep(2.0)
            
            # Playback finished
            self.is_playing = False
            self.playback_status.config(text="⏹️ Stopped", fg='#888888')
            self.play_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            
        except Exception as e:
            print(f"❌ Error in playback thread: {e}")
    
    def _execute_action(self, action):
        """Execute a single action"""
        try:
            command = action.get('command', '')
            parameters = action.get('parameters', {})
            
            if command == 'BRAZOS':
                bi = parameters.get('BI', 0)
                bd = parameters.get('BD', 0)
                fi = parameters.get('FI', 0)
                fd = parameters.get('FD', 0)
                hi = parameters.get('HI', 0)
                hd = parameters.get('HD', 0)
                pd = parameters.get('PD', 0)
                
                if self.esp32_client:
                    self.esp32_client.send_movement(bi, bd, fi, fd, hi, hd, pd)
            
            elif command == 'MANO':
                mano = parameters.get('M', '')
                gesto = parameters.get('GESTO', '')
                dedo = parameters.get('DEDO', '')
                angulo = parameters.get('ANG', 0)
                
                if self.esp32_client:
                    if gesto:
                        self.esp32_client.send_gesture(mano, gesto)
                    elif dedo:
                        self.esp32_client.send_finger_control(mano, dedo, angulo)
            
            elif command == 'MUNECA':
                # Handle wrist movements with new relative positioning system
                mano = parameters.get('mano', '')
                angulo = parameters.get('angulo', 80)
                
                if self.esp32_client:
                    # Send wrist control command to ESP32
                    self.esp32_client.send_wrist_control(mano, angulo)
                    print(f"🎯 Executing wrist command: {mano} wrist to {angulo}°")
            
            elif command == 'CUELLO':
                l = parameters.get('L', 0)
                i = parameters.get('I', 0)
                s = parameters.get('S', 0)
                
                if self.esp32_client:
                    self.esp32_client.send_neck_movement(l, i, s)
            
            elif command == 'HABLAR':
                texto = parameters.get('texto', '')
                
                if self.esp32_client:
                    self.esp32_client.send_speech(texto)
                    
        except Exception as e:
            print(f"❌ Error executing action: {e}")
            
    def pause_sequence(self):
        """Pause sequence playback"""
        try:
            self.is_playing = False
            self.playback_status.config(text="⏸️ Paused", fg='#FF9800')
            self.play_button.config(state="normal")
            self.pause_button.config(state="disabled")
            
        except Exception as e:
            print(f"❌ Error pausing sequence: {e}")
            
    def stop_sequence(self):
        """Stop sequence playback"""
        try:
            self.is_playing = False
            self.playback_status.config(text="⏹️ Stopped", fg='#888888')
            self.play_button.config(state="normal")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            
        except Exception as e:
            print(f"❌ Error stopping sequence: {e}")
            
    def save_sequence(self):
        """Save current sequence"""
        try:
            # Check if there are any recorded actions
            total_actions = len(self.recorded_actions)
            
            # Also check if there's a current movement with actions
            current_actions = 0
            if self.current_movement and self.current_movement.get("actions"):
                current_actions = len(self.current_movement["actions"])
            
            if total_actions == 0 and current_actions == 0:
                messagebox.showwarning("Warning", 
                    "No sequence to save. Please record some actions first.\n\n"
                    "To record actions:\n"
                    "1. Connect to ESP32 or enable Debug Mode\n"
                    "2. Click 'Start Recording'\n"
                    "3. Use the robot controls to create movements\n"
                    "4. Click 'Stop Recording'")
                return
            
            # If there's a current movement with actions, add it to recorded actions
            if self.current_movement and self.current_movement.get("actions") and self.is_recording:
                self.recorded_actions.append(self.current_movement.copy())
                print(f"✅ Added current movement with {len(self.current_movement['actions'])} actions to recorded actions")
            
            # Create sequence data
            sequence_data = {
                "name": self.sequence_name.get(),
                "title": self.sequence_title.get(),
                "created_at": datetime.datetime.now().isoformat(),
                "movements": self.recorded_actions.copy(),
                "total_movements": len(self.recorded_actions),
                "total_actions": sum(len(movement.get("actions", [])) for movement in self.recorded_actions)
            }
            
            # Ask for filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"{self.sequence_name.get()}.json"
            )
            
            if filename:
                # Save to file
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(sequence_data, f, indent=2, ensure_ascii=False)
                
                # Add to listbox if not already present
                sequence_name = self.sequence_name.get()
                existing_items = list(self.sequence_listbox.get(0, tk.END))
                if sequence_name not in existing_items:
                    self.sequence_listbox.insert(tk.END, sequence_name)
                
                messagebox.showinfo("Success", 
                    f"Sequence saved successfully!\n\n"
                    f"File: {filename}\n"
                    f"Movements: {sequence_data['total_movements']}\n"
                    f"Total Actions: {sequence_data['total_actions']}")
                print(f"✅ Sequence saved: {filename}")
                
        except Exception as e:
            print(f"❌ Error saving sequence: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", 
                f"Error saving sequence:\n\n{str(e)}\n\n"
                f"Please check:\n"
                f"1. You have write permissions in the selected directory\n"
                f"2. The filename is valid\n"
                f"3. There are recorded actions to save")
            
    def load_sequence(self):
        """Load selected sequence"""
        try:
            # Ask for filename
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Sequence"
            )
            
            if filename:
                # Load from file
                with open(filename, 'r', encoding='utf-8') as f:
                    sequence_data = json.load(f)
                
                # Update sequence info
                self.sequence_name.set(sequence_data.get("name", "Loaded_Sequence"))
                self.sequence_title.set(sequence_data.get("title", "Loaded Sequence"))
                
                # Load movements
                self.recorded_actions = sequence_data.get("movements", [])
                
                # Update display
                self.update_sequence_display()
                
                messagebox.showinfo("Success", f"Sequence loaded: {filename}")
                print(f"✅ Sequence loaded: {filename}")
                
        except Exception as e:
            print(f"❌ Error loading sequence: {e}")
            messagebox.showerror("Error", f"Error loading sequence: {e}")
                
    def delete_sequence(self):
        """Delete selected sequence"""
        try:
            selection = self.sequence_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a sequence to delete")
                return
            
                seq_name = self.sequence_listbox.get(selection[0])
            
            # Confirm deletion
            result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{seq_name}'?")
            
            if result:
                self.sequence_listbox.delete(selection[0])
                print(f"✅ Deleted sequence: {seq_name}")
                
        except Exception as e:
            print(f"❌ Error deleting sequence: {e}")
            messagebox.showerror("Error", f"Error deleting sequence: {e}")
    
    def create_sample_sequence(self):
        """Create a sample sequence for testing"""
        try:
            # Create a sample movement
            sample_movement = {
                "id": 1,
                "name": "Sample_Movement_1",
                "actions": [
                    {
                        "command": "BRAZOS",
                        "parameters": {
                            "BI": 10, "BD": 40, "FI": 80, "FD": 90, 
                            "HI": 80, "HD": 80, "PD": 45
                        },
                        "duration": 1000,
                        "description": "Home Position",
                        "timestamp": time.time()
                    },
                    {
                        "command": "MUNECA",
                        "parameters": {
                            "mano": "derecha",
                            "angulo": 80
                        },
                        "duration": 1000,
                        "description": "Right Wrist to 80° (Rest Position)",
                        "timestamp": time.time()
                    },
                    {
                        "command": "MUNECA",
                        "parameters": {
                            "mano": "derecha",
                            "angulo": 120
                        },
                        "duration": 1000,
                        "description": "Right Wrist to 120° (Relative Movement)",
                        "timestamp": time.time()
                    },
                    {
                        "command": "MANO",
                        "parameters": {
                            "M": "derecha",
                            "GESTO": "SALUDO"
                        },
                        "duration": 1000,
                        "description": "Wave Gesture",
                        "timestamp": time.time()
                    },
                    {
                        "command": "HABLAR",
                        "parameters": {
                            "texto": "Hello students! This is a sample sequence with wrist movements."
                        },
                        "duration": 2000,
                        "description": "Sample Speech",
                        "timestamp": time.time()
                    }
                ]
            }
            
            # Add to recorded actions
            self.recorded_actions.append(sample_movement)
            
            # Update sequence name
            self.sequence_name.set("Sample_Sequence")
            self.sequence_title.set("Sample Sequence")
            
            # Update display
            self.update_sequence_display()
            
            messagebox.showinfo("Sample Sequence Created", 
                "A sample sequence has been created!\n\n"
                "This sequence includes:\n"
                "- Home position movement\n"
                "- Right wrist to 80° (rest position)\n"
                "- Right wrist to 120° (relative movement)\n"
                "- Wave gesture\n"
                "- Sample speech\n\n"
                "You can now save this sequence or modify it.")
            
            print("✅ Sample sequence created successfully")
            
        except Exception as e:
            print(f"❌ Error creating sample sequence: {e}")
            messagebox.showerror("Error", f"Error creating sample sequence: {e}")
    
    def log_message(self, message):
        """Log a message"""
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
        except Exception as e:
            print(f"Error logging message: {e}")
