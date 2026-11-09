import httpx

from datetime import datetime, timezone

from fastapi import HTTPException


PROMETHEUS_URL = "http://localhost:9090"


class PrometheusService:

    @staticmethod
    async def _request(endpoint, params=None):

        url = f"{PROMETHEUS_URL}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=15.0) as http:
                response = await http.get(
                    url,
                    params=params
                )

                response.raise_for_status()

                data = response.json()

                if data.get("status") != "success":
                    raise HTTPException(
                        status_code=502,
                        detail="Prometheus query failed"
                    )

                return data

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Prometheus request timed out"
            )

        except httpx.HTTPStatusError as error:
            error_details = error.response.text[:1000]

            raise HTTPException(
                status_code=502,
                detail={
                    "message": "Prometheus rejected the request",
                    "status_code": error.response.status_code,
                    "prometheus_error": error_details
                }
            )

        except httpx.RequestError as error:
            raise HTTPException(
                status_code=503,
                detail=f"Unable to connect to Prometheus: {error}"
            )

    @staticmethod
    async def health():

        try:
            async with httpx.AsyncClient(timeout=5.0) as http:

                response = await http.get(
                    f"{PROMETHEUS_URL}/-/healthy"
                )

                response.raise_for_status()

                return {
                    "status": "connected",
                    "service": "prometheus",
                    "message": response.text.strip()
                }

        except httpx.HTTPError:
            raise HTTPException(
                status_code=503,
                detail="Prometheus is unavailable"
            )

    @staticmethod
    async def query(promql: str):

        data = await PrometheusService._request(
            "/api/v1/query",
            params={"query": promql}
        )

        return {
            "query": promql,
            "result_type": data["data"]["resultType"],
            "results": data["data"]["result"],
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }

    @staticmethod
    async def query_range(
        promql: str,
        start: str,
        end: str,
        step: str = "60s"
    ):

        data = await PrometheusService._request(
            "/api/v1/query_range",
            params={
                "query": promql,
                "start": start,
                "end": end,
                "step": step
            }
        )

        return {
            "query": promql,
            "result_type": data["data"]["resultType"],
            "results": data["data"]["result"],
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }

    @staticmethod
    async def cpu_metrics():

        promql = """
        100 * (
            1 -
            avg by (instance) (
                rate(node_cpu_seconds_total{mode="idle"}[5m])
            )
        )
        """

        return await PrometheusService.query(promql)

    @staticmethod
    async def memory_metrics():

        promql = """
        100 * (
            1 -
            (
                node_memory_MemAvailable_bytes
                /
                node_memory_MemTotal_bytes
            )
        )
        """

        return await PrometheusService.query(promql)

    @staticmethod
    async def pod_cpu_metrics():

        promql = """
        sum by (namespace, pod) (
            rate(container_cpu_usage_seconds_total{
                container!="",
                container!="POD"
            }[5m])
        )
        """

        return await PrometheusService.query(promql)

    @staticmethod
    async def pod_memory_metrics():

        promql = """
        sum by (namespace, pod) (
            container_memory_working_set_bytes{
                container!="",
                container!="POD"
            }
        )
        """

        return await PrometheusService.query(promql)

    @staticmethod
    async def restart_metrics():

        promql = """
        sum by (namespace, pod) (
            kube_pod_container_status_restarts_total
        )
        """

        return await PrometheusService.query(promql)

    @staticmethod
    async def historical_cpu_metrics(start: str, end: str, step: str = "60s"):

        promql = """
        100 * (
            1 - 
            avg by (instance) (
                rate(node_cpu_seconds_total{mode="idle"}[5m])
            )
        )
        """

        return await PrometheusService.query_range(
            promql=promql,
            start=start,
            end=end,
            step=step
        )

    @staticmethod
    async def historical_memory_metrics(start: str, end: str, step: str = "60s"):

        promql = """
        100 * (
            1 - 
            (
                node_memory_MemAvailable_bytes
                /
                node_memory_MemTotal_bytes
            )
        )
        """

        return await PrometheusService.query_range(
            promql=promql,
            start=start,
            end=end,
            step=step
        )

    @staticmethod
    async def historical_pod_cpu_metrics(start: str, end: str, step: str = "60s"):

        promql = """
        sum by (namespace, pod) (
            rate(container_cpu_usage_seconds_total{
            container!="",
            container!="POD"
            }[5m])
        )
        """

        return await PrometheusService.query_range(
            promql=promql,
            start=start,
            end=end,
            step=step
        )

    @staticmethod
    async def historical_pod_memory_metrics(start: str, end: str, step: str = "60s"):

        promql = """
        sum by (namespace, pod) (
            container_memory_working_set_bytes{
                container!="",
                container!="POD"
            }
        )
        """

        return await PrometheusService.query_range(
            promql=promql,
            start=start,
            end=end,
            step=step
        )