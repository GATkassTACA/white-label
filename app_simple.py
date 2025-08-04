import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Simple test route"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <h1>PharmAssist Enterprise - Template Debug</h1>
        <p>Template error: {str(e)}</p>
        <p>Current working directory: {os.getcwd()}</p>
        <p>Template folder: {app.template_folder}</p>
        <p>Looking for templates in: {os.path.join(os.getcwd(), 'templates')}</p>
        <p>Templates directory exists: {os.path.exists('templates')}</p>
        <p>Index.html exists: {os.path.exists('templates/index.html')}</p>
        <h2>Files in current directory:</h2>
        <ul>
        {''.join([f'<li>{f}</li>' for f in os.listdir('.') if not f.startswith('.')])}
        </ul>
        """

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'operational',
        'template_folder': app.template_folder,
        'cwd': os.getcwd(),
        'templates_exist': os.path.exists('templates'),
        'index_exists': os.path.exists('templates/index.html')
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
