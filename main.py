


###############################################

# Existing imports
import os
import uuid
import time
from fastapi import FastAPI, Form, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from supabase import create_client, Client
from transformers import pipeline
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access individual keys directly from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Initialize the Hugging Face sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Create FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dummy password for admin authentication
ADMIN_PASSWORD = "password"

# Function to fetch all feedback data from Supabase
def fetch_feedback():
    response = supabase.table("feedback").select("*").execute()
    return response.data if response.data else []

# Fallback function using a pretrained transformer model
def fallback_sentiment_analysis(text: str):
    result = sentiment_analyzer(text)[0]
    return result['label'] if 'label' in result else "Neutral"

# Feedback sentiment analysis function with retry and fallback
async def analyze_feedback_with_retry(text: str, retries=3):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Analyze the sentiment of this feedback: {text}"}
        ]
    }

    async with httpx.AsyncClient() as client:
        attempt = 0
        while attempt < retries:
            try:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                sentiment = result["choices"][0]["message"]["content"].strip()
                return sentiment
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    attempt += 1
                else:
                    print("OpenAI API failed. Using local model for sentiment analysis.")
                    return fallback_sentiment_analysis(text)
    return "Error"

# Function to insert feedback into Supabase
async def insert_feedback(feedback_data):
    feedback_data["feedback_id"] = str(uuid.uuid4())
    feedback_data["sentiment"] = await analyze_feedback_with_retry(feedback_data["feedback_text"])
    response = supabase.table("feedback").insert(feedback_data).execute()
    return response.data if response.data else None

# Route to display feedback form and feedback data
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    feedback_data = fetch_feedback()
    return templates.TemplateResponse("index.html", {"request": request, "feedback_data": feedback_data, "is_admin": False})

@app.post("/submit_feedback")
async def submit_feedback(feedback_text: str = Form(...), user_id: str = Form(...)):
    # Log the incoming data for debugging purposes
    print(f"Received feedback_text: {feedback_text}, user_id: {user_id}")
    
    # Check if any of the form fields are missing
    if not feedback_text or not user_id:
        raise HTTPException(status_code=422, detail="Both feedback text and user ID are required.")

    new_feedback = {
        "feedback_text": feedback_text,
        "user_id": user_id
    }
    inserted_data = await insert_feedback(new_feedback)
    
    if inserted_data:
        return RedirectResponse(url="/", status_code=303)
    else:
        raise HTTPException(status_code=500, detail="Error inserting feedback")

# Route for the admin analysis login page
@app.get("/admin_analysis", response_class=HTMLResponse)
async def admin_analysis(request: Request):
    return templates.TemplateResponse("admin_analysis.html", {"request": request})

# Route to handle analysis access with admin authentication
@app.post("/view_analysis", response_class=HTMLResponse)
async def view_analysis(request: Request, user_id: str = Form(...), password: str = Form(...)):
    if user_id == "admin" and password == ADMIN_PASSWORD:
        feedback_data = fetch_feedback()
        return templates.TemplateResponse("analysis.html", {"request": request, "feedback_data": feedback_data})
    else:
        raise HTTPException(status_code=403, detail="Incorrect admin credentials")
    