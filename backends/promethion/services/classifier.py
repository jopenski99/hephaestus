import requests
from typing import Optional, Dict, List
from promethion.api.core.config import settings
from promethion.services.llm_handler import LLMHandler

class GeneralClassifier:
    """
    Hybrid classifier for articles and documents.
    - Allows manual category tagging.
    - Falls back to LLM-based auto-categorization via Ollama.
    """

    def __init__(self, model: str = None):
        self.model = settings.CLASSIFIER_NAME if model is None else model
        self.api_key = settings.CLASSIFIER_KEY
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")
        self.base_url = settings.CLASSIFIER_URL
        self.categories = [
            "Tech",
            "News",
            "Life Practice",
            "Coding",
            "General Welfare",
            "Home Care",
            "Science",
            "Education",
            "Health",
            "Law",
            "Politics",
            "Environment",
        ]

    def _query_llm(self, text: str) -> str:
        """Internal: Query the local Ollama model for classification."""
        prompt = f"""
        You are a content classifier.
        Given the text below, identify the most appropriate category.

        Categories: {', '.join(self.categories)}

        Text:
        {text[:1000]}

        Respond ONLY with the best matching category name.
        """

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=60,
            )

            if response.status_code == 200:
                data = response.json()
                result = data.get("response", "").strip()
                return result if result in self.categories else "General Welfare"
            else:
                print(f"❌ LLM API error: {response.text}")
                return "Unknown"

        except Exception as e:
            print(f"❌ Classification failed: {e}")
            return "Unknown"

    def classify(self, text: str, variant: str = "default") -> Dict[str, str]:
        
        text = text.strip()
        model = settings.CLASSIFIER_NAME 
        api_key = settings.CLASSIFIER_KEY
        base_url = settings.CLASSIFIER_URL
        port = settings.CLASSIFIER_PORT
        
        llm = LLMHandler(model=model, base_url=base_url, api_key=api_key, port=port)
        category = llm.handleLLM(text,"classification",None,variant)
        
        return {"category": category}
    def list_categories(self) -> List[str]:
        """Returns the list of supported categories."""
        return self.categories
