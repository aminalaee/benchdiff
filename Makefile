.PHONY: test lint format coverage

test:
	uv run --group dev --extra svg pytest tests/

lint:
	uv run --group dev --extra svg ruff check benchdiff/ tests/
	uv run --group dev --extra svg ruff format --check benchdiff/ tests/
	uv run --group dev --extra svg mypy benchdiff/ tests/

format:
	uv run --group dev --extra svg ruff format benchdiff/ tests/
	uv run --group dev --extra svg ruff check --fix benchdiff/ tests/

coverage:
	uv run --group dev --extra svg pytest --cov=benchdiff --cov-report=term-missing tests/
