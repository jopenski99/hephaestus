import requests
import json
from promethion.api.core.config import settings
class LLMClient:
    def __init__(self, config: dict):
        print(config["port"] is not "")
        if config["port"] is not "":
            self.base_url = f"{config['base_url']}:{config['port']}"
        else:
            self.base_url = config['base_url']
            
        self.api_key = config["api_key"]
        self.model = config['model']
        
        if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
            self.base_url = f"{self.base_url}/api/chat"
            self.headers = {
                "Content-Type": "application/json"
            }
        else:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",   
                "X-Title": "HephaestusAI"             
            }
        #print({key: value for key, value in self.__dict__.items()})

    def query_llm(self, prompt) -> str:
        """Send a classification or text prompt to the LLM via OpenRouter."""

        payload_obj = {
            **prompt,
            "stream": False,
            "model": self.model
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(payload_obj)  # OpenRouter requires raw JSON
            )

            # Debugging logs
            #print("🔹 Payload Sent:", json.dumps(payload_obj, indent=2))
            #print("🔹 Status Code:", response.status_code)

            if response.status_code == 200:
                data = response.json()
                #print("🔹 Raw Response:", json.dumps(data, indent=2))

                # ✅ Extract assistant message properly
                return data["choices"][0]["message"]["content"].strip()
            else:
                #print("❌ API Error:", response.text)
                return f"Error from LLM API ({response.status_code}): {response.text}"

        except Exception as e:
            print(f"⚠️ Exception while querying LLM: {e}")
            return "Error: Unable to connect to LLM service."
    
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
                    