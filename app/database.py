from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL (file in project root)
DATABASE_URL = "sqlite:///./invoicing.db"

# Create engine (core connection to DB)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite
)

# Session factory (used to create DB sessions)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for models
Base = declarative_base()