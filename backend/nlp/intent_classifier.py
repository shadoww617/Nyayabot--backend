def classify_intent(query: str):

    q = query.lower()

    if any(word in q for word in ["punishment", "jail", "fine", "sentence"]):
        return "punishment_information"

    if any(word in q for word in ["can", "allowed", "legal", "illegal", "valid"]):
        return "legality_check"

    if any(word in q for word in ["how", "procedure", "process", "steps"]):
        return "legal_procedure"

    if any(word in q for word in ["right", "rights", "privacy", "freedom"]):
        return "fundamental_rights"

    if any(word in q for word in ["police", "arrest", "search", "warrant"]):
        return "police_powers"

    return "general_legal_query"
