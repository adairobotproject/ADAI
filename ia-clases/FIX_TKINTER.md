# Solución para el Error de tkinter en macOS

## Problema

Si ves el error:
```
ModuleNotFoundError: No module named '_tkinter'
```

Esto significa que tu Python no tiene soporte para tkinter, que es necesario para la interfaz gráfica de la aplicación.

## Solución Rápida

### Opción 1: Instalar python-tk (Recomendado)

```bash
brew install python-tk@3.12
```

Luego recrea el entorno virtual:
```bash
cd ia-clases
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
./setup_python312.sh
```

### Opción 2: Reinstalar Python con soporte de tkinter

```bash
brew uninstall python@3.12
brew install python@3.12 python-tk@3.12
```

Luego recrea el entorno virtual:
```bash
cd ia-clases
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
./setup_python312.sh
```

### Opción 3: Usar el Python del Sistema

Si tienes Python del sistema (no de Homebrew), puedes usarlo:

```bash
cd ia-clases
rm -rf venv
/usr/bin/python3 -m venv venv
source venv/bin/activate
./setup.sh
```

**Nota:** El Python del sistema en macOS generalmente incluye tkinter.

## Verificar que tkinter funciona

Después de instalar, verifica:

```bash
source venv/bin/activate
python -c "import tkinter; print('tkinter OK')"
```

Si no hay errores, tkinter está funcionando correctamente.

## ¿Por qué pasa esto?

Homebrew instala Python sin algunas dependencias opcionales como tkinter para mantener el paquete más ligero. Python-tk es un paquete separado que proporciona el soporte de tkinter.

