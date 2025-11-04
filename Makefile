PROJECT_ID ?= poc-analytics-conversationel
REGION     ?= europe-west1
REPO       ?= analytics-agents-dev
IMAGE_NAME ?= analytics-agent
TAG        ?= dev-$(shell date +%Y%m%d-%H%M%S)
# TAG        ?= dev
IMAGE_URI  ?= $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO)/$(IMAGE_NAME):$(TAG)
LATEST_URI ?= $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO)/$(IMAGE_NAME):latest

.PHONY: help build push tag-latest run lint test terraform-init terraform-plan terraform-apply terraform-destroy cloudbuild

help:
	@echo "Available targets:"
	@echo "  make build             - Build Docker image tagged with timestamp"
	@echo "  make push              - Configure Docker auth and push image"
	@echo "  make tag-latest        - Tag/push image as latest"
	@echo "  make run               - Run FastAPI app locally"
	@echo "  make lint              - Run code linters (ruff)"
	@echo "  make test              - Run unit tests (pytest)"
	@echo "  make terraform-init    - terraform init for UAT"
	@echo "  make terraform-plan    - terraform plan for UAT"
	@echo "  make terraform-apply   - terraform apply for UAT"
	@echo "  make terraform-destroy - terraform destroy for UAT"
	@echo "  make cloudbuild        - Run Cloud Build to build & push image"

build:
	@docker build -t $(IMAGE_URI) .

push:
	@gcloud auth configure-docker $(REGION)-docker.pkg.dev --quiet
	@docker push $(IMAGE_URI)

tag-latest:
	@docker tag $(IMAGE_URI) $(LATEST_URI)
	@docker push $(LATEST_URI)

run:
	@uv run uvicorn app.api:app --host 0.0.0.0 --port 8080

lint:
	@uv run ruff check .

test:
	@uv run pytest

terraform-init:
	@cd infra/terraform/envs/uat && terraform init -backend-config=backend.tfvars

terraform-plan:
	@cd infra/terraform/envs/uat && terraform plan -var-file=terraform.tfvars

terraform-apply:
	@cd infra/terraform/envs/uat && terraform apply -var-file=terraform.tfvars

terraform-destroy:
	@cd infra/terraform/envs/uat && terraform destroy -var-file=terraform.tfvars

cloudbuild-dev:
	@gcloud builds submit \
		--config cloudbuild.yaml \
		--substitutions _ENV=$(TAG),_REGION=$(REGION),_REPO=$(REPO)
