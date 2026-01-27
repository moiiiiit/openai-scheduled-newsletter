import pulumi
import pulumi_auth0 as auth0

auth0_config = pulumi.Config("auth0")

app = auth0.Client(
    "openai-newsletter",
    name="OpenAI Newsletter API",
    description="Newsletter generation with per-user prompts",
    allowed_logout_urls=["https://newsletter-api.mohitbhole.net"],
    allowed_origins=["https://newsletter-api.mohitbhole.net"],
    app_type="regular_web",
    callbacks=["https://newsletter-api.mohitbhole.net/auth/callback"],
)

auth0_client_id = app.client_id

pulumi.export("auth0_client_id", auth0_client_id)
pulumi.export("auth0_domain", auth0_config.require("domain"))
