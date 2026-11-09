"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  Box,
  Cpu,
  MemoryStick,
  Server,
  RefreshCw,
  Activity,
} from "lucide-react";

import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

import PodResourceOverview from "@/components/workloads/PodResourceOverview";
import PodResourceTable, {
  PodResource,
} from "@/components/workloads/PodResourceTable";

import {
  getHistoricalPodCPU,
  getHistoricalPodMemory,
  getNamespaces,
  getKubernetesPods,
  KubernetesNamespace,
} from "@/lib/api";

export default function WorkloadsPage() {
  const [pods, setPods] = useState<PodResource[]>([]);
  const [namespaces, setNamespaces] = useState<KubernetesNamespace[]>([]);

  const [selectedNamespace, setSelectedNamespace] = useState("all");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadWorkloads = useCallback(async () => {
    try {
      setError("");

      const endDate = new Date();
      const startDate = new Date(
        endDate.getTime() - 15 * 60 * 1000
      );

      const start = startDate.toISOString();
      const end = endDate.toISOString();

      const [cpuResponse, memoryResponse, namespaceResponse, kubernetesResponse] =
        await Promise.all([
          getHistoricalPodCPU(start, end, "60s"),
          getHistoricalPodMemory(start, end, "60s"),
          getNamespaces(),
          getKubernetesPods(),
        ]);

      setNamespaces(namespaceResponse.namespaces);

      // Combine CPU and memory series using namespace + pod.
      const podMap = new Map<string, PodResource>();

      cpuResponse.results.forEach((series) => {
        const namespace = series.metric.namespace;
        const pod = series.metric.pod;

        if (!namespace || !pod || !series.values?.length) {
          return;
        }

        const latestValue = series.values[series.values.length - 1];
        const cpuCores = Number(latestValue[1]);

        const key = `${namespace}/${pod}`;

        podMap.set(key, {
          namespace,
          pod,
          cpuCores,
          cpuMillicores: cpuCores * 1000,
          memoryBytes: 0,
          memoryMiB: 0,

          status: "unknown",
          healthStatus: "unknown",
          restarts: 0,
          readyContainers: 0,
          totalContainers: 0,
          podIP: null,
          node: null,
        });
      });

      memoryResponse.results.forEach((series) => {
        const namespace = series.metric.namespace;
        const pod = series.metric.pod;

        if (!namespace || !pod || !series.values?.length) {
          return;
        }

        const latestValue = series.values[series.values.length - 1];
        const memoryBytes = Number(latestValue[1]);

        const key = `${namespace}/${pod}`;

        const existing = podMap.get(key);

        if (existing) {
          existing.memoryBytes = memoryBytes;
          existing.memoryMiB = memoryBytes / (1024 * 1024);
        } else {
          // Preserve pods that have memory data but no CPU series.
          podMap.set(key, {
            namespace,
            pod,
            cpuCores: 0,
            cpuMillicores: 0,
            memoryBytes,
            memoryMiB: memoryBytes / (1024 * 1024),

            status: "unknown",
            healthStatus: "unknown",
            restarts: 0,
            readyContainers: 0,
            totalContainers: 0,
            podIP: null,
            node: null,
          });
        }
      });

      // Index Kubernetes inventory by namespace + pod name.
const kubernetesPodMap = new Map(
  kubernetesResponse.pods.map((pod) => [
    `${pod.namespace}/${pod.name}`,
    pod,
  ])
);

// Merge Kubernetes inventory with Prometheus resource metrics.
const allPodKeys = new Set([
  ...podMap.keys(),
  ...kubernetesPodMap.keys(),
]);

const mergedPods: PodResource[] = Array.from(allPodKeys).map(
  (key) => {
    const metrics = podMap.get(key);
    const kubernetesPod = kubernetesPodMap.get(key);

    return {
      namespace: kubernetesPod?.namespace ?? metrics?.namespace ?? "",
      pod: kubernetesPod?.name ?? metrics?.pod ?? "",

      cpuCores: metrics?.cpuCores ?? 0,
      cpuMillicores: metrics?.cpuMillicores ?? 0,
      memoryBytes: metrics?.memoryBytes ?? 0,
      memoryMiB: metrics?.memoryMiB ?? 0,

      status: kubernetesPod?.status ?? "Unknown",
      healthStatus: kubernetesPod?.health_status ?? "Unknown",
      restarts: kubernetesPod?.restarts ?? 0,
      readyContainers: kubernetesPod?.ready_containers ?? 0,
      totalContainers: kubernetesPod?.total_containers ?? 0,

      podIP: kubernetesPod?.pod_ip ?? null,
      node: kubernetesPod?.node ?? null,
    };
  }
);

setPods(mergedPods);

      setLastUpdated(new Date());
    } catch (err) {
      console.error("Workloads API error:", err);

      setError(
        "Unable to load workload metrics. Check the backend and Prometheus connection."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWorkloads();

    const interval = setInterval(loadWorkloads, 30000);

    return () => clearInterval(interval);
  }, [loadWorkloads]);

  const filteredPods = useMemo(() => {
    if (selectedNamespace === "all") {
      return pods;
    }

    return pods.filter(
      (pod) => pod.namespace === selectedNamespace
    );
  }, [pods, selectedNamespace]);

  const totalCPU = filteredPods.reduce(
    (sum, pod) => sum + pod.cpuCores,
    0
  );

  const totalMemory = filteredPods.reduce(
    (sum, pod) => sum + pod.memoryMiB,
    0
  );

  const namespaceCount = new Set(
    filteredPods.map((pod) => pod.namespace)
  ).size;

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Header />

        <div className="dashboard-content">
          {/* Page heading */}
          <section className="page-heading">
            <div>
              <div className="eyebrow">
                KUBERNETES INFRASTRUCTURE
              </div>

              <h1>Workloads</h1>

              <p>
                Monitor pod-level CPU and memory consumption
                across your Kubernetes cluster.
              </p>
            </div>

            <div className="cluster-status">
              <span className="status-dot" />
              Cluster Connected
            </div>
          </section>

          {/* Toolbar */}
          <div className="dashboard-toolbar">
            <span>
              {loading
                ? "Loading workloads..."
                : lastUpdated
                  ? `Last updated: ${lastUpdated.toLocaleTimeString()}`
                  : "Waiting for data"}
            </span>

            <button
              className="refresh-button"
              onClick={loadWorkloads}
              disabled={loading}
            >
              <RefreshCw size={14} />
              Refresh
            </button>
          </div>

          {/* Error message */}
          {error && (
            <div className="error-banner">
              {error}

              <button onClick={loadWorkloads}>
                Retry
              </button>
            </div>
          )}

          {/* Summary cards */}
          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon purple">
                <Box size={20} />
              </div>

              <div>
                <span className="stat-title">
                  Monitored Pods
                </span>

                <h2>{loading ? "--" : filteredPods.length}</h2>

                <p>Pods discovered by Kubernetes</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon blue">
                <Cpu size={20} />
              </div>

              <div>
                <span className="stat-title">
                  Total CPU Usage
                </span>

                <h2>
                  {loading ? "--" : `${(totalCPU * 1000).toFixed(2)} m`}
                </h2>

                <p>Combined CPU consumption</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon green">
                <MemoryStick size={20} />
              </div>

              <div>
                <span className="stat-title">
                  Total Memory Usage
                </span>

                <h2>
                  {loading ? "--" : `${totalMemory.toFixed(2)} MiB`}
                </h2>

                <p>Combined memory consumption</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon orange">
                <Server size={20} />
              </div>

              <div>
                <span className="stat-title">
                  Active Namespaces
                </span>

                <h2>{namespaceCount}</h2>

                <p>Namespaces containing workloads</p>
              </div>
            </div>
          </section>

          {/* Namespace filter */}
          <section className="workload-filter-section">
            <div>
              <h3>Workload Resource Analysis</h3>

              <p>
                Analyze CPU and memory usage by namespace.
              </p>
            </div>

            <div className="namespace-filter">
              <label htmlFor="namespace">
                Namespace
              </label>

              <select
                id="namespace"
                value={selectedNamespace}
                onChange={(event) =>
                  setSelectedNamespace(event.target.value)
                }
              >
                <option value="all">All Namespaces</option>

                {namespaces.map((namespace) => (
                  <option
                    key={namespace.name}
                    value={namespace.name}
                  >
                    {namespace.name}
                  </option>
                ))}
              </select>
            </div>
          </section>

          {/* Resource rankings */}
          <section className="section-title">
            <div>
              <h2>Resource Consumption</h2>

              <p>
                Top resource-consuming pods
              </p>
            </div>

            <span className="live-indicator">
              <span className="status-dot" />
              Prometheus · 30s refresh
            </span>
          </section>

          {loading ? (
            <div className="workload-loading">
              Loading pod resource metrics...
            </div>
          ) : (
            <PodResourceOverview pods={filteredPods} />
          )}

          {/* Resource table */}
          <section className="section-title">
            <div>
              <h2>Pod Inventory</h2>

              <p>
                Individual pod resource consumption
              </p>
            </div>

            <span className="live-indicator">
              <Activity size={14} />
              Live workload data
            </span>
          </section>

          <PodResourceTable pods={filteredPods} />

          <footer className="dashboard-footer">
            KubeWise AI · Kubernetes Workload Monitoring
          </footer>
        </div>
      </main>
    </div>
  );
}