"""
Demo authentication endpoint for testing
"""
from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta

demo_auth_bp = Blueprint('demo_auth', __name__)

@demo_auth_bp.route('/api/demo/auth/demo-login', methods=['POST', 'OPTIONS'])
def demo_login():
    """Demo login endpoint"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json() or {}
        email = data.get('email', '')
        password = data.get('password', '')
        
        # Check demo credentials
        if email == 'demo@loginexia.com' and password == 'demo123':
            # Generate demo token
            token_payload = {
                'user_id': 1,
                'email': email,
                'role': 'admin',
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            
            # Use a simple secret for demo
            token = jwt.encode(token_payload, 'demo-secret-key', algorithm='HS256')
            
            return jsonify({
                'success': True,
                'access_token': token,
                'user': {
                    'id': 1,
                    'email': email,
                    'name': 'Demo User',
                    'role': 'admin'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@demo_auth_bp.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def standard_login():
    """Standard login endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # Redirect to demo login for now
    return demo_login()
