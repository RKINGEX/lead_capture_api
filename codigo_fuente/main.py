from fastapi import FastAPI
from database import engine, Base, sessionlocal
from models import Lead
from schemas import Valid_Lead
from llm_service import clasify_lead

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/leads")
def create_lead(lead: Valid_Lead):
    # endpoint to receive lead data and create a new lead
    db = sessionlocal() 

    new_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        request=lead.request,
        notes=lead.notes
    )

    db.add(new_lead)

    db.commit()
    db.refresh(new_lead)

    try:
        result = clasify_lead(new_lead)

        new_lead.temperature = result.temperature

        db.commit()

        

    except Exception as e:

        print({"error": "Error classifying lead", "details": str(e)})

        new_lead.temperature = "pending"

        db.commit()

    db.refresh(new_lead)

    db.close()

    return {"message": "Lead created successfully", 
            "id": new_lead.id,
            "temperature": new_lead.temperature
            }

