from pathlib import Path

import typer

from benchdiff.reporter import print_results
from benchdiff.runner import run

app = typer.Typer()


@app.command()
def main(
    path: Path = typer.Argument(
        default=Path("."), help="Path to search for bench_*.py files"
    ),
    repeat: int = typer.Option(5, help="Number of measurement loops"),
    times: int = typer.Option(1000, help="Number of calls per measurement"),
) -> None:
    results = run(path, repeat=repeat, times=times)
    if not results:
        typer.echo("No benchmarks found.")
        raise typer.Exit(1)
    print_results(results)
