from fastapi import APIRouter, HTTPException

from app.services.anomaly_service import anomaly_service
from app.services.incident_service import incident_service


router = APIRouter()


@router.get("/")
async def get_anomalies():
    try:
        return await anomaly_service.scan()

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Anomaly detection failed: {str(exc)}"
        )


@router.get("/summary")
async def get_anomaly_summary():
    try:
        result = await anomaly_service.scan()

        return {
            "timestamp": result["timestamp"],
            "total_anomalies": result["total_anomalies"],
            "summary": result["summary"]
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to retrieve anomaly summary: {str(exc)}"
        )

@router.post("/scan")
async def scan_and_sync_incidents():

    try:
        result = await anomaly_service.scan()

        if result.get("status") != "success":
            raise HTTPException(
                status_code=502,
                detail="Anomaly scan was not successful. Incidents were not synchronized."            
            )

        incident_result = await incident_service.sync_anomalies(
            result["anomalies"]
        )

        return {
            "status": "success",
            "message": "Anomaly scan completed and incidents synchronized.",
            "scan": result,
            "incident_sync": incident_result
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Incident synchronization failed: {str(exc)}"
        )