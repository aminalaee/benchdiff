from pathlib import Path

from benchdiff.runner import _load_benchmarks, _time_fn, run


def test_time_fn_returns_correct_sample_count():
    timings = _time_fn(lambda: None, repeat=3, times=10)
    assert len(timings) == 3


def test_time_fn_positive_timings():
    timings = _time_fn(lambda: None, repeat=5, times=10)
    assert all(t >= 0 for t in timings)


def test_load_benchmarks(tmp_path: Path):
    bench = tmp_path / "bench_example.py"
    bench.write_text(
        "def fn_a(): pass\n"
        "def fn_b(): pass\n"
        '__benchmarks__ = [("group", [fn_a, fn_b])]\n'
    )
    benchmarks = _load_benchmarks(bench)
    assert len(benchmarks) == 1
    group_name, fns = benchmarks[0]
    assert group_name == "group"
    assert [f.__name__ for f in fns] == ["fn_a", "fn_b"]


def test_load_benchmarks_missing_attr(tmp_path: Path):
    bench = tmp_path / "bench_empty.py"
    bench.write_text("def fn(): pass\n")
    assert _load_benchmarks(bench) == []


def test_run(tmp_path: Path):
    bench = tmp_path / "bench_example.py"
    bench.write_text(
        "def fn_a(): pass\n"
        "def fn_b(): pass\n"
        '__benchmarks__ = [("group", [fn_a, fn_b])]\n'
    )
    results = run(tmp_path, repeat=2, times=10)
    assert len(results) == 1
    assert results[0].name == "group"
    assert len(results[0].results) == 2


def test_run_no_bench_files(tmp_path: Path):
    results = run(tmp_path)
    assert results == []
