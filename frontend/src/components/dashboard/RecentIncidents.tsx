import { AlertTriangle, ArrowUpRight } from "lucide-react";
import Link from "next/link";
import type { Incident } from "@/lib/api";

interface RecentIncidentsProps {
  incidents: Incident[];
}

export default function RecentIncidents({
  incidents,
}: RecentIncidentsProps) {
  return (
    <div className="incidents-card">
      <div className="section-header">
        <div>
          <h3>Recent Incidents</h3>
          <p>Latest infrastructure events</p>
        </div>

        <Link href="/incidents" className="view-all">
          View all <ArrowUpRight size={15} />
        </Link>
      </div>

      {incidents.length === 0 ? (
        <div className="empty-state">
          <AlertTriangle size={22} />
          <p>No incidents recorded yet.</p>
        </div>
      ) : (
        incidents.slice(0, 5).map((incident) => (
          <div key={incident.incident_id} className="incident-row">
            <div className="incident-icon">
              <AlertTriangle size={18} />
            </div>

            <div className="incident-information">
              <strong>{incident.type.replaceAll("_", " ")}</strong>
              <span>{incident.resource_name}</span>
              <small>
                {new Date(incident.last_seen).toLocaleString()}
              </small>
            </div>

            <div className="incident-badges">
              <span className={`severity-badge ${incident.severity}`}>
                {incident.severity}
              </span>

              <span
                className={
                  incident.status === "resolved"
                    ? "resolved-badge"
                    : "active-badge"
                }
              >
                {incident.status}
              </span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}