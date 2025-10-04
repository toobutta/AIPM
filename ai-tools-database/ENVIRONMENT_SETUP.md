# Environment Variables Setup Guide

## 🚀 Quick Setup

1. **Copy the `.env` file** and update with your actual Supabase credentials
2. **Get your Supabase details** from the Supabase dashboard
3. **Update the required fields** marked with `YOUR_...`

## 📋 Required Variables

### Database Configuration
```bash
# Replace with your actual Supabase database URL
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT_REF.supabase.co:5432/postgres
```

**Where to find these values:**
- Go to your Supabase project dashboard
- Click **Settings** → **Database**
- Copy the **Connection string** under "Connection parameters"
- It looks like: `postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres`

### Optional Supabase Client Variables
```bash
# Optional: For direct Supabase features
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
SUPABASE_SERVICE_KEY=YOUR_SUPABASE_SERVICE_KEY
```

**Where to find these values:**
- Go to **Settings** → **API** in your Supabase dashboard
- Copy the **Project URL** (for SUPABASE_URL)
- Copy the **anon** and **service_role** keys

## 🔧 Optional Configuration

### API Settings
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
```

### Security
```bash
# Change this in production!
SECRET_KEY=your-secret-key-here-change-this-in-production
```

### Database Pool Settings (Production)
```bash
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
```

### CORS Settings
```bash
# Comma-separated list of allowed origins
ALLOWED_ORIGINS=*
# Example for specific domains:
# ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Rate Limiting
```bash
RATE_LIMIT_ENABLED=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Caching (Redis)
```bash
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

### Monitoring
```bash
SENTRY_DSN=YOUR_SENTRY_DSN
METRICS_ENABLED=false
```

## 🎯 Step-by-Step Setup

### 1. Get Supabase Database URL
1. Go to [supabase.com](https://supabase.com)
2. Open your project
3. Go to **Settings** → **Database**
4. Scroll to "Connection parameters"
5. Copy the **Connection string**

### 2. Update .env File
```bash
# Replace this line with your actual connection string:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT_REF.supabase.co:5432/postgres
```

### 3. (Optional) Get Supabase API Keys
1. Go to **Settings** → **API**
2. Copy **Project URL** → SUPABASE_URL
3. Copy **anon** key → SUPABASE_ANON_KEY
4. Copy **service_role** key → SUPABASE_SERVICE_KEY

### 4. Test Your Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Test database connection
python quick_start.py

# Or manually:
uvicorn main:app --reload
```

## 🔍 Verification

### Health Check
```bash
curl http://localhost:8000/health
```

### Test Database Connection
```bash
curl http://localhost:8000/api/providers
```

### Check API Documentation
- Open: http://localhost:8000/docs
- Should see the API documentation interface

## ⚠️ Common Issues

### Connection Refused
- Check that your DATABASE_URL is correct
- Verify your Supabase project is active
- Make sure you're using port 5432 (not 6543)

### Permission Denied
- Double-check your password in the DATABASE_URL
- Make sure special characters are URL-encoded

### Database Not Found
- Run the schema.sql in Supabase SQL Editor first
- Verify the database name is "postgres" (default)

### SSL Issues
- Add `?sslmode=require` to your DATABASE_URL if needed
- Example: `...supabase.co:5432/postgres?sslmode=require`

## 🚀 Production Considerations

1. **Change SECRET_KEY** to something secure
2. **Set RATE_LIMIT_ENABLED=true**
3. **Configure proper CORS origins**
4. **Enable monitoring with SENTRY_DSN**
5. **Set up Redis for caching**
6. **Use HTTPS in production**

## 📚 Example Production .env

```bash
# Database
DATABASE_URL=postgresql://postgres:secure_password@project-ref.supabase.co:5432/postgres?sslmode=require

# Supabase
SUPABASE_URL=https://project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Security
SECRET_KEY=your-very-secure-secret-key-here-64-chars-long

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
METRICS_ENABLED=true

# Logging
LOG_LEVEL=WARNING
```