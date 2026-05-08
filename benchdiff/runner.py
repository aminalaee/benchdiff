import importlib.util
import time
from collections.abc import Callable
from pathlib import Path

from benchdiff.models import BenchmarkResult, GroupResult


def _time_fn(fn: Callable, repeat: int, times: int) -> list[float]:
    timings = []
    for _ in range(repeat):
        start = time.perf_counter()
        for _ in range(times):
            fn()
        elapsed = time.perf_counter() - start
        timings.append(elapsed / times)
    return timings


def _load_benchmarks(path: Path) -> list[tuple[str, list[Callable]]]:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "__benchmarks__", [])


def run(
    path: Path,
    repeat: int = 5,
    times: int = 1000,
) -> list[GroupResult]:
    results = []
    for file in sorted(path.glob("bench_*.py")):
        for group_name, fns in _load_benchmarks(file):
            group_results = [
                BenchmarkResult(name=fn.__name__, timings=_time_fn(fn, repeat, times))
                for fn in fns
            ]
            results.append(GroupResult(name=group_name, results=group_results))
    return results
