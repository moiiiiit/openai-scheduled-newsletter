"""Azure infrastructure resources"""

import pulumi
from pulumi_azure_native import resources, network, containerservice, authorization
from config import location, subscription_id
from acr import create_acr

# Resource Group
resource_group = resources.ResourceGroup("resource_group", location=location)

# Azure Container Registry
acr, acr_admin_username, acr_admin_password = create_acr(resource_group)

# Virtual Network
vnet = network.VirtualNetwork(
    "openai-newsletter-vnet",
    resource_group_name=resource_group.name,
    location=location,
    address_space=network.AddressSpaceArgs(address_prefixes=["10.0.0.0/16"]),
)

# AKS Subnet
aks_subnet = network.Subnet(
    "openai-newsletter-subnet",
    resource_group_name=resource_group.name,
    virtual_network_name=vnet.name,
    address_prefix="10.0.1.0/24"
)

# AKS Cluster
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

# Get kubeconfig
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

# Get kubelet identity for ACR pull role
cluster_details = containerservice.get_managed_cluster_output(
    resource_group_name=resource_group.name,
    resource_name=aks.name,
)


def get_kubelet_principal_id(profile):
    if not profile or "kubeletidentity" not in profile:
        return None
    kubelet = profile["kubeletidentity"]
    return (
        kubelet.get("object_id") or 
        kubelet.get("objectId") or 
        kubelet.get("principal_id") or 
        kubelet.get("principalId") or
        kubelet.get("client_id") or
        kubelet.get("clientId")
    )


kubelet_principal_id = cluster_details.identity_profile.apply(get_kubelet_principal_id)

# ACR Pull role assignment
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

# Exports
pulumi.export("resource_group_name", resource_group.name)
pulumi.export("vnet_id", vnet.id)
pulumi.export("aks_subnet_id", aks_subnet.id)
pulumi.export("aks_cluster_name", aks.name)
pulumi.export("kubeconfig", pulumi.Output.secret(kubeconfig))
pulumi.export("kubelet_identity_profile", cluster_details.identity_profile)
pulumi.export("kubelet_principal_id", kubelet_principal_id)
pulumi.export("acr_pull_role_id", acr_pull_role.id)
