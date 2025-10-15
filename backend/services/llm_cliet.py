import requests
import json
from backend.api.core.config import settings
class LLMClient:
    def __init__(self):
        self.base_url = settings.AI_HOST + ":" + str(settings.AI_PORT)
        print(f"🔧 LLM Client configured to use {self.base_url}")

    def query_llm(self, context: str, question: str) -> str:
        print(f"🔎 Querying LLM with context: “{context}” and question: “{question}”")
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the context to answer accurately."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
        ]

        response = requests.post(
            self.base_url + "/api/chat",
            json={"model": settings.LLM_MODEL, "messages": messages, "stream": False}
        )

        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            return message.get("content", "No response from model.")
        else:
            return f"Error from LLM API: {response.text}"
    
    def stream_llm(self, context: str, question: str):
        """
        Streams tokens from Ollama's chat API.
        """
        prompt = f"""You are a helpful assistant.
        Use the context below to answer the user's question accurately.

        Context:
        {context}

        Question:
        {question}

        Answer:"""

        with requests.post(
            f"{self.base_url}/api/chat",
            json={"model": settings.LLM_MODEL, "messages": [{"role": "user", "content": prompt}]},
            stream=True
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        elif data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
                    