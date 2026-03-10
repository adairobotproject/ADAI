#!/usr/bin/env python3
"""
ESP32 Connector for Robot GUI
============================

Connector to communicate with ESP32 robot controller via HTTP.
Supports control of arms, neck, hands, fingers, and wrists.
"""

import requests
import json
import time
import threading
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin

@dataclass
class ESP32Config:
    """Configuration for ESP32 connection"""
    host: str = "192.168.1.100"  # Default ESP32 IP
    port: int = 80
    timeout: float = 2.0
    retry_attempts: int = 3
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

class ESP32Connector:
    """Connector to ESP32 robot controller"""
    
    def __init__(self, config: ESP32Config):
        self.config = config
        self.connected = False
        self.last_response = ""
        self.error_count = 0
        self.status_thread = None
        self.running = False
        
        # Robot state tracking
        self.arm_positions = {
            'brazo_izq': 100, 'frente_izq': 95,
            'brazo_der': 30, 'frente_der': 160
        }
        self.neck_positions = {
            'lateral': 155, 'inferior': 95, 'superior': 105
        }
        self.hand_positions = {
            'derecha': [0, 0, 0, 0, 0],  # 5 fingers
            'izquierda': [0, 0, 0, 0, 0]  # 5 fingers
        }
        self.wrist_positions = {
            'derecha': 80, 'izquierda': 80
        }
        
        # Safety limits (from ESP32 code)
        self.arm_limits = {
            'brazo_izq': (0, 40), 'frente_izq': (60, 120),
            'brazo_der': (0, 40), 'frente_der': (70, 110)
        }
        self.neck_limits = {
            'lateral': (120, 190), 'inferior': (60, 130), 'superior': (90, 120)
        }
        self.hand_limits = (0, 180)
        self.wrist_limits = (0, 160)
    
    def connect(self) -> Tuple[bool, str]:
        """Test connection to ESP32"""
        try:
            response = requests.get(
                urljoin(self.config.base_url, "/"),
                timeout=self.config.timeout
            )
            if response.status_code == 200:
                self.connected = True
                self.error_count = 0
                return True, "Connected to ESP32"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            self.connected = False
            return False, f"Connection failed: {str(e)}"
    
    def disconnect(self):
        """Disconnect from ESP32"""
        self.connected = False
        self.running = False
        if self.status_thread and self.status_thread.is_alive():
            self.status_thread.join(timeout=1.0)
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     data: Optional[Dict] = None) -> Tuple[bool, str]:
        """Make HTTP request to ESP32"""
        if not self.connected:
            return False, "Not connected to ESP32"
        
        url = urljoin(self.config.base_url, endpoint)
        
        for attempt in range(self.config.retry_attempts):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, timeout=self.config.timeout)
                elif method.upper() == "POST":
                    response = requests.post(
                        url, 
                        data=data, 
                        timeout=self.config.timeout,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'}
                    )
                else:
                    return False, f"Unsupported method: {method}"
                
                if response.status_code == 200:
                    self.last_response = response.text
                    return True, response.text
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.config.retry_attempts - 1:
                    self.error_count += 1
                    return False, f"Request failed: {str(e)}"
                time.sleep(0.1)  # Brief delay before retry
        
        return False, "Max retry attempts reached"
    
    def send_http_post(self, endpoint: str, data: Dict) -> bool:
        """Send HTTP POST request to ESP32"""
        try:
            url = urljoin(self.config.base_url, endpoint)
            response = requests.post(
                url,
                data=data,
                timeout=self.config.timeout,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                self.last_response = response.text
                return True
            else:
                self.error_count += 1
                self.last_response = f"HTTP {response.status_code}: {response.text}"
                return False
                
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            self.last_response = f"Request failed: {str(e)}"
            return False
            try:
                if method.upper() == "GET":
                    response = requests.get(url, timeout=self.config.timeout)
                elif method.upper() == "POST":
                    response = requests.post(
                        url, 
                        data=data,
                        timeout=self.config.timeout,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'}
                    )
                else:
                    return False, f"Unsupported method: {method}"
                
                if response.status_code == 200:
                    self.last_response = response.text
                    self.error_count = 0
                    return True, response.text
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.config.retry_attempts - 1:
                    self.error_count += 1
                    return False, f"Request failed: {str(e)}"
                time.sleep(0.1)
        
        return False, "Max retry attempts reached"
    
    # ===== ARM CONTROL =====
    
    def move_arms(self, bi: int, fi: int, bd: int, fd: int) -> Tuple[bool, str]:
        """Move robot arms to specified positions"""
        # Validate positions
        if not self._validate_arm_position('brazo_izq', bi):
            return False, f"Brazo izquierdo out of range: {bi}"
        if not self._validate_arm_position('frente_izq', fi):
            return False, f"Frente izquierdo out of range: {fi}"
        if not self._validate_arm_position('brazo_der', bd):
            return False, f"Brazo derecho out of range: {bd}"
        if not self._validate_arm_position('frente_der', fd):
            return False, f"Frente derecho out of range: {fd}"
        
        data = {
            'bi': str(bi),
            'fi': str(fi),
            'bd': str(bd),
            'fd': str(fd)
        }
        
        success, response = self._make_request("/brazos/mover", "POST", data)
        if success:
            # Update local state
            self.arm_positions['brazo_izq'] = bi
            self.arm_positions['frente_izq'] = fi
            self.arm_positions['brazo_der'] = bd
            self.arm_positions['frente_der'] = fd
        
        return success, response
    
    def move_arm_arrow(self, arm_index: int, direction: int) -> Tuple[bool, str]:
        """Move arm using arrow controls (increment/decrement)"""
        arm_names = ['brazo_izq', 'frente_izq', 'brazo_der', 'frente_der']
        if arm_index < 0 or arm_index >= len(arm_names):
            return False, f"Invalid arm index: {arm_index}"
        
        arm_name = arm_names[arm_index]
        current_pos = self.arm_positions[arm_name]
        new_pos = current_pos + (direction * 5)  # 5 degree increments
        
        # Validate new position
        if not self._validate_arm_position(arm_name, new_pos):
            return False, f"Position out of range: {new_pos}"
        
        data = {
            'indice': str(arm_index),
            'direccion': str(direction)
        }
        
        success, response = self._make_request("/brazos/flecha", "POST", data)
        if success:
            self.arm_positions[arm_name] = new_pos
        
        return success, response
    
    def arms_rest_position(self) -> Tuple[bool, str]:
        """Move arms to rest position"""
        success, response = self._make_request("/brazos/descanso")
        if success:
            # Update to rest positions
            self.arm_positions = {
                'brazo_izq': 100, 'frente_izq': 95,
                'brazo_der': 30, 'frente_der': 160
            }
        return success, response
    
    def arms_salute(self) -> Tuple[bool, str]:
        """Perform salute gesture"""
        return self._make_request("/brazos/saludo")
    
    def arms_hug(self) -> Tuple[bool, str]:
        """Perform hug gesture"""
        return self._make_request("/brazos/abrazar")
    
    # ===== NECK CONTROL =====
    
    def move_neck(self, lateral: int, inferior: int, superior: int) -> Tuple[bool, str]:
        """Move robot neck to specified positions"""
        # Validate positions
        if not self._validate_neck_position('lateral', lateral):
            return False, f"Lateral out of range: {lateral}"
        if not self._validate_neck_position('inferior', inferior):
            return False, f"Inferior out of range: {inferior}"
        if not self._validate_neck_position('superior', superior):
            return False, f"Superior out of range: {superior}"
        
        data = {
            'lateral': str(lateral),
            'inferior': str(inferior),
            'superior': str(superior)
        }
        
        success, response = self._make_request("/cuello/mover", "POST", data)
        if success:
            # Update local state
            self.neck_positions['lateral'] = lateral
            self.neck_positions['inferior'] = inferior
            self.neck_positions['superior'] = superior
        
        return success, response
    
    def move_neck_arrow(self, neck_index: int, direction: int) -> Tuple[bool, str]:
        """Move neck using arrow controls"""
        neck_names = ['lateral', 'inferior', 'superior']
        if neck_index < 0 or neck_index >= len(neck_names):
            return False, f"Invalid neck index: {neck_index}"
        
        neck_name = neck_names[neck_index]
        current_pos = self.neck_positions[neck_name]
        new_pos = current_pos + (direction * 5)  # 5 degree increments
        
        # Validate new position
        if not self._validate_neck_position(neck_name, new_pos):
            return False, f"Position out of range: {new_pos}"
        
        data = {
            'indice': str(neck_index),
            'direccion': str(direction)
        }
        
        success, response = self._make_request("/cuello/flecha", "POST", data)
        if success:
            self.neck_positions[neck_name] = new_pos
        
        return success, response
    
    def neck_center(self) -> Tuple[bool, str]:
        """Center neck position"""
        success, response = self._make_request("/cuello/centrar")
        if success:
            self.neck_positions = {'lateral': 155, 'inferior': 95, 'superior': 105}
        return success, response
    
    def neck_random(self) -> Tuple[bool, str]:
        """Move neck to random position"""
        return self._make_request("/cuello/aleatorio")
    
    def neck_yes(self) -> Tuple[bool, str]:
        """Perform 'yes' gesture (up-down)"""
        return self._make_request("/cuello/si")
    
    def neck_no(self) -> Tuple[bool, str]:
        """Perform 'no' gesture (left-right)"""
        return self._make_request("/cuello/no")
    
    # ===== HAND CONTROL =====
    
    def hand_gesture(self, hand: str, gesture: str) -> Tuple[bool, str]:
        """Perform hand gesture"""
        valid_gestures = ['paz', 'rock', 'ok', 'senalar', 'abrir', 'cerrar']
        if gesture not in valid_gestures:
            return False, f"Invalid gesture: {gesture}"
        
        data = {
            'mano': hand,
            'gesto': gesture
        }
        
        return self._make_request("/manos/gesto", "POST", data)
    
    def move_finger(self, hand: str, finger: str, angle: int) -> Tuple[bool, str]:
        """Move specific finger to angle"""
        if not self._validate_hand_position(angle):
            return False, f"Angle out of range: {angle}"
        
        data = {
            'mano': hand,
            'dedo': finger,
            'angulo': str(angle)
        }
        
        success, response = self._make_request("/manos/dedo", "POST", data)
        if success:
            # Update local state
            finger_index = self._get_finger_index(finger)
            if finger_index >= 0:
                if hand == 'derecha':
                    self.hand_positions['derecha'][finger_index] = angle
                else:
                    self.hand_positions['izquierda'][finger_index] = angle
        
        return success, response
    
    def move_finger_arrow(self, finger_index: int, direction: int) -> Tuple[bool, str]:
        """Move finger using arrow controls"""
        if finger_index < 0 or finger_index >= 10:  # 5 fingers per hand
            return False, f"Invalid finger index: {finger_index}"
        
        # Determine hand and finger
        hand = 'derecha' if finger_index < 5 else 'izquierda'
        finger = self._get_finger_name(finger_index % 5)
        
        # Get current position
        if hand == 'derecha':
            current_pos = self.hand_positions['derecha'][finger_index]
        else:
            current_pos = self.hand_positions['izquierda'][finger_index - 5]
        
        new_pos = current_pos + (direction * 10)  # 10 degree increments
        
        # Validate new position
        if not self._validate_hand_position(new_pos):
            return False, f"Position out of range: {new_pos}"
        
        data = {
            'indice': str(finger_index),
            'direccion': str(direction)
        }
        
        success, response = self._make_request("/manos/flecha", "POST", data)
        if success:
            # Update local state
            if hand == 'derecha':
                self.hand_positions['derecha'][finger_index] = new_pos
            else:
                self.hand_positions['izquierda'][finger_index - 5] = new_pos
        
        return success, response
    
    # ===== WRIST CONTROL =====
    
    def move_wrist(self, hand: str, angle: int) -> Tuple[bool, str]:
        """Move wrist to specified angle"""
        if not self._validate_wrist_position(angle):
            return False, f"Angle out of range: {angle}"
        
        data = {
            'mano': hand,
            'angulo': str(angle)
        }
        
        success, response = self._make_request("/munecas/mover", "POST", data)
        if success:
            self.wrist_positions[hand] = angle
        
        return success, response
    
    def move_wrist_arrow(self, wrist_index: int, direction: int) -> Tuple[bool, str]:
        """Move wrist using arrow controls"""
        if wrist_index < 0 or wrist_index >= 2:  # 2 wrists
            return False, f"Invalid wrist index: {wrist_index}"
        
        hand = 'derecha' if wrist_index == 0 else 'izquierda'
        current_pos = self.wrist_positions[hand]
        new_pos = current_pos + (direction * 10)  # 10 degree increments
        
        # Validate new position
        if not self._validate_wrist_position(new_pos):
            return False, f"Position out of range: {new_pos}"
        
        data = {
            'indice': str(wrist_index),
            'direccion': str(direction)
        }
        
        success, response = self._make_request("/munecas/flecha", "POST", data)
        if success:
            self.wrist_positions[hand] = new_pos
        
        return success, response
    
    def wrists_center(self) -> Tuple[bool, str]:
        """Center both wrists"""
        success, response = self._make_request("/munecas/centrar")
        if success:
            self.wrist_positions = {'derecha': 80, 'izquierda': 80}
        return success, response
    
    def wrists_random(self) -> Tuple[bool, str]:
        """Move wrists to random positions"""
        return self._make_request("/munecas/aleatorio")
    
    # ===== SYSTEM CONTROL =====
    
    def system_security(self, enabled: bool) -> Tuple[bool, str]:
        """Enable/disable safety mode"""
        data = {'on': str(enabled).lower()}
        return self._make_request("/system/security", "POST", data)
    
    def system_speed(self, slow: bool) -> Tuple[bool, str]:
        """Set movement speed (slow/normal)"""
        data = {'slow': str(slow).lower()}
        return self._make_request("/system/speed", "POST", data)
    
    def system_check(self) -> Tuple[bool, str]:
        """Check system connections"""
        return self._make_request("/system/check")
    
    def system_reset(self) -> Tuple[bool, str]:
        """Reset robot to default position"""
        return self._make_request("/system/reset")
    
    def system_rest_position(self) -> Tuple[bool, str]:
        """Move robot to rest position"""
        return self._make_request("/system/descanso")
    
    # ===== DIRECT SERVO CONTROL =====
    
    def move_servo(self, channel: int, angle: int) -> Tuple[bool, str]:
        """Move servo directly"""
        if channel < 0 or channel > 15:
            return False, f"Invalid channel: {channel}"
        if angle < 0 or angle > 180:
            return False, f"Invalid angle: {angle}"
        
        data = {
            'ch': str(channel),
            'ang': str(angle)
        }
        
        return self._make_request("/servo", "POST", data)
    
    def send_command(self, command: str) -> Tuple[bool, str]:
        """Send custom command"""
        data = {'cmd': command}
        return self._make_request("/cmd", "POST", data)
    
    # ===== STATUS AND DEBUG =====
    
    def get_debug_info(self) -> Tuple[bool, str]:
        """Get debug information"""
        return self._make_request("/debug")
    
    def get_positions(self) -> Tuple[bool, Dict]:
        """Get current positions"""
        success, response = self._make_request("/posiciones")
        if success:
            try:
                return True, json.loads(response)
            except json.JSONDecodeError:
                return False, {"error": "Invalid JSON response"}
        return False, {"error": response}
    
    def start_status_monitoring(self):
        """Start background status monitoring"""
        if self.status_thread and self.status_thread.is_alive():
            return
        
        self.running = True
        self.status_thread = threading.Thread(target=self._status_monitor, daemon=True)
        self.status_thread.start()
    
    def _status_monitor(self):
        """Background status monitoring thread"""
        while self.running:
            try:
                success, positions = self.get_positions()
                if success:
                    # Update local state with received positions
                    self._update_positions_from_response(positions)
                
                time.sleep(2.0)  # Update every 2 seconds
            except Exception as e:
                print(f"Status monitor error: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _update_positions_from_response(self, positions: Dict):
        """Update local state from positions response"""
        try:
            # Update arms
            if 'brazos' in positions:
                for i, brazo in enumerate(positions['brazos']):
                    if i == 0: self.arm_positions['brazo_izq'] = brazo['posicion']
                    elif i == 1: self.arm_positions['frente_izq'] = brazo['posicion']
                    elif i == 2: self.arm_positions['brazo_der'] = brazo['posicion']
                    elif i == 3: self.arm_positions['frente_der'] = brazo['posicion']
            
            # Update neck
            if 'cuello' in positions:
                for i, cuello in enumerate(positions['cuello']):
                    if i == 0: self.neck_positions['lateral'] = cuello['posicion']
                    elif i == 1: self.neck_positions['inferior'] = cuello['posicion']
                    elif i == 2: self.neck_positions['superior'] = cuello['posicion']
            
            # Update hands
            if 'manos' in positions:
                for i, mano in enumerate(positions['manos']):
                    if i < 5:  # Right hand
                        self.hand_positions['derecha'][i] = mano['posicion']
                    else:  # Left hand
                        self.hand_positions['izquierda'][i-5] = mano['posicion']
            
            # Update wrists
            if 'munecas' in positions:
                for i, muneca in enumerate(positions['munecas']):
                    if i == 0: self.wrist_positions['derecha'] = muneca['posicion']
                    elif i == 1: self.wrist_positions['izquierda'] = muneca['posicion']
                    
        except Exception as e:
            print(f"Error updating positions: {e}")
    
    # ===== VALIDATION HELPERS =====
    
    def _validate_arm_position(self, arm_name: str, position: int) -> bool:
        """Validate arm position within limits"""
        if arm_name not in self.arm_limits:
            return False
        min_pos, max_pos = self.arm_limits[arm_name]
        return min_pos <= position <= max_pos
    
    def _validate_neck_position(self, neck_name: str, position: int) -> bool:
        """Validate neck position within limits"""
        if neck_name not in self.neck_limits:
            return False
        min_pos, max_pos = self.neck_limits[neck_name]
        return min_pos <= position <= max_pos
    
    def _validate_hand_position(self, position: int) -> bool:
        """Validate hand/finger position within limits"""
        min_pos, max_pos = self.hand_limits
        return min_pos <= position <= max_pos
    
    def _validate_wrist_position(self, position: int) -> bool:
        """Validate wrist position within limits"""
        min_pos, max_pos = self.wrist_limits
        return min_pos <= position <= max_pos
    
    def _get_finger_index(self, finger: str) -> int:
        """Get finger index from name"""
        finger_map = {
            'pulgar': 0, 'indice': 1, 'medio': 2, 'anular': 3, 'menique': 4
        }
        return finger_map.get(finger, -1)
    
    def _get_finger_name(self, index: int) -> str:
        """Get finger name from index"""
        finger_names = ['pulgar', 'indice', 'medio', 'anular', 'menique']
        return finger_names[index] if 0 <= index < len(finger_names) else 'pulgar'
    
    # ===== GETTERS FOR CURRENT STATE =====
    
    def get_arm_positions(self) -> Dict[str, int]:
        """Get current arm positions"""
        return self.arm_positions.copy()
    
    def get_neck_positions(self) -> Dict[str, int]:
        """Get current neck positions"""
        return self.neck_positions.copy()
    
    def get_hand_positions(self) -> Dict[str, List[int]]:
        """Get current hand positions"""
        return {
            'derecha': self.hand_positions['derecha'].copy(),
            'izquierda': self.hand_positions['izquierda'].copy()
        }
    
    def get_wrist_positions(self) -> Dict[str, int]:
        """Get current wrist positions"""
        return self.wrist_positions.copy()
    
    def get_connection_status(self) -> Dict[str, any]:
        """Get connection status and statistics"""
        return {
            'connected': self.connected,
            'error_count': self.error_count,
            'last_response': self.last_response,
            'config': {
                'host': self.config.host,
                'port': self.config.port,
                'timeout': self.config.timeout
            }
        }
