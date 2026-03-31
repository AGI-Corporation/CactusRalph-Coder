'use strict';

const { Router } = require('express');
const { runQuery } = require('../neo4j');

const router = Router();

/**
 * Transforms raw Neo4j query results into the JSON graph structure
 * expected by front-end graph libraries (nodes + edges + metadata).
 *
 * Each row must expose `nodes` (array of Node objects) and
 * `relationships` (array of Relationship objects) returned by a
 * Cypher `RETURN` clause that uses `collect()`.
 *
 * @param {Object[]} rows - Raw records from `runQuery`.
 * @returns {{ nodes: Object[], edges: Object[] }}
 */
function toGraphPayload(rows) {
  const nodeMap = new Map();
  const edgeMap = new Map();

  for (const row of rows) {
    const nodes = row.nodes || [];
    const relationships = row.relationships || [];

    for (const node of nodes) {
      if (!node || nodeMap.has(node.identity)) continue;
      nodeMap.set(node.identity, {
        id: node.identity,
        labels: node.labels,
        properties: node.properties,
      });
    }

    for (const rel of relationships) {
      if (!rel || edgeMap.has(rel.identity)) continue;
      edgeMap.set(rel.identity, {
        id: rel.identity,
        type: rel.type,
        source: rel.start,
        target: rel.end,
        properties: rel.properties,
      });
    }
  }

  return {
    nodes: Array.from(nodeMap.values()),
    edges: Array.from(edgeMap.values()),
    metadata: { nodeCount: nodeMap.size, edgeCount: edgeMap.size },
  };
}

/**
 * GET /api/graph/repo
 *
 * Returns the full graph for a repository.
 *
 * Query params:
 *   owner  {string} – GitHub owner / organisation (required)
 *   repo   {string} – Repository name (required)
 *   limit  {number} – Max nodes to return (default 200)
 */
router.get('/repo', async (req, res, next) => {
  const { owner, repo, limit = 200 } = req.query;

  if (!owner || !repo) {
    return res.status(400).json({ error: 'Query parameters "owner" and "repo" are required' });
  }

  const cypher = `
    MATCH (r:Repository {owner: $owner, name: $repo})
    OPTIONAL MATCH path = (r)-[*1..2]-(n)
    WITH collect(DISTINCT n) + [r] AS ns,
         collect(DISTINCT relationships(path)) AS rsList
    UNWIND rsList AS rsBatch
    UNWIND rsBatch AS rs
    WITH ns, collect(DISTINCT rs) AS rels
    RETURN ns AS nodes, rels AS relationships
    LIMIT $limit
  `;

  try {
    const rows = await runQuery(cypher, { owner, repo, limit: parseInt(limit, 10) });
    return res.json(toGraphPayload(rows));
  } catch (err) {
    return next(err);
  }
});

/**
 * GET /api/graph/file
 *
 * Returns the graph neighbourhood around a specific file.
 *
 * Query params:
 *   owner  {string} – GitHub owner / organisation (required)
 *   repo   {string} – Repository name (required)
 *   path   {string} – File path within the repository (required)
 *   limit  {number} – Max nodes to return (default 100)
 */
router.get('/file', async (req, res, next) => {
  const { owner, repo, path: filePath, limit = 100 } = req.query;

  if (!owner || !repo || !filePath) {
    return res.status(400).json({
      error: 'Query parameters "owner", "repo", and "path" are required',
    });
  }

  const cypher = `
    MATCH (f:File {path: $filePath})
    WHERE f.repo = $repo AND f.owner = $owner
    OPTIONAL MATCH path = (f)-[*1..2]-(n)
    WITH collect(DISTINCT n) + [f] AS ns,
         collect(DISTINCT relationships(path)) AS rsList
    UNWIND rsList AS rsBatch
    UNWIND rsBatch AS rs
    WITH ns, collect(DISTINCT rs) AS rels
    RETURN ns AS nodes, rels AS relationships
    LIMIT $limit
  `;

  try {
    const rows = await runQuery(cypher, {
      owner,
      repo,
      filePath,
      limit: parseInt(limit, 10),
    });
    return res.json(toGraphPayload(rows));
  } catch (err) {
    return next(err);
  }
});

/**
 * GET /api/graph/concept
 *
 * Returns all nodes and relationships associated with a domain concept.
 *
 * Query params:
 *   concept {string} – Concept / term to search for (required)
 *   limit   {number} – Max nodes to return (default 100)
 */
router.get('/concept', async (req, res, next) => {
  const { concept, limit = 100 } = req.query;

  if (!concept) {
    return res.status(400).json({ error: 'Query parameter "concept" is required' });
  }

  const cypher = `
    MATCH (c:Concept)
    WHERE toLower(c.name) CONTAINS toLower($concept)
    OPTIONAL MATCH path = (c)-[*1..2]-(n)
    WITH collect(DISTINCT n) + [c] AS ns,
         collect(DISTINCT relationships(path)) AS rsList
    UNWIND rsList AS rsBatch
    UNWIND rsBatch AS rs
    WITH ns, collect(DISTINCT rs) AS rels
    RETURN ns AS nodes, rels AS relationships
    LIMIT $limit
  `;

  try {
    const rows = await runQuery(cypher, { concept, limit: parseInt(limit, 10) });
    return res.json(toGraphPayload(rows));
  } catch (err) {
    return next(err);
  }
});

module.exports = router;
