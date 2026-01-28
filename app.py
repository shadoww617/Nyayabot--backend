import os
import json
import re
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# -------------------------------------------------
# Load Hinglish grammar words
# -------------------------------------------------

HINGLISH_PATH = "backend/nlp/hinglish_words.json"

with open(HINGLISH_PATH, "r", encoding="utf-8") as f:
    HINGLISH_WORDS = set(json.load(f))

# -------------------------------------------------
# Setup
# -------------------------------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(
    title="NyayaBot",
    description="Indian Legal Assistant with Memory",
    version="1.2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Models
# -------------------------------------------------

class Message(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    query: str
    history: Optional[List[Message]] = []

# -------------------------------------------------
# Improved Hinglish detection
# -------------------------------------------------

def detect_language(text: str) -> str:
    text = text.lower()
    words = re.findall(r"[a-z]+", text)

    hits = sum(1 for w in words if w in HINGLISH_WORDS)

    # threshold-based detection
    if hits >= 2:
        return "hinglish"
    return "english"

# -------------------------------------------------
# API
# -------------------------------------------------

@app.post("/ask")
def ask(req: AskRequest):

    language = detect_language(req.query)

    # ---- memory ----
    conversation = ""
    for msg in req.history[-6:]:
        conversation += f"{msg.role.upper()}: {msg.content}\n"

    # ---- system behavior ----
    if language == "hinglish":
        system_prompt = (
            "You are NyayaBot, an Indian legal assistant. "
            "Reply strictly in simple Hinglish using Roman Hindi. "
            "Do not switch to pure English."
        )
    else:
        system_prompt = (
            "You are NyayaBot, an Indian legal assistant. "
            "Reply clearly in simple English."
        )

    final_prompt = f"""
Conversation so far:
{conversation}

User question:
{req.query}

Explain applicable Indian law clearly.
Do not provide legal advice.
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": final_prompt}
        ]
    )

    return {
        "language": language,
        "answer": response.output_text
    }
