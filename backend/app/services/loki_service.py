import os
import time
import httpx

from fastapi import HTTPException


LOKI_URL = os.getenv("LOKI_URL", "http://localhost:3100")


class LokiService:

    def __init__(self):
        self.base_url = LOKI_URL.rstrip("/")

    async def health(self):
        """Check whether Loki is ready."""

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/ready"
                )

                response.raise_for_status()

                return {
                    "status": "connected",
                    "service": "loki",
                    "message": "Loki is healthy."
                }

        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Loki connection failed: {str(exc)}"
            )

    async def get_labels(self):
        """Retrieve all available Loki stream labels."""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/loki/api/v1/labels"
                )

                response.raise_for_status()

                return response.json()

        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Unable to retrieve Loki labels: {str(exc)}"
            )

    async def query_range(
        self,
        query: str,
        limit: int = 100,
        start: int = None,
        end: int = None,
        direction: str = "backward"
    ):
        """Execute a LogQL range query."""

        end = end or time.time_ns()
        start = start or (end - 15 * 60 * 1_000_000_000)

        if start >= end:
            raise HTTPException(
                status_code=400,
                detail="Start time must be earlier than end time."
            )

        if not 1 <= limit <= 1000:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 1000."
            )

        if direction not in ("forward", "backward"):
            raise HTTPException(
                status_code=400,
                detail="Direction must be forward or backward."
            )

        params = {
            "query": query,
            "start": str(start),
            "end": str(end),
            "limit": limit,
            "direction": direction
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"{self.base_url}/loki/api/v1/query_range",
                    params=params
                )

                response.raise_for_status()

                return response.json()

        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Loki query failed: {exc.response.text}"
            )

        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Unable to query Loki: {str(exc)}"
            )

    async def search_logs(
        self,
        namespace: str = None,
        pod: str = None,
        search: str = None,
        limit: int = 100
    ):
        """Search logs with optional Kubernetes filters."""

        selector = []

        if namespace:
            selector.append(f'namespace="{namespace}"')

        if pod:
            selector.append(f'pod="{pod}"')

        if not selector:
            raise HTTPException(
                status_code=400,
                detail="Provide at least a namespace or pod filter."
            )

        query = "{" + ", ".join(selector) + "}"

        if search:
            # Escape double quotes and backslashes in the literal.
            escaped_search = search.replace("\\", "\\\\").replace('"', '\\"')
            query += f' |= "{escaped_search}"'

        return await self.query_range(
            query=query,
            limit=limit
        )

    async def get_error_logs(
        self,
        namespace: str = None,
        limit: int = 100
    ):
        """Search for error-related log messages."""

        selector = []

        if namespace:
            selector.append(f'namespace="{namespace}"')

        query = "{" + ", ".join(selector) + "}"

        if not selector:
            query = '{namespace=~".+"}'

        query += ' |~ "(?i)(error|exception|fatal)"'

        return await self.query_range(
            query=query,
            limit=limit
        )


loki_service = LokiService()