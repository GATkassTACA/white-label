import pytest
import json
from unittest.mock import patch, mock_open

class TestChatRoutes:
    """Test cases for chat routes"""
    
    def test_index_route(self, client):
        """Test the main index route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ChatHub Pro' in response.data  # Default branding name
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'white-label-chat'
    
    def test_get_rooms(self, client):
        """Test get rooms endpoint"""
        response = client.get('/api/rooms')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check room structure
        room = data[0]
        assert 'id' in room
        assert 'name' in room
        assert 'users' in room
    
    def test_get_branding_default(self, client):
        """Test branding endpoint with default config"""
        response = client.get('/api/branding')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'company_name' in data
        assert 'primary_color' in data
        assert 'welcome_message' in data
    
    @patch('builtins.open', mock_open(read_data='{"company_name": "Custom Chat", "primary_color": "#123456"}'))
    def test_get_branding_custom(self, client):
        """Test branding endpoint with custom config"""
        with patch('os.path.join'):
            response = client.get('/api/branding')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['company_name'] == 'Custom Chat'
            assert data['primary_color'] == '#123456'
    
    def test_index_with_custom_branding(self, client, sample_branding):
        """Test index page renders with custom branding"""
        with patch('app.routes.chat.load_branding_config', return_value=sample_branding):
            response = client.get('/')
            assert response.status_code == 200
            assert b'Test Chat' in response.data
            assert b'#ff0000' in response.data

class TestBrandingConfiguration:
    """Test branding configuration loading"""
    
    def test_load_branding_file_not_found(self, app):
        """Test loading branding when config file doesn't exist"""
        from app.routes.chat import load_branding_config
        
        with app.app_context():
            with patch('builtins.open', side_effect=FileNotFoundError):
                config = load_branding_config()
                
                # Should return default config
                assert config['company_name'] == 'ChatSaaS'
                assert config['primary_color'] == '#007bff'
    
    def test_load_branding_valid_json(self, app):
        """Test loading valid branding configuration"""
        from app.routes.chat import load_branding_config
        
        test_config = '{"company_name": "Test", "primary_color": "#000"}'
        
        with app.app_context():
            with patch('builtins.open', mock_open(read_data=test_config)):
                with patch('os.path.join'):
                    config = load_branding_config()
                    
                    assert config['company_name'] == 'Test'
                    assert config['primary_color'] == '#000'
