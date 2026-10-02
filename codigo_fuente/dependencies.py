from codigo_fuente.database import sessionlocal
from fastapi import  HTTPException, Depends
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv("API_KEY")  # Retrieve the API key from environment variables

api_key_header = APIKeyHeader(name="X-API-Key")

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

def verify_api_key(x_api_key: str = Depends(api_key_header)):
    """Dependency function to verify the API key for FastAPI endpoints."""
    if x_api_key != api_key:
        logger.warning("Invalid API Key attempt")
        raise HTTPException(status_code=403, 
                            detail="Invalid API Key")

    return x_api_key
