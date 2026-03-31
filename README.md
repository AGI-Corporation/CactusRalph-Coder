# CactusRalph-Coder

REST API service that connects **Dolittle Rosetta** to a Neo4j graph layer,
exposing code-intelligence graphs (repositories, files, concepts) for use by
front-end graph-visualisation libraries.

---

## Features

- **JWT-authenticated** endpoints — every graph route requires a valid Bearer token.
- **Three graph endpoints** — query by repository, file path, or domain concept.
- **Neo4j integration** — runs Cypher queries and transforms results into a
  front-end-ready JSON structure (`nodes`, `edges`, `metadata`).
- **CORS-configurable** — point at your development or production front-end URL
  via environment variables.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Node.js | ≥ 18 |
| Neo4j | ≥ 5 (Community or Enterprise) |

---

## Setup

```bash
# 1. Install dependencies
npm install

# 2. Create your environment file
cp .env.example .env
# Edit .env and fill in NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, JWT_SECRET, etc.

# 3. Start the server
npm start          # production
npm run dev        # development (auto-restarts on file change)
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEO4J_URI` | ✅ | Bolt URI of your Neo4j instance (e.g. `bolt://localhost:7687`) |
| `NEO4J_USER` | ✅ | Neo4j username |
| `NEO4J_PASSWORD` | ✅ | Neo4j password |
| `JWT_SECRET` | ✅ | Secret used to verify JWT tokens — use a long random string |
| `PORT` | | HTTP port (default `3000`) |
| `NODE_ENV` | | `development` or `production` |
| `CORS_ORIGINS` | | Comma-separated allowed origins (e.g. `http://localhost:5173`) |

---

## API

All graph endpoints require:

```
Authorization: Bearer <jwt>
```

### Health check

```
GET /health
```

Returns `{ "status": "ok" }` — no authentication needed.

### Graph by repository

```
GET /api/graph/repo?owner=<owner>&repo=<name>[&limit=200]
```

### Graph by file

```
GET /api/graph/file?owner=<owner>&repo=<name>&path=<file-path>[&limit=100]
```

### Graph by concept

```
GET /api/graph/concept?concept=<term>[&limit=100]
```

#### Response shape

```json
{
  "nodes": [
    { "id": 1, "labels": ["Repository"], "properties": { "name": "myapp" } }
  ],
  "edges": [
    { "id": 10, "type": "HAS_FILE", "source": 1, "target": 2, "properties": {} }
  ],
  "metadata": { "nodeCount": 1, "edgeCount": 1 }
}
```

---

## Development

```bash
npm test        # run Jest test suite
npm run lint    # run ESLint
```