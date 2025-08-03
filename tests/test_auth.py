import pytest
import uuid
from services.auth import AuthService
from unittest.mock import patch
import os

class TestAuthService:
    """Test cases for authentication service"""
    
    def test_generate_token(self, app):
        """Test JWT token generation"""
        user_id = str(uuid.uuid4())
        username = "testuser"
        
        with app.app_context():
            token = AuthService.generate_token(user_id, username)
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0
    
    def test_verify_valid_token(self, app):
        """Test verifying a valid token"""
        user_id = str(uuid.uuid4())
        username = "testuser"
        
        with app.app_context():
            # Generate token
            token = AuthService.generate_token(user_id, username)
            
            # Verify token
            result = AuthService.verify_token(token)
            
            assert result['valid'] is True
            assert result['user_id'] == user_id
            assert result['username'] == username
    
    def test_verify_invalid_token(self, app):
        """Test verifying an invalid token"""
        with app.app_context():
            result = AuthService.verify_token("invalid-token")
            
            assert result['valid'] is False
            assert 'error' in result
    
    def test_create_guest_user(self):
        """Test creating a guest user"""
        guest = AuthService.create_guest_user()
        
        assert 'user_id' in guest
        assert 'username' in guest
        assert guest['is_guest'] is True
        assert guest['username'].startswith('Guest_')
        assert len(guest['user_id']) > 0
    
    def test_validate_username_valid(self):
        """Test validating valid usernames"""
        valid_usernames = ["user123", "test_user", "user-name", "ValidUser"]
        
        for username in valid_usernames:
            is_valid, message = AuthService.validate_username(username)
            assert is_valid is True, f"Username '{username}' should be valid"
    
    def test_validate_username_invalid(self):
        """Test validating invalid usernames"""
        invalid_usernames = [
            "",  # Empty
            "ab",  # Too short
            "a" * 21,  # Too long
            "user@name",  # Invalid character
            "user name",  # Space
            "user.name",  # Dot
            "user#name"  # Hash
        ]
        
        for username in invalid_usernames:
            is_valid, message = AuthService.validate_username(username)
            assert is_valid is False, f"Username '{username}' should be invalid"
            assert len(message) > 0
    
    def test_validate_username_edge_cases(self):
        """Test username validation edge cases"""
        # Exactly 3 characters (minimum)
        is_valid, _ = AuthService.validate_username("abc")
        assert is_valid is True
        
        # Exactly 20 characters (maximum)
        is_valid, _ = AuthService.validate_username("a" * 20)
        assert is_valid is True
        
        # None username
        is_valid, _ = AuthService.validate_username(None)
        assert is_valid is False
