import sys
from pathlib import Path

import pytest

from benchdiff.models import BenchmarkResult, GroupResult
from benchdiff.reporter import (
    _fmt_time,
    _hint,
    _to_unit,
    _unit,
    print_markdown,
    print_results,
    save_svg,
)


def test_unit_nanoseconds() -> None:
    assert _unit(0.0000005) == "ns"


def test_unit_microseconds() -> None:
    assert _unit(0.0000015) == "µs"


def test_unit_milliseconds() -> None:
    assert _unit(0.0015) == "ms"


def test_unit_seconds() -> None:
    assert _unit(1.5) == "s"


def test_to_unit_nanoseconds() -> None:
    assert _to_unit(0.0000005, "ns") == pytest.approx(500.0)


def test_to_unit_microseconds() -> None:
    assert _to_unit(0.0000015, "µs") == pytest.approx(1.5)


def test_to_unit_milliseconds() -> None:
    assert _to_unit(0.0015, "ms") == pytest.approx(1.5)


def test_to_unit_seconds() -> None:
    assert _to_unit(1.5, "s") == pytest.approx(1.5)


def test_fmt_time_nanoseconds() -> None:
    assert _fmt_time(0.0000005, "ns") == "500.000ns"


def test_fmt_time_microseconds() -> None:
    assert _fmt_time(0.0000015, "µs") == "1.500µs"


def test_fmt_time_milliseconds() -> None:
    assert _fmt_time(0.0015, "ms") == "1.500ms"


def test_fmt_time_seconds() -> None:
    assert _fmt_time(1.5, "s") == "1.500s"


def test_print_results_shows_group_and_variants(capsys: pytest.CaptureFixture) -> None:
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


def test_print_results_same_unit_per_group(capsys: pytest.CaptureFixture) -> None:
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


def test_print_results_single_variant_no_ratio(capsys: pytest.CaptureFixture) -> None:
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


def test_print_results_system_info(capsys: pytest.CaptureFixture) -> None:
    groups = [
        GroupResult(
            name="group",
            results=[BenchmarkResult(name="fn", timings=[1.0])],
        )
    ]
    print_results(groups, repeat=3, times=500)
    output = capsys.readouterr().out
    assert sys.version.split()[0] in output
    assert "3" in output
    assert "500" in output


def test_hint_single_unit() -> None:
    assert "nanoseconds" in _hint({"ns"}).plain
    assert "lower is better" in _hint({"ns"}).plain


def test_hint_mixed_units() -> None:
    text = _hint({"ns", "µs"}).plain
    assert "lower is better" in text
    assert "nanoseconds" not in text


def test_print_results_hint(capsys: pytest.CaptureFixture) -> None:
    groups = [
        GroupResult(
            name="group",
            results=[BenchmarkResult(name="fn", timings=[0.000001])],
        )
    ]
    print_results(groups)
    output = capsys.readouterr().out
    assert "microseconds" in output
    assert "lower is better" in output


def test_print_results_system_info_rounds_format(capsys: pytest.CaptureFixture) -> None:
    groups = [
        GroupResult(
            name="group",
            results=[BenchmarkResult(name="fn", timings=[1.0])],
        )
    ]
    print_results(groups, repeat=5, times=10_000)
    output = capsys.readouterr().out
    assert "10,000" in output


def test_print_markdown_structure(capsys: pytest.CaptureFixture) -> None:
    groups = [
        GroupResult(
            name="UUID generation",
            results=[
                BenchmarkResult(name="fast", timings=[0.000001, 0.000001, 0.000001]),
                BenchmarkResult(name="slow", timings=[0.000003, 0.000003, 0.000003]),
            ],
        )
    ]
    print_markdown(groups)
    output = capsys.readouterr().out
    assert "**UUID generation**" in output
    assert "| Benchmark |" in output
    assert "fast" in output
    assert "1.000x" in output
    assert "3.000x" in output


def test_print_markdown_mixed_units_hint(capsys: pytest.CaptureFixture) -> None:
    groups = [
        GroupResult(
            name="ns group", results=[BenchmarkResult(name="a", timings=[0.0000001])]
        ),
        GroupResult(
            name="ms group", results=[BenchmarkResult(name="b", timings=[0.001])]
        ),
    ]
    print_markdown(groups)
    output = capsys.readouterr().out
    assert "*lower is better*" in output
    assert "nanoseconds" not in output


def test_print_markdown_no_rich_markup(capsys: pytest.CaptureFixture) -> None:
    groups = [
        GroupResult(
            name="group",
            results=[
                BenchmarkResult(name="a", timings=[1.0]),
                BenchmarkResult(name="b", timings=[2.0]),
            ],
        )
    ]
    print_markdown(groups)
    output = capsys.readouterr().out
    assert "[green]" not in output
    assert "[red]" not in output


@pytest.fixture
def two_groups() -> list[GroupResult]:
    return [
        GroupResult(
            name="uuid4()",
            results=[
                BenchmarkResult(name="stdlib_uuid4", timings=[0.0000012, 0.0000013]),
                BenchmarkResult(name="uuid_utils_uuid4", timings=[5.6e-8, 6e-8]),
            ],
        ),
        GroupResult(
            name="uuid7()",
            results=[
                BenchmarkResult(name="stdlib_uuid7", timings=[0.0000014, 0.0000014]),
                BenchmarkResult(name="uuid_utils_uuid7", timings=[8.3e-8, 9e-8]),
            ],
        ),
    ]


def test_save_svg_creates_file(tmp_path: Path, two_groups: list[GroupResult]) -> None:
    output = tmp_path / "bench.svg"
    save_svg(two_groups, output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_save_svg_is_valid_svg(tmp_path: Path, two_groups: list[GroupResult]) -> None:
    output = tmp_path / "bench.svg"
    save_svg(two_groups, output)
    content = output.read_text()
    assert content.startswith("<?xml")
    assert "<svg" in content


def test_save_svg_contains_group_names(
    tmp_path: Path, two_groups: list[GroupResult]
) -> None:
    output = tmp_path / "bench.svg"
    save_svg(two_groups, output)
    content = output.read_text()
    assert "uuid4()" in content
    assert "uuid7()" in content


def test_save_svg_contains_system_info(
    tmp_path: Path, two_groups: list[GroupResult]
) -> None:
    output = tmp_path / "bench.svg"
    save_svg(two_groups, output, repeat=3, times=500)
    content = output.read_text()
    assert sys.version.split()[0] in content
    assert "rounds" in content
