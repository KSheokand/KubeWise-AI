# KubeWise AI 🚀
### Intelligent Kubernetes Observability & AI-Powered Root Cause Analysis Platform

KubeWise AI is a Kubernetes observability platform designed to monitor cluster health, analyze workload performance, detect infrastructure anomalies, and manage incidents through a centralized dashboard.

The platform integrates Kubernetes metrics, Prometheus monitoring, Loki log aggregation, and MongoDB-based incident management to provide real-time visibility into containerized infrastructure.

The long-term objective is to introduce AI-powered multi-agent reasoning for automated anomaly investigation, root cause analysis, and predictive resource optimization.

---

## 📌 Project Overview

Managing Kubernetes infrastructure requires monitoring multiple components, including nodes, pods, deployments, resource consumption, logs, and application failures.

KubeWise AI aims to simplify this process by bringing infrastructure monitoring and incident intelligence into one unified platform.

### Key Objectives

- Monitor Kubernetes cluster and node health.
- Track pod-level CPU and memory utilization.
- Monitor workload readiness and container restarts.
- Collect and analyze Kubernetes application logs.
- Detect abnormal resource consumption and container failures.
- Maintain persistent incident records and event timelines.
- Provide historical resource utilization visualizations.
- Build an extensible foundation for AI-driven root cause analysis.

---

## ✨ Features Implemented

### 1. Kubernetes Cluster Monitoring

- Kubernetes cluster health monitoring.
- Node status and resource information.
- Namespace discovery.
- Pod inventory across namespaces.
- Deployment monitoring.
- Container readiness tracking.
- Pod restart count monitoring.
- Container state inspection.

### 2. Resource Monitoring

Integrated Kubernetes Metrics Server and Prometheus for infrastructure monitoring.

**Metrics include:**
- Node CPU utilization.
- Node memory utilization.
- Pod-level CPU consumption.
- Pod-level memory consumption.
- Historical CPU utilization.
- Historical memory utilization.
- Namespace-level workload analysis.

Historical metrics are visualized using interactive charts.

### 3. Prometheus Integration

Prometheus provides time-series metrics collection and querying.

Implemented capabilities:
- Instant metric queries.
- Historical range queries.
- CPU utilization monitoring.
- Memory utilization monitoring.
- Pod-level resource monitoring.
- Restart-related metric queries.

### 4. Centralized Log Monitoring

Integrated Grafana Loki and Grafana Alloy for Kubernetes log collection.

- Kubernetes pod log collection.
- Centralized log aggregation.
- Loki-based log querying.
- Container log visibility.

### 5. Anomaly Detection Engine

Implemented a rule-based anomaly detection engine using Prometheus metrics.

Currently monitored conditions include:

| Anomaly | Detection Condition |
|---|---|
| High Node CPU | CPU utilization ≥ 80% |
| Critical Node CPU | CPU utilization ≥ 95% |
| High Node Memory | Memory utilization ≥ 85% |
| Critical Node Memory | Memory utilization ≥ 95% |
| High Pod CPU | CPU utilization ≥ 80% |
| Critical Pod CPU | CPU utilization ≥ 95% |
| High Pod Memory | Memory utilization ≥ 85% |
| Critical Pod Memory | Memory utilization ≥ 95% |
| Pod Restarts | Restart activity within a 10-minute window |
| Container Failures | OOMKilled, CrashLoopBackOff, ImagePullBackOff and related failures |

The engine classifies anomalies according to severity and generates associated evidence and recommendations.

### 6. Incident Management

Integrated MongoDB for persistent incident storage.

Implemented capabilities:
- Automatic incident creation from detected anomalies.
- Incident deduplication using fingerprints.
- Active and resolved incident tracking.
- Incident severity classification.
- Incident occurrence tracking.
- Incident event history.
- Incident resolution.
- Manual incident resolution.
- Incident statistics and filtering.

Each incident maintains its lifecycle, including creation, updates, and resolution events.

### 7. Interactive Web Dashboard

Built a Next.js dashboard for infrastructure visibility.

**Dashboard**
- Cluster health overview.
- Node and pod statistics.
- Active and resolved incident statistics.
- CPU and memory utilization charts.
- Recent incident information.
- Automatic dashboard refresh.

**Incident Management**
- Incident listing.
- Severity and status filtering.
- Incident search.
- Incident details drawer.
- Incident event timeline.
- Manual incident resolution.

