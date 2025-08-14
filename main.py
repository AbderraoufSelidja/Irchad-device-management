from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from api import devices
import time
import os
import json
from datetime import datetime
from api import maintainers
app = FastAPI()

#  Add CORS Middleware to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(devices.router)
app.include_router(maintainers.routes.router, tags=["maintainer"])
# app.include_router(maintainers.router)  # You can uncomment this if needed

LOG_FILE = "requests_history.log"

#  Create the log file if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        file.write("=== Historique des requêtes ===\n")

#  Logging middleware
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Skip Swagger and OpenAPI UI
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    # Read request body
    body = await request.body()
    try:
        body = json.loads(body.decode("utf-8")) if body else "Aucun corps"
    except json.JSONDecodeError:
        body = body.decode("utf-8") if body else "Aucun corps"

    # Get response
    response = await call_next(request)

    # Capture response body
    response_body = b"".join([chunk async for chunk in response.body_iterator])
    response = Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )

    process_time = time.time() - start_time

    # Log entry format
    log_entry = f"\n[{datetime.utcnow().isoformat()}] {request.method} {request.url}\n"

    if body and body != "Aucun corps":
        log_entry += f"Corps de la requête:\n{json.dumps(body, indent=2, ensure_ascii=False)}\n"

    try:
        response_content = json.loads(response_body)
        log_entry += (
            f"Réponse:\n{json.dumps(response_content, indent=4, ensure_ascii=False)}\n"
        )
    except json.JSONDecodeError:
        log_entry += f"Réponse (non JSON):\n{response_body.decode('utf-8')}\n"

    log_entry += (
        f"Status: {response.status_code} | Durée: {process_time:.4f} sec\n"
        f"{'-'*60}\n"
    )

    # Write to log file
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_entry)

    return response

#  Add the custom logging middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)
