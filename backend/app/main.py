from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import connect_database, close_database

from app.api.routes import (
    cluster,
    nodes,
    pods,
    deployments,
    namespaces,
    metrics,
    prometheus,
    logs,
    anomalies,
    incidents
)

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting Kubernetes AI...")
    await connect_database()

    print("KubeWise AI startup completed.")

    yield

    print("Shutting down KubeWise AI...")
    await close_database()

app = FastAPI(
    title="KubeWise AI",
    description=(
        "Intelligent Kubernetes Observability Platform "
        "with AI-powered infrastructure monitoring."
    ),
    version="0.1.0",
    lifespan=lifespan
)


# Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Root endpoint
@app.get("/")
def root():

    return {
        "message": "Welcome to KubeWise AI",
        "version": "0.1.0",
        "status": "running"
    }


# Backend health
@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "kubewise-backend"
    }


# API routes
app.include_router(
    cluster.router,
    prefix="/api/v1/cluster",
    tags=["Cluster"]
)

app.include_router(
    nodes.router,
    prefix="/api/v1/nodes",
    tags=["Nodes"]
)

app.include_router(
    pods.router,
    prefix="/api/v1/pods",
    tags=["Pods"]
)

app.include_router(
    deployments.router,
    prefix="/api/v1/deployments",
    tags=["Deployments"]
)

app.include_router(
    namespaces.router,
    prefix="/api/v1/namespaces",
    tags=["Namespaces"]
)

app.include_router(
    metrics.router,
    prefix="/api/v1/metrics",
    tags=["Metrics"]
)

app.include_router(
    prometheus.router,
    prefix="/api/v1/prometheus",
    tags=["Prometheus"]
)

app.include_router(
    logs.router,
    prefix="/api/v1/logs",
    tags=["Logs"]
)

app.include_router(
    anomalies.router,
    prefix="/api/v1/anomalies",
    tags=["Anomaly Detection"]
)

app.include_router(
    incidents.router,
    prefix="/api/v1/incidents",
    tags=["Incident Management"]
)