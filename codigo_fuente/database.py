from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL") 

engine = create_engine(DATABASE_URL)

sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency function to get a database session for FastAPI endpoints.
    This function creates a new database session using the sessionlocal factory, yields it for use in
    FastAPI endpoints, and ensures that the session is closed after the request is completed.
    """
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
