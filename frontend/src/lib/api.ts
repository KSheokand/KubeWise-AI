import axios from "axios";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types

export interface ClusterMetrics {
  cluster: string;
  nodes: number;
  pods: number;
  cpu: {
    usage_cores: number;
    capacity_cores: number;
    utilization_percent: number;
  };
  memory: {
    usage_bytes: number;
    usage_mib: number;
    capacity_bytes: number;
    utilization_percent: number;
  };
  timestamp: string;
}

export interface Incident {
  incident_id: string;
  fingerprint: string;
  type: string;
  resource: string;
  resource_name: string;
  severity: "critical" | "warning";
  status: "active" | "resolved";
  description: string;
  recommendation?: string;
  occurrence_count: number;
  first_seen: string;
  last_seen: string;
  resolved_at?: string;
}

export interface IncidentStats {
  total_incidents: number;
  active_incidents: number;
  resolved_incidents: number;
  severity_breakdown: {
    critical: number;
    warning: number;
  };
  anomaly_types: {
    type: string;
    count: number;
  }[];
}

export interface IncidentListResponse {
  total: number;
  limit: number;
  skip: number;
  incidents: Incident[];
}

export interface IncidentEvent {
    event_id: string;
    incident_id: string;
    event_type: string;
    severity?: string;
    evidence?: Record<string, unknown>;
    timestamp: string;
}

export interface PrometheusMetricSeries {
  metric: Record<string, string>;
  values: [number, string][];
}

export interface PrometheusHistoryResponse {
  query: string;
  result_type: string;
  results: PrometheusMetricSeries[];
  timestamp: string;
}

export interface ChartDataPoint {
  time: string;
  usage: number;
}

export interface KubernetesNamespace {
  name: string;
  status: string;
  created_at: string;
}

export interface NamespaceListResponse {
  count: number;
  namespaces: KubernetesNamespace[];
}

export interface PodResource {
  namespace: string;
  pod: string;
  cpuCores: number;
  cpuMillicores: number;
  memoryBytes: number;
  memoryMiB: number;
}

export interface KubernetesPod {
  name: string;
  namespace: string;
  status: string;
  health_status: string;
  pod_ip: string | null;
  node: string | null;
  restarts: number;
  ready_containers: number;
  total_containers: number;
  container_states: {
    name: string;
    ready: boolean;
    restart_count: number;
    state: string;
    reason: string | null;
  }[];
  created_at: string | null;
}

// API functions

export const getClusterMetrics = async () => {
  const response = await api.get<ClusterMetrics>(
    "/api/v1/metrics/summary"
  );

  return response.data;
};

export const getIncidentStats = async () => {
  const response = await api.get<IncidentStats>(
    "/api/v1/incidents/stats"
  );

  return response.data;
};

export const getIncidents = async (
  limit = 10,
  skip = 0
) => {
  const response = await api.get<IncidentListResponse>(
    "/api/v1/incidents/",
    {
      params: { limit, skip },
    }
  );

  return response.data;
};

export const getActiveIncidents = async () => {
  const response = await api.get(
    "/api/v1/incidents/active"
  );

  return response.data;
};

export const getClusterHealth = async () => {
  const response = await api.get(
    "/api/v1/cluster/health"
  );

  return response.data;
};

export const getIncidentDetails = async (id: string) => {
  const response = await api.get(`/api/v1/incidents/${id}`);
  return response.data;
};

export const getIncidentHistory = async (
  incidentId?: string
) => {
  const response = await api.get(
    "/api/v1/incidents/history",
    {
      params: incidentId ? { incident_id: incidentId } : {},
    }
  );

  return response.data;
};

export const resolveIncident = async (id: string) => {
  const response = await api.patch(
    `/api/v1/incidents/${id}/resolve`
  );

  return response.data;
};

// Historical Prometheus Metrics

export const getHistoricalCPU = async (
  start: string,
  end: string,
  step = "60s"
): Promise<PrometheusHistoryResponse> => {
  const response = await api.get<PrometheusHistoryResponse>(
    "/api/v1/prometheus/history/cpu",
    {
      params: { start, end, step },
    }
  );

  return response.data;
};

export const getHistoricalMemory = async (
  start: string,
  end: string,
  step = "60s"
): Promise<PrometheusHistoryResponse> => {
  const response = await api.get<PrometheusHistoryResponse>(
    "/api/v1/prometheus/history/memory",
    {
      params: { start, end, step },
    }
  );

  return response.data;
};

// Pod-level historical metrics

export const getHistoricalPodCPU = async (
  start: string,
  end: string,
  step = "60s"
): Promise<PrometheusHistoryResponse> => {
  const response = await api.get<PrometheusHistoryResponse>(
    "/api/v1/prometheus/history/pod-cpu",
    {
      params: { start, end, step },
    }
  );

  return response.data;
};

export const getHistoricalPodMemory = async (
  start: string,
  end: string,
  step = "60s"
): Promise<PrometheusHistoryResponse> => {
  const response = await api.get<PrometheusHistoryResponse>(
    "/api/v1/prometheus/history/pod-memory",
    {
      params: { start, end, step },
    }
  );

  return response.data;
};

// Kubernetes namespaces

export const getNamespaces = async (): Promise<NamespaceListResponse> => {
  const response = await api.get<NamespaceListResponse>(
    "/api/v1/namespaces/"
  );

  return response.data;
};

export const getKubernetesPods = async (
  namespace?: string
): Promise<{ count: number; pods: KubernetesPod[] }> => {
  const response = await api.get("/api/v1/pods/", {
    params: namespace ? { namespace } : {},
  });

  return response.data;
};