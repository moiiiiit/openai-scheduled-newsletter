import pulumi
import pulumi_azure_native as azure

from config import location
from infrastructure import resource_group

cfg = pulumi.Config()
db_admin_password = cfg.require_secret("mysql_admin_password")

# MySQL Flexible Server
mysql_server = azure.dbformysql.Server(
    "newsletter-mysql",
    resource_group_name=resource_group.name,
    server_name="newsletter-mysql-srv",
    location=location,
    sku={
        "name": "Standard_D2ds_v4",
        "tier": azure.dbformysql.ServerSkuTier.GENERAL_PURPOSE,
    },
    storage=azure.dbformysql.StorageArgs(
        storage_size_gb=5,
    ),
    version=azure.dbformysql.ServerVersion.SERVER_VERSION_5_7,
    administrator_login="mysqladmin",
    administrator_login_password=db_admin_password,
    backup=azure.dbformysql.BackupArgs(
        backup_retention_days=7,
        geo_redundant_backup="Disabled",
    ),
    high_availability=azure.dbformysql.HighAvailabilityArgs(
        mode="Disabled",
    ),
)

# Firewall rule to allow Azure services
azure.dbformysql.FirewallRule(
    "allow-azure-services",
    resource_group_name=resource_group.name,
    server_name=mysql_server.name,
    firewall_rule_name="AllowAllAzureIps",
    start_ip_address="0.0.0.0",
    end_ip_address="0.0.0.0",
)

# Create the database
mysql_db = azure.dbformysql.Database(
    "newsletter-db",
    resource_group_name=resource_group.name,
    server_name=mysql_server.name,
    database_name="newsletter",
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci",
)

# Connection string
db_connection_string = pulumi.Output.all(
    mysql_server.fully_qualified_domain_name,
    db_admin_password
).apply(
    lambda args: f"mysql://mysqladmin:{args[1]}@{args[0]}:3306/newsletter?ssl-mode=REQUIRED"
)

pulumi.export("mysql_server_name", mysql_server.name)
pulumi.export("mysql_fqdn", mysql_server.fully_qualified_domain_name)
pulumi.export("db_connection_string", pulumi.Output.secret(db_connection_string))
