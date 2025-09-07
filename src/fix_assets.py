"""
Fix para servir correctamente los assets de React
"""
from flask import send_from_directory, send_file
import os

def setup_asset_routes(app):
    """Configurar rutas para servir assets correctamente"""
    
    # Detectar dónde está la build de React
    react_build_dir = None
    if os.path.exists('build'):
        react_build_dir = 'build'
    elif os.path.exists('dist'):
        react_build_dir = 'dist'
    elif os.path.exists('static/build'):
        react_build_dir = 'static/build'
    elif os.path.exists('static'):
        react_build_dir = 'static'
    
    if not react_build_dir:
        print("❌ No se encuentra directorio de React build")
        return app
    
    print(f"📁 React build encontrada en: {react_build_dir}")
    
    # Ruta para servir assets
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """Servir archivos de assets"""
        assets_paths = [
            os.path.join(react_build_dir, 'assets'),
            os.path.join(react_build_dir, 'static/assets'),
            os.path.join('assets'),
            os.path.join('static', 'assets')
        ]
        
        for assets_dir in assets_paths:
            if os.path.exists(assets_dir):
                file_path = os.path.join(assets_dir, filename)
                if os.path.exists(file_path):
                    print(f"✅ Sirviendo asset: {file_path}")
                    return send_file(file_path)
        
        # Si no se encuentra, buscar en todo el proyecto
        for root, dirs, files in os.walk('.'):
            if filename in files:
                print(f"✅ Asset encontrado en: {root}/{filename}")
                return send_file(os.path.join(root, filename))
        
        print(f"❌ Asset no encontrado: {filename}")
        return "Asset not found", 404
    
    # Ruta para el favicon
    @app.route('/favicon.ico')
    def favicon():
        paths = [
            os.path.join(react_build_dir, 'favicon.ico'),
            'favicon.ico',
            'static/favicon.ico'
        ]
        for path in paths:
            if os.path.exists(path):
                return send_file(path)
        return '', 204
    
    # Ruta principal para servir index.html
    @app.route('/app')
    @app.route('/app/')
    @app.route('/app/<path:path>')
    def serve_react_app(path=None):
        """Servir la aplicación React"""
        index_paths = [
            os.path.join(react_build_dir, 'index.html'),
            'index.html',
            'static/index.html'
        ]
        
        for index_path in index_paths:
            if os.path.exists(index_path):
                print(f"✅ Sirviendo React app desde: {index_path}")
                return send_file(index_path)
        
        return "React app not found", 404
    
    # Debug: Mostrar todas las rutas
    @app.route('/debug/routes')
    def debug_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        return {'routes': routes}
    
    print("✅ Asset routes configuradas")
    return app

# Si se ejecuta directamente
if __name__ == "__main__":
    print("Añade esto a tu main.py:")
    print("from fix_assets import setup_asset_routes")
    print("app = setup_asset_routes(app)")
