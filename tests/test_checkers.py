from app.checking.checkers import TestChecker


def test_parse_junit_summary_from_testsuite(tmp_path):
    reports = tmp_path / "build" / "test-results" / "testDebugUnitTest"
    reports.mkdir(parents=True)
    report = reports / "TEST-sample.xml"
    report.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<testsuite tests="5" failures="1" errors="1" skipped="1">
</testsuite>
""",
        encoding="utf-8",
    )

    total, passed = TestChecker._parse_junit_summary(str(tmp_path))

    assert total == 5
    assert passed == 2
