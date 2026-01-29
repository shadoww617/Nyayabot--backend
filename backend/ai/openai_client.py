import os
import requests
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_answer(prompt: str) -> str:
    try:
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an Indian legal information assistant. "
                        "Explain laws in simple and neutral language. "
                        "Do not give legal advice. "
                        "Do not invent sections."
                        "Do not provide explanations for things outside indian law."
                        "Simply say, please ask me law related questions in case of queries not related to law"
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 500
        }

        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )

        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        if "error" in result:
            return f"OpenAI error: {result['error']['message']}"

        return "No response received."

    except Exception as e:
        print("OpenAI REST error:", repr(e))
        return "Explanation generation failed."
