"""Configuration management for the Pulumi stack"""

import pulumi

# Azure configuration
azure_config = pulumi.Config("azure-native")
location = azure_config.require("location")
subscription_id = azure_config.require("subscription_id")

# Application configuration
app_config = pulumi.Config()
openai_api_key = app_config.require_secret("openai_api_key")
sender_email = app_config.require("sender_email")
sender_password = app_config.require_secret("sender_password")
smtp_server = app_config.get("smtp_server") or "smtp.gmail.com"
prompts_json = app_config.get("prompts_json") or '[{"name":"demo","model":"gpt-4","prompt":"Test"}]'
bcc_emails = app_config.get("bcc_emails") or "ops@example.com"
