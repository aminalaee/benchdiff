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
