# Glossary

Definitions for all terms, acronyms, and concepts used in the CactusRalph-Coder wiki.

---

## A

**Action** — A discrete step in an execution plan. Each action calls a single tool with specific parameters. Actions have a `status` (`pending | in_progress | done | failed | skipped`) and are scored by the Ralph Meter after completion.

**Action Node** — The data structure representing a single action in the execution plan. Fields include: `id`, `tool_name`, `params`, `status`, `result`, `score`, `retry_count`.

**Action Plan** — An ordered list of Action Nodes produced by the Planning Module for a given goal. The plan may be updated mid-session as new facts are discovered.

**Action Score** — The Ralph Meter score for a single action, computed immediately after the action completes.

**Augment (generation strategy)** — A Self-Building Codes strategy that adds new functionality to an existing component without modifying any of its existing logic.

**Autonomous Mode** — An interaction mode in which Ralph executes the full action plan without pausing for user confirmation, except for destructive actions, constraint violations, and unrecoverable errors.

---

## B

**Band** — A named score range on the Ralph Meter (Excellent, Good, Acceptable, Poor, Failing). Each band has a specific minimum score and a visual indicator.

**Bootstrapping** — The three-stage process by which the Self-Building Codes engine initialises: Seed (hand-written components), First Self-Build (initial improvement), and Continuous Improvement (steady state).

**Branch Coverage** — A test coverage metric that measures the percentage of code branches (if/else, switch cases, loops) exercised by the test suite.

---

## C

**Calibration** — The process of measuring and adjusting Ralph Meter scoring weights against a golden dataset of manually-reviewed tasks, to ensure that scores reflect real quality.

**Child Agent Session** — An isolated agent session spawned by the Self-Build Layer during a self-build. The child session has read-only access to the parent's project state and cannot modify working memory.

**Compression** — The process by which the Context Window Manager summarises lower-priority items in working memory to free space when the context window is near capacity.

**Constraint** — A restriction applied to Ralph's behaviour during a session (e.g., "do not modify `main.py`", "use Python 3.11+"). Constraints are stated in the user's prompt and stored in Working Memory.

**Context Window** — The finite amount of text (measured in tokens) that a language model can process in a single call. CactusRalph-Coder uses the Context Window Manager to work within this limit.

**Context Window Manager (CWM)** — The component responsible for monitoring, compressing, archiving, and re-injecting items in working memory to stay within the context window limit.

**Crossover (evolutionary strategy)** — A Self-Building Codes strategy that combines the best sections of two partial implementations into a single hybrid candidate.

**Cyclomatic Complexity** — A measure of the number of independent paths through a function. Lower is simpler. The default threshold in Ralph Meter's Code Quality dimension is 10.

---

## D

**Decision-Making Model** — Ralph's cost-benefit scoring formula for choosing between multiple possible actions. Balances expected value, confidence, risk penalty, and token cost.

**Dependency Ordering** — The step in the Planning Module that arranges sub-tasks so that each sub-task's prerequisites are completed before it begins.

**Destructive Action** — A tool call rated as potentially irreversible (e.g., `delete_file`). Destructive actions require explicit user confirmation in Interactive Mode.

**Dimension** — One of eight scoring categories in the Ralph Meter: Correctness, Completeness, Code Quality, Security, Performance, Readability, Test Coverage, and Efficiency.

---

## E

**Efficiency (dimension)** — A Ralph Meter dimension that scores Ralph's own process efficiency: token usage, number of tool calls, and session iteration count.

**Episode** — A record of a single agent session stored in Episodic Memory. Contains: session ID, timestamp, goal, action summary, outcome, and lessons learned.

**Episodic Memory** — A persistent store of session episode records, enabling Ralph to recall and learn from past sessions.

**Execution Engine** — The core component that iterates over an action plan, calls tools, and passes results to the Reflection Loop.

---

## F

**Failing (band)** — The lowest Ralph Meter score band (0–39). A failing score indicates fundamental problems that require discarding the output and restarting.

**Fallback Encoding List** — A list of character encodings tried in order when a file's encoding cannot be auto-detected (e.g., `[utf-8, latin-1, cp1252]`).

