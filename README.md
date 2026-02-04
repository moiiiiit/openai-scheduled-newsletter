# OpenAI Scheduled Newsletter

Most likely deployed here: https://newsletter-api.mohitbhole.net/docs (Reach out if interested in seeing demo and app is offline)
This project generates a scheduled technical digest of 'anything' using OpenAI's API. Realistically, this project is more of a scaffold-style application for me to learn AWS/Azure services, and setting up all the platform and orchestration for a hybrid application. Hence the 'overengineering' with API, Auth0, database, AKS deployment for the API and ACI deployment for the scheduled job.

Started as a simple script to send a newsletter to my wife, evolved into a process for me to 0->1 a cloud-native web application.

### Why a Hybrid Approach?

The application is split between **Azure Kubernetes Service (AKS)** for the API and **Azure Container Instances (ACI)** for the scheduled job because:

1. **Cost Efficiency** – The scheduled job runs periodically (not continuously), so ACI charges only for execution time (~$2/month) rather than maintaining a full Kubernetes cluster 24/7.
2. **Separation of Concerns** – The API and job are independent workloads with different patterns: the API needs constant availability and auto-scaling, while the job runs on a schedule and exits.
3. **Scalability** – Each component scales independently. The API can handle traffic spikes without affecting job execution, and vice versa.
4. **Learning & Growth** – This architecture supports future additions: adding a database, message queues, or additional services becomes cleaner with separated components. Ideally, because databases and cache storage are stateful, for production ready applications, it would be benefitial to use cloud native services like Azure DB (or Azure Psql) or Azure Cache. The other way is to use kubernetes operators with AKS or stateful sets, but this is more complex and requires specialized talent and knowledge in the workings of the databases.
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
- Secret (used by both API and Job): `openai-secrets` with keys `api-key`, `sender-email`, `sender-password`, `smtp-server`, `auth0-client-id`, `auth0-client-secret`, `auth0-domain`.
- ConfigMap: `newsletter-config` with `prompts.json` and `bcc-emails`.
- **Prompts are loaded from mounted file** (`/etc/config/prompts.json`), not environment variables, to avoid JSON escaping issues.
- **API is now public** (authentication handled by oauth2-proxy at ingress level, not Basic Auth).

## Requirements
- Python 3.10+
- Poetry
- Dependencies: PyYAML, requests

## Build and Deploy with Pulumi

Pulumi orchestrates the entire deployment: Azure infrastructure, Docker image builds, and Kubernetes resources.

### Prerequisites

1. **Azure CLI** logged in and subscription set
2. **Pulumi** installed
3. **Auth0 account** (free tier) with a Pulumi M2M (Machine-to-Machine) app created
4. **Docker daemon** running (for image builds via `pulumi-docker-build`)

### Pulumi Configuration

Set the required Pulumi secrets and config values:

```bash
cd pulumi

# Azure configuration
pulumi config set azure-native:location westus2
pulumi config set azure-native:subscription_id <your-subscription-id>

# Application configuration
pulumi config set openai_api_key <your-openai-api-key> --secret
pulumi config set sender_email your-email@gmail.com
pulumi config set sender_password <app-password-or-smtp-password> --secret
pulumi config set smtp_server smtp.gmail.com  # optional; defaults to gmail
pulumi config set prompts_json '[{"name":"EV Tech Weekly","model":"gpt-5","prompt":"..."}]'  # JSON array
pulumi config set bcc_emails "user1@example.com,user2@example.com"

# Auth0 configuration
# First, create a Pulumi M2M app in Auth0 and get its credentials
pulumi config set auth0:domain your-tenant.us.auth0.com
pulumi config set auth0:clientId <m2m-client-id> --secret
pulumi config set auth0:clientSecret <m2m-client-secret> --secret

# Auth0 client secret (from the OpenAI Newsletter app created by Pulumi)
# Retrieve from Auth0 dashboard after pulumi up creates the client
pulumi config set auth0_client_secret <client-secret-from-auth0-dashboard> --secret
```

### Deploy

```bash
cd pulumi
pulumi up --yes
```

This will:
- Create Azure infrastructure (VNet, AKS, ACR, etc.)
- Build Docker images for API and Job via `pulumi-docker-build`
- Push images to ACR
- Deploy to Kubernetes (API Deployment, CronJob, ConfigMaps, Secrets)
- Create Auth0 application for authentication

### Images Built Automatically

Pulumi uses `pulumi-docker-build` to build and push images. No manual `docker build` or `docker push` needed. The Dockerfiles are in:
- `openai_scheduled_newsletter_api/Dockerfile`
- `openai_scheduled_newsletter_job/Dockerfile`

The Dockerfiles copy the `shared/` directory during build, so run `pulumi up` from the repository root.

## API Endpoints

All endpoints are now public (authentication via oauth2-proxy at ingress):

- `GET /health` – Health check (no auth required)
- `GET /prompts` – List all prompts
- `POST /execute/{prompt_idx}` – Execute prompt by index (runs async in background)

Swagger docs available at `GET /docs` (once oauth2-proxy is deployed).

## Scheduled Job (CronJob)

The job runs via Kubernetes CronJob on a schedule (default: 8 AM UTC = 2 AM CST). Update `openai_scheduled_newsletter_job/k8s/cronjob.yaml`:

```yaml
spec:
  schedule: "0 14 * * *"  # Change to run at a different time (e.g., 2 PM UTC for 8 AM CST)
  timeZone: "America/Chicago"  # Kubernetes 1.27+ supports timeZone
```

Redeploy: `pulumi up --yes`

## Authentication (oauth2-proxy + Auth0)

**In Progress:** oauth2-proxy deployment (sits in front of API, redirects unauthenticated requests to Auth0).

For now, the API is public. Will be gated by Auth0 authentication once oauth2-proxy is deployed.

## Architecture

- **API**: FastAPI on AKS (Kubernetes Deployment, HTTPS via Let's Encrypt + NGINX Ingress)
- **Scheduled Job**: Python CLI on AKS (Kubernetes CronJob, runs on schedule)
- **Data**: Azure Container Registry (Docker images), Kubernetes ConfigMaps/Secrets
- **Auth**: Auth0 (OIDC provider) + oauth2-proxy (in progress)
- **IaC**: Pulumi (Python, manages Azure + Kubernetes resources)

## License
MIT

