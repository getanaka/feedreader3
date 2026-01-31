.PHONY: lint format typecheck test qa

lint:
	uv run ruff check

format:
	uv run ruff format

typecheck:
	uv run mypy feedreader3 tests

TEST_PROJECT = feedreader3-test
test:
	@docker compose -p $(TEST_PROJECT) ps --status running | grep -q test || docker compose -p $(TEST_PROJECT) -f docker-compose.test.yml --env-file ./tests/.env.test up -d
	@docker compose -p $(TEST_PROJECT) exec test uv run pytest

coverage:
	@docker compose -p $(TEST_PROJECT) ps --status running | grep -q test || docker compose -p $(TEST_PROJECT) -f docker-compose.test.yml --env-file ./tests/.env.test up -d
	@docker compose -p $(TEST_PROJECT) exec test uv run pytest --cov

qa: lint format typecheck test
