import os
import json
import re


# ----------------------------
# Load Hinglish dictionary safely
# ----------------------------

BASE_DIR = os.path.dirname(__file__)
HINGLISH_PATH = os.path.join(BASE_DIR, "hinglish_words.json")

with open(HINGLISH_PATH, encoding="utf-8") as f:
    HINGLISH_DICT = json.load(f)


# ----------------------------
# Hinglish → English translator
# ----------------------------

def translate_hinglish(text: str) -> str:
    """
    Converts common Hinglish words into English
    Example:
    police bina warrant phone check kar sakti hai kya
    → police without warrant phone check can do what
    """

    text = text.lower()

    # normalize punctuation
    text = re.sub(r"[?!.]", "", text)

    words = text.split()
    translated = []

    for w in words:
        translated.append(HINGLISH_DICT.get(w, w))

    return " ".join(translated)
