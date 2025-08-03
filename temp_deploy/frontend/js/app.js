// Main application JavaScript
const { useState, useEffect } = React;

function App() {
    const [currentPage, setCurrentPage] = useState('home');
    const [isLoading, setIsLoading] = useState(true);
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        // Check for stored authentication
        checkAuthentication();
        setTimeout(() => setIsLoading(false), 1000);
    }, []);

    // API base URL - automatically detects environment
    const getApiBaseUrl = () => {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:5000';
        }
        // For Azure deployment, use the same domain as the frontend
        return window.location.origin;
    };

    const checkAuthentication = async () => {
        const token = localStorage.getItem('access_token');
        const storedUser = localStorage.getItem('user');
        
        if (token && storedUser) {
            try {
                // Verify token is still valid
                const response = await fetch(`${getApiBaseUrl()}/api/auth/verify-token`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    setUser(data.user);
                    setIsAuthenticated(true);
                } else {
                    // Token invalid, clear storage
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                }
            } catch (error) {
                console.error('Auth check failed:', error);
            }
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        setUser(null);
        setIsAuthenticated(false);
        setCurrentPage('home');
    };

    const Navigation = () => (
        React.createElement('nav', { className: 'glass-effect p-4 mb-8' },
            React.createElement('div', { className: 'max-w-6xl mx-auto flex justify-between items-center' },
                React.createElement('div', { className: 'text-white text-xl font-bold' }, 'White Label Chat SaaS'),
                React.createElement('div', { className: 'flex items-center space-x-4' },
                    React.createElement('div', { className: 'space-x-4' },
                        ['home', 'chat', 'documents', 'wizard'].map(page =>
                            React.createElement('button', {
                                key: page,
                                onClick: () => setCurrentPage(page),
                                className: `px-4 py-2 rounded-lg transition-all capitalize ${
                                    currentPage === page 
                                        ? 'bg-white text-purple-700 font-semibold' 
                                        : 'text-white hover:bg-white hover:bg-opacity-20'
                                }`
                            }, page)
                        )
                    ),
                    React.createElement('div', { className: 'border-l border-white border-opacity-30 pl-4' },
                        isAuthenticated 
                            ? React.createElement('div', { className: 'flex items-center space-x-3' },
                                React.createElement('span', { className: 'text-white text-sm' },
                                    `Welcome, ${user?.username}`,
                                    user?.user_type === 'admin' && React.createElement('span', { 
                                        className: 'ml-1 px-2 py-1 bg-yellow-500 text-xs rounded' 
                                    }, 'Admin')
                                ),
                                React.createElement('button', {
                                    onClick: handleLogout,
                                    className: 'px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-sm'
                                }, 'Logout')
                            )
                            : React.createElement('a', {
                                href: '/auth.html',
                                className: 'px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors'
                            }, 'Sign In')
                    )
                )
            )
        )
    );

    const HomePage = () => (
        React.createElement('div', { className: 'text-center text-white' },
            React.createElement('h1', { className: 'text-5xl font-bold mb-6' }, '🚀 Modern Frontend is Ready!'),
            React.createElement('p', { className: 'text-xl mb-8 opacity-90' }, 'Your white-label chat SaaS now has a modern React frontend'),
            React.createElement('div', { className: 'grid md:grid-cols-3 gap-6 max-w-4xl mx-auto' },
                React.createElement('div', { className: 'glass-effect p-6 rounded-xl' },
                    React.createElement('h3', { className: 'text-xl font-semibold mb-3' }, '⚡ React + Modern Tools'),
                    React.createElement('p', { className: 'opacity-80' }, 'Built with React 18 and modern development practices')
                ),
                React.createElement('div', { className: 'glass-effect p-6 rounded-xl' },
                    React.createElement('h3', { className: 'text-xl font-semibold mb-3' }, '🎨 Tailwind CSS'),
                    React.createElement('p', { className: 'opacity-80' }, 'Utility-first styling for rapid UI development')
                ),
                React.createElement('div', { className: 'glass-effect p-6 rounded-xl' },
                    React.createElement('h3', { className: 'text-xl font-semibold mb-3' }, '🔗 Flask Integration'),
                    React.createElement('p', { className: 'opacity-80' }, 'Seamlessly connected to your Flask backend')
                )
            )
        )
    );

    // Add other page components here (ChatPage, DocumentsPage, WizardPage)
    // For brevity, I'll add placeholders that can be expanded
    
    const ChatPage = () => React.createElement('div', { className: 'text-white text-center' }, 
        React.createElement('h2', { className: 'text-3xl font-bold mb-4' }, '💬 Chat Interface'),
        React.createElement('p', null, 'Chat functionality will be loaded here')
    );
    
    const DocumentsPage = () => React.createElement('div', { className: 'text-white text-center' },
        React.createElement('h2', { className: 'text-3xl font-bold mb-4' }, '📄 Document Management'),
        React.createElement('p', null, 'Document upload and processing interface')
    );
    
    const WizardPage = () => React.createElement('div', { className: 'text-white text-center' },
        React.createElement('h2', { className: 'text-3xl font-bold mb-4' }, '🎨 White-Label Wizard'),
        React.createElement('p', null, 'Client branding configuration tool')
    );

    const LoadingScreen = () => (
        React.createElement('div', { className: 'flex items-center justify-center min-h-screen text-white' },
            React.createElement('div', { className: 'text-center' },
                React.createElement('div', { className: 'animate-spin rounded-full h-32 w-32 border-b-2 border-white mx-auto mb-4' }),
                React.createElement('h2', { className: 'text-2xl font-semibold' }, 'Loading Modern Frontend...')
            )
        )
    );

    if (isLoading) {
        return React.createElement(LoadingScreen);
    }

    const renderPage = () => {
        switch(currentPage) {
            case 'chat': return React.createElement(ChatPage);
            case 'documents': return React.createElement(DocumentsPage);
            case 'wizard': return React.createElement(WizardPage);
            default: return React.createElement(HomePage);
        }
    };

    return React.createElement('div', { className: 'min-h-screen p-4' },
        React.createElement(Navigation),
        renderPage(),
        React.createElement('footer', { className: 'text-center text-white mt-12 opacity-70' },
            React.createElement('p', null, `✨ Modern React Frontend - Connected to Flask Backend on ${getApiBaseUrl()}`)
        )
    );
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    ReactDOM.render(React.createElement(App), document.getElementById('app'));
});
