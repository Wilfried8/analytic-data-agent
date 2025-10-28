## Terraform State Notes

### Backend
- Environment: `infra/terraform/envs/uat`
- Backend: Google Cloud Storage bucket `terraform-state-analytics-agent`, prefix `dev/default.tfstate`
- Locking: relies on GCS object locking; avoid parallel `terraform apply` runs

### Current Resources Tracked
- Project services:
  - `run.googleapis.com`
  - `iam.googleapis.com`
  - `geminidataanalytics.googleapis.com`
  - `bigquery.googleapis.com`
- Imported resources (ensure these stay in state):
  - Service account `analytics-agent-run-dev@poc-analytics-conversationel.iam.gserviceaccount.com`
  - IAM project bindings on that service account (`roles/run.invoker`, `roles/bigquery.dataViewer`, `roles/bigquery.user`, `roles/aiplatform.user`, `roles/iam.serviceAccountUser`)
  - Cloud Run service `analytics-agent-dev` in `europe-west1`

### Import Snippets
```bash
# Service account
terraform import \
  'module.run_service_account.google_service_account.this' \
  projects/poc-analytics-conversationel/serviceAccounts/analytics-agent-run-dev@poc-analytics-conversationel.iam.gserviceaccount.com

# IAM role bindings
ROLE=roles/run.invoker  # adjust per role
terraform import \
  "module.run_service_account.google_project_iam_member.service_account_roles[\"${ROLE}\"]" \
  projects/poc-analytics-conversationel/roles/${ROLE}/members/serviceAccount:analytics-agent-run-dev@poc-analytics-conversationel.iam.gserviceaccount.com

# Cloud Run service
terraform import \
  'module.cloud_run_service.google_cloud_run_v2_service.this' \
  projects/poc-analytics-conversationel/locations/europe-west1/services/analytics-agent-dev
```

### Recommended Workflow
1. `make terraform-init`
2. `terraform state list` (confirm tracked resources)
3. `make terraform-plan` and review output
4. `make terraform-apply` only after plan approval
5. Post-apply: `terraform state pull > state-backup-$(date +%Y%m%d%H%M).json` (optional backup)

### Drift & Safety Checks
- Run `make terraform-plan` regularly; investigate any unexpected changes
- If a resource appears outside state, import it before applying changes
- Keep this file updated whenever new resources are imported or the backend changes
