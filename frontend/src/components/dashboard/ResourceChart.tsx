"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ResourceChartProps {
  title: string;
  value: string;
  subtitle: string;
  color: string;
  data: { time: string; usage: number }[];
}

export default function ResourceChart({
  title,
  value,
  subtitle,
  color,
  data,
}: ResourceChartProps) {
  return (
    <div className="chart-card">
      <div className="chart-header">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>

        <div className="chart-value">{value}</div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id={`gradient-${color}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>

            <XAxis
              dataKey="time"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#717b91", fontSize: 11 }}
            />

            <YAxis
              domain={[0, 100]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#717b91", fontSize: 11 }}
              tickFormatter={(value) => `${value}%`}
            />

            <Tooltip
              contentStyle={{
                background: "#151c2c",
                border: "1px solid #29334a",
                borderRadius: "8px",
                color: "#fff",
              }}
              formatter={(value) => [`${value}%`, "Usage"]}
            />

            <Area
              type="monotone"
              dataKey="usage"
              stroke={color}
              strokeWidth={2}
              fill={`url(#gradient-${color})`}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}