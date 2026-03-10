# GUÍA PASO A PASO PARA GOPRO HERO 11 WEBCAM
# Si no encuentras la opción USB en los menús de la GoPro

import cv2
import time
import subprocess
import os

def check_gopro_hero11_connection():
    """
    Verifica el estado actual de conexión de la GoPro Hero 11
    """
    print("🔍 VERIFICANDO CONEXIÓN GOPRO HERO 11")
    print("=" * 50)
    
    # 1. Verificar dispositivos USB conectados
    print("\n📱 PASO 1: Verificando dispositivos USB...")
    try:
        # En Windows, usar PowerShell para ver dispositivos USB
        result = subprocess.run([
            'powershell', 
            'Get-WmiObject -Class Win32_USBHub | Select-Object Name, DeviceID'
        ], capture_output=True, text=True)
        
        if 'gopro' in result.stdout.lower() or 'hero' in result.stdout.lower():
            print("✅ GoPro detectada como dispositivo USB")
        else:
            print("❌ GoPro no detectada como dispositivo USB")
            print("💡 Verifica que el cable USB esté bien conectado")
    except:
        print("⚠️ No se pudo verificar dispositivos USB")
    
    # 2. Verificar si está en modo MTP (modo de archivos)
    print("\n📁 PASO 2: Verificando si está en modo MTP...")
    try:
        # Verificar si aparece como dispositivo de almacenamiento
        drives = ['D:', 'E:', 'F:', 'G:', 'H:', 'I:', 'J:', 'K:']
        gopro_drive = None
        
        for drive in drives:
            if os.path.exists(drive):
                try:
                    files = os.listdir(drive)
                    # GoPro en modo MTP suele mostrar carpetas DCIM, MISC, etc.
                    if any(folder in ['DCIM', 'MISC', '100GOPRO'] for folder in files):
                        gopro_drive = drive
                        break
                except:
                    pass
        
        if gopro_drive:
            print(f"⚠️ GoPro detectada como almacenamiento en {gopro_drive}")
            print("❌ Está en modo MTP (transferencia de archivos)")
            print("💡 Necesita cambiarse a modo webcam")
        else:
            print("✅ No detectada como almacenamiento - posiblemente en modo correcto")
    
    except Exception as e:
        print(f"⚠️ Error verificando almacenamiento: {e}")
    
    # 3. Probar acceso directo como webcam
    print("\n🎥 PASO 3: Probando acceso directo como webcam...")
    
    webcam_working = False
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None and frame.mean() > 1:
                    print(f"✅ Webcam funcional encontrada en índice {i}")
                    cv2.imwrite(f"gopro_test_{i}.jpg", frame)
                    webcam_working = True
                cap.release()
        except:
            pass
    
    if not webcam_working:
        print("❌ No se pudo acceder como webcam")
    
    return webcam_working

def force_gopro_webcam_mode():
    """
    Intenta forzar el modo webcam usando diferentes métodos
    """
    print("\n🔧 INTENTANDO FORZAR MODO WEBCAM...")
    
    methods = [
        "Método 1: Usando GoPro Webcam App",
        "Método 2: Reconexión USB",
        "Método 3: Configuración manual"
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n{method}")
        print("-" * 40)
        
        if i == 1:
            print("1. Abre GoPro Webcam en tu PC")
            print("2. Conecta la GoPro por USB")
            print("3. La app debería detectarla automáticamente")
            print("4. Si aparece 'Connected', está funcionando")
            
        elif i == 2:
            print("1. Desconecta el cable USB de la GoPro")
            print("2. Apaga la GoPro completamente")
            print("3. Enciende la GoPro")
            print("4. Abre GoPro Webcam en PC PRIMERO")
            print("5. Luego conecta el cable USB")
            
        elif i == 3:
            print("1. En la GoPro, busca en TODOS los menús:")
            print("   - Preferences > General > USB")
            print("   - Settings > System > USB")
            print("   - Controls > USB")
            print("2. Busca cualquier opción que mencione:")
            print("   - 'USB Connection'")
            print("   - 'PC Connection'") 
            print("   - 'Transfer Mode'")
            print("3. Cambia de 'MTP' a 'USB' o 'PC'")
        
        # Pausa para que el usuario pueda ejecutar el método
        input("Presiona Enter cuando hayas completado este método...")
        
        # Verificar si funcionó
        if test_webcam_after_method():
            print(f"✅ ¡{method} FUNCIONÓ!")
            return True
        else:
            print(f"❌ {method} no funcionó, probando siguiente...")
    
    return False

def test_webcam_after_method():
    """
    Prueba rápida para ver si el webcam ya funciona
    """
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None and frame.mean() > 5:
                cap.release()
                return True
        cap.release()
    except:
        pass
    return False

def gopro_hero11_manual_steps():
    """
    Pasos manuales específicos para Hero 11
    """
    print("\n📋 PASOS MANUALES ESPECÍFICOS PARA HERO 11:")
    print("=" * 50)
    
    steps = [
        "🔋 PASO 1: Preparar la GoPro",
        "   - Enciende la GoPro Hero 11",
        "   - Asegúrate que tenga >50% batería",
        "   - Usa cable USB original de GoPro",
        "",
        "💻 PASO 2: Preparar la PC",
        "   - Descarga GoPro Webcam desde gopro.com",
        "   - Cierra todas las apps que usen cámara",
        "   - Abre GoPro Webcam",
        "",
        "🔌 PASO 3: Secuencia de conexión",
        "   - Abre GoPro Webcam PRIMERO",
        "   - Luego conecta USB a la GoPro",
        "   - Espera 10-15 segundos",
        "   - GoPro Webcam debería mostrar 'Connected'",
        "",
        "⚙️ PASO 4: Si no se conecta automáticamente",
        "   - En GoPro Webcam: Click 'Refresh'",
        "   - Si sigue sin funcionar:",
        "     * Desconecta USB",
        "     * Cierra GoPro Webcam", 
        "     * Reinicia la GoPro",
        "     * Repite desde PASO 2",
        "",
        "🎯 PASO 5: Configurar una vez conectada",
        "   - En GoPro Webcam:",
        "     * Resolution: 720p",
        "     * Field of View: Linear",
        "     * Quality: High",
        "",
        "✅ PASO 6: Verificar funcionamiento",
        "   - Deberías ver video en tiempo real",
        "   - La GoPro aparecerá como cámara en Windows",
        "   - Tu código Python podrá acceder a ella"
    ]
    
    for step in steps:
        print(step)
    
    print(f"\n🚨 NOTA IMPORTANTE:")
    print(f"La Hero 11 puede no tener opción USB manual en menús.")
    print(f"GoPro Webcam app se encarga de cambiar el modo automáticamente.")

if __name__ == "__main__":
    print("🎯 GUÍA COMPLETA GOPRO HERO 11 WEBCAM")
    print("Esta guía te ayudará paso a paso")
    
    # Verificar estado actual
    print("\n🔍 Verificando estado actual...")
    is_working = check_gopro_hero11_connection()
    
    if is_working:
        print("\n✅ ¡Tu GoPro ya está funcionando como webcam!")
    else:
        print("\n🔧 La GoPro necesita configuración...")
        
        # Mostrar pasos manuales
        gopro_hero11_manual_steps()
        
        print(f"\n¿Quieres intentar los métodos automáticos? (s/n): ", end="")
        response = input().strip().lower()
        
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            success = force_gopro_webcam_mode()
            if success:
                print("\n🎉 ¡GoPro configurada exitosamente!")
            else:
                print("\n❌ Los métodos automáticos no funcionaron")
                print("Sigue los pasos manuales mostrados arriba")