from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
from fastmcp import FastMCP
import httpx
import os
from typing import Optional

mcp = FastMCP("wger Workout Manager")

BASE_URL = "https://wger.de/api/v2"


def get_headers(api_key: Optional[str] = None) -> dict:
    token = api_key or os.environ.get("WGER_API_KEY", "")
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@mcp.tool()
async def list_exercises(
    language: Optional[str] = None,
    category: Optional[int] = None,
    muscles: Optional[int] = None,
    equipment: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List exercises from the wger exercise wiki. Filter by language, category, muscles, or equipment."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    if language:
        params["language"] = language
    if category is not None:
        params["category"] = category
    if muscles is not None:
        params["muscles"] = muscles
    if equipment is not None:
        params["equipment"] = equipment
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exercise/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_exercise(
    exercise_id: int,
    api_key: Optional[str] = None,
) -> dict:
    """Get details of a specific exercise by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exercise/{exercise_id}/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_exercise_categories(api_key: Optional[str] = None) -> dict:
    """List all exercise categories (e.g., Chest, Back, Legs)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exercisecategory/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_muscles(api_key: Optional[str] = None) -> dict:
    """List all muscles available in the exercise wiki."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/muscle/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_equipment(api_key: Optional[str] = None) -> dict:
    """List all equipment types used in exercises."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/equipment/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_workouts(
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List all workouts for the authenticated user."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/workout/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_workout(
    workout_id: int,
    api_key: Optional[str] = None,
) -> dict:
    """Get details of a specific workout by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/workout/{workout_id}/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_workout(
    description: str = "",
    api_key: Optional[str] = None,
) -> dict:
    """Create a new workout for the authenticated user."""
    payload = {"description": description}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/workout/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def delete_workout(
    workout_id: int,
    api_key: Optional[str] = None,
) -> dict:
    """Delete a specific workout by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/workout/{workout_id}/", headers=get_headers(api_key))
        response.raise_for_status()
        return {"success": True, "workout_id": workout_id}


