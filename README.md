# White Label Chat SaaS

A customizable, real-time chat application built with Flask and Socket.IO. Perfect for white-label solutions with configurable branding and features.

## Features

- **Real-time messaging** with Socket.IO
- **Customizable branding** via JSON configuration
- **Multi-room support** with user management
- **Authentication system** with JWT tokens
- **Guest user support** for quick access
- **RESTful API** for integration
- **Docker support** for easy deployment
- **Comprehensive test suite** with pytest

## Project Structure

```
white-label-chat-saas/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes/
│   │   ├── __init__.py
│   │   └── chat.py              # Chat routes and API endpoints
│   ├── templates/
│   │   └── base.html            # Main chat interface
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Custom styles
│   │   └── images/              # Logo and images
│   ├── branding/
│   │   └── configs.json         # Branding configuration
│   └── socket_events.py         # Socket.IO event handlers
├── models/
│   └── user.py                  # User, Message, and Room models
├── services/
│   └── auth.py                  # Authentication service
├── tests/                       # Test suite
│   ├── conftest.py              # Test configuration
│   ├── test_routes.py           # Route tests
│   ├── test_models.py           # Model tests
│   ├── test_auth.py             # Authentication tests
│   └── test_socketio.py         # Socket.IO tests
├── config.py                    # Application configuration
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── Dockerfile                   # Docker configuration
├── pyproject.toml              # Tool configuration
└── .env.example                # Environment variables template
```

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/GATkassTACA/white-label.git
cd white-label
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
notepad .env  # Windows
nano .env     # macOS/Linux
```

### 4. Run the Application

```bash
python run.py
```

Visit `http://127.0.0.1:5000` to access the chat application.

## Testing

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m socket        # Socket.IO tests only
```

### Test Commands

```bash
# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=app --cov=models --cov=services --cov-report=html

# Run specific test file
pytest tests/test_routes.py

# Run specific test function
pytest tests/test_routes.py::TestChatRoutes::test_health_.check
```

### Test Coverage

View detailed coverage report:
```bash
pytest --cov-report=html
# Open htmlcov/index.html in your browser
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Branding Configuration
```
GET /api/branding
```

### Available Rooms
```
GET /api/rooms
```

## Socket.IO Events

### Client Events (Sent by client)
- `join_room` - Join a chat room
- `leave_room` - Leave a chat room
- `send_message` - Send a message
- `typing` - Indicate typing
- `stop_typing` - Stop typing indication

### Server Events (Sent by server)
- `user_connected` - User connected
- `user_joined_room` - User joined room
- `user_left_room` - User left room
- `receive_message` - New message received
- `user_typing` - User is typing
- `user_stop_typing` - User stopped typing

## Customization

### Branding Configuration

Edit `app/branding/configs.json`:

```json
{
    "company_name": "Your Chat App",
    "primary_color": "#007bff",
    "secondary_color": "#6c757d",
    "logo_url": "/static/images/your-logo.png",
    "welcome_message": "Welcome to Your Chat!",
    "features": {
        "real_time_messaging": true,
        "file_sharing": false,
        "voice_calls": false,
        "video_calls": false
    }
}
```

### Environment Variables

Key environment variables in `.env`:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
MAX_USERS_PER_ROOM=50
RATE_LIMIT_MESSAGES_PER_MINUTE=60
```

## Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t white-label-chat .

# Run container
docker run -p 5000:5000 -e SECRET_KEY=your-secret-key white-label-chat
```

### Production Considerations

1. **Set a secure SECRET_KEY**
2. **Configure rate limiting**
3. **Set up Redis for scaling** (optional)
4. **Configure HTTPS**
5. **Set up monitoring and logging**

## Development

### Code Formatting

```bash
# Format code with Black
black .

# Check code style with flake8
flake8 .
```

### Adding Features

1. Create feature branch
2. Add tests for new functionality
3. Implement feature
4. Run test suite
5. Submit pull request

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test suite for examples

<!-- Trigger deployment -->