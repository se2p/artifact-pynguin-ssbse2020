# Manage the flutils package
# Run the following for more information:
#	make help


# ---- SET VARIABLES ----

PROJECT := flutils
PROJECT_HOME := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

ifndef XDG_CONFIG_HOME
	XDG_CONFIG_HOME := $(HOME)/.config
endif

PROJECT_CONFIG_HOME := $(XDG_CONFIG_HOME)/$(PROJECT)

IMAGE_NAME := registry.gitlab.com/finite-loop/$(PROJECT)/pyenv:latest
RUNNING_CONTAINERS := $(shell docker ps -a -q)
PATH_NEW := $(shell pyenv root)/shims:$(PATH)
PYENV_EXISTS := $(shell command -v pyenv 2>/dev/null)
DOCKER_EXISTS := $(shell command -v docker 2>/dev/null)
DOCKER_RUNNING := $(docker info 2>&1>/dev/null && echo 'docker is running')
TWINE_EXISTS := $(shell command -v twine 2>/dev/null)
GIT_EXISTS := $(shell command -v git 2>/dev/null)
TWINE_USER := $(shell sed -n 1,1p $(HOME)/.pypi 2>/dev/null)
TWINE_PASS := $(shell sed -n 2,1p $(HOME)/.pypi 2>/dev/null)
TWINE_USER_TEST := $(shell sed -n 3,1p $(HOME)/.pypi 2>/dev/null)
TWINE_PASS_TEST := $(shell sed -n 4,1p $(HOME)/.pypi 2>/dev/null)

# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)


.PHONY: all
all: help
	@echo $(MAKEFILE_DIR)


.PHONY: vals
vals:
	@echo
	@echo "$(GREEN)            PROJECT:$(RESET) $(PROJECT)"
	@echo "$(GREEN)       PROJECT_HOME:$(RESET) $(PROJECT_HOME)"
	@echo "$(GREEN)PROJECT_CONFIG_HOME:$(RESET) $(PROJECT_CONFIG_HOME)"
	@echo
	@echo "$(GREEN)        PYPIRC_PATH:$(RESET) $(PYPIRC_PATH)"
	@echo "$(GREEN)    XDG_CONFIG_HOME:$(RESET) $(XDG_CONFIG_HOME)"


# ---- VALIDATION COMMANDS ----

.PHONY: validate-docker
validate-docker:
ifneq ($(shell command -v docker 2>&1>/dev/null; echo $$?), 0)
	$(error "Unable to find Docker.  Is it installed?")
else
ifneq ($(shell docker info 2>&1>/dev/null; echo $$?), 0)
	$(error "Docker is NOT running.  Please Start Docker!")
else
	@echo "Docker is running"
endif
endif


.PHONY: validate-pypirc
validate-pypirc:
ifneq ("$(wildcard $(PROJECT_HOME)/.pypirc)", "")
PYPIRC_PATH := $(PROJECT_HOME)/.pypirc
else
ifneq ("$(wildcard $(PROJECT_CONFIG_HOME)/.pypirc)", "")
PYPIRC_PATH := $(PROJECT_CONFIG_HOME)/.pypirc
else
ifneq ("$(wildcard $(HOME)/.pypirc)", "")
PYPIRC_PATH := $(HOME)/.pypirc
else
	$(error "Unable to find '.pypirc' in '$(PROJECT_HOME)', '$(PROJECT_CONFIG_HOME)' or '$(HOME)'")
endif
endif
endif


.PHONY: validate-activated
validate-activated:
ifndef VIRTUAL_ENV
	$(error "Must be in an activated virtualenv.")
endif


.PHONY: validate-twine
validate-twine: validate-activated validate-pypirc
ifneq ($(shell command -v twine 2>&1>/dev/null; echo $$?), 0)
	$(error "Unable to fine 'twine'; has it been pip installed?"
else
	@echo "Python virtual environment is activated"
	@echo "Found '.pypirc' at: '$(PYPIRC_PATH)'"
endif


.PHONY: validate-pyenv
validate-pyenv:
ifneq ($(shell command -v pyenv 2>&1>/dev/null; echo $$?), 0)
	$(error "Unable to find pyenv. Install instructions: https://bit.ly/2q7BGQe")
else
	@echo "Found 'pyenv'"
endif

# ---- VALIDATION COMMANDS ----

.PHONY: docker-image
## Make the CI (Continuous Integration) Docker image
docker-image: validate-docker
	@echo IMAGE_NAME = '$(IMAGE_NAME)'
	cd tests; docker build --no-cache -t $(IMAGE_NAME) .;
	@echo Done
	@echo "\nRun the following command to get a shell in the container:\n"
	@echo "    docker run -ti $(IMAGE_NAME) bash\n"


.PHONY: clean
## Clean up build and test files
clean:
	rm -rf .coverage
	rm -rf .mypy_cache
	rm -rf .tox
	rm -rf build
	rm -rf dist
	rm -rf flutils.egg-info
	rm -rf htmlcov
	rm -rf docs/_build
	rm -rf out


.PHONY: docker-image-push
## Push the CI Docker image to GitLab
docker-image-push:
	@echo IMAGE_NAME = '$(IMAGE_NAME)'
	docker push $(IMAGE_NAME)
	@echo Done



.PHONY: docker-stop-containers
## Stop all running docker containers
docker-stop-containers: validate-docker
ifndef RUNNING_CONTAINERS
	@echo "No Docker containers to stop."
else
	docker stop $(RUNNING_CONTAINERS)
endif

.PHONY: docs
## Build the flutils docs
docs: validate-activated
	rm -rf docs/_build && cd docs && make html

.PHONY: docs-requirements
## Build/update the python requirements needed by the doc build server.
docs-requirements: validate-activated
	pipenv lock -r --dev > docs/requirements-docs.txt


.PHONY: help
## Show help
help:
# The following help code was modified from https://bit.ly/2D2e0oP
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${GREEN}%s${RESET}\n    %s\n\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)


.PHONY: pyenv-pythons
## Install the CPython versions with pyenv needed for development and testing
pyenv-pythons: validate-pyenv
	pyenv update
	tests/pyenv-install-cpython --no-pyenv-local 3.6 3.7 3.8
	@echo Done


.PHONY: sdist
## Build the flutils package for PyPi
sdist: validate-activated clean
	./setup.py sdist
	@echo Done


.PHONY: sdist-push
## Test, build and push the flutils package and push to pypi
sdist-push: export TWINE_USERNAME = $(TWINE_USER)
sdist-push: export TWINE_PASSWORD = $(TWINE_PASS)
sdist-push: validate-twine tests sdist
	twine upload --skip-existing dist/*
	@echo Done
	@echo "View package at: https://pypi.org/project/flutils/"


.PHONY: sdist-push-test
## Test, build and push the flutils package and push to test.pypi
sdist-push-test: export TWINE_USERNAME = $(TWINE_USER_TEST)
sdist-push-test: export TWINE_PASSWORD = $(TWINE_PASS_TEST)
sdist-push-test: validate-twine tests sdist
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ --skip-existing dist/*
	@echo Done
	@echo "View package at: https://test.pypi.org/project/flutils/"


.PHONY: tests
## Run the tests for each CPython version
tests:
	@rm -rf .coverage
	@rm -rf .mypy_cache
	@rm -rf .tox
	@rm -rf build
	@rm -rf dist
	@rm -rf flutils.egg-info
	@rm -rf htmlcov
	@rm -rf out
	PATH=$(PATH_NEW); tox
