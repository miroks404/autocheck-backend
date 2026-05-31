import shutil
import subprocess
from pathlib import Path

from app.core.config import get_settings


def _docker_command_available() -> str | None:
    return shutil.which("docker")


def docker_workspace_mount_args(workspace_path: str) -> list[str]:
    """Build docker volume/workdir args for checker workspace paths."""
    settings = get_settings()
    workspace = Path(workspace_path).resolve()
    storage_root = Path(settings.checker_storage_mount).resolve()
    try:
        relative = workspace.relative_to(storage_root)
    except ValueError:
        return ["-v", f"{workspace}:{workspace}", "-w", str(workspace)]
    return [
        "-v",
        f"{settings.checker_storage_volume}:/storage",
        "-w",
        f"/storage/{relative.as_posix()}",
    ]


def run_in_isolated_container(
    command: str,
    workspace_path: str | None = None,
    timeout_sec: int = 180,
    image: str = "python:3.12-alpine",
) -> dict:
    """
    Runs a command inside an isolated ephemeral container.
    """
    docker_bin = _docker_command_available()
    if not docker_bin:
        return {
            "ok": False,
            "timed_out": False,
            "isolated": False,
            "return_code": 127,
            "output": "docker binary not available",
        }
    cmd = [docker_bin, "run", "--rm", "--network=none"]
    if workspace_path:
        cmd += docker_workspace_mount_args(workspace_path)
    cmd += [image, "sh", "-lc", command]
    try:
        proc = subprocess.run(
            cmd,
            timeout=timeout_sec,
            capture_output=True,
            text=True,
            check=False,
        )
        output = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
        return {
            "ok": proc.returncode == 0,
            "timed_out": False,
            "isolated": True,
            "return_code": proc.returncode,
            "output": output.strip(),
        }
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + ("\n" if exc.stdout and exc.stderr else "") + (exc.stderr or "")
        return {
            "ok": False,
            "timed_out": True,
            "isolated": True,
            "return_code": 124,
            "output": output.strip() or "timeout exceeded",
        }


def run_local_command(command: str, workspace_path: str, timeout_sec: int = 180) -> dict:
    try:
        proc = subprocess.run(
            ["sh", "-lc", command],
            cwd=workspace_path,
            timeout=timeout_sec,
            capture_output=True,
            text=True,
            check=False,
        )
        output = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
        return {
            "ok": proc.returncode == 0,
            "timed_out": False,
            "isolated": False,
            "return_code": proc.returncode,
            "output": output.strip(),
        }
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + ("\n" if exc.stdout and exc.stderr else "") + (exc.stderr or "")
        return {
            "ok": False,
            "timed_out": True,
            "isolated": False,
            "return_code": 124,
            "output": output.strip() or "timeout exceeded",
        }


def run_checker_command(
    command: str,
    workspace_path: str,
    timeout_sec: int = 180,
    image: str = "python:3.12-alpine",
) -> dict:
    result = run_in_isolated_container(command=command, workspace_path=workspace_path, timeout_sec=timeout_sec, image=image)
    # Requirement: candidate code must not run in the main application container.
    if not result["isolated"]:
        return {
            "ok": False,
            "timed_out": False,
            "isolated": False,
            "return_code": 127,
            "output": "docker isolation is required but unavailable",
        }
    return result
