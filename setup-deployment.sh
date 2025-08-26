#!/bin/bash

echo "🚀 Setting up JuristAI for Vercel Deployment"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the root of your JuristAI project"
    exit 1
fi

echo "✅ Project structure detected"

# Create backend repository setup
echo "📁 Preparing backend for separate repository..."

# Create backend directory structure check
if [ -d "backend" ]; then
    echo "✅ Backend directory exists"
    
    # Check for required files
    if [ -f "backend/main.py" ] && [ -f "backend/requirements.txt" ] && [ -f "backend/vercel.json" ]; then
        echo "✅ Backend files are ready"
    else
        echo "❌ Missing required backend files"
        exit 1
    fi
else
    echo "❌ Backend directory not found"
    exit 1
fi

# Check frontend setup
echo "📁 Checking frontend setup..."
if [ -f "package.json" ] && [ -f "next.config.js" ]; then
    echo "✅ Frontend files are ready"
else
    echo "❌ Missing required frontend files"
    exit 1
fi

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo ""
echo "1. Create two separate GitHub repositories:"
echo "   - jurist-ai-frontend (for Next.js app)"
echo "   - jurist-ai-backend (for FastAPI app)"
echo ""
echo "2. For Backend Repository:"
echo "   - Copy contents of 'backend/' folder to new repository"
echo "   - Push to GitHub"
echo "   - Deploy to Vercel using the guide in DEPLOYMENT_GUIDE.md"
echo ""
echo "3. For Frontend Repository:"
echo "   - Copy all files except 'backend/' folder to new repository"
echo "   - Update .env.local with your backend URL"
echo "   - Push to GitHub"
echo "   - Deploy to Vercel using the guide in DEPLOYMENT_GUIDE.md"
echo ""
echo "4. Set up your database (Supabase recommended for free tier)"
echo ""
echo "5. Configure environment variables in Vercel dashboard"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "Good luck! 🚀"
