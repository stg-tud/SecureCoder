import docker
import os
import sys
from typing import Dict, Optional, Generator, Any


class DockerRunner:
    def __init__(self):
        self.client = self._get_docker_client()

    def _get_docker_client(self) -> docker.DockerClient:
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
                    raise RuntimeError(
                        f"Error: Could not connect to Docker even with user socket.\nDetails: {e}"
                    )
            else:
                raise RuntimeError(
                    f"Error: Could not connect to Docker. Is the Docker daemon running?\nDetails: {e}"
                )

    def pull_image(self, image_name: str, output_callback: Optional[callable] = None):
        if output_callback:
            output_callback(f"Pulling image {image_name}...")
        try:
            self.client.images.pull(image_name)
            if output_callback:
                output_callback(f"Successfully pulled {image_name}")
        except Exception as e:
            raise RuntimeError(f"Error pulling image {image_name}: {e}")

    def run(
        self,
        image: str,
        command: str,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        network_mode: str = "bridge",
        output_callback: Optional[callable] = None,
    ):
        """
        Runs a container and streams logs synchronously.
        """
        container = None
        try:
            if output_callback:
                output_callback(f"Starting container from {image}...")

            container = self.client.containers.run(
                image,
                command=command,
                detach=True,
                auto_remove=True,
                environment=environment,
                volumes=volumes,
                network_mode=network_mode,
            )

            if output_callback:
                output_callback(f"Container ID {container.short_id} started.")

            # Stream logs
            log_generator = container.logs(
                stream=True, follow=True, stdout=True, stderr=True
            )

            for log_chunk in log_generator:
                decoded_line = log_chunk.decode("utf-8", errors="replace")
                if output_callback:
                    output_callback(decoded_line.rstrip())
                else:
                    print(decoded_line.rstrip())

            # Wait for container to finish and get exit code
            result = container.wait()
            exit_code = result.get("StatusCode", 0)

            if exit_code != 0:
                raise RuntimeError(
                    f"Container exited with non-zero status code: {exit_code}"
                )

        except KeyboardInterrupt:
            if output_callback:
                output_callback("\nUser interrupted execution.")
            raise
        except Exception as e:
            if output_callback:
                output_callback(f"\nAn error occurred: {e}")
            raise
        finally:
            if container:
                if output_callback:
                    output_callback(
                        f"Stopping and removing container {container.short_id}..."
                    )
                try:
                    container.stop()
                except Exception as e:
                    if output_callback:
                        output_callback(f"Error during cleanup: {e}")
