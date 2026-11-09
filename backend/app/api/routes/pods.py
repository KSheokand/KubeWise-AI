from fastapi import APIRouter, HTTPException

from kubernetes.client.exceptions import ApiException

from app.services.kubernetes_service import KubernetesService

router = APIRouter()


@router.get("/")
def get_pods(namespace: str = None):

    pods = KubernetesService.get_pods(namespace)

    return {
        "count": len(pods),
        "pods": pods
    }


@router.get("/{namespace}/{pod_name}")
def get_pod_details(namespace: str, pod_name: str):

    try:
        return KubernetesService.get_pod_details(
            namespace,
            pod_name
        )

    except ApiException as error:

        if error.status == 404:
            raise HTTPException(
                status_code=404,
                detail="Pod not found"
            )

        raise HTTPException(
            status_code=error.status or 500,
            detail=error.reason or "Kubernetes API error"
        )