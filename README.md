# Deepseek Daily Newsletter

This project generates a weekly technical digest of Electric Vehicle (EV) technology news using Deepseek's API.

## Features
- Fetches global EV news and trends
- Uses Deepseek API and custom prompts
- Sends results via email


## Usage
To use your own API key locally without committing secrets to version control, create a file called `secrets.yaml` in the `k8s/` directory with the following format:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: deepseek-email-secrets
data:
  DEEPSEEK_API_KEY: 
  SENDER_EMAIL_APP_PASSWORD: 
  SENDER_EMAIL: 
  EMAILS_JSON: 
  PROMPTS_JSON: 
  SMTP_SERVER:
  SMTP_PORT: 

```

Replace `<b64 encoded api key>` with your base64-encoded Deepseek API key. For example, to encode your key:

```bash
echo -n "sk-your-api-key-here" | base64
```

Then copy the output into the YAML file.
1. Configure your API key, prompts, emails (and base64 encode the strings) in your Kubernetes secret or `.env` file.
2. Use the Makefile for common development and deployment tasks:

### Common Makefile Targets

- `make install` – Install Docker, MicroK8s, and dependencies (run once per machine)
- `make build` – Build and push the Docker image to the local MicroK8s registry
- `make apply-local-secret` – Apply your local secret (with API key) to the cluster
- `make apply-manifests` – Apply all Kubernetes manifests (deployment, service, secrets)
- `make run` – Build, apply secrets, and deploy everything (full workflow)
- `make cleanup-pods` – Scale down and remove newsletter pods/deployment
- `make purge` – Remove MicroK8s registry data
- `make uninstall` – Uninstall MicroK8s and clean up all related data

### Example Workflow

```bash
# 1. Install dependencies (first time only)
make install

# 2. Build and deploy
make run

# 3. Clean up pods (optional)
make cleanup-pods
```

See the `Makefile` for more details and advanced usage.

## Requirements
- Python 3.10+
- Poetry
- Dependencies: PyYAML, requests

## License
MIT
