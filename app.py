from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# NLP
from backend.nlp.translator import translate_hinglish
from backend.nlp.query_normalizer import normalize_query
from backend.nlp.keyword_expander import expand_keywords
from backend.nlp.intent_classifier import classify_intent

# RAG
from backend.rag.retriever import retrieve
from backend.rag.ranker import rank_documents
from backend.rag.prompt_builder import build_prompt

# LLM
from backend.ai.openai_client import generate_answer


# -------------------------
# FastAPI setup
# -------------------------

app = FastAPI(
    title="NyayBot API",
    version="1.0",
    description="Indian Legal Information Assistant (Educational Use Only)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # frontend + github pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Request schema
# -------------------------

class AskRequest(BaseModel):
    query: str


# -------------------------
# Main endpoint
# -------------------------

@app.post("/ask")
def ask(req: AskRequest):
    try:
        user_query = req.query.strip()

        # 1️⃣ Hinglish → English
        translated = translate_hinglish(user_query)

        # 2️⃣ Normalize
        normalized = normalize_query(translated)

        # 3️⃣ Expand keywords
        expanded = expand_keywords(normalized)

        # 4️⃣ Intent classification
        intent = classify_intent(expanded)

        # 5️⃣ Retrieve legal docs
        docs = retrieve(expanded)

        # 6️⃣ Rank documents
        ranked_docs = rank_documents(expanded, docs)

        # 7️⃣ Build LLM prompt
        prompt = build_prompt(
            query=expanded,
            intent=intent,
            documents=ranked_docs
        )

        # 8️⃣ Generate answer
        answer = generate_answer(prompt)

        return {
            "query": user_query,
            "translated_query": translated,
            "intent": intent,
            "answer": answer,
            "sources": [
                {
                    "section": d.get("title"),
                    "source": d.get("source")
                }
                for d in ranked_docs[:5]
            ],
            "disclaimer": "Educational information only. Not legal advice."
        }

    except Exception as e:
        return {
            "error": str(e)
        }
