from fastapi import APIRouter, Query

from app.services.loki_service import loki_service


router = APIRouter()


@router.get("/health")
async def loki_health():
    return await loki_service.health()


@router.get("/labels")
async def get_labels():
    return await loki_service.get_labels()


@router.get("/search")
async def search_logs(
    namespace: str = None,
    pod: str = None,
    search: str = None,
    limit: int = Query(default=100, ge=1, le=1000)
):
    return await loki_service.search_logs(
        namespace=namespace,
        pod=pod,
        search=search,
        limit=limit
    )


@router.get("/errors")
async def get_error_logs(
    namespace: str = None,
    limit: int = Query(default=100, ge=1, le=1000)
):
    return await loki_service.get_error_logs(
        namespace=namespace,
        limit=limit
    )


@router.get("/query")
async def query_logs(
    query: str,
    limit: int = Query(default=100, ge=1, le=1000)
):
    return await loki_service.query_range(
        query=query,
        limit=limit
    )


@router.get("/pod/{namespace}/{pod_name}")
async def get_pod_logs(
    namespace: str,
    pod_name: str,
    limit: int = Query(default=100, ge=1, le=1000)
):
    return await loki_service.search_logs(
        namespace=namespace,
        pod=pod_name,
        limit=limit
    )