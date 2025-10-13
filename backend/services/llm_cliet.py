import requests
import json
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
    def stream_llm(self, context: str, question: str):
        """
        Streams response tokens from Ollama as they are generated.
        """
        prompt = f"""You are a helpful assistant.
            Use the context below to answer accurately.
            
            Context:
            {context}
            
            Question:
            {question}
            
            Answer:"""
          
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": "phi3:mini", "prompt": prompt, "stream": True},
            stream=True,
        )

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "message" in data and "content" in data["message"]:
                    yield data["message"]["content"]
                if data.get("done"):
                    break