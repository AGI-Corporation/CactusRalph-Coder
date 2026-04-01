"""
CactusRalph-Coder agents: Planner, Coder, Reviewer, Tester.
Each agent wraps an LLM call and returns structured output.
"""

import ast
import json
import os

from openai import OpenAI


class BaseAgent:
    """Base class for all CactusRalph agents."""

    def __init__(self, name: str):
        self.name = name
        api_key = os.environ.get("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.default_model = os.environ.get("LLM_MODEL", "gpt-4o")

    def _call_llm(self, prompt: str, model: str = None) -> str:
        """Call the LLM and return raw text."""
        if self.client is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Set it in your .env file."
            )
        model = model or self.default_model
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    def _call_llm_json(self, prompt: str, model: str = None) -> dict:
        """Call the LLM requesting a JSON response and return parsed dict."""
        if self.client is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Set it in your .env file."
            )
        model = model or self.default_model
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        return json.loads(raw)


class PlannerAgent(BaseAgent):
    """Analyzes requirements and creates step-by-step implementation plans."""

    def __init__(self):
        super().__init__("PlannerAgent")

    def plan(self, requirement: str, context: dict = None) -> dict:
        """
        Analyze a requirement and return an implementation plan.

        Returns a dict with:
            steps          - ordered list of implementation steps
            files_to_create - list of file paths to create
            files_to_modify - list of existing file paths to change
            notes           - any caveats or assumptions
        """
        context_str = json.dumps(context or {}, indent=2)
        prompt = f"""You are an expert software architect.

Analyze the following requirement and produce a detailed implementation plan in JSON.

Requirement:
{requirement}

Context:
{context_str}

Return a JSON object with these keys:
- "steps": list of strings describing each implementation step in order
- "files_to_create": list of file paths that need to be created
- "files_to_modify": list of existing file paths that need changes
- "notes": any important caveats, assumptions, or considerations

Return only valid JSON."""
        return self._call_llm_json(prompt)


class CoderAgent(BaseAgent):
    """Generates code from plans and specifications."""

    def __init__(self):
        super().__init__("CoderAgent")

    def generate(self, spec: dict, context: dict = None) -> dict:
        """
        Generate code files from a specification/plan.

        Returns a dict mapping filename -> code content.
        """
        context_str = json.dumps(context or {}, indent=2)
        spec_str = json.dumps(spec, indent=2)
        prompt = f"""You are an expert Python developer.

Generate complete, production-quality code for the following specification.

Specification:
{spec_str}

Context:
{context_str}

Return a JSON object where each key is a filename (relative path) and each value
is the complete file content as a string. Include all necessary imports, docstrings,
error handling, and type hints. Return only valid JSON."""
        return self._call_llm_json(prompt)

    def improve(self, code: str, feedback: str) -> str:
        """Improve existing code based on reviewer feedback."""
        prompt = f"""You are an expert Python developer.

Improve the following code based on the reviewer feedback provided.

Original code:
```python
{code}
```

Reviewer feedback:
{feedback}

Return only the improved code (no explanation, no markdown fences)."""
        return self._call_llm(prompt)


class ReviewerAgent(BaseAgent):
    """Reviews code for quality, correctness, and security."""

    def __init__(self):
        super().__init__("ReviewerAgent")

    def review(self, code: str, language: str = "python") -> dict:
        """
        Review code and return a structured assessment.

        Returns a dict with:
            score       - integer 0-100
            issues      - list of issue strings
            suggestions - list of improvement suggestion strings
            approved    - bool (True if score >= 70 and no critical issues)
        """
        prompt = f"""You are a senior {language} code reviewer focused on quality, security, and correctness.

Review the following code thoroughly:

```{language}
{code}
```

Return a JSON object with:
- "score": integer from 0 to 100 reflecting overall code quality
- "issues": list of strings describing bugs, security flaws, or anti-patterns found
- "suggestions": list of strings with concrete improvement suggestions
- "approved": boolean — true if code is acceptable (score >= 70 and no critical security issues)

Be specific and actionable. Return only valid JSON."""
        return self._call_llm_json(prompt)


class TesterAgent(BaseAgent):
    """Generates test suites and validates code syntax."""

    def __init__(self):
        super().__init__("TesterAgent")

    def generate_tests(self, code: str, framework: str = "pytest") -> str:
        """Generate a test suite for the given code using the specified framework."""
        prompt = f"""You are an expert Python test engineer.

Write a comprehensive {framework} test suite for the following code.
Cover happy paths, edge cases, and error conditions.

Code to test:
```python
{code}
```

Return only the test code (no explanation, no markdown fences)."""
        return self._call_llm(prompt)

    def validate_syntax(self, code: str) -> tuple:
        """
        Check Python syntax using ast.parse.

        Returns (is_valid: bool, message: str).
        """
        try:
            ast.parse(code)
            return True, "Syntax is valid."
        except SyntaxError as exc:
            return False, f"SyntaxError at line {exc.lineno}: {exc.msg}"
        except Exception as exc:
            return False, f"Unexpected error during syntax check: {exc}"
