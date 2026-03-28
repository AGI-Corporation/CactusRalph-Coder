# Ralph Meter

The **Ralph Meter** is CactusRalph-Coder's multi-dimensional quality scoring and feedback system. Every action Ralph takes — from writing a function to opening a pull request — is graded across a set of weighted dimensions. The aggregate score drives Ralph's internal improvement loop and provides humans with a transparent, auditable measure of Ralph's performance.

---

## Table of Contents

1. [Purpose and Design Goals](#1-purpose-and-design-goals)
2. [Scoring Dimensions](#2-scoring-dimensions)
   - 2.1 [Correctness](#21-correctness)
   - 2.2 [Completeness](#22-completeness)
   - 2.3 [Code Quality](#23-code-quality)
   - 2.4 [Security](#24-security)
   - 2.5 [Performance](#25-performance)
   - 2.6 [Readability](#26-readability)
   - 2.7 [Test Coverage](#27-test-coverage)
   - 2.8 [Efficiency](#28-efficiency)
3. [Score Computation](#3-score-computation)
   - 3.1 [Raw Score Formula](#31-raw-score-formula)
   - 3.2 [Weighted Aggregate](#32-weighted-aggregate)
   - 3.3 [Penalty Modifiers](#33-penalty-modifiers)
4. [Score Thresholds and Bands](#4-score-thresholds-and-bands)
5. [Score Lifecycle](#5-score-lifecycle)
   - 5.1 [Pre-Action Estimate](#51-pre-action-estimate)
   - 5.2 [Post-Action Measurement](#52-post-action-measurement)
   - 5.3 [Session Aggregate](#53-session-aggregate)
   - 5.4 [Historical Trend](#54-historical-trend)
6. [Score-Driven Iteration](#6-score-driven-iteration)
7. [Feedback Reports](#7-feedback-reports)
   - 7.1 [Action-Level Report](#71-action-level-report)
   - 7.2 [Session-Level Report](#72-session-level-report)
   - 7.3 [Project-Level Dashboard](#73-project-level-dashboard)
8. [Calibration and Tuning](#8-calibration-and-tuning)
9. [Dimension Weights Reference Table](#9-dimension-weights-reference-table)
10. [Extending the Ralph Meter](#10-extending-the-ralph-meter)

---

## 1. Purpose and Design Goals

The Ralph Meter was designed with four goals:

| Goal | Description |
|---|---|
| **Transparency** | Every score is explainable — no black-box judgements |
| **Actionability** | Scores point to specific things Ralph can improve |
| **Consistency** | The same code always produces the same score, given the same rubric |
| **Evolvability** | New dimensions can be added without invalidating historical scores |

The Ralph Meter is **not** a subjective opinion of Ralph's output. It is a structured rubric applied programmatically, much like a CI pipeline produces a pass/fail result.

---

## 2. Scoring Dimensions

Each dimension is scored independently on a scale of **0 to 100**.

### 2.1 Correctness

**What it measures:** Does the output actually solve the problem?

| Sub-dimension | Weight |
|---|---|
| Tests pass | 40% |
| Functional requirements met | 40% |
| Edge cases handled | 20% |

Correctness is the **highest-weighted dimension overall**. An output with perfect style but broken functionality cannot score well.

**Measurement methods:**
- Run the project's test suite; count pass/fail/error.
- Run static analysis tools (type checkers, linters) for correctness-class errors.
- Compare against a requirements checklist derived from the user's prompt.

### 2.2 Completeness

**What it measures:** Did Ralph do everything asked?

| Sub-dimension | Weight |
|---|---|
| All requested features implemented | 50% |
| No unresolved TODOs or placeholders left | 30% |
| All files affected are updated (e.g., README, tests) | 20% |

**Measurement methods:**
- Parse the user's prompt into a feature checklist using an NLP extractor.
- Grep the codebase for `TODO`, `FIXME`, `HACK`, `PLACEHOLDER`.
- Verify that test files and documentation were updated alongside code changes.

### 2.3 Code Quality

**What it measures:** Is the code well-structured and maintainable?

| Sub-dimension | Weight |
|---|---|
| Linter violations | 30% |
| Cyclomatic complexity | 25% |
| Code duplication | 20% |
| Naming conventions | 15% |
| Module cohesion | 10% |

**Measurement methods:**
- Run language-specific linters (ESLint, Pylint, Clippy, etc.).
- Compute cyclomatic complexity using static analysis.
- Use AST diffing to detect duplicated logic blocks.

### 2.4 Security

**What it measures:** Does the output introduce security vulnerabilities?

| Sub-dimension | Weight |
|---|---|
| No secrets committed | 35% |
| No known vulnerable dependencies | 30% |
| No OWASP Top-10 class vulnerabilities | 25% |
| No unsafe shell constructs | 10% |

**Measurement methods:**
- Scan all changed files for credential patterns (API keys, tokens, passwords).
- Query the GitHub Advisory Database for vulnerable dependencies.
- Run a SAST tool (CodeQL or equivalent) on changed code.

Security has a **hard floor**: any output with a Security score below 50 cannot receive a passing overall score, regardless of other dimensions.

### 2.5 Performance

**What it measures:** Is the code efficient enough for its intended use?

| Sub-dimension | Weight |
|---|---|
| Algorithmic complexity appropriate | 40% |
| No obvious N+1 or redundant I/O | 35% |
| Memory usage reasonable | 25% |

**Measurement methods:**
- Static analysis for common performance anti-patterns (nested loops over large datasets, synchronous I/O in hot paths, etc.).
- Where benchmarks exist, run them and compare against baseline.

### 2.6 Readability

**What it measures:** Can a human understand and maintain the code?

| Sub-dimension | Weight |
|---|---|
| Functions and variables have clear names | 30% |
| Functions are appropriately short | 25% |
| Comments explain *why*, not *what* | 20% |
| Public API has docstrings | 15% |
| Consistent formatting | 10% |

**Measurement methods:**
- Measure average function length.
- Check that exported symbols have docstrings.
- Run a formatter (Prettier, Black, gofmt, etc.) and measure the diff size.

### 2.7 Test Coverage

**What it measures:** Is the new code adequately tested?

| Sub-dimension | Weight |
|---|---|
| Line coverage of new code | 40% |
| Branch coverage of new code | 35% |
| Tests cover edge cases | 25% |

**Measurement methods:**
- Run the test suite with coverage instrumentation.
- Parse the coverage report for lines/branches touched by new code only.
- Check for tests that probe boundary conditions (empty input, max values, error paths).

### 2.8 Efficiency

**What it measures:** Did Ralph accomplish the task in a lean, focused way?

| Sub-dimension | Weight |
|---|---|
| Minimal token usage for the result achieved | 40% |
| No unnecessary tool calls | 35% |
| Session completed within expected iteration count | 25% |

Efficiency is an **agent-level** dimension (not a code quality dimension). It scores Ralph's own process, not just its output.

---

## 3. Score Computation

### 3.1 Raw Score Formula

Each sub-dimension is scored 0–100. The dimension score is the weighted average of its sub-dimensions:

```
dimension_score = Σ (sub_score_i × sub_weight_i)
```

### 3.2 Weighted Aggregate

The overall Ralph Meter score is the weighted average across all eight dimensions:

```
ralph_meter_score = Σ (dimension_score_i × dimension_weight_i)
```

Default dimension weights (see [Section 9](#9-dimension-weights-reference-table) for the full table):

| Dimension | Default Weight |
|---|---|
| Correctness | 25% |
| Security | 20% |
| Completeness | 15% |
| Code Quality | 12% |
| Test Coverage | 12% |
| Readability | 8% |
| Performance | 5% |
| Efficiency | 3% |

### 3.3 Penalty Modifiers

Certain events apply multiplicative penalties to the final score:

| Event | Penalty Multiplier |
|---|---|
| Secret committed (caught, reverted) | × 0.70 |
| Secret committed (not caught) | × 0.00 (score zeroed) |
| Unrecoverable error triggered | × 0.85 |
| Constraint violated | × 0.90 |
| User had to manually correct an error | × 0.80 |

Penalties stack multiplicatively: two penalties of × 0.90 result in × 0.81.

---

## 4. Score Thresholds and Bands

| Band | Score Range | Meaning |
|---|---|---|
| 🟢 Excellent | 90 – 100 | Exceptional work; ship it |
| 🟡 Good | 75 – 89 | Solid work; minor improvements possible |
| 🟠 Acceptable | 60 – 74 | Meets minimum bar; iterate before shipping |
| 🔴 Poor | 40 – 59 | Significant issues; must iterate |
| ⛔ Failing | 0 – 39 | Fundamental problems; discard and restart |

Ralph will not move to the next task in the plan if the current task scores below **Acceptable (60)**. It will instead enter the [Score-Driven Iteration](#6-score-driven-iteration) loop.

---

## 5. Score Lifecycle

### 5.1 Pre-Action Estimate

Before executing an action, Ralph estimates the expected Ralph Meter score delta. This estimate is used in the [Decision-Making Model](Ralph.md#6-decision-making-model) to pick the best action.

### 5.2 Post-Action Measurement

After every action, the Ralph Meter evaluates the relevant dimensions and produces an **action score**. This score is recorded in the session log.

### 5.3 Session Aggregate

At the end of a session, the Ralph Meter averages all action scores (weighted by action complexity) into a **session score**. The session score is attached to the PR description and any progress report.

### 5.4 Historical Trend

Over multiple sessions, the Ralph Meter maintains a **rolling average score** for the project. A declining trend triggers a warning flag that is surfaced in the [Project-Level Dashboard](#73-project-level-dashboard).

---

## 6. Score-Driven Iteration

When an action score falls below 60, Ralph enters a structured iteration loop:

```
1. DIAGNOSE   — Which dimensions are below threshold? What specific sub-dimensions failed?
2. HYPOTHESIZE — What change would most improve the score?
3. ACT        — Apply the change.
4. MEASURE    — Re-score.
5. COMPARE    — Is the new score higher? By how much?
6. REPEAT     — Continue until score ≥ 60, or max iterations reached.
```

**Maximum iterations per action:** 3 (configurable; see [Configuration](Configuration.md)).

If the score is still below 60 after max iterations, Ralph:
1. Documents the unresolved issue.
2. Flags the action as `partial`.
3. Continues to the next action in the plan.
4. Includes a summary of the unresolved issue in the final session report.

---

## 7. Feedback Reports

### 7.1 Action-Level Report

Generated after each action. Format:

```
Action: write_file(src/utils/parser.py)
─────────────────────────────────────
Correctness:    88/100  ██████████▋░
Completeness:   95/100  ███████████▊░
Code Quality:   72/100  ████████▌░░░
Security:       100/100 ████████████
Performance:    80/100  █████████▌░░
Readability:    85/100  ██████████▏░
Test Coverage:  60/100  ███████▎░░░░
Efficiency:     91/100  ██████████▉░
─────────────────────────────────────
OVERALL:        84/100  🟡 Good

Top issues:
  ⚠ Code Quality: cyclomatic complexity of `parse_block()` is 14 (threshold: 10)
  ⚠ Test Coverage: branch coverage for new code is 58% (threshold: 70%)
```

### 7.2 Session-Level Report

Generated at the end of a session. Includes:
- Per-action scores table.
- Session aggregate score.
- Top 3 strengths.
- Top 3 areas for improvement.
- Comparison to the previous session score.

### 7.3 Project-Level Dashboard

A summary view aggregated across all sessions for a repository. Includes:
- Rolling 30-day average Ralph Meter score.
- Score trend chart (as ASCII sparkline in text mode).
- Dimension breakdown heat map.
- Most frequently failing sub-dimensions.

---

## 8. Calibration and Tuning

The Ralph Meter is calibrated against a **golden dataset** — a collection of 500 manually-reviewed coding tasks with ground-truth quality labels.

The golden dataset is stored at `ralph_meter/calibration/golden_dataset.jsonl` (newline-delimited JSON). Each record has the shape:

```json
{
  "task_id": "gd-0001",
  "description": "Write a Python function to parse ISO 8601 timestamps",
  "language": "python",
  "human_quality_label": 82,
  "human_reviewer": "reviewer_a",
  "reviewed_at": "2025-11-14T10:22:00Z"
}
```

To contribute tasks to the golden dataset, open a pull request that appends records to `golden_dataset.jsonl` and includes the reviewed code sample in `ralph_meter/calibration/samples/gd-<id>/`. The dataset maintainers will assign human quality labels before merging.

Calibration is re-run whenever:

- A new scoring dimension is added.
- Dimension weights are modified.
- The underlying language models are updated.

Calibration output is stored in `ralph_meter_calibration.json` and includes:
- Correlation between Ralph Meter scores and human quality labels.
- Precision/recall for the Acceptable threshold.
- Bias analysis by programming language and task type.

---

## 9. Dimension Weights Reference Table

| Dimension | Default Weight | Min | Max | Adjustable? |
|---|---|---|---|---|
| Correctness | 25% | 15% | 40% | Yes |
| Security | 20% | 15% | 30% | No (security is non-negotiable) |
| Completeness | 15% | 5% | 25% | Yes |
| Code Quality | 12% | 5% | 20% | Yes |
| Test Coverage | 12% | 5% | 20% | Yes |
| Readability | 8% | 2% | 15% | Yes |
| Performance | 5% | 1% | 15% | Yes |
| Efficiency | 3% | 1% | 10% | Yes |

Weights must always sum to 100%. Adjusting weights that are not in their default range requires a configuration file change (see [Configuration](Configuration.md)).

---

## 10. Extending the Ralph Meter

To add a new scoring dimension:

1. **Define the dimension** — name, description, sub-dimensions, and measurement methods.
2. **Implement a scorer** — a function `score_<dimension>(context: ScoringContext) -> DimensionScore`.
3. **Register the scorer** — add it to `ralph_meter_config.json` with an initial weight of 0%.
4. **Calibrate** — run the calibration suite and adjust the weight to find a good balance.
5. **Document** — add a section to this wiki page.
6. **Announce** — note the new dimension in `CHANGELOG.md`.

New dimensions start with a weight of 0% so they don't affect existing scores until calibrated. Gradually increase the weight over multiple releases.

---

*See also: [Ralph](Ralph.md) | [Self-Building Codes](Self-Building-Codes.md) | [Architecture](Architecture.md)*