**Feedback Report** — A structured document produced by the Ralph Meter at the action, session, or project level, summarising scores and actionable improvement suggestions.

---

## G

**Goal Decomposition** — The process of breaking a high-level user goal into an ordered list of atomic, actionable sub-tasks. Performed by the Planning Module.

**Golden Dataset** — A curated collection of 500 manually-reviewed coding tasks with ground-truth quality labels, used to calibrate the Ralph Meter.

**Guardrail** — A hard safety constraint enforced unconditionally by Ralph, regardless of user instructions (e.g., never commit secrets, never push to protected branches).

---

## H

**Hard Floor** — A minimum score on a single dimension below which the overall Ralph Meter score automatically fails, regardless of other dimension scores. Security has a hard floor of 50.

**Historical Trend** — The rolling average of Ralph Meter session scores over time for a project, used to detect declining quality.

---

## I

**Integration Phase** — The step in the Self-Build Lifecycle where a validated new implementation is written to the canonical path, the old implementation is archived, and a git commit is created.

**Interactive Mode** — An interaction mode in which Ralph pauses after each major action to present a summary and ask the user to confirm, redirect, or stop.

---

## L

**Line Coverage** — A test coverage metric that measures the percentage of source code lines executed by the test suite.

**Long-Term Memory** — A persistent vector database that stores project facts, user preferences, and compressed episode summaries across sessions.

---

## M

**Maximum Iterations** — The configurable limit on how many times Ralph will retry an action before marking it as `partial` and moving on (default: 3).

**Memory Manager** — The component that coordinates Short-Term, Long-Term, and Episodic Memory, handling reads, writes, compression, and archiving.

**Micro-Reflection** — A fast evaluation step performed after each individual action: validate output, assert facts, score with Ralph Meter, and adapt the plan.

**Mutation (evolutionary strategy)** — A Self-Building Codes strategy that generates multiple variants of a component by applying targeted modifications (algorithm substitution, data structure change, etc.).

---

## O

**OODA Loop** — Observe → Orient → Decide → Act. A decision-making framework adapted for Ralph's internal monologue at each reasoning step.

---

## P

**Patch (generation strategy)** — A Self-Building Codes strategy that surgically replaces specific lines or blocks in an existing component, leaving the rest unchanged.

**Penalty Modifier** — A multiplicative factor applied to the Ralph Meter final score when specific events occur (e.g., secret committed, user had to manually correct an error).

**PerceptionBundle** — The normalised data structure produced by the Perception Layer from all incoming inputs (user prompt, repository snapshot, tool outputs, session history).

**Planning Module** — The component that converts the current goal and observed facts into an ordered, dependency-resolved action plan.

**Protected Component** — A component that is permanently excluded from self-modification (e.g., `core/safety_guardrails.py`, `ralph_meter/scorer.py`).

---

## R

**Ralph** — The core autonomous coding agent of CactusRalph-Coder. Ralph plans, executes, scores, and self-improves within bounded safety constraints.

**Ralph Meter** — The multi-dimensional quality scoring and feedback system that evaluates every action Ralph takes across eight dimensions.

**Ralph Meter Gate** — A validation gate in the Self-Build Pipeline that checks whether a generated implementation meets the minimum Ralph Meter dimension scores specified in the SBDD.

**Reflection Loop** — The component that evaluates each action result, scores it with the Ralph Meter, updates working memory, and adapts the action plan.

**Regression Gate** — A validation gate in the Self-Build Pipeline that runs the full project test suite to verify that a new implementation introduces no new test failures.

**Rewrite (generation strategy)** — A Self-Building Codes strategy that generates an entirely new implementation from scratch, used when the current implementation has fundamental design flaws.

**Rolling Average** — The average Ralph Meter session score computed over the most recent N sessions (default: 30) for a project.

---

## S

**SAST (Static Application Security Testing)** — Automated security analysis performed on source code without executing it. Used in the Security Gate and Ralph Meter's Security dimension.

