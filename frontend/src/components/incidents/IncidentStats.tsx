import {
  AlertTriangle,
  CheckCircle2,
  Activity,
  ShieldAlert,
} from "lucide-react";

import type { IncidentStats as IncidentStatsType } from "@/lib/api";

interface Props {
  stats: IncidentStatsType | null;
}

export default function IncidentStats({ stats }: Props) {
  const cards = [
    {
      title: "Total Incidents",
      value: stats?.total_incidents ?? "--",
      icon: Activity,
      color: "blue",
    },
    {
      title: "Active Incidents",
      value: stats?.active_incidents ?? "--",
      icon: AlertTriangle,
      color: "orange",
    },
    {
      title: "Critical Incidents",
      value: stats?.severity_breakdown.critical ?? "--",
      icon: ShieldAlert,
      color: "red",
    },
    {
      title: "Resolved Incidents",
      value: stats?.resolved_incidents ?? "--",
      icon: CheckCircle2,
      color: "green",
    },
  ];

  return (
    <div className="incident-stats-grid">
      {cards.map((card) => {
        const Icon = card.icon;

        return (
          <div className="incident-stat-card" key={card.title}>
            <div className="incident-stat-heading">
              <span>{card.title}</span>
              <div className={`incident-stat-icon ${card.color}`}>
                <Icon size={19} />
              </div>
            </div>

            <strong>{card.value}</strong>
          </div>
        );
      })}
    </div>
  );
}