# import asyncio
# import logging
# import os
# import shutil
# import sys
# from pathlib import Path
# from typing import Dict, Optional, Callable

# logger = logging.getLogger(__name__)


# class LocalRunner:
#     """
#     A runner that executes commands locally in a virtual environment.
#     """

#     def __init__(
#         self, venv_path: Optional[Path] = None, python_interpreter: str = sys.executable
#     ):
#         self.venv_path = venv_path or Path(".venv")
#         self.python_interpreter = python_interpreter
#         self.workdir: Optional[Path] = None
#         self.env: Dict[str, str] = {}

#     async def _ensure_venv(self):
#         if not self.venv_path.exists():
#             logger.info(
#                 f"Creating virtual environment at {self.venv_path} using {self.python_interpreter}"
#             )
#             proc = await asyncio.create_subprocess_exec(
#                 self.python_interpreter,
#                 "-m",
#                 "venv",
#                 str(self.venv_path),
#                 stdout=asyncio.subprocess.PIPE,
#                 stderr=asyncio.subprocess.PIPE,
#             )
#             await proc.wait()

#             # Upgrade pip
#             pip_executable = self.venv_path / "bin" / "pip"
#             proc = await asyncio.create_subprocess_exec(
#                 str(pip_executable),
#                 "install",
#                 "--upgrade",
#                 "pip",
#                 stdout=asyncio.subprocess.PIPE,
#                 stderr=asyncio.subprocess.PIPE,
#             )
#             await proc.wait()

#     async def run_ephemeral(
#         self,
#         command: str,
#         volumes: Dict[str, str] = {},
#         env: Dict[str, str] = {},
#         workdir: Optional[str] = None,
#         network: str = "host",
#         remove: bool = True,
#         output_callback: Optional[Callable[[str], None]] = None,
#     ) -> int:
#         """
#         Run a command locally.
#         """
#         # Setup venv if needed (though ephemeral usually implies quick run, we might need venv)
#         await self._ensure_venv()

#         # Determine workdir
#         local_workdir = self._resolve_workdir(workdir, volumes)

#         # Prepare env
#         run_env = self._prepare_env(env)

#         logger.info(f"Running local command: {command}")

#         process = await asyncio.create_subprocess_shell(
#             command,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.STDOUT,
#             cwd=local_workdir,
#             env=run_env,
#             executable="/bin/zsh",
#         )

#         if process.stdout:
#             async for line in process.stdout:
#                 decoded = line.decode().strip()
#                 if output_callback:
#                     output_callback(f"[local] {decoded}")
#                 else:
#                     print(f"[local] {decoded}")

#         exit_code = await process.wait()

#         if remove:
#             await self.remove("ephemeral")

#         return exit_code

#     async def run_detached(
#         self,
#         name: str,
#         volumes: Dict[str, str] = {},
#         env: Dict[str, str] = {},
#         workdir: Optional[str] = None,
#         entrypoint: Optional[str] = None,
#     ) -> str:
#         """
#         Prepare the local environment.
#         """
#         await self._ensure_venv()

#         # Store context for subsequent exec_command calls
#         self.env = env.copy()
#         self.workdir = self._resolve_workdir(workdir, volumes)

#         return name

#     async def exec_command(
#         self,
#         command: str,
#         output_callback: Optional[Callable[[str], None]] = None,
#     ) -> int:
#         """
#         Execute a command in the virtual environment.
#         """
#         run_env = self._prepare_env(self.env)

#         logger.info(f"Running local command: {command} in {self.workdir}")

#         # Explicitly activate venv to ensure environment is correct
#         activate_script = self.venv_path.resolve() / "bin" / "activate"
#         wrapped_command = f"source {activate_script} && {command}"

#         process = await asyncio.create_subprocess_shell(
#             wrapped_command,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.STDOUT,
#             cwd=self.workdir,
#             env=run_env,
#             executable="/bin/zsh",
#         )

#         if process.stdout:
#             async for line in process.stdout:
#                 decoded = line.decode().strip()
#                 if output_callback:
#                     output_callback(f"[local] {decoded}")
#                 else:
#                     print(f"[local] {decoded}")

#         return await process.wait()

#     async def stop(self):
#         # No-op for local runner as we don't have a long-running container process
#         pass

#     async def remove(self, force: bool = True):
#         """
#         Clean up the virtual environment.
#         """
#         if self.venv_path.exists():
#             logger.info(f"Removing virtual environment at {self.venv_path}")
#             shutil.rmtree(self.venv_path)

#     async def stream_logs(
#         self,
#         output_callback: Callable[[str], None],
#     ):
#         pass

#     def _resolve_workdir(
#         self, workdir: Optional[str], volumes: Dict[str, str]
#     ) -> Optional[Path]:
#         if not workdir:
#             return None

#         # Try to map container path to host path via volumes
#         for host, container in volumes.items():
#             if workdir.startswith(container):
#                 rel = os.path.relpath(workdir, container)
#                 if rel == ".":
#                     return Path(host)
#                 return Path(host) / rel

#         # If no mapping found, assume it's a local path or relative
#         return Path(workdir)

#     def _prepare_env(self, env: Dict[str, str]) -> Dict[str, str]:
#         run_env = os.environ.copy()
#         run_env.update(env)

#         venv_bin = self.venv_path / "bin"
#         run_env["PATH"] = f"{venv_bin}:{run_env.get('PATH', '')}"
#         run_env["VIRTUAL_ENV"] = str(self.venv_path)

#         return run_env


class LocalRunner:
    pass
