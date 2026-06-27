.PHONY: install test lint format check clean build publish publish-test

install:
	uv sync

test:
	uv run pytest -v

lint:
	uv run ruff check flex_kit
	uv run mypy flex_kit

format:
	uv run ruff format flex_kit tests
	uv run ruff check --fix flex_kit tests

check: lint test

clean:
	rm -rf dist/ build/ *.egg-info

build: clean
	uv build

publish: build
	uv publish

publish-test: build
	uv publish --publish-url https://test.pypi.org/legacy/
