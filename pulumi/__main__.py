"""An Azure RM Python Pulumi program"""

import pulumi
from pulumi_azure_native import storage
from pulumi_azure_native import resources
from pulumi_azure_native import network
from pulumi_azure_native import containerservice
from pulumi_azure_native import containerregistry
from pulumi_azure_native import authorization
from pulumi_kubernetes import Provider
from pulumi_kubernetes.core.v1 import Secret, ConfigMap
from pulumi_kubernetes.yaml import ConfigFile
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from pulumi_kubernetes.core.v1 import Namespace

config = pulumi.Config("azure-native")
location = config.require("location")
subscription_id = config.require("subscription_id")

resource_group = resources.ResourceGroup("resource_group", location=location)

acr = containerregistry.Registry(
    "openainewsletteracr",
    resource_group_name=resource_group.name,
    location=location,
    sku=containerregistry.SkuArgs(
        name="Basic"
    ),
    admin_user_enabled=True
)

pulumi.export("acr_login_server", acr.login_server)
pulumi.export("acr_name", acr.name)

vnet = network.VirtualNetwork(
    "openai-newsletter-vnet",
    resource_group_name=resource_group.name,
    location=location,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"]
    ),
)

aks_subnet = network.Subnet(
    "openai-newsletter-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24"
)

pulumi.export("resource_group_name", resource_group.name)
pulumi.export("vnet_id", vnet.id)
pulumi.export("aks_subnet_id", aks_subnet.id)

aks = containerservice.ManagedCluster(
    "openai-newsletter-aks",
    resource_group_name=resource_group.name,
    location=location,
    dns_prefix="openai-newsletter-aks",

    identity=containerservice.ManagedClusterIdentityArgs(
        type=containerservice.ResourceIdentityType.SYSTEM_ASSIGNED
    ),

    agent_pool_profiles=[
        containerservice.ManagedClusterAgentPoolProfileArgs(
            name="agentpool",
            count=2,
            vm_size="Standard_B2s_v2",
            mode="System",
            vnet_subnet_id=aks_subnet.id,
        )
    ],

    network_profile=containerservice.ContainerServiceNetworkProfileArgs(
        network_plugin="azure",
        service_cidr="10.1.0.0/16",
        dns_service_ip="10.1.0.10",
    ),
)

pulumi.export("aks_cluster_name", aks.name)

creds = pulumi.Output.all(resource_group.name, aks.name).apply(
    lambda args: containerservice.list_managed_cluster_user_credentials(
        resource_group_name=args[0],
        resource_name=args[1]
    )
)


def parse_kubeconfig(creds_response):
    import base64

    raw_value = creds_response.kubeconfigs[0].value
    raw_bytes = raw_value if isinstance(raw_value, (bytes, bytearray)) else raw_value.encode("utf-8")
    return base64.b64decode(raw_bytes).decode("utf-8")


kubeconfig = creds.apply(parse_kubeconfig)

pulumi.export("kubeconfig", pulumi.Output.secret(kubeconfig))

# Create AcrPull role assignment only after kubelet identity is available
cluster_details = containerservice.get_managed_cluster_output(
    resource_group_name=resource_group.name,
    resource_name=aks.name,
)

kubelet_principal_id = cluster_details.identity_profile.apply(
    lambda profile: profile["kubeletidentity"].object_id if profile and "kubeletidentity" in profile else None
)

pulumi.export("kubelet_identity_profile", cluster_details.identity_profile)
pulumi.export("kubelet_principal_id", kubelet_principal_id)

acr_pull_role_definition_id = pulumi.Output.concat(
    "/subscriptions/", subscription_id,
    "/providers/Microsoft.Authorization/roleDefinitions/",
    "7f951dda-4ed3-4680-a7ca-43fe172d538d"  # AcrPull
)
acr_pull_role = authorization.RoleAssignment(
    "openai-newsletter-aks-acr-pull",
    principal_id=kubelet_principal_id,
    principal_type="ServicePrincipal",
    role_definition_id=acr_pull_role_definition_id,
    scope=acr.id,
)
pulumi.export("acr_pull_role_id", acr_pull_role.id)

k8s_provider = Provider(
    "openai-newsletter-k8s-provider",
    kubeconfig=kubeconfig
)

app_config = pulumi.Config()
openai_api_key = app_config.require_secret("openai_api_key")
sender_email = app_config.require("sender_email")
sender_password = app_config.require_secret("sender_password")
smtp_server = app_config.get("smtp_server") or "smtp.gmail.com"
prompts_json = app_config.get("prompts_json") or '[{"name":"demo","model":"gpt-4","prompt":"Test"}]'
bcc_emails = app_config.get("bcc_emails") or "ops@example.com"

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

k8s_configmap = ConfigMap(
    "newsletter-config",
    metadata={"name": "newsletter-config"},
    data={
        "prompts.json": prompts_json,
        "bcc-emails": bcc_emails,
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Images in ACR
api_image = acr.login_server.apply(lambda s: f"{s}/api:latest")
job_image = acr.login_server.apply(lambda s: f"{s}/job:latest")


def set_images(obj, opts):
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


# Deploy API manifests (deployment, service, ingress)
api_deployment = ConfigFile(
    "api-deployment",
    file="../openai_scheduled_newsletter_api/k8s/deployment.yaml",
    transformations=[set_images],
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[k8s_secret, k8s_configmap])
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

# Deploy Job manifests (cronjob, service account)
job_cron = ConfigFile(
    "job-cron",
    file="../openai_scheduled_newsletter_job/k8s/cronjob.yaml",
    transformations=[set_images],
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[k8s_secret, k8s_configmap])
)

job_sa = ConfigFile(
    "job-serviceaccount",
    file="../openai_scheduled_newsletter_job/k8s/serviceaccount.yaml",
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[job_cron])
)

# Install NGINX Ingress Controller to handle Ingress resources
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