**Workload Monitoring**
- Kubernetes pod inventory.
- Namespace filtering.
- Pod-level CPU and memory consumption.
- Resource consumption rankings.
- Historical Prometheus metrics.
- Pod health and readiness information.

---

## 🏗️ System Architecture

```text
                 KUBERNETES CLUSTER
                         |
          +--------------+--------------+
          |              |              |
       Nodes           Pods        Deployments
          |              |              |
          +--------------+--------------+
                         |
               Kubernetes API
                         |
          +--------------+--------------+
          |              |              |
    Metrics Server   Prometheus      Loki
          |              |              |
          |         Time-Series      Alloy
          |           Metrics          |
          |              |          Pod Logs
          +--------------+--------------+
                         |
                  FastAPI Backend
                         |
          +--------------+--------------+
          |              |              |
      Kubernetes     Prometheus       Loki
       Service        Service        Service
          |              |              |
          +--------------+--------------+
                         |
                Anomaly Detection
                         |
                  Incident Service
                         |
                     MongoDB
                         |
                  REST API Layer
                         |
                 Next.js Frontend
                         |
              KubeWise AI Dashboard
```

### Planned AI Architecture

The following capabilities are planned for future development:

```text
              Observability Data
                      |
              Anomaly Detection
                      |
               Agent Orchestrator
                      |
        +-------------+-------------+
        |             |             |
     Metrics       Logs Agent    Kubernetes
      Agent                       Agent
        |             |             |
        +-------------+-------------+
                      |
              Root Cause Analysis
                      |
             Recommended Actions
                      |
             Predictive Insights
```

*The AI agent architecture is a planned extension, not a currently implemented feature.*

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Styling | Tailwind CSS, CSS |
| Charts | Recharts |
| Icons | Lucide React |
| Backend | Python, FastAPI |
| API Communication | REST APIs, HTTPX |
| Database | MongoDB Atlas |
| Kubernetes Integration | Kubernetes Python Client |
| Containerization | Docker |
| Local Kubernetes | Kind |
| Cluster Metrics | Kubernetes Metrics Server |
| Monitoring | Prometheus |
| Logging | Grafana Loki |
| Log Collection | Grafana Alloy |
| Package Management | Helm |
| Version Control | Git, GitHub |

---

## 📂 Project Structure

```text
KubeWise-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── anomalies.py
│   │   │       ├── cluster.py
│   │   │       ├── deployments.py
│   │   │       ├── incidents.py
│   │   │       ├── logs.py
│   │   │       ├── metrics.py
│   │   │       ├── namespaces.py
│   │   │       ├── nodes.py
│   │   │       ├── pods.py
│   │   │       └── prometheus.py
│   │   │
│   │   ├── core/
│   │   │   ├── database.py
│   │   │   └── kubernetes_client.py
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── services/
│   │   │   ├── anomaly_service.py
│   │   │   ├── incident_service.py
│   │   │   ├── kubernetes_service.py
│   │   │   ├── loki_service.py
│   │   │   ├── metrics_service.py
│   │   │   └── prometheus_service.py
│   │   │
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── incidents/
│   │   │   ├── workloads/
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   ├── incidents/
│   │   │   ├── layout/
│   │   │   └── workloads/
│   │   │
│   │   └── lib/
│   │       ├── api.ts
│   │       └── metrics.ts
│   │
│   └── package.json
│
├── infrastructure/
│   ├── alloy/
│   ├── kubernetes/
│   │   ├── demo/
│   │   └── kind-config.yaml
│   ├── loki/
│   └── prometheus/
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation and Setup

### Prerequisites

Install the following tools:

- Python 3.12+
- Node.js 22+
- npm
- Docker
- kubectl
- Kind
- Helm
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/KSheokand/KubeWise-AI.git

cd KubeWise-AI
```

### 2. Configure the Kubernetes Cluster

Create the local Kind cluster using the provided configuration:

```bash
kind create cluster \
  --name kubewise-local \
  --config infrastructure/kubernetes/kind-config.yaml
```

Verify the cluster:

```bash
kubectl cluster-info

kubectl get nodes
```

### 3. Configure the Backend

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside the backend directory:

```env
MONGODB_URL=your_mongodb_connection_string
MONGODB_DATABASE=KubeWiseAI
```

Start the backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

### 4. Configure the Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

Frontend dashboard:

```text
http://localhost:3000
```

### 5. Infrastructure Monitoring

