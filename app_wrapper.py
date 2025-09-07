"""
Wrapper para servir React en lugar de API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la app original
from src.main import app
from flask import send_file, send_from_directory

# Override de la ruta raíz
@app.route('/', methods=['GET'])
def serve_react():
    """Servir React app en ruta raíz"""
    if os.path.exists('static/index.html'):
        return send_file('static/index.html')
    return redirect('/app')

@app.route('/app', methods=['GET'])
@app.route('/app/', methods=['GET'])
def serve_app():
    """Servir React app en /app"""
    if os.path.exists('static/index.html'):
        return send_file('static/index.html')
    return "App not found", 404

# Rutas para assets
@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/assets/<path:path>')
def asset_files(path):
    return send_from_directory('static/assets', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
