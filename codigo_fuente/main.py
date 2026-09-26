from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()

class Lead(BaseModel):
    name: str = Field(..., description="Nombre del lead")
    email: EmailStr = Field(..., description="Correo electrónico del lead")
    phone: str = Field(..., description="Teléfono del lead")
    request: str = Field(..., description="Solicitud del lead")
    notes: str = Field(description="Notas adicionales del lead")

@app.post("/leads")
def create_lead(lead: Lead):
    # endpoint to receive lead data and create a new lead
    return {"message": "Lead creado exitosamente", 
            "datos": lead.model_dump()}

