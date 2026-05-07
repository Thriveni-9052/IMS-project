from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import asyncio
import time
import os
from collections import defaultdict, deque
from services.worker import worker
from services.incident_engine import (
    process_signal,
    get_open_incident,
    create_incident,
    incidents
)
stores = {    
"incident_store": [],
    "raw_store": []
}
# -------------------
# APP LIFESPAN
# -------------------
signal_queue = asyncio.Queue()

async def signal_worker():
    while True:
        signal = await signal_queue.get()

        incident_id = process_signal(signal)
        print("Processed Incident:", incident_id)

        signal_queue.task_done()

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(signal_worker())
    yield
app = FastAPI(lifespan=lifespan)

# -------------------
# TEMPLATE FIX (IMPORTANT)
# -------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(
    directory=os.path.abspath(
        os.path.join(BASE_DIR, "..", "frontend", "templates")
    )
)

# -------------------
# STORAGE
# -------------------
signals = []
incidents = []
start_time = time.time()
# UI ROUTES
# -------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


@app.get("/incidents/table", response_class=HTMLResponse)
async def incidents_table(request: Request):
    return templates.TemplateResponse(
        "partials/incident_table.html",
        {"request": request, "incidents": incidents}
    )

# -------------------
# RATE LIMIT
# -------------------
rate_limit = defaultdict(lambda: deque(maxlen=10))
RATE_LIMIT_WINDOW = 1
MAX_REQUESTS = 5

# -------------------
# DEBOUNCE
# -------------------
debounce = defaultdict(lambda: {
    "count": 0,
    "first_seen": None
})

THRESHOLD = 3


# -------------------
# RATE LIMIT CHECK
# -------------------
def check_rate_limit(ip: str):
    now = time.time()
    q = rate_limit[ip]

    while q and now - q[0] > RATE_LIMIT_WINDOW:
        q.popleft()

    if len(q) >= MAX_REQUESTS:
        return False

    q.append(now)
    return True


# -------------------
# SEVERITY ENGINE
# -------------------
def get_severity(component: str):
    if "RDBMS" in component:
        return "P0"
    elif "CACHE" in component:
        return "P2"
    elif "QUEUE" in component:
        return "P1"
    return "P3"


# -------------------
# SIGNAL PROCESSOR
# -------------------
def process_signal(signal):
    comp = signal["component_id"]
    now = time.time()

    d = debounce[comp]

    if d["first_seen"] is None:
        d["first_seen"] = now

    if now - d["first_seen"] > 10:
        d["count"] = 0
        d["first_seen"] = now

    d["count"] += 1

    signals.append({
        "component_id": comp,
        "severity": signal.get("severity", "P3"),
        "timestamp": now
    })

# -------------------
# WORKER
# -------------------

# ------------------
incidents = [
    {
        "id":"INC001",
        "component": "CACHE_CLUSTER_01",
        "severity": "P2",
        "status": "OPEN",
        "signals": ["timeout error", "latency spike"]
    },
    {
        "id":"INC002",
        "component": "RDBMS_PRIMARY",
        "severity": "P0",
        "status": "INVESTIGATING",
        "signals": ["db down", "connection failure"]
    }
]

# -------------------
# API: SIGNALS
# -----------------
@app.post("/signals")
async def add_signal(signal: dict):
    await signal_queue.put(signal)
    return {"message": "queued"}

# -------------------
# CLOSE INCIDENT
# -------------------
@app.post("/close/{incident_id}")
async def close_incident(incident_id: str, rca: dict):

    for inc in incidents:
        if inc["id"] == incident_id:

            # check RCA
            if not rca.get("root_cause") or not rca.get("fix") or not rca.get("prevention"):
                return {"error": "RCA incomplete"}

            # START TIME already stored when incident created
            start = inc["start_time"]

            # END TIME now
            end = time.time()

            # MTTR calculation
            mttr = end - start

            inc["status"] = "CLOSED"
            inc["end_time"] = end
            inc["mttr"] = mttr
            inc["rca"] = rca

            return {
                "message": "Incident closed",
                "mttr_seconds": mttr
            }

    return {"error": "Incident not found"}


# -------------------
# INCIDENT LIST
# -------------------
@app.get("/incidents/{incident_id}")
async def incident_detail(incident_id: str):
    for inc in incidents:
        if inc["id"] == incident_id:
            return inc

    return {
        "incident_id": incident_id,
        "message": "Not found"
 }

@app.get("/debug/incidents")
def debug():
    return incidents
# -------------------
# HEALTH
# -------------------
@app.get("/health")
def health():
    uptime = time.time() - start_time

    return {
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "signals": len(signals),
        "incidents": len(incidents),
        "queue_size": signal_queue.qsize()
    }
