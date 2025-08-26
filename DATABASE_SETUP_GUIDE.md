# Database & Environment Variables Setup Guide

## Step 1: Setting Up PostgreSQL Database with Supabase

### 1.1 Create Supabase Account
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub (recommended) or email
4. Verify your email if needed

### 1.2 Create New Project
1. Click "New project"
2. Choose your organization (or create one)
3. Fill in project details:
   - **Name**: `jurist-ai-db` (or any name you prefer)
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your location
   - **Pricing Plan**: Free tier (up to 500MB, 2 CPU cores)
4. Click "Create new project"
5. Wait 2-3 minutes for setup to complete

### 1.3 Get Database Connection String
1. In your Supabase dashboard, go to **Settings** → **Database**
2. Scroll down to "Connection string"
3. Copy the **URI** connection string
4. It should look like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with the password you set earlier
6. **Save this connection string** - you'll need it for environment variables

### 1.4 Enable Required Extensions (Optional but Recommended)
1. Go to **Database** → **Extensions**
2. Enable these extensions for your AI app:
   - `vector` (for AI embeddings)
   - `pg_stat_statements` (for query optimization)
   - `pgcrypto` (for advanced encryption)

## Step 2: Getting Required API Keys

### 2.1 Clerk Authentication
1. Go to [clerk.com](https://clerk.com)
2. Sign up and create a new application
3. Choose "Next.js" as your framework
4. Copy these keys from the dashboard:
   - **Publishable Key**: `pk_test_...`
   - **Secret Key**: `sk_test_...`

### 2.2 Groq API (Fast AI Inference)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with Google/GitHub or email
3. Go to **API Keys** section
4. Click "Create API Key"
5. Name it "JuristAI" and copy the key: `gsk_...`

### 2.3 OpenAI API (Alternative AI Provider)
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up and add payment method (required for API access)
3. Go to **API Keys**
4. Click "Create new secret key"
5. Name it "JuristAI" and copy the key: `sk-...`

## Step 3: Environment Variables Configuration

### 3.1 Backend Environment Variables
Create a file called `backend/.env` with these variables:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# AI Services
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here

# JWT Configuration
SECRET_KEY=your_very_secure_secret_key_at_least_32_characters_long_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
```

### 3.2 Frontend Environment Variables
Create a file called `.env.local` in your root directory:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# AI Services (if needed by frontend)
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here

# Database (if needed by frontend)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

## Step 4: Testing Your Database Connection

### 4.1 Test Backend Connection
1. Navigate to your backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Test database connection with this Python script:
   ```python
   # test_db.py
   import os
   from sqlalchemy import create_engine, text
   from dotenv import load_dotenv
   
   load_dotenv()
   
   DATABASE_URL = os.getenv("DATABASE_URL")
   
   try:
       engine = create_engine(DATABASE_URL)
       with engine.connect() as connection:
           result = connection.execute(text("SELECT version()"))
           print("✅ Database connection successful!")
           print(f"PostgreSQL version: {result.fetchone()[0]}")
   except Exception as e:
       print(f"❌ Database connection failed: {e}")
   ```

4. Run the test:
   ```bash
   python test_db.py
   ```

### 4.2 Test Frontend Environment
1. In your root directory, run:
   ```bash
   npm run dev
   ```

2. Check the console for any environment variable errors

## Step 5: Security Best Practices

### 5.1 Generate Secure SECRET_KEY
Use this Python script to generate a secure secret key:

```python
import secrets
import string

def generate_secret_key(length=32):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

print("Generated SECRET_KEY:")
print(generate_secret_key(32))
```

### 5.2 Environment File Security
- **NEVER** commit `.env` or `.env.local` files to Git
- Add them to your `.gitignore`:
  ```
  .env
  .env.local
  .env.*.local
  ```

### 5.3 Production Environment Variables
When deploying to Vercel, you'll set these same variables in the Vercel dashboard:
1. Go to your Vercel project
2. Settings → Environment Variables
3. Add each variable one by one
4. Make sure to select the right environment (Production, Preview, Development)

## Troubleshooting

### Common Database Issues:
1. **Connection timeout**: Check if your IP is allowed (Supabase allows all by default)
2. **Invalid password**: Ensure you're using the correct database password
3. **SSL required**: Supabase requires SSL connections (usually handled automatically)

### Common API Key Issues:
1. **Clerk keys not working**: Make sure you're using the correct environment (test vs production)
2. **OpenAI quota exceeded**: Check your usage limits and billing
3. **Groq rate limits**: Free tier has rate limits, consider upgrading if needed

### Environment Variable Issues:
1. **Variables not loading**: Restart your development server after adding new variables
2. **Frontend can't access backend**: Check CORS configuration and API URL
3. **Build fails**: Ensure all required variables are set in Vercel dashboard

## Next Steps

Once you have:
- ✅ Database connection string from Supabase
- ✅ API keys from Clerk, Groq, and OpenAI
- ✅ Environment files configured
- ✅ Tested database connection

You're ready to deploy to Vercel! Follow the deployment guide in `QUICK_DEPLOYMENT.md`.


