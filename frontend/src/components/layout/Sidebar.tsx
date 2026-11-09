"use client";

import {
  LayoutDashboard,
  Activity,
  Server,
  Box,
  AlertTriangle,
  FileText,
  Settings,
  Network,
  ShieldCheck,
} from "lucide-react";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  {
    title: "OVERVIEW",
    items: [
      { name: "Dashboard", icon: LayoutDashboard, href: "/" },
      { name: "Incidents", icon: AlertTriangle, href: "/incidents" },
    ],
  },
  {
    title: "INFRASTRUCTURE",
    items: [
      { name: "Clusters", icon: Server, href: "/clusters" },
      { name: "Workloads", icon: Box, href: "/workloads" },
      { name: "Monitoring", icon: Activity, href: "/monitoring" },
      { name: "Service Map", icon: Network, href: "/service-map" },
    ],
  },
  {
    title: "MANAGEMENT",
    items: [
      { name: "Logs", icon: FileText, href: "/logs" },
      { name: "Settings", icon: Settings, href: "/settings" },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <ShieldCheck size={23} />
        </div>

        <div>
          <h1>KubeWise</h1>
          <span>INTELLIGENT OBSERVABILITY</span>
        </div>
      </div>

      <div className="workspace">
        <div className="workspace-avatar">K</div>
        <div className="workspace-info">
          <strong>Local Workspace</strong>
          <span>Development Environment</span>
        </div>
      </div>

      <nav className="sidebar-navigation">
        {navigation.map((section) => (
          <div key={section.title} className="nav-section">
            <p className="nav-heading">{section.title}</p>

            {section.items.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`nav-link ${active ? "active" : ""}`}
                >
                  <Icon size={18} />
                  <span>{item.name}</span>

                  {item.name === "Incidents" && (
                    <span className="nav-indicator" />
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="system-status">
          <span className="status-dot" />
          <div>
            <strong>System Operational</strong>
            <span>All services connected</span>
          </div>
        </div>

        <div className="version">KubeWise AI · v0.1.0</div>
      </div>
    </aside>
  );
}