from fastapi import FastAPI

app = FastAPI()

@app.post("/leads")
async def create_lead(lead: dict):
    # Aquí puedes agregar la lógica para procesar el lead recibido
    return {"message": "Lead creado exitosamente", "lead": lead}