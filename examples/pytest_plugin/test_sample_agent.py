"""Offline pytest example for the pytest-agentest plugin.

Judges the recorded trace in examples/first_trace with agentest from inside a
pytest test, using the `agentest_run` fixture that pytest-agentest provides.
No network, model or API key is needed.

Run from the repository root:

    pip install agentest-ai pytest-agentest
    pytest examples/pytest_plugin -q
"""

from pathlib import Path

import pytest

pytest.importorskip("pytest_agentest", reason="pip install pytest-agentest")

FIRST_TRACE = Path(__file__).resolve().parents[1] / "first_trace"
TRACE = FIRST_TRACE / "trace.otlp.json"
TOOLS = FIRST_TRACE / "tools.json"


def verdict(report: str, check_id: str) -> str:
    """Return the verdict printed for one check ID in a Markdown report."""
    for line in report.splitlines():
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and cells[0] == check_id and len(cells) > 1:
            return cells[1]
    raise AssertionError(f"{check_id} not found in the agentest report")


def test_declared_tools_pass(agentest_run):
    result = agentest_run(otlp=str(TRACE), ids="T5-001", extra=["--tools", str(TOOLS)])
    assert verdict(result.stdout, "T5-001") == "pass"


def test_write_without_confirmation_is_caught(agentest_run):
    # The recorded write reports success with "confirm": false, so T5-007 fails.
    result = agentest_run(otlp=str(TRACE), ids="T5-007", extra=["--tools", str(TOOLS)])
    assert verdict(result.stdout, "T5-007") == "fail"
    assert "mark_reviewed" in result.stdout
