import re
from typing import Dict, Any, Set
from pydantic import BaseModel, Field, field_validator

class InputSanitizer:
    """Sanitizes incoming customer messages to shield against prompt injection attacks."""

    PROMPT_INJECTION_PATTERNS = [
        r"ignore (all )?previous instructions",
        r"you are now a system admin",
        r"reveal your (system )?prompt",
        r"system override",
        r"forget your rules",
        r"bypass (all )?safety",
        r"act as an unrestricted AI"
    ]

    @classmethod
    def sanitize_user_input(cls, user_text: str) -> str:
        """Filters user input if prompt injection patterns are detected."""
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, user_text, re.IGNORECASE):
                print(f"Warning: Prompt injection attack pattern detected: '{pattern}'")
                return "[Message content sanitized due to policy safety guidelines]"
        return user_text.strip()


class ToolCallRequest(BaseModel):
    """Pydantic v2 validation schema for function call requests received from Gemini."""
    tool_name: str = Field(..., alias="name")
    arguments: Dict[str, Any] = Field(default_factory=dict, alias="args")

    @field_validator("tool_name")
    def validate_tool_name(cls, v: str) -> str:
        allowed_tools: Set[str] = {
            "check_inventory",
            "reserve_inventory",
            "search_knowledge",
            "create_order",
            "handoff_human"
        }
        if v not in allowed_tools:
            raise ValueError(f"Unauthorized tool execution requested by model: {v}")
        return v
