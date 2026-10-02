from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from codigo_fuente.models import Lead

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLite 
sqlite_engine = create_engine("sqlite:///leads.db")

sqlite_SessionLocal = sessionmaker(bind=sqlite_engine)

# PostgreSQL
postgresql_engine = create_engine(DATABASE_URL)

postgresql_SessionLocal = sessionmaker(bind=postgresql_engine)

sqlite_db = sqlite_SessionLocal()
postgresql_db = postgresql_SessionLocal()

try:
    leads = sqlite_db.query(Lead).all()

    if not leads:
        raise ValueError("No leads found in the SQLite database.")
    
    for lead in leads:
        new_lead = Lead(
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            request=lead.request,
            notes=lead.notes,
            temperature=lead.temperature
        )
        postgresql_db.add(new_lead)
    postgresql_db.commit()
    print("Data migration completed successfully.")

except ValueError as ve:
    print(f"Data migration error: {ve}")

except Exception as e:
    postgresql_db.rollback()
    print(f"An error occurred: {e}")
    
finally:
    sqlite_db.close()
    postgresql_db.close()
