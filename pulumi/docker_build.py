"""Automated Docker image building and pushing to ACR using Pulumi Docker Build provider"""

import pulumi
import pulumi_docker_build as docker_build
import os


def build_and_push_images(acr, acr_username, acr_password):
    """Build and push API and Job images to ACR using pulumi-docker-build"""
    
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    registry_auth = docker_build.RegistryArgs(
        address=acr.login_server,
        username=acr_username,
        password=acr_password,
    )
    
    api_image = docker_build.Image(
        "api-image",
        context=docker_build.BuildContextArgs(
            location=base_path,
        ),
        dockerfile=docker_build.DockerfileArgs(
            location=os.path.join(base_path, "openai_scheduled_newsletter_api/Dockerfile"),
        ),
        platforms=[docker_build.Platform.LINUX_AMD64],
        push=True,
        registries=[registry_auth],
        tags=[pulumi.Output.concat(acr.login_server, "/api:latest")],
    )
    
    job_image = docker_build.Image(
        "job-image",
        context=docker_build.BuildContextArgs(
            location=base_path,
        ),
        dockerfile=docker_build.DockerfileArgs(
            location=os.path.join(base_path, "openai_scheduled_newsletter_job/Dockerfile"),
        ),
        platforms=[docker_build.Platform.LINUX_AMD64],
        push=True,
        registries=[registry_auth],
        tags=[pulumi.Output.concat(acr.login_server, "/job:latest")],
    )
    
    pulumi.export("api_image_ref", api_image.ref)
    pulumi.export("job_image_ref", job_image.ref)
    
    return api_image, job_image
