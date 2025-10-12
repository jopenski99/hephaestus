import requests

class LLMClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def query_llm(self, context: str, question: str) -> str:
        print(f"🔎 Querying LLM with context: “{context}” and question: “{question}”")
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the context to answer accurately."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
        ]

        response = requests.post(
            self.base_url + "/api/chat",
            json={"model": "phi3:mini", "messages": messages, "stream": False}
        )

        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            return message.get("content", "No response from model.")
        else:
            return f"Error from LLM API: {response.text}"
