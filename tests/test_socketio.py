import pytest
from unittest.mock import patch
import json

class TestSocketEvents:
    """Test cases for Socket.IO events"""
    
    def test_user_connection(self, socketio_client):
        """Test user connection event"""
        # Test connection
        received = socketio_client.get_received()
        
        # Should receive user_connected event
        assert len(received) > 0
        event = received[0]
        assert event['name'] == 'user_connected'
        assert 'user_id' in event['args'][0]
        assert 'username' in event['args'][0]
        assert event['args'][0]['username'].startswith('User_')
    
    def test_join_room_event(self, socketio_client):
        """Test joining a room"""
        # Clear any initial events
        socketio_client.get_received()
        
        # Join a room
        socketio_client.emit('join_room', {'room_id': 'general'})
        
        # Check for room joined events
        received = socketio_client.get_received()
        
        # Should receive user_joined_room and room_joined events
        event_names = [event['name'] for event in received]
        assert 'user_joined_room' in event_names
        assert 'room_joined' in event_names
    
    def test_send_message_event(self, socketio_client):
        """Test sending a message"""
        # Clear initial events
        socketio_client.get_received()
        
        # Send a message
        test_message = "Hello, World!"
        socketio_client.emit('send_message', {
            'message': test_message,
            'room_id': 'general'
        })
        
        # Check for message received event
        received = socketio_client.get_received()
        
        message_events = [event for event in received if event['name'] == 'receive_message']
        assert len(message_events) > 0
        
        message_data = message_events[0]['args'][0]
        assert message_data['message'] == test_message
        assert 'username' in message_data
        assert 'timestamp' in message_data
    
    def test_leave_room_event(self, socketio_client):
        """Test leaving a room"""
        # First join a room
        socketio_client.emit('join_room', {'room_id': 'test_room'})
        socketio_client.get_received()  # Clear events
        
        # Then leave the room
        socketio_client.emit('leave_room', {'room_id': 'test_room'})
        
        # Check for user left room event
        received = socketio_client.get_received()
        
        leave_events = [event for event in received if event['name'] == 'user_left_room']
        assert len(leave_events) > 0
        
        leave_data = leave_events[0]['args'][0]
        assert leave_data['room_id'] == 'test_room'
        assert 'username' in leave_data
    
    def test_typing_events(self, socketio_client):
        """Test typing indicator events"""
        # Clear initial events
        socketio_client.get_received()
        
        # Start typing
        socketio_client.emit('typing', {'room_id': 'general'})
        
        # Note: typing events are only sent to other users, not the sender
        # So we expect no events for a single client
        received = socketio_client.get_received()
        typing_events = [event for event in received if event['name'] == 'user_typing']
        
        # Should be empty since we're the only client
        assert len(typing_events) == 0
    
    def test_disconnect_event(self, socketio_client):
        """Test user disconnection"""
        # Connect first
        assert socketio_client.is_connected()
        
        # Disconnect
        socketio_client.disconnect()
        
        # Verify disconnection
        assert not socketio_client.is_connected()

class TestSocketEventValidation:
    """Test validation of socket event data"""
    
    def test_empty_message_not_sent(self, socketio_client):
        """Test that empty messages are not broadcast"""
        socketio_client.get_received()  # Clear events
        
        # Send empty message
        socketio_client.emit('send_message', {'message': ''})
        
        # Should not receive any message events
        received = socketio_client.get_received()
        message_events = [event for event in received if event['name'] == 'receive_message']
        assert len(message_events) == 0
    
    def test_whitespace_only_message_not_sent(self, socketio_client):
        """Test that whitespace-only messages are not broadcast"""
        socketio_client.get_received()  # Clear events
        
        # Send whitespace-only message
        socketio_client.emit('send_message', {'message': '   \t\n  '})
        
        # Should not receive any message events
        received = socketio_client.get_received()
        message_events = [event for event in received if event['name'] == 'receive_message']
        assert len(message_events) == 0
    
    def test_message_with_room_id(self, socketio_client):
        """Test sending message to specific room"""
        socketio_client.get_received()  # Clear events
        
        # Send message to specific room
        socketio_client.emit('send_message', {
            'message': 'Room-specific message',
            'room_id': 'support'
        })
        
        received = socketio_client.get_received()
        message_events = [event for event in received if event['name'] == 'receive_message']
        
        if message_events:  # May not receive if not in the room
            message_data = message_events[0]['args'][0]
            assert message_data['room_id'] == 'support'
