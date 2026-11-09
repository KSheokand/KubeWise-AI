from fastapi import APIRouter

from app.services.kubernetes_service import KubernetesService

router = APIRouter()


@router.get("/")
def get_nodes():

    return {
        "count": len(KubernetesService.get_nodes()),
        "nodes": KubernetesService.get_nodes()
    }