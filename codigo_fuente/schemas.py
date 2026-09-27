from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class Valid_Lead(BaseModel):
    name: str = Field(..., description="Nombre del lead")
    email: EmailStr = Field(..., description="Correo electrónico del lead")
    phone: str = Field(..., description="Teléfono del lead")
    request: str = Field(..., description="Solicitud del lead")
    notes: str = Field(description="Notas adicionales del lead")

class LeadClassification(BaseModel):
    temperature: Literal["cold", "hot"] = Field(..., description="Classification of the lead based on temperature")
    reason: str = Field(..., description="Reason for the classification")

