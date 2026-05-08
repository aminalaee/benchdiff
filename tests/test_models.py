from benchdiff.models import BenchmarkResult, GroupResult


def test_benchmark_result_min() -> None:
    result = BenchmarkResult(name="fn", timings=[3.0, 1.0, 2.0])
    assert result.min == 1.0


def test_benchmark_result_max() -> None:
    result = BenchmarkResult(name="fn", timings=[3.0, 1.0, 2.0])
    assert result.max == 3.0


def test_benchmark_result_median() -> None:
    result = BenchmarkResult(name="fn", timings=[1.0, 2.0, 3.0, 4.0, 5.0])
    assert result.median == 3.0


def test_benchmark_result_median_even() -> None:
    result = BenchmarkResult(name="fn", timings=[1.0, 2.0, 3.0, 4.0])
    assert result.median == 2.5


def test_group_result_fastest() -> None:
    fast = BenchmarkResult(name="fast", timings=[1.0, 1.0, 1.0])
    slow = BenchmarkResult(name="slow", timings=[3.0, 3.0, 3.0])
    group = GroupResult(name="group", results=[slow, fast])
    assert group.fastest.name == "fast"


def test_group_result_fastest_single() -> None:
    only = BenchmarkResult(name="only", timings=[2.0])
    group = GroupResult(name="group", results=[only])
    assert group.fastest.name == "only"
