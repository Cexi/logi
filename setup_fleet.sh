#!/bin/bash

# ========================================
# Script Automático de Setup para fleet.loginexia.com
# Genera TODOS los archivos necesarios
# ========================================

echo "🚀 Configurando fleet.loginexia.com - Setup Automático"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "src/main.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra src/main.py${NC}"
    echo "Asegúrate de ejecutar este script en la raíz de tu proyecto loginexia"
    exit 1
fi

echo -e "${GREEN}✅ Directorio del proyecto detectado${NC}"

# ========================================
# 1. CREAR DOCKERFILE
# ========================================
echo -e "${YELLOW}📦 Creando Dockerfile...${NC}"
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copiar el resto del código
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs /app/static

# Dar permisos
RUN chmod -R 755 /app

# Puerto
EXPOSE 5000

# Variables de entorno por defecto
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Comando para iniciar
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:application"]
EOF

# ========================================
# 2. CREAR DOCKER-COMPOSE.YML
# ========================================
echo -e "${YELLOW}🐳 Creando docker-compose.yml...${NC}"
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build: .
    container_name: fleet_loginexia
    restart: always
    ports:
      - "127.0.0.1:5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env
      - ./static:/app/static
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
      - TZ=Europe/Madrid
    networks:
      - fleet_network
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: fleet_redis
    restart: always
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - fleet_network
    command: redis-server --appendonly yes

networks:
  fleet_network:
    driver: bridge

volumes:
  redis_data:
    driver: local
EOF

# ========================================
# 3. CREAR APP.PY (CRÍTICO - En la raíz)
# ========================================
echo -e "${YELLOW}🔧 Creando app.py (punto de entrada)...${NC}"
cat > app.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de entrada WSGI para fleet.loginexia.com
Este archivo DEBE estar en la raíz del proyecto
"""

import os
import sys
from pathlib import Path

# Añadir el directorio actual al path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configurar variables de entorno
os.environ.setdefault('FLASK_ENV', 'production')

# Importar la aplicación
try:
    from src.main import create_app
    application = create_app()
except ImportError:
    # Fallback si create_app no existe
    from src.main import app
    application = app

# Alias para compatibilidad
app = application

# Solo para desarrollo/testing local
if __name__ == '__main__':
    print("🚀 Iniciando Fleet Loginexia en modo desarrollo...")
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

# ========================================
# 4. CREAR/ACTUALIZAR SRC/MAIN.PY
# ========================================
echo -e "${YELLOW}📝 Actualizando src/main.py...${NC}"

# Hacer backup del main.py actual
cp src/main.py src/main.py.backup

cat > src/main.py << 'EOF'
import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Factory para crear la aplicación Flask"""
    
    BASE_DIR = Path(__file__).parent.parent
    sys.path.insert(0, str(BASE_DIR))
    
    # Crear aplicación
    app = Flask(__name__,
                static_folder=os.path.join(BASE_DIR, 'static'),
                static_url_path='/static')
    
    # Configuración CORS para fleet.loginexia.com
    CORS(app, 
         origins=[
            "https://loginexia.com",
            "https://www.loginexia.com",
            "https://fleet.loginexia.com",
            "http://localhost:3000",
            "http://localhost:5000"
         ],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True
    )
    
    # Configuración de Flask
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(BASE_DIR, 'data', 'app.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', os.getenv('SECRET_KEY', 'jwt-secret')),
        JWT_ACCESS_TOKEN_EXPIRES=3600,  # 1 hora
        JWT_REFRESH_TOKEN_EXPIRES=2592000,  # 30 días
    )
    
    # Configuración Redis
    app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Inicializar base de datos
    from src.models.user import db
    db.init_app(app)
    
    # Importar y registrar blueprints
    try:
        from src.routes.user import user_bp
        from src.routes.auth import auth_bp
        from src.routes.riders import riders_bp
        from src.routes.ai import ai_bp
        from src.routes.demo import demo_bp
        from src.routes.whatsapp import whatsapp_bp
        
        app.register_blueprint(user_bp, url_prefix='/api/users')
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(riders_bp, url_prefix='/api/riders')
        app.register_blueprint(ai_bp, url_prefix='/api/ai')
        app.register_blueprint(demo_bp, url_prefix='/api/demo')
        app.register_blueprint(whatsapp_bp, url_prefix='/api/whatsapp')
        logger.info("✅ Todos los blueprints registrados correctamente")
    except ImportError as e:
        logger.error(f"Error importando blueprints: {e}")
    
    # Rutas base
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Fleet Management API - Loginexia',
            'version': '2.0.0',
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'health': '/health',
                'api_auth': '/api/auth/login',
                'api_riders': '/api/riders',
                'api_ai': '/api/ai',
                'api_whatsapp': '/api/whatsapp',
                'documentation': '/api/docs'
            },
            'environment': os.getenv('FLASK_ENV', 'development')
        })
    
    @app.route('/health')
    def health():
        """Endpoint de health check"""
        try:
            # Verificar base de datos
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except:
            db_status = 'unhealthy'
        
        return jsonify({
            'status': 'healthy',
            'service': 'fleet-loginexia',
            'version': '2.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'database': db_status,
            'environment': os.getenv('FLASK_ENV', 'development')
        })
    
    @app.route('/api/docs')
    def api_docs():
        """Documentación básica de la API"""
        return jsonify({
            'title': 'Fleet Loginexia API Documentation',
            'version': '2.0.0',
            'base_url': 'https://fleet.loginexia.com',
            'authentication': {
                'type': 'JWT Bearer',
                'login_endpoint': '/api/auth/login',
                'refresh_endpoint': '/api/auth/refresh'
            },
            'endpoints': {
                'auth': {
                    'POST /api/auth/login': 'User login',
                    'POST /api/auth/register': 'User registration',
                    'POST /api/auth/refresh': 'Refresh token'
                },
                'riders': {
                    'GET /api/riders': 'List all riders',
                    'GET /api/riders/{id}': 'Get rider details',
                    'POST /api/riders': 'Create new rider',
                    'PUT /api/riders/{id}': 'Update rider',
                    'DELETE /api/riders/{id}': 'Delete rider'
                },
                'ai': {
                    'POST /api/ai/nl-to-sql': 'Natural language to SQL',
                    'POST /api/ai/recommendations': 'Get AI recommendations',
                    'POST /api/ai/chat': 'AI chat assistant'
                },
                'whatsapp': {
                    'POST /api/whatsapp/send-alert': 'Send WhatsApp alert',
                    'POST /api/whatsapp/config': 'Configure WhatsApp'
                }
            }
        })
    
    # Servir frontend React si existe
    @app.route('/app')
    @app.route('/app/<path:path>')
    def serve_react(path=''):
        static_folder = app.static_folder
        if path and os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        elif os.path.exists(os.path.join(static_folder, 'index.html')):
            return send_from_directory(static_folder, 'index.html')
        else:
            return jsonify({'error': 'Frontend not found'}), 404
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'error': 'Endpoint not found',
            'message': str(e),
            'status': 404
        }), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            'error': 'Bad request',
            'message': str(e),
            'status': 400
        }), 400
    
    # Middleware para logging
    @app.before_request
    def log_request():
        logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    @app.after_request
    def log_response(response):
        response.headers['X-Powered-By'] = 'Fleet Loginexia'
        response.headers['X-Version'] = '2.0.0'
        return response
    
    # Crear tablas al iniciar
    with app.app_context():
        try:
            # Crear directorio para BD si no existe
            db_dir = os.path.join(BASE_DIR, 'data')
            os.makedirs(db_dir, exist_ok=True)
            
            # Crear tablas
            db.create_all()
            
            # Inicializar datos demo
            try:
                from src.database.init_db import init_db
                init_db(app)
                logger.info("✅ Base de datos inicializada correctamente")
            except Exception as e:
                logger.warning(f"No se pudo inicializar datos demo: {e}")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {str(e)}")
    
    logger.info("✅ Aplicación Flask creada exitosamente")
    return app

