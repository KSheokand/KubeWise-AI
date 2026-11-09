import hashlib
import json
import uuid

from datetime import datetime, timezone

from pymongo import ReturnDocument

from app.core.database import get_database


class IncidentService:

    @staticmethod
    def _now():
        return datetime.now(timezone.utc)

    @staticmethod
    def _generate_fingerprint(anomaly):
        """
        Generate a stable fingerprint for an anomaly.

        Repeated detections of the same type and resource
        should map to the same incident.
        """

        identity = {
            "type": anomaly.get("type"),
            "resource": anomaly.get("resource"),
            "resource_name": anomaly.get("resource_name")
        }

        raw = json.dumps(identity, sort_keys=True)

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _serialize(document):
        if document is None:
            return None

        document["_id"] = str(document["_id"])

        return document

    async def record_anomaly(self, anomaly):

        db = get_database()

        incidents = db.incidents
        events = db.incident_events

        now = self._now()

        fingerprint = self._generate_fingerprint(anomaly)

        incident_id = str(uuid.uuid4())

        # Create a new incident or update an existing active one.
        incident = await incidents.find_one_and_update(
            {
                "fingerprint": fingerprint,
                "status": "active"
            },
            {
                "$set": {
                    "severity": anomaly.get("severity", "warning"),
                    "description": anomaly.get("description"),
                    "recommendation": anomaly.get("recommendation"),
                    "last_seen": now,
                    "latest_evidence": anomaly,
                },
                "$setOnInsert": {
                    "incident_id": incident_id,
                    "fingerprint": fingerprint,
                    "type": anomaly.get("type"),
                    "resource": anomaly.get("resource"),
                    "resource_name": anomaly.get("resource_name"),
                    "status": "active",
                    "first_seen": now,
                    "created_at": now,
                },
                "$inc": {
                    "occurrence_count": 1
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        event_type = (
            "created"
            if incident["occurrence_count"] == 1
            else "updated"
        )

        await events.insert_one({
            "event_id": str(uuid.uuid4()),
            "incident_id": incident["incident_id"],
            "event_type": event_type,
            "severity": anomaly.get("severity"),
            "evidence": anomaly,
            "timestamp": now
        })

        return self._serialize(incident)

    async def sync_anomalies(self, anomalies):

        """
        Synchronize the latest anomaly scan with MongoDB.

        1. Create or update incidents for detected anomalies.
        2. Resolve active incidents that are no longer detected.
        """

        db = get_database()

        incidents = db.incidents
        events = db.incident_events

        current_fingerprints = set()

        recorded_incidents = []

        # Create or update incidents.
        for anomaly in anomalies:

            fingerprint = self._generate_fingerprint(anomaly)

            current_fingerprints.add(fingerprint)

            incident = await self.record_anomaly(anomaly)

            recorded_incidents.append(incident)

        # Find active incidents that were not detected in this scan.
        active_cursor = incidents.find({
            "status": "active"
        })

        async for incident in active_cursor:

            if incident["fingerprint"] in current_fingerprints:
                continue

            now = self._now()

            await incidents.update_one(
                {
                    "incident_id": incident["incident_id"],
                    "status": "active"
                },
                {
                    "$set": {
                        "status": "resolved",
                        "resolved_at": now,
                        "last_seen": incident["last_seen"]
                    }
                }
            )

            await events.insert_one({
                "event_id": str(uuid.uuid4()),
                "incident_id": incident["incident_id"],
                "event_type": "resolved",
                "timestamp": now
            })

        return {
            "detected": len(recorded_incidents),
            "active_incidents": len(current_fingerprints),
            "incidents": recorded_incidents
        }

    async def get_active_incidents(self):

        db = get_database()

        cursor = db.incidents.find(
            {"status": "active"}
        ).sort("last_seen", -1)

        results = []

        async for document in cursor:
            results.append(self._serialize(document))

        return results

    async def get_incident(self, incident_id):

        db = get_database()

        incident = await db.incidents.find_one({
            "incident_id": incident_id
        })

        return self._serialize(incident)

    async def get_incident_history(self, incident_id):

        db = get_database()

        cursor = db.incident_events.find(
            {"incident_id": incident_id}
        ).sort("timestamp", 1)

        history = []

        async for event in cursor:

            event["_id"] = str(event["_id"])

            history.append(event)

        return history

    async def get_all_incidents(
        self,
        status=None,
        severity=None,
        limit=50,
        skip=0
    ):
        db = get_database()

        filters = {}

        if status:
            filters["status"] = status

        if severity:
            filters["severity"] = severity

        cursor = (
            db.incidents.find(filters)
            .sort("last_seen", -1)
            .skip(skip)
            .limit(limit)
        )

        results = []

        async for document in cursor:
            results.append(self._serialize(document))

        total = await db.incidents.count_documents(filters)

        return {
            "total": total,
            "limit": limit,
            "skip": skip,
            "incidents": results
        }

    async def resolve_incident(self, incident_id):

        db = get_database()

        now = self._now()

        incident = await db.incidents.find_one({
            "incident_id": incident_id
        })

        if incident is None:
            return None

        if incident.get("status") == "resolved":
            return self._serialize(incident)

        updated = await db.incidents.find_one_and_update(
            {
                "incident_id": incident_id,
                "status": "active"
            },
            {
                "$set": {
                    "status": "resolved",
                    "resolved_at": now
                }
            },
            return_document=ReturnDocument.AFTER
        )

        if updated is None:
            return self._serialize(
                await db.incidents.find_one({
                    "incident_id": incident_id
                })
            )

        await db.incident_events.insert_one({
            "event_id": str(uuid.uuid4()),
            "incident_id": incident_id,
            "event_type": "manually_resolved",
            "timestamp": now
        })

        return self._serialize(updated)

    async def get_all_history(
        self,
        incident_id=None,
        limit=100,
        skip=0
    ):

        db = get_database()

        filters = {}

        if incident_id:
            filters["incident_id"] = incident_id

        cursor = (
            db.incident_events.find(filters)
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        events = []

        async for event in cursor:
            event["_id"] = str(event["_id"])
            events.append(event)

        total = await db.incident_events.count_documents(filters)

        return {
            "total": total,
            "limit": limit,
            "skip": skip,
            "events": events
        }

    async def get_incident_stats(self):

        db = get_database()

        incidents = db.incidents

        total = await incidents.count_documents({})

        active = await incidents.count_documents({
            "status": "active"
        })

        resolved = await incidents.count_documents({
            "status": "resolved"
        })

        critical = await incidents.count_documents({
            "severity": "critical"
        })

        warning = await incidents.count_documents({
            "severity": "warning"
        })

        pipeline = [
            {
                "$group": {
                    "_id": "$type",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]

        anomaly_types = []

        cursor = await incidents.aggregate(pipeline)

        async for item in cursor:
            anomaly_types.append({
                "type": item["_id"],
                "count": item["count"]
            })

        return {
            "total_incidents": total,
            "active_incidents": active,
            "resolved_incidents": resolved,
            "severity_breakdown": {
                "critical": critical,
                "warning": warning
            },
            "anomaly_types": anomaly_types
        }

incident_service = IncidentService()