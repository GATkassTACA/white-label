class User:
    """User model for the chat application"""
    
    def __init__(self, user_id, username, email=None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.is_active = True
        self.rooms = set()
        self.created_at = None
        self.last_seen = None
    
    def __repr__(self):
        return f"<User {self.username} ({self.user_id})>"
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'rooms': list(self.rooms),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }
    
    def join_room(self, room_id):
        """Add user to a room"""
        self.rooms.add(room_id)
    
    def leave_room(self, room_id):
        """Remove user from a room"""
        self.rooms.discard(room_id)
    
    def is_in_room(self, room_id):
        """Check if user is in a specific room"""
        return room_id in self.rooms

class Message:
    """Message model for chat messages"""
    
    def __init__(self, message_id, user_id, username, content, room_id='general'):
        self.message_id = message_id
        self.user_id = user_id
        self.username = username
        self.content = content
        self.room_id = room_id
        self.created_at = None
        self.is_edited = False
        self.edited_at = None
    
    def __repr__(self):
        return f"<Message {self.message_id} by {self.username}>"
    
    def to_dict(self):
        """Convert message object to dictionary"""
        return {
            'message_id': self.message_id,
            'user_id': self.user_id,
            'username': self.username,
            'content': self.content,
            'room_id': self.room_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None
        }

class Room:
    """Room model for chat rooms"""
    
    def __init__(self, room_id, name, description=None, max_users=50):
        self.room_id = room_id
        self.name = name
        self.description = description
        self.max_users = max_users
        self.users = set()
        self.created_at = None
        self.is_active = True
    
    def __repr__(self):
        return f"<Room {self.name} ({self.room_id})>"
    
    def to_dict(self):
        """Convert room object to dictionary"""
        return {
            'room_id': self.room_id,
            'name': self.name,
            'description': self.description,
            'max_users': self.max_users,
            'current_users': len(self.users),
            'users': list(self.users),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def add_user(self, user_id):
        """Add a user to the room"""
        if len(self.users) < self.max_users:
            self.users.add(user_id)
            return True
        return False
    
    def remove_user(self, user_id):
        """Remove a user from the room"""
        self.users.discard(user_id)
    
    def is_full(self):
        """Check if room is at capacity"""
        return len(self.users) >= self.max_users
