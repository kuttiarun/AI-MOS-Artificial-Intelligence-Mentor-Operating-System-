"""
AI-MOS Backend — Pydantic Schemas: Gateway
==========================================
Defines the request/response validation models for the
/api/v1/gateway/* endpoints.

All models use strict Pydantic v2 validation to ensure
malformed payloads are rejected at the boundary layer
before reaching any service logic.
"""

import re

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Request Models
# =============================================================================


class ChatPayload(BaseModel):
    """
    Incoming payload for POST /api/v1/gateway/chat.

    The frontend sends the user's current curriculum position (node_id)
    alongside their message. The backend injects context based on node_id
    before forwarding to the LLM provider.
    """

    current_node_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique curriculum node slug identifying the active lesson.",
        examples=["java-collections-hashmap"],
    )
    user_message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="The student's raw message to the AI mentor.",
        examples=["Why does an array resize when it runs out of capacity?"],
    )

    @field_validator("user_message")
    @classmethod
    def sanitize_prompt_injection(cls, value: str) -> str:
        """
        SRS §4 — Prompt Injection Defense.
        Strips common prompt-injection trigger phrases that attempt to override
        the pedagogical system prompt rules.

        This is a lightweight regex guard; it is NOT a complete security layer
        and should be paired with careful system prompt construction.
        """
        # Patterns that attempt to override AI system instructions
        injection_patterns: list[str] = [
            r"ignore\s+(all\s+)?(your\s+)?(previous|prior|above)\s+instructions?",
            r"disregard\s+(all\s+)?(your\s+)?(previous|prior|above)\s+instructions?",
            r"forget\s+(all\s+)?(your\s+)?(previous|prior|above)\s+instructions?",
            r"you\s+are\s+now\s+a\s+different",
            r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions",
            r"jailbreak",
            r"dan\s+mode",
        ]
        combined_pattern = "|".join(injection_patterns)
        sanitized = re.sub(combined_pattern, "[REDACTED]", value, flags=re.IGNORECASE)
        return sanitized.strip()


# =============================================================================
# Response Models
# =============================================================================


class ErrorResponse(BaseModel):
    """
    Structured JSON error envelope returned when streaming cannot be initiated.
    Allows the frontend to surface clear, actionable error messages
    without crashing the active learning block state (SRS §4).
    """

    error: str = Field(..., description="Human-readable error description.")
    code: str = Field(..., description="Machine-readable error code.", examples=["UPSTREAM_AUTH_FAILED"])
    detail: str | None = Field(
        default=None,
        description="Optional additional technical context for debugging.",
    )


class HealthResponse(BaseModel):
    """Response model for GET /health liveness probe."""

    status: str
    engine: str
    environment: str
