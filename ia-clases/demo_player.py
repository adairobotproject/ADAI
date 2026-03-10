#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Player - Executes demos with sequences synchronized to PDF pages
"""

import os
import time
import threading
import cv2
import numpy as np
import fitz  # PyMuPDF
from typing import Optional, Callable
import json

class DemoPlayer:
    """Plays demos with sequences synchronized to PDF pages"""
    
    def __init__(self, demo_manager=None, sequence_executor=None):
        """
        Initialize the Demo Player
        
        Args:
            demo_manager: DemoSequenceManager instance
            sequence_executor: Function to execute sequences
        """
        self.demo_manager = demo_manager
        self.sequence_executor = sequence_executor
        
        # Player state
        self.is_playing = False
        self.current_demo = None
        self.current_page = 0
        self.total_pages = 0
        self.stop_flag = False
        
        # Callbacks
        self.on_page_change = None
        self.on_sequence_start = None
        self.on_sequence_end = None
        self.on_demo_complete = None
        self.on_error = None
        
        print("🎬 Demo Player inicializado")
    
    def set_callbacks(self, page_change=None, sequence_start=None, sequence_end=None, 
                     demo_complete=None, error=None):
        """Set callback functions"""
        self.on_page_change = page_change
        self.on_sequence_start = sequence_start
        self.on_sequence_end = sequence_end
        self.on_demo_complete = demo_complete
        self.on_error = error
    
    def play_demo(self, demo_name: str, start_page: int = 0) -> bool:
        """
        Play a demo with sequences
        
        Args:
            demo_name: Name of the demo to play
            start_page: Page to start from (0-based)
            
        Returns:
            bool: True if demo started successfully
        """
        try:
            if not self.demo_manager:
                self._call_error("Demo Manager no disponible")
                return False
            
            # Get demo info
            demo_info = self.demo_manager.get_demo_info(demo_name)
            if not demo_info:
                self._call_error(f"Demo '{demo_name}' no encontrado")
                return False
            
            # Check if PDF exists
            pdf_path = demo_info['pdf_path']
            if not os.path.exists(pdf_path):
                self._call_error(f"PDF no encontrado: {pdf_path}")
                return False
            
            # Initialize player state
            self.current_demo = demo_name
            self.current_page = start_page
            self.total_pages = demo_info['page_count']
            self.stop_flag = False
            self.is_playing = True
            
            print(f"🎬 Iniciando demo: {demo_name}")
            print(f"   📄 Páginas: {self.total_pages}")
            print(f"   🚀 Página inicial: {start_page}")
            
            # Start demo in separate thread
            demo_thread = threading.Thread(target=self._play_demo_thread, 
                                         args=(demo_info,), daemon=True)
            demo_thread.start()
            
            return True
            
        except Exception as e:
            self._call_error(f"Error iniciando demo: {e}")
            return False
    
    def _play_demo_thread(self, demo_info):
        """Main demo playback thread"""
        try:
            pdf_path = demo_info['pdf_path']
            page_sequences = demo_info['page_sequences']
            sequence_timing = demo_info['sequence_timing']
            
            # Open PDF
            with fitz.open(pdf_path) as doc:
                print(f"📚 PDF abierto: {len(doc)} páginas")
                
                # Play each page
                for page_num in range(self.current_page, self.total_pages):
                    if self.stop_flag:
                        print("⏹️ Demo detenido por el usuario")
                        break
                    
                    print(f"📄 Reproduciendo página {page_num + 1}/{self.total_pages}")
                    
                    # Update current page
                    self.current_page = page_num
                    self._call_page_change(page_num, self.total_pages)
                    
                    # Get page sequence
                    sequence_info = self.demo_manager.get_page_sequence(
                        self.current_demo, page_num)
                    
                    # Show PDF page
                    self._show_pdf_page(doc, page_num)
                    
                    # Execute sequence if assigned
                    if sequence_info:
                        sequence_name, timing = sequence_info
                        self._execute_page_sequence(sequence_name, timing)
                    else:
                        # No sequence, just wait
                        time.sleep(sequence_timing.get(str(page_num), 5.0))
                    
                    # Small pause between pages
                    time.sleep(0.5)
                
                # Demo completed
                self.is_playing = False
                self._call_demo_complete()
                print("✅ Demo completado")
                
        except Exception as e:
            self.is_playing = False
            self._call_error(f"Error en demo: {e}")
            print(f"❌ Error en demo: {e}")
    
    def _show_pdf_page(self, doc, page_num):
        """Show PDF page in OpenCV window"""
        try:
            # Get page
            page = doc[page_num]
            
            # Convert page to image
            pix = page.get_pixmap()
            img_data = np.frombuffer(pix.samples, dtype=np.uint8)
            img = img_data.reshape((pix.h, pix.w, pix.n))
            
            # Convert to BGR for OpenCV
            if pix.n == 4:  # RGBA
                img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:  # RGB
                img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            else:  # Grayscale
                img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
            # Create window and show page
            cv2.namedWindow("Demo PDF", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Demo PDF", 800, 600)
            cv2.imshow("Demo PDF", img_bgr)
            cv2.waitKey(100)  # Small delay to show the page
            
        except Exception as e:
            print(f"⚠️ Error mostrando página PDF: {e}")
    
    def _execute_page_sequence(self, sequence_name: str, timing: float):
        """Execute sequence for current page"""
        try:
            print(f"🎯 Ejecutando secuencia: {sequence_name}")
            self._call_sequence_start(sequence_name)
            
            if self.sequence_executor:
                # Execute sequence using provided executor
                success = self.sequence_executor(sequence_name)
                if not success:
                    print(f"⚠️ Error ejecutando secuencia: {sequence_name}")
            else:
                # Simulate sequence execution
                print(f"⏱️ Simulando secuencia por {timing} segundos...")
                time.sleep(timing)
            
            self._call_sequence_end(sequence_name)
            print(f"✅ Secuencia completada: {sequence_name}")
            
        except Exception as e:
            print(f"❌ Error ejecutando secuencia: {e}")
            self._call_sequence_end(sequence_name, error=str(e))
    
    def stop_demo(self):
        """Stop current demo"""
        if self.is_playing:
            self.stop_flag = True
            self.is_playing = False
            print("⏹️ Deteniendo demo...")
            
            # Close PDF window
            try:
                cv2.destroyWindow("Demo PDF")
            except:
                pass
    
    def pause_demo(self):
        """Pause current demo (placeholder for future implementation)"""
        print("⏸️ Pausando demo (no implementado aún)")
    
    def resume_demo(self):
        """Resume current demo (placeholder for future implementation)"""
        print("▶️ Resumiendo demo (no implementado aún)")
    
    def get_current_status(self) -> dict:
        """Get current demo status"""
        return {
            'is_playing': self.is_playing,
            'current_demo': self.current_demo,
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'stop_flag': self.stop_flag
        }
    
    def _call_page_change(self, page_num, total_pages):
        """Call page change callback"""
        if self.on_page_change:
            try:
                self.on_page_change(page_num, total_pages)
            except Exception as e:
                print(f"⚠️ Error en callback page_change: {e}")
    
    def _call_sequence_start(self, sequence_name):
        """Call sequence start callback"""
        if self.on_sequence_start:
            try:
                self.on_sequence_start(sequence_name)
            except Exception as e:
                print(f"⚠️ Error en callback sequence_start: {e}")
    
    def _call_sequence_end(self, sequence_name, error=None):
        """Call sequence end callback"""
        if self.on_sequence_end:
            try:
                self.on_sequence_end(sequence_name, error)
            except Exception as e:
                print(f"⚠️ Error en callback sequence_end: {e}")
    
    def _call_demo_complete(self):
        """Call demo complete callback"""
        if self.on_demo_complete:
            try:
                self.on_demo_complete()
            except Exception as e:
                print(f"⚠️ Error en callback demo_complete: {e}")
    
    def _call_error(self, error_msg):
        """Call error callback"""
        if self.on_error:
            try:
                self.on_error(error_msg)
            except Exception as e:
                print(f"⚠️ Error en callback error: {e}")
        print(f"❌ {error_msg}")

# Global instance
_demo_player = None

def get_demo_player(demo_manager=None, sequence_executor=None) -> DemoPlayer:
    """Get global demo player instance"""
    global _demo_player
    if _demo_player is None:
        _demo_player = DemoPlayer(demo_manager, sequence_executor)
    return _demo_player
