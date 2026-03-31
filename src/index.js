'use strict';

const app = require('./app');
const config = require('./config');
const { closeDriver } = require('./neo4j');

const server = app.listen(config.port, () => {
  console.log(
    `[${config.nodeEnv}] CactusRalph-Coder API listening on port ${config.port}`,
  );
});

async function shutdown(signal) {
  console.log(`Received ${signal}. Shutting down…`);
  server.close(async () => {
    await closeDriver();
    process.exit(0);
  });
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
