"""
Configuración para React Router (SPA)
"""
from flask import send_file
import os

def setup_react_router(app):
    """
    Configurar todas las rutas para que sirvan React
    Las rutas de React: /login, /dashboard, /settings, etc.
    """
    
    # Lista de rutas que maneja React internamente
    react_routes = [
        '/',
        '/login',
        '/dashboard',
        '/riders',
        '/deliveries',
        '/analytics',
        '/alerts',
        '/settings',
        '/profile',
        '/logout'
    ]
    
    # Función para servir React
    def serve_react_app():
        """Servir el index.html de React para cualquier ruta"""
        # Buscar el archivo HTML de React
        html_paths = [
            'static/working.html',  # El que sabemos que funciona
            'static/react.html',
            'static/index.html',
            'index.html'
        ]
        
        for path in html_paths:
            if os.path.exists(path):
                print(f"Serving React from: {path}")
                return send_file(path)
        
        # Si no encuentra ninguno, crear uno básico
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Loginexia Fleet</title>
            <link rel="stylesheet" href="/static/assets/index-C8OnwuCY.css">
        </head>
        <body>
            <div id="root"></div>
            <script type="module" src="/static/assets/index-DXPCKFP6.js"></script>
        </body>
        </html>
        '''
    
    # Registrar todas las rutas de React
    for route in react_routes:
        app.add_url_rule(route, endpoint=f'react_{route}', view_func=serve_react_app)
    
    # Catch-all para cualquier otra ruta que React pueda usar
    @app.route('/<path:path>')
    def catch_all(path):
        # Si es un archivo estático, no interferir
        if path.startswith('static/') or path.startswith('assets/') or path.startswith('api/'):
            return app.send_static_file(path) if path.startswith('static/') else ('Not Found', 404)
        
        # Para cualquier otra ruta, servir React
        return serve_react_app()
    
    print("✅ React Router configured for SPA")
    return app
