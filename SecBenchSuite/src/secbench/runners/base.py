import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, List, Optional


@dataclass
class RunnerResult:
    tool: str
    output: str
    exit_code: int
    success: bool


class BaseRunner(ABC):
    def __init__(self, name: str, command_template: str):
        self.name = name
        self.command_template = command_template

    async def run(self, target: str, **kwargs) -> AsyncIterator[str]:
        cmd = self.command_template.format(target=target, **kwargs)
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )

        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                yield line.decode().strip()

        await process.wait()