@mcp.tool()
async def list_training_logs(
    workout: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List workout training logs for the authenticated user. Optionally filter by workout ID."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    if workout is not None:
        params["workout"] = workout
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/workoutsession/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_training_log(
    session_id: int,
    api_key: Optional[str] = None,
) -> dict:
    """Get a specific workout session/training log by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/workoutsession/{session_id}/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_training_log(
    workout: int,
    date: str,
    notes: Optional[str] = None,
    impression: Optional[str] = None,
    time_start: Optional[str] = None,
    time_end: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Create a new workout session/training log. Date format: YYYY-MM-DD. Impression: '1' (General), '2' (Burned out), '3' (Good), '4' (Excellent)."""
    payload: dict = {"workout": workout, "date": date}
    if notes:
        payload["notes"] = notes
    if impression:
        payload["impression"] = impression
    if time_start:
        payload["time_start"] = time_start
    if time_end:
        payload["time_end"] = time_end
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/workoutsession/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_log_entries(
    exercise: Optional[int] = None,
    workout: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List individual exercise log entries (sets, reps, weight). Filter by exercise or workout."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    if exercise is not None:
        params["exercise"] = exercise
    if workout is not None:
        params["workout"] = workout
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/workoutlog/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_log_entry(
    exercise: int,
    workout: int,
    reps: int,
    weight: float,
    date: str,
    rir: Optional[int] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Log a set for an exercise in a workout. Date format: YYYY-MM-DD. Weight in kg. RIR = Reps In Reserve."""
    payload: dict = {
        "exercise": exercise,
        "workout": workout,
        "reps": reps,
        "weight": str(weight),
        "date": date,
    }
    if rir is not None:
        payload["rir"] = str(rir)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/workoutlog/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_nutrition_plans(
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List all nutrition plans for the authenticated user."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nutritionplan/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_nutrition_plan(
    plan_id: int,
    api_key: Optional[str] = None,
) -> dict:
    """Get details of a specific nutrition plan by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nutritionplan/{plan_id}/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_nutrition_plan_info(
    plan_id: int,
    api_key: Optional[str] = None,
) -> dict:
    """Get full nutritional info (planned calories, macros) for a nutrition plan."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nutritionplan/{plan_id}/nutritional_values/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_nutrition_plan(
    description: Optional[str] = None,
    goal_energy: Optional[float] = None,
    goal_protein: Optional[float] = None,
    goal_carbohydrates: Optional[float] = None,
    goal_fat: Optional[float] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Create a new nutrition plan for the authenticated user."""
    payload: dict = {}
    if description:
        payload["description"] = description
    if goal_energy is not None:
        payload["goal_energy"] = goal_energy
    if goal_protein is not None:
        payload["goal_protein"] = goal_protein
    if goal_carbohydrates is not None:
        payload["goal_carbohydrates"] = goal_carbohydrates
    if goal_fat is not None:
        payload["goal_fat"] = goal_fat
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/nutritionplan/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_meals(
    plan: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List meals in nutrition plans. Optionally filter by plan ID."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    if plan is not None:
        params["plan"] = plan
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/meal/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_meal(
    plan: int,
    name: Optional[str] = None,
    time: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Create a new meal in a nutrition plan. Time format: HH:MM:SS."""
    payload: dict = {"plan": plan}
    if name:
        payload["name"] = name
    if time:
        payload["time"] = time
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/meal/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_meal_items(
    meal: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List food items in meals. Optionally filter by meal ID."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    if meal is not None:
        params["meal"] = meal
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/mealitem/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_meal_item(
    meal: int,
    ingredient: int,
    amount: float,
    weight_unit: Optional[int] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Add a food item (ingredient) to a meal with a specified amount in grams (or custom weight unit)."""
    payload: dict = {"meal": meal, "ingredient": ingredient, "amount": str(amount)}
    if weight_unit is not None:
        payload["weight_unit"] = weight_unit
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/mealitem/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def search_ingredients(
    name: str,
    language: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """Search for food ingredients/products in the wger food database."""
    params = {"format": "json", "name": name, "limit": limit, "offset": offset}
    if language:
        params["language"] = language
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/ingredient/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_ingredient(
    ingredient_id: int,
    api_key: Optional[str] = None,
) -> dict:
    """Get details of a specific food ingredient by ID, including nutritional values."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/ingredient/{ingredient_id}/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_body_weight(
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List body weight entries for the authenticated user."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/weightentry/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_body_weight_entry(
    date: str,
    weight: float,
    api_key: Optional[str] = None,
) -> dict:
    """Log a body weight entry. Date format: YYYY-MM-DD. Weight in kg."""
    payload = {"date": date, "weight": str(weight)}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/weightentry/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def delete_body_weight_entry(
    entry_id: int,
    api_key: Optional[str] = None,
) -> dict:
    """Delete a body weight entry by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/weightentry/{entry_id}/", headers=get_headers(api_key))
        response.raise_for_status()
        return {"success": True, "entry_id": entry_id}


@mcp.tool()
async def list_measurements(
    category: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List body measurement entries. Optionally filter by category ID."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    if category is not None:
        params["category"] = category
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/measurement/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_measurement_categories(api_key: Optional[str] = None) -> dict:
    """List all measurement categories (e.g., Waist, Arms, Chest)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/measurement-category/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_measurement_entry(
    category: int,
    date: str,
    value: float,
    notes: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Log a body measurement entry. Date format: YYYY-MM-DD. Value in cm or other unit depending on category."""
    payload: dict = {"category": category, "date": date, "value": str(value)}
    if notes:
        payload["notes"] = notes
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/measurement/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_nutrition_logs(
    plan: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List nutrition diary/log entries for the authenticated user."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    if plan is not None:
        params["plan"] = plan
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nutritiondiary/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_nutrition_log(
    plan: int,
    ingredient: int,
    amount: float,
    datetime_logged: Optional[str] = None,
    weight_unit: Optional[int] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Log a food consumption entry in the nutrition diary. Datetime format: YYYY-MM-DDTHH:MM:SS."""
    payload: dict = {"plan": plan, "ingredient": ingredient, "amount": str(amount)}
    if datetime_logged:
        payload["datetime"] = datetime_logged
    if weight_unit is not None:
        payload["weight_unit"] = weight_unit
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/nutritiondiary/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_user_profile(api_key: Optional[str] = None) -> dict:
    """Get the profile information for the authenticated user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/userprofile/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def list_routines(
    limit: int = 20,
    offset: int = 0,
    api_key: Optional[str] = None,
) -> dict:
    """List workout routines for the authenticated user."""
    params = {"limit": limit, "offset": offset, "format": "json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/routine/", headers=get_headers(api_key), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_routine(
    routine_id: int,
    api_key: Optional[str] = None,
) -> dict:
    """Get details of a specific workout routine by ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/routine/{routine_id}/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_routine(
    name: str,
    description: Optional[str] = None,
    training_days_per_week: Optional[int] = None,
    api_key: Optional[str] = None,
) -> dict:
    """Create a new workout routine."""
    payload: dict = {"name": name}
    if description:
        payload["description"] = description
    if training_days_per_week is not None:
        payload["training_days_per_week"] = training_days_per_week
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/routine/", headers=get_headers(api_key), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_api_info(api_key: Optional[str] = None) -> dict:
    """Get API server information and available endpoints."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/", headers=get_headers(api_key), params={"format": "json"})
        response.raise_for_status()
        return response.json()




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
