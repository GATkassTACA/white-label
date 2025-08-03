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
- **Features**: Real-time messaging, file sharing, custom themes
- **Limits**: 10 rooms, 50 users per room, 30-day message history

### PharmaHub  
- **URL**: `http://localhost:5000/pharmahub`
- **API**: `http://localhost:5000/api/branding/pharmahub`
- **Primary Color**: #0984e3 (Blue)
- **Features**: Real-time messaging, file sharing, voice calls, custom themes
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

1. Add a new client configuration to `app/branding/configs.json`
2. Create logo files in `static/images/`
3. Test the configuration at `/{client_name}`

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
