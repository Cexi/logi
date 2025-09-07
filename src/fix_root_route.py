"""
Override para servir React en lugar de API en ruta raíz
"""
from flask import send_file, send_from_directory
import os

def override_root_route(app):
    """Reemplazar la ruta raíz para servir React"""
    
    # Remover la ruta existente si existe
    rules_to_remove = []
    for rule in app.url_map.iter_rules():
        if rule.rule == '/':
            rules_to_remove.append(rule)
    
    for rule in rules_to_remove:
        app.url_map._rules.remove(rule)
    
    # Nueva ruta raíz que sirve React
    @app.route('/')
    def index():
        """Servir la aplicación React"""
        # Buscar index.html en diferentes ubicaciones
        index_paths = [
            'static/index.html',
            'index.html',
            'app/index.html',
            'build/index.html'
        ]
        
        for path in index_paths:
            if os.path.exists(path):
                print(f"Serving React app from: {path}")
                return send_file(path)
        
        # Si no encuentra index.html, crear uno que redirija
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Loginexia Fleet - Cargando...</title>
            <meta http-equiv="refresh" content="0; url=/app">
        </head>
        <body>
            <p>Redirigiendo a la aplicación...</p>
            <script>window.location.href = '/app';</script>
        </body>
        </html>
        '''
    
    # Mover la info de API a /api
    @app.route('/api')
    @app.route('/api/')
    def api_info():
        """API information endpoint"""
        return {
            "service": "Fleet Management API - Loginexia",
            "version": "2.0.0",
            "status": "operational",
            "environment": "production",
            "endpoints": {
                "health": "/health",
                "documentation": "/api/docs",
                "api_auth": "/api/auth/login",
                "api_riders": "/api/riders",
                "api_whatsapp": "/api/whatsapp",
                "api_ai": "/api/ai"
            }
        }
    
    print("✅ Root route overridden to serve React")
    return app
