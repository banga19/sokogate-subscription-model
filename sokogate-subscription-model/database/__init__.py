from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .init_db import DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()