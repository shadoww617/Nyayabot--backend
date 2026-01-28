from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.nlp.translator import translate_hinglish
from backend.nlp.query_normalizer import normalize_query
from backend.nlp.keyword_expander import expand_keywords
from backend.nlp.intent_classifier import classify_intent

from backend.rag.retriever import retrieve
from backend.rag.ranker import rank_documents
from backend.rag.prompt_builder import build_prompt

from backend.ai.openai_client import generate_answer

app = FastAPI(title="NyayBot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
def ask(query: str):

    q1 = translate_hinglish(query)
    q2 = normalize_query(q1)
    q3 = expand_keywords(q2)

    intent = classify_intent(q3)

    docs = retrieve(q3)
    ranked = rank_documents(q3, docs)

    prompt = build_prompt(
        query=query,
        intent=intent,
        documents=ranked
    )

    answer = generate_answer(prompt)

    return {
        "query": query,
        "intent": intent,
        "documents": ranked,
        "answer": answer
    }
