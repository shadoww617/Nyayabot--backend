import os
import traceback
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# Load env variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(
    title="NYAYABOT Backend",
    description="Legal AI Assistant (Hinglish + English)",
    version="1.0"
)

# CORS (important for frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validate API key early
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


@app.get("/")
def root():
    return {
        "status": "running",
        "message": "NYAYABOT backend is live"
    }


@app.post("/ask")
def ask(query: str = Query(..., min_length=3)):
    try:
        prompt = f"""
You are NyayaBot — an Indian legal assistant.
Answer in simple Hinglish.
Explain law clearly, practically, and politely.

User question:
{query}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful Indian legal assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        answer = response.choices[0].message.content

        return {
            "query": query,
            "answer": answer
        }

    except Exception as e:
        print("🔥 ERROR OCCURRED")
        print(traceback.format_exc())

        return {
            "error": "Internal Server Error",
            "details": str(e)
        }
