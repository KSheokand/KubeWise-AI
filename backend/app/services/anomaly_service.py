from datetime import datetime, timezone

from app.services.prometheus_service import PrometheusService
from app.core.kubernetes_client import get_core_v1_api


class AnomalyDetectionService:

    CPU_QUERY = """
    100 * (
        1 - avg by (instance) (
            rate(node_cpu_seconds_total{mode="idle"}[5m])
        )
    )
    """

    MEMORY_QUERY = """
    100 * (
        1 - (
            node_memory_MemAvailable_bytes
            / node_memory_MemTotal_bytes
        )
    )
    """

    RESTART_QUERY = """
    sum by (namespace, pod) (
        increase(kube_pod_container_status_restarts_total[10m])
    ) > 0
    """

    POD_CPU_QUERY = """
    (
        sum by (namespace, pod) (
            rate(container_cpu_usage_seconds_total{
                container!="",
                container!="POD"
            }[5m])
        )
        /
        on (namespace, pod)
        sum by (namespace, pod) (
            kube_pod_container_resource_limits{
                resource="cpu"
            }
        )
    ) * 100
    """

    POD_MEMORY_QUERY = """
    (
        sum by (namespace, pod) (
            container_memory_working_set_bytes{
                container!="",
                container!="POD"
            }
        )
        /
        on (namespace, pod)
        sum by (namespace, pod) (
            kube_pod_container_resource_limits{
                resource="memory"
            }
        )
    ) * 100
    """

    async def _execute_query(self, promql: str):
        """Execute a Prometheus instant query."""

        response = await PrometheusService.query(promql)

        results = response.get("results")

        if results is None:
            raise RuntimeError(
                "Prometheus response does not contain results."
            )

        return results

    def _create_anomaly(
        self,
        anomaly_type,
        resource,
        resource_name,
        value,
        threshold,
        severity,
        description,
        recommendation
    ):
        return {
            "id": f"{anomaly_type}-{resource_name}",
            "type": anomaly_type,
            "resource": resource,
            "resource_name": resource_name,
            "value": round(value, 2),
            "threshold": threshold,
            "severity": severity,
            "description": description,
            "recommendation": recommendation,
            "detected_at": datetime.now(timezone.utc).isoformat()
        }

    async def detect_cpu_anomalies(self):
        results = await self._execute_query(self.CPU_QUERY)

        anomalies = []

        for item in results:
            metric = item.get("metric", {})
            value = float(item["value"][1])

            instance = metric.get("instance", "unknown")

            if value >= 95:
                anomalies.append(
                    self._create_anomaly(
                        "high_cpu",
                        "node",
                        instance,
                        value,
                        95,
                        "critical",
                        f"Node CPU utilization is {value:.2f}%.",
                        "Investigate CPU-intensive processes and consider "
                        "rescheduling workloads or scaling capacity."
                    )
                )

            elif value >= 80:
                anomalies.append(
                    self._create_anomaly(
                        "high_cpu",
                        "node",
                        instance,
                        value,
                        80,
                        "warning",
                        f"Node CPU utilization is {value:.2f}%.",
                        "Monitor CPU usage and identify resource-intensive pods."
                    )
                )

        return anomalies

    async def detect_pod_cpu_anomalies(self):
        results = await self._execute_query(self.POD_CPU_QUERY)

        anomalies = []

        for item in results:
            metric = item.get("metric", {})

            value = float(item["value"][1])

            namespace = metric.get("namespace", "unknown")
            pod = metric.get("pod", "unknown")

            resource_name = f"{namespace}/{pod}"

            if value >= 95:
                anomalies.append(
                    self._create_anomaly(
                        "high_pod_cpu",
                        "pod",
                        resource_name,
                        value,
                        95,
                        "critical",
                        f"Pod CPU utilization is {value:.2f}% "
                        "of its configured CPU limit.",
                        "Investigate CPU-intensive processes, "
                        "optimize the workload or increase its CPU limit."
                    )
                )

            elif value >= 80:
                anomalies.append(
                    self._create_anomaly(
                        "high_pod_cpu",
                        "pod",
                        resource_name,
                        value,
                        80,
                        "warning",
                        f"Pod CPU utilization is {value:.2f}% "
                        "of its configured CPU limit.",
                        "Monitor CPU consumption and investigate "
                        "whether the workload needs additional CPU resources."
                    )
                )

        return anomalies

    async def detect_pod_memory_anomalies(self):
        results = await self._execute_query(self.POD_MEMORY_QUERY)

        anomalies = []

        for item in results:
            metric = item.get("metric", {})
            value = float(item["value"][1])

            namespace = metric.get("namespace", "unknown")
            pod = metric.get("pod", "unknown")

            resource_name = f"{namespace}/{pod}"

            if value >= 95:
                anomalies.append(
                    self._create_anomaly(
                        "high_pod_memory",
                        "pod",
                        resource_name,
                        value,
                        95,
                        "critical",
                        f"Pod memory utilization is {value:.2f}% "
                        "of its configured memory limit.",
                        "Investigate memory-intensive processes, "
                        "possible memory leaks, and increase the "
                        "memory limit if justified."
                    )
                )

            elif value >= 85:
                anomalies.append(
                    self._create_anomaly(
                        "high_pod_memory",
                        "pod",
                        resource_name,
                        value,
                        85,
                        "warning",
                        f"Pod memory utilization is {value:.2f}% "
                        "of its configured memory limit.",
                        "Monitor memory consumption and investigate "
                        "unusually high memory usage."
                    )
                )

        return anomalies

    async def detect_memory_anomalies(self):
        results = await self._execute_query(self.MEMORY_QUERY)

        anomalies = []

        for item in results:
            metric = item.get("metric", {})
            value = float(item["value"][1])

            instance = metric.get("instance", "unknown")

            if value >= 95:
                anomalies.append(
                    self._create_anomaly(
                        "high_memory",
                        "node",
                        instance,
                        value,
                        95,
                        "critical",
                        f"Node memory utilization is {value:.2f}%.",
                        "Investigate memory-intensive workloads and check "
                        "for possible memory leaks or OOM events."
                    )
                )

            elif value >= 85:
                anomalies.append(
                    self._create_anomaly(
                        "high_memory",
                        "node",
                        instance,
                        value,
                        85,
                        "warning",
                        f"Node memory utilization is {value:.2f}%.",
                        "Monitor memory consumption and inspect pod requests "
                        "and limits."
                    )
                )

        return anomalies

    async def detect_restart_anomalies(self):
        results = await self._execute_query(self.RESTART_QUERY)

        anomalies = []

        for item in results:
            metric = item.get("metric", {})
            value = float(item["value"][1])

            namespace = metric.get("namespace", "unknown")
            pod = metric.get("pod", "unknown")

            resource_name = f"{namespace}/{pod}"

            severity = "critical" if value >= 3 else "warning"

            anomalies.append(
                self._create_anomaly(
                    "pod_restarts",
                    "pod",
                    resource_name,
                    value,
                    3,
                    severity,
                    f"Pod {resource_name} has experienced "
                    f"{value:.0f} container restarts in the last 10 minutes.",
                    "Inspect container logs, pod events, resource limits "
                    "and the container's previous termination reason."
                )
            )

        return anomalies

    async def detect_container_failures(self):
        """Detect OOMKilled, CrashLoopBackOff and image pull failures."""

        core_v1 = get_core_v1_api()
        pods = core_v1.list_pod_for_all_namespaces().items

        anomalies = []

        failure_severities = {
            "OOMKilled": "critical",
            "CrashLoopBackOff": "critical",
            "ImagePullBackOff": "warning",
            "ErrImagePull": "warning",
            "StartError": "critical",
            "RunContainerError": "critical",
            "CreateContainerError": "critical",
            "CreateContainerConfigError": "critical"
        }

        for pod in pods:
            namespace = pod.metadata.namespace
            pod_name = pod.metadata.name

            if not pod.status.container_statuses:
                continue

            for container in pod.status.container_statuses:

                container_name = container.name
                reason = None

                # Check previous termination first.
                last_state = container.last_state

                termination_message = None

                if last_state and last_state.terminated:

                    termination_reason = last_state.terminated.reason

                    if termination_reason in failure_severities:
                        reason = termination_reason

                    termination_message = last_state.terminated.message

                # Check current waiting state if no OOM event was found.
                waiting = container.state.waiting if container.state else None

                if not reason and waiting and waiting.reason in failure_severities:
                    reason = waiting.reason

                if not reason:
                    continue

                anomalies.append({
                    "id": f"{reason}-{namespace}-{pod_name}-{container_name}",
                    "type": reason,
                    "resource": "container",
                    "resource_name": f"{namespace}/{pod_name}",
                    "container": container_name,
                    "value": 1,
                    "threshold": 0,
                    "severity": failure_severities[reason],
                    "description": (
                        f"Container {container_name} in pod "
                        f"{namespace}/{pod_name} has encountered "
                        f"{reason}."
                        f"Details: {termination_message or 'No additional details available.'}"
                    ),
                    "recommendation": (
                        "Inspect container logs, Kubernetes events, "
                        "resource limits and the container termination reason."
                    ),
                    "detected_at": datetime.now(timezone.utc).isoformat()
                })

        return anomalies

    async def scan(self):
        """Run all anomaly detection rules."""

        cpu_anomalies = await self.detect_cpu_anomalies()
        memory_anomalies = await self.detect_memory_anomalies()
        restart_anomalies = await self.detect_restart_anomalies()

        pod_cpu_anomalies = await self.detect_pod_cpu_anomalies()
        pod_memory_anomalies = await self.detect_pod_memory_anomalies()
        container_failure_anomalies = await self.detect_container_failures()

        anomalies = (
            cpu_anomalies
            + memory_anomalies
            + restart_anomalies
            + pod_cpu_anomalies
            + pod_memory_anomalies
            + container_failure_anomalies
        )

        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_anomalies": len(anomalies),
            "summary": {
                "critical": sum(
                    1 for a in anomalies
                    if a["severity"] == "critical"
                ),
                "warning": sum(
                    1 for a in anomalies
                    if a["severity"] == "warning"
                )
            },
            "anomalies": anomalies
        }


anomaly_service = AnomalyDetectionService()