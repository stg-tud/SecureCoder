import docker
import sys
import time
import os


def run_and_monitor():
    # 1. Initialize the Docker client
    # This connects to your local Docker daemon (usually /var/run/docker.sock)
    try:
        client = docker.from_env()
        client.ping()  # Explicitly check connectivity
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

    print("--- 1. Pulling image (python:3.9-slim)... ---")
    image_name = "python:3.9-slim"
    try:
        client.images.pull(image_name)
    except Exception as e:
        print(f"Error pulling image: {e}")
        return

    # 2. Define the payload
    # This is a simple python script we will inject into the container.
    # CRITICAL: We use 'python -u'. The '-u' flag forces unbuffered binary stdout/stderr.
    # Without this, you won't see the logs 'live'; they would appear all at once at the end.
    container_command = (
        "python -u -c'"
        "import time;"
        'print("Container: Process started...")\n'
        "for i in range(1, 6):\n"
        '   print(f"Container: Working on task {i}/5...")\n'
        "   time.sleep(1)\n"
        'print("Container: Process finished!")\''
    )

    print("--- 2. Starting Container ---")

    # detach=True: Starts the container in the background and returns the object immediately.
    container = client.containers.run(
        image_name,
        command=container_command,
        detach=True,
        auto_remove=False,  # We keep it briefly to inspect, then remove manually
    )

    print(f"Host: Container ID {container.short_id} is running.")
    print("--- 3. Live Log Streaming ---")

    try:
        # 3. Stream the logs
        # stream=True: Returns a generator instead of a string
        # follow=True: Keeps the connection open until the container stops
        log_generator = container.logs(
            stream=True, follow=True, stdout=True, stderr=True
        )

        for log_chunk in log_generator:
            # Docker logs return bytes, so we must decode them.
            # We use sys.stdout.write to mimic exact terminal behavior
            decoded_line = log_chunk.decode("utf-8")

            # Print with a prefix so you know it's coming from the container
            sys.stdout.write(f"[LIVE STREAM] {decoded_line}")
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nHost: User interrupted monitoring.")
    finally:
        # 4. Cleanup
        print("\n--- 4. Cleanup ---")
        print(f"Host: Stopping and removing container {container.short_id}...")
        container.stop()
        container.remove()
        print("Host: Done.")


if __name__ == "__main__":
    run_and_monitor()
