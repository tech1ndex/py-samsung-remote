PYMODULE := src/samsung_remote
TESTS := tests
IMAGE := py-samsung-remote
INSTALL_STAMP := .install.stamp
POETRY := $(shell command -v poetry 2> /dev/null)
MYPY := $(shell command -v mypy 2> /dev/null)

.DEFAULT_GOAL := help

.PHONY: all
all: install lint test

.PHONY: help
help:
	@echo "Please use 'make <target>', where <target> is one of"
	@echo ""
	@echo "  install     install packages and prepare environment"
	@echo "  lint        run the code linters"
	@echo "  test        run all the tests"
	@echo "  all         install, lint, and test the project"
	@echo "  docker      build the Docker image"
	@echo "  run         run the Docker image on port 5001"
	@echo "  clean       remove all temporary files listed in .gitignore"
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."
	@echo "Most actions are configured in 'pyproject.toml'."

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): pyproject.toml
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) run pip install --upgrade pip setuptools
	$(POETRY) install --with dev,tests,linters
	touch $(INSTALL_STAMP)

.PHONY: lint
lint: $(INSTALL_STAMP)
    # Configured in pyproject.toml
    # Skips mypy if not installed
	@if [ -z $(MYPY) ]; then echo "Mypy not found, skipping..."; else echo "Running Mypy..."; $(POETRY) run mypy $(PYMODULE); fi
	@echo "Running Ruff..."; $(POETRY) run ruff check . --fix

.PHONY: test
test: $(INSTALL_STAMP)
    # Configured in pyproject.toml
	$(POETRY) run pytest

.PHONY: docker
docker:
	docker build -t $(IMAGE) .

.PHONY: run
run: docker
	docker run --rm -p 5001:5001 --env-file .env $(IMAGE)

.PHONY: clean
clean:
    # Delete all files in .gitignore
	git clean -Xdf
