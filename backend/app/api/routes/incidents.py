from fastapi import APIRouter, HTTPException, Query

from app.services.incident_service import incident_service


router = APIRouter()


# List all incidents with optional filters
@router.get("/")
async def get_all_incidents(
    status: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    skip: int = Query(default=0, ge=0)
):
    try:
        if status and status not in ["active", "resolved"]:
            raise HTTPException(
                status_code=400,
                detail="Status must be active or resolved."
            )

        if severity and severity not in ["critical", "warning"]:
            raise HTTPException(
                status_code=400,
                detail="Severity must be critical or warning."
            )

        return await incident_service.get_all_incidents(
            status=status,
            severity=severity,
            limit=limit,
            skip=skip
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve incidents: {str(exc)}"
        )


# List active incidents
@router.get("/active")
async def get_active_incidents():

    try:
        incidents = await incident_service.get_active_incidents()

        return {
            "total": len(incidents),
            "incidents": incidents
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve active incidents: {str(exc)}"
        )


# Incident statistics
@router.get("/stats")
async def get_incident_stats():

    try:
        return await incident_service.get_incident_stats()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve incident statistics: {str(exc)}"
        )


# Incident event history
@router.get("/history")
async def get_incident_history(
    incident_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    skip: int = Query(default=0, ge=0)
):

    try:
        return await incident_service.get_all_history(
            incident_id=incident_id,
            limit=limit,
            skip=skip
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve incident history: {str(exc)}"
        )


# Manually resolve an incident
@router.patch("/{incident_id}/resolve")
async def resolve_incident(incident_id: str):

    try:
        incident = await incident_service.resolve_incident(
            incident_id
        )

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found."
            )

        return {
            "status": "success",
            "message": "Incident resolved successfully.",
            "incident": incident
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to resolve incident: {str(exc)}"
        )


# Get one incident by ID
@router.get("/{incident_id}")
async def get_incident(incident_id: str):

    try:
        incident = await incident_service.get_incident(
            incident_id
        )

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found."
            )

        history = await incident_service.get_incident_history(
            incident_id
        )

        return {
            "incident": incident,
            "history": history
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve incident: {str(exc)}"
        )