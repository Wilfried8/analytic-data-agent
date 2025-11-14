PROJECT_ID ?= poc-analytics-conversationel
REGION     ?= europe-west1
REPO       ?= analytics-agents-dev
IMAGE_NAME ?= analytics-agent
TAG        ?= dev-$(shell date +%Y%m%d-%H%M%S)

.PHONY: help run lint test terraform-init terraform-plan terraform-apply terraform-destroy cloudbuild

help:
	@echo "  make run               - Run FastAPI app locally"
	@echo "  make lint              - Run code linters (ruff)"
	@echo "  make test              - Run unit tests (pytest)"
	@echo "  make terraform-init    - terraform init for UAT"
	@echo "  make terraform-plan    - terraform plan for UAT"
	@echo "  make terraform-apply   - terraform apply for UAT"
	@echo "  make terraform-destroy - terraform destroy for UAT"
	@echo "  make cloudbuild        - Run Cloud Build to build & push image"
run:
	@uv run uvicorn app.api:app --host 0.0.0.0 --port 8080

lint:
	@uv run ruff check .

test:
	@uv run pytest

streamlit:
	@streamlit run ui/dtreamlit_app.py

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
		--substitutions _ENV=$(TAG),_REGION=$(REGION),_REPO=$(REPO),_TF_ENV=uat
