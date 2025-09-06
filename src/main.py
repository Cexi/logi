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
