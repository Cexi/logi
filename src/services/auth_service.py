import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from src.models.user import User, db
from src.models.organization import Organization, APIKey

class AuthService:
    @staticmethod
    def generate_tokens(user):
        """Generate access and refresh tokens for a user"""
        payload = {
            'user_id': user.id,
            'organization_id': user.organization_id,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=1)  # Access token expires in 1 hour
        }
        
        refresh_payload = {
            'user_id': user.id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=30)  # Refresh token expires in 30 days
        }
        
        access_token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
    
    @staticmethod
    def verify_token(token):
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def generate_api_key():
        """Generate a new API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(api_key):
        """Hash an API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(api_key):
        """Verify an API key and return the associated organization"""
        key_hash = AuthService.hash_api_key(api_key)
        api_key_obj = APIKey.query.filter_by(key_hash=key_hash, is_active=True).first()
        
        if api_key_obj and (not api_key_obj.expires_at or api_key_obj.expires_at > datetime.utcnow()):
            # Update last used timestamp
            api_key_obj.last_used = datetime.utcnow()
            db.session.commit()
            return api_key_obj.organization
        
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = AuthService.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Get user from database
        current_user = User.query.get(payload['user_id'])
        if not current_user or not current_user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def api_key_required(f):
    """Decorator to require valid API key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key is missing'}), 401
        
        organization = AuthService.verify_api_key(api_key)
        if not organization:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(organization, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

