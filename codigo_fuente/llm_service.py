import os
from dotenv import load_dotenv
from google import genai
from schemas import LeadClassification

load_dotenv()

try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except:
    client = None

def clasify_lead(lead):

    prompt = f"""
    You are a lead classification expert. You will receive information about a lead in JSON format. 

    Your task is to classify the lead as either "cold" (cold) or "hot" (hot) based on the provided information.

    You can consider a lead hot if demonstrates interest in the product or service, and is likely to convert into a customer.
    
    You can consider a lead cold if shows little or no interest in the product or service, and is unlikely to 
    convert into a customer.
    
    Lead Data:
    
    name: {lead.name}
    email: {lead.email}
    phone: {lead.phone}
    request: {lead.request}
    notes: {lead.notes}

    Please return the classification and a brief reason for your classification
    """

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema":LeadClassification,
        },
    )

    return response.parsed