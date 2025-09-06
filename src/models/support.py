from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from src.models.user import db

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='open')  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    category = db.Column(db.String(50))  # api_issue, billing, feature_request, bug, other
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id'))
    rider_id = db.Column(db.String(100))  # Reference to rider in external system
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    messages = db.relationship('TicketMessage', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SupportTicket {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'category': self.category,
            'assigned_to': self.assigned_to,
            'rider_id': self.rider_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'message_count': len(self.messages) if self.messages else 0
        }

class TicketMessage(db.Model):
    __tablename__ = 'ticket_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = db.Column(db.String(36), db.ForeignKey('support_tickets.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)  # Internal notes vs customer-facing
    message_type = db.Column(db.String(20), default='text')  # text, system, attachment
    attachments = db.Column(db.JSON)  # Store file paths/URLs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TicketMessage {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'message': self.message,
            'is_internal': self.is_internal,
            'message_type': self.message_type,
            'attachments': self.attachments,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # cash_threshold, no_show, off_zone, battery_low
    rider_id = db.Column(db.String(100))  # Reference to rider in external system
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved
    data = db.Column(db.JSON)  # Additional alert data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    # WhatsApp notification fields
    whatsapp_sent = db.Column(db.Boolean, default=False)
    whatsapp_sent_at = db.Column(db.DateTime)
    whatsapp_message_id = db.Column(db.String(255))
    whatsapp_status = db.Column(db.String(50))  # sent, delivered, read, failed
    rider_phone = db.Column(db.String(20))  # Rider's WhatsApp number
    
    def __repr__(self):
        return f'<Alert {self.alert_type} - {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'alert_type': self.alert_type,
            'rider_id': self.rider_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'whatsapp_sent': self.whatsapp_sent,
            'whatsapp_sent_at': self.whatsapp_sent_at.isoformat() if self.whatsapp_sent_at else None,
            'whatsapp_status': self.whatsapp_status,
            'rider_phone': self.rider_phone
        }

