## Terraform State Reference

### Backend
- Working directory: `infra/terraform/envs/uat`
- Remote backend: Google Cloud Storage bucket **`terraform-state-analytics-agent`**
  with prefix **`dev`** (see `backend.tfvars`)
- No additional locking mechanism is configured, so avoid concurrent
  `terraform apply` executions

### Expected configuration

`terraform.tfvars` pins the current runtime to:

| Variable | Value |
| --- | --- |
| `project_id` | `poc-analytics-conversationel` |
| `region` | `europe-west1` |
| `run_service_name` | `analytics-agent-dev` |
| `run_service_account_id` | `analytics-agent-run-dev` |
| `run_image` | `europe-west1-docker.pkg.dev/poc-analytics-conversationel/analytics-agents-dev/analytics-agent:dev-20251112-155910` |

`run_env_vars` sets the FastAPI configuration (dataset/tables, default `DATA_AGENT_ID`,
etc.). Update those values before applying if the backend should change.

### Resources that must stay in state

1. `module.project_services` – enables the required APIs:
   `run.googleapis.com`, `iam.googleapis.com`, `geminidataanalytics.googleapis.com`,
   `bigquery.googleapis.com`.
2. `module.run_service_account`
   - Service account:
     `analytics-agent-run-dev@poc-analytics-conversationel.iam.gserviceaccount.com`
   - IAM bindings applied at project level. Expected roles:
     `roles/run.invoker`, `roles/bigquery.dataViewer`, `roles/bigquery.user`,
     `roles/aiplatform.user`, `roles/iam.serviceAccountUser`,
     `roles/cloudaicompanion.user`, `roles/owner`.
3. `module.cloud_run_service`
   - Cloud Run v2 service `analytics-agent-dev` in `europe-west1`
   - Deployed with the image referenced above and the environment variables from
     `run_env_vars`

If a resource drifts out of state (imported manually, renamed in the console, etc.)
re-import it before the next apply.

### Import helpers

```bash
# Service account
terraform import \
  'module.run_service_account.google_service_account.this' \
  projects/poc-analytics-conversationel/serviceAccounts/analytics-agent-run-dev@poc-analytics-conversationel.iam.gserviceaccount.com

# IAM bindings (iterate ROLE over the list above)
ROLE=roles/run.invoker
terraform import \
  "module.run_service_account.google_project_iam_member.service_account_roles[\"${ROLE}\"]" \
  "projects/poc-analytics-conversationel/roles/${ROLE}/members/serviceAccount:analytics-agent-run-dev@poc-analytics-conversationel.iam.gserviceaccount.com"

# Cloud Run service
terraform import \
  'module.cloud_run_service.google_cloud_run_v2_service.this' \
  projects/poc-analytics-conversationel/locations/europe-west1/services/analytics-agent-dev
```

### Recommended workflow

1. `make terraform-init`
2. `terraform state list` (quick sanity check)
3. `make terraform-plan` and review
4. `make terraform-apply` once the plan is approved
5. Optional backup: `terraform state pull > state-backup-$(date +%Y%m%d%H%M).json`

### Drift & safety checks

- Run `make terraform-plan` regularly or after console changes.
- If a command fails due to missing resources, use the import snippets above and re-run.
- Update this file whenever the backend (bucket/prefix), project, region, service name,
  or IAM role set changes so future operators know what should exist.
