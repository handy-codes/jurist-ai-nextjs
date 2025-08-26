# Deployment Guide - JuristAI to Vercel

This guide will help you deploy both the frontend (Next.js) and backend (FastAPI) to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **Database**: Set up a PostgreSQL database (you can use Supabase, Railway, or any other provider)
4. **API Keys**: Get your API keys for Groq, OpenAI, and Clerk

## Step 1: Deploy Backend (FastAPI)

### 1.1 Prepare Backend Repository
- Create a separate GitHub repository for your backend
- Copy the `backend/` folder contents to the new repository
- Make sure all `__init__.py` files are present

### 1.2 Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your backend GitHub repository
4. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (root of the repository)
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

### 1.3 Set Environment Variables
In your Vercel project dashboard, go to Settings > Environment Variables and add:

```
DATABASE_URL=your_postgresql_connection_string
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

### 1.4 Deploy
Click "Deploy" and wait for the deployment to complete. Note your backend URL (e.g., `https://your-backend-name.vercel.app`)

## Step 2: Deploy Frontend (Next.js)

### 2.1 Update Frontend Configuration
1. Update your frontend environment variables to point to your deployed backend
2. Create a `.env.local` file in your frontend root:

```
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key

# API Configuration
NEXT_PUBLIC_API_URL=https://your-backend-name.vercel.app

# Database (if needed for frontend)
DATABASE_URL=your_postgresql_connection_string

# AI Services
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 2.2 Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your frontend GitHub repository
4. Configure the project:
   - **Framework Preset**: Next.js (should auto-detect)
   - **Root Directory**: `./` (root of the repository)
   - **Build Command**: `npm run build` (should auto-detect)
   - **Output Directory**: `.next` (should auto-detect)
   - **Install Command**: `npm install` (should auto-detect)

### 2.3 Set Environment Variables
In your Vercel project dashboard, go to Settings > Environment Variables and add the same variables from your `.env.local` file.

### 2.4 Deploy
Click "Deploy" and wait for the deployment to complete. Note your frontend URL (e.g., `https://your-frontend-name.vercel.app`)

## Step 3: Update CORS Configuration

After both deployments are complete, update your backend CORS configuration to include your actual frontend URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://your-frontend-name.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy your backend.

## Step 4: Test Your Deployment

1. Visit your frontend URL
2. Test the authentication flow
3. Test API calls to your backend
4. Check the browser console for any CORS errors

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Make sure your backend CORS configuration includes your frontend URL
2. **Database Connection**: Ensure your DATABASE_URL is correct and accessible from Vercel
3. **Environment Variables**: Double-check all environment variables are set in Vercel
4. **Build Errors**: Check the build logs in Vercel for any missing dependencies

### Database Setup Options:

1. **Supabase**: Free tier available, easy PostgreSQL setup
2. **Railway**: Good for PostgreSQL hosting
3. **Neon**: Serverless PostgreSQL
4. **PlanetScale**: MySQL alternative

### Monitoring:

- Use Vercel's built-in analytics and monitoring
- Set up error tracking with services like Sentry
- Monitor your database performance

## Security Considerations

1. **Environment Variables**: Never commit sensitive keys to your repository
2. **CORS**: Only allow necessary origins
3. **API Keys**: Use environment variables for all API keys
4. **Database**: Use connection pooling and proper indexing

## Cost Optimization

1. **Vercel Hobby Plan**: Free for personal projects
2. **Database**: Use free tiers when possible
3. **API Usage**: Monitor your AI API usage to control costs

Your app should now be live on Vercel! 🚀
