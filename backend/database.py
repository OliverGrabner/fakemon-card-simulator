from sqlalchemy import create_engine, Column, Integer, Text, TIMESTAMP, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Load .env file only if running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

# Weird mixup fix between SQLAlchemy and Render 
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL and "sqlite" in DATABASE_URL:
    # SQLite (testing) - minimal config with threading override for tests
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"check_same_thread": False}  # Allow FastAPI TestClient to work
    )
else:
    # PostgreSQL (production) - with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=True
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Database Model
class GeneratedCard(Base): 
    # Table : id (int), image (base64), upvotes (int), created (datetime)
    __tablename__ = "generated_cards"

    id = Column(Integer, primary_key=True, index=True)
    image_data = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0, index=True)
    created_at = Column(TIMESTAMP, default=datetime.now(), index=True)

    # Sort by upvotes vs created date indexing performance optimization
    __table_args__ = (
        Index('idx_upvotes_desc', upvotes.desc()),
        Index('idx_created_at_desc', created_at.desc()),
    )


# Initialize database
def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created")


# Dependency for getting database session
def get_db():
    """Dependency for getting database session in FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
