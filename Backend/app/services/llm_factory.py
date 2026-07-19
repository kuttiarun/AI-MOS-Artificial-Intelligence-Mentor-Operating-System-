"""
AI-MOS Backend — LLM Factory Service
======================================
Model-agnostic LLM client orchestrator implementing the BYOK
(Bring Your Own Key) pattern described in Architecture.md and PRD MOD-04.

Design principles:
- The user's API key NEVER touches disk, logs, or the database.
  It lives solely in the request-scoped memory of this call frame.
- Each provider is an explicit branch, making it straightforward to
  add new providers (Anthropic, Google Gemini, etc.) in Phase 2.
- All streaming is done via httpx async generators, which are passed
  directly back to FastAPI's StreamingResponse without buffering.

Supported providers (Phase 1):
  - nvidia-nim   → OpenAI-compatible NVIDIA NIM endpoint
  - openai       → STUB (Phase 2)
  - google-gemini → STUB (Phase 2)
  - anthropic    → STUB (Phase 2)
"""

import logging

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Provider endpoint registry
_PROVIDER_ENDPOINTS: dict[str, str] = {
    "nvidia-nim": "https://integrate.api.nvidia.com/v1/chat/completions",
    # Phase 2 additions:
    # "openai": "https://api.openai.com/v1/chat/completions",
    # "google-gemini": "https://generativelanguage.googleapis.com/v1beta/...",
    # "anthropic": "https://api.anthropic.com/v1/messages",
}

# Default model per provider (user can override in Phase 2 onboarding config)
_DEFAULT_MODELS: dict[str, str] = {
    # Meta Llama 3.1 70B — strong general-purpose reasoning model on NIM
    "nvidia-nim": "meta/llama-3.1-70b-instruct",
}


