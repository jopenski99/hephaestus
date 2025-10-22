import pytz
import yaml
from pathlib import Path
from datetime import datetime
from promethion.api.core.config import settings
from promethion.services.rag_query import RAGQueryEngine


class PromptManager:
    def __init__(self):
        self.base_dir = Path(settings.PROMTPS_DIR)

    # -----------------------------------------------------------
    # Load YAML prompt file
    # -----------------------------------------------------------
    def load_prompt(self, name: str) -> dict:
        file_path = self.base_dir / f"{name}.yml"
        print("=" * 60)
        print(f"📄 Loading prompt from: {file_path}")
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        return data or {}

    # -----------------------------------------------------------
    # Format prompt for local/Ollama models
    # -----------------------------------------------------------
    def format_prompt(
        self,
        name: str,
        message: str,
        variant: str = "default",
        context: str = None
    ) -> str:
        timezone = pytz.timezone("Asia/Manila")
        current_datetime = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

        data = self.load_prompt(name)
        variant_data = data.get(variant)
        if not variant_data:
            raise ValueError(f"❌ Variant '{variant}' not found in {name}.yml")

        # Default template for local/Ollama models
        template = variant_data.get("template", "")
        if not template:
            raise ValueError(f"❌ Missing 'template' field under '{variant}' in {name}.yml")

        # Inject context (from RAG if needed)
        if not context:
            rqe = RAGQueryEngine()
            context = rqe.query(message, n_results=5)

        return template.format(
            message=message,
            context=context or "",
            timezone=timezone,
            current_datetime=current_datetime
        )

    # -----------------------------------------------------------
    # Format prompt for OpenRouter or API-based models
    # -----------------------------------------------------------
    def format_open_router_prompt(
        self,
        name: str,
        message: str,
        variant: str = "open-router",
        context: str = None
    ) -> dict:
        timezone = pytz.timezone("Asia/Manila")
        current_datetime = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

        data = self.load_prompt(name)
        variant_data = data.get(variant)
        print("=" * 60)
        print(variant)
        print("=" * 60)
        #print(variant_data)
        if not variant_data:
            raise ValueError(f"❌ Variant '{variant}' not found in {name}.yml")

        system_prompt = variant_data.get("system", "")
        user_prompt = variant_data.get("user", "")
        print("=" * 60)
        print(system_prompt, user_prompt)
        if not system_prompt or not user_prompt:
            raise ValueError(f"❌ Both 'system' and 'user' fields are required in '{variant}' section of {name}.yml")

        # Fill in placeholders
        system_prompt = system_prompt.format(
            message=message,
            context=context or "",
            timezone=timezone,
            current_datetime=current_datetime
        )

        user_prompt = user_prompt.format(
            message=message,
            context=context or "",
            timezone=timezone,
            current_datetime=current_datetime
        )

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": data.get("default", {}).get("config", {}).get("temperature", 0.3),
        }

        print("=" * 60)
        print("🧠 OpenRouter Payload Generated:")
        #print(payload)

        return payload
