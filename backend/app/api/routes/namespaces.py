from fastapi import APIRouter

from app.services.kubernetes_service import KubernetesService

router = APIRouter()


@router.get("/")
def get_namespaces():

    namespaces = KubernetesService.get_namespaces()

    return {
        "count": len(namespaces),
        "namespaces": namespaces
    }