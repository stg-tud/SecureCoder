import yaml
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    api_base_url: str = "http://localhost:8080/v1"
    openrouter_providers: List[str] = field(default_factory=list)
    default_model: str = "openai/gpt-4o-mini"
    system_prompt: str = (
        "You are a security-aware code assistant. Generate secure code."
    )
    output_dir: str = "results"

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        # Defaults
        config = cls()

        # Load from file
        config_path = Path(path) if path else Path("secbench.yaml")
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    data = yaml.safe_load(f) or {}

                config.openai_api_key = data.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
                config.openrouter_api_key = data.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY")
                config.api_base_url = data.get("api_base_url") or os.getenv("OPENAI_BASE_URL") or config.api_base_url
                config.openrouter_providers = cls._parse_providers(
                    data.get("openrouter_providers")
                    or os.getenv("OPENROUTER_PROVIDERS")
                    or os.getenv("OPENROUTER_PROVIDER")
                )
                config.default_model = data.get("default_model", config.default_model)
                config.system_prompt = data.get("system_prompt", config.system_prompt)
                config.output_dir = data.get("output_dir", config.output_dir)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        return config

    @staticmethod
    def _parse_providers(value) -> List[str]:
        if not value:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return [str(item).strip() for item in value if str(item).strip()]
