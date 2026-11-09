"use client";

import { Eye, CheckCircle2, AlertTriangle } from "lucide-react";

import type { Incident } from "@/lib/api";

interface Props {
  incidents: Incident[];
  onSelect: (incident: Incident) => void;
  onResolve: (id: string) => void;
  resolvingId: string | null;
}

export default function IncidentTable({
  incidents,
  onSelect,
  onResolve,
  resolvingId,
}: Props) {
  if (incidents.length === 0) {
    return (
      <div className="incident-empty">
        <CheckCircle2 size={30} />
        <h3>No incidents found</h3>
        <p>Try changing your filters or search query.</p>
      </div>
    );
  }

  return (
    <div className="incident-table-wrapper">
      <table className="incident-table">
        <thead>
          <tr>
            <th>INCIDENT</th>
            <th>RESOURCE</th>
            <th>SEVERITY</th>
            <th>STATUS</th>
            <th>OCCURRENCES</th>
            <th>LAST DETECTED</th>
            <th>ACTIONS</th>
          </tr>
        </thead>

        <tbody>
          {incidents.map((incident) => (
            <tr key={incident.incident_id}>
              <td>
                <div className="incident-name-cell">
                  <AlertTriangle size={17} />
                  <div>
                    <strong>
                      {incident.type.replaceAll("_", " ")}
                    </strong>
                    <small>
                      {incident.incident_id.slice(0, 13)}...
                    </small>
                  </div>
                </div>
              </td>

              <td>
                <span className="resource-name">
                  {incident.resource_name}
                </span>
              </td>

              <td>
                <span className={`severity-badge ${incident.severity}`}>
                  {incident.severity}
                </span>
              </td>

              <td>
                <span
                  className={`incident-status ${incident.status}`}
                >
                  {incident.status}
                </span>
              </td>

              <td>{incident.occurrence_count}</td>

              <td>
                {new Date(incident.last_seen).toLocaleString()}
              </td>

              <td>
                <div className="incident-actions">
                  <button
                    className="action-button"
                    onClick={() => onSelect(incident)}
                    title="View incident"
                  >
                    <Eye size={16} />
                  </button>

                  {incident.status === "active" && (
                    <button
                      className="resolve-button"
                      onClick={() => onResolve(incident.incident_id)}
                      disabled={resolvingId === incident.incident_id}
                    >
                      {resolvingId === incident.incident_id
                        ? "Resolving..."
                        : "Resolve"}
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}