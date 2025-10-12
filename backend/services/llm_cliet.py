import requests
import json

class LLMClient:
    def query_llm(context: str, question: str) -> str:
        """
        Sends a context-augmented prompt to the local LLM (Ollama or API).
        """
        prompt = f"""You are a helpful assistant. 
        Use the context below to answer the user's question accurately.

        Context:
        {context}

        Question:
        {question}

        Answer:"""

        # Example: call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response from model.")
        else:
            return f"Error from LLM API: {response.text}"

