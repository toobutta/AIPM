"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import settings

# Create database engine
engine = create_engine(settings.database_url)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    """
    from models import Base
    Base.metadata.create_all(bind=engine)

def drop_db():
    """
    Drop all database tables (for testing)
    """
    from models import Base
    Base.metadata.drop_all(bind=engine)