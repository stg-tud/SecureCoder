import asyncio
import logging
from pathlib import Path
from secbench.runners.local_runner import LocalRunner

logging.basicConfig(level=logging.INFO)


async def test_local_runner():
    print("Testing LocalRunner...")

    # Use a temporary venv for testing
    venv_path = Path(".test_venv")
    runner = LocalRunner(venv_path=venv_path)

    try:
        # 1. Setup
        print("\n1. Setting up environment...")
        await runner.run_detached(name="test_run", workdir=".")

        # 2. Check python version
        print("\n2. Checking Python version...")
        await runner.exec_command(command="python --version")

        # 3. Install a package
        print("\n3. Installing 'requests'...")
        await runner.exec_command(command="pip install pillow")

        # 4. Verify installation
        print("\n4. Verifying installation...")
        await runner.exec_command(
            command="python -c 'import PIL; print(PIL.__version__)'"
        )

        # 5. Check environment variables
        print("\n5. Checking environment variables...")
        await runner.exec_command(command="env | grep VIRTUAL_ENV")

        print("\nLocalRunner test passed!")

    finally:
        # Cleanup
        print("\nCleaning up...")
        await runner.remove()


if __name__ == "__main__":
    asyncio.run(test_local_runner())
