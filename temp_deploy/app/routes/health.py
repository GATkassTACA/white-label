from flask import Blueprint, jsonify
from datetime import datetime
import os
import sys

health_bp = Blueprint('health', __name__)

@health_bp.route('/api/health')
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'python_version': sys.version,
            'checks': {}
        }
        
        # Database connectivity check
        try:
            from app import db
            db.session.execute('SELECT 1')
            health_data['checks']['database'] = 'healthy'
        except Exception as e:
            health_data['checks']['database'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'degraded'
        
        # Redis connectivity check (if configured)
        try:
            redis_url = os.environ.get('REDIS_URL')
            if redis_url:
                try:
                    import redis
                    r = redis.from_url(redis_url)
                    r.ping()
                    health_data['checks']['redis'] = 'healthy'
                except ImportError:
                    health_data['checks']['redis'] = 'redis_not_installed'
            else:
                health_data['checks']['redis'] = 'not_configured'
        except Exception as e:
            health_data['checks']['redis'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'degraded'
        
        # File system check
        try:
            logs_dir = 'logs'
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            test_file = os.path.join(logs_dir, 'health_check.tmp')
            with open(test_file, 'w') as f:
                f.write('health_check')
            os.remove(test_file)
            health_data['checks']['filesystem'] = 'healthy'
        except Exception as e:
            health_data['checks']['filesystem'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'degraded'
        
        # Return appropriate status code
        status_code = 200 if health_data['status'] == 'healthy' else 503
        
        return jsonify(health_data), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/api/ready')
def readiness_check():
    """Readiness check for Kubernetes/container orchestration"""
    try:
        from app import db
        
        # Check if database is ready
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@health_bp.route('/api/live')
def liveness_check():
    """Liveness check for Kubernetes/container orchestration"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
