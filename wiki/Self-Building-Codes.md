# Self-Building Codes

**Self-Building Codes** is the subsystem of CactusRalph-Coder that enables Ralph to autonomously write, test, refine, and evolve its own code — including its own tools, helpers, and core reasoning modules. This creates a virtuous cycle: the better Ralph's code, the better Ralph becomes at writing code.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Principles](#2-core-principles)
3. [The Self-Build Lifecycle](#3-the-self-build-lifecycle)
   - 3.1 [Trigger Conditions](#31-trigger-conditions)
   - 3.2 [Scope Determination](#32-scope-determination)
   - 3.3 [Design Phase](#33-design-phase)
   - 3.4 [Generation Phase](#34-generation-phase)
   - 3.5 [Validation Phase](#35-validation-phase)
   - 3.6 [Integration Phase](#36-integration-phase)
   - 3.7 [Retrospective](#37-retrospective)
4. [Code Generation Engine](#4-code-generation-engine)
   - 4.1 [Prompt Construction](#41-prompt-construction)
   - 4.2 [Generation Strategies](#42-generation-strategies)
   - 4.3 [Multi-Pass Refinement](#43-multi-pass-refinement)
5. [Self-Modifiable Components](#5-self-modifiable-components)
   - 5.1 [Tool Wrappers](#51-tool-wrappers)
   - 5.2 [Reasoning Helpers](#52-reasoning-helpers)
   - 5.3 [Scoring Adapters](#53-scoring-adapters)
   - 5.4 [Memory Backends](#54-memory-backends)
   - 5.5 [Prompt Templates](#55-prompt-templates)
6. [Protected Components](#6-protected-components)
7. [Validation Gates](#7-validation-gates)
   - 7.1 [Syntax Gate](#71-syntax-gate)
   - 7.2 [Test Gate](#72-test-gate)
   - 7.3 [Ralph Meter Gate](#73-ralph-meter-gate)
   - 7.4 [Regression Gate](#74-regression-gate)
   - 7.5 [Security Gate](#75-security-gate)
8. [Evolutionary Strategies](#8-evolutionary-strategies)
   - 8.1 [Mutation](#81-mutation)
   - 8.2 [Crossover](#82-crossover)
   - 8.3 [Selection](#83-selection)
9. [Version Control and Rollback](#9-version-control-and-rollback)
10. [Bootstrapping](#10-bootstrapping)
11. [Safety Constraints](#11-safety-constraints)
12. [Observability and Audit Logs](#12-observability-and-audit-logs)
13. [Example: Ralph Improves Its Own Parser](#13-example-ralph-improves-its-own-parser)

---

## 1. Overview

Self-Building Codes is what distinguishes CactusRalph-Coder from a simple code generation tool. Rather than being a static system that applies fixed algorithms, Ralph can:

- **Detect limitations** in its own tooling.
- **Draft improved implementations** of those tools.
- **Test the new implementation** against the existing test suite and extended test cases.
- **Replace the old implementation** only when the new one demonstrably scores higher on the Ralph Meter.
- **Commit the change** with full documentation and a changelog entry.

This capability is bounded by strict safety constraints to ensure Ralph cannot accidentally lobotomise itself or introduce instability.

---

## 2. Core Principles

| Principle | Description |
|---|---|
| **Conservative by default** | Self-modification is an opt-in capability; it never happens implicitly |
| **Test before replace** | Old code is never removed until new code has passed all validation gates |
| **Atomic replacement** | A component is either fully replaced or not touched at all — no partial upgrades |
| **Always reversible** | Every self-build operation creates a tagged git commit so it can be reverted |
| **Score must improve** | A self-build that produces the same or lower Ralph Meter score is rejected |
| **Human visibility** | Every self-build is surfaced in the PR description and session report |

---

## 3. The Self-Build Lifecycle

### 3.1 Trigger Conditions

A self-build is triggered when one or more of the following conditions are met:

| Trigger | Description |
|---|---|
| **Low utility score** | A tool consistently returns low-quality results (utility score < 60 over 10+ calls) |
| **Repeated failures** | A tool fails more than 3 times in a session due to bugs in the tool itself |
| **Explicit user request** | The user asks Ralph to improve a specific part of its tooling |
| **Scheduled review** | A weekly automated review identifies components that are below current best practice |
| **New capability unlocked** | A new external library or API becomes available that would improve an existing tool |

Self-builds are **never** triggered by Ralph on a whim. Each trigger is logged with a reason code and a link to the evidence that justified the trigger.

### 3.2 Scope Determination

Once a trigger fires, Ralph determines the **minimum viable scope** for the self-build:

1. Identify the specific component (function, class, module, or tool) that is underperforming.
2. Map its dependencies and dependents.
3. Define the self-build boundary: only the identified component and any helpers it directly owns.
4. Verify that the component is in the [Self-Modifiable Components](#5-self-modifiable-components) list and not in [Protected Components](#6-protected-components).

### 3.3 Design Phase

Ralph produces a **Self-Build Design Document (SBDD)** before writing any code:

```markdown
## Self-Build Design Document

Component:      src/tools/file_reader.py
Trigger:        Repeated failures (4 in last session, reason: encoding detection bug)
Current score:  Correctness 48/100 | Code Quality 62/100
Target score:   Correctness ≥ 80/100 | Code Quality ≥ 70/100

Proposed Change:
  Replace the ad-hoc encoding detection loop with the `chardet` library.
  Add a fallback encoding list: [utf-8, latin-1, cp1252].
  Add test cases for non-UTF-8 files.

Impact Analysis:
  - Dependents: 3 other tools call file_reader.read()
  - Breaking changes: None (same function signature)
  - Risk: Low

Rollback Plan:
  git revert <commit-sha> — restores previous implementation in < 60s
```

The SBDD is committed to `self_builds/YYYY-MM-DD_<component>.md` before any code is changed.

### 3.4 Generation Phase

Ralph generates the new implementation using the [Code Generation Engine](#4-code-generation-engine). Key constraints applied during generation:

- The new implementation **must** have the same public API (function signatures, return types).
- All existing tests **must** continue to pass.
- The new implementation **must** include its own new tests for the improvements it makes.

### 3.5 Validation Phase

Every generated implementation passes through the [Validation Gates](#7-validation-gates) in order. If any gate fails, generation is re-attempted up to 3 times with an adjusted prompt. If all retries fail, the self-build is abandoned and the failure is logged.

### 3.6 Integration Phase

Once all validation gates pass:

1. The old implementation is moved to `archive/<component>_<timestamp>.py` (not deleted).
2. The new implementation is written to the canonical path.
3. All dependents are re-run to verify no regressions.
4. The SBDD is updated with the final scores.
5. A git commit is created with the message: `self-build: improve <component> (<old_score>→<new_score>)`.

### 3.7 Retrospective

After integration, Ralph writes a **Self-Build Retrospective** entry in `self_builds/retrospectives.md`:

- Was the trigger valid? Did the change actually fix the problem?
- Did the score improve as predicted?
- What lessons were learned that should influence future self-builds?

---

## 4. Code Generation Engine

### 4.1 Prompt Construction

The code generation prompt is assembled from:

1. **Component specification** — the public API that must be preserved.
2. **Current implementation** — the code being replaced, with inline annotations marking known problems.
3. **Failing tests** — test cases that the current implementation fails.
4. **Target metrics** — the minimum Ralph Meter scores required to pass.
5. **Constraints** — language version, dependencies allowed, style guide.
6. **Examples** — similar, high-scoring components from the codebase as positive examples.

### 4.2 Generation Strategies

Ralph can use three generation strategies depending on the nature of the change:

| Strategy | When to Use | Description |
|---|---|---|
| **Rewrite** | Fundamental design flaws | Generate an entirely new implementation from scratch |
| **Patch** | Localised bugs or sub-optimal sections | Surgically replace specific lines or blocks |
| **Augment** | Missing functionality | Add new code without modifying existing logic |

The strategy is selected during the Design Phase and recorded in the SBDD.

### 4.3 Multi-Pass Refinement

Generated code is refined in up to three passes:

| Pass | Focus | Tool Used |
|---|---|---|
| Pass 1 | Correctness | Run tests, fix test failures |
| Pass 2 | Quality | Run linter, apply suggestions |
| Pass 3 | Readability | Review docstrings, naming, comments |

Each pass re-scores the component on the relevant Ralph Meter dimensions. Refinement stops early if all target scores are met.

---

## 5. Self-Modifiable Components

The following component types are eligible for self-modification:

### 5.1 Tool Wrappers

Tool wrappers are thin adapters between Ralph's core and external tools (file system, shell, web). They are the most commonly self-modified components because they interact with external systems that change frequently.

**Examples:**
- `tools/file_reader.py` — reads files with encoding detection
- `tools/shell_runner.py` — executes shell commands safely
- `tools/search_client.py` — queries search APIs

**Self-build triggers:** Changed external API, new encoding edge cases, performance bottlenecks.

### 5.2 Reasoning Helpers

Utility functions used by the planning and reflection modules.

**Examples:**
- `reasoning/goal_decomposer.py` — breaks goals into sub-tasks
- `reasoning/plan_validator.py` — checks a plan for logical inconsistencies
- `reasoning/summariser.py` — compresses working memory

**Self-build triggers:** Poor goal decomposition detected across multiple sessions, planning failures.

### 5.3 Scoring Adapters

Language-specific or framework-specific adapters for the Ralph Meter.

**Examples:**
- `scoring/python_linter_adapter.py` — interprets Pylint output
- `scoring/js_coverage_adapter.py` — interprets Istanbul/NYC coverage reports
- `scoring/security_scanner_adapter.py` — interprets CodeQL SARIF output

**Self-build triggers:** New linter version changes output format, new security rules added.

### 5.4 Memory Backends

Adapters for different storage systems used by Ralph's memory subsystems.

**Examples:**
- `memory/vector_store_client.py` — interface to the vector database
- `memory/episode_serialiser.py` — serialises episodic memory to JSON

**Self-build triggers:** Schema changes, performance issues with large memory stores.

### 5.5 Prompt Templates

Jinja2 templates used to construct prompts for each major operation.

**Examples:**
- `prompts/code_generation.jinja2`
- `prompts/code_review.jinja2`
- `prompts/goal_decomposition.jinja2`

**Self-build triggers:** Low output quality consistently traced to a specific prompt template.

---

## 6. Protected Components

The following components are **permanently off-limits** for self-modification:

| Component | Reason |
|---|---|
| `core/safety_guardrails.py` | Prevents Ralph from disabling its own safety checks |
| `core/tool_interface.py` | Core tool contract must be stable |
| `core/memory_manager.py` | Memory corruption risk is too high |
| `ralph_meter/scorer.py` | Ralph must not be able to inflate its own scores |
| `self_builds/lifecycle_controller.py` | Self-builds must not rewrite their own controller |
| `.github/` directory | CI/CD pipelines are under human control only |

Attempts to target a protected component are silently rejected. The rejection is logged but not surfaced as an error to the user.

---

## 7. Validation Gates

Every generated implementation must pass all five gates in order. A failure at any gate stops the pipeline for that attempt.

### 7.1 Syntax Gate

- Parse the generated code with the language's official parser.
- Verify all imports resolve.
- Verify all type annotations are valid (where applicable).

**Pass condition:** Zero syntax errors.

### 7.2 Test Gate

- Run the existing test suite for the component.
- Run any new tests added by Ralph for this self-build.

**Pass condition:** All existing tests pass; all new tests pass.

### 7.3 Ralph Meter Gate

- Score the generated implementation across all relevant dimensions.
- Compare scores to the target metrics defined in the SBDD.

**Pass condition:** All target dimension scores are met or exceeded.

### 7.4 Regression Gate

- Run the full project test suite (not just tests for the changed component).
- Run all tools that depend on the changed component and verify their outputs.

**Pass condition:** Zero new test failures compared to the baseline run.

### 7.5 Security Gate

- Scan the generated code for secrets.
- Run a SAST tool on the generated code.
- Verify no new security vulnerabilities are introduced.

**Pass condition:** Zero new security findings. Security score ≥ 90/100.

---

## 8. Evolutionary Strategies

For components where simple rewriting is not effective, Ralph uses evolutionary computation strategies inspired by genetic algorithms.

### 8.1 Mutation

Ralph generates N variants of the component by applying targeted mutations:

- Substitute one algorithm for another (e.g., linear search → binary search).
- Replace a data structure (e.g., list → set for O(1) lookups).
- Reorder operations to minimise redundant work.
- Introduce memoisation or caching.

Each variant is independently scored. The highest-scoring variant that passes all gates is selected.

### 8.2 Crossover

When two partial implementations each solve a different aspect of the problem well, Ralph combines them:

1. Identify which sections of implementation A score well on dimension X.
2. Identify which sections of implementation B score well on dimension Y.
3. Produce a hybrid that combines the best sections of both.

### 8.3 Selection

After generating and scoring a population of variants, Ralph applies **tournament selection**:

1. Randomly pick 3 variants.
2. Select the highest scorer of the 3.
3. Repeat until a final candidate is selected.
4. Run the full validation pipeline on the final candidate.

---

## 9. Version Control and Rollback

Every self-build produces a **tagged git commit**:

```
self-build/tools/file_reader/v2.1.0
```

The tag format is: `self-build/<component-path>/<new-version>`.

**Rollback procedure:**

```bash
# List self-build tags for a component
git tag -l "self-build/tools/file_reader/*"

# Revert to a previous version
git revert self-build/tools/file_reader/v2.1.0

# Or hard reset to a known-good tag (use with caution)
git checkout self-build/tools/file_reader/v2.0.0 -- src/tools/file_reader.py
```

Rollbacks are always logged and trigger a post-mortem entry in `self_builds/retrospectives.md`.

---

## 10. Bootstrapping

The Self-Building Codes engine itself is minimal at first start. It bootstraps through three stages:

| Stage | Description |
|---|---|
| **Stage 0: Seed** | Minimal hand-written implementations of all self-modifiable components |
| **Stage 1: First Self-Build** | Ralph runs its first self-build on the lowest-scoring Stage 0 component |
| **Stage 2: Continuous Improvement** | The system enters steady-state; self-builds run automatically on trigger |

The seed implementations are stored in `self_builds/seed/` and are never modified. They serve as a stable reference point for rollback if the system reaches an unrecoverable state.

---

## 11. Safety Constraints

The following hard constraints are always enforced, overriding all other logic:

1. **No recursive self-builds** — a self-build cannot trigger another self-build during the same session.
2. **One component at a time** — no concurrent self-builds.
3. **Human confirmation required for core changes** — any self-build targeting a component with more than 10 dependents requires explicit user approval.
4. **Score must improve by at least 5 points** — a self-build that only improves the score by 1–4 points is rejected (the risk isn't worth it).
5. **Daily rate limit** — no more than 5 self-builds per day per project (prevents runaway modification loops).
6. **Context isolation** — the code generation model used during a self-build does not have access to the live production memory store, only a read-only snapshot.

---

## 12. Observability and Audit Logs

All self-build activity is recorded in structured logs:

```json
{
  "timestamp": "2026-03-28T08:01:56Z",
  "trigger": "repeated_failures",
  "component": "src/tools/file_reader.py",
  "strategy": "rewrite",
  "attempts": 2,
  "gates_passed": ["syntax", "test", "ralph_meter", "regression", "security"],
  "score_before": { "correctness": 48, "code_quality": 62, "overall": 61 },
  "score_after":  { "correctness": 89, "code_quality": 78, "overall": 82 },
  "commit_sha": "a3f7c2d",
  "tag": "self-build/src/tools/file_reader/v2.1.0",
  "duration_seconds": 142
}
```

Logs are stored in `self_builds/audit_log.jsonl` (newline-delimited JSON). The file is append-only and is never overwritten by Ralph.

---

## 13. Example: Ralph Improves Its Own Parser

Here is a concrete walkthrough of a self-build event:

**Situation:** Ralph notices that `reasoning/goal_decomposer.py` consistently produces overly granular sub-tasks for simple requests, causing 2× more actions than necessary.

**Trigger:** Low efficiency score (Efficiency: 44/100) across 8 sessions.

**SBDD summary:**
- Component: `reasoning/goal_decomposer.py`
- Strategy: Patch (only the granularity heuristic needs changing)
- Change: Introduce a complexity estimator that produces fewer sub-tasks for simple one-liner goals

**Generation:** Ralph generates a patched version using the Patch strategy.

**Validation:**
- ✅ Syntax Gate: passes
- ✅ Test Gate: 47/47 existing tests pass; 5 new tests added and pass
- ✅ Ralph Meter Gate: Efficiency 44→79; Correctness unchanged at 91
- ✅ Regression Gate: full suite passes
- ✅ Security Gate: no new findings

**Integration:** Component replaced. Commit tagged `self-build/reasoning/goal_decomposer/v1.3.0`.

**Outcome:** Average session action count drops from 24 to 13 for simple tasks. Overall Efficiency dimension improves from 44 to 79.

---

*See also: [Ralph](Ralph.md) | [Ralph Meter](Ralph-Meter.md) | [Architecture](Architecture.md)*
