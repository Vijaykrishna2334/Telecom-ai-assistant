"""
Function calling router for telecom operations.
"""
import json
import re
from typing import Any, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class FunctionRouter:
    """Router for handling function calls from LLM."""

    def __init__(self) -> None:
        """Initialize function router."""
        self.functions: dict[str, Any] = {}

    def register(self, name: str, func: Any) -> None:
        """
        Register a function.

        Args:
            name: Function name
            func: Callable function
        """
        self.functions[name] = func
        logger.info("Registered function", name=name)

    async def route(self, function_name: str, arguments: dict[str, Any]) -> Any:
        """
        Route a function call to the appropriate handler.

        Args:
            function_name: Name of the function to call
            arguments: Function arguments

        Returns:
            Function result

        Raises:
            ValueError: If function is not found
        """
        if function_name not in self.functions:
            raise ValueError(f"Function '{function_name}' not found")

        logger.info(
            "Routing function call", function=function_name, arguments=arguments
        )

        func = self.functions[function_name]
        try:
            result = await func(**arguments)
            return result
        except Exception as e:
            logger.error(
                "Function call failed", function=function_name, error=str(e)
            )
            raise

    def extract_function_call(self, text: str) -> Optional[dict[str, Any]]:
        """
        Extract function call from LLM response.

        Args:
            text: LLM response text

        Returns:
            Dict with function name and arguments, or None
        """
        # Try to find JSON function call
        json_pattern = r'\{[^{}]*"function"[^{}]*"arguments"[^{}]*\}'
        matches = re.findall(json_pattern, text)

        if matches:
            try:
                call = json.loads(matches[0])
                if "function" in call and "arguments" in call:
                    return call
            except json.JSONDecodeError:
                pass

        # Try to parse natural language patterns
        patterns = [
            (r"call (\w+) with (.+)", self._parse_with_pattern),
            (r"execute (\w+)\((.+)\)", self._parse_execute_pattern),
            (r"run (\w+) function (.+)", self._parse_run_pattern),
        ]

        for pattern, parser in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return parser(match)

        return None

    def _parse_with_pattern(self, match: re.Match[str]) -> dict[str, Any]:
        """Parse 'call X with Y' pattern."""
        function = match.group(1)
        args_str = match.group(2)
        arguments = self._parse_arguments(args_str)
        return {"function": function, "arguments": arguments}

    def _parse_execute_pattern(self, match: re.Match[str]) -> dict[str, Any]:
        """Parse 'execute X(Y)' pattern."""
        function = match.group(1)
        args_str = match.group(2)
        arguments = self._parse_arguments(args_str)
        return {"function": function, "arguments": arguments}

    def _parse_run_pattern(self, match: re.Match[str]) -> dict[str, Any]:
        """Parse 'run X function Y' pattern."""
        function = match.group(1)
        args_str = match.group(2)
        arguments = self._parse_arguments(args_str)
        return {"function": function, "arguments": arguments}

    def _parse_arguments(self, args_str: str) -> dict[str, Any]:
        """
        Parse argument string into dict.

        Args:
            args_str: Argument string

        Returns:
            Dict of arguments
        """
        arguments = {}
        # Try JSON first
        try:
            arguments = json.loads(args_str)
            if isinstance(arguments, dict):
                return arguments
        except json.JSONDecodeError:
            pass

        # Parse key=value pairs
        pairs = re.findall(r'(\w+)=(["\']?)([^,"\'\s]+)\2', args_str)
        for key, _, value in pairs:
            # Try to convert to appropriate type
            if value.lower() == "true":
                arguments[key] = True
            elif value.lower() == "false":
                arguments[key] = False
            elif value.isdigit():
                arguments[key] = int(value)
            else:
                arguments[key] = value

        return arguments


# Global function router instance
function_router = FunctionRouter()