# Para importación directa (compatibilidad)
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF

# ========================================
# 5. CREAR .ENV DE PRODUCCIÓN
# ========================================
echo -e "${YELLOW}🔐 Creando archivo .env...${NC}"
cat > .env << 'EOF'
# ============================================
# CONFIGURACIÓN DE PRODUCCIÓN - fleet.loginexia.com
# ============================================

# Flask Configuration
FLASK_ENV=production
FLASK_APP=app:application
DEBUG=False

# CAMBIAR ESTAS CLAVES POR UNAS SEGURAS
SECRET_KEY=change-this-to-a-very-secure-random-string-at-least-32-characters-long
JWT_SECRET_KEY=another-very-secure-random-string-for-jwt-tokens

# Database
DATABASE_URL=sqlite:///data/app.db
# Para PostgreSQL (recomendado para producción):
# DATABASE_URL=postgresql://user:password@localhost/loginexia

# Redis
REDIS_URL=redis://redis:6379/0

# API Keys - DELIVERY HERO
DH_CLIENT_ID=your-delivery-hero-client-id
DH_KEY_ID=your-delivery-hero-key-id
DH_PRIVATE_KEY_PATH=keys/dh_private_key.pem

# API Keys - OPENAI
OPENAI_API_KEY=your-openai-api-key-here

# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token
WHATSAPP_PHONE_NUMBER_ID=your-whatsapp-phone-number-id
WHATSAPP_VERIFY_TOKEN=your-webhook-verify-token

# URLs Configuration
API_URL=https://fleet.loginexia.com
FRONTEND_URL=https://loginexia.com
ALLOWED_ORIGINS=https://loginexia.com,https://www.loginexia.com,https://fleet.loginexia.com

# Email Configuration (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password

# Monitoring (opcional)
SENTRY_DSN=
NEW_RELIC_LICENSE_KEY=

# Rate Limiting
RATE_LIMIT_DEFAULT=100 per minute
RATE_LIMIT_AUTH=10 per minute
RATE_LIMIT_AI=20 per minute
EOF

echo -e "${RED}⚠️  IMPORTANTE: Edita el archivo .env con tus claves reales${NC}"

