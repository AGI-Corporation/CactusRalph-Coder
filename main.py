#!/usr/bin/env python3
"""CactusRalph-Coder — AI-Powered Coding Agent"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="CactusRalph-Coder AI Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --task "Create a FastAPI endpoint that returns a list of users"
  python main.py --interactive
  python main.py --queue
        """,
    )
    parser.add_argument(
        "--task",
        "-t",
        type=str,
        help="Coding requirement to process immediately",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode (prompt for tasks)",
    )
    parser.add_argument(
        "--queue",
        "-q",
        action="store_true",
        help="Process all pending tasks from the task queue",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Directory to write generated files into",
    )
    args = parser.parse_args()

    # Lazy import so the CLI is usable even without all deps installed for --help
    from cactus.engine import CactusEngine

    project_root = os.getcwd()
    engine = CactusEngine(project_root=project_root)

    if args.task:
        result = engine.run_coding_cycle(args.task)
        _write_files(result.get("files", {}), args.output)
        sys.exit(0 if result["success"] else 1)

    elif args.interactive:
        engine.run(interactive=True)

    elif args.queue:
        engine.run(interactive=False)

    else:
        parser.print_help()
        sys.exit(0)


def _write_files(files: dict, output_dir: str = None):
    """Write generated files to disk."""
    if not files:
        return
    base = os.path.abspath(output_dir) if output_dir else os.getcwd()
    os.makedirs(base, exist_ok=True)
    for filename, code in files.items():
        dest = os.path.join(base, filename)
        parent = os.path.dirname(dest)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(dest, "w") as f:
            f.write(code)
        print(f"  Wrote: {dest}")


if __name__ == "__main__":
    main()
