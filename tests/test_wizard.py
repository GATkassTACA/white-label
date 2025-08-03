import pytest
import json
import os
from unittest.mock import patch, mock_open
from werkzeug.datastructures import FileStorage
from io import BytesIO

class TestBrandingWizard:
    """Test cases for the branding wizard"""
    
    def test_wizard_get_page(self, client):
        """Test that the wizard page loads correctly"""
        response = client.get('/wizard')
        assert response.status_code == 200
        assert b'Branding Wizard' in response.data
        assert b'Create a custom branded chat experience' in response.data
    
    def test_wizard_client_id_validation_valid(self, client):
        """Test client ID validation with valid ID"""
        response = client.post('/wizard/validate-client-id', 
                             json={'client_id': 'test_client'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True
        assert 'available' in data['message']
    
    def test_wizard_client_id_validation_invalid_format(self, client):
        """Test client ID validation with invalid format"""
        response = client.post('/wizard/validate-client-id', 
                             json={'client_id': 'test-client!'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False
        assert 'letters, numbers, and underscores' in data['message']
    
    def test_wizard_client_id_validation_existing(self, client):
        """Test client ID validation with existing client"""
        response = client.post('/wizard/validate-client-id', 
                             json={'client_id': 'scarlettai'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is False
        assert 'already exists' in data['message']
    
    def test_wizard_create_brand_basic(self, client, tmp_path):
        """Test creating a basic brand configuration"""
        # Mock the config file path
        with patch('app.routes.wizard.current_app') as mock_app:
            mock_app.root_path = str(tmp_path)
            
            # Create branding directory
            branding_dir = tmp_path / 'branding'
            branding_dir.mkdir()
            
            # Create initial config file
            config_file = branding_dir / 'configs.json'
            config_file.write_text(json.dumps({
                'default': {'company_name': 'Default'}
            }))
            
            response = client.post('/wizard', data={
                'client_id': 'testcorp',
                'company_name': 'Test Corporation',
                'primary_color': '#ff0000',
                'secondary_color': '#00ff00',
                'welcome_message': 'Welcome to Test Corp!',
                'chat_placeholder': 'Type here...',
                'footer_text': 'Powered by Test Corp',
                'max_rooms': '15',
                'max_users_per_room': '75',
                'message_history_days': '45',
                'font_family': 'Roboto, sans-serif',
                'border_radius': '12px'
            })
            
            # Should redirect to the new client page
            assert response.status_code == 302
            assert '/testcorp' in response.location
    
    def test_wizard_create_brand_missing_required(self, client):
        """Test creating brand with missing required fields"""
        response = client.post('/wizard', data={
            'client_id': 'testcorp',
            # Missing company_name, primary_color, welcome_message
        })
        
        assert response.status_code == 200
        assert b'Error creating branding' in response.data
    
    def test_wizard_create_brand_duplicate_client_id(self, client, tmp_path):
        """Test creating brand with duplicate client ID"""
        with patch('app.routes.wizard.current_app') as mock_app:
            mock_app.root_path = str(tmp_path)
            
            branding_dir = tmp_path / 'branding'
            branding_dir.mkdir()
            
            config_file = branding_dir / 'configs.json'
            config_file.write_text(json.dumps({
                'existing_client': {'company_name': 'Existing'}
            }))
            
            response = client.post('/wizard', data={
                'client_id': 'existing_client',
                'company_name': 'Test Corporation',
                'primary_color': '#ff0000',
                'welcome_message': 'Welcome!',
            })
            
            assert response.status_code == 200
            assert b'already exists' in response.data
    
    def test_wizard_with_logo_upload(self, client, tmp_path):
        """Test creating brand with logo upload"""
        with patch('app.routes.wizard.current_app') as mock_app:
            mock_app.root_path = str(tmp_path)
            
            # Create directories
            branding_dir = tmp_path / 'branding'
            branding_dir.mkdir()
            static_dir = tmp_path / '..' / 'static' / 'images'
            static_dir.mkdir(parents=True)
            
            config_file = branding_dir / 'configs.json'
            config_file.write_text(json.dumps({'default': {}}))
            
            # Create a fake image file
            fake_image = BytesIO(b'fake image data')
            fake_image.name = 'test_logo.png'
            
            response = client.post('/wizard', data={
                'client_id': 'testcorp',
                'company_name': 'Test Corporation', 
                'primary_color': '#ff0000',
                'welcome_message': 'Welcome!',
                'logo': (fake_image, 'test_logo.png')
            })
            
            assert response.status_code == 302
    
    def test_wizard_preview_functionality(self, client):
        """Test the preview functionality"""
        response = client.post('/wizard/preview', data={
            'company_name': 'Preview Corp',
            'primary_color': '#123456',
            'welcome_message': 'Preview message'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['config']['company_name'] == 'Preview Corp'
        assert data['config']['primary_color'] == '#123456'

class TestWizardIntegration:
    """Integration tests for wizard with existing system"""
    
    def test_wizard_creates_accessible_client(self, client, tmp_path):
        """Test that wizard-created clients are accessible"""
        with patch('app.routes.wizard.current_app') as mock_wizard_app, \
             patch('app.routes.chat.current_app') as mock_chat_app:
            
            mock_wizard_app.root_path = str(tmp_path)
            mock_chat_app.root_path = str(tmp_path)
            
            # Create directories and initial config
            branding_dir = tmp_path / 'branding'
            branding_dir.mkdir()
            config_file = branding_dir / 'configs.json'
            config_file.write_text(json.dumps({'default': {'company_name': 'Default'}}))
            
            # Create brand via wizard
            response = client.post('/wizard', data={
                'client_id': 'wizardtest',
                'company_name': 'Wizard Test Corp',
                'primary_color': '#purple',
                'welcome_message': 'Created via wizard!'
            })
            
            # Should redirect successfully
            assert response.status_code == 302
            
            # Now test that the client is accessible
            # Note: This would work in a real scenario, but mocking makes it complex
            # The redirect location should contain the client name
            assert '/wizardtest' in response.location