# ========================================
# 6. CREAR .DOCKERIGNORE
# ========================================
echo -e "${YELLOW}📋 Creando .dockerignore...${NC}"
cat > .dockerignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.coverage
.pytest_cache/
htmlcov/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project
*.log
*.db
*.sqlite3
data/*.db
logs/
instance/
.env.local
.env.development

# Git
.git/
.gitignore

# Documentation
*.md
docs/
EOF

# ========================================
# 7. CREAR SCRIPT DE DEPLOY
# ========================================
echo -e "${YELLOW}🚀 Creando script de deploy...${NC}"
cat > deploy.sh << 'EOF'
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
EOF

chmod +x deploy.sh

# ========================================
# 8. CREAR NGINX CONFIG PARA PLESK
# ========================================
echo -e "${YELLOW}📄 Creando configuración de Nginx...${NC}"
cat > nginx_config.txt << 'EOF'
# ============================================
# CONFIGURACIÓN NGINX PARA PLESK
# Copiar esto en: Plesk > fleet.loginexia.com > Apache & nginx Settings
# ============================================

# Proxy para la aplicación Flask
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Timeouts largos para operaciones IA
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    send_timeout 300;
    
    # Buffer size para uploads
    client_max_body_size 16M;
    client_body_buffer_size 128k;
    
    # Buffering
    proxy_buffering off;
    proxy_request_buffering off;
}

# Health check endpoint (sin logs)
location /health {
    proxy_pass http://127.0.0.1:5000/health;
    access_log off;
}

# Static files
location /static {
    alias /var/www/vhosts/loginexia.com/fleet.loginexia.com/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# WebSocket support (si lo necesitas)
location /socket.io {
    proxy_pass http://127.0.0.1:5000/socket.io;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
EOF

# ========================================
# 9. ACTUALIZAR REQUIREMENTS.TXT
# ========================================
echo -e "${YELLOW}📦 Actualizando requirements.txt...${NC}"

# Verificar si gunicorn está en requirements
if ! grep -q "gunicorn" requirements.txt; then
    echo "gunicorn==23.0.0" >> requirements.txt
fi

# Verificar si redis está en requirements
if ! grep -q "redis" requirements.txt; then
    echo "redis==5.0.1" >> requirements.txt
fi

# ========================================
# 10. CREAR DIRECTORIOS NECESARIOS
# ========================================
echo -e "${YELLOW}📁 Creando directorios necesarios...${NC}"
mkdir -p data logs static keys

# ========================================
# RESUMEN FINAL
# ========================================
echo ""
echo "=========================================="
echo -e "${GREEN}✅ ¡CONFIGURACIÓN COMPLETADA!${NC}"
echo "=========================================="
echo ""
echo "📁 Archivos creados:"
echo "  ✓ Dockerfile"
echo "  ✓ docker-compose.yml"
echo "  ✓ app.py (punto de entrada)"
echo "  ✓ src/main.py (actualizado)"
echo "  ✓ .env (configuración)"
echo "  ✓ .dockerignore"
echo "  ✓ deploy.sh (script de deploy)"
echo "  ✓ nginx_config.txt (config para Plesk)"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo ""
echo "1. EDITAR el archivo .env con tus claves reales:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. COMMIT y PUSH a GitHub:"
echo "   ${YELLOW}git add .${NC}"
echo "   ${YELLOW}git commit -m 'Configuración para fleet.loginexia.com con Docker'${NC}"
echo "   ${YELLOW}git push${NC}"
echo ""
echo "3. EN EL SERVIDOR VPS:"
echo ""
echo "   a) Conectar por SSH:"
echo "      ${YELLOW}ssh tu-usuario@tu-vps-ip${NC}"
echo ""
echo "   b) Ir al directorio del subdominio:"
echo "      ${YELLOW}cd /var/www/vhosts/loginexia.com/fleet.loginexia.com${NC}"
echo ""
echo "   c) Clonar tu repositorio:"
echo "      ${YELLOW}git clone https://github.com/tu-usuario/tu-repo.git .${NC}"
echo ""
echo "   d) Instalar Docker (si no lo tienes):"
echo "      ${YELLOW}curl -fsSL https://get.docker.com | sh${NC}"
echo ""
echo "   e) Ejecutar el deploy:"
echo "      ${YELLOW}chmod +x deploy.sh${NC}"
echo "      ${YELLOW}./deploy.sh${NC}"
echo ""
echo "4. EN PLESK:"
echo "   - Ir a fleet.loginexia.com > Apache & nginx Settings"
echo "   - Copiar el contenido de nginx_config.txt"
echo "   - Guardar y aplicar"
echo ""
echo "5. VERIFICAR:"
echo "   ${YELLOW}curl https://fleet.loginexia.com/health${NC}"
echo ""
echo "=========================================="
echo -e "${GREEN}¡Tu aplicación está lista para deploy!${NC}"
echo "=========================================="
echo ""
echo "⚠️  NOTA: El archivo src/main.py.backup contiene tu código original"
echo ""
echo "💡 TIP: Ejecuta './deploy.sh' para hacer deploy automático con Docker"
echo ""
