# promethion/utils/classifier.py
import re

def classify_text(text: str) -> str:
    """Naive keyword-based classifier. Replace with LLM later."""
    text_lower = text.lower()
    if re.search(r"\b(tech|ai|software|computer|robot)\b", text_lower):
        return "tech"
    if re.search(r"\b(code|python|developer|programming)\b", text_lower):
        return "coding"
    if re.search(r"\b(health|home|care|family)\b", text_lower):
        return "home_care"
    if re.search(r"\b(wellness|mental|welfare|support)\b", text_lower):
        return "general_welfare"
    if re.search(r"\b(tips|motivation|life)\b", text_lower):
        return "life_practice"
    return "news"
