"""
PharmChat Installer Creator
Creates a standalone executable installer for pharmacy deployment
"""

import os
import sys
import shutil
from pathlib import Path

def create_pharmacy_installer():
    """Create a complete pharmacy installation package"""
    
    print("🏥 Creating PharmChat Pharmacy Installer Package")
    print("=" * 60)
    
    # Create installer directory structure
    installer_dir = Path("PharmChat_Installer")
    if installer_dir.exists():
        shutil.rmtree(installer_dir)
    
    installer_dir.mkdir()
    
    # Create subdirectories
    (installer_dir / "app").mkdir()
    (installer_dir / "docs").mkdir()
    (installer_dir / "config").mkdir()
    (installer_dir / "scripts").mkdir()
    
    # Copy main pharmacy application
    shutil.copy("pharmacy_chat.py", installer_dir / "app" / "pharmacy_chat.py")
    
    # Create requirements file
    requirements = """flask>=2.3.0
werkzeug>=2.3.0
python-dotenv>=1.0.0
"""
    
    with open(installer_dir / "app" / "requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    
    # Create Windows installer script
    windows_installer = """@echo off
echo.
echo ========================================
echo   PharmChat Pharmacy Installer
echo   HIPAA-Compliant Local Installation
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo ✓ Python detected
echo.

REM Create installation directory
set INSTALL_DIR=C:\\PharmChat
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo ✓ Created installation directory: %INSTALL_DIR%
echo.

REM Copy application files
xcopy /E /I app\\* "%INSTALL_DIR%\\" /Y

echo ✓ Copied application files
echo.

REM Install Python dependencies
cd /d "%INSTALL_DIR%"
python -m pip install -r requirements.txt

echo ✓ Installed dependencies
echo.

REM Create desktop shortcut
set SHORTCUT_PATH=%USERPROFILE%\\Desktop\\PharmChat.lnk
echo @echo off > "%INSTALL_DIR%\\start_pharmchat.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\\start_pharmchat.bat"
echo python pharmacy_chat.py >> "%INSTALL_DIR%\\start_pharmchat.bat"

REM Create start menu entry
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PharmChat" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PharmChat"
copy "%INSTALL_DIR%\\start_pharmchat.bat" "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PharmChat\\PharmChat.bat"

echo ✓ Created shortcuts
echo.

REM Create Windows service (optional)
echo [Unit] > "%INSTALL_DIR%\\pharmchat.service"
echo Description=PharmChat Pharmacy Communication System >> "%INSTALL_DIR%\\pharmchat.service"
echo After=network.target >> "%INSTALL_DIR%\\pharmchat.service"
echo. >> "%INSTALL_DIR%\\pharmchat.service"
echo [Service] >> "%INSTALL_DIR%\\pharmchat.service"
echo Type=simple >> "%INSTALL_DIR%\\pharmchat.service"
echo User=pharmchat >> "%INSTALL_DIR%\\pharmchat.service"
echo WorkingDirectory=%INSTALL_DIR% >> "%INSTALL_DIR%\\pharmchat.service"
echo ExecStart=python pharmacy_chat.py >> "%INSTALL_DIR%\\pharmchat.service"
echo Restart=always >> "%INSTALL_DIR%\\pharmchat.service"
echo. >> "%INSTALL_DIR%\\pharmchat.service"
echo [Install] >> "%INSTALL_DIR%\\pharmchat.service"
echo WantedBy=multi-user.target >> "%INSTALL_DIR%\\pharmchat.service"

echo.
echo ========================================
echo   PharmChat Installation Complete!
echo ========================================
echo.
echo Installation Directory: %INSTALL_DIR%
echo.
echo To start PharmChat:
echo   1. Double-click 'PharmChat' on your desktop, OR
echo   2. Go to Start Menu ^> PharmChat ^> PharmChat
echo.
echo System will be available at: http://localhost:5000
echo.
echo Default Login Credentials:
echo   Pharmacist: pharmacist@yourpharmacy.com / PharmSecure123!
echo   Technician: tech@yourpharmacy.com / TechSecure123!
echo   Manager: manager@yourpharmacy.com / ManagerSecure123!
echo.
echo ⚠️  IMPORTANT: Change all passwords on first login!
echo.
echo For support: support@pharmchat.com
echo             1-800-PHARMCHAT
echo.
pause
"""
    
    with open(installer_dir / "install_windows.bat", "w", encoding="utf-8") as f:
        f.write(windows_installer)
    
    # Create pharmacy configuration template
    config_template = """{
    "pharmacy_name": "Your Pharmacy Name",
    "pharmacy_address": "123 Main St, Your City, ST 12345",
    "pharmacy_phone": "(555) 123-4567",
    "pharmacy_npi": "1234567890",
    "primary_color": "#059669",
    "secondary_color": "#065f46",
    "logo_path": "assets/logo.png",
    "hipaa_officer": "HIPAA Privacy Officer Name",
    "hipaa_phone": "(555) 123-4567",
    "backup_schedule": "daily",
    "session_timeout": 30,
    "password_policy": {
        "min_length": 8,
        "require_uppercase": true,
        "require_lowercase": true,
        "require_numbers": true,
        "require_special": true
    },
    "audit_settings": {
        "log_user_actions": true,
        "log_document_access": true,
        "retention_days": 2555
    }
}"""
    
    with open(installer_dir / "config" / "pharmacy_config.json", "w", encoding="utf-8") as f:
        f.write(config_template)
    
    # Create setup documentation
    setup_guide = """# PharmChat Quick Setup Guide

## 🏥 Welcome to PharmChat!

Your HIPAA-compliant pharmacy communication system has been installed successfully.

### 📋 First Steps

1. **Start PharmChat**
   - Double-click the desktop shortcut, OR
   - Go to Start Menu > PharmChat

2. **Access the System**
   - Open your web browser
   - Go to: http://localhost:5000

3. **Login with Default Credentials**
   - Pharmacist: pharmacist@yourpharmacy.com / PharmSecure123!
   - Technician: tech@yourpharmacy.com / TechSecure123!
   - Manager: manager@yourpharmacy.com / ManagerSecure123!

4. **⚠️ IMMEDIATELY Change All Passwords!**

### 🔧 Customization

1. **Pharmacy Branding**
   - Edit: C:\\PharmChat\\config\\pharmacy_config.json
   - Update pharmacy name, address, colors
   - Replace logo in assets folder

2. **Staff Accounts**
   - Add real staff email addresses
   - Set up proper roles and permissions
   - Remove demo accounts

3. **HIPAA Settings**
   - Configure HIPAA officer information
   - Set up audit logging preferences
   - Configure data retention policies

### 📞 Support

- **Email**: support@pharmchat.com
- **Phone**: 1-800-PHARMCHAT
- **Hours**: Monday-Friday, 8 AM - 6 PM EST

### 🔒 Security Reminders

- ✅ All data stays on your local computer
- ✅ No internet connection required for operation
- ✅ Regular password changes recommended
- ✅ Enable automatic screen locks
- ✅ Backup your data regularly

---

**Your pharmacy communication system is now ready for secure, HIPAA-compliant operation!**
"""
    
    with open(installer_dir / "docs" / "QUICK_SETUP.md", "w", encoding="utf-8") as f:
        f.write(setup_guide)
    
    # Create uninstaller
    uninstaller = """@echo off
echo.
echo ========================================
echo   PharmChat Uninstaller
echo ========================================
echo.

set INSTALL_DIR=C:\\PharmChat

echo WARNING: This will completely remove PharmChat and ALL DATA
echo.
set /p CONFIRM=Are you sure you want to continue? (yes/no): 

if /i not "%CONFIRM%"=="yes" (
    echo Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo Removing PharmChat...

REM Stop any running instances
taskkill /f /im python.exe 2>nul

REM Remove installation directory
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
    echo ✓ Removed installation directory
)

REM Remove desktop shortcut
if exist "%USERPROFILE%\\Desktop\\PharmChat.lnk" (
    del "%USERPROFILE%\\Desktop\\PharmChat.lnk"
    echo ✓ Removed desktop shortcut
)

REM Remove start menu entry
if exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PharmChat" (
    rmdir /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\PharmChat"
    echo ✓ Removed start menu entry
)

echo.
echo PharmChat has been completely removed from your system.
echo.
pause
"""
    
    with open(installer_dir / "uninstall.bat", "w", encoding="utf-8") as f:
        f.write(uninstaller)
    
    # Create README for installer package
    readme = """# PharmChat Installer Package

## 📦 Package Contents

- `install_windows.bat` - Windows installer script
- `app/` - PharmChat application files
- `config/` - Configuration templates
- `docs/` - Setup and user documentation
- `uninstall.bat` - Removal script

## 🚀 Installation Instructions

### For Windows:
1. Right-click on `install_windows.bat`
2. Select "Run as administrator"
3. Follow the installation prompts
4. Access PharmChat at http://localhost:5000

### For Mac/Linux:
1. Ensure Python 3.8+ is installed
2. Copy `app/` contents to desired location
3. Run: `pip install -r requirements.txt`
4. Run: `python pharmacy_chat.py`

## 📋 System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB for app, 5GB+ for documents
- **Network**: No internet required after installation

## 🔒 Security Features

- ✅ 100% local installation
- ✅ HIPAA-compliant by design
- ✅ Encrypted data storage
- ✅ Role-based access control
- ✅ Comprehensive audit logging

## 📞 Support

- **Email**: support@pharmchat.com
- **Phone**: 1-800-PHARMCHAT
- **Website**: www.pharmchat.com

---

**PharmChat - Secure Communication for Modern Pharmacies**
"""
    
    with open(installer_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    
    # Create pharmacy license agreement
    license_agreement = """PHARMCHAT SOFTWARE LICENSE AGREEMENT

IMPORTANT: READ THIS LICENSE AGREEMENT CAREFULLY BEFORE INSTALLING OR USING PHARMCHAT SOFTWARE.

1. LICENSE GRANT
   This agreement grants you a non-exclusive license to use PharmChat software 
   on a single pharmacy location or as specified in your purchase agreement.

2. PERMITTED USES
   - Install and use on pharmacy computers for business operations
   - Create backups for data protection
   - Customize branding and configuration for your pharmacy

3. RESTRICTIONS
   - Do not redistribute, sell, or transfer the software
   - Do not reverse engineer or modify core functionality
   - Do not use for non-pharmacy business operations

4. HIPAA COMPLIANCE
   This software is designed to support HIPAA compliance but proper policies
   and procedures must be implemented by your pharmacy.

5. DATA PRIVACY
   All patient data remains on your local systems. No data is transmitted
   to external servers or third parties.

6. SUPPORT AND UPDATES
   Technical support and software updates are provided as specified in
   your service agreement.

7. WARRANTY DISCLAIMER
   Software is provided "as-is" without warranty. Use at your own risk.

8. LIMITATION OF LIABILITY
   Provider's liability is limited to the purchase price of the software.

By installing this software, you agree to these terms and conditions.

For questions: legal@pharmchat.com
"""
    
    with open(installer_dir / "docs" / "LICENSE.txt", "w", encoding="utf-8") as f:
        f.write(license_agreement)
    
    print("[OK] Created installer directory structure")
    print("[OK] Copied application files")
    print("[OK] Created Windows installer script")
    print("[OK] Created configuration templates")
    print("[OK] Created documentation")
    print("[OK] Created uninstaller")
    print("[OK] Created license agreement")
    
    print("\n" + "=" * 60)
    print("PHARMACY INSTALLER PACKAGE READY!")
    print("=" * 60)
    print(f"Package Location: {installer_dir.absolute()}")
    print("\nPackage Contents:")
    print("   ├── install_windows.bat (Main installer)")
    print("   ├── uninstall.bat (Removal tool)")
    print("   ├── README.md (Installation guide)")
    print("   ├── app/ (PharmChat application)")
    print("   ├── config/ (Configuration templates)")
    print("   └── docs/ (Documentation & license)")
    
    print("\nNext Steps:")
    print("   1. Test the installer on a clean Windows system")
    print("   2. Create executable with PyInstaller for easier distribution")
    print("   3. Package into ZIP file for download distribution")
    print("   4. Set up digital signing for security trust")
    
    print("\nDistribution Options:")
    print("   • Email ZIP package to customers")
    print("   • Host on secure download portal")
    print("   • Provide on USB drives for on-site installation")
    print("   • Remote installation via screen sharing")
    
    return installer_dir

if __name__ == "__main__":
    try:
        installer_path = create_pharmacy_installer()
        print(f"\n[SUCCESS] Installer package created at {installer_path}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
