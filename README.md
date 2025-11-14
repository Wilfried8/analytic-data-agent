# Analytics Data Agent

FastAPI + Streamlit tooling to pilot a Gemini Data Analytics agent backed by BigQuery
tables for the residence use case. The repo also ships Terraform modules to
deploy the API on Cloud Run together with a run-time service account.

## Repository layout

| Path | Description |
| --- | --- |
| `app/` | FastAPI service, agent helpers, and configuration primitives. |
| `ui/` | Streamlit sandbox used to call the REST API quickly (health, agent management, chat). |
| `scripts/` | CLI utilities for creating, deleting, chatting with, or inspecting agents. |
| `infra/terraform/` | Reusable Terraform modules + `envs/uat` environment used for Cloud Run. |
| `tests/` | Unit tests (pytest) covering helpers such as datasource wiring. |

## Prerequisites

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) (preferred) or `pip`
- Google Cloud project with **Gemini Data Analytics**, **Cloud Run**, **BigQuery**, **IAM**
  APIs enabled
- Service account key allowed to access BigQuery tables and Gemini Data Analytics (only
  needed for local runs; Cloud Run uses the workload identity provisioned by Terraform)

## Initial setup

```bash
uv venv
source .venv/bin/activate
uv sync               # install dependencies
cp .env.example .env  # edit with your project, dataset, table names, etc.
```

Required environment variables are documented in `.env.example`; the FastAPI app reads
them via `app.config.load_settings`. At minimum you must provide:

- `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_CLOUD_DATASET`, `GOOGLE_CLOUD_TABLE_RESIDENTS`, `GOOGLE_CLOUD_TABLE_FACTURATIONS`
- `DATA_AGENT_ID` (default fallback identifier)
- `SYSTEM_INSTRUCTION_PATH` (defaults to `system_instruction.yml`)
- `GOOGLE_APPLICATION_CREDENTIALS` when running locally

The Streamlit UI also uses `AGENT_API_URL` to target your deployed API.

## Local development

- **Run the API**: `make run` (alias for `uv run uvicorn app.api:app --host 0.0.0.0 --port 8080`).
- **Streamlit sandbox**: `streamlit run ui/dtreamlit_app.py` (lets you ping `/health`,
  create/list/delete agents, and test `/chat` end-to-end).
- **Lint**: `make lint` (ruff).
- **Tests**: `make test` (pytest).
- **Manual scripts** (after sourcing the venv):
  ```bash
  uv run python scripts/create_agent.py        # create or update DATA_AGENT_ID
  uv run python scripts/delete_agent.py --id <agent_id>
  uv run python scripts/chat.py --question "..." --conversation-id optional
  uv run python scripts/inspect_agents.py
  uv run python scripts/validate_env.py        # sanity-check required env vars
  ```

## API surface (FastAPI)

- `GET /health` – readiness probe
- `GET /agent` – fetch the currently configured agent (using `DATA_AGENT_ID`)
- `GET /agents` – list every agent in `project_id/location`
- `POST /agent` – create an agent; accepts optional body `{"data_agent_id": "custom-id"}`
- `PUT /agent` – update the existing agent definition
- `DELETE /agent/{agent_id}` – delete by id (supports `?force=true`)
- `POST /chat` – ask questions (`{"question": "...", "conversation_id": "...", "preview": bool}`)

All routes rely on the settings resolved at process start, so redeploy Cloud Run after
changing environment variables or pushing new code.

## Container build & deployment

1. Build & push an image (local or Cloud Build):
   ```bash
   TAG=dev-$(date +%Y%m%d-%H%M%S)
   gcloud builds submit --config cloudbuild.yaml \
     --substitutions _ENV=${TAG},_REGION=europe-west1,_REPO=analytics-agents-dev
   ```
   or create/push manually with your preferred workflow, then update
   `infra/terraform/envs/uat/terraform.tfvars:run_image`.
2. Update `infra/terraform/envs/uat/terraform.tfvars` with the new image tag if needed.
3. Provision/upgrade infrastructure:
   ```bash
   make terraform-init
   make terraform-plan
   make terraform-apply
   ```
   Terraform takes care of enabling APIs, creating the run-time service account, and
   deploying the Cloud Run service with the environment variables specified in
   `run_env_vars`.
4. The Streamlit UI (or any other client) can now interact with the Cloud Run URL
   exposed by Terraform outputs.

Refer to `STATE.md` for the authoritative view of the Terraform backend, tracked
resources, and import commands.
