# Configuration

This page covers all configuration options for CactusRalph-Coder: environment variables, configuration files, secrets management, and deployment-specific settings.

---

## Table of Contents

1. [Configuration Files Overview](#1-configuration-files-overview)
2. [Environment Variables](#2-environment-variables)
3. [ralph.config.json](#3-ralphconfigjson)
   - 3.1 [Agent Settings](#31-agent-settings)
   - 3.2 [Memory Settings](#32-memory-settings)
   - 3.3 [Interaction Mode](#33-interaction-mode)
4. [ralph_meter_config.json](#4-ralph_meter_configjson)
   - 4.1 [Dimension Weights](#41-dimension-weights)
   - 4.2 [Score Thresholds](#42-score-thresholds)
   - 4.3 [Iteration Limits](#43-iteration-limits)
5. [self_build_config.json](#5-self_build_configjson)
6. [Secrets Management](#6-secrets-management)
7. [GitHub Actions Setup](#7-github-actions-setup)
8. [Local Development Setup](#8-local-development-setup)
9. [Advanced Tuning](#9-advanced-tuning)
10. [Configuration Validation](#10-configuration-validation)

---

## 1. Configuration Files Overview

CactusRalph-Coder uses three JSON configuration files at the repository root:

| File | Purpose |
|---|---|
| `ralph.config.json` | Core agent behaviour, memory, and interaction settings |
| `ralph_meter_config.json` | Scoring weights, thresholds, and iteration limits |
| `self_build_config.json` | Self-build triggers, rate limits, and allowed components |

All three files are optional. Sensible defaults are used when a file is absent. Invalid configuration causes a startup error with a descriptive message indicating which key is invalid and what values are accepted.

---

## 2. Environment Variables

Secrets and environment-specific settings are provided via environment variables, **never** in config files.

| Variable | Required | Description |
|---|---|---|
| `RALPH_LLM_API_KEY` | Yes | API key for the language model provider |
| `RALPH_LLM_ENDPOINT` | No | Custom endpoint URL (default: provider's public API) |
| `RALPH_LLM_MODEL` | No | Model name/ID to use (default: configured in `ralph.config.json`) |
| `RALPH_VECTOR_DB_URL` | No | Connection URL for the vector database |
| `RALPH_VECTOR_DB_API_KEY` | No | API key for the vector database |
| `GITHUB_TOKEN` | Yes (GitHub Actions) | Token used for GitHub API calls |
| `RALPH_LOG_LEVEL` | No | Log verbosity: `DEBUG`, `INFO`, `WARN`, `ERROR` (default: `INFO`) |
| `RALPH_DISABLE_SELF_BUILD` | No | Set to `true` to disable all self-build activity |
| `RALPH_READONLY` | No | Set to `true` to prevent any file writes or commits |

---

## 3. ralph.config.json

### 3.1 Agent Settings

```json
{
  "agent": {
    "model": "gpt-4o",
    "max_tokens_per_call": 4096,
    "temperature": 0.2,
    "top_p": 0.95,
    "max_actions_per_session": 100,
    "parallel_actions_enabled": false,
    "tool_call_timeout_seconds": 30,
    "tool_call_retry_count": 3,
    "tool_call_retry_backoff_seconds": 5
  }
}
```

| Key | Type | Default | Description |
|---|---|---|---|
| `model` | string | `"gpt-4o"` | Language model identifier |
| `max_tokens_per_call` | integer | `4096` | Max tokens in a single LLM call |
| `temperature` | float | `0.2` | Sampling temperature (lower = more deterministic) |
| `top_p` | float | `0.95` | Nucleus sampling parameter |
| `max_actions_per_session` | integer | `100` | Hard cap on actions per session (prevents runaway loops) |
| `parallel_actions_enabled` | boolean | `false` | Enable parallel execution of independent actions |
| `tool_call_timeout_seconds` | integer | `30` | Seconds before a tool call is considered timed out |
| `tool_call_retry_count` | integer | `3` | Number of retries after a tool call failure |
| `tool_call_retry_backoff_seconds` | integer | `5` | Wait time between retries |

### 3.2 Memory Settings

```json
{
  "memory": {
    "short_term_compression_threshold": 0.8,
    "long_term_query_top_k": 10,
    "episode_history_depth": 5,
    "vector_db_provider": "chromadb",
    "vector_db_collection": "ralph_memory"
  }
}
```

| Key | Type | Default | Description |
|---|---|---|---|
| `short_term_compression_threshold` | float | `0.8` | Fraction of context window at which compression triggers |
| `long_term_query_top_k` | integer | `10` | Number of facts to retrieve from long-term memory per query |
| `episode_history_depth` | integer | `5` | Number of recent episodes to load at session start |
| `vector_db_provider` | string | `"chromadb"` | Vector database backend (`chromadb`, `pinecone`, `weaviate`) |
| `vector_db_collection` | string | `"ralph_memory"` | Collection/index name in the vector database |

### 3.3 Interaction Mode

```json
{
  "interaction": {
    "default_mode": "interactive",
    "autonomous_mode_confirmation_threshold": 10,
    "pause_on_destructive_actions": true,
    "session_report_verbosity": "detailed"
  }
}
```

| Key | Type | Default | Description |
|---|---|---|---|
| `default_mode` | string | `"interactive"` | Default mode: `interactive`, `autonomous`, or `review` |
| `autonomous_mode_confirmation_threshold` | integer | `10` | Number of dependents above which confirmation is required for self-builds |
| `pause_on_destructive_actions` | boolean | `true` | Whether to pause and ask for confirmation on destructive actions |
| `session_report_verbosity` | string | `"detailed"` | Report verbosity: `minimal`, `standard`, or `detailed` |

---

## 4. ralph_meter_config.json

### 4.1 Dimension Weights

Weights must sum to exactly 100. Changing weights takes effect immediately on the next session.

```json
{
  "dimension_weights": {
    "correctness": 25,
    "security": 20,
    "completeness": 15,
    "code_quality": 12,
    "test_coverage": 12,
    "readability": 8,
    "performance": 5,
    "efficiency": 3
  }
}
```

See the [Ralph Meter – Dimension Weights Reference Table](Ralph-Meter.md#9-dimension-weights-reference-table) for allowed ranges.

### 4.2 Score Thresholds

```json
{
  "score_thresholds": {
    "excellent": 90,
    "good": 75,
    "acceptable": 60,
    "poor": 40,
    "security_hard_floor": 50
  }
}
```

| Key | Default | Description |
|---|---|---|
| `excellent` | `90` | Minimum score for Excellent band |
| `good` | `75` | Minimum score for Good band |
| `acceptable` | `60` | Minimum score to pass (below this triggers iteration) |
| `poor` | `40` | Minimum score for Poor band (below this triggers a restart) |
| `security_hard_floor` | `50` | Minimum Security dimension score regardless of other dimensions |

### 4.3 Iteration Limits

```json
{
  "iteration_limits": {
    "max_retries_per_action": 3,
    "max_self_build_retries": 3,
    "max_sessions_for_trend": 30
  }
}
```

---

## 5. self_build_config.json

```json
{
  "self_build": {
    "enabled": true,
    "max_self_builds_per_day": 5,
    "min_score_improvement_required": 5,
    "trigger_utility_score_threshold": 60,
    "trigger_failure_count_threshold": 3,
    "require_human_confirmation_above_dependents": 10,
    "allowed_strategies": ["rewrite", "patch", "augment"],
    "evolution_population_size": 5,
    "evolution_max_generations": 3
  }
}
```

| Key | Type | Default | Description |
|---|---|---|---|
| `enabled` | boolean | `true` | Master switch for all self-build activity |
| `max_self_builds_per_day` | integer | `5` | Daily rate limit for self-build operations |
| `min_score_improvement_required` | integer | `5` | Minimum Ralph Meter improvement needed to accept a self-build |
| `trigger_utility_score_threshold` | integer | `60` | Utility score below which a tool is flagged for self-build |
| `trigger_failure_count_threshold` | integer | `3` | Number of failures before a tool is flagged for self-build |
| `require_human_confirmation_above_dependents` | integer | `10` | Self-builds on components with more than N dependents require confirmation |
| `allowed_strategies` | array | all | Which generation strategies are permitted |
| `evolution_population_size` | integer | `5` | Number of variants generated in evolutionary mode |
| `evolution_max_generations` | integer | `3` | Maximum generations in evolutionary mode |

---

## 6. Secrets Management

**Never** store secrets in configuration files or source code. CactusRalph-Coder reads secrets exclusively from environment variables.

**Recommended approaches:**

| Environment | Recommended Secret Store |
|---|---|
| GitHub Actions | GitHub Actions Secrets (`Settings → Secrets and variables → Actions`) |
| Local development | `.env` file (ensure `.env` is in `.gitignore`) |
| Self-hosted server | OS environment variables or HashiCorp Vault |
| Serverless | Provider-native secret store (AWS Secrets Manager, GCP Secret Manager, etc.) |

Ralph scans all files before committing for common secret patterns. If a secret pattern is detected, the commit is blocked and a warning is shown.

---

## 7. GitHub Actions Setup

Add a workflow file at `.github/workflows/ralph.yml`:

```yaml
name: CactusRalph-Coder

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [opened, synchronize]

jobs:
  ralph:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Ralph
        uses: AGI-Corporation/CactusRalph-Coder@main
        with:
          mode: autonomous
        env:
          RALPH_LLM_API_KEY: ${{ secrets.RALPH_LLM_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Required secrets:**
- `RALPH_LLM_API_KEY` — set in repository secrets.

**Optional secrets:**
- `RALPH_VECTOR_DB_URL` and `RALPH_VECTOR_DB_API_KEY` — only needed if using a persistent vector database for long-term memory.

---

## 8. Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/AGI-Corporation/CactusRalph-Coder.git
cd CactusRalph-Coder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a .env file (never commit this file)
cat > .env << EOF
RALPH_LLM_API_KEY=your_api_key_here
RALPH_LOG_LEVEL=DEBUG
EOF

# 4. Run Ralph in interactive mode
python -m ralph --mode interactive "Your task description here"

# 5. Run Ralph in review mode on a file
python -m ralph --mode review src/your_file.py
```

---

## 9. Advanced Tuning

### Lowering Temperature for Determinism

For tasks requiring highly predictable output (e.g., boilerplate generation), lower the temperature:

```json
{
  "agent": {
    "temperature": 0.0
  }
}
```

### Enabling Parallel Actions

For projects where independent actions (e.g., writing tests for multiple independent modules) are common:

```json
{
  "agent": {
    "parallel_actions_enabled": true
  }
}
```

⚠️ Parallel actions increase token usage and can produce harder-to-debug logs. Only enable if sequential execution is a bottleneck.

### Disabling Self-Builds for Stability

For production-critical repositories where stability is more important than self-improvement:

```json
{
  "self_build": {
    "enabled": false
  }
}
```

Or via environment variable:

```bash
export RALPH_DISABLE_SELF_BUILD=true
```

---

## 10. Configuration Validation

Ralph validates all configuration at startup. Validation checks include:

- All required keys are present (if a config file exists).
- All values are within allowed ranges.
- Dimension weights sum to exactly 100.
- Score thresholds form a monotonically increasing sequence.
- No secrets are present in config files.

If validation fails, Ralph exits with a non-zero status code and prints a human-readable error:

```
[CONFIG ERROR] ralph_meter_config.json:
  - dimension_weights: weights sum to 97, must sum to 100
  - score_thresholds.acceptable: value 55 is below minimum 60
```

---

*See also: [Ralph](Ralph.md) | [Ralph Meter](Ralph-Meter.md) | [Self-Building Codes](Self-Building-Codes.md) | [Architecture](Architecture.md)*
