from fastapi import APIRouter, HTTPException, Query

from app.services.prometheus_service import PrometheusService


router = APIRouter()


@router.get("/health")
async def prometheus_health():

    return await PrometheusService.health()


@router.get("/query")
async def execute_query(
    query: str = Query(..., min_length=1, max_length=2000)
):

    return await PrometheusService.query(query)


@router.get("/cpu")
async def get_cpu_metrics():

    return await PrometheusService.cpu_metrics()


@router.get("/memory")
async def get_memory_metrics():

    return await PrometheusService.memory_metrics()


@router.get("/pods/cpu")
async def get_pod_cpu_metrics():

    return await PrometheusService.pod_cpu_metrics()


@router.get("/pods/memory")
async def get_pod_memory_metrics():

    return await PrometheusService.pod_memory_metrics()


@router.get("/restarts")
async def get_restart_metrics():

    return await PrometheusService.restart_metrics()


@router.get("/history/cpu")
async def get_historical_cpu(
    start: str = Query(..., description="Start time in RFC3339 or Unix timestamp format"),
    end: str = Query(..., description="End time in RFC3339 or Unix timestamp format"),
    step: str = Query("60s", description="Prometheus sampling interval")
):
    return await PrometheusService.historical_cpu_metrics(
        start=start,
        end=end,
        step=step
    )


@router.get("/history/memory")
async def get_historical_memory(
    start: str = Query(...),
    end: str = Query(...),
    step: str = Query("60s")
):
    return await PrometheusService.historical_memory_metrics(
        start=start,
        end=end,
        step=step
    )


@router.get("/history/pod-cpu")
async def get_historical_pod_cpu(
    start: str = Query(...),
    end: str = Query(...),
    step: str = Query("60s")
):
    return await PrometheusService.historical_pod_cpu_metrics(
        start=start,
        end=end,
        step=step
    )


@router.get("/history/pod-memory")
async def get_historical_pod_memory(
    start: str = Query(...),
    end: str = Query(...),
    step: str = Query("60s")
):
    return await PrometheusService.historical_pod_memory_metrics(
        start=start,
        end=end,
        step=step
    )

@router.get("/history")
async def get_historical_metrics(
    query: str = Query(..., min_length=1, max_length=2000),
    start: str = Query(...),
    end: str = Query(...),
    step: str = Query("60s")
):

    return await PrometheusService.query_range(
        promql=query,
        start=start,
        end=end,
        step=step
    )