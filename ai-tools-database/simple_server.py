#!/usr/bin/env python3
"""
Simple FastAPI server without database dependencies
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json

app = FastAPI(title="AI Tools Database API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Tools Database API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database_status": "pending_setup",
        "version": "1.0.0"
    }

@app.get("/api/providers")
async def get_providers():
    """Return hardcoded providers list without database"""
    providers = [
        {"id": 1, "name": "openai", "display_name": "OpenAI"},
        {"id": 2, "name": "claude", "display_name": "Claude"},
        {"id": 3, "name": "gemini", "display_name": "Gemini"},
        {"id": 4, "name": "mistral", "display_name": "Mistral"},
        {"id": 5, "name": "cohere", "display_name": "Cohere"}
    ]
    return providers

if __name__ == "__main__":
    import uvicorn
    print("Starting simple API server on http://localhost:8000")
    print("Database connection temporarily disabled - using mock data")
    uvicorn.run(app, host="0.0.0.0", port=8000)