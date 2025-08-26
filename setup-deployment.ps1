Write-Host "Setting up JuristAI for Vercel Deployment" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "package.json") -or -not (Test-Path "backend")) {
    Write-Host "Error: Please run this script from the root of your JuristAI project" -ForegroundColor Red
    exit 1
}

Write-Host "Project structure detected" -ForegroundColor Green

# Create backend repository setup
Write-Host "Preparing backend for separate repository..." -ForegroundColor Yellow

# Create backend directory structure check
if (Test-Path "backend") {
    Write-Host "Backend directory exists" -ForegroundColor Green
    
    # Check for required files
    if ((Test-Path "backend/main.py") -and (Test-Path "backend/requirements.txt") -and (Test-Path "backend/vercel.json")) {
        Write-Host "Backend files are ready" -ForegroundColor Green
    } else {
        Write-Host "Missing required backend files" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Backend directory not found" -ForegroundColor Red
    exit 1
}

# Check frontend setup
Write-Host "Checking frontend setup..." -ForegroundColor Yellow
if ((Test-Path "package.json") -and (Test-Path "next.config.js")) {
    Write-Host "Frontend files are ready" -ForegroundColor Green
} else {
    Write-Host "Missing required frontend files" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "==============" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Create two separate GitHub repositories:" -ForegroundColor White
Write-Host "   - jurist-ai-frontend (for Next.js app)" -ForegroundColor White
Write-Host "   - jurist-ai-backend (for FastAPI app)" -ForegroundColor White
Write-Host ""
Write-Host "2. For Backend Repository:" -ForegroundColor White
Write-Host "   - Copy contents of 'backend/' folder to new repository" -ForegroundColor White
Write-Host "   - Push to GitHub" -ForegroundColor White
Write-Host "   - Deploy to Vercel using the guide in DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "3. For Frontend Repository:" -ForegroundColor White
Write-Host "   - Copy all files except 'backend/' folder to new repository" -ForegroundColor White
Write-Host "   - Update .env.local with your backend URL" -ForegroundColor White
Write-Host "   - Push to GitHub" -ForegroundColor White
Write-Host "   - Deploy to Vercel using the guide in DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "4. Set up your database (Supabase recommended for free tier)" -ForegroundColor White
Write-Host ""
Write-Host "5. Configure environment variables in Vercel dashboard" -ForegroundColor White
Write-Host ""
Write-Host "See DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Yellow
Write-Host ""
Write-Host "Good luck!" -ForegroundColor Green
