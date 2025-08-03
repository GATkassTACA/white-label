@echo off
echo ============================================
echo Azure App Service Publish Profile Helper
echo ============================================
echo.
echo Since basic auth is disabled, you need to:
echo.
echo 1. Go to Azure Portal
echo 2. Navigate to your App Service: white-label-chat-km
echo 3. Click "Configuration" ^> "General settings"
echo 4. Set "Basic Auth Publishing Credentials" to ON
echo 5. Click "Save"
echo 6. Go back to Overview and click "Get publish profile"
echo 7. Download the .publishsettings file
echo 8. Open it in notepad and copy ALL content
echo.
echo 9. Go to GitHub: https://github.com/GATkassTACA/white-label
echo 10. Click Settings ^> Secrets and variables ^> Actions
echo 11. Click "New repository secret"
echo 12. Name: AZUREAPPSERVICE_PUBLISHPROFILE_WHITELABELCHATAPP
echo 13. Value: Paste the entire publish profile content
echo 14. Click "Add secret"
echo.
echo 15. Go back to GitHub Actions and manually trigger the workflow
echo.
pause
