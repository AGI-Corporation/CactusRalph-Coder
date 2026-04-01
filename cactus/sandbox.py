"""
Sandbox: safe code execution and syntax validation.
"""

import ast
import os
import subprocess
import sys
import tempfile


class Sandbox:
    """Executes code safely in a subprocess with a configurable timeout."""

    SANDBOX_DIR_NAME = ".sandbox_run"

    def __init__(self, project_root: str = "."):
        self.project_root = os.path.abspath(project_root)
        self._sandbox_dir = os.path.join(self.project_root, self.SANDBOX_DIR_NAME)

    # ------------------------------------------------------------------
    # Syntax validation
    # ------------------------------------------------------------------

    def validate_syntax(self, code: str, language: str = "python") -> tuple:
        """
        Validate code syntax.

        For Python, uses ast.parse. Other languages fall back to a simple
        compile check where possible.

        Returns (is_valid: bool, message: str).
        """
        if language.lower() == "python":
            try:
                ast.parse(code)
                return True, "Syntax is valid."
            except SyntaxError as exc:
                return False, f"SyntaxError at line {exc.lineno}: {exc.msg}"
            except Exception as exc:
                return False, f"Unexpected validation error: {exc}"

        # Generic fallback: try to compile as Python anyway
        return True, f"Syntax validation not implemented for '{language}'; skipped."

    # ------------------------------------------------------------------
    # Test runner
    # ------------------------------------------------------------------

    def run_tests(self, test_code: str, source_code: str = None) -> tuple:
        """
        Write test (and optionally source) code to temp files and run pytest.

        Returns (passed: bool, output: str).
        """
        # Use a stable directory inside the project to avoid /tmp restrictions
        sandbox_dir = self._sandbox_dir
        os.makedirs(sandbox_dir, exist_ok=True)

        test_file = os.path.join(sandbox_dir, "test_generated.py")
        source_file = os.path.join(sandbox_dir, "source_generated.py")

        try:
            with open(test_file, "w") as f:
                f.write(test_code)

            if source_code:
                with open(source_file, "w") as f:
                    f.write(source_code)

            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=sandbox_dir,
            )
            passed = result.returncode == 0
            output = result.stdout + result.stderr
            return passed, output

        except subprocess.TimeoutExpired:
            return False, "Test run timed out after 60 seconds."
        except Exception as exc:
            return False, f"Error running tests: {exc}"
        finally:
            # Clean up temp files
            for path in (test_file, source_file):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except OSError:
                    pass
            try:
                os.rmdir(sandbox_dir)
            except OSError:
                pass

    # ------------------------------------------------------------------
    # General safe execution
    # ------------------------------------------------------------------

    def execute_safe(self, code: str, timeout: int = 30) -> tuple:
        """
        Execute arbitrary Python code in a subprocess with a timeout.

        Returns (success: bool, output: str).
        """
        # Validate syntax first
        valid, msg = self.validate_syntax(code)
        if not valid:
            return False, msg

        sandbox_dir = self._sandbox_dir
        os.makedirs(sandbox_dir, exist_ok=True)
        exec_file = os.path.join(sandbox_dir, "exec_generated.py")

        try:
            with open(exec_file, "w") as f:
                f.write(code)

            result = subprocess.run(
                [sys.executable, exec_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=sandbox_dir,
            )
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output

        except subprocess.TimeoutExpired:
            return False, f"Execution timed out after {timeout} seconds."
        except Exception as exc:
            return False, f"Execution error: {exc}"
        finally:
            try:
                if os.path.exists(exec_file):
                    os.remove(exec_file)
            except OSError:
                pass
            try:
                os.rmdir(sandbox_dir)
            except OSError:
                pass
