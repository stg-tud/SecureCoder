import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional
import httpx


class GenerationRunner:
    def __init__(
        self,
        api_key: str = "dummy",
        base_url: str = "http://localhost:8080/v1",
        provider_order: Optional[List[str]] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.provider_order = provider_order or []

    async def generate_one(
        self,
        model: str,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.8,
    ) -> str:
        result = await self.generate_one_with_metadata(
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )
        return result["content"]

    async def generate_one_with_metadata(
        self,
        model: str,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.8,
    ) -> Dict[str, object]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        extra_body = self._provider_extra_body()
        if extra_body:
            payload.update(extra_body)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
        response.raise_for_status()
        body = response.json()
        choices = body.get("choices") or []
        if not choices:
            raise RuntimeError("No choices returned from chat completion API")
        content = choices[0].get("message", {}).get("content")
        usage = body.get("usage") or {}
        return {
            "content": content,
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "estimated_cost": usage.get("estimated_cost"),
            },
        }

    def _provider_extra_body(self):
        if not self.provider_order:
            return None
        return {
            "provider": {
                "only": self.provider_order,
                "order": self.provider_order,
                "allow_fallbacks": len(self.provider_order) > 1,
            }
        }

    def save_sample(
        self, content: str, model: str, index: int, output_dir: Path
    ) -> str:
        """Save the generated sample to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_model = model.replace("/", "_").replace(":", "_")
        filename = f"sample_{timestamp}_{sanitized_model}_{index}.txt"
        file_path = output_dir / filename

        with open(file_path, "w") as f:
            f.write(content)
        return str(file_path)

    async def generate(
        self,
        model: str,
        prompt: str,
        count: int = 1,
        system_prompt: str = None,
        output_dir: Path = None,
    ) -> AsyncIterator[str]:
        """Generate samples from a model."""
        yield f"Generating {count} samples with {model}..."

        try:
            # In a real scenario, we might want to run these in parallel
            for i in range(count):
                yield f"Requesting sample {i+1}/{count}..."
                result = await self.generate_one_with_metadata(model, prompt, system_prompt)
                content = result["content"]

                msg = f"Sample {i+1} generated ({len(content)} chars)"
                if output_dir:
                    path = self.save_sample(content, model, i + 1, output_dir)
                    msg += f" -> {path}"

                yield msg

        except Exception as e:
            yield f"Error during generation: {str(e)}"
