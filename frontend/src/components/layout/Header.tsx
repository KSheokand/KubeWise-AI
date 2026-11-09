"use client";

import { Bell, Search, Command } from "lucide-react";

export default function Header() {
  return (
    <header className="topbar">
      <div className="breadcrumb">
        <span>Workspace</span>
        <span className="breadcrumb-divider">/</span>
        <strong>Overview</strong>
      </div>

      <div className="header-actions">
        <div className="search-box">
          <Search size={16} />
          <span>Search anything...</span>
          <kbd><Command size={11} /> K</kbd>
        </div>

        <button className="icon-button" aria-label="Notifications">
          <Bell size={19} />
          <span className="notification-dot" />
        </button>

        <div className="user-avatar">K</div>
      </div>
    </header>
  );
}