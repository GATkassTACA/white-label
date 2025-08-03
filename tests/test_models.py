import pytest
from models.user import User, Message, Room
from datetime import datetime

class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self):
        """Test creating a new user"""
        user = User("123", "testuser", "test@example.com")
        
        assert user.user_id == "123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert len(user.rooms) == 0
    
    def test_user_to_dict(self):
        """Test converting user to dictionary"""
        user = User("123", "testuser")
        user_dict = user.to_dict()
        
        assert user_dict['user_id'] == "123"
        assert user_dict['username'] == "testuser"
        assert user_dict['is_active'] is True
        assert user_dict['rooms'] == []
    
    def test_user_join_room(self):
        """Test user joining a room"""
        user = User("123", "testuser")
        user.join_room("general")
        
        assert "general" in user.rooms
        assert user.is_in_room("general") is True
    
    def test_user_leave_room(self):
        """Test user leaving a room"""
        user = User("123", "testuser")
        user.join_room("general")
        user.leave_room("general")
        
        assert "general" not in user.rooms
        assert user.is_in_room("general") is False
    
    def test_user_multiple_rooms(self):
        """Test user in multiple rooms"""
        user = User("123", "testuser")
        user.join_room("general")
        user.join_room("support")
        
        assert len(user.rooms) == 2
        assert user.is_in_room("general") is True
        assert user.is_in_room("support") is True

class TestMessageModel:
    """Test cases for Message model"""
    
    def test_message_creation(self):
        """Test creating a new message"""
        message = Message("msg123", "user123", "testuser", "Hello world!")
        
        assert message.message_id == "msg123"
        assert message.user_id == "user123"
        assert message.username == "testuser"
        assert message.content == "Hello world!"
        assert message.room_id == "general"  # default
        assert message.is_edited is False
    
    def test_message_with_room(self):
        """Test creating message with specific room"""
        message = Message("msg123", "user123", "testuser", "Hello!", "support")
        
        assert message.room_id == "support"
    
    def test_message_to_dict(self):
        """Test converting message to dictionary"""
        message = Message("msg123", "user123", "testuser", "Hello!")
        message_dict = message.to_dict()
        
        assert message_dict['message_id'] == "msg123"
        assert message_dict['user_id'] == "user123"
        assert message_dict['username'] == "testuser"
        assert message_dict['content'] == "Hello!"
        assert message_dict['room_id'] == "general"
        assert message_dict['is_edited'] is False

class TestRoomModel:
    """Test cases for Room model"""
    
    def test_room_creation(self):
        """Test creating a new room"""
        room = Room("general", "General Chat", "Main chat room")
        
        assert room.room_id == "general"
        assert room.name == "General Chat"
        assert room.description == "Main chat room"
        assert room.max_users == 50  # default
        assert len(room.users) == 0
        assert room.is_active is True
    
    def test_room_add_user(self):
        """Test adding user to room"""
        room = Room("general", "General Chat")
        
        result = room.add_user("user123")
        assert result is True
        assert "user123" in room.users
        assert len(room.users) == 1
    
    def test_room_remove_user(self):
        """Test removing user from room"""
        room = Room("general", "General Chat")
        room.add_user("user123")
        room.remove_user("user123")
        
        assert "user123" not in room.users
        assert len(room.users) == 0
    
    def test_room_max_capacity(self):
        """Test room at maximum capacity"""
        room = Room("small", "Small Room", max_users=2)
        
        # Add users up to capacity
        assert room.add_user("user1") is True
        assert room.add_user("user2") is True
        assert room.is_full() is True
        
        # Try to add one more user (should fail)
        assert room.add_user("user3") is False
        assert len(room.users) == 2
    
    def test_room_to_dict(self):
        """Test converting room to dictionary"""
        room = Room("general", "General Chat")
        room.add_user("user123")
        
        room_dict = room.to_dict()
        
        assert room_dict['room_id'] == "general"
        assert room_dict['name'] == "General Chat"
        assert room_dict['max_users'] == 50
        assert room_dict['current_users'] == 1
        assert "user123" in room_dict['users']
        assert room_dict['is_active'] is True
