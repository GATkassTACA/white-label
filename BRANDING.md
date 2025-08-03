# White Label Chat SaaS - Client Branding Guide

This document explains how to set up and use client-specific branding configurations in the White Label Chat SaaS application.

## Overview

The branding system allows you to create custom configurations for different clients, each with their own:
- Company name and logo
- Color schemes  
- Welcome messages
- Feature sets
- User limits
- Custom styling

## Configuration Structure

All branding configurations are stored in `app/branding/configs.json` as a JSON object with client keys.

## Available Clients

Currently configured clients:

### ScarlettAI
- **URL**: `http://localhost:5000/scarlettai`
- **API**: `http://localhost:5000/api/branding/scarlettai`
- **Primary Color**: #e84393 (Pink)
- **Features**: Real-time messaging, file sharing, custom themes, **PDF document scanning**
- **Limits**: 10 rooms, 50 users per room, 30-day message history

### PharmaHub  
- **URL**: `http://localhost:5000/pharmahub`
- **API**: `http://localhost:5000/api/branding/pharmahub`
- **Primary Color**: #0984e3 (Blue)
- **Features**: Real-time messaging, file sharing, voice calls, custom themes, **PDF document scanning**
- **Limits**: 20 rooms, 100 users per room, 90-day message history

## API Endpoints

### Get All Available Clients
```
GET /api/clients
```
Returns:
```json
{
  "clients": ["scarlettai", "pharmahub"],
  "count": 2
}
```

### Get Client-Specific Branding
```
GET /api/branding/{client}
```
Examples:
- `/api/branding/scarlettai`
- `/api/branding/pharmahub`

### Get Default Branding
```
GET /api/branding
```

## Client URLs

Each client can access their branded version at:
- `/` - Default branding
- `/{client}` - Client-specific branding

Examples:
- `http://localhost:5000/scarlettai`
- `http://localhost:5000/pharmahub`

## Document Scanning Feature

The platform now includes a comprehensive PDF document scanning feature available at `/documents`:

### Features
- **Multi-method PDF processing**: PyPDF2, pdfplumber, and OCR with Tesseract
- **Drag & drop upload interface** with real-time feedback
- **Content analysis**: Text extraction, word counts, keyword analysis
- **Processing history**: Track all document processing attempts
- **File validation**: 10MB limit, PDF format validation
- **Automatic fallback**: If one extraction method fails, others are tried

### URLs
- `/documents/` - Main document scanner interface
- `/documents/history` - View processing history
- `/documents/api/process` - API endpoint for document processing

### Supported File Types
- PDF documents (up to 10MB)
- Multiple extraction methods ensure high success rate

### Integration
The document scanning feature is available to all clients and can be accessed from any branded interface.

## Configuration Format

Each client configuration includes:

```json
{
  "client_name": {
    "company_name": "Client Name",
    "primary_color": "#hex",
    "secondary_color": "#hex", 
    "logo_url": "path/to/logo",
    "welcome_message": "Welcome message",
    "chat_placeholder": "Input placeholder text",
    "footer_text": "Footer text",
    "features": {
      "real_time_messaging": true,
      "file_sharing": true,
      "voice_calls": false,
      "video_calls": false,
      "custom_themes": true
    },
    "limits": {
      "max_rooms": 10,
      "max_users_per_room": 50,
      "message_history_days": 30
    },
    "styling": {
      "font_family": "Font name",
      "border_radius": "8px",
      "box_shadow": "CSS shadow"
    }
  }
}
```

## Adding New Clients

### Option 1: Using the Branding Wizard (Recommended)

1. Navigate to `/wizard` in your browser
2. Fill out the branding wizard form:
   - **Client ID**: Unique identifier (letters, numbers, underscores only)
   - **Company Name**: Display name for the client
   - **Colors**: Primary and secondary brand colors
   - **Logo**: Upload logo file (PNG, JPG, GIF, SVG)
   - **Messages**: Welcome message, chat placeholder, footer text
   - **Features**: Enable/disable file sharing, voice/video calls
   - **Limits**: Configure room limits, user limits, message history
   - **Styling**: Choose fonts and visual styling options
3. Click "Create Branding" to generate the client configuration
4. You'll be redirected to the new client's branded chat interface

### Option 2: Manual Configuration

1. Add a new client configuration to `app/branding/configs.json`
2. Create logo files in `static/images/`
3. Test the configuration at `/{client_name}`

## Branding Wizard Features

The wizard provides:
- **Live Preview**: See changes in real-time as you configure
- **Client ID Validation**: Ensures unique client identifiers
- **Logo Upload**: Automatic handling of logo files
- **Feature Toggles**: Easy enable/disable of platform features
- **Advanced Styling**: Professional styling options
- **Form Validation**: Prevents invalid configurations

Access the wizard at: `http://localhost:5000/wizard`

## Logo Files

Logo files should be placed in `static/images/` and can be:
- SVG (recommended for scalability)
- PNG (for complex graphics)
- JPG (for photographs)

Current logos:
- `static/images/scarlettai-logo.svg`
- `static/images/pharmahub-logo.svg`

## Testing

The branding system is covered by tests in:
- `tests/test_routes.py` - Route testing
- Tests verify default branding, custom branding, and API endpoints

Run tests with:
```bash
.\run_tests.bat full
```

## Deployment Notes

When deploying:
1. Ensure `app/branding/configs.json` is included
2. Include all logo files in `static/images/`
3. Set appropriate environment variables for production
4. Test all client URLs and API endpoints

## Security Considerations

- Client names in URLs are used as keys to look up configurations
- Invalid client names fall back to default configuration
- No user input is directly used in configuration loading
- All client configurations are pre-defined in the JSON file
