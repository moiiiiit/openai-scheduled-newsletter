# OpenAI Scheduled Newsletter

This project generates a scheduled technical digest of 'anything' using OpenAI's API. Realistically, this project is more of a scaffold-style application for me to learn AWS/Azure services, and setting up all the platform and orchestration for a hybrid application. Hence the 'overengineering' with API, (eventually) database, AKS deployment for the API and ACI deployment for the scheduled job.

### Why a Hybrid Approach?

The application is split between **Azure Kubernetes Service (AKS)** for the API and **Azure Container Instances (ACI)** for the scheduled job because:

1. **Cost Efficiency** – The scheduled job runs periodically (not continuously), so ACI charges only for execution time (~$2/month) rather than maintaining a full Kubernetes cluster 24/7.
2. **Separation of Concerns** – The API and job are independent workloads with different patterns: the API needs constant availability and auto-scaling, while the job runs on a schedule and exits.
3. **Scalability** – Each component scales independently. The API can handle traffic spikes without affecting job execution, and vice versa.
4. **Learning & Growth** – This architecture supports future additions: adding a database, message queues, or additional services becomes cleaner with separated components.
5. **Production-Ready Pattern** – This mirrors real-world microservices architectures where specialized services are deployed on platforms optimized for their workload patterns. 



## Features
- Uses OpenAI API and custom prompts
- Sends results via email


## Usage
To use your own API key locally without committing secrets to version control, create a file called `secrets.yaml` in the `k8s/` directory with the following format:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openai-email-secrets
data:
  OPENAI_API_KEY: 
  SENDER_EMAIL_APP_PASSWORD: 
  SENDER_EMAIL: 
  EMAILS_JSON: 
  SMTP_SERVER:
  SMTP_PORT: 
stringData:
  PROMPTS_JSON: 

```

Replace `<b64 encoded api key>` with your base64-encoded OpenAI API key. For example, to encode your key:

```bash
echo -n "sk-your-api-key-here" | base64
```

Then copy the output into the YAML file.
1. Configure your API key, prompts, emails (and base64 encode the strings) in your Kubernetes secret or `.env` file.
2. Use the Makefile for common development and deployment tasks:

### Common Makefile Targets (Local Development)

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

