# AIPM (AI Project Manager)

A comprehensive AI project management system with tools and databases for AI development workflows.

## Components

### 🤖 AI Tools Database
A complete database and API system for managing AI SDK tool and function definitions across major AI providers.

**Features:**
- Multi-provider support (OpenAI, Claude, Gemini, Mistral, Cohere)
- FastAPI-based REST API with 20+ endpoints
- Supabase integration with PostgreSQL database
- MCP server for AI assistant integration
- Format conversion between different AI provider schemas
- Validation system for tool schemas

**Quick Start:**
```bash
cd ai-tools-database
pip install -r requirements.txt
python simple_server.py
```

**API Endpoints:**
- `GET /health` - System health check
- `GET /api/providers` - List supported AI providers
- `POST /api/tools` - Add new tools
- `GET /api/tools` - Search and retrieve tools

**Database Setup:**
1. Set up Supabase project and configure `.env` with your credentials
2. Run the schema from `ai-tools-database/schema.sql` in Supabase SQL Editor
3. Start the API server and populate with example tools

## Repository Structure

```
AIPM/
├── ai-tools-database/     # AI SDK tools database system
├── src/                   # Additional project components
├── config.yaml           # Project configuration
├── pyproject.toml        # Python project configuration
└── README.md            # This file
```

## GitHub Integration

This project is connected to GitHub at:
```
https://github.com/toobutta/AIPM
```

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/toobutta/AIPM.git
   cd AIPM
   ```

2. Set up the AI Tools Database:
   ```bash
   cd ai-tools-database
   # Follow the setup instructions in FINAL_SETUP.md
   ```

3. Start the development server:
   ```bash
   python simple_server.py
   ```

## License

This project is part of the AIPM (AI Project Manager) system.