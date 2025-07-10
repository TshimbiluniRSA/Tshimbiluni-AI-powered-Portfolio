from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database path (created in root of src/)
DATABASE_URL = "sqlite:///./portfolio.db"

# Create engine (required check_same_thread=False for SQLite)
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal will be used to interact with DB in routes/services
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is used for declaring models
Base = declarative_base()
