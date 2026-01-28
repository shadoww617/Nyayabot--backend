def rank_documents(docs, query):
    q = query.lower()
    ranked = []

    for doc in docs:
        score = 0

        if "police" in q and doc["domain"] == "Criminal Procedure":
            score += 3
        if "arrest" in q and doc["domain"] == "Criminal Procedure":
            score += 2
        if "cyber" in q and doc["domain"] == "Cyber Law":
            score += 3
        if "privacy" in q and "Constitution" in doc["source"]:
            score += 3

        ranked.append((score, doc))

    ranked.sort(reverse=True, key=lambda x: x[0])
    return [d[1] for d in ranked[:4]]
