from flask_socketio import emit, join_room, leave_room
from flask import request
from datetime import datetime, timezone
from models import db, User, Message, Room, Client, Analytics
import uuid

# Store active users and rooms in memory (for session management)
active_users = {}
room_users = {}

def register_socket_events(socketio):
    """Register all socket event handlers"""
    
    @socketio.on('connect')
    def on_connect(auth):
        """Handle user connection"""
        if auth:
            print(f"Connection authenticated: {auth}")
        else:
            print("Anonymous connection")
        # Create or get guest user
        user_id = str(uuid.uuid4())
        username = f"User_{user_id[:8]}"
        
        # Create guest user in database
        user = User(
            user_id=user_id,
            username=username
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Store in memory for session
            active_users[request.sid] = {
                'user_id': user_id,
                'username': username,
                'connected_at': datetime.now(timezone.utc)
            }
            
            emit('user_connected', {
                'user_id': user_id,
                'username': username,
                'message': f'{username} connected to the chat'
            })
            
            # Track analytics
            analytics = Analytics(
                metric_type='user_connected',
                user_id=user_id,
                extra_data={'session_id': request.sid}
            )
            db.session.add(analytics)
            db.session.commit()
            
            print(f"User {username} connected with session {request.sid}")
            
        except Exception as e:
            print(f"Error creating user: {e}")
            db.session.rollback()
    
    @socketio.on('disconnect')
    def on_disconnect():
        """Handle user disconnection"""
        if request.sid in active_users:
            user_info = active_users[request.sid]
            username = user_info['username']
            
            # Remove user from all rooms
            for room_id in list(room_users.keys()):
                if request.sid in room_users.get(room_id, set()):
                    room_users[room_id].discard(request.sid)
                    emit('user_left_room', {
                        'username': username,
                        'room_id': room_id
                    }, room=room_id)
            
            del active_users[request.sid]
            print(f"User {username} disconnected")
    
    @socketio.on('join_room')
    def on_join_room(data):
        """Handle user joining a room"""
        room_id = data.get('room_id', 'general')
        
        if request.sid in active_users:
            user_info = active_users[request.sid]
            username = user_info['username']
            
            join_room(room_id)
            
            # Track room membership
            if room_id not in room_users:
                room_users[room_id] = set()
            room_users[room_id].add(request.sid)
            
            emit('user_joined_room', {
                'username': username,
                'room_id': room_id,
                'message': f'{username} joined the room'
            }, room=room_id)
            
            # Send room info to the user
            emit('room_joined', {
                'room_id': room_id,
                'user_count': len(room_users[room_id])
            })
    
    @socketio.on('leave_room')
    def on_leave_room(data):
        """Handle user leaving a room"""
        room_id = data.get('room_id', 'general')
        
        if request.sid in active_users:
            user_info = active_users[request.sid]
            username = user_info['username']
            
            leave_room(room_id)
            
            # Remove from room tracking
            if room_id in room_users:
                room_users[room_id].discard(request.sid)
            
            emit('user_left_room', {
                'username': username,
                'room_id': room_id,
                'message': f'{username} left the room'
            }, room=room_id)
    
    @socketio.on('send_message')
    def on_send_message(data):
        """Handle sending a message"""
        if request.sid in active_users:
            user_info = active_users[request.sid]
            username = user_info['username']
            user_id = user_info['user_id']
            message_content = data.get('message', '')
            room_id_name = data.get('room_id', 'general')
            
            if message_content.strip():
                try:
                    # Get or create room
                    room = Room.query.filter_by(name=room_id_name).first()
                    if not room:
                        room = Room(
                            name=room_id_name,
                            description=f"Auto-created room: {room_id_name}",
                            is_private=False,
                            max_users=50
                        )
                        db.session.add(room)
                        db.session.commit()
                    
                    # Get user from database
                    user = User.query.get(user_id)
                    if not user:
                        print(f"User {user_id} not found in database")
                        return
                    
                    # Create message in database
                    message = Message(
                        content=message_content,
                        message_type='text',
                        user_id=user_id,
                        room_id=room.id,
                        extra_data={'session_id': request.sid}
                    )
                    
                    db.session.add(message)
                    db.session.commit()
                    
                    # Prepare message data for broadcast
                    message_data = {
                        'id': message.id,
                        'user_id': user_id,
                        'username': username,
                        'message': message_content,
                        'timestamp': message.created_at.isoformat(),
                        'room_id': room_id_name,
                        'message_type': 'text'
                    }
                    
                    # Broadcast to room (or all users if general room)
                    if room_id_name and room_id_name != 'general':
                        emit('receive_message', message_data, room=room_id_name)
                    else:
                        emit('receive_message', message_data, broadcast=True)
                    
                    # Track analytics
                    analytics = Analytics(
                        metric_type='message_sent',
                        user_id=user_id,
                        room_id=room.id,
                        extra_data={'message_length': len(message_content)}
                    )
                    db.session.add(analytics)
                    db.session.commit()
                    
                except Exception as e:
                    print(f"Error saving message: {e}")
                    db.session.rollback()
    
    @socketio.on('typing')
    def on_typing(data):
        """Handle typing indicators"""
        if request.sid in active_users:
            user_info = active_users[request.sid]
            room_id = data.get('room_id', 'general')
            
            emit('user_typing', {
                'username': user_info['username'],
                'room_id': room_id
            }, room=room_id, include_self=False)
    
    @socketio.on('stop_typing')
    def on_stop_typing(data):
        """Handle stop typing indicators"""
        if request.sid in active_users:
            user_info = active_users[request.sid]
            room_id = data.get('room_id', 'general')
            
            emit('user_stop_typing', {
                'username': user_info['username'],
                'room_id': room_id
            }, room=room_id, include_self=False)
