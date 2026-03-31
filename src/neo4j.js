'use strict';

const neo4j = require('neo4j-driver');
const config = require('./config');

let _driver = null;

/**
 * Returns a singleton Neo4j driver instance.
 */
function getDriver() {
  if (!_driver) {
    _driver = neo4j.driver(
      config.neo4j.uri,
      neo4j.auth.basic(config.neo4j.user, config.neo4j.password),
      {
        disableLosslessIntegers: true,
        logging: neo4j.logging.console(
          config.nodeEnv === 'production' ? 'warn' : 'info',
        ),
      },
    );
  }
  return _driver;
}

/**
 * Runs a Cypher query and returns an array of plain JS objects.
 *
 * @param {string} cypher - The Cypher query string.
 * @param {Object} params  - Query parameters.
 * @returns {Promise<Object[]>} Rows as plain objects.
 */
async function runQuery(cypher, params = {}) {
  const driver = getDriver();
  const session = driver.session({ defaultAccessMode: neo4j.session.READ });
  try {
    const result = await session.run(cypher, params);
    return result.records.map((record) => record.toObject());
  } finally {
    await session.close();
  }
}

/**
 * Gracefully closes the driver (call on process exit).
 */
async function closeDriver() {
  if (_driver) {
    await _driver.close();
    _driver = null;
  }
}

module.exports = { getDriver, runQuery, closeDriver };
