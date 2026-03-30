# Executive Summary:- 
* A scalable URL shortening service can be built with stateless Node.js servers behind a load balancer, a PostgreSQL database for persistence, and Redis for high-speed caching. Clients send long URLs via a POST /urls API, which generates a unique short code (e.g. using Base62 encoding of an ID or a random UUID), stores it in Postgres, and returns the short link. Redirect requests (GET /{code}) use Redis (cache-aside) for ultra-fast lookups, falling back to Postgres on cache miss
. We enforce a UNIQUE index on the short_code in Postgres to guarantee no collisions
. Expiry of links is handled via an expires_at column and a cleanup job. Rate limiting (e.g. per-IP on the POST endpoint) and analytics/event logging (e.g. write append-only clicks to a table or log) are added for robustness. Dockerfiles and a docker-compose.yml define services for Node, Postgres, and Redis (with environment variables via .env). A comprehensive test suite (unit, integration, end-to-end) ensures correctness. Key considerations (caching strategy, consistency trade-offs, security, performance targets) are addressed below, with actionable implementation steps and code samples.

<img width="1324" height="499" alt="image" src="https://github.com/user-attachments/assets/6592570c-33c0-455a-bf5c-3a44766d9b20" />

## REST API Design:-
* POST /urls – Create a short URL. Request JSON: { "original_url": "...", "custom_alias": "...", "expires_in": 3600 }. The server:

* Validates input (URL format, length).
Generates or accepts a unique short code. If a custom_alias is provided and taken, returns 409 Conflict
.
* Inserts a new record in Postgres and (optionally) caches it.
Returns 201 Created with JSON { "short_url": "https://short.ly/abc123", "short_code": "abc123", "expires_at": "2026-04-30T12:34:56Z" }
.
* GET /{short_code} – Redirect to original URL. The server:

Looks up the code in Redis; if found, returns a 302 Found redirect immediately.
If not in cache, queries Postgres. If not found or expired, returns 404 Not Found.
Otherwise, caches the result (cache-aside) and issues 302 Found with Location: {original_url} (not 301, to capture every click for analytics
).
Other endpoints (optional): GET /stats/{short_code} (return click analytics), DELETE /{short_code} (revoke a link), or health checks (e.g. GET /health). Each endpoint should set appropriate HTTP status codes (400 for bad input, 500 on server error). Authentication (API keys) can be layered on POST if needed, but is not required per specs.

## Short Code Generation Strategy:-
Key choices are:

Auto-increment ID + Base62 encoding: Easy and collision-free. A sequential ID from Postgres is encoded to a short string using [0-9A-Za-z] characters. For example, 6-character Base62 covers ~56.8 billion combos
; 7 characters covers 62^7 ≈ 3.5 trillion
. This easily scales for billions of URLs, with trivial code and no collisions. Trade-off: It's predictable (every new URL increments by 1). We can mitigate predictability (if needed) by shuffling or prefixing.

Random or UUID: Use a cryptographically strong random generator (crypto.randomUUID() in Node.js
 or nanoid). This yields unpredictable codes without a single DB counter. Trade-off: There is a tiny collision probability, so we must check the database and retry on conflict. Also, random strings can be longer (or fixed length, but ensure enough entropy).

Hash of URL: Hash the original URL (e.g. MD5 or SHA256) and take the first N Base62 chars. This can create a deterministic mapping, but collisions are possible
. One must either increase the hash length or check for duplicates and handle collisions (e.g. by appending or re-hashing). Collisions can be problematic in high-scale settings.

## Redis Caching Strategy:-
We use Redis as an in-memory cache for the short-code lookup, dramatically reducing database load and latency. Use the cache-aside (lazy-loading) pattern
: On a redirect request, the app first queries Redis; if the code is found (cache hit), return the URL immediately. If the code is missing (cache miss), fetch from Postgres and then store it in Redis for future requests
. Example workflow:

* GET /abc123 received by Node.
redis.get("abc123") returns null (miss).
* Query Postgres: SELECT original_url FROM url_mappings WHERE short_code='abc123'.
If found, redis.set("abc123", original_url, 'EX', ttl), then res.redirect(302, original_url).
We also do write-through caching on link creation: after inserting into Postgres, we immediately redis.set(code, original_url) so the first redirect won’t be a miss.

What to cache: Only the essential mapping short_code → original_url. Optionally, store derived analytics counters or user metadata, but keep it simple.

* Cache TTL: Set an appropriate Time-To-Live to expire entries and free memory. This could match the link’s expiration (expires_at). For example, if expires_at is 24 hours ahead, set Redis TTL to 86400 seconds. For non-expiring links, a long TTL (e.g. one day or one week) can ensure eventual eviction while still benefiting from caching. Redis eviction policy (e.g. LRU) can also be configured.

* Invalidation: If a short link is deleted or its target changed (rare), delete the Redis key. Otherwise, we rely on TTL or eviction. Because writes (link creations) go through the application, the app can always update or delete the cache key when updating the database.

* Why cache-aside? This pattern gives full control to the application
. It is ideal for read-heavy workloads like redirects. By contrast, write-through (writing to cache & DB simultaneously) is simpler for writes but unnecessary here since reads dominate.
