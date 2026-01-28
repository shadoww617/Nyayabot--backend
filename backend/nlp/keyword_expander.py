KEYWORD_MAP = {
    "police": ["investigating officer", "law enforcement"],
    "phone": ["mobile", "digital device", "electronic device"],
    "arrest": ["custody", "detention"],
    "warrant": ["court order", "judicial permission"],
    "cyber": ["online", "digital crime"],
    "privacy": ["personal liberty", "data protection"]
}

def expand_keywords(query: str) -> str:
    expanded = query
    for word, synonyms in KEYWORD_MAP.items():
        if word in query:
            expanded += " " + " ".join(synonyms)
    return expanded
