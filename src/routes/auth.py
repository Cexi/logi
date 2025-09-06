from flask import Blueprint, request, jsonify
from src.models.user import User, db
from src.models.organization import Organization, APIKey
from src.services.auth_service import AuthService, token_required, admin_required
from src.services.encryption_service import EncryptionService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login
        user.update_last_login()
        
        # Generate tokens
        tokens = AuthService.generate_tokens(user)
        
        return jsonify({
            'user': user.to_dict(),
            'organization': user.organization.to_dict() if user.organization else None,
            **tokens
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400
        
        payload = AuthService.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return jsonify({'error': 'Invalid refresh token'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        # Generate new tokens
        tokens = AuthService.generate_tokens(user)
        
        return jsonify(tokens), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user (admin only or during setup)"""
    try:
        data = request.get_json()
        
        required_fields = ['email', 'password', 'first_name', 'last_name', 'organization_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create organization if it doesn't exist
        organization = Organization.query.filter_by(name=data['organization_name']).first()
        if not organization:
            organization = Organization(
                name=data['organization_name'],
                subscription_tier=data.get('subscription_tier', 'basic')
            )
            db.session.add(organization)
            db.session.flush()  # Get the ID
        
        # Create user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            organization_id=organization.id,
            role=data.get('role', 'admin')  # First user is admin
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        tokens = AuthService.generate_tokens(user)
        
        return jsonify({
            'user': user.to_dict(),
            'organization': organization.to_dict(),
            **tokens
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile"""
    return jsonify({
        'user': current_user.to_dict(),
        'organization': current_user.organization.to_dict() if current_user.organization else None
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update current user profile"""
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            current_user.first_name = data['first_name']
        if 'last_name' in data:
            current_user.last_name = data['last_name']
        
        # Only admin can change role
        if 'role' in data and current_user.role == 'admin':
            current_user.role = data['role']
        
        db.session.commit()
        
        return jsonify({'user': current_user.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Change user password"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 400
        
        current_user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api-keys', methods=['GET'])
@token_required
@admin_required
def get_api_keys(current_user):
    """Get organization API keys"""
    api_keys = APIKey.query.filter_by(
        organization_id=current_user.organization_id,
        is_active=True
    ).all()
    
    return jsonify({
        'api_keys': [key.to_dict() for key in api_keys]
    }), 200

@auth_bp.route('/api-keys', methods=['POST'])
@token_required
@admin_required
def create_api_key(current_user):
    """Create new API key"""
    try:
        data = request.get_json()
        name = data.get('name')
        permissions = data.get('permissions', {})
        
        if not name:
            return jsonify({'error': 'API key name is required'}), 400
        
        # Generate API key
        api_key = AuthService.generate_api_key()
        key_hash = AuthService.hash_api_key(api_key)
        
        # Create API key record
        api_key_obj = APIKey(
            organization_id=current_user.organization_id,
            key_hash=key_hash,
            name=name,
            permissions=permissions
        )
        
        db.session.add(api_key_obj)
        db.session.commit()
        
        return jsonify({
            'api_key': api_key,  # Return the actual key only once
            'key_info': api_key_obj.to_dict(),
            'message': 'API key created successfully. Save it securely as it won\'t be shown again.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api-keys/<key_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_api_key(current_user, key_id):
    """Delete API key"""
    try:
        api_key = APIKey.query.filter_by(
            id=key_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not api_key:
            return jsonify({'error': 'API key not found'}), 404
        
        api_key.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'API key deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout user (client-side token removal)"""
    return jsonify({'message': 'Logged out successfully'}), 200

