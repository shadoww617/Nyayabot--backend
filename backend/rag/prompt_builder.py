def build_prompt(query, docs):
    context_blocks = []

    for d in docs:
        block = f"""
{d['title']}
Source: {d['source']}
{d['content']}
"""
        context_blocks.append(block)

    context = "\n".join(context_blocks)

    return f"""
You are an Indian legal information assistant.

User Question:
{query}

Relevant Legal Provisions:
{context}

Explain the legal position in simple language.
Do not give legal advice.
Do not invent laws.
"""
