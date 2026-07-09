IMAGE_NAME  ?= budgetah-frontend
IMAGE_TAG   ?= latest
NODE_VERSION := 24.18
APP_VERSION := $(shell grep '"version"' package.json | head -1 | sed 's/.*"version": "\(.*\)".*/\1/')
CONTAINER_REGISTRY = harbor.sourpatch.internal.coldbrewlabs.ca/library

.PHONY: build print-%

print-%:
	@echo $($*)

build:
	podman build \
	--build-arg NODE_BUILD_IMAGE=docker.io/node:${NODE_VERSION}-trixie \
	--build-arg NODE_RUN_IMAGE=docker.io/node:${NODE_VERSION}-trixie-slim \
	-t $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION) .

push:
	podman push $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION)

build-curated:
	podman build \
	--build-arg NODE_BUILD_IMAGE=quay.io/rfcurated/node:${NODE_VERSION}-noble-rfcurated \
	--build-arg NODE_RUN_IMAGE=quay.io/rfcurated/node:${NODE_VERSION}-noble-rfcurated \
	-t $(IMAGE_NAME):$(APP_VERSION)-rfcurated .

build-curated-scratch:
	podman build \
	--build-arg NODE_BUILD_IMAGE=quay.io/rfcurated/node:${NODE_VERSION}-noble-rfcurated \
	--build-arg NODE_RUN_IMAGE=quay.io/rfcurated/node:${NODE_VERSION}-noble-scratch-rfcurated \
	-t $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION)-scratch-rfcurated .

push-curated-scratch:
	podman push $(CONTAINER_REGISTRY)/$(IMAGE_NAME):$(APP_VERSION)-scratch-rfcurated