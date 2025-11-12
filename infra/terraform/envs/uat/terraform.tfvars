project_id = "poc-analytics-conversationel"
region     = "europe-west1"
# run_image  = "europe-west1-docker.pkg.dev/poc-analytics-conversationel/analytics-agents-dev/analytics-agent:dev-20251028-163057"
# run_image  = "europe-west1-docker.pkg.dev/poc-analytics-conversationel/analytics-agents-dev/analytics-agent:dev-20251103-175022"
run_image = "europe-west1-docker.pkg.dev/poc-analytics-conversationel/analytics-agents-dev/analytics-agent:dev-20251112-155910"

run_env_vars = {
  GOOGLE_CLOUD_PROJECT            = "poc-analytics-conversationel"
  GOOGLE_CLOUD_DATASET            = "test_demo"
  GOOGLE_CLOUD_TABLE_RESIDENTS    = "residents"
  GOOGLE_CLOUD_TABLE_FACTURATIONS = "facturations"
  DATA_AGENT_ID                   = "senior_residence_analytics_agent-dev"
}
