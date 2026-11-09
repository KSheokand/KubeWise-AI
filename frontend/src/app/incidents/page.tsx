"use client";

import { useCallback, useEffect, useState } from "react";

import {
  AlertTriangle,
  RefreshCw,
  Search,
  Filter,
} from "lucide-react";

import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

import IncidentStats from "@/components/incidents/IncidentStats";
import IncidentTable from "@/components/incidents/IncidentTable";
import IncidentDetails from "@/components/incidents/IncidentDetails";

import {
  getIncidents,
  getIncidentStats,
  resolveIncident,
  Incident,
  IncidentEvent,
  IncidentStats as IncidentStatsType,
  getIncidentHistory,
} from "@/lib/api";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [stats, setStats] = useState<IncidentStatsType | null>(null);

  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState("all");
  const [status, setStatus] = useState("all");

  const [selectedIncident, setSelectedIncident] =
    useState<Incident | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [resolvingId, setResolvingId] = useState<string | null>(null);

  const [events, setEvents] = useState<IncidentEvent[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setError("");

      const [incidentResult, statsResult] = await Promise.all([
        getIncidents(200),
        getIncidentStats(),
      ]);

      setIncidents(incidentResult.incidents);
      setStats(statsResult);
    } catch (err) {
      console.error(err);
      setError("Unable to load incidents. Check the backend connection.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();

    const interval = setInterval(loadData, 15000);

    return () => clearInterval(interval);
  }, [loadData]);

  const filteredIncidents = incidents.filter((incident) => {
    const matchesSearch =
      incident.resource_name.toLowerCase().includes(search.toLowerCase()) ||
      incident.type.toLowerCase().includes(search.toLowerCase()) ||
      incident.incident_id.toLowerCase().includes(search.toLowerCase());

    const matchesSeverity =
      severity === "all" || incident.severity === severity;

    const matchesStatus =
      status === "all" || incident.status === status;

    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const handleResolve = async (id: string) => {
    const confirmed = window.confirm(
      "Are you sure you want to manually resolve this incident?"
    );

    if (!confirmed) return;

    try {
      setResolvingId(id);

      await resolveIncident(id);

      await loadData();

      if (selectedIncident?.incident_id === id) {
        setSelectedIncident(null);
      }
    } catch (err) {
      console.error(err);
      setError("Unable to resolve incident.");
    } finally {
      setResolvingId(null);
    }
  };

  const handleSelectIncident = async (incident: Incident) => {
    setSelectedIncident(incident);
    setEvents([]);
    setLoadingHistory(true);

    try {
        const result = await getIncidentHistory(
            incident.incident_id
        );

        setEvents(result.events ?? []);
    } catch (error) {
        console.error("Unable to load incident history:", error);
        setEvents([]);
    } finally {
        setLoadingHistory(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Header />

        <div className="dashboard-content">
          <section className="page-heading">
            <div>
              <div className="eyebrow">INFRASTRUCTURE MONITORING</div>
              <h1>Incident Management</h1>
              <p>
                Investigate, monitor and manage Kubernetes incidents.
              </p>
            </div>

            <button
              className="refresh-button"
              onClick={loadData}
              disabled={loading}
            >
              <RefreshCw size={15} />
              Refresh
            </button>
          </section>

          <IncidentStats stats={stats} />

          {error && (
            <div className="error-banner">
              {error}
            </div>
          )}

          <section className="incident-management-card">
            <div className="incident-management-heading">
              <div>
                <h2>
                  <AlertTriangle size={19} />
                  All Incidents
                </h2>

                <p>
                  {filteredIncidents.length} incidents displayed
                </p>
              </div>
            </div>

            <div className="incident-filter-bar">
              <div className="incident-search">
                <Search size={17} />

                <input
                  type="text"
                  placeholder="Search incidents or resources..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </div>

              <div className="filter-control">
                <Filter size={15} />

                <select
                  value={severity}
                  onChange={(event) => setSeverity(event.target.value)}
                >
                  <option value="all">All Severities</option>
                  <option value="critical">Critical</option>
                  <option value="warning">Warning</option>
                </select>
              </div>

              <div className="filter-control">
                <select
                  value={status}
                  onChange={(event) => setStatus(event.target.value)}
                >
                  <option value="all">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
            </div>

            {loading ? (
              <div className="incident-loading">
                Loading incidents...
              </div>
            ) : (
              <IncidentTable
                incidents={filteredIncidents}
                onSelect={handleSelectIncident}
                onResolve={handleResolve}
                resolvingId={resolvingId}
              />
            )}
          </section>
        </div>
      </main>

      <IncidentDetails
        incident={selectedIncident}
        events={events}
        loadingHistory={loadingHistory}
        onClose={() => {
            setSelectedIncident(null);
            setEvents([]);
        }}
      />
    </div>
  );
}