#!/usr/bin/env python3
"""
Database initialization and migration script.

This script creates the database tables and sets up initial data.
"""

import os
import sys
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from models import db, User, Client, Room, Message, Document, Analytics

def init_database():
    """Initialize the database with tables and sample data."""
    app, _ = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables (for fresh start)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Create sample data
        create_sample_data()
        
        print("✅ Database initialization complete!")

def create_sample_data():
    """Create sample data for development and testing."""
    print("Creating sample data...")
    
    # Create sample clients
    client1 = Client(
        client_name="scarlettai",
        company_name="Scarlett AI",
        primary_color="#FF6B6B",
        secondary_color="#4ECDC4",
        logo_url="https://via.placeholder.com/50x50/FF6B6B/FFFFFF?text=SA",
        features={"chat": True, "documents": True, "analytics": True},
        settings={"welcome_message": "Welcome to Scarlett AI Chat!"}
    )
    
    client2 = Client(
        client_name="pharmahub",
        company_name="PharmaHub",
        primary_color="#4CAF50",
        secondary_color="#2196F3",
        logo_url="https://via.placeholder.com/50x50/4CAF50/FFFFFF?text=PH",
        features={"chat": True, "documents": True, "analytics": False},
        settings={"welcome_message": "Welcome to PharmaHub Support!"}
    )
    
    # Create default client
    default_client = Client(
        client_name="default",
        company_name="ChatSaaS",
        primary_color="#007bff",
        secondary_color="#6c757d",
        logo_url="https://via.placeholder.com/50x50/007bff/FFFFFF?text=CS",
        features={"chat": True, "documents": True, "analytics": True},
        settings={"welcome_message": "Welcome to our chat platform!"}
    )
    
    db.session.add_all([client1, client2, default_client])
    db.session.commit()
    
    # Create sample users with new authentication fields
    from werkzeug.security import generate_password_hash
    
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=generate_password_hash("Admin123!"),
        full_name="System Administrator",
        user_type="admin",
        is_active=True,
        email_verified=True,
        client_id=default_client.id
    )
    
    demo_user = User(
        username="demo_user",
        email="demo@example.com",
        password_hash=generate_password_hash("Demo123!"),
        full_name="Demo User",
        user_type="registered",
        is_active=True,
        email_verified=True,
        client_id=default_client.id
    )
    
    guest_user = User(
        username="Guest_001",
        user_type="guest",
        is_active=True,
        client_id=default_client.id
    )
    
    db.session.add_all([admin_user, demo_user, guest_user])
    db.session.commit()
    
    # Create sample rooms
    general_room = Room(
        name="general",
        description="General chat room",
        is_private=False,
        max_users=100,
        client_id=default_client.id
    )
    
    support_room = Room(
        name="support",
        description="Customer support chat",
        is_private=False,
        max_users=50,
        client_id=client1.id
    )
    
    db.session.add_all([general_room, support_room])
    db.session.commit()
    
    # Create sample messages
    welcome_message = Message(
        content="Welcome to the chat! This is a sample message from the database.",
        message_type="system",
        user_id=admin_user.id,
        room_id=general_room.id,
        client_id=default_client.id
    )
    
    demo_message = Message(
        content="Hello! This is a demo message to show the database integration is working.",
        message_type="text",
        user_id=demo_user.id,
        room_id=general_room.id,
        client_id=default_client.id
    )
    
    db.session.add_all([welcome_message, demo_message])
    db.session.commit()
    
    print(f"✅ Created {Client.query.count()} clients")
    print(f"✅ Created {User.query.count()} users")
    print(f"✅ Created {Room.query.count()} rooms")
    print(f"✅ Created {Message.query.count()} messages")

def reset_database():
    """Reset the database by dropping and recreating all tables."""
    app, _ = create_app()
    
    with app.app_context():
        print("⚠️  WARNING: This will delete all data!")
        confirm = input("Are you sure you want to reset the database? (y/N): ")
        
        if confirm.lower() != 'y':
            print("❌ Database reset cancelled.")
            return
        
        print("Resetting database...")
        init_database()

def show_database_info():
    """Show information about the current database."""
    app, _ = create_app()
    
    with app.app_context():
        print("📊 Database Information:")
        print("=" * 40)
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Clients: {Client.query.count()}")
        print(f"Users: {User.query.count()}")
        print(f"Rooms: {Room.query.count()}")
        print(f"Messages: {Message.query.count()}")
        print(f"Documents: {Document.query.count()}")
        print(f"Analytics records: {Analytics.query.count()}")
        print("=" * 40)
        
        # Show sample data
        print("\n📋 Sample Clients:")
        for client in Client.query.all():
            print(f"  - {client.client_name}: {client.company_name}")
        
        print("\n👥 Sample Users:")
        for user in User.query.limit(5).all():
            print(f"  - {user.username} ({'Guest' if user.is_guest else 'Registered'})")
        
        print("\n💬 Recent Messages:")
        for message in Message.query.order_by(Message.created_at.desc()).limit(3).all():
            print(f"  - {message.author.username}: {message.content[:50]}...")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management script")
    parser.add_argument("command", choices=["init", "reset", "info"], 
                       help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_database()
    elif args.command == "reset":
        reset_database()
    elif args.command == "info":
        show_database_info()
