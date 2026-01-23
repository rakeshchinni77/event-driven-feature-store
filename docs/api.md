# Feature Store API Documentation

This document describes the REST API exposed by the **Event-Driven ML Feature Store**
for serving real-time, precomputed machine-learning features.

The API is designed to be **stateless, read-optimized, and production-ready**,
making it suitable for online inference and real-time ML systems.

---

## Base URL

```
http://localhost:8000

```

---

## GET /features/{entity_id}

Retrieve all stored features for a given entity.

This endpoint is optimized for **low-latency inference** and should be called
by downstream ML models or prediction services.

---

### Request

GET /features/{entity_id}

---


### Path Parameters

| Parameter | Type | Description |
|----------|------|-------------|
| entity_id | string | Unique entity identifier (e.g., user ID) |

---

### Example Request

```bash
curl http://localhost:8000/features/user_123abc

```

---
Successful Response (200 OK)

```

{
  "entity_id": "user_123abc",
  "features": {
    "last_action_click": "1"
  },
  "last_updated": "2026-01-22T10:31:29Z"
}

```
---
### Response Fields

| Field        | Type   | Description                                             |
|--------------|--------|---------------------------------------------------------|
| entity_id    | string | Requested entity identifier                             |
| features     | object | Key-value map of feature names and values               |
| last_updated | string | ISO-8601 timestamp of the most recent feature update    |

---
## Error Responses
### 404 — Entity Not Found

Returned when no features exist for the requested entity.
```
{
  "detail": "No features found for entity"
}
```
### 500 — Internal Server Error

Returned for unexpected system failures such as database connectivity issues.
```
{
  "detail": "Internal server error"
}
```

---

## API Design Principles

Stateless — safe for horizontal scaling

Read-only — no mutation endpoints exposed

Low latency — optimized for online inference

Strong consistency — serves only committed Kafka events

Production safe — suitable for real-world ML systems

