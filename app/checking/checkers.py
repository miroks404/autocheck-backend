import re
import xml.etree.ElementTree as ET
from pathlib import Path

from app.checking.container_runner import run_checker_command
from app.checking.interfaces import CheckResultDTO
from app.models import Submission

ANDROID_CHECKER_IMAGE = "autocheck-android-checker:latest"
DEFAULT_CHECKER_IMAGE = "python:3.12-alpine"


def _runtime_image(workspace_path: str) -> str:
    root = Path(workspace_path)
    if (root / "gradlew").exists() or (root / "app" / "build.gradle").exists() or (root / "app" / "build.gradle.kts").exists():
        return ANDROID_CHECKER_IMAGE
    return DEFAULT_CHECKER_IMAGE


class StaticAnalysisChecker:
    """StaticAnalysisChecker — runs static analysis for candidate submission.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - run(submission, workspace_path) -> CheckResultDTO
    """

    name = "static_analysis"

    def run(self, submission: Submission, workspace_path: str) -> CheckResultDTO:
        command = self._detect_command(workspace_path)
        if not command:
            return CheckResultDTO(
                checker=self.name,
                status="error",
                score=0,
                message="No static analyzer command detected",
                details={"errors": 0, "warnings": 0},
            )
        result = run_checker_command(
            command,
            workspace_path=workspace_path,
            timeout_sec=180,
            image=_runtime_image(workspace_path),
        )
        if result["timed_out"]:
            return CheckResultDTO(
                checker=self.name,
                status="error",
                score=0,
                message="Превышено время выполнения",
                details={"errors": 0, "warnings": 0, "output": result["output"], "isolated": result["isolated"]},
            )
        output = result["output"]
        errors = len(re.findall(r"\berror\b", output, re.IGNORECASE))
        warnings = len(re.findall(r"\bwarning\b", output, re.IGNORECASE))
        score = max(0, 100 - errors * 5 - warnings)
        return CheckResultDTO(
            checker=self.name,
            status="passed" if result["ok"] else "failed",
            score=score,
            message="Static analysis completed",
            details={"errors": errors, "warnings": warnings, "output": output[:4000], "isolated": result["isolated"]},
        )

    @staticmethod
    def _detect_command(workspace_path: str) -> str | None:
        root = Path(workspace_path)
        if (root / "gradlew").exists():
            return "chmod +x ./gradlew && ./gradlew lint --no-daemon"
        if (root / "detekt.yml").exists():
            return "./gradlew detekt --no-daemon"
        if (root / "package.json").exists():
            return "npm ci --silent && npx eslint ."
        if (root / "pubspec.yaml").exists():
            return "dart analyze || flutter analyze"
        return None


class ArchitectureChecker:
    """ArchitectureChecker — validates project layering and dependency direction.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - run(submission, workspace_path) -> CheckResultDTO
    """

    name = "architecture"

    def run(self, submission: Submission, workspace_path: str) -> CheckResultDTO:
        result = run_checker_command(
            command=(
                "python - <<'PY'\n"
                "import json, pathlib\n"
                "root = pathlib.Path('/workspace')\n"
                "files=[p for p in root.rglob('*') if p.is_file()]\n"
                "normalized=[p.relative_to(root).as_posix().lower() for p in files]\n"
                "layer_names=['domain','data','presentation','application','infrastructure']\n"
                "layers_found=sum(1 for layer in layer_names if any(f'/{layer}/' in f or f.startswith(f'{layer}/') for f in normalized))\n"
                "violations=0\n"
                "for p in root.rglob('*.py'):\n"
                "  if '/domain/' not in p.as_posix().lower():\n"
                "    continue\n"
                "  c=p.read_text(encoding='utf-8', errors='ignore')\n"
                "  if 'from app.infrastructure' in c or 'import app.infrastructure' in c:\n"
                "    violations += 1\n"
                "print(json.dumps({'layers_found':layers_found,'violations':violations}))\n"
                "PY"
            ),
            workspace_path=workspace_path,
            timeout_sec=180,
            image=_runtime_image(workspace_path),
        )
        if result["timed_out"]:
            return CheckResultDTO(
                checker=self.name,
                status="error",
                score=0,
                message="Превышено время выполнения",
                details={"output": result["output"], "isolated": result["isolated"]},
            )
        try:
            payload = __import__("json").loads(result["output"].splitlines()[-1])
            layers_found = int(payload.get("layers_found", 0))
            violations = int(payload.get("violations", 0))
        except Exception:
            layers_found = 0
            violations = 0
        score = max(0, min(100, layers_found * 25 - violations * 20))
        return CheckResultDTO(
            checker=self.name,
            status="passed" if score >= 50 else "failed",
            score=score,
            message="Architecture check completed",
            details={"layers_found": layers_found, "dependency_violations": violations, "isolated": result["isolated"]},
        )


