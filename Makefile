.PHONY: help docs
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

lint: ## Run code linters
	isort --check appunit tests
	black --check appunit tests
	flake8 appunit tests
	mypy appunit tests
	safety check --full-report -i 38624 -i 38625

fmt format: ## Run code formatters
	isort appunit tests
	black appunit tests

requirements:  ## Make requirements
	poetry export -f requirements.txt -E docs > requirements.docs.txt
