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


## Usage (Local)

Set the required environment variables before running locally:

```
export OPENAI_API_KEY=sk-...
export SENDER_EMAIL=you@example.com
export SENDER_PASSWORD=app-password-or-smtp-password
export SMTP_SERVER=smtp.gmail.com
export PROMPTS_JSON='[{"name":"demo","model":"gpt-4","prompt":"Hello"}]'
export BCC_EMAILS='ops@example.com'
```

### Run locally (no Docker)
- Install deps (includes dev/pytest):
  - `cd openai_scheduled_newsletter_api && poetry install --with dev`
  - `cd ../openai_scheduled_newsletter_job && poetry install --with dev`
- Start API: `make run-api` (uvicorn on :8000)
- Run job once: `make run-job`
- Run tests: `make test` (or `./run_tests.sh`)

### Kubernetes secrets/config
- Secret (used by both API and Job): `openai-secrets` with keys `api-key`, `sender-email`, `sender-password`, `smtp-server` (see `openai_scheduled_newsletter_api/k8s/secret.yaml`).
- ConfigMap: `newsletter-config` with `prompts.json` and `bcc-emails` (see `openai_scheduled_newsletter_api/k8s/configmap.yaml`).

Apply your own values before deploying.

## Requirements
- Python 3.10+
- Poetry
- Dependencies: PyYAML, requests

## License
MIT

