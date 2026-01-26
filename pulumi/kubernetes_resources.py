"""Kubernetes resources and workloads"""

import pulumi
from pulumi_kubernetes import Provider
from pulumi_kubernetes.core.v1 import Secret, ConfigMap, Namespace
from pulumi_kubernetes.yaml import ConfigFile
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from infrastructure import kubeconfig, acr, acr_admin_username, acr_admin_password, aks
from config import openai_api_key, sender_email, sender_password, smtp_server, prompts_json, bcc_emails
from docker_build import build_and_push_images

# Build and push Docker images first
api_image_resource, job_image_resource = build_and_push_images(acr, acr_admin_username, acr_admin_password)

# Kubernetes Provider
k8s_provider = Provider(
    "openai-newsletter-k8s-provider",
    kubeconfig=kubeconfig,
    opts=pulumi.ResourceOptions(depends_on=[aks])
)

# Kubernetes Secret
k8s_secret = Secret(
    "openai-newsletter-secrets",
    metadata={"name": "openai-secrets"},
    string_data={
        "api-key": openai_api_key,
        "sender-email": sender_email,
        "sender-password": sender_password,
        "smtp-server": smtp_server,
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Kubernetes ConfigMap
k8s_configmap = ConfigMap(
    "newsletter-config",
    metadata={"name": "newsletter-config"},
    data={
        "prompts.json": prompts_json,
        "bcc-emails": bcc_emails,
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Image names from ACR
api_image = acr.login_server.apply(lambda s: f"{s}/api:latest")
job_image = acr.login_server.apply(lambda s: f"{s}/job:latest")


def set_images(obj, opts):
    """Transformation function to set ACR image references"""
    kind = obj.get("kind")
    name = obj.get("metadata", {}).get("name")

    if kind == "Deployment" and name == "openai-newsletter-api":
        containers = obj.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
        for c in containers:
            c["image"] = api_image

    if kind == "CronJob" and name == "openai-newsletter-job":
        containers = obj.get("spec", {}).get("jobTemplate", {}).get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
        for c in containers:
            c["image"] = job_image

    return obj


# Deploy API manifests (depends on image being pushed)
api_deployment = ConfigFile(
    "api-deployment",
    file="../openai_scheduled_newsletter_api/k8s/deployment.yaml",
    transformations=[set_images],
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[k8s_secret, k8s_configmap, api_image_resource])
)

api_service = ConfigFile(
    "api-service",
    file="../openai_scheduled_newsletter_api/k8s/service.yaml",
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[api_deployment])
)

api_ingress = ConfigFile(
    "api-ingress",
    file="../openai_scheduled_newsletter_api/k8s/ingress.yaml",
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[api_service])
)

# Deploy Job manifests (depends on image being pushed)
job_cron = ConfigFile(
    "job-cron",
    file="../openai_scheduled_newsletter_job/k8s/cronjob.yaml",
    transformations=[set_images],
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[k8s_secret, k8s_configmap, job_image_resource])
)

job_sa = ConfigFile(
    "job-serviceaccount",
    file="../openai_scheduled_newsletter_job/k8s/serviceaccount.yaml",
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[job_cron])
)

# Install NGINX Ingress Controller
ingress_ns = Namespace(
    "ingress-nginx-namespace",
    metadata={"name": "ingress-nginx"},
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

ingress_controller = Chart(
    "ingress-nginx",
    ChartOpts(
        chart="ingress-nginx",
        version="4.10.0",
        namespace="ingress-nginx",
        fetch_opts=FetchOpts(
            repo="https://kubernetes.github.io/ingress-nginx",
        ),
        values={
            "controller": {
                "service": {
                    "type": "LoadBalancer"
                }
            }
        }
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[ingress_ns])
)
