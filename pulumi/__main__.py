"""An Azure RM Python Pulumi program"""

import pulumi
from pulumi_azure_native import storage
from pulumi_azure_native import resources
from pulumi_azure_native import network
from pulumi_azure_native import containerservice

config = pulumi.Config("azure-native")
location = config.require("location")  # Reads from Pulumi.dev.yaml

# Create an Azure Resource Group
resource_group = resources.ResourceGroup("resource_group", location=location)

vnet = network.VirtualNetwork(
    "aks-vnet",
    resource_group_name=resource_group.name,
    location=location,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"]
    ),
)

aks_subnet = network.Subnet(
    "aks-subnet",
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
            vm_size="Standard_B2s",
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