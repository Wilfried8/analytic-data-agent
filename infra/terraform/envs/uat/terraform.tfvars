project_id = "poc-analytics-conversationel"
region     = "europe-west1"
run_image  = "gcr.io/poc-analytics-conversationel/analytics-agent:uat"

run_env_vars = {
  GOOGLE_CLOUD_PROJECT            = "poc-analytics-conversationel"
  GOOGLE_CLOUD_DATASET            = "test_demo"
  GOOGLE_CLOUD_TABLE_RESIDENTS    = "residents"
  GOOGLE_CLOUD_TABLE_FACTURATIONS = "facturations"
  DATA_AGENT_ID                   = "senior_residence_analytics_agent-uat"
}
