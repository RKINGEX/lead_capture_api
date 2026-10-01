import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from schemas import LeadClassification
import logging

logger = logging.getLogger(__name__)

load_dotenv() # It loads environment variables from a .env file,

try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    client = None #Autoset client as none since there was a problem with the API key

def classify_lead(lead):
    # It checks if the client is None, which indicates that the LLM client was not initialized properly. 
    # If the client is None, it raises a RuntimeError with a message indicating that the LLM client is not initialized 
    # Suggests checking the GEMINI_API_KEY.
    if client is None:
        raise RuntimeError("LLM client not initialized - check your GEMINI_API_KEY")

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

    try:
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema":LeadClassification,
            },
        )


        return response.parsed
    
    except genai.exceptions.ServerError as e:
        raise ServerError(f"Server error occurred unable to use LLM: {e}")
    except Exception as e:
        logger.exception("Unexpected error occurred while classifying lead", extra={"details": str(e)})
        raise ((f"Unexpected error occurred: {e}"))