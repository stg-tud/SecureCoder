import os
import asyncio
from typing import AsyncIterator, List
from openai import AsyncOpenAI


class GenerationRunner:
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    async def generate(
        self, model: str, prompt: str, count: int = 1
    ) -> AsyncIterator[str]:
        """Generate samples from a model."""
        yield f"Generating {count} samples with {model}..."

        try:
            # In a real scenario, we might want to run these in parallel
            for i in range(count):
                yield f"Requesting sample {i+1}/{count}..."
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.choices[0].message.content
                yield f"Sample {i+1} generated ({len(content)} chars)"
                # Here we would save the content to a file/struct

        except Exception as e:
            yield f"Error during generation: {str(e)}"
