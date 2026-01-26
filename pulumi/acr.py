"""Azure Container Registry resources"""

import pulumi
from pulumi_azure_native import containerregistry
from config import location

def create_acr(resource_group):
    """Create Azure Container Registry"""
    acr = containerregistry.Registry(
        "openainewsletteracr",
        resource_group_name=resource_group.name,
        location=location,
        sku=containerregistry.SkuArgs(name="Basic"),
        admin_user_enabled=True
    )
    
    # Get ACR credentials
    acr_credentials = pulumi.Output.all(resource_group.name, acr.name).apply(
        lambda args: containerregistry.list_registry_credentials(
            resource_group_name=args[0],
            registry_name=args[1]
        )
    )
    
    acr_admin_username = acr_credentials.apply(lambda creds: creds.username)
    acr_admin_password = acr_credentials.apply(lambda creds: creds.passwords[0].value)
    
    # Exports
    pulumi.export("acr_login_server", acr.login_server)
    pulumi.export("acr_name", acr.name)
    pulumi.export("acr_admin_username", acr_admin_username)
    pulumi.export("acr_admin_password", pulumi.Output.secret(acr_admin_password))
    
    return acr, acr_admin_username, acr_admin_password
