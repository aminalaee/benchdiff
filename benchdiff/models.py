import statistics
from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    name: str
    timings: list[float]

    @property
    def min(self) -> float:
        return min(self.timings)

    @property
    def median(self) -> float:
        return statistics.median(self.timings)

    @property
    def max(self) -> float:
        return max(self.timings)


@dataclass
class GroupResult:
    name: str
    results: list[BenchmarkResult]

    @property
    def fastest(self) -> BenchmarkResult:
        return min(self.results, key=lambda r: r.median)
