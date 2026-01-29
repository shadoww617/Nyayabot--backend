from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.rag.prompt_builder import build_prompt
from backend.ai.openai_client import ask_llm
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(
    title="NyayaBot",
    description="Indian Legal Assistant",
    version="1.2"
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

BASE_DIR = os.path.dirname(__file__)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

HINGLISH = load_json("backend/nlp/hinglish_words.json")
IPC = load_json("backend/data/ipc.json")
CRPC = load_json("backend/data/crpc.json")

# ---------------------------
# Request schema
# ---------------------------

class AskRequest(BaseModel):
    query: str
    history: list = []

# ---------------------------
# Language detection (improved)
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
    found = []

    q = query.lower()

    for sec in IPC:
        if sec["title"].lower() in q:
            found.append(f"IPC {sec['section']} – {sec['title']}")

    for sec in CRPC:
        if sec["title"].lower() in q:
            found.append(f"CrPC {sec['section']} – {sec['title']}")

    return found[:5]

# ---------------------------
# Routes
# ---------------------------

@app.post("/ask")
def ask(req: AskRequest):

    language = detect_language(req.query)

    conversation = ""
    for msg in req.history[-6:]:
        conversation += f"{msg.role.upper()}: {msg.content}\n"

    if language == "hinglish":
        system_prompt = (
            "You are NyayaBot, an Indian legal assistant. "
            "Reply in clear, natural Hinglish using English letters only. "
            "Be polite, structured and easy to understand."
        )
    else:
        system_prompt = (
            "You are NyayaBot, an Indian legal assistant. "
            "Reply in simple, clear English."
        )

    final_prompt = f"""
Conversation so far:
{conversation}

User question:
{req.query}

Explain clearly using Indian law where relevant.
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
        "answer": response.output_text
    }