class BuildChecker:
    """BuildChecker — attempts project build and computes build score.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - run(submission, workspace_path) -> CheckResultDTO
    """

    name = "build"

    def run(self, submission: Submission, workspace_path: str) -> CheckResultDTO:
        command = self._detect_command(workspace_path)
        if not command:
            return CheckResultDTO(
                checker=self.name,
                status="error",
                score=0,
                message="Build command is not configured for this stack",
                details={"compile_errors": 0},
            )
        result = run_checker_command(
            command,
            workspace_path=workspace_path,
            timeout_sec=180,
            image=_runtime_image(workspace_path),
        )
        if result["timed_out"]:
            return CheckResultDTO(
                checker=self.name,
                status="error",
                score=0,
                message="Превышено время выполнения",
                details={"compile_errors": 0, "output": result["output"], "isolated": result["isolated"]},
            )
        compile_errors = len(re.findall(r"\berror\b", result["output"], re.IGNORECASE))
        return CheckResultDTO(
            checker=self.name,
            status="passed" if result["ok"] else "failed",
            score=100 if result["ok"] else 0,
            message="Build succeeded" if result["ok"] else "Build failed",
            details={"compile_errors": compile_errors, "output": result["output"][:4000], "isolated": result["isolated"]},
        )

    @staticmethod
    def _detect_command(workspace_path: str) -> str | None:
        root = Path(workspace_path)
        if (root / "gradlew").exists():
            return "chmod +x ./gradlew && ./gradlew assembleDebug --no-daemon"
        if list(root.glob("*.xcodeproj")):
            return "xcodebuild -list"
        if (root / "pubspec.yaml").exists():
            return "flutter build apk --debug"
        if (root / "package.json").exists():
            return "npm ci --silent && npm run build"
        return None


