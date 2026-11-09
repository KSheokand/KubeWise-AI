from functools import lru_cache

from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from fastapi import HTTPException


@lru_cache()
def get_kubernetes_clients():
    """
    Load Kubernetes credentials and initialize API clients.

    Uses the local Kind cluster context.
    """

    try:
        config.load_kube_config(
            context="kind-kubewise-local"
        )

        core_v1 = client.CoreV1Api()
        apps_v1 = client.AppsV1Api()

        return core_v1, apps_v1

    except ConfigException as error:
        raise HTTPException(
            status_code=503,
            detail=f"Kubernetes configuration error: {error}"
        )

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to connect to Kubernetes: {error}"
        )


def get_core_v1_api():
    core_v1, _ = get_kubernetes_clients()
    return core_v1


def get_apps_v1_api():
    _, apps_v1 = get_kubernetes_clients()
    return apps_v1