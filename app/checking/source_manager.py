import os
import shutil
import subprocess
import zipfile
from pathlib import Path

from app.models import Submission

BASE_STORAGE = Path("/app/storage/submissions")


def submission_workspace(submission_id: int) -> Path:
    return BASE_STORAGE / str(submission_id) / "workspace"


def prepare_submission_workspace(submission: Submission) -> Path:
    workspace = submission_workspace(submission.id)
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    if submission.source_type == "git":
        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", submission.source_value, str(workspace)],
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
        if clone_result.returncode != 0:
            raise RuntimeError((clone_result.stderr or clone_result.stdout).strip() or "Failed to clone repository")
        return workspace

    zip_path = Path(submission.source_value).expanduser().resolve()
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(workspace)
    return normalize_workspace_root(workspace)


def normalize_workspace_root(workspace: Path) -> Path:
    items = [p for p in workspace.iterdir() if p.name != "__MACOSX"]
    if len(items) == 1 and items[0].is_dir():
        nested = items[0]
        temp_dir = workspace.parent / "workspace_normalized"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        shutil.move(str(nested), str(temp_dir))
        shutil.rmtree(workspace)
        shutil.move(str(temp_dir), str(workspace))
    return workspace


def collect_source_snippets(workspace: Path, max_files: int = 10, max_lines: int = 200) -> list[dict]:
    allowed_ext = {".py", ".kt", ".kts", ".swift", ".java", ".js", ".ts", ".tsx", ".jsx", ".dart", ".go", ".rb"}
    snippets: list[dict] = []
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "build", "dist", ".idea", ".gradle"}]
        for filename in files:
            path = Path(root) / filename
            if path.suffix.lower() not in allowed_ext:
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue
            if not content:
                continue
            snippets.append(
                {
                    "file": str(path.relative_to(workspace)),
                    "lines": min(len(content), max_lines),
                    "content": "\n".join(content[:max_lines]),
                }
            )
            if len(snippets) >= max_files:
                return snippets
    return snippets
