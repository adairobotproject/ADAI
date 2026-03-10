#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Sequence Manager - Manages sequences associated with PDF demo pages
"""

import os
import json
import time
import datetime
from typing import Dict, List, Optional, Tuple
import fitz  # PyMuPDF

class DemoSequenceManager:
    """Manages sequences associated with PDF demo pages"""
    
    def __init__(self, sequences_dir: str = "sequences", demos_dir: str = "demos"):
        """
        Initialize the Demo Sequence Manager
        
        Args:
            sequences_dir: Directory containing saved sequences
            demos_dir: Directory containing demo configurations
        """
        self.sequences_dir = sequences_dir
        self.demos_dir = demos_dir
        
        # Create directories if they don't exist
        os.makedirs(self.sequences_dir, exist_ok=True)
        os.makedirs(self.demos_dir, exist_ok=True)
        
        # Load available sequences
        self.available_sequences = self.load_available_sequences()
        
        # Demo configurations
        self.demo_configs = {}
        self.load_demo_configs()
        
        print(f"🎬 Demo Sequence Manager inicializado")
        print(f"   📁 Sequences: {self.sequences_dir}")
        print(f"   📁 Demos: {self.demos_dir}")
        print(f"   📋 Sequences disponibles: {len(self.available_sequences)}")
    
    def load_available_sequences(self) -> Dict[str, str]:
        """Load all available sequences from the sequences directory"""
        sequences = {}
        
        try:
            if not os.path.exists(self.sequences_dir):
                return sequences
            
            for filename in os.listdir(self.sequences_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.sequences_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            sequence_data = json.load(f)
                        
                        sequence_name = sequence_data.get('name', filename.replace('.json', ''))
                        sequences[sequence_name] = filepath
                        
                    except Exception as e:
                        print(f"⚠️ Error loading sequence {filename}: {e}")
                        continue
            
            print(f"✅ Cargadas {len(sequences)} secuencias disponibles")
            
        except Exception as e:
            print(f"❌ Error loading sequences: {e}")
        
        return sequences
    
    def load_demo_configs(self):
        """Load all demo configurations"""
        try:
            config_file = os.path.join(self.demos_dir, "demo_configs.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.demo_configs = json.load(f)
                print(f"✅ Cargadas {len(self.demo_configs)} configuraciones de demo")
            else:
                self.demo_configs = {}
                print("📝 No hay configuraciones de demo existentes")
                
        except Exception as e:
            print(f"❌ Error loading demo configs: {e}")
            self.demo_configs = {}
    
    def save_demo_configs(self):
        """Save demo configurations to file"""
        try:
            config_file = os.path.join(self.demos_dir, "demo_configs.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.demo_configs, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuraciones de demo guardadas")
            
        except Exception as e:
            print(f"❌ Error saving demo configs: {e}")
    
    def create_demo_config(self, demo_name: str, pdf_path: str, title: str = "", 
                          description: str = "") -> bool:
        """
        Create a new demo configuration
        
        Args:
            demo_name: Name of the demo
            pdf_path: Path to the PDF file
            title: Demo title
            description: Demo description
            
        Returns:
            bool: True if created successfully
        """
        try:
            # Verify PDF exists and get page count
            if not os.path.exists(pdf_path):
                print(f"❌ PDF no encontrado: {pdf_path}")
                return False
            
            with fitz.open(pdf_path) as doc:
                page_count = len(doc)
            
            # Create demo configuration
            demo_config = {
                "name": demo_name,
                "title": title or demo_name,
                "description": description,
                "pdf_path": pdf_path,
                "page_count": page_count,
                "created_at": datetime.datetime.now().isoformat(),
                "page_sequences": {},  # Will store page -> sequence mappings
                "sequence_timing": {}  # Will store timing for each sequence
            }
            
            # Initialize page sequences (empty for now)
            for page_num in range(page_count):
                demo_config["page_sequences"][str(page_num)] = None
                demo_config["sequence_timing"][str(page_num)] = 5.0  # Default 5 seconds
            
            # Save configuration
            self.demo_configs[demo_name] = demo_config
            self.save_demo_configs()
            
            print(f"✅ Demo configurado: {demo_name} ({page_count} páginas)")
            return True
            
        except Exception as e:
            print(f"❌ Error creating demo config: {e}")
            return False
    
    def assign_sequence_to_page(self, demo_name: str, page_num: int, 
                               sequence_name: str, timing: float = 5.0) -> bool:
        """
        Assign a sequence to a specific page
        
        Args:
            demo_name: Name of the demo
            page_num: Page number (0-based)
            sequence_name: Name of the sequence to assign
            timing: How long to show the page (seconds)
            
        Returns:
            bool: True if assigned successfully
        """
        try:
            if demo_name not in self.demo_configs:
                print(f"❌ Demo no encontrado: {demo_name}")
                return False
            
            if sequence_name not in self.available_sequences:
                print(f"❌ Sequence no encontrada: {sequence_name}")
                print(f"📋 Sequences disponibles: {list(self.available_sequences.keys())}")
                return False
            
            demo_config = self.demo_configs[demo_name]
            page_count = demo_config["page_count"]
            
            if page_num < 0 or page_num >= page_count:
                print(f"❌ Número de página inválido: {page_num} (0-{page_count-1})")
                return False
            
            # Assign sequence to page
            demo_config["page_sequences"][str(page_num)] = sequence_name
            demo_config["sequence_timing"][str(page_num)] = timing
            
            # Save configuration
            self.save_demo_configs()
            
            print(f"✅ Sequence '{sequence_name}' asignada a página {page_num} de '{demo_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error assigning sequence: {e}")
            return False
    
    def remove_sequence_from_page(self, demo_name: str, page_num: int) -> bool:
        """
        Remove sequence assignment from a page
        
        Args:
            demo_name: Name of the demo
            page_num: Page number (0-based)
            
        Returns:
            bool: True if removed successfully
        """
        try:
            if demo_name not in self.demo_configs:
                print(f"❌ Demo no encontrado: {demo_name}")
                return False
            
            demo_config = self.demo_configs[demo_name]
            page_count = demo_config["page_count"]
            
            if page_num < 0 or page_num >= page_count:
                print(f"❌ Número de página inválido: {page_num}")
                return False
            
            # Remove sequence from page
            demo_config["page_sequences"][str(page_num)] = None
            demo_config["sequence_timing"][str(page_num)] = 5.0
            
            # Save configuration
            self.save_demo_configs()
            
            print(f"✅ Sequence removida de página {page_num} de '{demo_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error removing sequence: {e}")
            return False
    
    def get_demo_info(self, demo_name: str) -> Optional[Dict]:
        """Get information about a demo"""
        return self.demo_configs.get(demo_name)
    
    def get_page_sequence(self, demo_name: str, page_num: int) -> Optional[Tuple[str, float]]:
        """
        Get sequence assigned to a specific page
        
        Returns:
            Tuple[sequence_name, timing] or None if no sequence assigned
        """
        try:
            if demo_name not in self.demo_configs:
                return None
            
            demo_config = self.demo_configs[demo_name]
            page_sequences = demo_config["page_sequences"]
            sequence_timing = demo_config["sequence_timing"]
            
            sequence_name = page_sequences.get(str(page_num))
            timing = sequence_timing.get(str(page_num), 5.0)
            
            if sequence_name:
                return (sequence_name, timing)
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error getting page sequence: {e}")
            return None
    
    def load_sequence_data(self, sequence_name: str) -> Optional[Dict]:
        """Load sequence data from file"""
        try:
            if sequence_name not in self.available_sequences:
                return None
            
            filepath = self.available_sequences[sequence_name]
            with open(filepath, 'r', encoding='utf-8') as f:
                sequence_data = json.load(f)
            
            return sequence_data
            
        except Exception as e:
            print(f"❌ Error loading sequence data: {e}")
            return None
    
    def get_available_demos(self) -> List[str]:
        """Get list of available demos"""
        return list(self.demo_configs.keys())
    
    def delete_demo(self, demo_name: str) -> bool:
        """Delete a demo configuration"""
        try:
            if demo_name not in self.demo_configs:
                print(f"❌ Demo no encontrado: {demo_name}")
                return False
            
            del self.demo_configs[demo_name]
            self.save_demo_configs()
            
            print(f"✅ Demo eliminado: {demo_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting demo: {e}")
            return False
    
    def refresh_sequences(self):
        """Refresh available sequences list"""
        self.available_sequences = self.load_available_sequences()
        print(f"🔄 Sequences actualizadas: {len(self.available_sequences)} disponibles")

# Global instance
_demo_sequence_manager = None

def get_demo_sequence_manager() -> DemoSequenceManager:
    """Get global demo sequence manager instance"""
    global _demo_sequence_manager
    if _demo_sequence_manager is None:
        _demo_sequence_manager = DemoSequenceManager()
    return _demo_sequence_manager
