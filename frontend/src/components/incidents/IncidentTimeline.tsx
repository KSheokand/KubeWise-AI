import {
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Clock,
  Activity,
} from "lucide-react";

import type { IncidentEvent } from "@/lib/api";

interface Props {
  events: IncidentEvent[];
  loading?: boolean;
}

const eventConfig: Record<
  string,
  { label: string; description: string; color: string }
> = {
  created: {
    label: "Incident Created",
    description: "A new infrastructure incident was detected.",
    color: "created",
  },

  updated: {
    label: "Incident Updated",
    description: "New anomaly evidence was recorded.",
    color: "updated",
  },

  resolved: {
    label: "Incident Resolved",
    description: "The incident was automatically resolved.",
    color: "resolved",
  },

  manually_resolved: {
    label: "Manually Resolved",
    description: "The incident was manually resolved.",
    color: "resolved",
  },
};

export default function IncidentTimeline({
  events,
  loading = false,
}: Props) {
  if (loading) {
    return (
      <div className="timeline-empty">
        Loading incident history...
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="timeline-empty">
        No event history available.
      </div>
    );
  }

  return (
    <div className="incident-timeline">
      {events.map((event, index) => {
        const config =
          eventConfig[event.event_type] ?? {
            label: event.event_type.replaceAll("_", " "),
            description: "An incident event was recorded.",
            color: "updated",
          };

        const Icon =
          event.event_type === "created"
            ? AlertTriangle
            : event.event_type.includes("resolved")
              ? CheckCircle2
              : event.event_type === "updated"
                ? RefreshCw
                : Activity;

        return (
          <div className="timeline-event" key={event.event_id}>
            <div className="timeline-marker">
              <div className={`timeline-icon ${config.color}`}>
                <Icon size={15} />
              </div>

              {index !== events.length - 1 && (
                <div className="timeline-line" />
              )}
            </div>

            <div className="timeline-content">
              <strong>{config.label}</strong>

              <p>{config.description}</p>

              {event.severity && (
                <span className={`severity-badge ${event.severity}`}>
                  {event.severity}
                </span>
              )}

              <div className="timeline-time">
                <Clock size={12} />

                {new Date(event.timestamp).toLocaleString()}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}