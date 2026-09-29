from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, HTTPException, Depends, Query
from database import engine, Base, get_db
from models import Lead
from schemas import Valid_Lead
from llm_service import clasify_lead
import math

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/leads", status_code=201)
def create_lead(lead: Valid_Lead, db: Session = Depends(get_db)):
    # endpoint to receive lead data and create a new lead) 

    try:
    # Error handling for incorrect POST format (missing required fields or invalid data types)
        new_lead = Lead(
                name=lead.name,
                email=lead.email,
                phone=lead.phone,
                request=lead.request,
                notes=lead.notes)
    except Exception as e:
        raise HTTPException(status_code=422, detail={"error": "Invalid lead data", "details": str(e)})

    try:
    # Error handling for unique date repetition (email or phone number) and invalid data
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={"error": "Lead with this email or phone number already exists", 
                                                     "details": "Email or phone number already in use"})

    

    try:
        result = clasify_lead(new_lead)

        new_lead.temperature = result.temperature

        db.commit()

    except RuntimeError as e:
    #It catches the RuntimeError exception raised by the clasify_lead function when the LLM client is unavailable. 
    #It prints an error message and sets the lead's temperature to "pending" before committing the changes to the database.
        print({"error": "LLM client unavailable", "details": str(e)})
        new_lead.temperature = "pending"
        db.commit()

    except Exception as e:
    #It catches any other unexpected exceptions raised by the clasify_lead function.
        print({"error": "Unexpected classification error", "details": str(e)})
        new_lead.temperature = "pending"
        db.commit()

    db.refresh(new_lead)

    return {"message": "Lead created successfully", 
            "id": new_lead.id,
            "temperature": new_lead.temperature
            }

@app.get("/leads", status_code=200)
def get_leads(limit: int = Query(10, ge=1, le=100, description="Number of leads to retrieve per page (1-100)"),
              pages: int = Query(1, ge=1, description="Page number to retrieve (1-based)"),
              db: Session = Depends(get_db)):
    """This retrieves a list of leads from the database, with optional pagination parameters (limit and pages)."""

    offset = (pages - 1) * limit

    total_leads = db.query(Lead).count()

    total_pages = math.ceil(total_leads / limit)
    
    leads = (db.query(Lead)
             .offset(offset)
             .limit(limit)
             .all()
            )
    
    return {"pages": pages,
            "limit": limit,
            "total_leads": total_leads,
            "total_pages": total_pages,
            "leads": leads}

@app.get("/leads/{id}", status_code=200)
def get_lead(id: int, db: Session = Depends(get_db)):
    """This retrieves a specific lead from the database based on the provided ID."""
    
    lead = db.query(Lead).filter(Lead.id == id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail={"error": "Lead not found", "details": f"No lead found with ID: {id}"})
    
    return lead

@app.patch("/leads/{id}", status_code=200)
def update_lead(id: int, lead: Valid_Lead, db: Session = Depends(get_db)):
    """This updates a specific lead in the database based on the provided ID and new lead data."""
    
    existing_lead = db.query(Lead).filter(Lead.id == id).first()
    
    if not existing_lead:
        raise HTTPException(status_code=404, detail={"error": "Lead not found", "details": f"No lead found with ID: {id}"})
    
    try:
        existing_lead.name = lead.name
        existing_lead.email = lead.email
        existing_lead.phone = lead.phone
        existing_lead.request = lead.request
        existing_lead.notes = lead.notes
        
        db.commit()
        db.refresh(existing_lead)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={"error": "Lead with this email or phone number already exists", 
                                                     "details": "Email or phone number already in use"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail={"error": "Unexpected error occurred", "details": str(e)})
    
    return {"message": "Lead updated successfully", 
            "id": existing_lead.id,
            "temperature": existing_lead.temperature
            }