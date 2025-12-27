import asyncio
import json
from pathlib import Path
from typing import Callable, List, Optional, Dict, Any

from secbench.config import Config
from secbench.runners.generation import GenerationRunner


class BaseBenchmark:
    def __init__(self, config: Config, benchmark_path: Path):
        self.config = config
        self.benchmark_path = benchmark_path.resolve()
        self.generation_runner = GenerationRunner(
            api_key=config.openrouter_api_key or config.openai_api_key or "dummy",
            base_url=config.api_base_url,
        )

    async def generate_samples(
        self,
        model: str,
        prompts: List[Dict[str, Any]],
        n: int = 1,
        temperature: float = 0.8,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate samples for a list of prompts.
        prompts: List of dicts, each containing at least 'id' and 'prompt'.
        Returns: List of results with 'id', 'prompt', 'response'.
        """
        results = []
        total = len(prompts) * n
        
        def log(msg):
            if output_callback:
                output_callback(msg)
            else:
                print(msg)

        log(f"Starting generation for {len(prompts)} prompts, {n} samples each.")

        for i, item in enumerate(prompts):
            prompt_id = item.get("id", str(i))
            prompt_text = item.get("prompt")
            
            if not prompt_text:
                log(f"Skipping prompt {prompt_id}: No prompt text found.")
                continue

            for j in range(n):
                log(f"Generating sample {j+1}/{n} for prompt {prompt_id}...")
                try:
                    content = await self.generation_runner.generate_one(
                        model=model,
                        prompt=prompt_text,
                        system_prompt=self.config.system_prompt,
                        temperature=temperature
                    )
                    results.append({
                        "id": prompt_id,
                        "prompt": prompt_text,
                        "response": content,
                        "sample_index": j,
                        "model": model,
                        "metadata": item
                    })
                except Exception as e:
                    log(f"Error generating for prompt {prompt_id}: {e}")
                    results.append({
                        "id": prompt_id,
                        "error": str(e),
                        "sample_index": j
                    })
        
        return results

    def save_results(self, results: List[Dict[str, Any]], output_dir: Path):
        """Save results to JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "generation_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")

    async def run_pipeline(
        self,
        model: str,
        output_dir: Path,
        n: int = 1,
        temperature: float = 0.8,
        output_callback: Optional[Callable[[str], None]] = None,
    ):
        """
        Default pipeline: Get prompts -> Generate -> Save.
        Subclasses should override this or implement get_prompts.
        """
        prompts = self.get_prompts()
        results = await self.generate_samples(
            model, prompts, n, temperature, output_callback
        )
        self.save_results(results, output_dir)

    def get_prompts(self) -> List[Dict[str, Any]]:
        """
        Retrieve prompts for the benchmark.
        Should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_prompts")
