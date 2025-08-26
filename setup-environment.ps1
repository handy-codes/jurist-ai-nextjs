# JuristAI Environment Setup Script

Write-Host "Setting up JuristAI Environment Variables" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Function to generate a secure secret key
function Generate-SecretKey {
    param([int]$Length = 32)
    
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:,.<>?"
    $secretKey = ""
    
    for ($i = 0; $i -lt $Length; $i++) {
        $secretKey += $chars[(Get-Random -Maximum $chars.Length)]
    }
    
    return $secretKey
}

Write-Host ""
Write-Host "Generating secure SECRET_KEY..." -ForegroundColor Yellow
$secretKey32 = Generate-SecretKey -Length 32
$secretKey64 = Generate-SecretKey -Length 64

Write-Host "32 characters: $secretKey32" -ForegroundColor Cyan
Write-Host "64 characters: $secretKey64" -ForegroundColor Cyan

Write-Host ""
Write-Host "Creating environment file templates..." -ForegroundColor Yellow

# Create backend .env template
$backendEnvContent = @"
# JuristAI Backend Environment Variables
# Fill in your actual values below

# Database Configuration
# Get this from Supabase: Settings -> Database -> Connection string (URI)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# AI Services
# Get from https://console.groq.com/api-keys
GROQ_API_KEY=gsk_your_groq_api_key_here

# Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your_openai_api_key_here

# JWT Configuration
SECRET_KEY=$secretKey32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
"@

# Create frontend .env.local template
$frontendEnvContent = @"
# JuristAI Frontend Environment Variables
# Fill in your actual values below

# Clerk Authentication
# Get from https://clerk.com -> Your App -> API Keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# AI Services (if needed by frontend)
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here

# Database (if needed by frontend)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
"@

# Save files
try {
    $backendEnvContent | Out-File -FilePath "backend\.env.example" -Encoding UTF8
    Write-Host "Created: backend\.env.example" -ForegroundColor Green
    
    $frontendEnvContent | Out-File -FilePath ".env.local.example" -Encoding UTF8
    Write-Host "Created: .env.local.example" -ForegroundColor Green
} catch {
    Write-Host "Error creating files: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "==========" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Set up Supabase database:" -ForegroundColor White
Write-Host "   - Go to https://supabase.com" -ForegroundColor Gray
Write-Host "   - Create new project" -ForegroundColor Gray
Write-Host "   - Get connection string from Settings -> Database" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Get API keys:" -ForegroundColor White
Write-Host "   - Clerk: https://clerk.com (authentication)" -ForegroundColor Gray
Write-Host "   - Groq: https://console.groq.com (AI API)" -ForegroundColor Gray
Write-Host "   - OpenAI: https://platform.openai.com (AI API)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Copy and fill environment files:" -ForegroundColor White
Write-Host "   - Copy backend\.env.example to backend\.env" -ForegroundColor Gray
Write-Host "   - Copy .env.local.example to .env.local" -ForegroundColor Gray
Write-Host "   - Fill in your actual API keys and database URL" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Test your setup:" -ForegroundColor White
Write-Host "   - Follow DATABASE_SETUP_GUIDE.md for detailed instructions" -ForegroundColor Gray
Write-Host ""
Write-Host "Your SECRET_KEY has been generated and included in the template!" -ForegroundColor Green
Write-Host "Keep your API keys secure and never commit them to version control!" -ForegroundColor Yellow


