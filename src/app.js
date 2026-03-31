'use strict';

const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const config = require('./config');
const { authenticate } = require('./auth/middleware');
const graphRouter = require('./routes/graph');

const app = express();

// ------------------------------------------------------------------
// CORS
// ------------------------------------------------------------------
app.use(
  cors({
    origin: config.cors.origins.length ? config.cors.origins : false,
    methods: ['GET'],
    allowedHeaders: ['Authorization', 'Content-Type'],
  }),
);

// ------------------------------------------------------------------
// Body parsing
// ------------------------------------------------------------------
app.use(express.json());

// ------------------------------------------------------------------
// Health check (no auth required)
// ------------------------------------------------------------------
app.get('/health', (_req, res) => res.json({ status: 'ok' }));

// ------------------------------------------------------------------
// Rate limiting for authenticated API routes
// ------------------------------------------------------------------
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,                  // max 100 requests per window per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later' },
});

// ------------------------------------------------------------------
// Graph API (JWT-protected, rate-limited)
// ------------------------------------------------------------------
app.use('/api/graph', apiLimiter, authenticate, graphRouter);

// ------------------------------------------------------------------
// 404 handler
// ------------------------------------------------------------------
app.use((_req, res) => res.status(404).json({ error: 'Not found' }));

// ------------------------------------------------------------------
// Global error handler
// ------------------------------------------------------------------
// eslint-disable-next-line no-unused-vars
app.use((err, _req, res, _next) => {
  const status = err.status || err.statusCode || 500;
  const message =
    config.nodeEnv === 'production' && status === 500
      ? 'Internal server error'
      : err.message || 'Internal server error';

  if (status === 500) {
    console.error(err);
  }

  res.status(status).json({ error: message });
});

module.exports = app;
