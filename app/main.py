from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if you use one for API key)
load_dotenv() 

# Import core components from the new modules
from .database import SCHEMA_STR, engine
from .openai_utils import text_to_sql_qa

# Define the data model for the API request body
class Question(BaseModel):
    question: str

app = FastAPI(
    title="Text-to-SQL Microservice",
    description="A service that translates natural language to SQL and provides a grounded answer."
)

@app.post("/query")
def answer_question(q: Question):
    """
    Endpoint that takes a natural language question and returns a factual answer
    by executing the full Text-to-SQL pipeline.
    """
    if not os.getenv("OPENAI_API_KEY"):
         raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable not set.")
        
    try:
        # Pass the safety function to the pipeline
        answer = text_to_sql_qa(
            question=q.question, 
            schema=SCHEMA_STR, 
            engine=engine
            )
        return {"question": q.question, "answer": answer}
        
    except ValueError as e:
        # Catches the error raised by the safety check
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # General error handler
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error.")

@app.get("/health")
def health_check():
    """Simple endpoint to verify the service is running."""
    return {"status": "ok", "message": "Text-to-SQL service is running."}