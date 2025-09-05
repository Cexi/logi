#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'src'))

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['DATABASE_URL'] = 'mysql+pymysql://loginexia_manus:midfor-6xikkE-qiqpaf@localhost/loginexia_db'

from src.main import app
from src.database.init_db import init_db

# Initialize database on first run
try:
    init_db(app)
except Exception as e:
    print(f"Database initialization error: {e}")

# This is the WSGI application object
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

