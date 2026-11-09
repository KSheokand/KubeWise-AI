"use client";

import { Cpu, MemoryStick } from "lucide-react";

export interface PodResource {
  namespace: string;
  pod: string;
  cpuCores: number;
  cpuMillicores: number;
  memoryBytes: number;
  memoryMiB: number;
  status: string;
  healthStatus: string;
  restarts: number;
  readyContainers: number;
  totalContainers: number;
  podIP: string | null;
  node: string | null;
}

interface Props {
  pods: PodResource[];
}

export default function PodResourceTable({ pods }: Props) {
  const sortedPods = [...pods].sort(
    (a, b) => b.cpuCores - a.cpuCores
  );

  const formatCPU = (cores: number) =>
    `${(cores * 1000).toFixed(2)} m`;

  const formatMemory = (memory: number) =>
    memory >= 1024
      ? `${(memory / 1024).toFixed(2)} GiB`
      : `${memory.toFixed(2)} MiB`;

  const getHealthClass = (health: string) => {
    if (health === "Healthy") return "healthy";
    if (health === "Completed") return "completed";
    if (health === "NotReady") return "warning";

    return "unhealthy";
  };

  return (
    <div className="pod-table-card">
      <div className="section-header">
        <div>
          <h3>Pod Resource Consumption</h3>
          <p>{pods.length} pods monitored</p>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="pod-resource-table">
          <thead>
            <tr>
              <th>Pod</th>
              <th>Namespace</th>
              <th>Health</th>
              <th>Readiness</th>
              <th>Restarts</th>
              <th><Cpu size={14} /> CPU</th>
              <th><MemoryStick size={14} /> Memory</th>
              <th>Node</th>
            </tr>
          </thead>

          <tbody>
            {sortedPods.map((pod) => (
              <tr key={`${pod.namespace}-${pod.pod}`}>
                <td className="pod-name">
                  <div>{pod.pod}</div>
                  <small>{pod.podIP || "No pod IP"}</small>
                </td>

                <td>
                  <span className="namespace-badge">
                    {pod.namespace}
                  </span>
                </td>

                <td>
                  <span
                    className={`pod-health-badge ${getHealthClass(
                      pod.healthStatus
                    )}`}
                  >
                    {pod.healthStatus}
                  </span>
                </td>

                <td>
                  {pod.readyContainers}/{pod.totalContainers}
                </td>

                <td>
                  <span
                    className={
                      pod.restarts > 0
                        ? "restart-count warning"
                        : "restart-count"
                    }
                  >
                    {pod.restarts}
                  </span>
                </td>

                <td>{formatCPU(pod.cpuCores)}</td>
                <td>{formatMemory(pod.memoryMiB)}</td>
                <td>{pod.node || "Unassigned"}</td>
              </tr>
            ))}

            {pods.length === 0 && (
              <tr>
                <td colSpan={8} className="empty-state">
                  No pods available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}