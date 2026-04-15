from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
from fastmcp import FastMCP
import httpx
import os
import json
from typing import Optional

mcp = FastMCP("wger-workout-manager")


def build_headers(auth_token: Optional[str] = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


@mcp.tool()
async def get_api_overview(base_url: str) -> dict:
    """Retrieve the full list of available API endpoints and their URLs from the wger REST API.
    Use this as a starting point to discover what resources are available before making specific requests."""
    base = normalize_base_url(base_url)
    url = f"{base}/api/v2/"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers={"Accept": "application/json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_resource_list(
    base_url: str,
    resource: str,
    auth_token: Optional[str] = None,
    filters: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Fetch a paginated list of records for any wger API resource (e.g. workout, exercise,
    nutritiondiary, weightentry, measurement, routine). Supports filtering, ordering, and pagination."""
    base = normalize_base_url(base_url)
    url = f"{base}/api/v2/{resource}/"

    params = {"format": "json", "limit": limit, "offset": (page - 1) * limit}
    if filters:
        for part in filters.split("&"):
            if "=" in part:
                key, value = part.split("=", 1)
                params[key.strip()] = value.strip()

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=build_headers(auth_token), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_resource_detail(
    base_url: str,
    resource: str,
    id: int,
    auth_token: Optional[str] = None,
) -> dict:
    """Retrieve a single record by ID for any wger API resource. Use this when you know the
    specific ID of a workout, exercise, nutrition plan, body weight entry, measurement, or other resource."""
    base = normalize_base_url(base_url)
    url = f"{base}/api/v2/{resource}/{id}/"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            url, headers=build_headers(auth_token), params={"format": "json"}
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_resource(
    base_url: str,
    resource: str,
    data: str,
    auth_token: str,
) -> dict:
    """Create a new record for any wger API resource such as a workout session, weight entry,
    nutrition diary log, measurement, or routine."""
    base = normalize_base_url(base_url)
    url = f"{base}/api/v2/{resource}/"

    try:
        payload = json.loads(data)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in data parameter: {str(e)}"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=build_headers(auth_token), json=payload)
        response.raise_for_status()
        if response.status_code == 204:
            return {"success": True, "message": "Resource created successfully"}
        return response.json()


@mcp.tool()
async def update_resource(
    base_url: str,
    resource: str,
    id: int,
    data: str,
    auth_token: str,
    full_update: bool = False,
) -> dict:
    """Update an existing record by ID for any wger API resource. Use full_update=False for
    partial PATCH updates (only specified fields) or full_update=True for full PUT replacement."""
    base = normalize_base_url(base_url)
    url = f"{base}/api/v2/{resource}/{id}/"

    try:
        payload = json.loads(data)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON in data parameter: {str(e)}"}

    async with httpx.AsyncClient(timeout=30) as client:
        if full_update:
            response = await client.put(url, headers=build_headers(auth_token), json=payload)
        else:
            response = await client.patch(url, headers=build_headers(auth_token), json=payload)
        response.raise_for_status()
        if response.status_code == 204:
            return {"success": True, "message": "Resource updated successfully"}
        return response.json()


@mcp.tool()
async def delete_resource(
    base_url: str,
    resource: str,
    id: int,
    auth_token: str,
) -> dict:
    """Delete a specific record by ID from any wger API resource. This action is irreversible."""
    base = normalize_base_url(base_url)
    url = f"{base}/api/v2/{resource}/{id}/"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.delete(url, headers=build_headers(auth_token))
        response.raise_for_status()
        return {"success": True, "message": f"{resource} with ID {id} deleted successfully"}


@mcp.tool()
async def authenticate(
    base_url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> dict:
    """Obtain a JWT access and refresh token pair by providing username and password credentials
    for a wger instance. Also supports refreshing an expired access token using a refresh token."""
    base = normalize_base_url(base_url)

    async with httpx.AsyncClient(timeout=30) as client:
        if refresh_token:
            url = f"{base}/api/v2/auth/token/refresh/"
            payload = {"refresh": refresh_token}
            response = await client.post(
                url,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        elif username and password:
            url = f"{base}/api/v2/auth/token/"
            payload = {"username": username, "password": password}
            response = await client.post(
                url,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        else:
            return {
                "error": "Either provide username and password, or a refresh_token to obtain a new access token."
            }


@mcp.tool()
async def get_nutrition_values(
    base_url: str,
    plan_id: int,
    auth_token: str,
    date: Optional[str] = None,
) -> dict:
    """Retrieve computed nutritional values (calories, protein, carbs, fat, etc.) for a nutrition
    plan or a specific log entry. Useful for reporting on daily or weekly nutrition goals."""
    base = normalize_base_url(base_url)

    async with httpx.AsyncClient(timeout=30) as client:
        if date:
            url = f"{base}/api/v2/nutritiondiary/"
            params = {"format": "json", "plan": plan_id}
            response = await client.get(
                url, headers=build_headers(auth_token), params=params
            )
            response.raise_for_status()
            diary_data = response.json()

            log_url = f"{base}/api/v2/nutritionplan/{plan_id}/nutritional_values/"
            log_params = {"format": "json"}
            log_response = await client.get(
                log_url, headers=build_headers(auth_token), params=log_params
            )
            log_response.raise_for_status()
            plan_values = log_response.json()

            return {
                "plan_id": plan_id,
                "date": date,
                "plan_nutritional_values": plan_values,
                "diary_entries": diary_data,
            }
        else:
            url = f"{base}/api/v2/nutritionplan/{plan_id}/nutritional_values/"
            params = {"format": "json"}
            response = await client.get(
                url, headers=build_headers(auth_token), params=params
            )
            response.raise_for_status()
            return {"plan_id": plan_id, "nutritional_values": response.json()}




async def health(request):
    return JSONResponse({"status": "ok", "server": mcp.name})

async def tools(request):
    registered = await mcp.list_tools()
    tool_list = [{"name": t.name, "description": t.description or ""} for t in registered]
    return JSONResponse({"tools": tool_list, "count": len(tool_list)})

mcp_app = mcp.http_app(transport="streamable-http")

class _FixAcceptHeader:
    """Ensure Accept header includes both types FastMCP requires."""
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            accept = headers.get(b"accept", b"").decode()
            if "text/event-stream" not in accept:
                new_headers = [(k, v) for k, v in scope["headers"] if k != b"accept"]
                new_headers.append((b"accept", b"application/json, text/event-stream"))
                scope = dict(scope, headers=new_headers)
        await self.app(scope, receive, send)

app = _FixAcceptHeader(Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", mcp_app),
    ],
    lifespan=mcp_app.lifespan,
))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
