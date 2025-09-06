import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db

# Import blueprints
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.riders import riders_bp
from src.routes.ai import ai_bp
from src.routes.demo import demo_bp
from src.routes.whatsapp import whatsapp_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(riders_bp, url_prefix='/api/riders')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(demo_bp, url_prefix='/api/demo')
app.register_blueprint(whatsapp_bp, url_prefix='/api/whatsapp')

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Import all models to ensure they're registered
from src.models.organization import Organization, APIKey, APIConfiguration
from src.models.support import SupportTicket, TicketMessage, Alert

from src.database.init_db import init_db

with app.app_context():
    db.create_all()
    init_db(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

