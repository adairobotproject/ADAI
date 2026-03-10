# 📦 Guía de Instalación - RobotAtlas

Esta guía te ayudará a configurar el proyecto RobotAtlas en cualquier computadora usando un entorno virtual (venv).

## 📋 Requisitos Previos

### Windows
- **Python 3.8 o superior** - [Descargar Python](https://www.python.org/downloads/)
  - ⚠️ **Importante:** Durante la instalación, marca la opción "Add Python to PATH"

### Linux
- Python 3.8 o superior (generalmente preinstalado)
- `python3-venv` (para crear entornos virtuales)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-venv
  
  # Fedora
  sudo dnf install python3-venv
  ```

### macOS
- Python 3.8 o superior
- Si no está instalado, usa Homebrew:
  ```bash
  brew install python3
  ```

## 🚀 Instalación Rápida

### Windows

1. **Abre PowerShell o CMD** en la carpeta del proyecto
2. **Ejecuta el script de setup:**
   ```cmd
   cd ia-clases
   setup.bat
   ```
3. **Espera a que termine la instalación** (puede tardar varios minutos)
4. **Ejecuta el proyecto:**
   ```cmd
   run.bat
   ```

### Linux / macOS

1. **Abre una terminal** en la carpeta del proyecto
2. **Da permisos de ejecución al script:**
   ```bash
   cd ia-clases
   chmod +x setup.sh
   ```
3. **Ejecuta el script de setup:**
   ```bash
   ./setup.sh
   ```
4. **Espera a que termine la instalación** (puede tardar varios minutos)
5. **Ejecuta el proyecto:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

## 🔧 Instalación Manual

Si prefieres hacerlo manualmente o los scripts no funcionan:

### 1. Crear Entorno Virtual

**Windows:**
```cmd
cd ia-clases
python -m venv venv
```

**Linux/macOS:**
```bash
cd ia-clases
python3 -m venv venv
```

### 2. Activar Entorno Virtual

**Windows:**
```cmd
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

Cuando el entorno virtual está activo, verás `(venv)` al inicio de tu línea de comandos.

### 3. Actualizar pip

```bash
python -m pip install --upgrade pip
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

⚠️ **Nota:** Algunas dependencias pueden tardar varios minutos en instalarse, especialmente:
- `opencv-python` y `opencv-contrib-python`
- `dlib` y `face-recognition`
- `mediapipe`

### 5. Ejecutar la Aplicación

```bash
python robot_gui_conmodulos.py
```

## 📦 Estructura del Proyecto

```
RobotAtlas/
├── ia-clases/              # Proyecto principal Python
│   ├── venv/               # Entorno virtual (se crea al hacer setup)
│   ├── requirements.txt    # Dependencias del proyecto
│   ├── setup.bat           # Script de setup para Windows
│   ├── setup.sh            # Script de setup para Linux/Mac
│   ├── run.bat             # Script de ejecución para Windows
│   ├── run.sh              # Script de ejecución para Linux/Mac
│   ├── robot_gui_conmodulos.py  # Aplicación principal
│   └── ...
├── atlas/                  # Aplicación móvil (ReactLynx)
└── Controladores Robot/    # Código Arduino
```

## ⚠️ Solución de Problemas

### Error: "Python no está en el PATH" (Windows)

1. Abre "Configuración del Sistema" → "Variables de entorno"
2. En "Variables del sistema", busca "Path" y haz clic en "Editar"
3. Agrega la ruta de Python (ej: `C:\Python39\` y `C:\Python39\Scripts\`)
4. Reinicia la terminal

### Error: "pip no está disponible"

```bash
# Windows
python -m ensurepip --upgrade

# Linux
sudo apt-get install python3-pip

# macOS
python3 -m ensurepip --upgrade
```

### Error al instalar dlib o face-recognition

**Windows:**
```cmd
# Instalar Visual C++ Build Tools primero
# Descargar desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# O instalar Visual Studio con C++

# Luego instalar cmake
pip install cmake

# Finalmente instalar dlib
pip install dlib
```

**Linux:**
```bash
sudo apt-get install cmake
sudo apt-get install libopenblas-dev liblapack-dev
pip install dlib
```

**macOS:**
```bash
brew install cmake
pip install dlib
```

### Error: "No module named 'cv2'"

Asegúrate de que el entorno virtual esté activado y luego:
```bash
pip install opencv-python opencv-contrib-python
```

### Error: "Tesseract not found"

**Windows:**
1. Descarga Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instálalo en `C:\Program Files\Tesseract-OCR\`
3. El código ya está configurado para usar esa ruta

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### El entorno virtual no se activa

**Windows:**
- Si usas PowerShell, puede que necesites cambiar la política de ejecución:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

**Linux/macOS:**
- Asegúrate de usar `source` y no solo ejecutar el script:
  ```bash
  source venv/bin/activate
  ```

## 🔄 Actualizar Dependencias

Si el proyecto se actualiza y hay nuevas dependencias:

```bash
# Activar entorno virtual
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Actualizar dependencias
pip install -r requirements.txt --upgrade
```

## 📝 Notas Importantes

1. **Siempre activa el entorno virtual** antes de ejecutar el proyecto
2. **No subas el venv a Git** - Ya está en `.gitignore`
3. **Cada computadora necesita su propio venv** - No copies el venv entre máquinas
4. **Python 3.8+ es requerido** - Versiones anteriores pueden no funcionar

## 🎯 Verificación de Instalación

Para verificar que todo está instalado correctamente:

```bash
# Activar entorno virtual
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Verificar Python
python --version

# Verificar paquetes principales
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import tkinter; print('Tkinter: OK')"
python -c "import PIL; print('Pillow:', PIL.__version__)"
```

## 📞 Soporte

Si encuentras problemas durante la instalación:

1. Verifica que Python 3.8+ esté instalado
2. Asegúrate de que el entorno virtual esté activado
3. Revisa los mensajes de error específicos
4. Consulta la sección "Solución de Problemas" arriba

## 🚀 Próximos Pasos

Una vez instalado:

1. **Configura la IP del ESP32** en la aplicación
2. **Configura la IP del servidor** para la app móvil
3. **Revisa la documentación** en `docs/` para más información
4. **Consulta los ejemplos** en `docs/EJEMPLOS_CONSULTAS_API.md`

---

**¡Listo!** Ya puedes ejecutar el proyecto en cualquier computadora. 🎉


