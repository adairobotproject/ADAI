# Guía de Solución de Problemas para Windows

## Problemas Comunes y Soluciones

### 1. Error: "No module named '_tkinter'"

**Problema:** Python no tiene soporte para tkinter.

**Solución:**
1. Reinstala Python desde https://www.python.org/downloads/
2. Durante la instalación, asegúrate de marcar la opción **"tcl/tk and IDLE"**
3. Marca también **"Add Python to PATH"**

### 2. Error al compilar dlib

**Problema:** dlib requiere compilación y necesita Visual C++ Build Tools.

**Solución:**
1. Descarga e instala **Visual Studio Build Tools**:
   - Ve a: https://visualstudio.microsoft.com/downloads/
   - Descarga "Build Tools for Visual Studio"
   - Durante la instalación, selecciona "Desktop development with C++"

2. O instala **Visual Studio Community** (versión completa):
   - Incluye todas las herramientas necesarias
   - Descarga desde: https://visualstudio.microsoft.com/downloads/

3. Después de instalar, reinicia tu terminal y ejecuta:
   ```cmd
   cd ia-clases
   venv\Scripts\activate
   pip install dlib==19.24.6
   ```

### 3. Error al compilar PyAudio

**Problema:** PyAudio requiere dependencias adicionales en Windows.

**Solución:**
1. Instala **Visual C++ Build Tools** (ver solución anterior)

2. O descarga el wheel precompilado:
   ```cmd
   pip install pipwin
   pipwin install pyaudio
   ```

3. O instala desde un wheel precompilado:
   - Visita: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
   - Descarga el archivo `.whl` correspondiente a tu versión de Python
   - Instala con: `pip install PyAudio-0.2.11-cp312-cp312-win_amd64.whl`

### 4. Error: "Microsoft Visual C++ 14.0 or greater is required"

**Problema:** Faltan las herramientas de compilación de C++.

**Solución:**
Instala **Visual Studio Build Tools**:
1. Descarga desde: https://visualstudio.microsoft.com/downloads/
2. Selecciona "Build Tools for Visual Studio"
3. Marca "Desktop development with C++"
4. Instala y reinicia tu terminal

### 5. Error: "CMake is not installed"

**Problema:** Algunos paquetes requieren CMake para compilarse.

**Solución:**
1. Descarga CMake desde: https://cmake.org/download/
2. Durante la instalación, marca **"Add CMake to system PATH"**
3. Reinicia tu terminal después de instalar

### 6. Python no se encuentra en PATH

**Problema:** El comando `python` no funciona en la terminal.

**Solución:**
1. Reinstala Python desde python.org
2. Durante la instalación, **marca "Add Python to PATH"**
3. O agrega Python manualmente al PATH:
   - Busca "Variables de entorno" en el menú de inicio
   - Agrega la ruta de Python a la variable PATH
   - Ejemplo: `C:\Python312\` y `C:\Python312\Scripts\`

### 7. El entorno virtual no se activa

**Problema:** El comando `venv\Scripts\activate` no funciona.

**Solución:**
1. Asegúrate de estar en el directorio correcto:
   ```cmd
   cd ia-clases
   ```

2. Si usas PowerShell, puede que necesites cambiar la política de ejecución:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. O usa el script de activación completo:
   ```cmd
   venv\Scripts\activate.bat
   ```

## Verificación de Instalación

Después de ejecutar `setup.bat`, verifica que todo esté instalado:

```cmd
venv\Scripts\activate
python -c "import cv2; print('OpenCV OK')"
python -c "import numpy; print('NumPy OK')"
python -c "import tkinter; print('tkinter OK')"
python -c "import matplotlib; print('Matplotlib OK')"
```

## Recursos Útiles

- **Python Downloads**: https://www.python.org/downloads/
- **Visual Studio Build Tools**: https://visualstudio.microsoft.com/downloads/
- **CMake**: https://cmake.org/download/
- **PyAudio Wheels**: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

## Notas Importantes

1. **Siempre reinicia tu terminal** después de instalar Visual Studio Build Tools o CMake
2. **Usa PowerShell o CMD como Administrador** si tienes problemas de permisos
3. **Asegúrate de tener conexión a internet** durante la instalación de paquetes
4. **Algunos paquetes pueden tardar varios minutos** en compilarse (especialmente dlib)

