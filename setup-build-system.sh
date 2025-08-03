#!/bin/bash

# Modern Build System Setup for White Label Chat SaaS
echo "🚀 Setting up modern build system..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Install additional router dependency
npm install react-router-dom @types/react-router-dom

# Install Node.js types for TypeScript
npm install --save-dev @types/node @tsconfig/node18

echo "✅ Dependencies installed successfully!"

# Create missing directories
mkdir -p src/components src/pages src/utils src/assets

# Build the project
echo "🔨 Building project..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🎉 Modern build system setup complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Development: npm run dev"
    echo "   2. Production build: npm run build"
    echo "   3. Preview build: npm run preview"
    echo ""
    echo "🌐 Development server will run on: http://localhost:3000"
    echo "🔗 API proxy configured for: http://localhost:5000"
else
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi
