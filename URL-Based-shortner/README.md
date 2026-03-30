## Executive Summary:- 
* A scalable URL shortening service can be built with stateless Node.js servers behind a load balancer, a PostgreSQL database for persistence, and Redis for high-speed caching. Clients send long URLs via a POST /urls API, which generates a unique short code (e.g. using Base62 encoding of an ID or a random UUID), stores it in Postgres, and returns the short link. Redirect requests (GET /{code}) use Redis (cache-aside) for ultra-fast lookups, falling back to Postgres on cache miss
. We enforce a UNIQUE index on the short_code in Postgres to guarantee no collisions
. Expiry of links is handled via an expires_at column and a cleanup job. Rate limiting (e.g. per-IP on the POST endpoint) and analytics/event logging (e.g. write append-only clicks to a table or log) are added for robustness. Dockerfiles and a docker-compose.yml define services for Node, Postgres, and Redis (with environment variables via .env). A comprehensive test suite (unit, integration, end-to-end) ensures correctness. Key considerations (caching strategy, consistency trade-offs, security, performance targets) are addressed below, with actionable implementation steps and code samples.

<img width="1324" height="499" alt="image" src="https://github.com/user-attachments/assets/6592570c-33c0-455a-bf5c-3a44766d9b20" />

REST API Design
POST /urls – Create a short URL. Request JSON: { "original_url": "...", "custom_alias": "...", "expires_in": 3600 }. The server:

Validates input (URL format, length).
Generates or accepts a unique short code. If a custom_alias is provided and taken, returns 409 Conflict
.
Inserts a new record in Postgres and (optionally) caches it.
Returns 201 Created with JSON { "short_url": "https://short.ly/abc123", "short_code": "abc123", "expires_at": "2026-04-30T12:34:56Z" }
.
GET /{short_code} – Redirect to original URL. The server:

Looks up the code in Redis; if found, returns a 302 Found redirect immediately.
If not in cache, queries Postgres. If not found or expired, returns 404 Not Found.
Otherwise, caches the result (cache-aside) and issues 302 Found with Location: {original_url} (not 301, to capture every click for analytics
).
Other endpoints (optional): GET /stats/{short_code} (return click analytics), DELETE /{short_code} (revoke a link), or health checks (e.g. GET /health). Each endpoint should set appropriate HTTP status codes (400 for bad input, 500 on server error). Authentication (API keys) can be layered on POST if needed, but is not required per specs.
