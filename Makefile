.PHONY: test lint format coverage

test:
	uv run --group dev pytest tests/

lint:
	uv run --group dev ruff check benchdiff/ tests/
	uv run --group dev ruff format --check benchdiff/ tests/
	uv run --group dev mypy benchdiff/ tests/

format:
	uv run --group dev ruff format benchdiff/ tests/
	uv run --group dev ruff check --fix benchdiff/ tests/

coverage:
	uv run --group dev pytest --cov=benchdiff --cov-report=term-missing tests/
