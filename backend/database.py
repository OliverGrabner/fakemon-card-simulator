from sqlalchemy import create_engine, Column, Integer, Text, TIMESTAMP, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Render provides DATABASE_URL starting with postgres://
# SQLAlchemy 2.0 requires postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Database Model
class GeneratedCard(Base):
    __tablename__ = "generated_cards"

    id = Column(Integer, primary_key=True, index=True)
    image_data = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)

    # Indexes for performance
    __table_args__ = (
        Index('idx_upvotes_desc', upvotes.desc()),
        Index('idx_created_at_desc', created_at.desc()),
    )


# Initialize database
def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


# Dependency for getting database session
def get_db():
    """Dependency for getting database session in FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
