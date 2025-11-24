.PHONY: lint format typecheck test qa

lint:
	uv run ruff check

format:
	uv run ruff format

typecheck:
	uv run mypy feedreader3 tests

test:
	uv run pytest

qa: lint format typecheck test
