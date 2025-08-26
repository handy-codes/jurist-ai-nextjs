# Quick Deployment Guide - JuristAI to Vercel

## 🚀 Essential Steps

### 1. Database Setup (Do this first!)
- Sign up for [Supabase](https://supabase.com) (free tier)
- Create a new PostgreSQL database
- Copy the connection string (you'll need this for environment variables)

### 2. Backend Deployment

#### Create Backend Repository:
1. Create new GitHub repo: `jurist-ai-backend`
2. Copy all files from `backend/` folder to the new repo
3. Push to GitHub

#### Deploy to Vercel:
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project" → Import your backend repo
3. Configure:
   - Framework: Other
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Install Command: `pip install -r requirements.txt`

#### Set Environment Variables in Vercel:
```
DATABASE_URL=your_supabase_connection_string
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

4. Deploy and note your backend URL (e.g., `https://jurist-ai-backend.vercel.app`)

### 3. Frontend Deployment

#### Create Frontend Repository:
1. Create new GitHub repo: `jurist-ai-frontend`
2. Copy all files EXCEPT `backend/` folder to the new repo
3. Create `.env.local` file with your backend URL:
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_key
CLERK_SECRET_KEY=your_clerk_secret
NEXT_PUBLIC_API_URL=https://jurist-ai-backend.vercel.app
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```
4. Push to GitHub

#### Deploy to Vercel:
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project" → Import your frontend repo
3. Framework should auto-detect as Next.js
4. Add the same environment variables from `.env.local`
5. Deploy

### 4. Update CORS (After both deployments)
Update `backend/main.py` CORS configuration with your actual frontend URL:
```python
allow_origins=[
    "http://localhost:3000", 
    "https://jurist-ai-frontend.vercel.app"
]
```
Then redeploy the backend.

## 🔑 Required API Keys
- **Clerk**: [clerk.com](https://clerk.com) (authentication)
- **Groq**: [groq.com](https://groq.com) (AI API)
- **OpenAI**: [openai.com](https://openai.com) (AI API)

## 📊 Database Options
- **Supabase** (Recommended): Free tier, easy setup
- **Railway**: Good PostgreSQL hosting
- **Neon**: Serverless PostgreSQL

## 🐛 Common Issues
1. **CORS Errors**: Make sure frontend URL is in backend CORS config
2. **Database Connection**: Check DATABASE_URL format and accessibility
3. **Environment Variables**: Verify all are set in Vercel dashboard
4. **Build Errors**: Check Vercel build logs for missing dependencies

## 📖 Full Guide
See `DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.
