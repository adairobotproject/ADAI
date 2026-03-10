# Guía de Instalación y Uso con Docker

## 🐳 Instalación con Docker

Docker simplifica la instalación al incluir todas las dependencias en un contenedor aislado.

### Requisitos Previos

1. **Docker Desktop** (o Docker Engine + Docker Compose)
   - macOS: https://docs.docker.com/desktop/install/mac-install/
   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - Linux: https://docs.docker.com/engine/install/

2. **XQuartz** (solo macOS, para GUI)
   ```bash
   brew install --cask xquartz
   ```
   Luego reinicia tu Mac.

### Instalación Rápida

```bash
cd ia-clases
chmod +x setup_docker.sh
./setup_docker.sh
```

Esto construirá la imagen de Docker con todas las dependencias.

## 🚀 Uso

### Modo Normal (con GUI)

```bash
docker-compose up
```

**Nota para macOS:**
1. Abre XQuartz
2. En XQuartz > Preferencias > Seguridad, marca "Permitir conexiones de clientes"
3. Ejecuta: `xhost +localhost`
4. Luego ejecuta `docker-compose up`

**Nota para Linux:**
```bash
xhost +local:docker
docker-compose up
```

### Modo Headless (sin GUI)

Para ejecutar sin interfaz gráfica:

```bash
docker-compose --profile headless up robotatlas-headless
```

Útil para servidores o cuando no necesitas la GUI.

### Modo Detached (en segundo plano)

```bash
docker-compose up -d
```

Para ver los logs:
```bash
docker-compose logs -f
```

### Detener el Contenedor

```bash
docker-compose down
```

## 📁 Volúmenes y Persistencia

Los siguientes directorios se montan como volúmenes para persistencia:

- `./clases` → `/app/clases` - Configuraciones de clases
- `./data` → `/app/data` - Datos de la aplicación
- `./logs` → `/app/logs` - Logs de la aplicación
- `./config` → `/app/config` - Archivos de configuración

## 🔧 Configuración

### Variables de Entorno

Puedes modificar `docker-compose.yml` para agregar variables de entorno:

```yaml
environment:
  - DISPLAY=:0
  - PYTHONUNBUFFERED=1
  - TZ=America/Mexico_City
  - OPENAI_API_KEY=tu_api_key  # Si es necesario
```

### Puertos

Los puertos expuestos por defecto:
- `8000` - API móvil
- `8080` - Puerto alternativo
- `5900` - VNC (acceso remoto a GUI)

Puedes modificarlos en `docker-compose.yml`:

```yaml
ports:
  - "8000:8000"  # host:container
```

### Acceso a Dispositivos

Para acceso a cámara y micrófono, el contenedor está configurado con `privileged: true`.

**Linux:**
```yaml
devices:
  - /dev/video0:/dev/video0  # Cámara
  - /dev/snd:/dev/snd        # Audio
```

**macOS/Windows:**
Docker Desktop maneja los dispositivos automáticamente.

## 🌐 Red

El contenedor usa `network_mode: "host"` para acceso completo a la red local, necesario para:
- Conexión a ESP32
- API móvil
- Servicios de red

## 🔍 Solución de Problemas

### Error: "Cannot connect to the Docker daemon"

**Solución:**
1. Asegúrate de que Docker Desktop esté ejecutándose
2. Verifica permisos: `docker ps`

### Error: "No display" (GUI no funciona)

**macOS:**
```bash
# Instalar XQuartz
brew install --cask xquartz

# Reiniciar Mac, luego:
xhost +localhost
docker-compose up
```

**Linux:**
```bash
xhost +local:docker
docker-compose up
```

### Error: "Permission denied" al acceder a dispositivos

**Solución:**
El contenedor ya está configurado con `privileged: true`. Si aún hay problemas:
```bash
docker-compose down
docker-compose up --privileged
```

### La cámara no funciona

**Solución:**
1. Verifica que la cámara esté disponible:
   ```bash
   ls -l /dev/video*
   ```

2. Ajusta el dispositivo en `docker-compose.yml`:
   ```yaml
   devices:
     - /dev/video0:/dev/video0  # Cambia video0 por tu dispositivo
   ```

### Reconstruir la imagen

Si cambias el Dockerfile o requirements:

```bash
docker-compose build --no-cache
docker-compose up
```

### Ver logs detallados

```bash
# Todos los logs
docker-compose logs -f

# Solo un servicio
docker-compose logs -f robotatlas

# Últimas 100 líneas
docker-compose logs --tail=100
```

### Acceder al contenedor

```bash
# Ejecutar bash en el contenedor
docker-compose exec robotatlas bash

# Ejecutar Python interactivo
docker-compose exec robotatlas python
```

## 📊 Recursos

El contenedor está limitado a:
- **CPU:** 4 cores máximo, 2 reservados
- **Memoria:** 4GB máximo, 2GB reservados

Puedes ajustar en `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

## 🔄 Actualización

Para actualizar a la última versión:

```bash
docker-compose pull  # Si usas imagen de registro
docker-compose build --pull  # Reconstruir con última base
docker-compose up -d
```

## 🗑️ Limpieza

Para eliminar todo (imágenes, contenedores, volúmenes):

```bash
docker-compose down -v --rmi all
```

**⚠️ Advertencia:** Esto eliminará todos los datos en volúmenes.

## 📝 Notas Adicionales

1. **Primera ejecución:** La construcción de la imagen puede tardar 10-20 minutos
2. **Espacio en disco:** La imagen final ocupa aproximadamente 2-3 GB
3. **Rendimiento:** Docker puede ser ligeramente más lento que instalación nativa
4. **GUI:** En algunos sistemas, la GUI puede tener problemas. Considera usar modo headless o VNC

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs: `docker-compose logs -f`
2. Verifica la configuración en `docker-compose.yml`
3. Consulta la documentación de Docker: https://docs.docker.com/

