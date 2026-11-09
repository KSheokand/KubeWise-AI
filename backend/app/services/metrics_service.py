from datetime import datetime, timezone

from kubernetes import client
from kubernetes.utils.quantity import parse_quantity

from fastapi import HTTPException
from kubernetes.client.exceptions import ApiException

from app.core.kubernetes_client import get_core_v1_api


class MetricsService:

    @staticmethod
    def _normalize_quantity(value, resource_type):
        """
        Convert Kubernetes resource quantities
        into numerical values.
        """

        parsed = float(parse_quantity(value))

        if resource_type == "cpu":
            return parsed

        if resource_type == "memory":
            return parsed

        return parsed

    @staticmethod
    def _format_container_metrics(containers):

        total_cpu = 0.0
        total_memory = 0.0

        container_data = []

        for container in containers:

            cpu = container["usage"].get("cpu", "0")
            memory = container["usage"].get("memory", "0")

            cpu_cores = MetricsService._normalize_quantity(
                cpu, "cpu"
            )

            memory_bytes = MetricsService._normalize_quantity(
                memory, "memory"
            )

            total_cpu += cpu_cores
            total_memory += memory_bytes

            container_data.append({
                "name": container["name"],
                "cpu": cpu,
                "cpu_cores": round(cpu_cores, 6),
                "memory": memory,
                "memory_mib": round(
                    memory_bytes / (1024 ** 2), 2
                )
            })

        return {
            "cpu_cores": round(total_cpu, 6),
            "cpu_millicores": round(total_cpu * 1000, 2),
            "memory_bytes": round(total_memory),
            "memory_mib": round(
                total_memory / (1024 ** 2), 2
            ),
            "containers": container_data
        }

    @staticmethod
    def _get_metrics_client():

        get_core_v1_api()

        return client.CustomObjectsApi()

    @staticmethod
    def get_node_metrics():

        try:

            api = MetricsService._get_metrics_client()

            metrics = api.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="nodes"
            )

            core_v1 = get_core_v1_api()
            nodes = {
                node.metadata.name: node
                for node in core_v1.list_node().items
            }

            result = []

            for item in metrics["items"]:

                node_name = item["metadata"]["name"]

                usage = item["usage"]

                cpu = usage.get("cpu", "0")
                memory = usage.get("memory", "0")

                cpu_cores = MetricsService._normalize_quantity(
                    cpu, "cpu"
                )

                memory_bytes = MetricsService._normalize_quantity(
                    memory, "memory"
                )

                node = nodes.get(node_name)

                allocatable = (
                    node.status.allocatable if node else {}
                ) or {}

                cpu_capacity = (
                    MetricsService._normalize_quantity(
                        allocatable["cpu"], "cpu"
                    )
                    if "cpu" in allocatable else None
                )

                memory_capacity = (
                    MetricsService._normalize_quantity(
                        allocatable["memory"], "memory"
                    )
                    if "memory" in allocatable else None
                )

                result.append({

                    "node": node_name,

                    "cpu": cpu,
                    "cpu_cores": round(cpu_cores, 6),
                    "cpu_millicores": round(
                        cpu_cores * 1000, 2
                    ),

                    "memory": memory,
                    "memory_bytes": round(memory_bytes),
                    "memory_mib": round(
                        memory_bytes / (1024 ** 2), 2
                    ),

                    "cpu_capacity_cores": cpu_capacity,

                    "cpu_utilization_percent": (
                        round(cpu_cores / cpu_capacity * 100, 2)
                        if cpu_capacity else None
                    ),

                    "memory_capacity_bytes": memory_capacity,

                    "memory_utilization_percent": (
                        round(
                            memory_bytes / memory_capacity * 100,
                            2
                        )
                        if memory_capacity else None
                    )

                })

            return {
                "count": len(result),
                "nodes": result,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat()
            }

        except ApiException as error:

            raise HTTPException(
                status_code=503,
                detail=f"Metrics API error: {error.reason}"
            )

    @staticmethod
    def get_pod_metrics(namespace=None):

        try:

            api = MetricsService._get_metrics_client()

            if namespace:

                metrics = api.list_namespaced_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    namespace=namespace,
                    plural="pods"
                )

            else:

                metrics = api.list_cluster_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    plural="pods"
                )

            result = []

            for item in metrics["items"]:

                metadata = item["metadata"]

                resource_metrics = (
                    MetricsService._format_container_metrics(
                        item.get("containers", [])
                    )
                )

                result.append({

                    "name": metadata["name"],
                    "namespace": metadata["namespace"],

                    **resource_metrics

                })

            return {
                "count": len(result),
                "pods": result,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat()
            }

        except ApiException as error:

            raise HTTPException(
                status_code=503,
                detail=f"Metrics API error: {error.reason}"
            )

    @staticmethod
    def get_cluster_metrics_summary():

        node_data = MetricsService.get_node_metrics()
        pod_data = MetricsService.get_pod_metrics()

        nodes = node_data["nodes"]
        pods = pod_data["pods"]

        total_cpu = sum(
            node["cpu_cores"] for node in nodes
        )

        total_memory = sum(
            node["memory_bytes"] for node in nodes
        )

        cpu_capacity = sum(
            node["cpu_capacity_cores"] or 0
            for node in nodes
        )

        memory_capacity = sum(
            node["memory_capacity_bytes"] or 0
            for node in nodes
        )

        return {

            "cluster": "kubewise-local",

            "nodes": len(nodes),
            "pods": len(pods),

            "cpu": {
                "usage_cores": round(total_cpu, 4),
                "capacity_cores": round(cpu_capacity, 4),
                "utilization_percent": (
                    round(total_cpu / cpu_capacity * 100, 2)
                    if cpu_capacity else None
                )
            },

            "memory": {
                "usage_bytes": round(total_memory),
                "usage_mib": round(
                    total_memory / (1024 ** 2), 2
                ),
                "capacity_bytes": round(memory_capacity),
                "utilization_percent": (
                    round(
                        total_memory / memory_capacity * 100,
                        2
                    )
                    if memory_capacity else None
                )
            },

            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()

        }