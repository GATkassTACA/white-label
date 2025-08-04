from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🏥 PharmAssist Enterprise - WORKING!</h1>
    <p>Application is running successfully.</p>
    <p>This is the restored working version from build 01c4c4d.</p>
    '''

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'PharmAssist is working'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
