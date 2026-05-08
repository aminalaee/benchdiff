from pathlib import Path

import pytest
from typer.testing import CliRunner

from benchdiff.cli import app

runner = CliRunner()


def test_cli_no_benchmarks(tmp_path: Path) -> None:
    result = runner.invoke(app, [str(tmp_path)])
    assert result.exit_code == 1
    assert "No benchmarks found" in result.output


def test_cli_runs_benchmarks(tmp_path: Path) -> None:
    bench = tmp_path / "bench_example.py"
    bench.write_text(
        "def fn_a(): pass\n"
        "def fn_b(): pass\n"
        '__benchmarks__ = [("group", [fn_a, fn_b])]\n'
    )
    result = runner.invoke(app, [str(tmp_path), "--repeat", "2", "--times", "10"])
    assert result.exit_code == 0


def test_cli_default_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, [])
    assert result.exit_code == 1