Prometheus, Loki, and Alloy are configured through Helm values and Kubernetes configuration files under `infrastructure/`.

Ensure the monitoring components are installed and running in their respective namespaces.

Useful verification commands:

```bash
kubectl get pods -A

kubectl top nodes

kubectl top pods -A
```

Prometheus UI:

```bash
kubectl port-forward -n monitoring \
  service/prometheus-server 9090:80
```

Open:

```text
http://localhost:9090
```

Loki can be accessed locally through port forwarding on port `3100` when its service is configured accordingly.

---

## 🔌 Backend API Endpoints

The backend exposes REST APIs under `/api/v1`.

| Module | Endpoint | Description |
|---|---|---|
| Cluster | `/cluster/health` | Cluster health summary |
| Nodes | `/nodes/` | Node inventory |
| Pods | `/pods/` | Kubernetes pod inventory |
| Deployments | `/deployments/` | Deployment information |
| Namespaces | `/namespaces/` | Namespace inventory |
| Metrics | `/metrics/summary` | Cluster resource summary |
| Metrics | `/metrics/nodes` | Node resource metrics |
| Metrics | `/metrics/pods` | Pod resource metrics |
| Prometheus | `/prometheus/` | Prometheus queries |
| Anomalies | `/anomalies/` | Detected anomalies |
| Anomalies | `/anomalies/scan` | Run anomaly detection and synchronize incidents |
| Incidents | `/incidents/` | Incident listing |
| Incidents | `/incidents/active` | Active incidents |
| Incidents | `/incidents/stats` | Incident statistics |
| Incidents | `/incidents/history` | Incident event history |
| Logs | `/logs/` | Log querying |

Refer to the interactive Swagger documentation for request parameters and response schemas.

---

## 🧪 Testing and Validation

The monitoring pipeline has been tested against a local Kind Kubernetes cluster.

Implemented validation scenarios include:

- High CPU utilization using a CPU stress workload.
- High memory utilization using a memory stress workload.
- Container startup failures.
- CrashLoopBackOff detection.
- Pod restart anomaly detection.
- Automatic incident creation.
- Incident resolution after anomalies disappear.
- Historical CPU and memory queries through Prometheus.
- Kubernetes pod inventory and readiness retrieval.

These tests help validate the integration between Kubernetes, Prometheus, the anomaly detection engine, MongoDB, and the frontend.

---

## 🗺️ Development Roadmap

### Phase 1 — Infrastructure and Observability Foundation
- [x] Local Kubernetes cluster using Kind.
- [x] Kubernetes API integration.
- [x] Metrics Server integration.
- [x] Prometheus integration.
- [x] Loki log aggregation.
- [x] Alloy log collection.

### Phase 2 — Backend Development
- [x] FastAPI backend.
- [x] Cluster health APIs.
- [x] Node and pod monitoring.
- [x] Deployment and namespace APIs.
- [x] Historical metrics APIs.
- [x] Anomaly detection engine.

### Phase 3 — Incident Management
- [x] MongoDB integration.
- [x] Persistent incident storage.
- [x] Incident deduplication.
- [x] Incident lifecycle management.
- [x] Incident event history.
- [x] Manual resolution.

### Phase 4 — Frontend Development
- [x] Dashboard.
- [x] Historical resource charts.
- [x] Incident management interface.
- [x] Incident timeline.
- [x] Workload monitoring page.
- [x] Kubernetes pod health integration.

### Phase 5 — Advanced Intelligence (Planned)
- [ ] AI-powered root cause analysis.
- [ ] Multi-agent observability architecture.
- [ ] Automated log and metric correlation.
- [ ] Dependency mapping.
- [ ] Predictive resource forecasting.
- [ ] Intelligent remediation recommendations.
- [ ] Automated remediation workflows.

---

## 🔮 Future Vision

KubeWise AI aims to evolve beyond traditional infrastructure monitoring into an intelligent observability and operations platform.

The planned AI capabilities will help correlate metrics, logs, Kubernetes events, and workload dependencies to identify the underlying causes of infrastructure incidents.

The ultimate goal is to reduce manual investigation, improve incident response, and enable predictive infrastructure management.

---

## 👨‍💻 Author

**Kartikeya Sheokand**

GitHub: [@KSheokand](https://github.com/KSheokand)

Project Repository: [KubeWise-AI](https://github.com/KSheokand/KubeWise-AI)

---
