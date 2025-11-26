import asyncio
import logging
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable

logger = logging.getLogger(__name__)


class DockerRunner:
    """
    A wrapper around the Docker CLI to run containers and execute commands.
    """

    def __init__(self, image: str):
        self.image = image

    async def run_ephemeral(
        self,
        command: str,
        volumes: Dict[str, str] = {},
        env: Dict[str, str] = {},
        workdir: Optional[str] = None,
        network: str = "host",
        remove: bool = True,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        """
        Run a command in a new container and exit.
        Equivalent to `docker run --rm ...`
        """
        cmd_parts = ["docker", "run"]
        if remove:
            cmd_parts.append("--rm")

        cmd_parts.extend(["--net", network])

        for host_path, container_path in volumes.items():
            cmd_parts.extend(["-v", f"{host_path}:{container_path}"])

        for key, value in env.items():
            if value:
                cmd_parts.extend(["-e", f"{key}={value}"])

        if workdir:
            cmd_parts.extend(["-w", workdir])

        cmd_parts.append(self.image)
        cmd_parts.extend(shlex.split(command))

        logger.info(f"Running docker command: {' '.join(cmd_parts)}")

        process = await asyncio.create_subprocess_exec(
            *cmd_parts, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )

        if process.stdout:
            async for line in process.stdout:
                decoded = line.decode().strip()
                if output_callback:
                    output_callback(f"[docker] {decoded}")
                else:
                    print(f"[docker] {decoded}")

        return await process.wait()

    async def run_detached(
        self,
        name: str,
        volumes: Dict[str, str] = {},
        env: Dict[str, str] = {},
        workdir: Optional[str] = None,
        entrypoint: Optional[str] = None,
    ) -> str:
        """
        Start a detached container. Returns the container ID/name.
        """
        cmd_parts = ["docker", "run", "-d", "--name", name, "--rm"]

        for host_path, container_path in volumes.items():
            cmd_parts.extend(["-v", f"{host_path}:{container_path}"])

        for key, value in env.items():
            if value:
                cmd_parts.extend(["-e", f"{key}={value}"])

        if workdir:
            cmd_parts.extend(["-w", workdir])

        if entrypoint:
            cmd_parts.extend(["--entrypoint", entrypoint])

        cmd_parts.extend([self.image, "tail", "-f", "/dev/null"])  # Keep alive

        process = await asyncio.create_subprocess_exec(
            *cmd_parts, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Failed to start container: {stderr.decode()}")

        return name

    async def exec_command(
        self,
        container: str,
        command: str,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        """
        Execute a command in a running container.
        """
        cmd_parts = ["docker", "exec", container]
        cmd_parts.extend(shlex.split(command))

        process = await asyncio.create_subprocess_exec(
            *cmd_parts, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )

        if process.stdout:
            async for line in process.stdout:
                decoded = line.decode().strip()
                if output_callback:
                    output_callback(f"[{container}] {decoded}")
                else:
                    print(f"[{container}] {decoded}")

        return await process.wait()

    async def stop(self, container: str):
        """Stop a running container."""
        process = await asyncio.create_subprocess_exec(
            "docker",
            "stop",
            container,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.wait()

    async def stream_logs(
        self,
        container: str,
        output_callback: Callable[[str], None],
    ):
        """
        Stream logs from a container using `docker logs -f`.
        """
        process = await asyncio.create_subprocess_exec(
            "docker",
            "logs",
            "-f",
            container,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        if process.stdout:
            async for line in process.stdout:
                decoded = line.decode().strip()
                output_callback(f"[{container}] {decoded}")

        await process.wait()

    async def remove(self, container: str, force: bool = True):
        """Remove a container."""
        cmd = ["docker", "rm"]
        if force:
            cmd.append("-f")
        cmd.append(container)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.wait()
