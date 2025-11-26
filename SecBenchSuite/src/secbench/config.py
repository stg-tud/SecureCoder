import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class Config:
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    default_model: str = "openai/gpt-3.5-turbo"
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

                config.openai_api_key = data.get("openai_api_key")
                config.openrouter_api_key = data.get("openrouter_api_key")
                config.default_model = data.get("default_model", config.default_model)
                config.output_dir = data.get("output_dir", config.output_dir)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        return config
