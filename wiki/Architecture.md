# Architecture

This page describes the full system architecture of CactusRalph-Coder: how components are organised, how data flows between them, and how the runtime model works.

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Component Map](#2-component-map)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
   - 3.1 [Standard Task Flow](#31-standard-task-flow)
   - 3.2 [Self-Build Flow](#32-self-build-flow)
   - 3.3 [Memory Read/Write Flow](#33-memory-readwrite-flow)
4. [Runtime Model](#4-runtime-model)
5. [Layer Descriptions](#5-layer-descriptions)
   - 5.1 [Interface Layer](#51-interface-layer)
   - 5.2 [Agent Core Layer](#52-agent-core-layer)
   - 5.3 [Tool Layer](#53-tool-layer)
   - 5.4 [Memory Layer](#54-memory-layer)
   - 5.5 [Scoring Layer](#55-scoring-layer)
   - 5.6 [Self-Build Layer](#56-self-build-layer)
6. [External Dependencies](#6-external-dependencies)
7. [Deployment Topologies](#7-deployment-topologies)

---

## 1. High-Level Overview

CactusRalph-Coder is structured as a **layered agent system**:

```
┌─────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                  │
│           (GitHub, CLI, REST API, IDE Plugin)       │
└──────────────────────┬──────────────────────────────┘
                       │ user prompt + context
┌──────────────────────▼──────────────────────────────┐
│                  AGENT CORE LAYER                   │
│    Perception → Working Memory → Planning →         │
│           Execution Engine → Reflection             │
└────┬──────────────┬────────────────┬────────────────┘
     │              │                │
┌────▼────┐  ┌──────▼──────┐  ┌──────▼──────┐
│  TOOL   │  │   MEMORY    │  │  SCORING    │
│  LAYER  │  │   LAYER     │  │  LAYER      │
│ (FS,    │  │ (Short-Term │  │ (Ralph      │
│  Shell, │  │  Long-Term  │  │  Meter)     │
│  Search)│  │  Episodic)  │  │             │
└─────────┘  └─────────────┘  └──────┬──────┘
                                      │ score signal
                              ┌───────▼──────┐
                              │  SELF-BUILD  │
                              │    LAYER     │
                              └──────────────┘
```

---

## 2. Component Map

| Component | File/Module | Responsibility |
|---|---|---|
| **PerceptionBundle** | `core/perception.py` | Normalise all incoming inputs |
| **WorkingMemory** | `core/working_memory.py` | Hold active goals and facts |
| **PlanningModule** | `core/planning.py` | Decompose goals into action plans |
| **ExecutionEngine** | `core/execution.py` | Execute action plans step by step |
| **ReflectionLoop** | `core/reflection.py` | Score and adapt after each action |
| **ContextWindowManager** | `core/cwm.py` | Compress and manage context limits |
| **ToolRegistry** | `tools/registry.py` | Register, discover, and call tools |
| **MemoryManager** | `memory/manager.py` | Coordinate all memory subsystems |
| **VectorStore** | `memory/vector_store.py` | Persist and query long-term memory |
| **EpisodeStore** | `memory/episode_store.py` | Store session episode records |
| **RalphMeter** | `ralph_meter/scorer.py` | Score all actions and outputs |
| **SelfBuildController** | `self_builds/lifecycle_controller.py` | Manage the self-build lifecycle |
| **SafetyGuardrails** | `core/safety_guardrails.py` | Enforce all safety constraints |

---

## 3. Data Flow Diagrams

### 3.1 Standard Task Flow

```
User Input
    │
    ▼
PerceptionBundle.build()
    │
    ▼
WorkingMemory.load_session()  ◄── VectorStore.query_relevant()
    │
    ▼
PlanningModule.decompose(goal)
    │ returns ActionPlan
    ▼
ExecutionEngine.run(plan)
    │
    ├── for each ActionNode:
    │       ToolRegistry.call(tool, params)
    │           │
    │           └── Tool executes, returns ToolResult
    │                   │
    │                   ▼
    │               ReflectionLoop.evaluate(result)
    │                   │
    │                   ├── RalphMeter.score(result)
    │                   │       │ score < 60?
    │                   │       └──► retry loop (max 3)
    │                   │
    │                   └── WorkingMemory.update(facts)
    │
    ▼
SessionReport.generate()
    │
    ▼
EpisodeStore.save(episode)
VectorStore.upsert(session_facts)
```

### 3.2 Self-Build Flow

```
Trigger detected (low utility score / repeated failures / user request)
    │
    ▼
SelfBuildController.assess_trigger()
    │ is component in protected list? → reject + log
    │
    ▼
SelfBuildController.create_sbdd(component)
    │
    ▼
CodeGenerationEngine.generate(sbdd)
    │
    ▼
ValidationPipeline.run(candidate)
    │
    ├── SyntaxGate → fail? → retry (max 3) → abandon
    ├── TestGate   → fail? → retry → abandon
    ├── RalphMeterGate → fail? → retry → abandon
    ├── RegressionGate → fail? → retry → abandon
    └── SecurityGate → fail? → retry → abandon
    │
    ▼
IntegrationStep.apply(candidate)
    │ archive old → write new → tag commit
    │
    ▼
Retrospective.write(result)
AuditLog.append(event)
```

### 3.3 Memory Read/Write Flow

```
Session Start
    │
    ├── ShortTermMemory.reset()
    ├── VectorStore.query(session_context) → inject top-K facts
    └── EpisodeStore.load_recent(N) → inject episode summaries

During Session
    │
    ├── ShortTermMemory.append(tool_result | user_message)
    └── ContextWindowManager.compress_if_needed()
            │ LRU eviction of low-priority items
            └── VectorStore.upsert(compressed_item)

Session End
    │
    ├── EpisodeStore.save(episode_record)
    ├── VectorStore.upsert(session_facts)
    └── ShortTermMemory.clear()
```

---

## 4. Runtime Model

CactusRalph-Coder runs as a **single-process, event-driven agent loop**:

```python
# Simplified pseudocode
while session_active:
    event = event_queue.get()           # blocking read

    if event.type == "user_message":
        perception = PerceptionBundle.build(event)
        memory.load(perception)
        plan = planner.decompose(perception.goal)

        for action in plan:
            result = executor.run(action)
            score = ralph_meter.score(result)
            reflection.evaluate(result, score)

            if self_build_controller.should_trigger(result):
                self_build_controller.run()  # blocks until complete

        session_report = reporter.generate()
        event_queue.put(SessionCompleteEvent(session_report))

    elif event.type == "shutdown":
        memory.persist()
        break
```

**Key properties:**
- Single-threaded by default (parallel execution of independent actions is opt-in).
- No background threads during active reasoning — everything is deterministic and auditable.
- I/O is always via the tool interface — Ralph never calls system APIs directly.

---

## 5. Layer Descriptions

### 5.1 Interface Layer

Adapters that translate external signals into `UserMessage` events that the agent loop can process:

| Adapter | Description |
|---|---|
| `interfaces/github_adapter.py` | Receives GitHub issue/PR events via webhooks |
| `interfaces/cli_adapter.py` | Reads from stdin; writes session output to stdout |
| `interfaces/rest_adapter.py` | Exposes a REST API for programmatic integration |
| `interfaces/ide_adapter.py` | Language Server Protocol bridge for IDE plugins |

### 5.2 Agent Core Layer

The brain of Ralph. Stateful during a session; all state is serialised to memory on session end.

Key invariants:
- The execution engine never skips the reflection loop.
- The planning module never produces a plan with cycles.
- The context window manager never evicts `critical`-priority items.

### 5.3 Tool Layer

Stateless functions that interact with the world. Each tool is:

- Idempotent where possible.
- Rate-limited to prevent runaway resource usage.
- Sandboxed — file tools cannot access paths outside the project root.

### 5.4 Memory Layer

Three-tier memory architecture:

| Tier | Latency | Capacity | Persistence |
|---|---|---|---|
| Short-Term | ~0ms | Context window | Session only |
| Long-Term | ~10ms | Unlimited (vector DB) | Permanent |
| Episodic | ~10ms | Unlimited (JSON store) | Permanent |

### 5.5 Scoring Layer

The Ralph Meter runs as a **scoring pipeline**: a chain of independent scorer functions, each responsible for one dimension. Scorers are stateless and can run in parallel.

### 5.6 Self-Build Layer

The self-build layer has its own isolated context. When a self-build runs, it spawns a **child agent session** with:

- A read-only snapshot of the project state.
- No access to the parent session's working memory.
- A restricted tool set (no `delete_file`, no `post_comment`).

This ensures self-builds cannot corrupt the parent session's state.

---

## 6. External Dependencies

| Dependency | Purpose | Version Policy |
|---|---|---|
| Language Model API | Provides the reasoning backbone for Ralph | Pinned; upgrade via self-build |
| Vector Database | Long-term and episodic memory storage | Pinned; upgrade via migration script |
| GitHub API | PR, issue, commit, workflow interactions | Latest stable; use official SDK |
| CodeQL | Security scanning during validation gates | Latest stable via GitHub Actions |
| Language linters | Per-language code quality scoring | Pinned per language in config |

---

## 7. Deployment Topologies

| Topology | Description | Use Case |
|---|---|---|
| **Local** | Single developer machine, CLI mode | Personal use, development |
| **GitHub Actions** | Runs as a GitHub Actions workflow step | Fully automated PR agent |
| **Self-Hosted Server** | Docker container with REST API exposed | Team shared instance |
| **Serverless** | Function-as-a-service, cold-start per request | Low-frequency usage |

The recommended topology for most teams is **GitHub Actions**, which requires no additional infrastructure.

---

*See also: [Ralph](Ralph.md) | [Ralph Meter](Ralph-Meter.md) | [Self-Building Codes](Self-Building-Codes.md)*
