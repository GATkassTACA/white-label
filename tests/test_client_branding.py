import pytest
import json
from unittest.mock import patch, mock_open

class TestClientBranding:
    """Test cases for client-specific branding"""
    
    def test_get_available_clients(self, client):
        """Test the clients API endpoint"""
        response = client.get('/api/clients')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'clients' in data
        assert 'count' in data
        assert isinstance(data['clients'], list)
        assert 'scarlettai' in data['clients']
        assert 'pharmahub' in data['clients']
        assert data['count'] == 2
    
    def test_get_scarlettai_branding(self, client):
        """Test ScarlettAI specific branding"""
        response = client.get('/api/branding/scarlettai')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['company_name'] == 'ScarlettAI'
        assert data['primary_color'] == '#e84393'
        assert data['welcome_message'] == 'Welcome to ScarlettAI Chat!'
        assert 'scarlettai-logo.svg' in data['logo_url']
    
    def test_get_pharmahub_branding(self, client):
        """Test PharmaHub specific branding"""
        response = client.get('/api/branding/pharmahub')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['company_name'] == 'PharmaHub'
        assert data['primary_color'] == '#0984e3'
        assert data['welcome_message'] == 'Chat with PharmaHub\'s assistant'
        assert 'pharmahub-logo.svg' in data['logo_url']
    
    def test_get_invalid_client_branding(self, client):
        """Test invalid client falls back to default"""
        response = client.get('/api/branding/nonexistent')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should return default branding
        assert data['company_name'] == 'ChatHub Pro'
    
    def test_client_specific_routes(self, client):
        """Test client-specific index routes"""
        # Test ScarlettAI route
        response = client.get('/scarlettai')
        assert response.status_code == 200
        assert b'ScarlettAI' in response.data
        
        # Test PharmaHub route  
        response = client.get('/pharmahub')
        assert response.status_code == 200
        assert b'PharmaHub' in response.data
    
    def test_nonexistent_client_route(self, client):
        """Test nonexistent client route falls back to default"""
        response = client.get('/nonexistent')
        assert response.status_code == 200
        # Should use default branding
        assert b'ChatHub Pro' in response.data

class TestBrandingConfigurationLoading:
    """Test branding configuration loading functionality"""
    
    def test_load_branding_with_client(self, app):
        """Test loading branding for specific client"""
        from app.routes.chat import load_branding_config
        
        with app.app_context():
            # Test with valid client
            config = load_branding_config('scarlettai')
            assert config['company_name'] == 'ScarlettAI'
            assert config['primary_color'] == '#e84393'
    
    def test_load_branding_without_client(self, app):
        """Test loading default branding"""
        from app.routes.chat import load_branding_config
        
        with app.app_context():
            # Test without client (should return default)
            config = load_branding_config()
            assert config['company_name'] == 'ChatHub Pro'
    
    def test_load_branding_invalid_client(self, app):
        """Test loading branding for invalid client"""
        from app.routes.chat import load_branding_config
        
        with app.app_context():
            # Test with invalid client (should return default)
            config = load_branding_config('invalid_client')
            assert config['company_name'] == 'ChatHub Pro'
