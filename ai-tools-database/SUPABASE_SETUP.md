# 🚀 Supabase Schema Setup Guide

## Quick Setup Instructions

1. **Open your Supabase Dashboard**:
   ```
   https://supabase.com/dashboard/project/nsijhyqhjizavcwedqtv
   ```

2. **Go to SQL Editor**:
   - Click "SQL Editor" in the left sidebar
   - Click "New query" to create a new SQL editor tab

3. **Copy and Paste Schema**:
   - Copy the entire content from `schema.sql`
   - Paste it into the SQL Editor
   - Click "Run" to execute

4. **Wait for Completion**:
   - The script will create 8 tables for your AI tools database
   - You should see "Query executed successfully" when done

## Alternative: Use Supabase CLI

If you prefer using the command line:

```bash
# Install Supabase CLI (if not installed)
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref nsijhyqhjizavcwedqtv

# Push the schema
supabase db push --db-url "postgresql://postgres.nsijhyqhjizavcwedqtv:Doug!as1221@nsijhyqhjizavcwedqtv.supabase.co:5432/postgres?sslmode=require"
```

## What Gets Created

The schema creates these tables:
- `providers` - AI provider information (OpenAI, Claude, Gemini, etc.)
- `categories` - Tool categorization
- `tools` - Core tool definitions in standardized format
- `provider_schemas` - Provider-specific tool schemas
- `tool_examples` - Usage examples for each tool
- `field_mappings` - Format conversion mappings
- `validation_rules` - Schema validation rules
- `api_usage` - Usage tracking

## Next Steps After Schema Setup

Once the schema is created, you can:

1. **Test the API**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Populate with Examples**:
   ```bash
   curl -X POST http://localhost:8000/api/populate-examples
   ```

3. **Explore the API**:
   ```bash
   curl http://localhost:8000/api/providers
   curl http://localhost:8000/api/tools?query=weather
   ```

## Troubleshooting

If you encounter connection issues after setting up the schema:
- Wait a few minutes for Supabase to fully provision the database
- Check that your IP isn't blocked by any firewall rules
- Verify the database URL in your `.env` file is correct