from flask_socketio import emit, join_room, leave_room
from flask import request
from datetime import datetime
import uuid

# Store active users and rooms in memory (in production, use Redis or database)
active_users = {}
room_users = {}

def register_socket_events(socketio):
    """Register all socket event handlers"""
    
    @socketio.on('connect')
    def on_connect():
        """Handle user connection"""
        user_id = str(uuid.uuid4())
        username = f"User_{user_id[:8]}"
        
        active_users[request.sid] = {
            'user_id': user_id,
            'username': username,
            'connected_at': datetime.now()
        }
        
        emit('user_connected', {
            'user_id': user_id,
            'username': username,
            'message': f'{username} connected to the chat'
        })
        
        print(f"User {username} connected with session {request.sid}")
    
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
            message = data.get('message', '')
            room_id = data.get('room_id', 'general')
            
            if message.strip():
                message_data = {
                    'user_id': user_info['user_id'],
                    'username': username,
                    'message': message,
                    'timestamp': datetime.now().isoformat(),
                    'room_id': room_id
                }
                
                # Broadcast to room (or all users if no room specified)
                if room_id and room_id != 'general':
                    emit('receive_message', message_data, room=room_id)
                else:
                    emit('receive_message', message_data, broadcast=True)
    
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