**SBDD (Self-Build Design Document)** — A markdown document Ralph creates before beginning a self-build, specifying the component, trigger, proposed change, impact analysis, and rollback plan.

**Score-Driven Iteration** — The loop Ralph enters when an action score falls below the Acceptable threshold, in which it diagnoses, hypothesises, acts, and measures until the score improves or max iterations are reached.

**Security (dimension)** — A Ralph Meter dimension that scores whether outputs introduce security vulnerabilities: secrets, vulnerable dependencies, OWASP Top-10 issues, and unsafe shell constructs.

**Security Gate** — A validation gate in the Self-Build Pipeline that scans generated code for secrets and runs a SAST tool to detect new security vulnerabilities.

**Seed** — The initial, hand-written implementations of all self-modifiable components, stored in `self_builds/seed/` and never modified.

**Selection (evolutionary strategy)** — Tournament-based selection among a population of generated variants, choosing the highest scorer for final validation.

**Self-Build** — A lifecycle event in which Ralph autonomously improves one of its own code components by generating, validating, and integrating an improved implementation.

**Self-Build Design Document** — See SBDD.

**Self-Building Codes** — The subsystem of CactusRalph-Coder that enables Ralph to write, test, refine, and evolve its own tools, helpers, and prompt templates.

**Session** — A single continuous interaction between a user and Ralph, from the first user message to the final session report.

**Session Aggregate Score** — The weighted average of all action scores in a session, representing the overall quality of Ralph's work for that session.

**Session Report** — A structured document produced at the end of each session summarising action scores, the session aggregate score, strengths, areas for improvement, and a comparison to the previous session.

**Short-Term Memory** — The active context window for the current session. Ephemeral; reset at session end.

**Sub-Dimension** — A specific measurable facet within a Ralph Meter dimension (e.g., "Tests pass" is a sub-dimension of Correctness).

**Sub-Task** — An atomic, actionable step produced by goal decomposition. Sub-tasks are the building blocks of action plans.

**Syntax Gate** — The first validation gate in the Self-Build Pipeline, which parses generated code with the official language parser and verifies imports and type annotations.

---

## T

**Test Gate** — A validation gate in the Self-Build Pipeline that runs the component's existing tests and any new tests added during the self-build.

**Token Cost** — The relative number of language model tokens required to execute an action. Used in the Decision-Making Model to prefer cheaper actions when expected values are equal.

**Tool** — A discrete, callable function that allows Ralph to interact with the outside world (file system, shell, search, GitHub API, etc.). All tools have a defined parameter schema, return schema, and safety rating.

**Tool Registry** — The component that registers, discovers, and calls all available tools. Acts as the single point of control for tool invocations.

**Tournament Selection** — An evolutionary selection method: randomly pick 3 candidates, select the highest scorer, repeat until a final candidate is chosen.

**Trigger** — A condition that initiates a self-build lifecycle event (low utility score, repeated failures, explicit user request, scheduled review, new capability unlocked).

---

## U

**Unrecoverable Error** — An error class in which state is corrupted or the goal is fundamentally impossible. Ralph halts, explains the situation, and proposes next steps to the user.

**Utility Score** — The rolling average Ralph Meter score for a specific tool across its last N invocations. A tool with a utility score below 60 over 10+ calls is a self-build trigger.

---

## V

**Validation Gates** — The five sequential checks (Syntax, Test, Ralph Meter, Regression, Security) that a generated implementation must pass before it can be integrated in a self-build.

**Vector Database** — A database optimised for storing and querying high-dimensional embeddings, used by Ralph's Long-Term Memory to store and retrieve facts by semantic similarity.

**Vector Store** — Ralph's abstraction over the vector database, providing `query` and `upsert` operations.

---

## W

**Working Memory** — The active scratchpad for the current session: current goal, sub-goals, constraints, observed facts, and open questions. Managed by the Context Window Manager.

---

*See also: [Home](Home.md) | [Ralph](Ralph.md) | [Ralph Meter](Ralph-Meter.md) | [Self-Building Codes](Self-Building-Codes.md) | [Architecture](Architecture.md) | [Configuration](Configuration.md)*