class TestChecker:
    """TestChecker — executes tests and computes pass rate score.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - run(submission, workspace_path) -> CheckResultDTO
    """

    name = "tests"

    def run(self, submission: Submission, workspace_path: str) -> CheckResultDTO:
        command = self._detect_command(workspace_path)
        if not command:
            return CheckResultDTO(
                checker=self.name,
                status="failed",
                score=0,
                message="No tests configured",
                details={"total": 0, "passed": 0},
            )
        result = run_checker_command(
            command,
            workspace_path=workspace_path,
            timeout_sec=180,
            image=_runtime_image(workspace_path),
        )
        if result["timed_out"]:
            return CheckResultDTO(
                checker=self.name,
                status="error",
                score=0,
                message="Превышено время выполнения",
                details={"total": 0, "passed": 0, "output": result["output"], "isolated": result["isolated"]},
            )
        total, passed = self._parse_junit_summary(workspace_path)
        junit_detected = total > 0
        if total == 0:
            passed = len(re.findall(r"\bPASS(?:ED)?\b", result["output"], re.IGNORECASE))
            failed = len(re.findall(r"\bFAIL(?:ED)?\b", result["output"], re.IGNORECASE))
            total = passed + failed
        if total == 0:
            # fallback heuristic for tool outputs without explicit markers
            total = 1
            passed = 1 if result["ok"] else 0
        score = int((passed / total) * 100) if total else 0
        return CheckResultDTO(
            checker=self.name,
            status="passed" if result["ok"] else "failed",
            score=score,
            message="Test run completed",
            details={
                "total": total,
                "passed": passed,
                "junit_detected": junit_detected,
                "output": result["output"][:4000],
                "isolated": result["isolated"],
            },
        )

    @staticmethod
    def _detect_command(workspace_path: str) -> str | None:
        root = Path(workspace_path)
        if (root / "gradlew").exists():
            return "chmod +x ./gradlew && ./gradlew test --no-daemon"
        if (root / "package.json").exists():
            return "npm ci --silent && npm test -- --watch=false"
        if (root / "pubspec.yaml").exists():
            return "flutter test"
        if list(root.glob("*.xcodeproj")):
            return "xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 15'"
        return None

    @staticmethod
    def _parse_junit_summary(workspace_path: str) -> tuple[int, int]:
        root = Path(workspace_path)
        total = 0
        failed = 0
        for report in root.rglob("*.xml"):
            parts = {part.lower() for part in report.parts}
            if "test-results" not in parts and "surefire-reports" not in parts and "junit" not in report.name.lower():
                continue
            try:
                xml_root = ET.fromstring(report.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue

            suites = [xml_root]
            if xml_root.tag == "testsuite":
                suites = [xml_root]
            elif xml_root.tag == "testsuites":
                suites = [node for node in xml_root if node.tag == "testsuite"]

            for suite in suites:
                tests = int(suite.attrib.get("tests", 0))
                failures = int(suite.attrib.get("failures", 0))
                errors = int(suite.attrib.get("errors", 0))
                skipped = int(suite.attrib.get("skipped", 0))
                total += tests
                failed += failures + errors + skipped

        if total <= 0:
            return 0, 0
        passed = max(0, total - failed)
        return total, passed


class DocumentationChecker:
    """DocumentationChecker — evaluates documentation coverage in source code.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - run(submission, workspace_path) -> CheckResultDTO
    """

    name = "documentation"

    def run(self, submission: Submission, workspace_path: str) -> CheckResultDTO:
        result = run_checker_command(
            command=(
                "python - <<'PY'\n"
                "import json, pathlib, re\n"
                "root = pathlib.Path('/workspace')\n"
                "ext={'.py','.kt','.swift','.java','.js','.ts','.dart'}\n"
                "code_files=[p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in ext]\n"
                "public_entities=0\n"
                "documented_entities=0\n"
                "for p in code_files:\n"
                "  lines=p.read_text(encoding='utf-8', errors='ignore').splitlines()\n"
                "  for idx, line in enumerate(lines):\n"
                "    s=line.strip()\n"
                "    if re.match(r'^(def |class |public |fun |struct |interface )', s):\n"
                "      public_entities += 1\n"
                "      prev=lines[idx-1].strip() if idx > 0 else ''\n"
                "      if prev.startswith('#') or prev.startswith('//') or prev.startswith('/*') or prev.startswith('\"\"\"'):\n"
                "        documented_entities += 1\n"
                "readme_exists=(root / 'README.md').exists()\n"
                "if readme_exists:\n"
                "  documented_entities += 1\n"
                "print(json.dumps({'public':public_entities,'documented':documented_entities,'readme':readme_exists}))\n"
                "PY"
            ),
            workspace_path=workspace_path,
            timeout_sec=180,
            image=_runtime_image(workspace_path),
        )
        if result["timed_out"]:
            return CheckResultDTO(
                checker=self.name,
                status="error",
                score=0,
                message="Превышено время выполнения",
                details={"output": result["output"], "isolated": result["isolated"]},
            )
        try:
            payload = __import__("json").loads(result["output"].splitlines()[-1])
            public_entities = int(payload.get("public", 0))
            documented_entities = int(payload.get("documented", 0))
            readme_exists = bool(payload.get("readme", False))
        except Exception:
            public_entities = 0
            documented_entities = 0
            readme_exists = False
        total_entities = public_entities + 1
        coverage = int(round((documented_entities / total_entities) * 100)) if total_entities else 0
        return CheckResultDTO(
            checker=self.name,
            status="passed" if coverage >= 50 else "failed",
            score=coverage,
            message="Documentation check completed",
            details={
                "public_entities": public_entities,
                "documented_entities": documented_entities,
                "readme_exists": readme_exists,
                "public_entities_documented_pct": coverage,
                "isolated": result["isolated"],
            },
        )


class GitPracticesChecker:
    """GitPracticesChecker — checks repository commit and branch quality.

    Date: 31-05-2026
    Author: Team 4
    Public methods:
    - run(submission, workspace_path) -> CheckResultDTO
    """

    name = "git_practices"

    def run(self, submission: Submission, workspace_path: str) -> CheckResultDTO:
        if not Path(workspace_path, ".git").exists():
            return CheckResultDTO(
                checker=self.name,
                status="failed",
                score=0,
                message="Git repository metadata not found",
                details={"meaningful_commits_pct": 0, "feature_branches": 0},
            )
        log_result = run_checker_command(
            "git log --pretty=format:'%s' -n 50",
            workspace_path=workspace_path,
            timeout_sec=60,
            image=_runtime_image(workspace_path),
        )
        branch_result = run_checker_command(
            "git branch --all",
            workspace_path=workspace_path,
            timeout_sec=60,
            image=_runtime_image(workspace_path),
        )
        review_result = run_checker_command(
            "git log --pretty=format:'%s' -n 200",
            workspace_path=workspace_path,
            timeout_sec=60,
            image=_runtime_image(workspace_path),
        )
        messages = [m.strip().lower() for m in log_result["output"].splitlines() if m.strip()]
        meaningful = [m for m in messages if m not in {"fix", "update"} and len(m.split()) >= 2]
        meaningful_pct = int(round((len(meaningful) / len(messages)) * 100)) if messages else 0
        feature_branches = len([b for b in branch_result["output"].splitlines() if "main" not in b and "master" not in b])
        review_markers = ("merge pull request", "pull request", "merge request", " mr ", "merge branch")
        review_evidence = 0
        for line in review_result["output"].lower().splitlines():
            if any(marker in line for marker in review_markers):
                review_evidence += 1
        score = min(100, int(meaningful_pct * 0.6 + min(feature_branches, 10) * 2 + min(review_evidence, 10) * 2))
        return CheckResultDTO(
            checker=self.name,
            status="passed" if score >= 50 else "failed",
            score=score,
            message="Git practices check completed",
            details={
                "meaningful_commits_pct": meaningful_pct,
                "feature_branches": feature_branches,
                "review_evidence": review_evidence,
                "output_excerpt": (log_result["output"][:1200] if log_result["output"] else ""),
            },
        )
