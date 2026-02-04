"""Cert-manager installation and configuration"""

import pulumi
from pulumi_kubernetes.core.v1 import Namespace, ServiceAccount
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from pulumi_kubernetes.yaml import ConfigFile
from pulumi_kubernetes.batch.v1 import Job
from pulumi_kubernetes.rbac.v1 import ClusterRole, ClusterRoleBinding


def setup_cert_manager(k8s_provider):
    """
    Install cert-manager with proper wait logic to avoid race conditions.
    Returns the ClusterIssuer resource.
    """
    
    # Create cert-manager namespace
    cert_manager_ns = Namespace(
        "cert-manager-namespace",
        metadata={"name": "cert-manager"},
        opts=pulumi.ResourceOptions(provider=k8s_provider)
    )

    # Install cert-manager via Helm
    cert_manager = Chart(
        "cert-manager",
        ChartOpts(
            chart="cert-manager",
            version="v1.14.4",
            namespace="cert-manager",
            fetch_opts=FetchOpts(
                repo="https://charts.jetstack.io",
            ),
            values={
                "installCRDs": True,
            }
        ),
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[cert_manager_ns])
    )

    # ServiceAccount for the wait job
    cert_manager_wait_sa = ServiceAccount(
        "cert-manager-wait-sa",
        metadata={
            "name": "cert-manager-wait",
            "namespace": "cert-manager",
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[cert_manager_ns])
    )

    # ClusterRole to view pods
    cert_manager_wait_role = ClusterRole(
        "cert-manager-wait-role",
        metadata={"name": "cert-manager-wait"},
        rules=[{
            "apiGroups": [""],
            "resources": ["pods"],
            "verbs": ["get", "list", "watch"],
        }],
        opts=pulumi.ResourceOptions(provider=k8s_provider)
    )

    # Bind the role to the service account
    cert_manager_wait_binding = ClusterRoleBinding(
        "cert-manager-wait-binding",
        metadata={"name": "cert-manager-wait"},
        role_ref={
            "apiGroup": "rbac.authorization.k8s.io",
            "kind": "ClusterRole",
            "name": "cert-manager-wait",
        },
        subjects=[{
            "kind": "ServiceAccount",
            "name": "cert-manager-wait",
            "namespace": "cert-manager",
        }],
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[cert_manager_wait_role, cert_manager_wait_sa])
    )

    # Job that waits for webhook to be ready
    cert_manager_wait_job = Job(
        "cert-manager-wait",
        metadata={
            "name": "cert-manager-wait",
            "namespace": "cert-manager",
        },
        spec={
            "backoffLimit": 10,
            "template": {
                "spec": {
                    "restartPolicy": "OnFailure",
                    "serviceAccountName": "cert-manager-wait",
                    "containers": [{
                        "name": "wait",
                        "image": "bitnami/kubectl:latest",
                        "command": [
                            "sh", "-c",
                            "kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=webhook -n cert-manager --timeout=300s"
                        ],
                    }],
                }
            }
        },
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[cert_manager, cert_manager_wait_binding])
    )

    # Create ClusterIssuer for Let's Encrypt after webhook is ready
    lets_encrypt_issuer = ConfigFile(
        "letsencrypt-issuer",
        file="letsencrypt-issuer.yaml",
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[cert_manager_wait_job])
    )

    return lets_encrypt_issuer
