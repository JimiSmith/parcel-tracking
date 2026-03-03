.PHONY: setup lint format-check test check mypy

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/pip install -r requirements-dev.txt

lint:
	$(BIN)/ruff check custom_components tests

format-check:
	$(BIN)/ruff format --check custom_components tests

test:
	$(BIN)/pytest -q

mypy:
	$(BIN)/mypy

check: lint format-check test
