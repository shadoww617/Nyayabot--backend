import json
import os

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data"
)

FILES = [
    "ipc.json",
    "crpc.json",
    "evidence_act.json",
    "it_act.json",
    "constitution.json"
]

def load_documents():
    docs = []
    for f in FILES:
        path = os.path.join(DATA_PATH, f)
        with open(path, encoding="utf-8") as file:
            docs.extend(json.load(file))
    return docs

DOCUMENTS = load_documents()

def retrieve(query: str, top_k=8):
    q = query.lower()
    results = []

    for doc in DOCUMENTS:
        text = (doc.get("title","") + " " + doc.get("content","")).lower()
        if any(word in text for word in q.split()):
            results.append(doc)

    return results[:top_k]
