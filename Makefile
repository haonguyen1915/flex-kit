.PHONY: install test lint format check clean build publish publish-test

install:
	poetry install

test:
	poetry run pytest -v

lint:
	poetry run ruff check flex_kit
	poetry run mypy flex_kit

format:
	poetry run ruff format flex_kit tests
	poetry run ruff check --fix flex_kit tests

check: lint test

clean:
	rm -rf dist/ build/ *.egg-info

build: clean
	poetry build

publish: build
	poetry publish

publish-test: build
	poetry publish -r testpypi
