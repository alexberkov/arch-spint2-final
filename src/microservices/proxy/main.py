import os
import random

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

load_dotenv()

MONOLITH_URL = os.getenv("MONOLITH_URL", "http://monolith:8080")
MOVIES_SERVICE_URL = os.getenv("MOVIES_SERVICE_URL", "http://movies-service:8081")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://events-service:8082")

PROXY_HOST = os.getenv("PROXY_HOST", "http://127.0.0.1")
PROXY_PORT = os.getenv("PROXY_PORT", "8000")

MOVIES_MIGRATION_PERCENT = int(os.getenv("MOVIES_MIGRATION_PERCENT", 50))


def get_forward_url(path: str) -> str:
    if path.startswith("/api/events"):
        return EVENT_SERVICE_URL

    if path.startswith("/api/movies"):
        return (MOVIES_SERVICE_URL
                if random.randint(0, 100) < MOVIES_MIGRATION_PERCENT
                else MONOLITH_URL)

    return MONOLITH_URL


app = FastAPI(
    title='Proxy Service',
    description='Forward requests to monolith/movies_service/events_service',
    servers=[
        {"url": f"{PROXY_HOST}:{PROXY_PORT}"}
    ],
)

client = httpx.AsyncClient()


@app.on_event("shutdown")
async def shutdown_event():
    await client.close()


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def dynamic_proxy(request: Request, path: str):
    url = get_forward_url(path)
    url = f"{url}/{path}"

    if request.url.query:
        url += f"?{request.url.query}"

    body = await request.body()

    headers = dict(request.headers)
    headers.pop("host", None)

    req = client.build_request(
        method=request.method, url=url, headers=headers, content=body
    )

    response = await client.send(req, stream=True)

    return StreamingResponse(
        response.aiter_raw(), status_code=response.status_code, headers=dict(response.headers)
    )
