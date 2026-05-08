from pathlib import Path

import typer

from benchdiff.reporter import print_markdown, print_results
from benchdiff.runner import run

app = typer.Typer()


@app.command()
def main(
    path: Path = typer.Argument(
        default=Path("."), help="Path to search for bench_*.py files"
    ),
    repeat: int = typer.Option(5, help="Number of measurement loops"),
    times: int = typer.Option(1000, help="Number of calls per measurement"),
    markdown: bool = typer.Option(False, "--markdown", help="Output as GFM markdown"),
) -> None:
    results = run(path, repeat=repeat, times=times)
    if not results:
        typer.echo("No benchmarks found.")
        raise typer.Exit(1)
    if markdown:
        print_markdown(results, repeat=repeat, times=times)
    else:
        print_results(results, repeat=repeat, times=times)
