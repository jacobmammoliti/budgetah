IMAGE_NAME  ?= budgetah-mcp
IMAGE_TAG   ?= latest
PYTHON_VERSION := $(shell cat .python-version)
APP_VERSION := $(shell grep '^version' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
CONTAINER_REGISTRY = harbor.sourpatch.internal.coldbrewlabs.ca/library

.PHONY: build print-%

print-%:
	@echo $($*)

build:
	podman build \
	--build-arg UV_IMAGE=astral/uv:python$(PYTHON_VERSION)-trixie-slim \
	--build-arg PYTHON_RUN_IMAGE=docker.io/library/python:$(PYTHON_VERSION)-slim-trixie \
	-t $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION) .

push:
	podman push $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION)

build-curated:
	podman build \
	--build-arg UV_IMAGE=astral/uv:python$(PYTHON_VERSION)-trixie-slim \
	--build-arg PYTHON_RUN_IMAGE=quay.io/rfcurated/python:$(PYTHON_VERSION)-runtime-noble-rfcurated \
	-t $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION)-rfcurated .

build-curated-scratch:
	podman build \
	--build-arg UV_IMAGE=astral/uv:python$(PYTHON_VERSION)-trixie-slim \
	--build-arg PYTHON_RUN_IMAGE=quay.io/rfcurated/python:$(PYTHON_VERSION)-runtime-noble-scratch-rfcurated \
	-t $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION)-scratch-rfcurated .

push-curated-scratch:
	podman push $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION)-scratch-rfcurated

build-google-distroless:
	podman build \
	--build-arg UV_IMAGE=astral/uv:python$(PYTHON_VERSION)-trixie-slim \
	--build-arg PYTHON_RUN_IMAGE=gcr.io/distroless/python3-debian13:nonroot \
	-t $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION)-distroless .