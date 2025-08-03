@echo off
setlocal

REM Modern Build System Setup for White Label Chat SaaS
echo 🚀 Setting up modern build system...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    echo    Download from: https://nodejs.org/
    exit /b 1
)

echo ✅ Node.js detected: 
node --version

REM Navigate to frontend directory
if not exist frontend mkdir frontend
cd frontend

REM Install dependencies
echo 📦 Installing dependencies...
call npm install

REM Install additional dependencies
call npm install react-router-dom @types/react-router-dom
call npm install --save-dev @types/node @tsconfig/node18

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

echo ✅ Dependencies installed successfully!

REM Create missing directories
if not exist src\components mkdir src\components
if not exist src\pages mkdir src\pages
if not exist src\utils mkdir src\utils
if not exist src\assets mkdir src\assets

REM Build the project
echo 🔨 Building project...
call npm run build

if %errorlevel% equ 0 (
    echo ✅ Build successful!
    echo.
    echo 🎉 Modern build system setup complete!
    echo.
    echo 📋 Next Steps:
    echo    1. Development: npm run dev
    echo    2. Production build: npm run build
    echo    3. Preview build: npm run preview
    echo.
    echo 🌐 Development server will run on: http://localhost:3000
    echo 🔗 API proxy configured for: http://localhost:5000
) else (
    echo ❌ Build failed. Please check the errors above.
    exit /b 1
)

pause
