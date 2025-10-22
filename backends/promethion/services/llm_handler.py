from promethion.services.prompt_manager import PromptManager
from promethion.services.llm_client import LLMClient

class LLMHandler:
    def __init__(self, model: str, port: str = None, api_key: str = None, base_url: str = None):
        self.llm_config = {"model": model, "port": port, "api_key": api_key, "base_url": base_url}
        print("=" * 60)
        print("LLM Config: " + str(self.llm_config))
    def handleLLM(self, text: str, type:str, context: str = None,variant: str = "default") -> str:
        # Construct a prompt instructing classification into your categories
        pm = PromptManager()
        llm = LLMClient(self.llm_config)
        
        prompt = ""
        print("=" * 60)
        print("Variant: " + variant)
        #print("localhost" in self.llm_config["base_url"] or "127.0.0.1" in self.llm_config["base_url"])
        if "localhost" in self.llm_config["base_url"] or "127.0.0.1" in self.llm_config["base_url"]:
            prompt = pm.format_prompt(type, text,context=context,variant=variant)
        else:
            prompt = pm.format_open_router_prompt(name=type,message=text,context=context,variant=variant)
        

        response = llm.query_llm(prompt)
        return response
