from datetime import datetime, timezone

from app.core.kubernetes_client import (
    get_core_v1_api,
    get_apps_v1_api
)


class KubernetesService:

    @staticmethod
    def get_nodes():

        core_v1 = get_core_v1_api()

        nodes = core_v1.list_node().items

        result = []

        for node in nodes:

            conditions = node.status.conditions or []

            ready_condition = next(
                (
                    condition
                    for condition in conditions
                    if condition.type == "Ready"
                ),
                None
            )

            is_ready = (
                ready_condition is not None
                and ready_condition.status == "True"
            )

            result.append({
                "name": node.metadata.name,
                "status": "Ready" if is_ready else "NotReady",
                "roles": [
                    label.replace("node-role.kubernetes.io/", "")
                    for label in (node.metadata.labels or {})
                    if label.startswith("node-role.kubernetes.io/")
                ],
                "kubernetes_version": (
                    node.status.node_info.kubelet_version
                ),
                "os": node.status.node_info.operating_system,
                "architecture": node.status.node_info.architecture,
                "capacity": node.status.capacity,
                "allocatable": node.status.allocatable,
                "created_at": (
                    node.metadata.creation_timestamp.isoformat()
                    if node.metadata.creation_timestamp
                    else None
                )
            })

        return result

    @staticmethod
    def get_namespaces():

        core_v1 = get_core_v1_api()

        namespaces = core_v1.list_namespace().items

        return [
            {
                "name": namespace.metadata.name,
                "status": namespace.status.phase,
                "created_at": (
                    namespace.metadata.creation_timestamp.isoformat()
                    if namespace.metadata.creation_timestamp
                    else None
                )
            }
            for namespace in namespaces
        ]

    @staticmethod
    def get_pods(namespace=None):

        core_v1 = get_core_v1_api()

        if namespace:
            pods = core_v1.list_namespaced_pod(
                namespace=namespace
            ).items
        else:
            pods = core_v1.list_pod_for_all_namespaces().items

        result = []

        for pod in pods:

            container_statuses = (
                pod.status.container_statuses or []
            )

            total_restarts = sum(
                container.restart_count
                for container in container_statuses
            )

            ready_containers = sum(
                1
                for container in container_statuses
                if container.ready
            )

            total_containers = len(
                pod.spec.containers
            )

            container_states = []
            waiting_reasons = []

            for container in container_statuses:

                state = container.state
                state_name = "Unknown"
                state_reason = None

                if state.running:
                    state_name = "Running"

                elif state.waiting:
                    state_name = "Waiting"
                    state_reason = state.waiting.reason

                    if state_reason:
                        waiting_reasons.append(state_reason)

                elif state.terminated:
                    state_name = "terminated"
                    state_reason = state.terminated.reason

                container_states.append({
                    "name": container.name,
                    "ready": container.ready,
                    "restart_count": container.restart_count,
                    "state": state_name,
                    "reason": state_reason
                })

            pod_phase = pod.status.phase or "Unknown"

            unhealty_reasons = {
                "CrashLoopBackOff",
                "ImagePullBackOff",
                "ErrImagePull",
                "CreateContainerConfigError",
                "CreateContainerError",
                "RunContainerError",
                "OOMKilled",
                "StartError"
            }

            detected_problems = [
                reason 
                for reason in waiting_reasons
                if reason in unhealty_reasons
            ]

            if detected_problems:
                heath_status = detected_problems[0]

            elif pod_phase == "Running" and (
                ready_containers < total_containers
            ):
                health_status= "NotReady"

            elif pod_phase == "Running":
                health_status = "Healthy"

            elif pod_phase == "Succeeded":
                health_status = "Completed"

            else:
                health_status = pod_phase

            result.append({
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "health_status": health_status,
                "pod_ip": pod.status.pod_ip,
                "node": pod.spec.node_name,
                "restarts": total_restarts,
                "ready_containers": ready_containers,
                "total_containers": total_containers,
                "container_states": container_states,
                "created_at": (
                    pod.metadata.creation_timestamp.isoformat()
                    if pod.metadata.creation_timestamp
                    else None
                )
            })

        return result

    @staticmethod
    def get_pod_details(namespace, pod_name):

        core_v1 = get_core_v1_api()

        pod = core_v1.read_namespaced_pod(
            name=pod_name,
            namespace=namespace
        )

        container_statuses = (
            pod.status.container_statuses or []
        )

        containers = []

        for container in pod.spec.containers:

            status = next(
                (
                    item
                    for item in container_statuses
                    if item.name == container.name
                ),
                None
            )

            containers.append({
                "name": container.name,
                "image": container.image,
                "ready": status.ready if status else False,
                "restart_count": (
                    status.restart_count if status else 0
                ),
                "resources": {
                    "requests": container.resources.requests or {},
                    "limits": container.resources.limits or {}
                }
            })

        return {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": pod.status.phase,
            "pod_ip": pod.status.pod_ip,
            "node": pod.spec.node_name,
            "containers": containers,
            "created_at": (
                pod.metadata.creation_timestamp.isoformat()
                if pod.metadata.creation_timestamp
                else None
            )
        }

    @staticmethod
    def get_deployments(namespace=None):

        apps_v1 = get_apps_v1_api()

        if namespace:
            deployments = apps_v1.list_namespaced_deployment(
                namespace=namespace
            ).items
        else:
            deployments = (
                apps_v1.list_deployment_for_all_namespaces().items
            )

        result = []

        for deployment in deployments:

            spec = deployment.spec
            status = deployment.status

            result.append({
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "desired_replicas": spec.replicas or 0,
                "ready_replicas": status.ready_replicas or 0,
                "available_replicas": status.available_replicas or 0,
                "updated_replicas": status.updated_replicas or 0,
                "created_at": (
                    deployment.metadata.creation_timestamp.isoformat()
                    if deployment.metadata.creation_timestamp
                    else None
                )
            })

        return result

    @staticmethod
    def get_cluster_health():

        nodes = KubernetesService.get_nodes()
        pods = KubernetesService.get_pods()
        deployments = KubernetesService.get_deployments()

        ready_nodes = sum(
            1 for node in nodes
            if node["status"] == "Ready"
        )

        running_pods = sum(
            1 for pod in pods
            if pod["status"] == "Running"
        )

        unhealthy_pods = sum(
            1 for pod in pods
            if pod["status"] not in ("Running", "Succeeded")
        )

        total_restarts = sum(
            pod["restarts"] for pod in pods
        )

        ready_deployments = sum(
            1 for deployment in deployments
            if deployment["ready_replicas"]
            == deployment["desired_replicas"]
        )

        return {
            "cluster_name": "kubewise-local",
            "status": (
                "Healthy"
                if ready_nodes == len(nodes)
                and unhealthy_pods == 0
                else "Degraded"
            ),
            "nodes": {
                "total": len(nodes),
                "ready": ready_nodes
            },
            "pods": {
                "total": len(pods),
                "running": running_pods,
                "unhealthy": unhealthy_pods,
                "total_restarts": total_restarts
            },
            "deployments": {
                "total": len(deployments),
                "ready": ready_deployments
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }