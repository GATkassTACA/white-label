from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PharmAssist - Working!</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8f0; }
            .container { max-width: 600px; margin: 0 auto; text-align: center; }
            h1 { color: #5EB97D; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 PharmAssist Enterprise</h1>
            <p>Application is running successfully!</p>
            <p>Ready for feature deployment.</p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
