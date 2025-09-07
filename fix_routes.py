"""
Script para configurar las rutas correctamente
"""
import os
from flask import Flask, send_from_directory, jsonify

def setup_frontend_routes(app):
    """Configurar rutas para servir el frontend React"""
    
    # Detectar dónde está el frontend
    if os.path.exists('build'):
        static_folder = 'build'
    elif os.path.exists('static'):
        static_folder = 'static'
    else:
        static_folder = '.'
    
    print(f"📁 Sirviendo frontend desde: {static_folder}")
    
    # Ruta para archivos estáticos
    @app.route('/<path:path>')
    def serve_static(path):
        if os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        else:
            # Si no existe el archivo, servir index.html (para React Router)
            return send_from_directory(static_folder, 'index.html')
    
    # Ruta raíz
    @app.route('/')
    def index():
        return send_from_directory(static_folder, 'index.html')
    
    # Rutas específicas que deben servir index.html
    @app.route('/login')
    @app.route('/dashboard')
    @app.route('/app')
    @app.route('/app/<path:path>')
    def serve_spa(path=None):
        return send_from_directory(static_folder, 'index.html')
    
    return app

if __name__ == "__main__":
    print("Añade estas líneas a tu archivo principal de Flask:")
    print("from fix_routes import setup_frontend_routes")
    print("app = setup_frontend_routes(app)")
