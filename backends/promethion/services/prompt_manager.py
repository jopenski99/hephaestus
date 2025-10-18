# backend/services/prompt_manager.py
import yaml
from pathlib import Path
from promethion.api.core.config import settings
from promethion.services.rag_query import RAGQueryEngine

class PromptManager:
    def __init__(self):
        self.base_dir = Path(settings.PROMTPS_DIR)

    def load_prompt(self, name: str, variant: str = "default") -> str:
        file_path = self.base_dir / f"{name}.yml"
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        #print(f"Loading prompt from: {file_path}")
        data = yaml.safe_load(file_path.read_text())
        return data.get(variant, {}) #.get("template", "")

    def format_prompt(self, name: str, message: str, variant: str = "default") -> str:
        template = self.load_prompt(name, variant)
        if(variant == "default"):
            return template.format(message=message)
        else :
            rqe = RAGQueryEngine()
            context = rqe.query(message, n_results=5)
            return template.format(context=context, message=message)

    def format_open_router_prompt(self, name: str, message: str, variant: str = "default") -> str:
        prompt_data = self.load_prompt(name,variant)
        system_prompt = prompt_data["system"]
        user_prompt = prompt_data["user"].format(messages=message)
        payload = {

            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3
        }

        return payload
