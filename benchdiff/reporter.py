import platform
import sys
from datetime import datetime

import cpuinfo
from rich import box
from rich.console import Console
from rich.console import Group as RenderGroup
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

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


def _hint(units: set[str]) -> Text:
    if len(units) == 1:
        unit_name = _UNIT_NAMES[next(iter(units))]
        return Text(f"  * times in {unit_name}, lower is better", style="dim")
    return Text("  * lower is better", style="dim")


def _system_info(repeat: int, times: int) -> Table:
    cpu = (
        cpuinfo.get_cpu_info().get("brand_raw")
        or platform.processor()
        or platform.machine()
    )
    info = Table(box=None, show_header=False, padding=(0, 2))
    info.add_column(style="dim")
    info.add_column(style="dim")
    info.add_row("Python", sys.version.split()[0])
    info.add_row("Platform", platform.platform(terse=True))
    info.add_row("CPU", cpu)
    info.add_row("Rounds", f"{repeat:,} × {times:,} calls")
    info.add_row("Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return info


def print_results(
    groups: list[GroupResult], repeat: int = 5, times: int = 1000
) -> None:
    console = Console()
    units: set[str] = set()

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold")
    table.add_column("Benchmark", no_wrap=True)
    table.add_column("Min", justify="center")
    table.add_column("Median", justify="center")
    table.add_column("Max", justify="center")
    table.add_column("×", justify="center")

    for group in groups:
        fastest = group.fastest
        unit = _unit(fastest.median)
        units.add(unit)
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
        _hint(units),
        Rule(style="dim"),
        _system_info(repeat, times),
    )
    console.print(Panel(content, title="[bold]benchdiff[/bold]", expand=False))


def print_markdown(groups: list[GroupResult], repeat: int = 5, times: int = 1000) -> None:
    units: set[str] = set()

    print("| Benchmark | Min | Median | Max | × |")
    print("|:---|---:|---:|---:|---:|")

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

    cpu = cpuinfo.get_cpu_info().get("brand_raw") or platform.processor() or platform.machine()
    print(
        f"\nPython {sys.version.split()[0]} · "
        f"{platform.platform(terse=True)} · "
        f"{cpu} · "
        f"{repeat:,} × {times:,} rounds · "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
