'use strict';

// Set env vars BEFORE requiring any app module so config.js doesn't throw.
process.env.NEO4J_URI = 'bolt://localhost:7687';
process.env.NEO4J_USER = 'neo4j';
process.env.NEO4J_PASSWORD = 'test-password';
process.env.JWT_SECRET = 'test-jwt-secret-that-is-long-enough';
process.env.CORS_ORIGINS = 'http://localhost:3000';
process.env.NODE_ENV = 'test';

const request = require('supertest');
const jwt = require('jsonwebtoken');
const app = require('../src/app');

// Mock the Neo4j layer so tests run without a live database.
jest.mock('../src/neo4j', () => ({
  runQuery: jest.fn(),
  closeDriver: jest.fn(),
}));

const { runQuery } = require('../src/neo4j');

const JWT_SECRET = process.env.JWT_SECRET;

function makeToken(payload = { sub: 'user-1' }) {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: '1h' });
}

// ---------------------------------------------------------------------------
// Helper: build a fake Neo4j row with node/relationship stubs
// ---------------------------------------------------------------------------
function fakeRow(nodes = [], relationships = []) {
  return { nodes, relationships };
}

const fakeNode = (id, labels, props) => ({
  identity: id,
  labels,
  properties: props,
});
const fakeRel = (id, type, start, end, props = {}) => ({
  identity: id,
  type,
  start,
  end,
  properties: props,
});

// ---------------------------------------------------------------------------
// Health check
// ---------------------------------------------------------------------------
describe('GET /health', () => {
  it('returns 200 ok without authentication', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: 'ok' });
  });
});

// ---------------------------------------------------------------------------
// Authentication middleware
// ---------------------------------------------------------------------------
describe('Authentication middleware', () => {
  it('returns 401 when Authorization header is absent', async () => {
    const res = await request(app).get('/api/graph/repo?owner=acme&repo=myapp');
    expect(res.status).toBe(401);
  });

  it('returns 401 for a malformed header (no Bearer prefix)', async () => {
    const res = await request(app)
      .get('/api/graph/repo?owner=acme&repo=myapp')
      .set('Authorization', 'Token abc123');
    expect(res.status).toBe(401);
  });

  it('returns 401 for an invalid token', async () => {
    const res = await request(app)
      .get('/api/graph/repo?owner=acme&repo=myapp')
      .set('Authorization', 'Bearer invalid.token.here');
    expect(res.status).toBe(401);
  });

  it('returns 401 for a token signed with the wrong secret', async () => {
    const badToken = jwt.sign({ sub: 'user-x' }, 'wrong-secret');
    const res = await request(app)
      .get('/api/graph/repo?owner=acme&repo=myapp')
      .set('Authorization', `Bearer ${badToken}`);
    expect(res.status).toBe(401);
  });
});

// ---------------------------------------------------------------------------
// GET /api/graph/repo
// ---------------------------------------------------------------------------
describe('GET /api/graph/repo', () => {
  const token = makeToken();

  beforeEach(() => runQuery.mockReset());

  it('returns 400 when owner is missing', async () => {
    const res = await request(app)
      .get('/api/graph/repo?repo=myapp')
      .set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/owner/i);
  });

  it('returns 400 when repo is missing', async () => {
    const res = await request(app)
      .get('/api/graph/repo?owner=acme')
      .set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/repo/i);
  });

  it('returns a graph payload for a valid request', async () => {
    const node = fakeNode(1, ['Repository'], { name: 'myapp', owner: 'acme' });
    const rel = fakeRel(10, 'HAS_FILE', 1, 2);
    runQuery.mockResolvedValueOnce([fakeRow([node], [rel])]);

    const res = await request(app)
      .get('/api/graph/repo?owner=acme&repo=myapp')
      .set('Authorization', `Bearer ${token}`);

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('nodes');
    expect(res.body).toHaveProperty('edges');
    expect(res.body).toHaveProperty('metadata');
    expect(res.body.nodes).toHaveLength(1);
    expect(res.body.edges).toHaveLength(1);
    expect(res.body.metadata.nodeCount).toBe(1);
    expect(res.body.metadata.edgeCount).toBe(1);
  });

  it('returns an empty graph when no data is found', async () => {
    runQuery.mockResolvedValueOnce([]);

    const res = await request(app)
      .get('/api/graph/repo?owner=acme&repo=empty')
      .set('Authorization', `Bearer ${token}`);

    expect(res.status).toBe(200);
    expect(res.body.nodes).toHaveLength(0);
    expect(res.body.edges).toHaveLength(0);
  });

  it('returns 500 when the Neo4j query fails', async () => {
    runQuery.mockRejectedValueOnce(new Error('Connection refused'));

    const res = await request(app)
      .get('/api/graph/repo?owner=acme&repo=myapp')
      .set('Authorization', `Bearer ${token}`);

    expect(res.status).toBe(500);
  });
});

// ---------------------------------------------------------------------------
// GET /api/graph/file
// ---------------------------------------------------------------------------
describe('GET /api/graph/file', () => {
  const token = makeToken();

  beforeEach(() => runQuery.mockReset());

  it('returns 400 when path is missing', async () => {
    const res = await request(app)
      .get('/api/graph/file?owner=acme&repo=myapp')
      .set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/path/i);
  });

  it('returns a graph payload for a valid request', async () => {
    const node = fakeNode(2, ['File'], { path: 'src/index.js' });
    runQuery.mockResolvedValueOnce([fakeRow([node], [])]);

    const res = await request(app)
      .get('/api/graph/file?owner=acme&repo=myapp&path=src/index.js')
      .set('Authorization', `Bearer ${token}`);

    expect(res.status).toBe(200);
    expect(res.body.nodes[0].labels).toContain('File');
  });
});

// ---------------------------------------------------------------------------
// GET /api/graph/concept
// ---------------------------------------------------------------------------
describe('GET /api/graph/concept', () => {
  const token = makeToken();

  beforeEach(() => runQuery.mockReset());

  it('returns 400 when concept is missing', async () => {
    const res = await request(app)
      .get('/api/graph/concept')
      .set('Authorization', `Bearer ${token}`);
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/concept/i);
  });

  it('returns a graph payload for a valid request', async () => {
    const node = fakeNode(3, ['Concept'], { name: 'Aggregate' });
    const rel = fakeRel(20, 'DEFINED_IN', 3, 2);
    runQuery.mockResolvedValueOnce([fakeRow([node], [rel])]);

    const res = await request(app)
      .get('/api/graph/concept?concept=Aggregate')
      .set('Authorization', `Bearer ${token}`);

    expect(res.status).toBe(200);
    expect(res.body.nodes[0].labels).toContain('Concept');
    expect(res.body.edges).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// 404 handler
// ---------------------------------------------------------------------------
describe('404 handler', () => {
  it('returns 404 for unknown routes', async () => {
    const res = await request(app).get('/api/unknown-route');
    expect(res.status).toBe(404);
  });
});
