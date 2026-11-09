from fastapi import APIRouter

from app.services.kubernetes_service import KubernetesService

router = APIRouter()


@router.get("/")
def get_deployments(namespace: str = None):

    deployments = KubernetesService.get_deployments(namespace)

    return {
        "count": len(deployments),
        "deployments": deployments
    }