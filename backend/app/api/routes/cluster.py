from fastapi import APIRouter

from app.services.kubernetes_service import KubernetesService

router = APIRouter()


@router.get("/health")
def cluster_health():

    return KubernetesService.get_cluster_health()