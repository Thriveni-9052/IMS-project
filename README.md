# Incident Management System (IMS)

## Overview

The Incident Management System (IMS) is a resilient, async, event-driven platform designed to monitor distributed infrastructure systems such as:

* APIs
* MCP Hosts
* Distributed Caches
* Async Queues
* RDBMS
* NoSQL Stores

The platform ingests high-volume failure signals, intelligently debounces duplicate alerts, creates incidents, manages lifecycle workflows, validates RCA submissions, and calculates MTTR metrics.

---

# Architecture Diagram

```text
                +------------------+
                |  Signal Sources  |
                |------------------|
                | APIs             |
                | Databases        |
                | Cache Clusters   |
                | Queues           |
                +--------+---------+
                         |
                         v
                +------------------+
                |  FastAPI Ingest  |
                |------------------|
                | /signals API     |
                | Rate Limiting    |
                +--------+---------+
                         |
                         v
                +------------------+
                | Async Queue      |
                | asyncio.Queue()  |
                +--------+---------+
                         |
                         v
                +------------------+
                | Worker Engine    |
                |------------------|
                | Debouncing       |
                | Incident Logic   |
                | Retry Handling   |
                +--------+---------+
                         |
        +----------------+----------------+
        |                                 |
        v                                 v
+------------------+          +------------------+
| Incident Store   |          | Raw Signal Store |
| Source of Truth  |          | Audit Log        |
+------------------+          +------------------+
        |
        v
+------------------+
| HTMX Dashboard   |
|------------------|
| Live Incidents   |
| RCA Form         |
| Incident Detail  |
+------------------+
```

---

# Features

## Async Signal Processing

* Uses FastAPI + asyncio
* Queue-based ingestion pipeline
* Non-blocking worker architecture

---

## Debouncing Logic

If multiple signals arrive for the same component within 10 seconds:

* Only one incident is created
* All signals are linked to the same incident

Example:

```text
100 CACHE_CLUSTER_01 failures
within 10 sec
→ 1 Incident
```

---

## Incident Lifecycle

Supported states:

```text
OPEN
→ INVESTIGATING
→ RESOLVED
→ CLOSED
```

---

## Mandatory RCA Validation

Incidents cannot be closed without:

* Root Cause
* Fix Applied
* Prevention Steps

---

## MTTR Calculation

MTTR is automatically calculated using:

```text
MTTR = end_time - start_time
```

---

## Rate Limiting

Basic rate limiting is implemented on the ingestion API to prevent overload and cascading failures.

---

## Retry Logic

Worker retries failed persistence operations:

```text
3 retries
2 second delay
```

---

# Tech Stack

| Layer       | Technology         |
| ----------- | ------------------ |
| Backend     | FastAPI            |
| Frontend    | HTMX + TailwindCSS |
| Concurrency | asyncio            |
| Queue       | asyncio.Queue      |
| Templates   | Jinja2             |
| Runtime     | Uvicorn            |

---

# Project Structure

```text
ims-project/
│
├── backend/
│   ├── main.py
│   ├── services/
│   │   ├── incident_engine.py
│   │   └── worker.py
│
├── frontend/
│   ├── templates/
│   │   ├── dashboard.html
│   │   └── partials/
│   │       └── incident_table.html
│
└── README.md
```

---

# API Endpoints

## Signal Ingestion

```http
POST /signals
```

Example:

```json
{
  "component_id": "CACHE_CLUSTER_01",
  "severity": "P2"
}
```

---

## Dashboard

```http
GET /
```

---

## Incident Table

```http
GET /incidents/table
```

---

## Incident Detail

```http
GET /incidents/{incident_id}
```

---

## Close Incident

```http
POST /close/{incident_id}
```

Example RCA:

```json
{
  "root_cause": "Database failure",
  "fix": "Restarted DB cluster",
  "prevention": "Added monitoring alerts"
}
```

---

## Health Check

```http
GET /health
```

---

# Setup Instructions

## Clone Repository

```bash
git clone <repo-url>
cd ims-project
```

---

## Install Dependencies

```bash
pip install fastapi uvicorn jinja2
```

---

## Start Server

```bash
cd backend

uvicorn main:app --reload
```

---

# Open Dashboard

```text
http://127.0.0.1:8000
```

---

# Backpressure Handling

The system uses:

* `asyncio.Queue`
* Async workers
* Non-blocking ingestion

This prevents crashes when persistence becomes slow.

Signals are buffered in-memory and processed asynchronously.

---

# Resilience Features

* Async queue workers
* Retry logic
* Rate limiting
* RCA validation
* Debouncing
* Health monitoring

---

# Future Improvements

* PostgreSQL integration
* MongoDB raw signal store
* Redis caching
* Kafka/RabbitMQ ingestion
* Prometheus metrics
* Docker Compose
* Kubernetes deployment

---

# Sample Failure Scenario

Example outage flow:

```text
1. CACHE_CLUSTER_01 latency spike
2. RDBMS_PRIMARY failure
3. Queue congestion
4. Incident creation
5. RCA submission
6. MTTR calculation
```

---

# Author
Madhav
