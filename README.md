# CactusRalph-Coder

> **AI-Powered Coding Agent for the AGI Corporation Ecosystem**

---

*"We don't write code. We architect intelligence that writes code."*
— AGI Corporation

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CactusRalph-Coder                           │
│                   AI Coding Agent Platform                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │   Planner   │  │    Coder    │  │  Reviewer   │
   │    Agent    │  │    Agent    │  │    Agent    │
   │             │  │             │  │             │
   │ Breaks task │  │ Generates   │  │ Reviews for │
   │ into steps  │  │ code files  │  │ bugs/quality│
   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Tester    │
                    │    Agent    │
                    │             │
                    │  Generates  │
                    │ & validates │
                    │    tests    │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │   Sandbox   │  │   Memory    │  │  MCP Bridge │
   │  Execution  │  │  Persistent │  │  Route.X    │
   │             │  │   Storage   │  │ Integration │
   └─────────────┘  └─────────────┘  └─────────────┘
```

---

## Agents

| Agent | Role | Key Methods |
|-------|------|-------------|
| **PlannerAgent** | Analyzes requirements and breaks them into actionable implementation steps | `plan(requirement, context)` |
| **CoderAgent** | Generates production-quality code from specs and plans | `generate(spec, context)`, `improve(code, feedback)` |
| **ReviewerAgent** | Reviews code for bugs, security issues, and quality | `review(code, language)` |
| **TesterAgent** | Generates test suites and validates code syntax | `generate_tests(code, framework)`, `validate_syntax(code)` |

---

## 2026 Development Phases

### Q1 — Core Engine ✅
- Multi-agent orchestration loop (Planner → Coder → Reviewer → Tester)
- OpenAI GPT-4o and Anthropic Claude integration
- Persistent memory and task queue
- Sandbox safe execution environment
- pytest-based test suite

### Q2 — MCP Integration
- Route.X MCP bridge for tool invocation
- GitHub MCP: auto-commit generated code
- FastAPI server exposing agent endpoints
- Real-time streaming responses via SSE

### Q3 — Enterprise Features
- Multi-project workspace management
- Code diff and PR generation
- Integration with CMMC compliance scanning
- evolution-agent knowledge pipeline

### Q4 — Production Hardening
- Horizontal scaling with async task workers
- Audit logging and compliance reporting
- Self-improving agent loop (evolution-agent style)
- Web UI dashboard

---

## Project Structure

```
CactusRalph-Coder/
├── cactus/                    # Core package
│   ├── __init__.py            # Package init + public API
│   ├── agents.py              # PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent
│   ├── engine.py              # CactusEngine — main orchestrator
│   ├── sandbox.py             # Safe code execution + syntax validation
│   ├── memory.py              # Persistent session memory
│   ├── mcp_bridge.py          # Route.X MCP integration
│   ├── memory.json            # Runtime memory (gitignored)
│   └── task_queue.json        # Task queue (initial: empty)
├── tests/
│   ├── __init__.py
│   ├── test_agents.py         # Agent unit tests
│   └── test_engine.py         # Engine + memory tests
├── logs/
│   └── .gitkeep
├── main.py                    # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## How It Works

1. **Task Intake** — a requirement string enters via CLI (`--task`) or task queue
2. **Planning** — `PlannerAgent` calls the LLM to decompose the requirement into steps and identifies files to create or modify
3. **Code Generation** — `CoderAgent` generates code for each file based on the plan
4. **Review** — `ReviewerAgent` scores the code, flags issues, and either approves or requests improvements
5. **Testing** — `TesterAgent` generates a pytest test suite and validates syntax
6. **Persistence** — `Memory` saves the session; generated files are written to disk
7. **MCP Push** — optionally, `MCPBridge` commits the files via GitHub MCP (Route.X)

---

## Quick Start

### Setup

```bash
# Clone
git clone https://github.com/AGI-Corporation/CactusRalph-Coder.git
cd CactusRalph-Coder

# Create virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and set OPENAI_API_KEY (or ANTHROPIC_API_KEY)
```

### Run

```bash
# Single task
python main.py --task "Create a FastAPI endpoint that returns a list of users"

# Interactive mode
python main.py --interactive

# Process task queue
python main.py --queue
```

---

## MCP Integration (Route.X)

CactusRalph-Coder integrates with Route.X via the Model Context Protocol (MCP). When `ROUTEX_MCP_URL` is configured, the agent can:

- **List available tools** from the MCP server
- **Call any MCP tool** by name with structured parameters
- **Push generated code to GitHub** via GitHub MCP

```bash
# Configure Route.X in .env
ROUTEX_MCP_URL=http://localhost:8080/mcp
ROUTEX_API_KEY=your_routex_api_key_here
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM Providers | OpenAI GPT-4o, Anthropic Claude |
| Agent Framework | LangGraph + LangChain |
| Web Framework | FastAPI + Uvicorn |
| MCP Integration | fastapi-mcp (Route.X) |
| HTTP Client | httpx, requests |
| Testing | pytest, pytest-asyncio |
| Config | python-dotenv, pydantic |
| CLI / Logging | rich |

---

## Safety Features

- **Sandbox Execution** — all generated code runs in a subprocess with a configurable timeout (default 30s), preventing runaway processes
- **Syntax Validation** — Python code is validated with `ast.parse` before execution
- **No Direct File Writes** — the engine returns a `files` dict; the caller decides when to write
- **LLM JSON Mode** — structured outputs are requested in JSON mode to prevent prompt injection via malformed responses
- **Environment Isolation** — secrets stay in `.env`, which is gitignored

---

## Integration Points

| System | How |
|--------|-----|
| **Route.X** | MCP bridge (`cactus/mcp_bridge.py`) — call tools, push code via GitHub MCP |
| **CMMC** | Output code can be piped to CMMC compliance scanner endpoint |
| **evolution-agent** | Shares BaseAgent pattern; memory format is compatible |

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built with ❤️ by the AGI Corporation*
