from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, HTTPException
from database import engine, Base, sessionlocal
from models import Lead
from schemas import Valid_Lead
from llm_service import clasify_lead

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/leads", status_code=201)
def create_lead(lead: Valid_Lead):
    # endpoint to receive lead data and create a new lead
    db = sessionlocal() 

    try:
        new_lead = Lead(
                name=lead.name,
                email=lead.email,
                phone=lead.phone,
                request=lead.request,
                notes=lead.notes)
    except Exception as e:
        raise HTTPException(status_code=422, detail={"error": "Invalid lead data", "details": str(e)})

    try:
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
        print({"error": "LLM client unavailable", "details": str(e)})
        new_lead.temperature = "pending"
        db.commit()

    except Exception as e:
        print({"error": "Unexpected classification error", "details": str(e)})
        new_lead.temperature = "pending"
        db.commit()

    db.refresh(new_lead)

    db.close()

    return {"message": "Lead created successfully", 
            "id": new_lead.id,
            "temperature": new_lead.temperature
            }

