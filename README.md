## anlytic-data-agent

Tooling and scripts to manage a Gemini Data Analytics agent backed by BigQuery tables for the senior residence use case.

> Production deployment guidance is available in `docs/deployment.md`.

### Prerequisites
- Python 3.11+
- `uv` (recommended) or `pip`
- Google Cloud project with Gemini Data Analytics API enabled
- Service account JSON key with access to BigQuery and Gemini Data Analytics

### Setup
1. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Copy the configuration template and fill in your values:
   ```bash
   cp .env.example .env
   ```
4. Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to your service account key.

### Scripts
- `scripts/create_agent.py` – creates or fetches the configured data agent.
- `scripts/delete_agent.py` – requests deletion of the configured data agent.
- `scripts/chat.py` – interactive or scripted conversations with the deployed agent.
- `scripts/inspect_agents.py` – inspect a single agent or list all agents in the project/location.

Run scripts via `uv run python scripts/<script>.py` after activating the virtual environment.

### FastAPI service
- Local launch: `uv run uvicorn app.api:app --reload --host 0.0.0.0 --port 8080`
- Health check: `GET http://localhost:8080/healthz`
- Ensure the agent exists: `POST http://localhost:8080/agent/sync`
- Ask a question: `POST http://localhost:8080/chat` with payload `{"question": "..."}`

### Container build & deploy

- Avec le Makefile (recommandé) :
  1. `make build TAG=uat-$(date +%Y%m%d-%H%M%S)`
  2. `make push TAG=uat-...`
  3. (Optionnel) `make tag-latest TAG=uat-...`
  4. Mettre à jour `run_image` dans `infra/terraform/envs/<env>/terraform.tfvars`
  5. `make terraform-plan` puis `make terraform-apply`

- Via Cloud Build :
  ```bash
  make cloudbuild TAG=uat-$(date +%Y%m%d-%H%M%S)
  ```
  (ou `gcloud builds submit --config cloudbuild.yaml --substitutions _IMAGE_NAME=europe-west1-docker.pkg.dev/<project>/analytics-agent/analytics-agent:<tag>`)
