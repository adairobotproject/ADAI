# 1. Instalar
cd ia-clases
./setup_docker.sh

# 2. Ejecutar (con GUI)
docker-compose up

# 3. Ejecutar (sin GUI)
docker-compose --profile headless up robotatlas-headless

# 4. Detener
docker-compose down