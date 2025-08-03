#!/usr/bin/env python3
"""
Azure App Service startup script
Handles PORT environment variable correctly
"""
import os
import subprocess
import sys

def main():
    # Get the port from environment variable
    port = os.environ.get('PORT', '8000')
    print(f"Azure PORT environment variable: {port}")
    
    # Build the gunicorn command
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--timeout', '600',
        '--access-logfile', '-',
        '--error-logfile', '-',
        'simple_app:app'
    ]
    
    print(f"Starting: {' '.join(cmd)}")
    
    # Execute gunicorn
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting gunicorn: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
