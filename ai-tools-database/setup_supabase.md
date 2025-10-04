# Supabase Setup Guide

## Option 1: Using Supabase Dashboard (Easiest)

1. **Create Project**:
   - Go to [supabase.com](https://supabase.com)
   - Click "Start your project" → "New project"
   - Choose organization and project settings
   - Set a strong database password
   - Choose a region closest to you

2. **Get Connection Details**:
   - Go to Settings → Database
   - Copy the **Connection string** under "Connection parameters"
   - It looks like: `postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres`

3. **Update .env file**:
   ```bash
   DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres"
   ```

4. **Run Database Schema**:
   - In Supabase dashboard, click **SQL Editor**
   - Copy all content from `schema.sql`
   - Paste into the editor and click **Run**

5. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Start the API**:
   ```bash
   uvicorn main:app --reload
   ```

## Option 2: Using Supabase CLI

1. **Install Supabase CLI**:
   ```bash
   npm install -g supabase
   # or
   bun install supabase
   ```

2. **Login to Supabase**:
   ```bash
   supabase login
   ```

3. **Link your project**:
   ```bash
   supabase link --project-ref YOUR_PROJECT_REF
   ```

4. **Run the schema**:
   ```bash
   supabase db push --schema=public
   ```

## Option 3: Using psql (if you have PostgreSQL installed)

1. **Install PostgreSQL** if not already installed

2. **Run the schema**:
   ```bash
   psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres" -f schema.sql
   ```

## Verify Setup

After running the schema, you can verify everything worked:

1. **Check the API**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Populate examples**:
   ```bash
   curl -X POST http://localhost:8000/api/populate-examples
   ```

3. **Check the database**:
   - In Supabase dashboard, go to **Table Editor**
   - You should see tables: `providers`, `tools`, `categories`, etc.

## Troubleshooting

### Connection Issues
- Verify your `DATABASE_URL` is correct
- Check that your password has no special characters that need URL encoding
- Make sure your Supabase project is active

### Permission Issues
- In Supabase, go to Settings → Database → Connection pooling
- Make sure your connection string uses port 5432 (not 6543)

### API Issues
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that the database connection is working: `curl http://localhost:8000/health`