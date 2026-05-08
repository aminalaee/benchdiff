import pytest

from benchdiff.models import BenchmarkResult, GroupResult
from benchdiff.reporter import _fmt_time, _unit, print_results


def test_unit_nanoseconds():
    assert _unit(0.0000005) == "ns"


def test_unit_microseconds():
    assert _unit(0.0000015) == "µs"


def test_unit_milliseconds():
    assert _unit(0.0015) == "ms"


def test_unit_seconds():
    assert _unit(1.5) == "s"


def test_fmt_time_nanoseconds():
    assert _fmt_time(0.0000005, "ns") == "500.000ns"


def test_fmt_time_microseconds():
    assert _fmt_time(0.0000015, "µs") == "1.500µs"


def test_fmt_time_milliseconds():
    assert _fmt_time(0.0015, "ms") == "1.500ms"


def test_fmt_time_seconds():
    assert _fmt_time(1.5, "s") == "1.500s"


def test_print_results_shows_group_and_variants(capsys: pytest.CaptureFixture):
    groups = [
        GroupResult(
            name="UUID generation",
            results=[
                BenchmarkResult(name="fast", timings=[1.0, 1.0, 1.0]),
                BenchmarkResult(name="slow", timings=[3.0, 3.0, 3.0]),
            ],
        )
    ]
    print_results(groups)
    output = capsys.readouterr().out
    assert "UUID generation" in output
    assert "fast" in output
    assert "slow" in output
    assert "3.000x" in output


def test_print_results_same_unit_per_group(capsys: pytest.CaptureFixture):
    groups = [
        GroupResult(
            name="group",
            results=[
                BenchmarkResult(name="fast", timings=[0.0000001]),
                BenchmarkResult(name="slow", timings=[0.000001]),
            ],
        )
    ]
    print_results(groups)
    output = capsys.readouterr().out
    assert "ns" in output
    assert "µs" not in output


def test_print_results_single_variant_no_ratio(capsys: pytest.CaptureFixture):
    groups = [
        GroupResult(
            name="only",
            results=[BenchmarkResult(name="fn", timings=[1.0])],
        )
    ]
    print_results(groups)
    output = capsys.readouterr().out
    assert "fn" in output
    assert "1.000x" in output
