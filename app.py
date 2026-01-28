import os
import traceback
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# Load env vars
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(
    title="NyayaBot Backend",
    description="Indian Legal AI Assistant (Hinglish)",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create client
client = OpenAI(api_key=OPENAI_API_KEY)


@app.get("/")
def root():
    return {"status": "NyayaBot backend running"}


@app.post("/ask")
def ask(query: str = Query(..., min_length=3)):
    try:
        prompt = f"""
You are NyayaBot — an Indian legal assistant.

Answer in simple Hinglish.
Explain law practically.
Avoid heavy legal jargon.

User question:
{query}
"""

        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )

        answer = response.output_text

        return {
            "query": query,
            "answer": answer
        }

    except Exception as e:
        print("🔥 ERROR")
        print(traceback.format_exc())

        return {
            "error": "Internal Server Error",
            "details": str(e)
        }
