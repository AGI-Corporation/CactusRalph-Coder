"""
CactusEngine: orchestrates the Planner → Coder → Reviewer → Tester pipeline.
"""

import json
import os

from rich.console import Console
from rich.panel import Panel

from cactus.agents import CoderAgent, PlannerAgent, ReviewerAgent, TesterAgent
from cactus.memory import Memory
from cactus.sandbox import Sandbox

console = Console()


class CactusEngine:
    """Main orchestrator for the CactusRalph coding agent workflow."""

    def __init__(self, project_root: str = "."):
        self.project_root = os.path.abspath(project_root)

        memory_file = os.environ.get(
            "MEMORY_FILE",
            os.path.join(self.project_root, "cactus", "memory.json"),
        )
        queue_file = os.environ.get(
            "TASK_QUEUE_FILE",
            os.path.join(self.project_root, "cactus", "task_queue.json"),
        )

        self.memory = Memory(memory_file)
        self.task_queue_file = queue_file
        self.sandbox = Sandbox(self.project_root)

        self.planner = PlannerAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()
        self.tester = TesterAgent()

    # ------------------------------------------------------------------
    # Core pipeline
    # ------------------------------------------------------------------

    def run_coding_cycle(self, requirement: str) -> dict:
        """
        Execute the full Plan → Code → Review → Test cycle.

        Returns:
            {
                "success": bool,
                "files":   {filename: code},
                "review":  {score, issues, suggestions, approved},
                "tests":   str,
                "plan":    dict,
            }
        """
        console.print(Panel(f"[bold cyan]Requirement:[/bold cyan] {requirement}"))

        # 1 — Plan
        console.print("[bold yellow]⚙  Planning...[/bold yellow]")
        context = {"project_root": self.project_root}
        plan = self.planner.plan(requirement, context)
        console.print(f"  Steps: {len(plan.get('steps', []))}")

        # 2 — Generate code
        console.print("[bold yellow]✏  Generating code...[/bold yellow]")
        files = self.coder.generate(plan, context)

        if not isinstance(files, dict):
            files = {}

        # 3 — Review (use first file if multiple)
        review = {"score": 0, "issues": [], "suggestions": [], "approved": False}
        combined_code = "\n\n".join(files.values())

        if combined_code.strip():
            console.print("[bold yellow]🔍 Reviewing code...[/bold yellow]")
            review = self.reviewer.review(combined_code)

            # If not approved, ask coder to improve using feedback
            if not review.get("approved", False):
                feedback = "; ".join(review.get("suggestions", []))
                if feedback:
                    console.print("[bold yellow]🔄 Improving code based on review...[/bold yellow]")
                    improved = self.coder.improve(combined_code, feedback)
                    # Replace files with improved version under a single key
                    if improved.strip():
                        files = {"improved_code.py": improved}
                        review = self.reviewer.review(improved)

        # 4 — Generate tests
        tests = ""
        if combined_code.strip():
            console.print("[bold yellow]🧪 Generating tests...[/bold yellow]")
            tests = self.tester.generate_tests(combined_code)

        success = review.get("approved", False)
        result = {
            "success": success,
            "files": files,
            "review": review,
            "tests": tests,
            "plan": plan,
        }

        # 5 — Persist to memory
        self.memory.save_session(requirement, result)

        status = "[bold green]✅ Success[/bold green]" if success else "[bold red]⚠  Review not approved[/bold red]"
        console.print(Panel(f"{status}  |  Score: {review.get('score', 0)}/100"))

        return result

    # ------------------------------------------------------------------
    # Task queue helpers
    # ------------------------------------------------------------------

    def _load_queue(self) -> list:
        if not os.path.exists(self.task_queue_file):
            return []
        with open(self.task_queue_file) as f:
            data = json.load(f)
        return data.get("tasks", [])

    def _save_queue(self, tasks: list):
        os.makedirs(os.path.dirname(self.task_queue_file), exist_ok=True)
        with open(self.task_queue_file, "w") as f:
            json.dump({"tasks": tasks}, f, indent=2)

    def _process_queue(self):
        tasks = self._load_queue()
        if not tasks:
            console.print("[dim]No tasks in queue.[/dim]")
            return

        pending = [t for t in tasks if t.get("status") != "done"]
        console.print(f"[bold]Processing {len(pending)} task(s) from queue...[/bold]")

        for task in tasks:
            if task.get("status") == "done":
                continue
            requirement = task.get("requirement", "")
            if not requirement:
                task["status"] = "skipped"
                continue
            console.print(f"\n[bold blue]Task:[/bold blue] {requirement}")
            result = self.run_coding_cycle(requirement)
            task["status"] = "done"
            task["success"] = result["success"]

        self._save_queue(tasks)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self, interactive: bool = False):
        """Run the engine in interactive or queue-processing mode."""
        if interactive:
            console.print(Panel("[bold magenta]CactusRalph-Coder — Interactive Mode[/bold magenta]"))
            console.print("Type your coding requirement and press Enter. Type 'quit' to exit.\n")
            while True:
                try:
                    requirement = input("Requirement> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if requirement.lower() in ("quit", "exit", "q"):
                    break
                if requirement:
                    self.run_coding_cycle(requirement)
        else:
            self._process_queue()
