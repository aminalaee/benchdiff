# benchdiff

A CLI benchmarking tool with rich terminal output and markdown export.

## Installation

```bash
pip install benchdiff
```

## Usage

Create a file named `bench_*.py` and define a `__benchmarks__` list:

```python
# bench_strings.py

words = ["hello", "world", "foo", "bar"]


def concat():
    result = ""
    for w in words:
        result += w


def join():
    "".join(words)


def format_string():
    "%s %s %s %s" % tuple(words)


def fstring():
    f"{words[0]} {words[1]} {words[2]} {words[3]}"


__benchmarks__ = [
    ("String concatenation", [concat, join]),
    ("String formatting", [format_string, fstring]),
]
```

Run benchmarks:

```bash
benchdiff benchmarks/
```

```
╭──────────────────────────────── benchdiff ────────────────────────────────╮
│                                                                           │
│   Benchmark                 Min         Median        Max          ×      │
│  ───────────────────────────────────────────────────────────────────────  │
│   String concatenation                                                    │
│     concat                78.333ns     80.833ns     97.750ns    1.711x    │
│     join                  44.250ns     47.250ns     53.125ns    1.000x    │
│   String formatting                                                       │
│     format_string        103.834ns    110.417ns    114.708ns    1.464x    │
│     fstring               75.000ns     75.417ns     76.083ns    1.000x    │
│                                                                           │
│   * times in nanoseconds, lower is better                                 │
│ ───────────────────────────────────────────────────────────────────────── │
│   Python      3.14.2                                                      │
│   Platform    macOS-26.3.1                                                │
│   CPU         Apple M3 Pro                                                │
│   Rounds      5 × 1,000 calls                                             │
│   Date        2026-05-08 10:05:59                                         │
╰───────────────────────────────────────────────────────────────────────────╯
```

## CLI options

```
benchdiff [PATH] [OPTIONS]

Arguments:
  PATH    Path to search for bench_*.py files [default: .]

Options:
  --repeat    Number of measurement loops [default: 5]
  --times     Number of calls per measurement [default: 1000]
  --markdown  Output as GFM markdown table
  --help      Show this message and exit.
```

## Markdown output

```bash
benchdiff benchmarks/ --markdown
```

| Benchmark | Min | Median | Max | × |
|:---|:---:|:---:|:---:|:---:|
| **String concatenation** | | | | |
| concat | 84.875ns | 94.250ns | 157.792ns | 1.879x |
| join | 50.042ns | 50.167ns | 52.166ns | 1.000x |
| **String formatting** | | | | |
| format_string | 113.833ns | 115.083ns | 118.750ns | 1.539x |
| fstring | 72.375ns | 74.791ns | 84.583ns | 1.000x |

*times in nanoseconds, lower is better*

Python 3.14.2 · macOS-26.3.1 · Apple M3 Pro · 5 × 1,000 rounds · 2026-05-08 11:14:38
