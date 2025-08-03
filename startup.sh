#!/bin/bash
echo "Starting Azure App Service deployment..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Environment variables:"
echo "FLASK_ENV: $FLASK_ENV"
echo "Files in current directory:"
ls -la

echo "Testing WSGI import..."
python -c "import wsgi; print('WSGI import successful')" || echo "WSGI import failed"

echo "Starting Gunicorn..."
gunicorn --bind 0.0.0.0:8000 --timeout 600 --access-logfile '-' --error-logfile '-' wsgi:app
