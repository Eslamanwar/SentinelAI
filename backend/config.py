from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM (OpenRouter)
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemini-2.5-flash"

    # Bright Data
    brightdata_api_key: str = ""
    brightdata_serp_api_url: str = "https://api.brightdata.com/serp/req"
    brightdata_serp_zone: str = "sentinel_serp"
    brightdata_web_unlocker_url: str = "https://api.brightdata.com/request"
    brightdata_unlocker_zone: str = "sentinel_serp"
    brightdata_scraping_browser_ws: str = ""
    brightdata_mcp_server_url: str = ""

    # Infrastructure
    kafka_bootstrap_servers: str = "kafka:29092"
    database_url: str = "postgresql://sentinel:sentinel@postgres:5432/sentinel"

    # Integrations
    slack_webhook_url: str = ""
    jira_base_url: str = ""
    jira_api_token: str = ""
    jira_project_key: str = "SENT"

    # Environment
    kubeconfig_path: str = "./environment/sample-kubeconfig.yaml"
    terraform_state_path: str = "./environment/sample-terraform.tfstate"
    vendor_inventory_path: str = "./environment/sample-vendors.json"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
