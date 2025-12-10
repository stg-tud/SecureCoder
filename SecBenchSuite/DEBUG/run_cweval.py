import docker
import sys
import time
import os
import platform


def run_and_monitor():
    # 1. Initialize the Docker client
    try:
        client = docker.from_env()
        client.ping()
    except docker.errors.DockerException as e:
        # Fallback: Check for macOS user-level socket if default fails
        user_socket = os.path.expanduser("~/.docker/run/docker.sock")
        if os.path.exists(user_socket):
            print(f"Default socket failed. Trying user socket: {user_socket}")
            try:
                client = docker.DockerClient(base_url=f"unix://{user_socket}")
                client.ping()
            except docker.errors.DockerException:
                print(f"Error: Could not connect to Docker.\nDetails: {e}")
                return
        else:
            print(
                f"Error: Could not connect to Docker. Is the Docker daemon running?\nDetails: {e}"
            )
            return

    image_name = "co1lin/cweval"
    print(f"--- 1. Pulling image ({image_name})... ---")
    try:
        client.images.pull(image_name)
    except Exception as e:
        print(f"Error pulling image: {e}")
        return

    # 2. Define the payload
    # Running the sanity checks from the README:
    # 1. source .env
    # 2. python cweval/commons.py compile_all_in --path benchmark/
    # 3. pytest benchmark/ -x -n 4
    # We use zsh because the README uses it.
    # Determine if we are on an ARM-based host (e.g. Apple Silicon)
    is_arm = platform.machine().lower() in ("arm64", "aarch64")
    cgo_env = "CGO_ENABLED=0 " if is_arm else ""

    container_command = (
        'zsh -l -c "source ~/miniforge3/bin/activate && '
        "cd /home/ubuntu/CWEval && "
        "source .env && "
        "echo '[Container] Tidy Go modules...' && "
        "go mod tidy && "
        "echo '[Container] Compiling reference solutions...' && "
        f"{cgo_env}python -u cweval/commons.py compile_all_in --path benchmark/ && "
        "echo '[Container] Running tests...' && "
        'pytest benchmark/ -x -n 4"'
    )

    print("--- 2. Starting Container ---")

    try:
        # detach=True: Starts the container in the background and returns the object immediately.
        container = client.containers.run(
            image_name,
            command=container_command,
            detach=True,
            auto_remove=False,
        )

        print(f"Host: Container ID {container.short_id} is running.")
        print("--- 3. Live Log Streaming ---")

        # 3. Stream the logs
        log_generator = container.logs(
            stream=True, follow=True, stdout=True, stderr=True
        )

        for log_chunk in log_generator:
            # Docker logs return bytes, so we must decode them.
            decoded_line = log_chunk.decode("utf-8", errors="replace")

            # Print with a prefix so you know it's coming from the container
            sys.stdout.write(f"[LIVE STREAM] {decoded_line}")
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nHost: User interrupted monitoring.")
    except Exception as e:
        print(f"\nHost: An error occurred: {e}")
    finally:
        # 4. Cleanup
        if "container" in locals():
            print("\n--- 4. Cleanup ---")
            print(f"Host: Stopping and removing container {container.short_id}...")
            try:
                container.stop()
                container.remove()
            except Exception as e:
                print(f"Error during cleanup: {e}")
            print("Host: Done.")


if __name__ == "__main__":
    run_and_monitor()
