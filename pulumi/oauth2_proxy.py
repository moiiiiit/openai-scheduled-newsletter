import base64
import secrets
import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts

from config import auth0_domain
from auth0_setup import auth0_client_id
from kubernetes_resources import k8s_provider

cfg = pulumi.Config()
auth0_client_secret = cfg.get_secret("auth0_client_secret")

oauth2_ns = k8s.core.v1.Namespace(
    "oauth2-proxy-ns",
    metadata={"name": "oauth2-proxy"},
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

cookie_secret = cfg.get_secret("oauth2_cookie_secret")
if cookie_secret is None:
    alphabet = string.ascii_letters + string.digits + "-_"
    cookie_secret = pulumi.Output.secret("".join(secrets.choice(alphabet) for _ in range(32)))

extra_args = pulumi.Output.all(auth0_domain, cookie_secret).apply(lambda a: [
    "--provider=oidc",
    f"--oidc-issuer-url=https://{a[0]}/",
    "--redirect-url=https://newsletter-api.mohitbhole.net/oauth2/callback",
    "--email-domain=*",
    f"--cookie-secret={a[1]}",
    "--cookie-secure=true",
    "--cookie-httponly=true",
    "--cookie-samesite=lax",
    "--skip-auth-preflight=true",
    "--skip-auth-regex=^/health$",
])

values = {
    "config": {
        "clientID": auth0_client_id,
        "clientSecret": auth0_client_secret,
    },
    "extraArgs": extra_args,
    "service": {
        "portNumber": 4180,
    },
}

oauth2_proxy_chart = Chart(
    "oauth2-proxy",
    ChartOpts(
        chart="oauth2-proxy",
        namespace="oauth2-proxy",
        fetch_opts=FetchOpts(
            repo="https://oauth2-proxy.github.io/manifests",
            version="7.6.0",
        ),
        values=values,
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[oauth2_ns]),
)

pulumi.export("oauth2_proxy_namespace", oauth2_ns.metadata["name"])
