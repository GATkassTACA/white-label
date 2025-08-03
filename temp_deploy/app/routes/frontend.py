from flask import Blueprint, render_template, send_from_directory, make_response
import os

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    """Serve the main frontend with proper CSP headers"""
    try:
        # Get the root directory of the project (go up two levels from app/routes)
        import os
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        frontend_dir = os.path.join(root_dir, 'frontend')
        file_path = os.path.join(frontend_dir, 'index-secure.html')
        
        if not os.path.exists(file_path):
            return f"Frontend file not found at: {file_path}", 404
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        response = make_response(content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        
        # Add security headers with environment-aware CSP
        from flask import request
        host = request.host
        
        # Determine the allowed connection sources based on environment
        if host.endswith('.azurewebsites.net'):
            connect_src = f"'self' https://{host} wss://{host}"
        else:
            connect_src = "'self' http://localhost:5000 ws://localhost:5000"
        
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://unpkg.com https://cdn.socket.io https://cdn.tailwindcss.com 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
            f"connect-src {connect_src}; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:;"
        )
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    except Exception as e:
        return f"Error loading frontend: {str(e)}", 500

@frontend_bp.route('/auth.html')
def auth():
    """Serve the authentication page"""
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        frontend_dir = os.path.join(root_dir, 'frontend')
        with open(os.path.join(frontend_dir, 'auth.html'), 'r', encoding='utf-8') as f:
            content = f.read()
        
        response = make_response(content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        
        # Add security headers for auth page
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://unpkg.com https://cdn.tailwindcss.com 'unsafe-eval' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
            "connect-src 'self' http://localhost:5000; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:;"
        )
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    except FileNotFoundError:
        return "Auth page not found", 404

@frontend_bp.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files with proper headers"""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    frontend_dir = os.path.join(root_dir, 'frontend')
    js_dir = os.path.join(frontend_dir, 'js')
    
    response = make_response(send_from_directory(js_dir, filename))
    response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response

@frontend_bp.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files with proper headers"""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    frontend_dir = os.path.join(root_dir, 'frontend')
    css_dir = os.path.join(frontend_dir, 'css')
    
    response = make_response(send_from_directory(css_dir, filename))
    response.headers['Content-Type'] = 'text/css; charset=utf-8'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response

@frontend_bp.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static assets"""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    frontend_dir = os.path.join(root_dir, 'frontend')
    static_dir = os.path.join(frontend_dir, 'static')
    
    return send_from_directory(static_dir, filename)
