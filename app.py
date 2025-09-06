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
