import docker
import os
import sys
import asyncio
import platform
from typing import AsyncIterator, Optional
from secbench.runners.base import BaseRunner


class DockerRunner(BaseRunner):
    def __init__(self, image_name: str = "co1lin/cweval"):
        super().__init__("docker", "")
        self.image_name = image_name
        self.client = self._init_client()

    def _init_client(self) -> Optional[docker.DockerClient]:
        try:
            client = docker.from_env()
            client.ping()
            return client
        except docker.errors.DockerException as e:
            # Fallback: Check for macOS user-level socket if default fails
            user_socket = os.path.expanduser("~/.docker/run/docker.sock")
            if os.path.exists(user_socket):
                try:
                    client = docker.DockerClient(base_url=f"unix://{user_socket}")
                    client.ping()
                    return client
                except docker.errors.DockerException:
                    pass

            # If we are here, we failed to connect
            # We will raise this later when run is called if client is None
            return None

    async def pull_image(self) -> AsyncIterator[str]:
        if not self.client:
            yield "Error: Docker client not initialized. Is Docker running?"
            return

        try:
            yield f"Pulling image {self.image_name}..."
            # Run blocking pull in executor
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self.client.images.pull, self.image_name)
            yield f"Successfully pulled {self.image_name}"
        except Exception as e:
            yield f"Error pulling image: {e}"

    async def run(self, target: str, **kwargs) -> AsyncIterator[str]:
        if not self.client:
            yield "Error: Docker client not initialized. Is Docker running?"
            return

        # Determine if we are on an ARM-based host (e.g. Apple Silicon)
        # This might be needed for environment variables inside the container
        is_arm = platform.machine().lower() in ("arm64", "aarch64")

        # Prepare environment variables if passed
        environment = kwargs.get("environment", {})

        # Prepare volumes if passed
        volumes = kwargs.get("volumes", {})

        container = None
        try:
            # Run container
            # We use detach=True to get the container object and stream logs
            container = self.client.containers.run(
                self.image_name,
                command=target,
                detach=True,
                auto_remove=False,  # We remove it manually to ensure we get all logs
                environment=environment,
                volumes=volumes,
                network_mode="host",  # Recommended in README
            )

            yield f"Container started: {container.short_id}"

            # Stream logs
            # container.logs(stream=True) returns a blocking generator.
            # We need to iterate it without blocking the event loop.
            # Since we can't easily await the generator yield, we might need to run the whole log consumption in a thread
            # and put lines into a queue, or just iterate and accept it blocks the loop briefly for each chunk.
            # Given this is a CLI tool, blocking the loop briefly might be acceptable, but for long running tasks it's bad.
            # However, `docker-py` logs stream is blocking.

            # Better approach for async generator from blocking generator:
            queue = asyncio.Queue()
            loop = asyncio.get_running_loop()

            def log_reader():
                try:
                    for line in container.logs(
                        stream=True, follow=True, stdout=True, stderr=True
                    ):
                        loop.call_soon_threadsafe(queue.put_nowait, line)
                    loop.call_soon_threadsafe(queue.put_nowait, None)  # Sentinel
                except Exception as e:
                    loop.call_soon_threadsafe(queue.put_nowait, e)

            # Start log reader in a separate thread
            import threading

            thread = threading.Thread(target=log_reader)
            thread.start()

            while True:
                line = await queue.get()
                if line is None:
                    break
                if isinstance(line, Exception):
                    yield f"Error reading logs: {line}"
                    break
                # Decode bytes
                decoded_line = line.decode("utf-8", errors="replace")
                yield decoded_line

            thread.join()

            # Wait for container to finish and get exit code
            result = container.wait()
            exit_code = result.get("StatusCode", 0)

            if exit_code != 0:
                yield f"Container exited with code {exit_code}"

        except Exception as e:
            yield f"Error running container: {e}"
        finally:
            if container:
                try:
                    container.stop()
                    container.remove()
                except Exception:
                    pass
