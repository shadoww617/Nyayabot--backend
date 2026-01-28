from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.rag.retriever import retrieve_laws
from backend.rag.prompt_builder import build_prompt
from backend.ai.openai_client import ask_llm
import json
import os

app = FastAPI(title="NyayaBot – Indian Legal Assistant")

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
# Language detection
# ---------------------------

def detect_language(text: str):
    words = text.lower().split()
    hits = sum(1 for w in words if w in HINGLISH)
    return "hinglish" if hits >= 2 else "english"

# ---------------------------
# Law retrieval (simple & explainable)
# ---------------------------

def retrieve_laws(query):
    found = []

    for sec in IPC:
        if sec["section"].lower() in query.lower() or sec["title"].lower() in query.lower():
            found.append(f"IPC {sec['section']} – {sec['title']}")

    for sec in CRPC:
        if sec["section"].lower() in query.lower() or sec["title"].lower() in query.lower():
            found.append(f"CrPC {sec['section']} – {sec['title']}")

    return found[:5]

# ---------------------------
# Answer builder
# ---------------------------

def build_answer(query, history, lang):
    context = " ".join([h["text"] for h in history[-2:]])

    if lang == "hinglish":
        answer = (
            f"Aapke sawaal ke base par:\n\n"
            f"{query}\n\n"
            f"Is situation ko Indian law ke hisaab se dekha jaata hai. "
            f"Final decision hamesha court aur case ke facts par depend karta hai."
        )
    else:
        answer = (
            f"Based on your question:\n\n"
            f"{query}\n\n"
            f"Under Indian law, the outcome depends on facts, evidence, and court judgment."
        )

    return answer

# ---------------------------
# Routes
# ---------------------------
context = ""

@app.get("/")
def root():
    return {"status": "NyayaBot backend running"}

@app.post("/ask")
def ask_question(req: AskRequest):
    query = req.query.strip()

    conversation_context = ""
    if req.history:
        conversation_context = "\n".join(
            [f"User: {h['user']}\nBot: {h['bot']}" for h in req.history[-3:]]
        )

    language = detect_language(query)

    retrieved_sections = retrieve_laws(query)

    prompt = build_prompt(
        query=query,
        context=conversation_context,
        laws=retrieved_sections,
        language=language
    )

    answer = ask_llm(prompt)

    return {
        "query": query,
        "language": language,
        "answer": answer,
        "references": retrieved_sections
    }
