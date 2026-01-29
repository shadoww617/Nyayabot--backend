from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from openai import OpenAI
from typing import List, Optional

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(
    title="NyayaBot",
    description="Indian Legal Assistant",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Load data
# ---------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

HINGLISH = load_json("backend/nlp/hinglish_words.json")
IPC = load_json("backend/data/ipc.json")
CRPC = load_json("backend/data/crpc.json")

# ---------------------------
# Request model
# ---------------------------

class Message(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    query: str
    history: Optional[List[Message]] = []

# ---------------------------
# Language detection
# ---------------------------

def detect_language(text: str):
    words = text.lower().split()
    hits = sum(1 for w in words if w in HINGLISH)

    if hits >= 1:
        return "hinglish"
    return "english"

# ---------------------------
# Law retrieval
# ---------------------------

def retrieve_laws(query):
    q = query.lower()
    refs = []

    for sec in IPC:
        if sec["title"].lower() in q:
            refs.append(f"IPC {sec['section']} – {sec['title']}")

    for sec in CRPC:
        if sec["title"].lower() in q:
            refs.append(f"CrPC {sec['section']} – {sec['title']}")

    return refs[:5]

# ---------------------------
# API
# ---------------------------

@app.post("/ask")
def ask(req: AskRequest):

    language = detect_language(req.query)
    law_refs = retrieve_laws(req.query)

    # Build conversation memory
    conversation = ""
    for msg in req.history[-6:]:
        conversation += f"{msg.role.upper()}: {msg.content}\n"

    if language == "hinglish":
        system_prompt = (
            "You are NyayaBot, an Indian legal assistant.\n"
            "Reply ONLY in Hinglish using English letters.\n"
            "Do NOT say Bot, AI, Assistant or system.\n"
            "Be polite, structured and easy to understand."
        )
    else:
        system_prompt = (
            "You are NyayaBot, an Indian legal assistant.\n"
            "Reply in simple, clear English.\n"
            "Do NOT say Bot, AI, Assistant or system."
        )

    final_prompt = f"""
Previous conversation:
{conversation}

User question:
{req.query}

If relevant, explain using Indian law.
Be educational, not judgmental.
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": final_prompt}
        ],
    )

    return {
        "language": language,
        "law_references": law_refs,
        "answer": response.output_text
    }
