from app.worker.tasks import _build_active_checkers


def test_build_active_checkers_uses_positive_weights():
    checkers = _build_active_checkers({"build": 50, "tests": 50, "documentation": 0})
    names = [checker.name for checker in checkers]

    assert names == ["build", "tests"]


def test_build_active_checkers_fallback_to_default_when_empty():
    checkers = _build_active_checkers({"build": 0, "tests": 0})
    names = [checker.name for checker in checkers]

    assert set(names) == {"static_analysis", "architecture", "build", "tests", "documentation", "git_practices"}
