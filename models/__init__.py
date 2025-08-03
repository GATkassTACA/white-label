"""Database models for the white-label chat application."""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON
import uuid

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and user management."""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for guest users
    full_name = db.Column(db.String(200), nullable=True)
    
    # User type: 'guest', 'registered', 'admin'
    user_type = db.Column(db.String(20), default='guest')
    is_active = db.Column(db.Boolean, default=True)
    
    # Authentication fields
    last_login = db.Column(db.DateTime, nullable=True)
    password_reset_token = db.Column(db.String(255), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255), nullable=True)
    
    # Client association for multi-tenancy
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    messages = db.relationship('Message', backref='author', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def is_guest(self):
        """Backward compatibility property"""
        return self.user_type == 'guest'
    
    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.user_type == 'admin'
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'user_type': self.user_type,
            'is_active': self.is_active,
            'is_guest': self.is_guest,
            'is_admin': self.is_admin,
            'email_verified': self.email_verified,
            'client_id': self.client_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data.update({
                'password_reset_token': self.password_reset_token,
                'password_reset_expires': self.password_reset_expires.isoformat() if self.password_reset_expires else None,
                'email_verification_token': self.email_verification_token
            })
        
        return data

class Client(db.Model):
    """Client model for white-label configurations."""
    __tablename__ = 'clients'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_name = db.Column(db.String(100), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    
    # Branding
    primary_color = db.Column(db.String(7), default='#007bff')  # Hex color
    secondary_color = db.Column(db.String(7), default='#6c757d')
    logo_url = db.Column(db.String(500), nullable=True)
    
    # Configuration (stored as JSON)
    features = db.Column(JSON, default={'chat': True, 'documents': True, 'analytics': False})
    settings = db.Column(JSON, default={})
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    messages = db.relationship('Message', backref='client', lazy='dynamic')
    documents = db.relationship('Document', backref='client', lazy='dynamic')
    
    def __repr__(self):
        return f'<Client {self.client_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_name': self.client_name,
            'company_name': self.company_name,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'logo_url': self.logo_url,
            'features': self.features,
            'settings': self.settings,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Room(db.Model):
    """Chat room model."""
    __tablename__ = 'rooms'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Room settings
    is_private = db.Column(db.Boolean, default=False)
    max_users = db.Column(db.Integer, default=50)
    
    # Client association
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    messages = db.relationship('Message', backref='room', lazy='dynamic')
    
    def __repr__(self):
        return f'<Room {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_private': self.is_private,
            'max_users': self.max_users,
            'client_id': self.client_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Message(db.Model):
    """Message model for chat messages."""
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, file, system, etc.
    
    # Relationships
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.String(36), db.ForeignKey('rooms.id'), nullable=True)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=True)
    
    # Metadata
    extra_data = db.Column(JSON, default={})  # For file info, reactions, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    edited_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Message {self.id[:8]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'message_type': self.message_type,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'client_id': self.client_id,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'author': self.author.to_dict() if self.author else None
        }

class Document(db.Model):
    """Document model for file uploads and processing."""
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    
    # Processing status
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    processed_content = db.Column(db.Text, nullable=True)  # Extracted text content
    
    # Relationships
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=True)
    
    # Metadata
    extra_data = db.Column(JSON, default={})  # Processing info, page count, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Document {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'status': self.status,
            'user_id': self.user_id,
            'client_id': self.client_id,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class Analytics(db.Model):
    """Analytics model for tracking usage metrics."""
    __tablename__ = 'analytics'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Metric information
    metric_type = db.Column(db.String(50), nullable=False)  # message_sent, user_joined, etc.
    metric_value = db.Column(db.Float, default=1.0)
    
    # Dimensions
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    room_id = db.Column(db.String(36), db.ForeignKey('rooms.id'), nullable=True)
    
    # Additional data
    extra_data = db.Column(JSON, default={})
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Analytics {self.metric_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
