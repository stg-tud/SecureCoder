from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Callable
from secbench.config import Config


class Benchmark(ABC):
    def __init__(self, config: Config, benchmark_path: Path):
        self.config = config
        self.benchmark_path = benchmark_path.resolve()

    @abstractmethod
    def run_pipeline(
        self,
        model: str,
        output_dir: Path,
        n: int = 1,
        temperature: float = 0.8,
        output_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Run the benchmark pipeline.
        """
        pass