class LLMFactory:
    """
    Static factory class that instantiates and executes LLM API calls
    using the student's locally-supplied API key on a per-request basis.

    The key is accepted as a parameter and used exactly once per call;
    it is never stored on the instance or written anywhere persistent.
    """

    @staticmethod
    async def get_streaming_response(
        provider: str,
        api_key: str,
        payload: dict,
        system_prompt: str,
    ) -> httpx.Response:
        """
        Routes the compiled pedagogical request to the user's target
        LLM compute provider and returns a raw streaming httpx.Response.

        The caller (gateway endpoint) is responsible for iterating the
        response stream and closing it via `aclose()`.

        Args:
            provider:      Provider identifier string (e.g., "nvidia-nim").
            api_key:       User's personal LLM API token. Never logged.
            payload:       Validated ChatPayload dict (contains user_message).
            system_prompt: Pre-constructed pedagogical context string.

        Returns:
            An open httpx.Response in streaming mode.

        Raises:
            HTTPException 400: Unsupported provider.
            HTTPException 401: Upstream authentication failure (invalid key).
            HTTPException 500: Network or upstream server error.
        """
        provider = provider.strip().lower()

        # ------------------------------------------------------------------
        # Validate provider is supported
        # ------------------------------------------------------------------
        if provider not in _PROVIDER_ENDPOINTS:
            supported = ", ".join(_PROVIDER_ENDPOINTS.keys())
            raise HTTPException(
                status_code=400,
                detail=f"LLM provider '{provider}' is not supported. "
                       f"Supported providers: [{supported}].",
            )

        # ------------------------------------------------------------------
        # Build the OpenAI-compatible message structure
        # ------------------------------------------------------------------
        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": payload["user_message"]},
        ]

        # ------------------------------------------------------------------
        # Route to the correct provider handler
        # ------------------------------------------------------------------
        if provider == "nvidia-nim":
            return await LLMFactory._call_openai_compatible(
                endpoint=_PROVIDER_ENDPOINTS["nvidia-nim"],
                api_key=api_key,
                model=_DEFAULT_MODELS["nvidia-nim"],
                messages=messages,
            )

        # ------------------------------------------------------------------
        # TODO (Phase 2): Add OpenAI, Google Gemini, Anthropic handlers
        # ------------------------------------------------------------------
        elif provider == "openai":
            # TODO: Implement OpenAI streaming handler in Phase 2
            raise HTTPException(
                status_code=501,
                detail="OpenAI provider support is scheduled for Phase 2.",
            )

        elif provider == "google-gemini":
            # TODO: Implement Google Gemini streaming handler in Phase 2
            raise HTTPException(
                status_code=501,
                detail="Google Gemini provider support is scheduled for Phase 2.",
            )

        elif provider == "anthropic":
            # TODO: Implement Anthropic Claude streaming handler in Phase 2
            raise HTTPException(
                status_code=501,
                detail="Anthropic provider support is scheduled for Phase 2.",
            )

        # Fallback (should never be reached due to the registry check above)
        raise HTTPException(status_code=400, detail="Unknown provider.")

    @staticmethod
    async def _call_openai_compatible(
        endpoint: str,
        api_key: str,
        model: str,
        messages: list[dict],
    ) -> httpx.Response:
        """
        Executes a streaming POST to any OpenAI-compatible API endpoint.
        Used for NVIDIA NIM in Phase 1; reusable for OpenAI in Phase 2.

        Security note: `api_key` is used exclusively in the Authorization
        header of this transient request. It is not captured by any logger.
        """
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Do not log the Authorization header — enforced by httpx default config
        }
        request_body = {
            "model": model,
            "messages": messages,
            "stream": True,
            # Temperature tuned for educational explanations: deterministic
            # enough to be consistent but not completely rigid
            "temperature": 0.6,
            "max_tokens": 2048,
        }

        # Use a long timeout for streaming — the initial connection must
        # establish within 30s, but the stream can run indefinitely.
        timeout = httpx.Timeout(connect=30.0, read=None, write=30.0, pool=10.0)

        # httpx.AsyncClient is instantiated per-request (stateless BYOK model).
        # No connection pooling across users — each request is fully isolated.
        client = httpx.AsyncClient(timeout=timeout)

        try:
            request = client.build_request("POST", endpoint, headers=headers, json=request_body)
            response = await client.send(request, stream=True)

            # ------------------------------------------------------------------
            # Graceful upstream error handling (SRS §4)
            # ------------------------------------------------------------------
            if response.status_code == 401:
                # Read the body before raising so we can close cleanly
                await response.aread()
                await client.aclose()
                raise HTTPException(
                    status_code=401,
                    detail={
                        "error": "API key authentication failed.",
                        "code": "UPSTREAM_AUTH_FAILED",
                        "detail": (
                            "Your LLM provider rejected the API key. "
                            "Please re-enter your key in the BYOK configuration panel."
                        ),
                    },
                )

            if response.status_code == 429:
                await response.aread()
                await client.aclose()
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded.",
                        "code": "UPSTREAM_RATE_LIMITED",
                        "detail": "Your API key has exceeded its rate limit. Please wait before retrying.",
                    },
                )

            if response.status_code != 200:
                body = await response.aread()
                await client.aclose()
                logger.warning(
                    "Upstream LLM provider returned non-200 status: %d",
                    response.status_code,
                    # Intentionally NOT logging api_key or request body
                )
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "Upstream provider error.",
                        "code": "UPSTREAM_ERROR",
                        "detail": f"Provider returned HTTP {response.status_code}.",
                    },
                )

            # Return the open streaming response; the caller MUST call aclose()
            return response

        except HTTPException:
            # Re-raise our own structured exceptions unchanged
            raise
        except httpx.ConnectError as exc:
            await client.aclose()
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Could not connect to LLM provider.",
                    "code": "PROVIDER_UNREACHABLE",
                    "detail": str(exc),
                },
            ) from exc
        except Exception as exc:
            await client.aclose()
            logger.error("Unexpected error reaching LLM provider: %s", type(exc).__name__)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Internal gateway error.",
                    "code": "GATEWAY_ERROR",
                    "detail": "An unexpected error occurred while contacting the LLM provider.",
                },
            ) from exc
