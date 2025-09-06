from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from src.models.user import db

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    subscription_tier = db.Column(db.String(50), nullable=False, default='basic')
    api_quota_limit = db.Column(db.Integer, default=1000)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='organization', lazy=True)
    api_keys = db.relationship('APIKey', backref='organization', lazy=True)
    api_configurations = db.relationship('APIConfiguration', backref='organization', lazy=True)
    support_tickets = db.relationship('SupportTicket', backref='organization', lazy=True)
    
    def __repr__(self):
        return f'<Organization {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subscription_tier': self.subscription_tier,
            'api_quota_limit': self.api_quota_limit,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class APIKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    key_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    permissions = db.Column(db.JSON)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<APIKey {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'permissions': self.permissions,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }

class APIConfiguration(db.Model):
    __tablename__ = 'api_configurations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    api_type = db.Column(db.String(50), nullable=False)  # 'rider_external', 'openai', etc.
    credentials = db.Column(db.JSON, nullable=False)  # Encrypted credentials
    settings = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<APIConfiguration {self.api_type} for {self.organization_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'api_type': self.api_type,
            'settings': self.settings,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

