from fastapi import APIRouter, HTTPException

from kubernetes.client.exceptions import ApiException

from app.services.metrics_service import MetricsService


router = APIRouter()


@router.get("/nodes")
def get_node_metrics():

    return MetricsService.get_node_metrics()


@router.get("/pods")
def get_pod_metrics():

    return MetricsService.get_pod_metrics()


@router.get("/pods/{namespace}")
def get_namespace_pod_metrics(namespace: str):

    try:
        return MetricsService.get_pod_metrics(namespace)

    except ApiException as error:

        if error.status == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Namespace '{namespace}' not found"
            )

        raise HTTPException(
            status_code=error.status or 500,
            detail=error.reason or "Kubernetes API error"
        )


@router.get("/summary")
def get_metrics_summary():

    return MetricsService.get_cluster_metrics_summary()