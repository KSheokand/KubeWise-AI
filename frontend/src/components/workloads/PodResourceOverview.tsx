"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { Cpu, MemoryStick } from "lucide-react";

interface PodResource {
  namespace: string;
  pod: string;
  cpuCores: number;
  memoryMiB: number;
}

interface Props {
  pods: PodResource[];
}

export default function PodResourceOverview({ pods }: Props) {
  const topCPU = [...pods]
    .sort((a, b) => b.cpuCores - a.cpuCores)
    .slice(0, 10)
    .map((pod) => ({
      name: pod.pod.length > 20
        ? `${pod.pod.slice(0, 20)}...`
        : pod.pod,
      usage: Number((pod.cpuCores * 1000).toFixed(2)),
      namespace: pod.namespace,
    }));

  const topMemory = [...pods]
    .sort((a, b) => b.memoryMiB - a.memoryMiB)
    .slice(0, 10)
    .map((pod) => ({
      name: pod.pod.length > 20
        ? `${pod.pod.slice(0, 20)}...`
        : pod.pod,
      usage: Number(pod.memoryMiB.toFixed(2)),
      namespace: pod.namespace,
    }));

  const tooltipStyle = {
    background: "#151c2c",
    border: "1px solid #29334a",
    borderRadius: "8px",
    color: "#fff",
  };

  return (
    <div className="pod-overview-grid">
      <div className="chart-card">
        <div className="chart-header">
          <div>
            <h3>
              <Cpu size={17} /> Top CPU Consumers
            </h3>
            <p>Highest CPU-consuming pods</p>
          </div>
        </div>

        <div className="pod-chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topCPU} layout="vertical">
              <XAxis
                type="number"
                tick={{ fill: "#8993a8", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />

              <YAxis
                type="category"
                dataKey="name"
                width={130}
                tick={{ fill: "#a1abc0", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />

              <Tooltip
                contentStyle={tooltipStyle}
                formatter={(value) => [
                  `${value} mCPU`,
                  "CPU Usage",
                ]}
              />

              <Bar
                dataKey="usage"
                fill="#818cf8"
                radius={[0, 5, 5, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-header">
          <div>
            <h3>
              <MemoryStick size={17} /> Top Memory Consumers
            </h3>
            <p>Highest memory-consuming pods</p>
          </div>
        </div>

        <div className="pod-chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topMemory} layout="vertical">
              <XAxis
                type="number"
                tick={{ fill: "#8993a8", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />

              <YAxis
                type="category"
                dataKey="name"
                width={130}
                tick={{ fill: "#a1abc0", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />

              <Tooltip
                contentStyle={tooltipStyle}
                formatter={(value) => [
                  `${value} MiB`,
                  "Memory Usage",
                ]}
              />

              <Bar
                dataKey="usage"
                fill="#22d3ee"
                radius={[0, 5, 5, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}