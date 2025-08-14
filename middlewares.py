import time
import os
import json
from datetime import datetime
from fastapi import Request

LOG_FILE = "requests_history.log"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        file.write("=== Historique des requêtes ===\n")

async def log_requests(request: Request, call_next):
    start_time = time.time()

    body = await request.body()
    try:
        body = json.loads(body.decode("utf-8")) if body else "Aucun corps"
    except json.JSONDecodeError:
        body = body.decode("utf-8") 

    response = await call_next(request)
    
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    response_body = response_body.decode("utf-8")

    process_time = time.time() - start_time

    log_entry = (
        f"\n[{datetime.utcnow().isoformat()}] {request.method} {request.url}\n"
        f"Corps de la requête: {json.dumps(body, indent=2, ensure_ascii=False)}\n"
        f"Réponse: {response_body}\n"
        f"Status: {response.status_code} | Durée: {process_time:.4f} sec\n"
        f"{'-'*60}\n"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_entry)

    return response
