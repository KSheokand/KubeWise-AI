"use client";

import {
  X,
  Clock,
  Server,
  Activity,
} from "lucide-react";

import type {
  Incident,
  IncidentEvent,
} from "@/lib/api";

import IncidentTimeline from "./IncidentTimeline";

interface Props {
  incident: Incident | null;
  events: IncidentEvent[];
  loadingHistory: boolean;
  onClose: () => void;
}

export default function IncidentDetails({
  incident,
  events,
  loadingHistory,
  onClose,
}: Props) {
  if (!incident) return null;

  return (
    <div className="details-overlay" onClick={onClose}>
      <aside
        className="incident-details-panel"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="details-header">
          <div>
            <span className="eyebrow">INCIDENT DETAILS</span>
            <h2>Incident Investigation</h2>
          </div>

          <button onClick={onClose} className="details-close">
            <X size={20} />
          </button>
        </div>

        <div className="details-body">
          <div className="details-type">
            <span className={`severity-badge ${incident.severity}`}>
              {incident.severity}
            </span>

            <span className={`incident-status ${incident.status}`}>
              {incident.status}
            </span>
          </div>

          <h3>
            {incident.type.replaceAll("_", " ")}
          </h3>

          <p className="details-description">
            {incident.description}
          </p>

          <div className="details-section">
            <h4>
              <Server size={16} />
              Resource Information
            </h4>

            <div className="details-field">
              <span>Resource type</span>
              <strong>{incident.resource}</strong>
            </div>

            <div className="details-field">
              <span>Resource name</span>
              <strong>{incident.resource_name}</strong>
            </div>

            <div className="details-field">
              <span>Incident ID</span>
              <strong className="break-id">
                {incident.incident_id}
              </strong>
            </div>
          </div>

          <div className="details-section">
            <h4>
              <Activity size={16} />
              Incident Information
            </h4>

            <div className="details-field">
              <span>Occurrences</span>
              <strong>{incident.occurrence_count}</strong>
            </div>

            <div className="details-field">
              <span>First detected</span>
              <strong>
                {new Date(incident.first_seen).toLocaleString()}
              </strong>
            </div>

            <div className="details-field">
              <span>Last detected</span>
              <strong>
                {new Date(incident.last_seen).toLocaleString()}
              </strong>
            </div>

            {incident.resolved_at && (
              <div className="details-field">
                <span>Resolved at</span>
                <strong>
                  {new Date(incident.resolved_at).toLocaleString()}
                </strong>
              </div>
            )}
          </div>

          {incident.recommendation && (
            <div className="recommendation-box">
              <h4>Recommended Action</h4>
              <p>{incident.recommendation}</p>
            </div>
          )}

          <div className="details-section">
            <h4>
              <Clock size={16} />
              Event Timeline
            </h4>

            <IncidentTimeline
              events={events}
              loading={loadingHistory}
            />
          </div>

          <div className="incident-fingerprint">
            Fingerprint: {incident.fingerprint}
          </div>
        </div>
      </aside>
    </div>
  );
}