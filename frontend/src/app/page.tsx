"use client";

import { useCallback, useEffect, useState } from "react";

import {
  Server,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Cpu,
  MemoryStick,
  RefreshCw,
} from "lucide-react";

import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import StatCard from "@/components/dashboard/StatCard";
import ResourceChart from "@/components/dashboard/ResourceChart";
import RecentIncidents from "@/components/dashboard/RecentIncidents";

import {
  getClusterMetrics,
  getIncidentStats,
  getIncidents,
  getClusterHealth,
  getHistoricalCPU,
  getHistoricalMemory,
  ClusterMetrics,
  IncidentStats,
  Incident,
  ChartDataPoint,
} from "@/lib/api";

import { convertPrometheusHistory } from "@/lib/metrics";

type TimeRange = "15m" | "1h" | "6h" | "24h";

const timeRangeConfig: Record<
  TimeRange,
  { milliseconds: number; step: string }
> = {
  "15m": { milliseconds: 15 * 60 * 1000, step: "15s" },
  "1h": { milliseconds: 60 * 60 * 1000, step: "60s" },
  "6h": { milliseconds: 6 * 60 * 60 * 1000, step: "5m" },
  "24h": { milliseconds: 24 * 60 * 60 * 1000, step: "5m" },
};

export default function Dashboard() {
  const [metrics, setMetrics] = useState<ClusterMetrics | null>(null);
  const [stats, setStats] = useState<IncidentStats | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [clusterHealth, setClusterHealth] = useState<any>(null);

  const [cpuHistory, setCpuHistory] = useState<ChartDataPoint[]>([]);
  const [memoryHistory, setMemoryHistory] = useState<ChartDataPoint[]>([]);

  const [timeRange, setTimeRange] = useState<TimeRange>("1h");
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Load cluster and incident information
  const loadDashboard = useCallback(async () => {
    try {
      setError("");

      const results = await Promise.all([
        getClusterMetrics(),
        getIncidentStats(),
        getIncidents(5),
        getClusterHealth(),
      ]);

      setMetrics(results[0]);
      setStats(results[1]);
      setIncidents(results[2].incidents);
      setClusterHealth(results[3]);

      setLastUpdated(new Date());
    } catch (err) {
      console.error("Dashboard API error:", err);

      setError(
        "Unable to retrieve dashboard data. Check that the backend and Kubernetes services are running."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // Load historical Prometheus metrics
  const loadHistoricalMetrics = useCallback(async () => {
    try {
      setHistoryLoading(true);
      setHistoryError("");

      const config = timeRangeConfig[timeRange];

      const endDate = new Date();
      const startDate = new Date(
        endDate.getTime() - config.milliseconds
      );

      const start = startDate.toISOString();
      const end = endDate.toISOString();

      const [cpuResponse, memoryResponse] = await Promise.all([
        getHistoricalCPU(start, end, config.step),
        getHistoricalMemory(start, end, config.step),
      ]);

      setCpuHistory(convertPrometheusHistory(cpuResponse));
      setMemoryHistory(convertPrometheusHistory(memoryResponse));
    } catch (err) {
      console.error("Historical metrics API error:", err);
      setHistoryError(
        "Unable to load historical metrics. Check Prometheus connectivity."
      );
    } finally {
      setHistoryLoading(false);
    }
  }, [timeRange]);

  // Initial dashboard loading and 15-second refresh
  useEffect(() => {
    loadDashboard();

    const interval = setInterval(loadDashboard, 15000);

    return () => clearInterval(interval);
  }, [loadDashboard]);

  // Load historical metrics when time range changes
  useEffect(() => {
    loadHistoricalMetrics();

    const interval = setInterval(
      loadHistoricalMetrics,
      60000
    );

    return () => clearInterval(interval);
  }, [loadHistoricalMetrics]);

  const cpuUsage = metrics?.cpu.utilization_percent ?? 0;
  const memoryUsage = metrics?.memory.utilization_percent ?? 0;

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Header />

        <div className="dashboard-content">
          <section className="page-heading">
            <div>
              <div className="eyebrow">
                INFRASTRUCTURE OVERVIEW
              </div>

              <h1>Dashboard</h1>

              <p>
                Monitor your Kubernetes infrastructure in real time.
              </p>
            </div>

            <div className="cluster-status">
              <span className="status-dot" />
              {metrics?.cluster ?? "Connecting..."}
            </div>
          </section>

          {error && (
            <div className="error-banner">
              {error}
              <button onClick={loadDashboard}>Retry</button>
            </div>
          )}

          <div className="dashboard-toolbar">
            <span>
              {loading
                ? "Loading dashboard..."
                : lastUpdated
                  ? `Last updated: ${lastUpdated.toLocaleTimeString()}`
                  : "Waiting for data"}
            </span>

            <button
              className="refresh-button"
              onClick={() => {
                loadDashboard();
                loadHistoricalMetrics();
              }}
              disabled={loading || historyLoading}
            >
              <RefreshCw size={14} />
              Refresh
            </button>
          </div>

          <section className="stats-grid">
            <StatCard
              title="Total Nodes"
              value={metrics?.nodes ?? "--"}
              subtitle="Connected to cluster"
              icon={Server}
              color="blue"
            />

            <StatCard
              title="Active Incidents"
              value={stats?.active_incidents ?? "--"}
              subtitle="Unresolved incidents"
              icon={AlertTriangle}
              color="orange"
            />

            <StatCard
              title="Resolved Incidents"
              value={stats?.resolved_incidents ?? "--"}
              subtitle="Historical incidents"
              icon={CheckCircle2}
              color="green"
            />

            <StatCard
              title="Running Pods"
              value={
                clusterHealth?.running_pods ??
                metrics?.pods ??
                "--"
              }
              subtitle="Cluster workloads"
              icon={Activity}
              color="purple"
            />
          </section>

          <section className="section-title">
            <div>
              <h2>Resource Utilization</h2>
              <p>Historical cluster resource consumption</p>
            </div>

            <span className="live-indicator">
              <span className="status-dot" />
              Live metrics · 15s refresh
            </span>
          </section>

          {/* Historical time range selector */}
          <div className="time-range-selector">
            <span>Time range</span>

            {(["15m", "1h", "6h", "24h"] as TimeRange[]).map(
              (range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={
                    timeRange === range ? "active" : ""
                  }
                  disabled={historyLoading}
                >
                  {range}
                </button>
              )
            )}
          </div>

          {historyError && (
            <div className="error-banner">
              {historyError}
              <button onClick={loadHistoricalMetrics}>
                Retry
              </button>
            </div>
          )}

          <section className="charts-grid">
            <ResourceChart
              title="CPU Utilization"
              value={
                metrics ? `${cpuUsage.toFixed(2)}%` : "--"
              }
              subtitle={
                historyLoading
                  ? "Loading historical data..."
                  : metrics
                    ? `${metrics.cpu.usage_cores.toFixed(2)} / ${metrics.cpu.capacity_cores.toFixed(2)} CPU cores`
                    : "Waiting for metrics"
              }
              color="#818cf8"
              data={cpuHistory}
            />

            <ResourceChart
              title="Memory Utilization"
              value={
                metrics
                  ? `${memoryUsage.toFixed(2)}%`
                  : "--"
              }
              subtitle={
                historyLoading
                  ? "Loading historical data..."
                  : metrics
                    ? `${metrics.memory.usage_mib.toFixed(2)} MiB used`
                    : "Waiting for metrics"
              }
              color="#22d3ee"
              data={memoryHistory}
            />
          </section>

          <section className="bottom-grid">
            <RecentIncidents incidents={incidents} />

            <div className="quick-insights">
              <div className="section-header">
                <div>
                  <h3>Infrastructure Health</h3>
                  <p>Connected platform services</p>
                </div>
              </div>

              <div className="health-item">
                <div className="health-icon blue">
                  <Cpu size={18} />
                </div>

                <div>
                  <strong>CPU Monitoring</strong>
                  <span>Metrics Server</span>
                </div>

                <span className="health-check">
                  {metrics ? "Connected" : "Unavailable"}
                </span>
              </div>

              <div className="health-item">
                <div className="health-icon purple">
                  <MemoryStick size={18} />
                </div>

                <div>
                  <strong>Memory Monitoring</strong>
                  <span>Metrics Server</span>
                </div>

                <span className="health-check">
                  {metrics ? "Connected" : "Unavailable"}
                </span>
              </div>

              <div className="health-item">
                <div className="health-icon green">
                  <CheckCircle2 size={18} />
                </div>

                <div>
                  <strong>Incident Management</strong>
                  <span>MongoDB</span>
                </div>

                <span className="health-check">
                  {stats ? "Connected" : "Unavailable"}
                </span>
              </div>
            </div>
          </section>

          <footer className="dashboard-footer">
            KubeWise AI · Intelligent Kubernetes Observability Platform
          </footer>
        </div>
      </main>
    </div>
  );
}