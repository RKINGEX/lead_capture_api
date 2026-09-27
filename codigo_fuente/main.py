from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from database import engine, Base, sessionlocal
from models import Lead

Base.metadata.create_all(bind=engine)

app = FastAPI()

class Valid_Lead(BaseModel):
    name: str = Field(..., description="Nombre del lead")
    email: EmailStr = Field(..., description="Correo electrónico del lead")
    phone: str = Field(..., description="Teléfono del lead")
    request: str = Field(..., description="Solicitud del lead")
    notes: str = Field(description="Notas adicionales del lead")

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

    db.close()

    return {"message": "Lead creado exitosamente", 
            "id": new_lead.id}

