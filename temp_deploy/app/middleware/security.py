from flask import request, g
import secrets
import string

def generate_nonce():
    """Generate a cryptographically secure nonce for CSP"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def add_security_headers(response):
    """Add security headers to all responses"""
    # Generate nonce for this request
    nonce = generate_nonce()
    g.csp_nonce = nonce
    
    # Basic security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Only add HSTS in production with HTTPS
    if not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
        # Development mode - don't add HSTS
        pass
    else:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

def init_security_middleware(app):
    """Initialize security middleware"""
    
    @app.after_request
    def after_request(response):
        """Add security headers to all responses"""
        return add_security_headers(response)
    
    @app.before_request
    def before_request():
        """Security checks before processing request"""
        # Add any pre-request security checks here
        pass
    
    return app
