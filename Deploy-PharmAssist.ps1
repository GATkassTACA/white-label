# PharmAssist Azure Deployment Script (PowerShell)
# Uses ARM templates for consistent, repeatable deployments

param(
    [string]$ResourceGroup = "pharmassist-production",
    [string]$Location = "Central US",
    [string]$TemplateFile = "pharmassist-deployment-template.json",
    [string]$ParametersFile = "pharmassist-deployment-parameters.json"
)

Write-Host "🏥 PharmAssist Azure Deployment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

$DeploymentName = "pharmassist-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

try {
    # Create resource group
    Write-Host "📁 Creating resource group: $ResourceGroup" -ForegroundColor Yellow
    az group create --name $ResourceGroup --location $Location

    # Deploy ARM template
    Write-Host "🚀 Deploying PharmAssist application..." -ForegroundColor Yellow
    $DeploymentOutput = az deployment group create `
        --resource-group $ResourceGroup `
        --template-file $TemplateFile `
        --parameters "@$ParametersFile" `
        --name $DeploymentName `
        --output json | ConvertFrom-Json

    # Extract outputs
    $WebAppName = $DeploymentOutput.properties.outputs.webAppName.value
    $WebAppUrl = $DeploymentOutput.properties.outputs.webAppUrl.value

    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "📱 App Name: $WebAppName" -ForegroundColor White
    Write-Host "🌐 URL: $WebAppUrl" -ForegroundColor White

    # Deploy application code
    Write-Host "📦 Deploying application code..." -ForegroundColor Yellow
    Compress-Archive -Path "pharmassist_app.py", "pdf_processing.py", "requirements.txt", "templates" -DestinationPath "pharmassist-deploy.zip" -Force

    az webapp deployment source config-zip `
        --resource-group $ResourceGroup `
        --name $WebAppName `
        --src "pharmassist-deploy.zip"

    # Configure startup command
    Write-Host "⚙️ Configuring startup command..." -ForegroundColor Yellow
    az webapp config set `
        --resource-group $ResourceGroup `
        --name $WebAppName `
        --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 pharmassist_app:app"

    # Restart app
    Write-Host "🔄 Restarting application..." -ForegroundColor Yellow
    az webapp restart `
        --resource-group $ResourceGroup `
        --name $WebAppName

    Write-Host ""
    Write-Host "🎉 PharmAssist deployment complete!" -ForegroundColor Green
    Write-Host "🌐 Access your application at: $WebAppUrl" -ForegroundColor Cyan
    Write-Host "🔍 Health check: $WebAppUrl/health" -ForegroundColor Cyan
    Write-Host "📊 API status: $WebAppUrl/api/status" -ForegroundColor Cyan

} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
