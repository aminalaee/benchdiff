import platform
import sys
from datetime import datetime
from pathlib import Path

import cpuinfo
from rich import box
from rich.console import Console
from rich.console import Group as RenderGroup
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from benchdiff.models import GroupResult

_UNIT_NAMES = {
    "ns": "nanoseconds",
    "µs": "microseconds",
    "ms": "milliseconds",
    "s": "seconds",
}


def _unit(seconds: float) -> str:
    if seconds < 1e-6:
        return "ns"
    if seconds < 1e-3:
        return "µs"
    if seconds < 1:
        return "ms"
    return "s"


def _fmt_time(seconds: float, unit: str) -> str:
    if unit == "ns":
        return f"{seconds * 1e9:.3f}ns"
    if unit == "µs":
        return f"{seconds * 1e6:.3f}µs"
    if unit == "ms":
        return f"{seconds * 1e3:.3f}ms"
    return f"{seconds:.3f}s"


def _cpu() -> str:
    return (
        cpuinfo.get_cpu_info().get("brand_raw")
        or platform.processor()
        or platform.machine()
    )


def _footer_str(repeat: int, times: int) -> str:
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    python = sys.version.split()[0]
    platform_str = platform.platform(terse=True)
    rounds = f"{repeat:,} × {times:,} rounds"
    return f"Python {python} · {platform_str} · {_cpu()} · {rounds} · {date}"


def _system_info(repeat: int, times: int) -> Table:
    info = Table(box=None, show_header=False, padding=(0, 2))
    info.add_column(style="dim")
    info.add_column(style="dim")
    info.add_row("Python", sys.version.split()[0])
    info.add_row("Platform", platform.platform(terse=True))
    info.add_row("CPU", _cpu())
    info.add_row("Rounds", f"{repeat:,} × {times:,} calls")
    info.add_row("Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return info


def print_results(
    groups: list[GroupResult], repeat: int = 5, times: int = 1000
) -> None:
    console = Console()

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold")
    table.add_column("Benchmark", no_wrap=True)
    table.add_column("Min", justify="center", min_width=12, no_wrap=True)
    table.add_column("Median", justify="center", min_width=12, no_wrap=True)
    table.add_column("Max", justify="center", min_width=12, no_wrap=True)
    table.add_column("×", justify="center", min_width=7, no_wrap=True)

    for group in groups:
        fastest = group.fastest
        unit = _unit(fastest.median)
        table.add_row(f"[bold cyan]{group.name}[/bold cyan]", "", "", "", "")

        for result in group.results:
            is_fastest = result.name == fastest.name
            ratio = result.median / fastest.median if fastest.median > 0 else 1.0

            name = (
                f"  [green]{result.name}[/green]" if is_fastest else f"  {result.name}"
            )
            ratio_str = (
                "[green]1.000x[/green]" if is_fastest else f"[red]{ratio:.3f}x[/red]"
            )

            table.add_row(
                name,
                _fmt_time(result.min, unit),
                _fmt_time(result.median, unit),
                _fmt_time(result.max, unit),
                ratio_str,
            )

    content = RenderGroup(
        table,
        Rule(style="dim"),
        _system_info(repeat, times),
    )
    console.print(Panel(content, title="[bold]benchdiff[/bold]", expand=False))


def print_markdown(
    groups: list[GroupResult], repeat: int = 5, times: int = 1000
) -> None:
    units: set[str] = set()

    print("| Benchmark | Min | Median | Max | × |")
    print("|:---|:---:|:---:|:---:|:---:|")

    for group in groups:
        fastest = group.fastest
        unit = _unit(fastest.median)
        units.add(unit)

        print(f"| **{group.name}** | | | | |")

        for result in group.results:
            is_fastest = result.name == fastest.name
            ratio = result.median / fastest.median if fastest.median > 0 else 1.0
            ratio_str = "1.000x" if is_fastest else f"{ratio:.3f}x"
            print(
                f"| {result.name} "
                f"| {_fmt_time(result.min, unit)} "
                f"| {_fmt_time(result.median, unit)} "
                f"| {_fmt_time(result.max, unit)} "
                f"| {ratio_str} |"
            )

    print()
    if len(units) == 1:
        print(f"*times in {_UNIT_NAMES[next(iter(units))]}, lower is better*")
    else:
        print("*lower is better*")

    print(f"\n{_footer_str(repeat, times)}")


def _to_unit(seconds: float, unit: str) -> float:
    if unit == "ns":
        return seconds * 1e9
    if unit == "µs":
        return seconds * 1e6
    if unit == "ms":
        return seconds * 1e3
    return seconds


def save_svg(
    groups: list[GroupResult], output: Path, repeat: int = 5, times: int = 1000
) -> None:
    try:
        import matplotlib  # type: ignore[import]

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt  # type: ignore[import]
    except ImportError:
        raise ImportError(
            "matplotlib is required for SVG output: pip install benchdiff[svg]"
        )

    n = len(groups)
    fig, axes = plt.subplots(n, 1, figsize=(10, 1.8 * n + 1.2))
    if n == 1:
        axes = [axes]

    for ax, group in zip(axes, groups):
        fastest = group.fastest
        unit = _unit(fastest.median)
        names = [r.name for r in group.results]
        medians = [_to_unit(r.median, unit) for r in group.results]
        palette = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        colors = [palette[i % len(palette)] for i in range(len(group.results))]

        bars = ax.barh(names, medians, color=colors, height=0.5)
        ax.invert_yaxis()

        max_val = max(medians)
        ax.set_xlim(0, max_val * 1.25)

        for bar, result in zip(bars, group.results):
            ratio = result.median / fastest.median
            label = f"{ratio:.3f}x"
            ax.text(
                bar.get_width() + max_val * 0.02,
                bar.get_y() + bar.get_height() / 2,
                label,
                va="center",
                ha="left",
                fontsize=9,
                color="#555555",
            )

        ax.set_title(group.name, fontsize=10, fontweight="bold", loc="left", pad=4)
        ax.set_xlabel(f"median time ({unit})", fontsize=8)
        ax.tick_params(axis="both", labelsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.text(
        0.5,
        0.005,
        _footer_str(repeat, times),
        ha="center",
        va="bottom",
        fontsize=7,
        color="#888888",
    )

    plt.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(str(output), format="svg", bbox_inches="tight")
    plt.close(fig)
