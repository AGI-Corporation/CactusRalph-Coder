# Ralph

Ralph is the heart of CactusRalph-Coder — an autonomous, self-aware coding agent designed to understand complex software engineering problems, reason through multi-step solutions, and produce high-quality code without constant human supervision.

---

## Table of Contents

1. [What Is Ralph?](#1-what-is-ralph)
2. [Personality and Identity](#2-personality-and-identity)
3. [Core Capabilities](#3-core-capabilities)
4. [Reasoning Architecture](#4-reasoning-architecture)
   - 4.1 [Perception Layer](#41-perception-layer)
   - 4.2 [Working Memory](#42-working-memory)
   - 4.3 [Planning Module](#43-planning-module)
   - 4.4 [Execution Engine](#44-execution-engine)
   - 4.5 [Reflection Loop](#45-reflection-loop)
5. [Tool Use](#5-tool-use)
   - 5.1 [File System Tools](#51-file-system-tools)
   - 5.2 [Code Execution Tools](#52-code-execution-tools)
   - 5.3 [Search and Retrieval Tools](#53-search-and-retrieval-tools)
   - 5.4 [Communication Tools](#54-communication-tools)
6. [Decision-Making Model](#6-decision-making-model)
7. [Context Window Management](#7-context-window-management)
8. [Memory Systems](#8-memory-systems)
   - 8.1 [Short-Term Memory](#81-short-term-memory)
   - 8.2 [Long-Term Memory](#82-long-term-memory)
   - 8.3 [Episodic Memory](#83-episodic-memory)
9. [Error Handling and Recovery](#9-error-handling-and-recovery)
10. [Ralph's Internal Monologue](#10-ralphs-internal-monologue)
11. [Interaction Modes](#11-interaction-modes)
    - 11.1 [Interactive Mode](#111-interactive-mode)
    - 11.2 [Autonomous Mode](#112-autonomous-mode)
    - 11.3 [Review Mode](#113-review-mode)
12. [Safety and Guardrails](#12-safety-and-guardrails)
13. [Versioning Ralph](#13-versioning-ralph)

---

## 1. What Is Ralph?

Ralph is a **large-language-model-powered autonomous agent** that specialises in software development tasks. Unlike a simple chatbot that answers questions, Ralph:

- Maintains **persistent state** across an entire session.
- Breaks large goals into **hierarchical sub-tasks**.
- Executes code, reads files, browses documentation, and validates results — all without leaving the agent loop.
- Scores its own work using the **Ralph Meter** and iterates until quality thresholds are met.
- Can modify its own tooling and code through the **Self-Building Codes** engine.

---

## 2. Personality and Identity

Ralph has a defined persona that influences the tone, style, and approach of every interaction:

| Trait | Description |
|---|---|
| **Curious** | Ralph proactively asks clarifying questions when requirements are ambiguous |
| **Methodical** | Ralph decomposes problems before writing a single line of code |
| **Honest** | Ralph acknowledges uncertainty and never fabricates facts |
| **Resilient** | Like its cactus namesake, Ralph thrives in harsh, constrained environments |
| **Direct** | Ralph communicates concisely — no unnecessary filler text |

Ralph does not have a fixed voice model or avatar, but its text responses are always structured, readable, and annotated with reasoning where appropriate.

---

## 3. Core Capabilities

| Capability | Detail |
|---|---|
| **Code Generation** | Produces idiomatic code in any mainstream language |
| **Code Review** | Reads existing code and produces structured, prioritised review feedback |
| **Refactoring** | Applies safe, semantic-preserving transformations to improve code quality |
| **Debugging** | Traces stack traces and runtime errors back to their root cause |
| **Test Writing** | Generates unit, integration, and end-to-end tests with realistic edge cases |
| **Documentation** | Writes inline comments, docstrings, README files, and wiki pages |
| **Architecture Design** | Produces system diagrams and architectural decision records (ADRs) |
| **Dependency Management** | Audits, upgrades, and explains third-party dependencies |
| **CI/CD Integration** | Reads pipeline logs, diagnoses failures, and patches workflow files |
| **Self-Improvement** | Rewrites its own helpers and tool wrappers when better approaches are discovered |

---

## 4. Reasoning Architecture

Ralph's reasoning is structured as a layered pipeline. Each layer has a specific responsibility and passes its output to the next.

### 4.1 Perception Layer

The perception layer ingests all incoming data:

- **User prompt** — the raw human instruction.
- **Repository snapshot** — file tree, recent git log, open issues.
- **Previous turn context** — a compressed summary of the current session.
- **Tool outputs** — results from previous tool calls in this session.

The perception layer normalises this data into a structured `PerceptionBundle` object before passing it to working memory.

### 4.2 Working Memory

Working memory is Ralph's scratchpad. It holds:

- The **current goal** (top-level task from the user).
- **Sub-goals** (intermediate steps needed to reach the goal).
- **Active constraints** (e.g., "do not modify `main.py`", "use Python 3.11+").
- **Observed facts** (things Ralph has discovered during this session).
- **Open questions** (things Ralph still needs to determine).

Working memory is bounded by the context window. When it fills up, the [Context Window Management](#7-context-window-management) subsystem compresses older entries.

### 4.3 Planning Module

The planning module converts the current goal + observed facts into an **ordered action plan**:

1. **Goal decomposition** — break the goal into atomic sub-tasks.
2. **Dependency ordering** — arrange sub-tasks so that prerequisites come first.
3. **Tool selection** — choose the best tool for each sub-task.
4. **Risk assessment** — flag destructive or irreversible actions (e.g., file deletion).

The plan is stored as a list of `ActionNode` objects, each with a `status` field (`pending | in_progress | done | failed | skipped`).

### 4.4 Execution Engine

The execution engine iterates over the action plan and calls the appropriate tool for each `ActionNode`. Execution is:

- **Sequential by default** — one action at a time for predictability.
- **Parallelisable** — independent actions with no shared state can be parallelised when explicitly marked safe.
- **Transactional where possible** — file edits are staged before committing so that failures can be rolled back.

### 4.5 Reflection Loop

After each action, Ralph enters a micro-reflection step:

1. **Validate** — did the tool return the expected output format?
2. **Assert** — do the observed facts still hold after this action?
3. **Score** — what does the Ralph Meter report for this action?
4. **Adapt** — update the plan based on new information.

If the Ralph Meter score for an action is below threshold, Ralph re-attempts the action with a refined approach before moving on.

---

## 5. Tool Use

Ralph operates through a strictly defined tool interface. Every tool has:

- A **name** (unique identifier).
- A **description** (what it does and when to use it).
- A **parameter schema** (JSON Schema for inputs).
- A **return schema** (JSON Schema for outputs).
- A **safety rating** (`safe | caution | destructive`).

### 5.1 File System Tools

| Tool | Description | Safety |
|---|---|---|
| `read_file` | Read a file's full contents | safe |
| `view_directory` | List files in a directory | safe |
| `write_file` | Create or overwrite a file | caution |
| `edit_file` | Apply a targeted string replacement | caution |
| `delete_file` | Permanently remove a file | destructive |
| `move_file` | Rename or relocate a file | caution |

### 5.2 Code Execution Tools

| Tool | Description | Safety |
|---|---|---|
| `run_bash` | Execute a shell command | caution |
| `run_tests` | Run the project's test suite | safe |
| `run_linter` | Run the project's linter | safe |
| `run_build` | Build the project | safe |

### 5.3 Search and Retrieval Tools

| Tool | Description | Safety |
|---|---|---|
| `grep_code` | Search file contents with regex | safe |
| `glob_files` | Find files by name pattern | safe |
| `search_web` | Retrieve information from the internet | safe |
| `search_docs` | Query internal documentation index | safe |

### 5.4 Communication Tools

| Tool | Description | Safety |
|---|---|---|
| `report_progress` | Push commits and update PR description | caution |
| `post_comment` | Add a comment to a GitHub issue or PR | caution |
| `request_review` | Trigger a code review agent | safe |

---

## 6. Decision-Making Model

Ralph uses a **cost-benefit decision framework** when choosing between multiple possible actions:

```
score(action) = (expected_value × confidence) - (risk_penalty × risk_level) - token_cost
```

Where:

- `expected_value` — estimated gain in goal completion (0–1).
- `confidence` — Ralph's certainty that the action achieves the expected value (0–1).
- `risk_penalty` — multiplier applied to destructive or irreversible actions (1–10).
- `risk_level` — how destructive the action is (0–1).
- `token_cost` — relative cost of executing the action in tokens.

Ralph always chooses the action with the highest `score`. Ties are broken by preferring **reversible** actions.

---

## 7. Context Window Management

Ralph's effective context window is finite. The Context Window Manager (CWM) ensures Ralph never loses critical information:

1. **Priority tagging** — every item in working memory is tagged with a priority (`critical | high | medium | low`).
2. **Compression** — when memory exceeds 80% capacity, `low` and `medium` items are summarised into compact bullet points.
3. **Archiving** — items summarised beyond recovery are saved to [Long-Term Memory](#82-long-term-memory).
4. **Injection** — when an archived item becomes relevant again (detected via keyword similarity), it is re-injected into working memory.

---

## 8. Memory Systems

### 8.1 Short-Term Memory

Short-term memory is the **active context window**. It is ephemeral and reset at the end of each session. Contains:

- Full user conversation history (current session only).
- Uncompressed working memory.
- Raw tool outputs from the last N actions.

### 8.2 Long-Term Memory

Long-term memory persists across sessions and is stored in a vector database. It contains:

- **Project facts** — repository structure, language choices, coding conventions.
- **User preferences** — communication style, tool preferences, domain focus.
- **Compressed episode summaries** — what was accomplished in each past session.

Ralph queries long-term memory at the start of every new session and injects the top-K most relevant facts into working memory.

### 8.3 Episodic Memory

Episodic memory is a special form of long-term memory structured as a timeline of **session episodes**. Each episode record includes:

- Session ID and timestamp.
- Goal that was attempted.
- Actions taken (summary).
- Final outcome (success / partial / failure).
- Lessons learned (key insights extracted by reflection).

Episodic memory powers Ralph's ability to say "I tried this approach before and it failed because…".

---

## 9. Error Handling and Recovery

Ralph distinguishes between four classes of errors:

| Class | Description | Recovery Strategy |
|---|---|---|
| **Tool Error** | A tool returned an unexpected error | Retry with backoff; if persistent, choose alternative tool |
| **Logic Error** | Ralph's reasoning led to an incorrect outcome | Reflect on failure, update plan, retry with revised approach |
| **Constraint Violation** | An action would break a stated constraint | Abort action, inform user, ask for guidance |
| **Unrecoverable Error** | State is corrupted or goal is impossible | Halt, explain situation, propose next steps to user |

All errors are logged with:
- Timestamp
- Action that caused the error
- Error message and stack trace (if available)
- Recovery action taken
- Ralph Meter score delta caused by the error

---

## 10. Ralph's Internal Monologue

Ralph maintains a structured internal monologue that is separate from its user-facing output. The monologue follows this template at each reasoning step:

```
[OBSERVE]  What do I know right now?
[ORIENT]   What is my current goal? What sub-goal am I working on?
[DECIDE]   What is the best next action? Why?
[ACT]      Execute the action.
[REVIEW]   Did it work? What did I learn? Update memory.
```

This is an implementation of the **OODA loop** (Observe → Orient → Decide → Act) adapted for software engineering agents.

---

## 11. Interaction Modes

### 11.1 Interactive Mode

In interactive mode, Ralph pauses after each major action and presents:
- A summary of what was just done.
- The current state of the plan.
- A prompt asking the user to confirm, redirect, or stop.

Use this mode when you want fine-grained control over Ralph's actions.

### 11.2 Autonomous Mode

In autonomous mode, Ralph executes the full plan without pausing. It only surfaces to the user when:
- A `destructive` safety-rated action is required.
- A constraint violation is detected.
- An unrecoverable error occurs.
- The goal is complete.

Use this mode for well-defined tasks that don't need human steering.

### 11.3 Review Mode

In review mode, Ralph reads existing code and produces a structured review report without making any changes. The report includes:

- Summary of what the code does.
- Bugs found (with severity ratings).
- Security vulnerabilities found.
- Performance improvement opportunities.
- Code style violations.
- Missing tests.
- Suggested refactors.

---

## 12. Safety and Guardrails

Ralph enforces the following guardrails unconditionally:

1. **Never commit secrets** — Ralph scans all file content before committing for API keys, passwords, and tokens.
2. **Never execute obfuscated commands** — commands using shell expansion tricks or eval-like constructs are rejected.
3. **Never access disallowed paths** — certain directories (e.g., `.github/agents/`) are off-limits.
4. **Never push directly to protected branches** — Ralph always creates a PR; it never force-pushes to `main`.
5. **Never fabricate facts** — Ralph will state uncertainty rather than guess.
6. **Always confirm destructive actions** — any action rated `destructive` requires explicit user confirmation in interactive mode.

---

## 13. Versioning Ralph

Ralph itself is versioned using semantic versioning (`MAJOR.MINOR.PATCH`):

| Component | Trigger |
|---|---|
| `MAJOR` | Changes to the core reasoning architecture or tool interface |
| `MINOR` | Addition of new tools, new capabilities, or new interaction modes |
| `PATCH` | Bug fixes, prompt tuning, and minor behaviour adjustments |

The current version is stored in `ralph_version.json` at the repository root. Changelogs are maintained in `CHANGELOG.md`.

---

*See also: [Ralph Meter](Ralph-Meter.md) | [Self-Building Codes](Self-Building-Codes.md) | [Architecture](Architecture.md)*
