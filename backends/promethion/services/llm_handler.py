from promethion.services.prompt_manager import PromptManager
from promethion.services.llm_client import LLMClient

class LLMHandler:
    def __init__(self, model: str, port: str = None, api_key: str = None, base_url: str = None):
        self.llm_config = {"model": model, "port": port, "api_key": api_key, "base_url": base_url}
        
    def handleLLM(self, text: str) -> str:
        # Construct a prompt instructing classification into your categories
        pm = PromptManager()
        llm = LLMClient(self.llm_config)
        if"localhost" in self.llm_config["base_url"] or "127.0.0.1" in self.llm_config["base_url"]:
            prompt = pm.format_prompt("classification", text)
        else:
            prompt = pm.format_open_router_prompt("classification",text)
        response = llm.query_llm(prompt)
        return response
