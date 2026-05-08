from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from benchdiff.models import GroupResult


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


def print_results(groups: list[GroupResult]) -> None:
    console = Console()

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold")
    table.add_column("Benchmark", no_wrap=True)
    table.add_column("Min", justify="center")
    table.add_column("Median", justify="center")
    table.add_column("Max", justify="center")
    table.add_column("×", justify="center")

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

    console.print(Panel(table, title="[bold]benchdiff[/bold]", expand=False))
