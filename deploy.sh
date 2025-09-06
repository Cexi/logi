#!/bin/bash
# Script de deploy para fleet.loginexia.com

echo "🚀 Desplegando fleet.loginexia.com..."

# Detener contenedores actuales
echo "Deteniendo servicios actuales..."
docker-compose down

# Construir nueva imagen
echo "Construyendo nueva imagen..."
docker-compose build --no-cache

# Iniciar servicios
echo "Iniciando servicios..."
docker-compose up -d

# Esperar a que esté listo
echo "Esperando a que los servicios estén listos..."
sleep 5

# Verificar salud
echo "Verificando estado de salud..."
curl -f http://localhost:5000/health || echo "⚠️ Health check falló"

# Mostrar logs
echo "Últimas líneas de logs:"
docker-compose logs --tail=20

echo "✅ Deploy completado!"
echo "Verifica en: https://fleet.loginexia.com/health"
