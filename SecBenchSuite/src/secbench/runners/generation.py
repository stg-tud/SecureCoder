import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, List
from openai import AsyncOpenAI


class GenerationRunner:
    def __init__(
        self, api_key: str = "dummy", base_url: str = "http://localhost:8080/v1"
    ):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    async def generate_one(
        self,
        model: str,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.8,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

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
                content = await self.generate_one(model, prompt, system_prompt)

                msg = f"Sample {i+1} generated ({len(content)} chars)"
                if output_dir:
                    path = self.save_sample(content, model, i + 1, output_dir)
                    msg += f" -> {path}"

                yield msg

        except Exception as e:
            yield f"Error during generation: {str(e)}"
