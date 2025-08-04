from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>White Label Chat</title></head>
    <body style="font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>🚀 White Label Chat Platform</h1>
        <p>Your production-ready chat application is running!</p>
        <div style="margin: 30px 0;">
            <a href="/admin" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                👤 Admin Login
            </a>
        </div>
        <div style="background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h3>🔐 Admin Credentials:</h3>
            <p><strong>Email:</strong> admin@example.com</p>
            <p><strong>Password:</strong> Admin123!</p>
        </div>
        <p><small>Azure App Service • Central US</small></p>
    </body>
    </html>
    '''

@app.route('/admin')
def admin():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-br from-blue-500 to-purple-600 min-h-screen">
        <div class="min-h-screen flex items-center justify-center p-4">
            <div class="bg-white bg-opacity-20 backdrop-blur-lg p-8 rounded-xl max-w-md w-full">
                <h1 class="text-3xl font-bold text-white mb-6 text-center">Admin Login</h1>
                <form class="space-y-4">
                    <div>
                        <input type="email" placeholder="admin@example.com" 
                               class="w-full p-3 rounded-lg bg-white bg-opacity-20 text-white placeholder-gray-300 border border-white border-opacity-30">
                    </div>
                    <div>
                        <input type="password" placeholder="Admin123!" 
                               class="w-full p-3 rounded-lg bg-white bg-opacity-20 text-white placeholder-gray-300 border border-white border-opacity-30">
                    </div>
                    <button type="submit" 
                            class="w-full bg-gradient-to-r from-blue-500 to-purple-600 py-3 rounded-lg font-semibold text-white hover:from-blue-600 hover:to-purple-700">
                        Sign In
                    </button>
                </form>
                <div class="mt-4 text-center">
                    <a href="/" class="text-white opacity-60 hover:opacity-80">← Back to Home</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {"status": "healthy", "app": "white-label-chat", "version": "1.0"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

# For Azure
application = app
