'use strict';

const jwt = require('jsonwebtoken');
const config = require('../config');

/**
 * Express middleware that validates a JWT Bearer token.
 *
 * Expects:  Authorization: Bearer <token>
 *
 * On success, attaches the decoded payload to `req.user` and calls `next()`.
 * On failure, responds with 401 Unauthorized.
 */
function authenticate(req, res, next) {
  const authHeader = req.headers['authorization'] || '';
  const [scheme, token] = authHeader.split(' ');

  if (scheme !== 'Bearer' || !token) {
    return res.status(401).json({ error: 'Missing or malformed Authorization header' });
  }

  try {
    req.user = jwt.verify(token, config.jwt.secret);
    return next();
  } catch {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

module.exports = { authenticate };
